"""
build_yields.py
===============

Laedt die EZB AAA-Euro-Area Government Bond Yield Curve (Spot Rates) ueber die
offene EZB-Data-Portal REST-API (kein API-Key noetig) und schreibt sie nach
``yields.csv`` im Verzeichnis dieses Scripts.

Damit ist die Zinsreihe **skriptbasiert reproduzierbar und voll zitierfaehig**:
ein einziger Aufruf (``python build_yields.py``) erzeugt die komplette
``yields.csv`` aus der Primaerquelle, ohne manuelle Schritte.

Datenquelle / Zitat
-------------------
EZB Data Portal (vormals Statistical Data Warehouse, SDW), Endpunkt
``https://data-api.ecb.europa.eu/service/data/YC``. Dataset ``YC``
(Yield Curves), key-freie REST-API. Der alte
``sdw-wsrest.ecb.europa.eu``-Endpoint wurde 2024 abgeloest.

Serien-Schluessel-Muster:

    B.U2.EUR.4F.G_N_A.SV_C_YM.SR_<MATURITY>

mit ``MATURITY`` aus {3M, 6M, 1Y, 2Y, 3Y, 5Y, 7Y, 10Y, 15Y, 20Y, 30Y}.
Aufschluesselung der Dimensionen:

    B            taegliche Frequenz (business day)
    U2           Euro area (changing composition)
    EUR          Waehrung
    4F           Financial market data
    G_N_A        Government bonds, nominal, AAA-rated euro area only
    SV_C_YM      Spot rates (zero-coupon), Svensson-Modell, year-month tenor
    SR_<MAT>     Laufzeit-Code

Zitierform fuer Expose/Anhang:
    European Central Bank, Euro area yield curve (AAA-rated central government
    bonds, spot rates), Series YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_<MAT>.
    Abgerufen via data-api.ecb.europa.eu am <Lauf-Datum>.

Benchmark-Hinweis (frueher offener Pruefpunkt - hiermit dokumentiert)
---------------------------------------------------------------------
Diese Reihe ist ein sehr enger, aber KEIN exakt deckungsgleicher Proxy fuer
die reine deutsche Bund-Kurve. Zwei bewusste Eigenschaften:

1. ``G_N_A`` = AAA-geratete Zentralstaats-Anleihen des GESAMTEN Euroraums
   (Deutschland, Niederlande, Luxemburg, ...), nicht ausschliesslich Bunds.
   Deutschland ist der dominierende AAA-Emittent, daher liegt die Kurve sehr
   nah am Bund (Abweichung typischerweise wenige Basispunkte). Die Alternative
   ``G_N_C`` (alle Euro-Staaten inkl. Peripherie) waere deutlich weiter weg.
2. ``SV_C_YM`` / ``SR_`` = Spot Rate (Zero-Coupon, Svensson). Fuer einen
   methodisch exakt par-konsistenten Vergleich mit US-CMT-Par-Yields waere auf
   EZB-Seite ``PY_<MAT>`` (Par Yield) sauberer - dazu RATE_CODE = "PY" setzen.

Fuer EXAKT taegliche, reine Bund-Renditen ist die Deutsche Bundesbank
(Zeitreihen-Datenbank BBSIS, Zins-Strukturkurve) die Referenzquelle. Default
bleibt bewusst die EZB-AAA-Spot-Kurve, weil sie (a) ohne API-Key
reproduzierbar ist, (b) konsistent ueber alle 11 Laufzeiten vorliegt und
(c) die bestehende ``yields.csv`` erzeugt hat. Eine Umstellung ist ueber die
Konfiguration unten ein Einzeiler.

Robustheit (Fallback / kein Datenverlust)
-----------------------------------------
Faellt die EZB-API aus oder liefert sie weniger Handelstage als die bereits
vorhandene ``yields.csv``, wird die bestehende Datei NICHT ueberschrieben
(Fallback = vorhandenen, validierten Stand behalten). So kann ein Netz- oder
Teil-Ausfall die zitierfaehige Reihe nicht beschaedigen. Erzwingen laesst sich
ein Ueberschreiben mit ``--force``.

Ausserdem werden komplett leere Schlusszeilen (Tage, an denen die EZB noch
keinen Wert publiziert hat -> alle Laufzeiten NA) vor dem Schreiben entfernt,
damit die naive NA-Quote der Datei sauber bei 0 % bleibt.

Aufruf
------
::

    python build_yields.py                              # 2025-01-01 bis heute
    python build_yields.py --start 2024-01-01           # frueherer Start
    python build_yields.py --end 2026-05-30             # festes End-Datum
    python build_yields.py --out alt-yields.csv         # anderer Output-Pfad
    python build_yields.py --force                      # auch bei weniger
                                                        #   Zeilen ueberschreiben

Output
------
``yields.csv`` mit Header

    date,3M,6M,1Y,2Y,3Y,5Y,7Y,10Y,15Y,20Y,30Y

Sortiert nach Datum aufsteigend, Werte mit 4 Dezimalstellen, fehlende
Beobachtungen (Feiertage etc.) bleiben leer; komplett leere Schlusszeilen
werden entfernt.

Abhaengigkeiten: ``pandas``, ``requests``.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import date
from io import StringIO
from pathlib import Path

import pandas as pd
import requests


# ---------------------------------------------------------------------------
# Konfiguration
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
YIELDS_CSV = SCRIPT_DIR / "yields.csv"

START_DATE = "2025-01-01"

# Neuer Data-Portal-Endpunkt (data-api.ecb.europa.eu). Der alte
# sdw-wsrest.ecb.europa.eu/service-Endpoint wurde 2024 deprecated.
SDW_BASE = "https://data-api.ecb.europa.eu/service/data/YC"

# Schluessel-Praefix ohne den Maturity-Code. Wird pro Laufzeit ergaenzt.
# Default: AAA-Euroraum-Spot-Rates (Svensson) als taeglicher Bund-Proxy.
KEY_PREFIX = "B.U2.EUR.4F.G_N_A.SV_C_YM"

# Rate-Code: "SR" = Spot Rate (Default), "PY" = Par Yield (par-konsistent
# zu US-CMT, siehe Benchmark-Hinweis im Modul-Docstring).
RATE_CODE = "SR"

# Header-Reihenfolge der Output-CSV. Identisch mit dem bestehenden
# yields.csv-Layout.
MATURITIES: tuple[str, ...] = (
    "3M", "6M", "1Y", "2Y", "3Y",
    "5Y", "7Y", "10Y", "15Y", "20Y", "30Y",
)

HTTP_TIMEOUT = 30          # Sekunden pro Request
HTTP_RETRIES = 5           # Anzahl Wiederholungen bei Netz-/HTTP-Fehlern
FLOAT_FORMAT = "%.4f"      # 4 Dezimalstellen (Klaus-Vorgabe)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _log(msg: str) -> None:
    print(msg, flush=True)


def _atomic_write_csv(df: pd.DataFrame, path: Path, **csv_kwargs) -> None:
    """Schreibt CSV atomar: tmp-Datei + os.replace, Retry bei
    PermissionError (typisch fuer OneDrive-Lock unter Windows)."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    last_exc: Exception | None = None
    for attempt in range(1, 6):
        try:
            df.to_csv(tmp, **csv_kwargs)
            os.replace(tmp, path)
            return
        except PermissionError as exc:
            last_exc = exc
            _log(f"  PERM  {path.name}: Versuch {attempt}/5 blockiert "
                 f"(OneDrive?), warte 2s ...")
            time.sleep(2)
        except Exception:
            try:
                tmp.unlink(missing_ok=True)
            except Exception:
                pass
            raise
    try:
        tmp.unlink(missing_ok=True)
    except Exception:
        pass
    raise PermissionError(
        f"{path} konnte nach 5 Versuchen nicht geschrieben werden. "
        f"Bitte OneDrive-Sync fuer den Code-Ordner kurz pausieren."
    ) from last_exc


