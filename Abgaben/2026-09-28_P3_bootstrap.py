# [Repository note: the functions marked "TODO Klaus" were written by Claude (Claude Code, 28.09.2026), not by the author; see README. Code otherwise unchanged.]
# 2026-09-28_P3_bootstrap
#
# Stufe 2, Schritt 6: Residuen-Bootstrap, BCa-Intervalle fuer (a, sigma) je Regime und die Verhaeltnisse.
# Verfahren verbindlich: METHODIK §2 Pkt. 4 inkl. "Festlegungen 28.09.2026" (A), (1)-(5).
#
# ARBEITSTEILUNG
#   Mechanik (Cowork): Laden, Regimepfad, Paare, Schaetzfunktion (aus deiner P2-Abgabe uebernommen),
#   Ziehungen laden, Replikationsschleife, Jackknife-Schleife, MC-Fehler, Ausgabe, Abgleich.
#   DEIN TEIL - die drei Funktionen mit "TODO Klaus":
#     (1) rueckrechnen_bs(b, delta)       a, sigma fuer ALLE b > 0 (Festlegung (1): auch b >= 1)
#     (2) regenerieren(R, e_stern)        eine Replikation: je Episode rekursiv ab beobachtetem Starttag
#     (3) bca(theta, stern, theta_jack)   z0, Beschleunigung, korrigierte Perzentile, Endpunkte
#   Nichts ausserhalb dieser drei Funktionen muss geaendert werden.
#
# ABGLEICH: Am Ende wird gegen Abgaben/bootstrap_referenz_ergebnisse.csv (Code/bootstrap_referenz.py,
# unabhaengige Implementierung, dieselben Ziehungen) verglichen. Erwartet: Abweichung ~1e-10.

from pathlib import Path

import numpy as np
import pandas as pd
import hmmlearn.hmm as hmm
from scipy.special import ndtr, ndtri  # Standardnormal: ndtr = Phi, ndtri = Phi^-1

seed, h, ALPHA, J_MC = 42, 1 / 252, 0.05, 10
BASIS = Path(__file__).parent.parent

# --- Regimepfad: identisch zu Stufe 1 / P2 ------------------------------------------------
df = pd.read_csv(BASIS / "Code" / "hmm_input_changes.csv", parse_dates=["Datum"])
X = df[["Level", "Slope", "Curvature"]].to_numpy()
model = hmm.GaussianHMM(n_components=2, covariance_type="full", n_iter=100, random_state=seed)
model.fit(X)
assert model.monitor_.converged
krise = int(np.argmax([np.trace(model.covars_[i]) for i in range(2)]))
pfad = model.predict(X)
ist_krise = pfad == krise

yields = pd.read_csv(BASIS / "Code" / "yields.csv", parse_dates=["date"])
r_df = yields.iloc[1:].reset_index(drop=True)
assert (r_df["date"].to_numpy() == df["Datum"].to_numpy()).all()
r = r_df["3M"].to_numpy()

# --- Episoden und Paare -----------------------------------------------------------------------
# EPISODEN[R] = Liste (start, ende) der Tagesindizes je Episode, chronologisch, ende inklusive.
grenzen = np.flatnonzero(pfad[1:] != pfad[:-1]) + 1
starts, enden = np.r_[0, grenzen], np.r_[grenzen - 1, len(pfad) - 1]
EPISODEN = {"Krise": [(s, e) for s, e in zip(starts, enden) if ist_krise[s]],
            "ruhig": [(s, e) for s, e in zip(starts, enden) if not ist_krise[s]]}
# PAARE[R] = Startindex i jedes behaltenen Paares (i, i+1), chronologisch. Spalte j der Ziehungsmatrix
# und Residuum j gehoeren zum j-ten Paar in dieser Reihenfolge.
PAARE = {R: np.concatenate([np.arange(s, e) for s, e in ep]) for R, ep in EPISODEN.items()}
assert len(PAARE["Krise"]) == 132 and len(PAARE["ruhig"]) == 231


def schaetzen(x, y):
    """Bedingte ML (aus P2): b, c wie OLS, delta^2 = SSR/n. Gibt b, c, delta, Residuen zurueck."""
    A = np.column_stack([np.ones_like(x), x])
    (c, b), *_ = np.linalg.lstsq(A, y, rcond=None)
    e = y - c - b * x
    return b, c, np.sqrt(e @ e / len(e)), e


PKT, RES = {}, {}
for R, i in PAARE.items():
    b, c, delta, e = schaetzen(r[i], r[i + 1])
    PKT[R] = dict(b=b, c=c, delta=delta)
    RES[R] = e


