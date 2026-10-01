# bic_stage2_referenz.py — Stufe 2, Schritt 7: Stage-2-BIC, REFERENZ (Cowork, 28.09.2026)
# Festlegung METHODIK §2 "Modellselektion", 28.09.2026: beide Modelle auf denselben 363 Paaren,
# bedingte gaussche Log-Likelihood am ML-Punkt, k = 3 / 6, n = 363. Regimepfad gegeben (Strafe im Stage-1-BIC).
# Zwei Wege: (A) geschlossene Form ln L = -n/2 (ln(2 pi delta^2) + 1); (B) statsmodels OLS.llf (ML-Varianz SSR/n).
import runpy
from pathlib import Path
import numpy as np, pandas as pd
import statsmodels.api as sm

ns = runpy.run_path(str(Path(__file__).parent / "bootstrap_referenz.py"), run_name="ref")  # Pfad, Paare, Schaetzer
r, P, schaetzen = ns["r"], ns["PAARE"], ns["schaetzen"]
alle = np.sort(np.concatenate([P["Krise"], P["ruhig"]]))
assert len(alle) == 363 and len(np.unique(alle)) == 363


def lnL_A(i):
    b, c, dl = schaetzen(r[i], r[i + 1]); n = len(i)
    return -n / 2 * (np.log(2 * np.pi * dl ** 2) + 1)


def lnL_B(i):
    return sm.OLS(r[i + 1], sm.add_constant(r[i])).fit().llf


n = 363
zeilen = []
for name, teile, k in [("ein Regime", [alle], 3), ("zwei Regime", [P["Krise"], P["ruhig"]], 6)]:
    A = sum(lnL_A(i) for i in teile); Bw = sum(lnL_B(i) for i in teile)
    assert np.isclose(A, Bw, rtol=1e-10), (A, Bw)
    zeilen.append({"Modell": name, "k": k, "n": n, "lnL": A, "BIC": -2 * A + k * np.log(n)})
tab = pd.DataFrame(zeilen).set_index("Modell")
b1, c1, d1 = schaetzen(r[alle], r[alle + 1])
print(tab.to_string()); print("Delta BIC (ein - zwei):", tab.BIC.iloc[0] - tab.BIC.iloc[1])
print("Ein-Regime-Schaetzung: b =", b1, "delta =", d1, "a =", -np.log(b1) * 252)
tab.to_csv(Path(__file__).parent.parent / "Abgaben" / "bic_stage2_referenz.csv")