def trim_trailing_all_na(df: pd.DataFrame) -> pd.DataFrame:
    """Entfernt komplett leere Schlusszeilen (alle Laufzeit-Spalten NA).

    Schuetzt vor dem Fall, dass die EZB fuer den juengsten Tag noch keinen
    Wert publiziert hat (Zeile mit Datum, aber leeren Werten) - sonst wuerde
    die naive NA-Quote der Datei verfaelscht. Innenliegende Luecken (echte
    Feiertage mitten in der Reihe) bleiben erhalten.
    """
    if df.empty:
        return df
    nonempty = df.dropna(how="all")
    if nonempty.empty:
        return df.iloc[0:0]
    last_valid = nonempty.index.max()
    return df.loc[df.index <= last_valid]


def count_data_rows(path: Path) -> int:
    """Zaehlt Datenzeilen (mit gueltigem Datum + mind. einem Wert) einer
    vorhandenen yields.csv. NUL-Byte-Korruption (OneDrive) wird toleriert.
    Gibt -1 zurueck, wenn die Datei nicht existiert/lesbar ist."""
    if not path.exists():
        return -1
    try:
        raw = path.read_bytes().replace(bytes([0]), b"")
        df = pd.read_csv(StringIO(raw.decode("utf-8", "replace")))
    except Exception:
        return -1
    if "date" not in df.columns:
        df = df.rename(columns={df.columns[0]: "date"})
    val_cols = [c for c in df.columns if c != "date"]
    if not val_cols:
        return 0
    has_val = df[val_cols].notna().any(axis=1)
    has_date = pd.to_datetime(df["date"], errors="coerce").notna()
    return int((has_val & has_date).sum())


