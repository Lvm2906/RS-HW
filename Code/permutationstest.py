"""
RS-HW — Exakter Rotationstest: Regimewechsel <-> dokumentierte Ereignisse
========================================================================
Forschungsfrage (a). Umsetzung der Vorab-Registrierung
`PRAEREGISTRIERUNG_Permutationstest_2026-08-25.md` / `Code/METHODIK.md` §2, §7.

Datenstand : hmm_input_changes.csv = 377 Handelstage (2025-01-03 .. 2026-06-26)
             key_events.csv        = 26 Zeilen, 21 auf Handelstagen
Fit        : hmmlearn.GaussianHMM, n_components=2, covariance_type="full",
             random_state=42  (konvergiert nach 27 Iterationen)
Design     : B1 smoothed-Informationsstand · B2 Viterbi-Wechsel (primaer),
             0,5-Kreuzung (sekundaer) · B3 Zaehlvariante · B4 k=2 primaer,
             k in {1,2,3} · B5 Nicht-Handelstage -> naechster Handelstag ·
             B6 keine Konsolidierung (primaer), eine Zeile je Episode (sekundaer)
             D1 Ereignisse zaehlen (26), Integer-Zaehlvektor
             D2 alle 377 zyklischen Verschiebungen aufzaehlen (exakt)
             D3 p = #{tau : T(tau) >= T_obs} / 377, tau = 0 eingeschlossen
             D4 Naehe-Maske einmal vorab, NICHT-zirkulaer
alpha      : 0,05 einseitig — gilt AUSSCHLIESSLICH fuer die Primaerzelle
             (Viterbi, alle Zeilen, k = 2). Die uebrigen 11 Zellen sind
             Robustheitspruefungen: berichtet, nicht gegen alpha getestet.

Aufruf:  python permutationstest.py [--selftest-only]
Ausgabe: Abgaben/permutationstest_ergebnisse.csv
"""
import sys, os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(os.path.dirname(HERE), "Abgaben",
                    "permutationstest_ergebnisse.csv")
SEED = 42
MAXGAP_DAYS = 14          # Episodenregel, METHODIK §7
KS = (1, 2, 3)

# --------------------------------------------------------------------------
# Kernfunktionen — bewusst frei von Datei-IO, damit der Selbsttest sie nutzt
# --------------------------------------------------------------------------

def switch_positions(state_seq):
    """Positionen, an denen die Zustandsfolge wechselt.

    Konvention: zurueckgegeben wird der Index des ERSTEN Tages des neuen
    Regimes. Der Sample-Beginn ist kein beobachteter Wechsel (die Reihe
    startet bereits im Krisenzustand) und zaehlt daher nicht mit.
    """
    s = np.asarray(state_seq)
    return np.flatnonzero(np.diff(s) != 0) + 1


def proximity_mask(switches, T, k):
    """Nicht-zirkulaere Naehe-Maske: +-k Handelstage um jeden Wechsel.

    Nicht-zirkulaer, weil die Maske den FESTEN Regimepfad beschreibt und
    dessen Raender echte Sample-Grenzen sind. Nur die Ereignisse rotieren.
    Fuer k <= 3 ist sie hier ohnehin identisch zur zirkulaeren Variante:
    der randnaechste Wechsel liegt 9 Positionen vom Anfang, 8 vom Ende.
    """
    m = np.zeros(T, dtype=bool)
    for s in switches:
        m[max(0, s - k): min(T - 1, s + k) + 1] = True
    return m


def statistic(event_counts, mask):
    """B3, Zaehlvariante: Anzahl EREIGNISSE im Naehefenster.

    Skalarprodukt statt Boolescher Maskierung, damit ein Handelstag mit
    zwei Ereignissen auch zwei zaehlt (D1).
    """
    return int(np.dot(event_counts, mask.astype(int)))


def exact_rotation_test(event_counts, mask):
    """D2/D3: alle T zyklischen Verschiebungen aufzaehlen, exakter p-Wert.

    np.roll(v, tau) verschiebt die Ereignisse um tau INDEXPOSITIONEN
    (Handelstage), nicht um Kalendertage. Die Maske rotiert nicht mit.
    """
    T = len(event_counts)
    t_obs = statistic(event_counts, mask)
    null = np.array([statistic(np.roll(event_counts, tau), mask)
                     for tau in range(T)])
    assert null[0] == t_obs, "tau = 0 muss T_obs reproduzieren"
    p = float(np.sum(null >= t_obs)) / T          # tau = 0 eingeschlossen
    return t_obs, p, null

# --------------------------------------------------------------------------
# Selbsttest (D6) — von Hand nachrechenbar
# --------------------------------------------------------------------------

def selftest():
    T, k = 10, 2
    ev = np.zeros(T, dtype=int)
    ev[[2, 3, 4]] = 1                     # Dreier-Cluster
    mask = proximity_mask(np.array([8]), T, k)   # ein Wechsel an Position 8
    # Fenster {6,7,8,9,10} -> auf {6..9} beschnitten (nicht-zirkulaer)
    assert list(np.flatnonzero(mask)) == [6, 7, 8, 9], np.flatnonzero(mask)
    t_obs, p, null = exact_rotation_test(ev, mask)
    assert t_obs == 0,    f"T_obs erwartet 0, ist {t_obs}"
    assert null[5] == 3,  f"tau=5 erwartet 3, ist {null[5]}"   # -> {7,8,9}
    assert null[3] == 2,  f"tau=3 erwartet 2, ist {null[3]}"   # -> {5,6,7}
    assert p == 1.0,      f"bei T_obs=0 muss p=1 sein, ist {p}"

    # Kollisionsprobe zu D1: zwei Ereignisse auf einem Tag zaehlen zweifach
    ev2 = np.zeros(T, dtype=int); ev2[7] = 2
    assert statistic(ev2, mask) == 2
    assert statistic((ev2 > 0).astype(int), mask) == 1   # Bool verschluckt eins

    print("Selbsttest bestanden:")
    print(f"  Maske k=2 um Wechsel 8  -> {list(np.flatnonzero(mask))}")
    print(f"  T_obs = {t_obs} · T(tau=5) = {null[5]} · T(tau=3) = {null[3]} · p = {p}")
    print("  Zaehlvektor zaehlt Doppelbelegung 2, Bool-Vektor nur 1 (D1 belegt)")

