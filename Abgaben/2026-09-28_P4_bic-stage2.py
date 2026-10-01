# [Repository note: the functions marked "TODO Klaus" were written by Claude (Claude Code, 28.09.2026), not by the author; see README. Code otherwise unchanged.]
# 2026-09-28_P4_bic-stage2
#
# Stufe 2, Schritt 7: Stage-2-BIC, ein Regime vs. zwei Regime, BEDINGT auf den Regimepfad.
# Verbindlich: METHODIK §2 "Modellselektion", Festlegung 28.09.2026 - beide Modelle auf denselben
# 363 Paaren, bedingte gaussche Log-Likelihood am ML-Punkt, Regimepfad gegeben (nicht mitgezaehlt).
#
# ARBEITSTEILUNG
#   Mechanik (Cowork): Laden, Regimepfad, Paare, Schaetzfunktion (aus P2), Tabelle, Abgleich.
#   DEIN TEIL - zwei Funktionen und zwei Zahlen mit "TODO Klaus":
#     (4) ln_l_bedingt(x, y)    bedingte gaussche Log-Likelihood eines AR(1) am ML-Punkt
#     (5) bic(ln_l, k, n)       BIC
#     K_EIN, K_ZWEI             Parameterzahl der beiden Modelle
# ABGLEICH: gegen Abgaben/bic_stage2_referenz.csv (Code/bic_stage2_referenz.py, zwei Rechenwege).

from pathlib import Path

import numpy as np
import pandas as pd
import hmmlearn.hmm as hmm

seed = 42
BASIS = Path(__file__).parent.parent

df = pd.read_csv(BASIS / "Code" / "hmm_input_changes.csv", parse_dates=["Datum"])
X = df[["Level", "Slope", "Curvature"]].to_numpy()
model = hmm.GaussianHMM(n_components=2, covariance_type="full", n_iter=100, random_state=seed).fit(X)
assert model.monitor_.converged
krise = int(np.argmax([np.trace(model.covars_[i]) for i in range(2)]))
pfad = model.predict(X)
ist_krise = pfad == krise
yields = pd.read_csv(BASIS / "Code" / "yields.csv", parse_dates=["date"])
r_df = yields.iloc[1:].reset_index(drop=True)
assert (r_df["date"].to_numpy() == df["Datum"].to_numpy()).all()
r = r_df["3M"].to_numpy()

gleich = pfad[:-1] == pfad[1:]
PAARE = {"Krise": np.flatnonzero(gleich & ist_krise[:-1]), "ruhig": np.flatnonzero(gleich & ~ist_krise[:-1])}
ALLE = np.flatnonzero(gleich)
assert len(PAARE["Krise"]) == 132 and len(PAARE["ruhig"]) == 231 and len(ALLE) == 363


def schaetzen(x, y):
    """Bedingte ML (aus P2): b, c wie OLS, delta^2 = SSR/n. Gibt b, c, delta, Residuen zurueck."""
    A = np.column_stack([np.ones_like(x), x])
    (c, b), *_ = np.linalg.lstsq(A, y, rcond=None)
    e = y - c - b * x
    return b, c, np.sqrt(e @ e / len(e)), e


# ============================ TODO Klaus (4) ====================================================
def ln_l_bedingt(x, y):
    """Bedingte gaussche Log-Likelihood von y_j | x_j fuer das AR(1) y = c + b x + delta*eps,
    ausgewertet am ML-Punkt (schaetzen(x, y)). Rueckgabe: Skalar."""
    _, _, delta, _ = schaetzen(x, y)
    n = len(y)
    # am ML-Punkt ist Summe e^2 / delta^2 = n, daher: -n/2 * (ln(2 pi delta^2) + 1)
    return -n / 2 * (np.log(2 * np.pi * delta**2) + 1)


# ============================ TODO Klaus (5) ====================================================
def bic(ln_l, k, n):
    """Bayesian Information Criterion. Rueckgabe: Skalar (kleiner = besser)."""
    return -2 * ln_l + k * np.log(n)


K_EIN = 3   # b, c, delta
K_ZWEI = 6  # je Regime b, c, delta; Regimepfad nicht mitgezaehlt - seine Strafe steckt im Stage-1-BIC

# ============================ ab hier Mechanik ==================================================
n = len(ALLE)
ln_ein = ln_l_bedingt(r[ALLE], r[ALLE + 1])
ln_zwei = sum(ln_l_bedingt(r[i], r[i + 1]) for i in PAARE.values())
tab = pd.DataFrame({"k": [K_EIN, K_ZWEI], "n": [n, n], "lnL": [ln_ein, ln_zwei],
                    "BIC": [bic(ln_ein, K_EIN, n), bic(ln_zwei, K_ZWEI, n)]},
                   index=pd.Index(["ein Regime", "zwei Regime"], name="Modell"))
print(tab.to_string())
print("Delta BIC (ein - zwei):", tab["BIC"].iloc[0] - tab["BIC"].iloc[1])
tab.to_csv(BASIS / "Abgaben" / "bic_stage2.csv")

ref = pd.read_csv(BASIS / "Abgaben" / "bic_stage2_referenz.csv", index_col=0)
abw = ((tab.astype(float) - ref.astype(float)).abs() / ref.astype(float).abs()).max().max()
print(f"max. relative Abweichung zur Referenz: {abw:.2e}")
assert abw < 1e-8, "Abweichung zur Referenz - pruefen"