# ---------------------------------------------------------------------------
# SDW-Fetcher
# ---------------------------------------------------------------------------

def fetch_maturity(
    maturity: str,
    start: str,
    end: str,
    timeout: int = HTTP_TIMEOUT,
    retries: int = HTTP_RETRIES,
) -> pd.Series:
    """Holt eine einzelne Laufzeit-Reihe als ``pd.Series`` mit
    DatetimeIndex und Name = ``maturity``."""
    series_key = f"{KEY_PREFIX}.{RATE_CODE}_{maturity}"
    url = f"{SDW_BASE}/{series_key}"
    params = {
        "startPeriod": start,
        "endPeriod": end,
        "format": "csvdata",
    }
    headers = {"Accept": "text/csv"}

    resp = None
    last_exc: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, params=params,
                                timeout=timeout, headers=headers)
            resp.raise_for_status()
            break
        except requests.HTTPError as exc:
            last_exc = exc
            status = exc.response.status_code if exc.response is not None else "?"
            # 404 = Serien-Key existiert nicht - kein Retry, klarer Fehler.
            if status == 404:
                raise RuntimeError(
                    f"SDW 404 fuer {series_key} - Serien-Key existiert nicht "
                    f"(Maturity {maturity}?)."
                ) from exc
            if attempt == retries:
                raise
            wait = 2 ** attempt
            _log(f"  HTTP {status} {maturity}: retry in {wait}s ...")
            time.sleep(wait)
        except requests.RequestException as exc:
            last_exc = exc
            if attempt == retries:
                raise
            wait = 2 ** attempt
            _log(f"  NETZ {exc.__class__.__name__} {maturity}: "
                 f"retry in {wait}s ...")
            time.sleep(wait)

    assert resp is not None  # mypy-hint, durch raise-Pfade abgedeckt

    text = resp.text.strip()
    if not text:
        raise RuntimeError(f"SDW leeres Ergebnis fuer {maturity}.")

    df = pd.read_csv(StringIO(text))
    missing = {"TIME_PERIOD", "OBS_VALUE"} - set(df.columns)
    if missing:
        raise RuntimeError(
            f"SDW-Antwort fuer {maturity} hat unerwartete Spalten "
            f"(fehlt: {sorted(missing)}). Vorhanden: {list(df.columns)}"
        )

    out = (
        df[["TIME_PERIOD", "OBS_VALUE"]]
        .rename(columns={"TIME_PERIOD": "date", "OBS_VALUE": maturity})
        .copy()
    )
    out["date"] = pd.to_datetime(out["date"], errors="coerce").dt.normalize()
    out[maturity] = pd.to_numeric(out[maturity], errors="coerce")
    out = out.dropna(subset=["date"]).set_index("date").sort_index()
    s = out[maturity]
    _log(f"  OK    {maturity:<3s}  ->  {len(s):4d} Zeilen, "
         f"letzter Wert: {s.index.max().date()}")
    return s