# --------------------------------------------------------------------------
# Daten
# --------------------------------------------------------------------------

def load_regime_paths():
    from hmmlearn.hmm import GaussianHMM
    df = pd.read_csv(os.path.join(HERE, "hmm_input_changes.csv"),
                     parse_dates=["Datum"])
    X = df[["Level", "Slope", "Curvature"]].values
    dates = pd.DatetimeIndex(df["Datum"])

    model = GaussianHMM(n_components=2, covariance_type="full",
                        n_iter=100, random_state=SEED).fit(X)
    traces = np.array([np.trace(c) for c in model.covars_])
    crisis = int(np.argmax(traces))       # label-switching-sicher

    viterbi = (model.predict(X) == crisis).astype(int)
    smoothed = (model.predict_proba(X)[:, crisis] > 0.5).astype(int)

    meta = dict(T=len(dates), iters=model.monitor_.iter,
                converged=model.monitor_.converged,
                traces=np.round(traces, 4), crisis=crisis,
                crisis_days_viterbi=int(viterbi.sum()),
                crisis_days_thresh=int(smoothed.sum()))
    return dates, viterbi, smoothed, meta


def load_event_counts(dates):
    """Zwei angemeldete Ereignisvarianten, beide als Integer-Zaehlvektor."""
    ev = pd.read_csv(os.path.join(HERE, "key_events.csv"),
                     parse_dates=["date"]).sort_values("date").reset_index(drop=True)
    T = len(dates)

    def to_counts(ts):
        pos = dates.searchsorted(np.asarray(ts, dtype="datetime64[ns]"), side="left")
        assert (pos < T).all(), "Ereignis hinter dem Sample-Ende"   # B5
        v = np.zeros(T, dtype=int)
        np.add.at(v, pos, 1)
        return v

    # (i) alle Zeilen
    counts_all = to_counts(ev["date"].values)
    assert counts_all.sum() == 26, counts_all.sum()

    # (ii) eine Zeile je Episode (METHODIK §7, entschieden 2026-08-26)
    strand = ["HORMUS" if e.startswith("hormus_") else f"ROW{i}"
              for i, e in enumerate(ev["event"])]
    ev = ev.assign(strand=strand)
    reps = []
    for _, g in ev.groupby("strand", sort=False):
        ds = list(g["date"])
        cur = [ds[0]]
        for i in range(1, len(ds)):
            if (ds[i] - ds[i - 1]).days <= MAXGAP_DAYS:
                cur.append(ds[i])
            else:
                reps.append(cur[0]); cur = [ds[i]]
        reps.append(cur[0])
    reps = sorted(reps)
    counts_epi = to_counts(pd.DatetimeIndex(reps).values)
    assert counts_epi.sum() == 22, counts_epi.sum()

    return {"alle Zeilen (26)": counts_all, "eine je Episode (22)": counts_epi}

# --------------------------------------------------------------------------

def main():
    selftest()
    if "--selftest-only" in sys.argv:
        return
    print()

    dates, viterbi, smoothed, meta = load_regime_paths()
    T = meta["T"]
    print(f"Fit: T={T} · konvergiert={meta['converged']} nach {meta['iters']} Iter. · "
          f"Spuren {meta['traces']} -> Krisenindex {meta['crisis']}")

    paths = {"Viterbi (primaer)": viterbi, "0,5-Kreuzung (sekundaer)": smoothed}
    events = load_event_counts(dates)

    rows = []
    for pname, path in paths.items():
        sw = switch_positions(path)
        print(f"{pname}: {len(sw)} Wechsel · {int(path.sum())} Krisentage")
        for ename, counts in events.items():
            for k in KS:
                mask = proximity_mask(sw, T, k)
                t_obs, p, null = exact_rotation_test(counts, mask)
                primary = (pname.startswith("Viterbi")
                           and ename.startswith("alle") and k == 2)
                rows.append(dict(
                    regimepfad=pname, ereignisse=ename, k=k,
                    wechsel=len(sw), maske_tage=int(mask.sum()),
                    abdeckung=round(mask.mean(), 4),
                    n_ereignisse=int(counts.sum()),
                    erwartung_H0=round(counts.sum() * mask.mean(), 3),
                    T_obs=t_obs, p_exakt=round(p, 6),
                    null_mittel=round(float(null.mean()), 3),
                    null_max=int(null.max()),
                    zelle="PRIMAER (gegen alpha=0,05)" if primary
                          else "Robustheit (nur berichtet)"))

    res = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    res.to_csv(OUT, index=False, encoding="utf-8")
    print("\n" + res.to_string(index=False))
    print(f"\ngeschrieben: {OUT}")


if __name__ == "__main__":
    main()