# ============================ TODO Klaus (1) ====================================================
def rueckrechnen_bs(b, delta):
    """a [1/J] und sigma [pp/sqrtJ] aus (b, delta), h = 1/252.
    Anders als zurueckrechnen() in P2: KEIN NaN fuer b >= 1 (Festlegung (1)) - a wird dann <= 0,
    sigma muss stetig ueber b = 1 hinweg definiert sein. Nur b > 0 muss funktionieren.
    Rueckgabe: (a, sigma)."""
    a = -np.log(b) / h
    if b == 1:
        # 0/0 in 2a/(1-b^2): Grenzwert 2a/(1-b^2) -> 1/h, also sigma -> delta/sqrt(h)
        return a, delta / np.sqrt(h)
    # b > 1: a < 0 und 1 - b^2 < 0, der Bruch bleibt positiv - dieselbe Formel gilt weiter
    return a, delta * np.sqrt(2 * a / (1 - b**2))


# ============================ TODO Klaus (2) ====================================================
def regenerieren(R, e_stern):
    """Eine Bootstrap-Replikation fuer Regime R.
    e_stern: Array der Laenge n_R mit gezogenen Residuen; e_stern[j] gehoert zum j-ten Paar (chronologisch).
    Je Episode (s, e) in EPISODEN[R]: Start beim BEOBACHTETEN Wert r[s], dann rekursiv mit
    PKT[R]["c"], PKT[R]["b"] weiter bis Tag e.
    Rueckgabe: (x, y) - zwei Arrays der Laenge n_R, die Paare (x_j, y_j) der neuen Reihe in derselben
    Reihenfolge wie PAARE[R]."""
    c, b = PKT[R]["c"], PKT[R]["b"]
    x, y = np.empty(len(e_stern)), np.empty(len(e_stern))
    j = 0  # laeuft ueber alle Episoden durch, nicht je Episode neu
    for s, e in EPISODEN[R]:
        vorwert = r[s]  # beobachteter erster Tag der Episode
        for t in range(s + 1, e + 1):
            neu = c + b * vorwert + e_stern[j]  # neu erzeugter Vorwert, nicht r[t-1]
            x[j], y[j] = vorwert, neu
            vorwert = neu
            j += 1
    assert j == len(e_stern)
    return x, y


# ============================ TODO Klaus (3) ====================================================
def bca(theta, stern, theta_jack):
    """BCa-Intervall, 1 - ALPHA, nach DiCiccio & Efron (1996) und METHODIK Festlegung (2).
    theta:      Punktschaetzung
    stern:      Array der B Bootstrap-Werte
    theta_jack: LISTE von Arrays, eines je Regime, das in die Groesse eingeht; Eintrag i = Groesse
                neu geschaetzt ohne Paar i dieses Regimes. (Einzelparameter: Liste mit einem Array;
                Verhaeltnis: Liste mit zwei Arrays.)
    Konventionen (METHODIK): z0 mit strikt "<"; Beschleunigung in der gewichteten
    Mehrstichprobenform; Endpunkte als np.quantile(stern, p) (lineare Interpolation).
    Rueckgabe: dict(z0=, acc=, p_unten=, p_oben=, unten=, oben=)."""
    stern = np.asarray(stern)
    z0 = ndtri(np.mean(stern < theta))  # Gl. 2.8, strikt "<"
    # Gl. 6.6/6.7, gewichtete Mehrstichprobenform: U_ki = (n_k - 1)(Mittel - Einzelwert), dann / n_k
    u = np.concatenate([(len(tj) - 1) * (np.mean(tj) - tj) / len(tj) for tj in map(np.asarray, theta_jack)])
    acc = (u**3).sum() / (6 * (u**2).sum() ** 1.5)
    z = ndtri(np.array([ALPHA / 2, 1 - ALPHA / 2]))
    p = ndtr(z0 + (z0 + z) / (1 - acc * (z0 + z)))  # Gl. 2.3
    unten, oben = np.quantile(stern, p)
    return dict(z0=z0, acc=acc, p_unten=p[0], p_oben=p[1], unten=unten, oben=oben)


# ============================ ab hier Mechanik ==================================================
# Einheitstest (2): Originalresiduen in Originalreihenfolge muessen die Daten exakt reproduzieren.
for R, i in PAARE.items():
    x, y = regenerieren(R, RES[R])
    assert np.allclose(x, r[i]) and np.allclose(y, r[i + 1]), f"Rekursion reproduziert Daten nicht ({R})"
