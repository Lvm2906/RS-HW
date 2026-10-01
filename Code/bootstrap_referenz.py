# bootstrap_referenz.py — Stufe 2, Schritt 6: REFERENZ-Implementierung (Cowork, 28.09.2026)
#
# Zweck: unabhaengige Gegenrechnung zu Klaus' Implementierung (Abgaben/2026-09-28_P3_bootstrap.py).
# Beide lesen dieselben Ziehungen (Abgaben/bootstrap_ziehungen.npz) und muessen daher bis auf
# Rundung identische Werte liefern. Verfahren exakt nach METHODIK §2 Pkt. 4 inkl. Festlegungen 28.09.2026.
# Bewusst anders gebaut als die Erstimplementierung: vektorisiert ueber alle Replikationen,
# geschlossene Summenformeln statt lstsq, Episoden per groupby.
import itertools
from pathlib import Path
import numpy as np
import pandas as pd
from hmmlearn.hmm import GaussianHMM
from scipy.special import ndtr, ndtri

BASIS = Path(__file__).parent.parent
H, ALPHA, J_MC = 1 / 252, 0.05, 10

# ---------- Regimepfad und Episoden --------------------------------------------------------
d = pd.read_csv(BASIS / "Code" / "hmm_input_changes.csv")
X = d[["Level", "Slope", "Curvature"]].to_numpy()
hmm = GaussianHMM(2, covariance_type="full", n_iter=100, random_state=42).fit(X)
assert hmm.monitor_.converged
krise = int(np.argmax([np.trace(c) for c in hmm.covars_]))
lab = np.where(hmm.predict(X) == krise, "Krise", "ruhig")
y = pd.read_csv(BASIS / "Code" / "yields.csv")
y = y[y["date"].isin(d["Datum"])].reset_index(drop=True)
assert len(y) == 377 and (y["date"].to_numpy() == d["Datum"].to_numpy()).all()
r = y["3M"].to_numpy(float)

episoden, p = [], 0
for g, grp in itertools.groupby(lab):
    L = len(list(grp)); episoden.append((g, p, p + L - 1)); p += L
assert len(episoden) == 14

EP = {R: [(s, e) for g, s, e in episoden if g == R] for R in ("Krise", "ruhig")}
PAARE = {R: np.concatenate([np.arange(s, e) for s, e in EP[R]]) for R in EP}  # Startindex je Paar
assert len(PAARE["Krise"]) == 132 and len(PAARE["ruhig"]) == 231


def schaetzen(x, y):
    """Bedingte ML (= OLS fuer b, c; delta^2 = SSR/n) ueber die letzte Achse. Liefert b, c, delta."""
    n = x.shape[-1]
    Sx, Sy, Sxx, Sxy = x.sum(-1), y.sum(-1), (x * x).sum(-1), (x * y).sum(-1)
    b = (n * Sxy - Sx * Sy) / (n * Sxx - Sx ** 2)
    c = (Sy - b * Sx) / n
    e = y - c[..., None] - b[..., None] * x
    return b, c, np.sqrt((e * e).sum(-1) / n)


def a_sigma(b, delta):
    """Brigo Gl. 55/57; fuer b > 1 stetig fortgesetzt (a <= 0 erlaubt, Festlegung (1) 28.09.)."""
    assert np.all(b > 0)
    a = -np.log(b) / H
    sigma = delta / np.sqrt((b * b - 1) * H / (2 * np.log(b)))
    return a, sigma


# ---------- Punktschaetzung und Residuen ---------------------------------------------------
PKT, RES = {}, {}
for R, i in PAARE.items():
    b, c, dl = schaetzen(r[i], r[i + 1])
    PKT[R] = dict(b=b, c=c, delta=dl)
    RES[R] = r[i + 1] - c - b * r[i]
    assert abs(RES[R].mean()) < 1e-12  # durch den Achsenabschnitt zentriert


def regenerieren(R, e_stern):
    """Je Episode ab dem beobachteten Starttag rekursiv neu erzeugen; e_stern: (B, n_R)."""
    b, c = PKT[R]["b"], PKT[R]["c"]
    Bn = e_stern.shape[0]
    xs, ys, j = np.empty_like(e_stern), np.empty_like(e_stern), 0
    for s, e in EP[R]:
        x = np.full(Bn, r[s])
        for _ in range(e - s):
            xn = c + b * x + e_stern[:, j]
            xs[:, j], ys[:, j] = x, xn
            x, j = xn, j + 1
    assert j == e_stern.shape[1]
    return xs, ys


# Einheitstest der Rekursion: Residuen in Originalreihenfolge muessen die Daten exakt reproduzieren.
for R, i in PAARE.items():
    xs, ys = regenerieren(R, RES[R][None, :])
    assert np.allclose(xs[0], r[i], atol=1e-12) and np.allclose(ys[0], r[i + 1], atol=1e-12), R

# ---------- Bootstrap ----------------------------------------------------------------------
Z = np.load(BASIS / "Abgaben" / "bootstrap_ziehungen.npz")
IDX = {"Krise": Z["idx_krise"].astype(int), "ruhig": Z["idx_ruhig"].astype(int)}
B = IDX["Krise"].shape[0]
assert B == 2000 and IDX["ruhig"].shape == (B, 231)

STERN = {}
for R in PAARE:
    xs, ys = regenerieren(R, RES[R][IDX[R]])
    b, c, dl = schaetzen(xs, ys)
    a, s = a_sigma(b, dl)
    STERN[R] = dict(b=b, a=a, sigma=s)

