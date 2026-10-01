# einfluss_pruefung.py - Gegenrechnung zur Beschleunigung (Cowork, 30.09.2026, Umsetzung Pruefbericht K4, Befund 2.5)
#
# Zweck: Die registrierte BCa-Beschleunigung nutzt Jackknife-Einflusswerte (DiCiccio & Efron 1996, Gl. 6.7;
# fuer die Verhaeltnisse die 1/n_k-gewichtete K-Stichproben-Form nach Efron 1994, Remark C). Die Quellen
# formulieren die Regel mit EXAKTEN empirischen Einflusswerten (Gl. 6.5 bzw. TR-Gl. 2.16). Dieses Skript
# berechnet die exakten Einflusswerte numerisch (gewichtete KQ-Schaetzung, zentrale Differenzen) und vergleicht
# Beschleunigung und BCa-Grenzen. Es aendert KEIN Ergebnis; die registrierte Rechnung bleibt die Jackknife-Form.
# Zusaetzlich: direkte Remark-C-Rechnung (ein langer Gewichtsvektor der Laenge N = 363, blockweise normiert)
# als Kontrolle der ausgeschriebenen 1/n_k-Gewichte (Formel (6) im Paper).
# Ausgabe: Abgaben/einfluss_pruefung.csv (gelesen von Paper/build_exhibits.py -> Makros InflDacc, InflDlim).
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.special import ndtr, ndtri

BASIS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASIS / "Code"))
import bootstrap_referenz as R  # rechnet beim Import, schreibt nichts

ALPHA, EPS = 0.05, 1e-7
Q = {"a": 0, "sigma": 1}
N = sum(len(i) for i in R.PAARE.values())


def schaetzen_gewichtet(reg, w):
    """Gewichtete bedingte ML (KQ fuer b, c; delta^2 = gewichtete mittlere quadr. Residuen) -> (a, sigma)."""
    i = R.PAARE[reg]; x, y = R.r[i], R.r[i + 1]; w = w / w.sum()
    mx, my = w @ x, w @ y
    b = (w @ ((x - mx) * (y - my))) / (w @ ((x - mx) ** 2)); c = my - b * mx
    return R.a_sigma(b, np.sqrt(w @ ((y - c - b * x) ** 2)))


def einfluss(stat, n):
    """Empirische Einflusswerte t_i = d/de stat((1-e)P0 + e e_i), zentrale Differenz."""
    P0 = np.full(n, 1 / n); t = np.empty(n)
    for k in range(n):
        Pp = (1 - EPS) * P0; Pp[k] += EPS
        Pm = (1 + EPS) * P0; Pm[k] -= EPS
        t[k] = (stat(Pp) - stat(Pm)) / (2 * EPS)
    return t


def acc(t):
    return (t ** 3).sum() / 6 / (t ** 2).sum() ** 1.5


def grenzen(theta, stern, a):
    z0 = ndtri(np.mean(stern < theta)); z = ndtri(np.array([ALPHA / 2, 1 - ALPHA / 2]))
    return np.quantile(stern, ndtr(z0 + (z0 + z) / (1 - a * (z0 + z))))


nK, nR = len(R.PAARE["Krise"]), len(R.PAARE["ruhig"])
ACC_EXAKT, ACC_REMARKC = {}, {}
for q, j in Q.items():
    for reg, n in (("Krise", nK), ("ruhig", nR)):
        ACC_EXAKT[f"{q}_{reg}"] = acc(einfluss(lambda P, reg=reg: schaetzen_gewichtet(reg, P)[j], n))
    # Verhaeltnis: Remark C direkt - ein Vektor der Laenge N, Bloecke je Regime normiert
    ACC_EXAKT[f"{q}_Krise/{q}_ruhig"] = acc(einfluss(
        lambda P: schaetzen_gewichtet("Krise", P[:nK])[j] / schaetzen_gewichtet("ruhig", P[nK:])[j], N))
    # Kontrolle Formel (6): dieselbe Groesse ueber die ausgeschriebenen Gewichte N/n_k
    tK = einfluss(lambda P: schaetzen_gewichtet("Krise", P)[j], nK) / R.TH["ruhig"][q]
    tR = -R.TH["Krise"][q] / R.TH["ruhig"][q] ** 2 * einfluss(lambda P: schaetzen_gewichtet("ruhig", P)[j], nR)
    ACC_REMARKC[f"{q}_Krise/{q}_ruhig"] = acc(np.r_[N / nK * tK, N / nR * tR])

ref = pd.read_csv(BASIS / "Abgaben" / "bootstrap_referenz_ergebnisse.csv", index_col=0)
zeilen = []
for k in R.THETA:
    aj, ae = R.ACC[k], ACC_EXAKT[k]
    lj, le = grenzen(R.THETA[k], R.STAT[k], aj), grenzen(R.THETA[k], R.STAT[k], ae)
    assert np.allclose(lj, ref.loc[k, ["BCa_unten", "BCa_oben"]].to_numpy(), rtol=1e-8), k
    d = np.abs(lj - le)
    se = ref.loc[k, ["MC_SE_unten", "MC_SE_oben"]].to_numpy()
    zeilen.append({"Groesse": k, "acc_jackknife": aj, "acc_exakt": ae, "d_acc": abs(aj - ae),
                   "d_unten": d[0], "d_oben": d[1], "MC_SE_unten": se[0], "MC_SE_oben": se[1],
                   "d_kleiner_MC_SE": bool((d < se).all())})
for k, v in ACC_REMARKC.items():
    assert abs(v - ACC_EXAKT[k]) < 1e-6, f"Formel (6) weicht von Remark C direkt ab: {k}"

tab = pd.DataFrame(zeilen).set_index("Groesse")
print(tab.to_string())
print("Formel (6) vs. Remark C direkt:", {k: f"{abs(v - ACC_EXAKT[k]):.1e}" for k, v in ACC_REMARKC.items()})
assert tab["d_kleiner_MC_SE"].all()
tab.to_csv(BASIS / "Abgaben" / "einfluss_pruefung.csv")