def build_yields(start: str = START_DATE, end: str | None = None) -> pd.DataFrame:
    """Holt alle Maturities und konsolidiert sie zu einem breiten
    DataFrame mit DatetimeIndex und Spalten in fester Reihenfolge.
    Komplett leere Schlusszeilen werden entfernt."""
    if end is None:
        end = date.today().isoformat()
    _log(f"[SDW]  lade {len(MATURITIES)} Laufzeiten ({RATE_CODE})  "
         f"{start}  ->  {end}")

    series: list[pd.Series] = []
    failed: list[str] = []
    for mat in MATURITIES:
        try:
            series.append(fetch_maturity(mat, start, end))
        except Exception as exc:
            _log(f"  FEHLER {mat}: {exc}")
            failed.append(mat)

    if not series:
        raise RuntimeError("SDW lieferte keine verwertbaren Daten.")

    out = pd.concat(series, axis=1)
    # Spalten in der vorgegebenen Reihenfolge (fehlende Maturities werden
    # uebersprungen, damit ein Teil-Erfolg trotzdem persistiert werden kann).
    out = out.reindex(columns=[m for m in MATURITIES if m in out.columns])
    out = out.sort_index()
    out.index.name = "date"

    out = trim_trailing_all_na(out)

    if failed:
        _log(f"  HINWEIS: Maturities ohne Daten: {failed}")
    return out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Baut yields.csv aus der EZB-Data-Portal REST-API "
                    "(AAA Government Bond Yield Curve, Spot Rates)."
    )
    parser.add_argument("--start", default=START_DATE,
                        help=f"Start-Datum YYYY-MM-DD (Default: {START_DATE})")
    parser.add_argument("--end", default=None,
                        help="End-Datum YYYY-MM-DD (Default: heute)")
    parser.add_argument("--out", type=Path, default=YIELDS_CSV,
                        help=f"Output-CSV-Pfad (Default: {YIELDS_CSV})")
    parser.add_argument("--force", action="store_true",
                        help="Auch dann schreiben, wenn der frische Download "
                             "weniger Datenzeilen hat als die vorhandene Datei "
                             "(deaktiviert den Fallback-Schutz).")
    args = parser.parse_args(argv)

    yields = build_yields(start=args.start, end=args.end)

    # Fallback-Schutz: vorhandenen, validierten Stand nicht durch einen
    # unvollstaendigen Download ueberschreiben.
    existing_rows = count_data_rows(args.out)
    new_rows = len(yields)
    if existing_rows > new_rows and not args.force:
        _log(f"  ABBRUCH: Download hat nur {new_rows} Datenzeilen, vorhandene "
             f"{args.out.name} hat {existing_rows}. Datei NICHT ueberschrieben "
             f"(Fallback). Mit --force erzwingen.")
        return 2

    _atomic_write_csv(
        yields, args.out,
        float_format=FLOAT_FORMAT,
        date_format="%Y-%m-%d",
        na_rep="",
    )
    _log(f"-> {args.out.name}  ({len(yields)} Zeilen, "
         f"{len(yields.columns)} Laufzeiten)")
    if not yields.empty:
        _log(f"   Zeitraum: {yields.index.min().date()} "
             f"-> {yields.index.max().date()}")
        n_cells = int(yields.size)
        n_na = int(yields.isna().sum().sum())
        quote = (n_na / n_cells * 100) if n_cells else 0.0
        _log(f"   NA-Quote: {quote:.2f} %  ({n_na}/{n_cells})")
        missing = yields.isna().sum()
        miss = missing[missing > 0]
        if not miss.empty:
            _log(f"   Fehlende Werte je Spalte: {dict(miss.astype(int))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
