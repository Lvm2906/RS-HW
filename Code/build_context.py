"""
build_context.py
================

Erzeugt vier Artefakte im Verzeichnis dieses Scripts:

* ``context_prices.csv``      Schlusskurse (yfinance + FRED, ab 2025-01-01).
* ``context_events.csv``      Pro Briefing-Tag drei Spalten:
                              ``date,regime,event``.
* ``context.csv``             Merge auf ``date`` (Preise links, Events rechts).
* ``extraction_warnings.txt`` Briefings mit <100 Zeichen extrahiertem Text
                              (Hinweis auf Bild-PDFs ohne OCR).

Quellen
-------
* yfinance: ^GSPC, ^IXIC, ^GDAXI, EURUSD=X, BZ=F, GC=F, ^VIX, ^TNX.
* FRED:     DFF (Federal Funds Rate) via fredgraph.csv (kein API-Key).

Schema: regime und event
------------------------
``regime`` ist ein **Tageszustand**:

    crisis   = Hormus-/Iran-Krise ist im Briefing aktiv praesent
               (Dauerstoerung – seit April 2026 fast durchgaengig).
    normal   = alles andere.

``event`` ist das **dominante Tagesthema** unabhaengig vom Regime.
Hormus wird hier nur taggt, wenn es eine *akute Eskalation* gab
(Beschuss, Kaperung, neues Sanktions-Paket). Andernfalls gewinnt das
naechste passende Thema. Erlaubte Werte:

    hormus_eskalation, oil_spike, risk_off, tech_selloff,
    defense_rally, cpi_surprise, fed_dissent, ezb_hike, ezb_hold,
    normal

Aufruf
------
::

    python build_context.py                # Default-Pfade
    python build_context.py --briefings .. # PDFs aus Elternordner
    python build_context.py --no-prices    # nur Events neu erzeugen

Abhaengigkeiten: ``pandas``, ``yfinance``, ``requests``, ``pypdf``.

"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time
from datetime import date
import datetime as _dt
from io import StringIO
from pathlib import Path

import pandas as pd
import requests

try:
    import yfinance as yf
except ImportError:  # pragma: no cover
    yf = None  # type: ignore[assignment]

# ---------------------------------------------------------------------------
# Konfiguration
# ---------------------------------------------------------------------------

START_DATE = "2025-01-01"
END_DATE = date.today().isoformat()

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_BRIEFING_DIR = SCRIPT_DIR.parent

PRICES_CSV = SCRIPT_DIR / "context_prices.csv"
EVENTS_CSV = SCRIPT_DIR / "context_events.csv"
CONTEXT_CSV = SCRIPT_DIR / "context.csv"
WARNINGS_TXT = SCRIPT_DIR / "extraction_warnings.txt"

MIN_PDF_TEXT_LEN = 100  # Schwelle fuer "PDF-Text plausibel extrahiert"

YF_TICKERS: dict[str, str] = {
    "sp500":   "^GSPC",
    "nasdaq":  "^IXIC",
    "dax":     "^GDAXI",
    "eur_usd": "EURUSD=X",
    "brent":   "BZ=F",
    "gold":    "GC=F",
    "vix":     "^VIX",
    "us_10y":  "^TNX",
}

FRED_DFF_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DFF"

# Regime: binaerer Tageszustand (Krise praesent ja/nein).
# Wir taggen "crisis", sobald die Hormus-/Iran-Krise im Briefing-Text
# auftaucht, unabhaengig von Akut-Eskalation.
REGIME_PATTERNS: tuple[tuple[str, str], ...] = (
    ("crisis",
        r"hormus|hormuz|stra(?:ß|ss)e\s+von\s+hormus|"
        r"iran[- ]?krise|us[- ]?iran[- ]?krise|"
        r"hormus[- ]?blockade"),
)

# Erlaubte Event-Werte (mit hormus_eskalation statt hormus_blockade).
ALLOWED_EVENTS: tuple[str, ...] = (
    "hormus_eskalation",
    "oil_spike",
    "risk_off",
    "tech_selloff",
    "defense_rally",
    "cpi_surprise",
    "fed_dissent",
    "ezb_hike",
    "ezb_hold",
    "normal",
)

# Event-Patterns. Reihenfolge = Dominanz-Prio.
# hormus_eskalation feuert NUR bei expliziter Akut-Indikatorik
# (Beschuss, Kaperung, Sanktions-Aktion, Raketen, Drohnen). Eine bloße
# Erwaehnung von Hormus reicht nicht – dafuer ist das Regime zustaendig.
EVENT_PATTERNS: tuple[tuple[str, str], ...] = (
    ("hormus_eskalation",
        # Akute Vorfaelle (keine Bestandsbeschreibung der Dauerkrise):
        r"beschuss|beschossen|"
        r"kaperung|gekapert|geentert|"
        r"raket(?:en)?[- ]?(?:angriff|abschuss|abgefeuert|einschlag)|"
        r"drohnen[- ]?(?:angriff|abschuss|schwarm)|"
        r"neue\s+sanktion(?:en|s[- ]?paket)?|"
        r"sanktion(?:s[- ]?paket|en[- ]?verschärfung)|"
        # Verbund-Wort 'hormus-eskalation' / 'hormuz-eskalation' = klar Akut:
        r"hormu[sz][- ]?eskalation|"
        # Akut-Modifier vor 'eskalation' in der Naehe von Hormus/Iran:
        r"(?:neue|frische|weitere|deutliche)\s+eskalation"
        r"[^.\n]{0,40}(?:hormus|hormuz|iran|persischen)|"
        r"eskaliert\s+(?:weiter|deutlich|drastisch|noch)"
        r"[^.\n]{0,80}(?:hormus|hormuz|iran|persischen|tanker)|"
        r"explosion[^.\n]{0,40}(?:tanker|hormus|persischen)"),
    # HINWEIS: Die "weichen" Trigger oben (Verbund-Wort 'hormus-eskalation',
    # 'eskalation'-Wendungen, 'explosion') unterliegen zusaetzlich einem
    # Hedge-Veto (HEDGE_CONTEXT / _is_hedged in _detect_event): Steht der
    # Treffer in einem hypothetischen/Absicherungs-Kontext ("Hedge gegen eine
    # Hormuz-Eskalation", "Risiko einer Eskalation"), zaehlt er NICHT als
    # akutes Tagesereignis. Harte Vorfaelle (Beschuss, Kaperung, Raketen,
    # Drohnen, Sanktionen) feuern dagegen immer.
    ("oil_spike",
        r"oil[- ]?spike|"
        r"(?:brent|wti|öl|oel)[^.\n]{0,40}\+\s*[5-9]\d?[.,]?\d*\s*%|"
        r"brent[^.\n]{0,30}(?:1[2-9]\d|200)\s*(?:usd|\$)"),
    ("risk_off",
        # Nur Gesamtmarkt-Risk-off. Die fruehere Klausel
        # 'safe-haven-nachfrage' wurde entfernt: sie feuerte auch an
        # Aktien-Rekordtagen, wenn lediglich Gold als Safe Haven erwaehnt
        # wurde (z.B. 2026-05-29: S&P/Nasdaq auf Allzeithoch, nur Gold-
        # Safe-Haven-Satz). Das ist kein Risk-off-Tag. Alle echten
        # risk_off-Tage tragen ohnehin einen der starken Trigger unten.
        r"risk[- ]?off|risikoabbau|"
        r"flight\s+to\s+(?:quality|safety)"),
    ("tech_selloff",
        r"tech[- ]?(?:selloff|sell-?off|abverkauf|crash|kollaps)|"
        r"nasdaq[^.\n]{0,30}-\s*[2-9][.,]?\d*\s*%|"
        r"halbleiter[- ]?(?:abverkauf|crash|kollaps|selloff)"),
    ("defense_rally",
        r"defense[- ]?rally|rüstungs[- ]?rally|"
        r"(?:rüstung|defense|verteidigung)[^.\n]{0,30}\+\s*[3-9][.,]?\d*\s*%"),
    ("cpi_surprise",
        r"cpi[- ]?(?:überraschung|surprise|sprung|hot|schock)|"
        r"verbraucherpreis[^.\n]{0,30}(?:überraschung|sprung|hot)|"
        r"inflation[^.\n]{0,30}(?:überraschung|surprise|deutlich\s+über)"),
    ("fed_dissent",
        r"fed[- ]?dissens|fomc[- ]?dissens|dissens[- ]?konstellation|"
        r"(?:fomc|fed)[^.\n]{0,40}(?:[345678]-[12345]|geteilt|split)\s*-?\s*"
        r"(?:abstimmung|vote)?"),
    ("ezb_hike",
        r"ezb[- ]?hike|ezb[^.\n]{0,30}(?:anhebung|erhöht|hike)|"
        r"einlagensatz[^.\n]{0,30}(?:angehoben|\+\s*25\s*bp)"),
    ("ezb_hold",
        r"ezb[^.\n]{0,30}(?:hielt|beließ|unverändert)|"
        r"ezb[- ]?hold|einlagensatz[^.\n]{0,30}unverändert"),
)

PDF_DATE_RE = re.compile(r"Markt[-_]?Briefing[-_](\d{4}-\d{2}-\d{2})", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Hedge-Veto fuer hormus_eskalation
# ---------------------------------------------------------------------------
# Die "harten" Trigger sind eindeutige Akut-Vorfaelle und feuern immer.
# Die "weichen" Trigger (Verbund-Wort, '...eskalation'-Wendungen, 'explosion')
# koennen auch in einem hypothetischen / Absicherungs-Kontext stehen
# ("Goldminen als Hedge gegen eine Hormuz-Eskalation", "Risiko einer weiteren
# Eskalation"). Solche Treffer sind KEIN gemeldeter Tagesvorfall und werden
# verworfen. Damit reproduziert das Skript handkuratierte 'normal'-Tags wie
# 2026-05-29 (Hedge-Erwaehnung, kein Vorfall) korrekt.

# Harte Akut-Indikatoren – nie vom Hedge-Veto betroffen.
HORMUS_HARD_PATTERN = (
    r"beschuss|beschossen|"
    r"kaperung|gekapert|geentert|"
    r"raket(?:en)?[- ]?(?:angriff|abschuss|abgefeuert|einschlag)|"
    r"drohnen[- ]?(?:angriff|abschuss|schwarm)|"
    r"neue\s+sanktion(?:en|s[- ]?paket)?|"
    r"sanktion(?:s[- ]?paket|en[- ]?verschärfung)"
)

# Kontextwoerter, die einen WEICHEN Hormus-Treffer als hypothetisch/Absicherung
# entlarven. Wird im Fenster um den Treffer geprueft.
HEDGE_CONTEXT_PATTERN = (
    r"hedge|absicher|absichern|gegen\s+eine|gegen\s+das\s+risiko|"
    r"risiko\s+(?:einer|eines|von)|als\s+schutz|schutz\s+gegen|"
    r"versicherung\s+gegen|falls|sollte\s+es|im\s+falle|"
    r"befuerchtung|befürchtung|sorge\s+(?:vor|um)|angst\s+vor|"
    r"droh(?:t|ende|enden)|potenziell|moegliche|mögliche|drohszenario"
)
HEDGE_WINDOW = 60  # Zeichen vor dem Treffer, in denen Hedge-Kontext zaehlt

# ---------------------------------------------------------------------------
# Same-Day-Veto fuer ezb_hold / ezb_hike (und analog nutzbar)
# ---------------------------------------------------------------------------
# Die Briefings erwaehnen EZB-Entscheidungen oft WOCHENLANG rueckblickend
# ("der EZB-Rat hielt am 30. April ...") oder als Markt-Erwartung
# ("Geldmaerkte preisen drei EZB-Hikes"). Beides ist KEINE Entscheidung *am
# Tag* und darf den Tag nicht als ezb_hold/ezb_hike taggen. ezb_hold/ezb_hike
# feuert daher nur, wenn (a) keine Pricing-Sprache im Fenster steht UND (b) der
# Treffer "heute"/"gestern" oder ein Datum nahe (+/- EZB_DECISION_LAG Tage) am
# Briefing-Datum referenziert. Reine Rueckblicke/Erwartungen -> verworfen.
EZB_PRICING_PATTERN = (
    r"preis(?:en|t|st)|pricing|eingepreist|erwart|rechnen\s+mit|"
    r"in\s+aussicht|spekul|wett(?:en|et)|signalisiert\s+drei|"
    r"drei\s+ezb-hikes"
)
EZB_DECISION_LAG = 3       # Tage Toleranz Briefing-Datum <-> referenziertes Datum
EZB_WINDOW = 80            # Zeichen-Fenster um den Treffer
_MONTHS_DE = {
    "januar": 1, "februar": 2, "maerz": 3, "märz": 3, "april": 4, "mai": 5,
    "juni": 6, "juli": 7, "august": 8, "september": 9, "oktober": 10,
    "november": 11, "dezember": 12,
}


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _log(msg: str) -> None:
    print(msg, flush=True)


def _atomic_write_csv(df: pd.DataFrame, path: Path, **csv_kwargs) -> None:
    """Schreibt CSV atomar: tmp-Datei + os.replace, mit Retry bei
    PermissionError (typisch fuer OneDrive-Lock auf Windows)."""
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


def _atomic_write_text(text: str, path: Path) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    last_exc: Exception | None = None
    for attempt in range(1, 6):
        try:
            tmp.write_text(text, encoding="utf-8")
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
        f"{path} konnte nach 5 Versuchen nicht geschrieben werden."
    ) from last_exc



# ---------------------------------------------------------------------------
# Preisdaten
# ---------------------------------------------------------------------------

def fetch_yfinance(
    tickers: dict[str, str] = YF_TICKERS,
    start: str = START_DATE,
    end: str = END_DATE,
) -> pd.DataFrame:
    if yf is None:
        raise RuntimeError("yfinance ist nicht installiert.")
    _log(f"[yfinance] lade {len(tickers)} Ticker  {start} -> {end}")
    series: list[pd.Series] = []
    for label, ticker in tickers.items():
        try:
            df = yf.download(
                ticker, start=start, end=end,
                progress=False, auto_adjust=False,
                group_by="column", threads=False,
            )
        except Exception as exc:
            _log(f"  FEHLER {ticker}: {exc}")
            continue
        if df is None or df.empty:
            _log(f"  WARN  {ticker}: leeres Ergebnis")
            continue
        if isinstance(df.columns, pd.MultiIndex):
            if "Close" in df.columns.get_level_values(0):
                close = df["Close"]
                if isinstance(close, pd.DataFrame):
                    close = close.iloc[:, 0]
            else:
                close = df.iloc[:, 0]
        else:
            close = df["Close"] if "Close" in df.columns else df.iloc[:, 0]
        close = close.rename(label).astype(float)
        series.append(close)
        _log(f"  OK    {ticker:>10s}  ->  {label:<8s}  ({len(close):4d} Zeilen)")
    if not series:
        raise RuntimeError("yfinance lieferte keine verwertbaren Daten.")
    out = pd.concat(series, axis=1)
    if getattr(out.index, "tz", None) is not None:
        out.index = out.index.tz_localize(None)
    out.index = pd.DatetimeIndex(out.index).normalize()
    out.index.name = "date"
    return out


def fetch_fred_dff(
    start: str = START_DATE,
    end: str = END_DATE,
    url: str = FRED_DFF_URL,
) -> pd.Series:
    _log(f"[FRED]     lade DFF              {start} -> {end}")
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    df = pd.read_csv(StringIO(resp.text))
    df.columns = [c.strip().lower() for c in df.columns]
    date_col = "date" if "date" in df.columns else df.columns[0]
    df = df.rename(columns={date_col: "date"})
    df["date"] = pd.to_datetime(df["date"])
    df["dff"] = pd.to_numeric(df["dff"], errors="coerce")
    mask = (df["date"] >= start) & (df["date"] <= end)
    df = df.loc[mask].set_index("date").sort_index()
    s = df["dff"].rename("fed_rate")
    _log(f"  OK    DFF        ->  fed_rate ({len(s):4d} Zeilen)")
    return s


def build_prices() -> pd.DataFrame:
    prices = fetch_yfinance()
    fed = fetch_fred_dff()
    prices = prices.join(fed, how="outer").sort_index()
    desired = ["sp500", "nasdaq", "dax", "eur_usd", "brent",
               "gold", "vix", "us_10y", "fed_rate"]
    prices = prices.reindex(columns=[c for c in desired if c in prices.columns])
    _atomic_write_csv(prices, PRICES_CSV, float_format="%.4f")
    _log(f"-> {PRICES_CSV.name}  ({len(prices)} Zeilen, "
         f"{len(prices.columns)} Spalten)")
    return prices


# ---------------------------------------------------------------------------
# Event-Extraktion
# ---------------------------------------------------------------------------

def _extract_pdf_text(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("pypdf ist nicht installiert.") from exc
    reader = PdfReader(str(path))
    parts: list[str] = []
    for page in reader.pages:
        try:
            parts.append(page.extract_text() or "")
        except Exception:
            continue
    return "\n".join(parts)


def _detect_regime(text: str) -> str:
    lower = text.lower()
    for tag, pattern in REGIME_PATTERNS:
        if re.search(pattern, lower, flags=re.IGNORECASE):
            return tag
    return "normal"


def _hormus_is_acute(lower: str) -> bool:
    """True, wenn der Text einen *akuten* Hormus-Vorfall meldet.

    Harte Indikatoren (Beschuss, Kaperung, Raketen, Drohnen, Sanktionen)
    zaehlen immer. Weiche Treffer (Verbund-Wort, '...eskalation'-Wendungen,
    'explosion') zaehlen nur, wenn KEIN Hedge-/Hypothese-Kontext direkt davor
    steht (Hedge-Veto).
    """
    if re.search(HORMUS_HARD_PATTERN, lower, flags=re.IGNORECASE):
        return True
    # Weiche Treffer einzeln pruefen und Hedge-Kontext im Fenster davor checken.
    soft = (
        r"hormu[sz][- ]?eskalation|"
        r"(?:neue|frische|weitere|deutliche)\s+eskalation"
        r"[^.\n]{0,40}(?:hormus|hormuz|iran|persischen)|"
        r"eskaliert\s+(?:weiter|deutlich|drastisch|noch)"
        r"[^.\n]{0,80}(?:hormus|hormuz|iran|persischen|tanker)|"
        r"explosion[^.\n]{0,40}(?:tanker|hormus|persischen)"
    )
    for m in re.finditer(soft, lower, flags=re.IGNORECASE):
        pre = lower[max(0, m.start() - HEDGE_WINDOW):m.start()]
        if not re.search(HEDGE_CONTEXT_PATTERN, pre, flags=re.IGNORECASE):
            return True  # echter Vorfall, kein Hedge-Kontext
    return False


def _nearby_dates(window: str, ref: "_dt.date") -> list:
    """Extrahiert Datumsangaben aus einem Textfenster (DD.MM[.YYYY] und
    'DD. Monat'). Jahr default = Jahr des Briefings."""
    found = []
    for m in re.finditer(r"(\d{1,2})\.\s*(\d{1,2})\.(?:\s*(\d{4}))?", window):
        dd, mm, yy = int(m.group(1)), int(m.group(2)), m.group(3)
        try:
            found.append(_dt.date(int(yy) if yy else ref.year, mm, dd))
        except ValueError:
            pass
    for m in re.finditer(
        r"(\d{1,2})\.\s*(januar|februar|maerz|märz|april|mai|juni|juli|"
        r"august|september|oktober|november|dezember)", window):
        try:
            found.append(_dt.date(ref.year, _MONTHS_DE[m.group(2)], int(m.group(1))))
        except (ValueError, KeyError):
            pass
    return found


def _ezb_is_sameday(lower: str, pattern: str, ref: "_dt.date | None") -> bool:
    """True nur fuer eine EZB-Entscheidung *am Briefing-Tag* (Same-Day).

    Verwirft Markt-Pricing ('Geldmaerkte preisen ...') und reine Rueckblicke
    (referenziertes Datum > EZB_DECISION_LAG Tage vom Briefing entfernt). Ohne
    bekanntes Briefing-Datum (ref=None) faellt die Funktion konservativ auf das
    alte Verhalten zurueck (reiner Regex-Treffer).
    """
    if ref is None:
        return bool(re.search(pattern, lower, flags=re.IGNORECASE))
    for m in re.finditer(pattern, lower, flags=re.IGNORECASE):
        win = lower[max(0, m.start() - EZB_WINDOW):m.end() + EZB_WINDOW]
        if re.search(EZB_PRICING_PATTERN, win, flags=re.IGNORECASE):
            continue  # Markt-Erwartung, keine Entscheidung
        ctx = lower[max(0, m.start() - 60):m.end() + 60]
        if re.search(r"\bheute\b|\bgestern\b", ctx):
            return True
        dates = _nearby_dates(win, ref)
        if dates and any(abs((ref - x).days) <= EZB_DECISION_LAG for x in dates):
            return True
    return False


def _detect_event(text: str, ref_date: "_dt.date | None" = None) -> str:
    lower = text.lower()
    for tag, pattern in EVENT_PATTERNS:
        if tag == "hormus_eskalation":
            # Sonderbehandlung mit Hedge-Veto statt reinem Regex-Treffer.
            if _hormus_is_acute(lower):
                return tag
            continue
        if tag in ("ezb_hold", "ezb_hike"):
            # Same-Day-Veto: nur Entscheidung am Briefing-Tag, kein Rueckblick
            # und kein Markt-Pricing.
            if _ezb_is_sameday(lower, pattern, ref_date):
                return tag
            continue
        if re.search(pattern, lower, flags=re.IGNORECASE):
            return tag
    return "normal"


def extract_events_from_pdfs(briefing_dir: Path) -> pd.DataFrame:
    """Liest alle Briefing-PDFs. Schreibt context_events.csv (date,regime,event)
    und extraction_warnings.txt fuer PDFs ohne plausiblen Text.

    SICHERHEIT: Wenn der Briefing-Ordner fehlt oder keine PDFs enthaelt,
    wird context_events.csv NICHT angetastet — das schuetzt manuell
    kuratierte Tags vor Loeschen durch einen falschen --briefings-Pfad.
    Stattdessen wird die vorhandene Datei zurueckgegeben (oder ein leerer
    DataFrame, falls keine existiert).
    """
    if not briefing_dir.exists():
        _log(f"[PDF]      Briefing-Ordner fehlt: {briefing_dir}")
        _log(f"           context_events.csv wird NICHT angetastet "
             f"(manuelle Tags geschuetzt).")
        if EVENTS_CSV.exists():
            return pd.read_csv(EVENTS_CSV)
        return pd.DataFrame(columns=["date", "regime", "event"])

    pdfs = sorted(briefing_dir.glob("Markt-Briefing-*.pdf"))
    if not pdfs:
        pdfs = sorted(briefing_dir.rglob("Markt-Briefing-*.pdf"))
    _log(f"[PDF]      {len(pdfs)} Briefing-Datei(en) in {briefing_dir}")

    if not pdfs:
        _log(f"           Keine Markt-Briefing-*.pdf gefunden. "
             f"context_events.csv wird NICHT angetastet "
             f"(manuelle Tags geschuetzt).")
        if EVENTS_CSV.exists():
            return pd.read_csv(EVENTS_CSV)
        return pd.DataFrame(columns=["date", "regime", "event"])

    rows: list[dict[str, str]] = []
    warnings: list[str] = []
    for pdf in pdfs:
        m = PDF_DATE_RE.search(pdf.name)
        if not m:
            _log(f"  SKIP  {pdf.name}: kein Datum im Dateinamen")
            continue
        d = m.group(1)
        try:
            text = _extract_pdf_text(pdf)
        except Exception as exc:
            warnings.append(f"{d}\t{pdf.name}\tFEHLER: {exc}")
            _log(f"  FEHLER {pdf.name}: {exc}")
            rows.append({"date": d, "regime": "", "event": ""})
            continue

        n_chars = len(text)
        if n_chars < MIN_PDF_TEXT_LEN:
            warnings.append(
                f"{d}\t{pdf.name}\t{n_chars} Zeichen extrahiert "
                f"(Schwelle {MIN_PDF_TEXT_LEN}) – vermutlich Bild-PDF / OCR noetig"
            )
            _log(f"  WARN  {pdf.name}: nur {n_chars} Zeichen Text \u2013 uebersprungen")
            rows.append({"date": d, "regime": "", "event": ""})
            continue

        regime = _detect_regime(text)
        try:
            ref_date = _dt.date.fromisoformat(d)
        except ValueError:
            ref_date = None
        event = _detect_event(text, ref_date)
        rows.append({"date": d, "regime": regime, "event": event})
        _log(f"  OK    {pdf.name}  ->  regime={regime:<7s} event={event}")

    df = pd.DataFrame(rows, columns=["date", "regime", "event"])
    if not df.empty:
        df = df.drop_duplicates(subset="date", keep="last").sort_values("date")
    _atomic_write_csv(df, EVENTS_CSV, index=False)
    _log(f"-> {EVENTS_CSV.name}  ({len(df)} Zeilen)")

    if warnings:
        header = (
            f"# Extraction-Warnings ({len(warnings)} Eintrag/Eintraege)\n"
            f"# Format: <date>\\t<file>\\t<reason>\n"
        )
        _atomic_write_text(header + "\n".join(warnings) + "\n", WARNINGS_TXT)
        _log(f"-> {WARNINGS_TXT.name}  ({len(warnings)} Warnung/en)")
    else:
        _atomic_write_text("# Keine Extraction-Warnings.\n", WARNINGS_TXT)
    return df


# ---------------------------------------------------------------------------
# Merge + Summary
# ---------------------------------------------------------------------------

def merge_context(prices: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    p = prices.reset_index()
    p["date"] = pd.to_datetime(p["date"]).dt.strftime("%Y-%m-%d")
    if events.empty:
        out = p.copy()
        out["regime"] = ""
        out["event"] = ""
    else:
        e = events.copy()
        e["date"] = pd.to_datetime(e["date"]).dt.strftime("%Y-%m-%d")
        out = p.merge(e, on="date", how="left")
    _atomic_write_csv(out, CONTEXT_CSV, index=False, float_format="%.4f")
    _log(f"-> {CONTEXT_CSV.name}  ({len(out)} Zeilen, "
         f"{len(out.columns)} Spalten)")
    return out


def print_summary(ctx: pd.DataFrame) -> None:
    _log("")
    _log("Zusammenfassung")
    _log("---------------")
    if ctx.empty:
        _log("  (keine Zeilen)")
        return
    _log(f"  Zeitraum:     {ctx['date'].min()}  ->  {ctx['date'].max()}")
    _log(f"  Tage:         {len(ctx)}")
    price_cols = [c for c in ctx.columns if c not in ("date", "regime", "event")]
    _log(f"  Preisspalten: {price_cols}")

    for col in ("regime", "event"):
        if col not in ctx.columns:
            continue
        ev = ctx[col].fillna("").replace("", "(leer)")
        counts = ev.value_counts()
        _log(f"  {col}:")
        for tag, n in counts.items():
            _log(f"    {tag:<20s} {n}")

    miss = ctx.isna().sum().sort_values(ascending=False)
    miss = miss[miss > 0]
    if not miss.empty:
        _log("  Missing Values (Top 5):")
        for col, n in miss.head(5).items():
            _log(f"    {col:<20s} {n}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Baue context.csv aus yfinance + FRED + Briefing-PDFs."
    )
    parser.add_argument("--briefings", type=Path, default=DEFAULT_BRIEFING_DIR,
                        help=f"Ordner mit Markt-Briefing-*.pdf "
                             f"(Default: {DEFAULT_BRIEFING_DIR})")
    parser.add_argument("--no-events", action="store_true",
                        help="PDF-Event-Extraktion ueberspringen.")
    parser.add_argument("--no-prices", action="store_true",
                        help="Preisdownload ueberspringen "
                             "(nutzt bestehende context_prices.csv).")
    args = parser.parse_args(argv)

    if args.no_prices and PRICES_CSV.exists():
        prices = pd.read_csv(PRICES_CSV, parse_dates=["date"]).set_index("date")
    else:
        prices = build_prices()

    if args.no_events:
        if EVENTS_CSV.exists():
            _log(f"[skip]    Event-Extraktion uebersprungen, "
                 f"lade vorhandene {EVENTS_CSV.name}")
            events = pd.read_csv(EVENTS_CSV)
        else:
            _log(f"[skip]    Event-Extraktion uebersprungen, "
                 f"keine {EVENTS_CSV.name} vorhanden -> leerer DataFrame")
            events = pd.DataFrame(columns=["date", "regime", "event"])
    else:
        events = extract_events_from_pdfs(args.briefings)

    ctx = merge_context(prices, events)
    print_summary(ctx)
    return 0


if __name__ == "__main__":
    sys.exit(main())