# Einheitstest (1): fuer 0 < b < 1 identisch mit der P2-Rueckrechnung.
for R in PKT:
    a, s = rueckrechnen_bs(PKT[R]["b"], PKT[R]["delta"])
    b = PKT[R]["b"]
    assert np.isclose(a, -np.log(b) / h) and np.isclose(s, PKT[R]["delta"] * np.sqrt(2 * a / (1 - b**2)))

Z = np.load(BASIS / "Abgaben" / "bootstrap_ziehungen.npz")
IDX = {"Krise": Z["idx_krise"].astype(int), "ruhig": Z["idx_ruhig"].astype(int)}
B = IDX["Krise"].shape[0]

STERN = {R: {"b": np.empty(B), "a": np.empty(B), "sigma": np.empty(B)} for R in PAARE}
for rep in range(B):
    for R in PAARE:  # beide Regime in derselben Replikation (gepaart)
        x, y = regenerieren(R, RES[R][IDX[R][rep]])
        b, c, delta, _ = schaetzen(x, y)
        a, s = rueckrechnen_bs(b, delta)
        STERN[R]["b"][rep], STERN[R]["a"][rep], STERN[R]["sigma"][rep] = b, a, s

# Jackknife: je ein Paar weglassen, neu schaetzen (Festlegung (2))
JACK = {R: {"a": np.empty(len(i)), "sigma": np.empty(len(i))} for R, i in PAARE.items()}
for R, i in PAARE.items():
    for k in range(len(i)):
        ohne = np.delete(i, k)
        b, c, delta, _ = schaetzen(r[ohne], r[ohne + 1])
        JACK[R]["a"][k], JACK[R]["sigma"][k] = rueckrechnen_bs(b, delta)

PUNKT = {R: dict(zip(("a", "sigma"), rueckrechnen_bs(PKT[R]["b"], PKT[R]["delta"]))) for R in PKT}
GROESSEN = {}
for q in ("a", "sigma"):
    for R in ("Krise", "ruhig"):
        GROESSEN[f"{q}_{R}"] = (PUNKT[R][q], STERN[R][q], [JACK[R][q]])
    GROESSEN[f"{q}_Krise/{q}_ruhig"] = (
        PUNKT["Krise"][q] / PUNKT["ruhig"][q],
        STERN["Krise"][q] / STERN["ruhig"][q],
        [JACK["Krise"][q] / PUNKT["ruhig"][q], PUNKT["Krise"][q] / JACK["ruhig"][q]])

zeilen = []
for name, (theta, stern, tj) in GROESSEN.items():
    erg = bca(theta, stern, tj)
    # Festlegung (5): MC-Fehler der Endpunkte, Gruppen-Jackknife ueber J = 10 Bloecke (Efron & Narasimhan)
    L = np.array([[bca(theta, np.delete(stern, g), tj)[k] for k in ("unten", "oben")]
                  for g in np.array_split(np.arange(B), J_MC)])
    se = np.sqrt((J_MC - 1) / J_MC * ((L - L.mean(0)) ** 2).sum(0))
    zeilen.append({"Groesse": name, "Punkt": theta, "Bootstrap_Mittel": stern.mean(),
                   "Verzerrung": stern.mean() - theta, "Bootstrap_Median": np.median(stern),
                   "z0": erg["z0"], "Beschleunigung": erg["acc"],
                   "Perzentil_unten": erg["p_unten"], "Perzentil_oben": erg["p_oben"],
                   "BCa_unten": erg["unten"], "BCa_oben": erg["oben"],
                   "MC_SE_unten": se[0], "MC_SE_oben": se[1]})

tab = pd.DataFrame(zeilen).set_index("Groesse")
pd.set_option("display.width", 250)
print(tab.round(4).to_string())
print("Replikationen mit b* >= 1:", {R: int((STERN[R]["b"] >= 1).sum()) for R in STERN}, "von", B)
tab.to_csv(BASIS / "Abgaben" / "bootstrap_ergebnisse.csv")

# --- Abgleich mit der Referenzimplementierung ---------------------------------------------------
ref = pd.read_csv(BASIS / "Abgaben" / "bootstrap_referenz_ergebnisse.csv", index_col=0)
abw = ((tab - ref).abs() / ref.abs().clip(lower=1e-12)).max().max()
print(f"max. relative Abweichung zur Referenz: {abw:.2e}")
assert abw < 1e-8, "Abweichung zur Referenzimplementierung - Zeile fuer Zeile pruefen"
