"""
RS-HW — Schritt 4: numerische Robustheit des Stage-1-Fits
=========================================================
Offener Punkt aus HANDOVER §2.4: Die Reproduzierbarkeitsaussage ruhte bisher
allein auf dem festen Seed 42. Geprueft wird hier, ob Konvergenz, Streuungen,
Label-Zuordnung und - entscheidend - der Viterbi-Pfad ueber verschiedene
Startwerte stabil bleiben.

Kein Designeingriff: Modell, Daten und Spezifikation sind unveraendert
(377x3, K=2, covariance_type="full", n_iter=100). Variiert wird ausschliesslich
random_state, das ueber die k-means-Initialisierung den EM-Startpunkt setzt.

Referenz ist der im Paper verwendete Fit mit Seed 42.
Ausgabe: Abgaben/robustheit_startwerte.csv
"""
import numpy as np, pandas as pd
from pathlib import Path
from hmmlearn.hmm import GaussianHMM

BASIS = Path(__file__).parent.parent
SEEDS = list(range(0, 20)) + [42, 123, 999, 2026]

df = pd.read_csv(BASIS / "Code" / "hmm_input_changes.csv", parse_dates=["Datum"])
X = df[["Level", "Slope", "Curvature"]].to_numpy()
assert X.shape == (377, 3), X.shape


def fit(seed):
    m = GaussianHMM(n_components=2, covariance_type="full", n_iter=100,
                    random_state=seed).fit(X)
    traces = np.array([np.trace(c) for c in m.covars_])
    krise = int(np.argmax(traces))              # label-switching-sicher
    pfad = (m.predict(X) == krise).astype(int)  # 1 = Krise
    return dict(seed=seed,
                konvergiert=bool(m.monitor_.converged),
                iterationen=int(m.monitor_.iter),
                logL=round(float(m.score(X)), 4),
                BIC=round(float(m.bic(X)), 4),
                spur_ruhig=round(float(traces.min()), 4),
                spur_krise=round(float(traces.max()), 4),
                krisenindex=krise,
                krisentage=int(pfad.sum()),
                wechsel=int((np.diff(pfad) != 0).sum())), pfad


ref, ref_pfad = fit(42)
zeilen = []
for s in SEEDS:
    r, p = fit(s)
    r["abw_zu_seed42"] = int((p != ref_pfad).sum())
    r["pfad_identisch"] = bool(r["abw_zu_seed42"] == 0)
    zeilen.append(r)

t = pd.DataFrame(zeilen).sort_values("seed").reset_index(drop=True)
t.to_csv(BASIS / "Abgaben" / "robustheit_startwerte.csv", index=False)

print(t[["seed", "konvergiert", "iterationen", "logL", "spur_ruhig", "spur_krise",
         "krisenindex", "krisentage", "wechsel", "abw_zu_seed42"]].to_string(index=False))
print()
print("Startwerte geprueft      :", len(t))
print("alle konvergiert         :", bool(t["konvergiert"].all()))
print("max. Iterationen         :", int(t["iterationen"].max()), "(Limit 100)")
print("verschiedene logL (4 NK) :", sorted(t['logL'].unique().tolist()))
print("Pfad identisch zu Seed 42:", int(t["pfad_identisch"].sum()), "von", len(t))
print("Krisenindex 0 / 1        :", int((t['krisenindex']==0).sum()), "/", int((t['krisenindex']==1).sum()))
print("Spannweite Spur ruhig    :", round(t['spur_ruhig'].max()-t['spur_ruhig'].min(), 6))
print("Spannweite Spur Krise    :", round(t['spur_krise'].max()-t['spur_krise'].min(), 6))
print("Krisentage min/max       :", int(t['krisentage'].min()), "/", int(t['krisentage'].max()))