aK, sK = a_sigma(PKT["Krise"]["b"], PKT["Krise"]["delta"])
aR, sR = a_sigma(PKT["ruhig"]["b"], PKT["ruhig"]["delta"])
THETA = {"a_Krise": aK, "a_ruhig": aR, "sigma_Krise": sK, "sigma_ruhig": sR,
         "a_Krise/a_ruhig": aK / aR, "sigma_Krise/sigma_ruhig": sK / sR}
STAT = {"a_Krise": STERN["Krise"]["a"], "a_ruhig": STERN["ruhig"]["a"],
        "sigma_Krise": STERN["Krise"]["sigma"], "sigma_ruhig": STERN["ruhig"]["sigma"],
        "a_Krise/a_ruhig": STERN["Krise"]["a"] / STERN["ruhig"]["a"],
        "sigma_Krise/sigma_ruhig": STERN["Krise"]["sigma"] / STERN["ruhig"]["sigma"]}


# ---------- Jackknife-Einflusswerte (Festlegung (2), gewichtete Mehrstichprobenform) -------
def jack_param(R):
    """Delete-one-pair je Regime: liefert a_(i), sigma_(i) fuer alle Paare des Regimes."""
    i = PAARE[R]; n = len(i)
    keep = ~np.eye(n, dtype=bool)
    xs = np.broadcast_to(r[i], (n, n))[keep].reshape(n, n - 1)
    ys = np.broadcast_to(r[i + 1], (n, n))[keep].reshape(n, n - 1)
    b, c, dl = schaetzen(xs, ys)
    return a_sigma(b, dl)


JK = {R: dict(zip(("a", "sigma"), jack_param(R))) for R in PAARE}
TH = {R: dict(zip(("a", "sigma"), a_sigma(PKT[R]["b"], PKT[R]["delta"]))) for R in PAARE}


def beschleunigung(gruppen):
    """gruppen: Liste von Arrays theta_(i) je Regime. U_ki = (n_k-1)(mittel_k - theta_(ki));
    a = 1/6 * sum (U/n_k)^3 / (sum (U/n_k)^2)^(3/2)."""
    num = den = 0.0
    for t in gruppen:
        n = len(t); U = (n - 1) * (t.mean() - t)
        num += ((U / n) ** 3).sum(); den += ((U / n) ** 2).sum()
    return num / 6 / den ** 1.5


ACC = {"a_Krise": beschleunigung([JK["Krise"]["a"]]),
       "a_ruhig": beschleunigung([JK["ruhig"]["a"]]),
       "sigma_Krise": beschleunigung([JK["Krise"]["sigma"]]),
       "sigma_ruhig": beschleunigung([JK["ruhig"]["sigma"]])}
for q in ("a", "sigma"):
    ACC[f"{q}_Krise/{q}_ruhig"] = beschleunigung([JK["Krise"][q] / TH["ruhig"][q],
                                                  TH["Krise"][q] / JK["ruhig"][q]])


# ---------- BCa ----------------------------------------------------------------------------
def quantil(v, p):
    """Lineare Interpolation (= np.quantile Standard), selbst implementiert."""
    v = np.sort(v); pos = (len(v) - 1) * p
    lo = int(np.floor(pos)); hi = min(lo + 1, len(v) - 1)
    return v[lo] + (pos - lo) * (v[hi] - v[lo])


def bca(theta, stern, acc):
    z0 = ndtri(np.mean(stern < theta))  # DiCiccio & Efron Gl. 2.8, strikt "<"
    out = []
    for z in (ndtri(ALPHA / 2), ndtri(1 - ALPHA / 2)):
        p = ndtr(z0 + (z0 + z) / (1 - acc * (z0 + z)))  # Gl. 2.3
        out.append(p)
    return z0, out[0], out[1], quantil(stern, out[0]), quantil(stern, out[1])


zeilen = []
for k in THETA:
    th, st, ac = THETA[k], STAT[k], ACC[k]
    z0, p1, p2, lo, hi = bca(th, st, ac)
    # Festlegung (5): MC-Fehler per Gruppen-Jackknife ueber J = 10 zusammenhaengende Bloecke
    blk = np.array_split(np.arange(B), J_MC)
    L = np.array([bca(th, np.delete(st, g), ac)[3:] for g in blk])
    se = np.sqrt((J_MC - 1) / J_MC * ((L - L.mean(0)) ** 2).sum(0))
    zeilen.append({"Groesse": k, "Punkt": th, "Bootstrap_Mittel": st.mean(),
                   "Verzerrung": st.mean() - th, "Bootstrap_Median": np.median(st),
                   "z0": z0, "Beschleunigung": ac, "Perzentil_unten": p1, "Perzentil_oben": p2,
                   "BCa_unten": lo, "BCa_oben": hi, "MC_SE_unten": se[0], "MC_SE_oben": se[1]})

tab = pd.DataFrame(zeilen).set_index("Groesse")
zaehl = {R: int((STERN[R]["b"] >= 1).sum()) for R in STERN}
pd.set_option("display.width", 250)
print(tab.round(4).to_string())
print("Replikationen mit b* >= 1:", zaehl, "von", B)
if __name__ == "__main__":  # nur bei direktem Aufruf schreiben, nicht beim Import durch Pruefskripte
    tab.to_csv(BASIS / "Abgaben" / "bootstrap_referenz_ergebnisse.csv")
    np.savez_compressed(BASIS / "Abgaben" / "bootstrap_referenz_replikationen.npz",
                        **{k.replace("/", "_zu_"): v for k, v in STAT.items()},
                        b_Krise=STERN["Krise"]["b"], b_ruhig=STERN["ruhig"]["b"])
