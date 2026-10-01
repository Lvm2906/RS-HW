# 2026-09-20_P2_ar1-schaetzung
#
# Stufe 2, Schritt 5: (a, sigma) je Regime aus dem 3M-Satz schaetzen (Punktschaetzung).
# Kein Bootstrap, keine CIs, keine Materialitaetsaussage (das ist Schritt 6).
#
# Das Vorgehen ist ESTIMATION unter dem physischen Mass aus einer Zeitreihe; es ist keine
# Q-Mass-Anpassung an Derivatepreise. Der Achsenabschnitt c je Regime ist ein
# Stoerparameter; er ist nicht das theta(t) des Hull-White-Modells.
#
# --- Die vier Formeln -------------------------------------------------------------------
# (1) SDE (Brigo et al. 2008, Gl. 47):     dx_t = a (theta - x_t) dt + sigma dW_t
# (2) Exakte Diskretisierung (Gl. 49/52):  x_i = c + b x_{i-1} + delta eps_i, eps ~ N(0,1)
#       b = exp(-a h),  c = theta (1 - exp(-a h)),  delta = sigma sqrt[(1 - exp(-2 a h)) / (2a)]
#     Das ist exakt, denn die OU-Uebergangsdichte ist geschlossen normal. Anders als bei Euler
#     entsteht kein Diskretisierungsfehler, egal wie gross h ist.
# (3) Rueckrechnung a:                      a = -ln(b) / h                    (Gl. 55)
#     (Niveau, nur nachrichtlich:           theta = c / (1 - b)               (Gl. 56))
# (4) Rueckrechnung sigma:                  sigma = delta sqrt[2a / (1 - b^2)]
#     (= Gl. 57 sigma = delta / sqrt[(b^2-1)h / (2 ln b)], denn ln b = -a h)
#
# --- h ----------------------------------------------------------------------------------
# h = 1/252 (ein Handelstag als Jahresbruchteil). Damit ist a in "pro Jahr" und sigma in
# Prozentpunkten pro sqrt(Jahr) angegeben, so wie HW-Parameter ueblicherweise angegeben
# und mit der Literatur verglichen werden. Wochenenden/Feiertage zaehlen nicht als Zeit
# (Handelstagsuhr).
#
# --- ML-Lesart --------------------------------------------------------------------------
# BEDINGTE Maximum Likelihood (bedingt auf den ersten Wert jedes Paares). Fuer das gaussche
# AR(1) liefert sie b, c wie OLS; delta^2_ML = SSR / n (ML-Nenner n, nicht n-2).
# Warum nicht exakt: Die exakte ML setzt voraus, dass der erste Tag jeder Episode aus der
# stationaeren Verteilung N(theta, sigma^2/2a) DES REGIMES stammt. Eine Episode beginnt aber
# direkt nach einem Regimewechsel, und der Startwert ist vom anderen Regime erzeugt. Die
# 7 Randterme je Regime waeren daher fehlspezifiziert. Das praezisiert die registrierte
# Entscheidung "Maximum Likelihood" (METHODIK §2 Pkt. 3) und waehlt nicht neu.
# Beleg fuer die ML-Formeln: van den Berg (2011), nicht Brigo et al. Abschn. 7 (dort nur OLS).
#
# --- Paare ueber nicht zusammenhaengende Episoden (Eigenleistung) -----------------------
# Der Prozess ist markovsch: p(x_1..x_T | x_0) = prod p(x_i | x_{i-1}). Die bedingte
# Likelihood eines Regimes ist das Produkt der Uebergangsdichten seiner behaltenen Paare.
# Ob die Paare zeitlich zusammenhaengen, spielt dafuer keine Rolle.

from pathlib import Path

import numpy as np
import pandas as pd
import hmmlearn.hmm as hmm
from scipy import stats

seed = 42
h = 1 / 252
BASIS = Path(__file__).parent.parent

# --- Regimepfad: identisch zu Stufe 1 ----------------------------------------------------
df = pd.read_csv(BASIS / "Code" / "hmm_input_changes.csv", parse_dates=["Datum"])
X = df[["Level", "Slope", "Curvature"]].to_numpy()
assert X.shape == (377, 3), f"Form war {X.shape}"

model = hmm.GaussianHMM(n_components=2, covariance_type="full", n_iter=100, random_state=seed)
model.fit(X)
assert model.monitor_.converged, "HMM nicht konvergiert"
assert model.monitor_.iter < model.monitor_.n_iter, "EM am Iterationslimit abgebrochen"

spuren = [np.trace(model.covars_[i]) for i in range(2)]
krise = int(np.argmax(spuren))
pfad = model.predict(X)
ist_krise = pfad == krise

# --- 3M-Reihe laden und ausrichten -------------------------------------------------------
yields = pd.read_csv(BASIS / "Code" / "yields.csv", parse_dates=["date"])
assert len(yields) == 378, f"yields.csv hat {len(yields)} Zeilen, erwartet 378"
assert yields["date"].iloc[0] == pd.Timestamp("2025-01-02")
# Der erste Tag geht bei der Aenderungsbildung verloren; die Niveaus auf dem 377er-Index
# sind die von Tag 2 bis 378.
r_df = yields.iloc[1:].reset_index(drop=True)
assert (r_df["date"].to_numpy() == df["Datum"].to_numpy()).all(), "Datumsindex weicht ab"
r = r_df["3M"].to_numpy()
assert len(r) == 377 and not np.isnan(r).any()

# --- Paare bilden, Nahtstellen verwerfen -------------------------------------------------
gleich = pfad[:-1] == pfad[1:]  # Paar (i, i+1) behalten, wenn Label_i == Label_{i+1}
segment = np.concatenate([[0], np.cumsum(pfad[1:] != pfad[:-1])])  # Episoden-ID je Tag
assert len(gleich) == 376
assert (~gleich).sum() == 13, f"Nahtstellen: {(~gleich).sum()}"

idx = {"Krise": np.flatnonzero(gleich & ist_krise[:-1]),
       "ruhig": np.flatnonzero(gleich & ~ist_krise[:-1])}
n_krise, n_ruhig = len(idx["Krise"]), len(idx["ruhig"])
assert n_krise == 132 and n_ruhig == 231, f"Kontrollsumme: {n_krise} / {n_ruhig}"


def schaetzen(i):
    """Bedingte ML fuer x_{i+1} = c + b x_i + delta eps ueber die Paare mit Startindex i."""
    x, y = r[i], r[i + 1]
    A = np.column_stack([np.ones_like(x), x])
    (c, b), *_ = np.linalg.lstsq(A, y, rcond=None)
    e = y - c - b * x
    n = len(e)
    delta = np.sqrt(e @ e / n)  # ML-Nenner n
    return dict(b=b, c=c, delta=delta, e=e, x=x, n=n)


def zurueckrechnen(b, c, delta):
    if not (0 < b < 1):  # Befund "keine messbare Rueckkehr" -> berichten, nicht reparieren
        return np.nan, np.nan, np.nan
    a = -np.log(b) / h
    sigma = delta * np.sqrt(2 * a / (1 - b**2))
    theta = c / (1 - b)
    return a, sigma, theta


# --- Residuendiagnostik -----------------------------------------------------------------
# Autokorrelation nur zwischen Residuen, die im selben Segment k Tage auseinanderliegen.
# Ein Lag ueber eine Nahtstelle wuerde Tage verbinden, die real Wochen trennen.
def ljung_box(e, start, lags):
    seg = segment[start]
    n, nenner = len(e), e @ e
    pos = {s: j for j, s in enumerate(start)}
    rho = []
    for k in range(1, lags + 1):
        z = sum(e[j] * e[pos[s + k]] for j, s in enumerate(start)
                if s + k in pos and seg[pos[s + k]] == seg[j])
        rho.append(z / nenner)
    rho = np.array(rho)
    Q = n * (n + 2) * np.sum(rho**2 / (n - np.arange(1, lags + 1)))
    return Q, stats.chi2.sf(Q, lags)


def lm_test(u, Z):
    """LM = n R^2 aus Hilfsregression u auf [1, Z]; df = Spalten von Z."""
    A = np.column_stack([np.ones(len(u)), Z])
    beta, *_ = np.linalg.lstsq(A, u, rcond=None)
    res = u - A @ beta
    R2 = 1 - res @ res / np.sum((u - u.mean())**2)
    LM = len(u) * R2
    return LM, stats.chi2.sf(LM, A.shape[1] - 1)


def arch_lm1(e, start):
    """ARCH-LM(1): e^2_t auf e^2_{t-1}, nur fuer im Segment benachbarte Residuen."""
    pos = {s: j for j, s in enumerate(start)}
    paare = [(pos[s - 1], j) for j, s in enumerate(start)
             if s - 1 in pos and segment[s - 1] == segment[s]]
    vor, nach = np.array(paare).T
    return lm_test(e[nach]**2, e[vor]**2)


zeilen, diag = [], []
for name, i in idx.items():
    s = schaetzen(i)
    a, sigma, theta = zurueckrechnen(s["b"], s["c"], s["delta"])
    zeilen.append({"Regime": name, "b": s["b"], "c": s["c"], "delta": s["delta"],
                   "a [1/J]": a, "sigma [pp/sqrtJ]": sigma, "theta_nachr.": theta,
                   "n Paare": s["n"]})

    lb5, lb10 = ljung_box(s["e"], i, 5), ljung_box(s["e"], i, 10)
    bp = lm_test(s["e"]**2, s["x"])  # Breusch-Pagan: Varianz haengt am Niveau?
    arch = arch_lm1(s["e"], i)       # Varianz-Clustering innerhalb der Episoden?
    diag.append({"Regime": name, "LB(5) p": lb5[1], "LB(10) p": lb10[1],
                 "BP (Niveau) p": bp[1], "ARCH-LM(1) p": arch[1],
                 "JB p": stats.jarque_bera(s["e"]).pvalue})

tab = pd.DataFrame(zeilen).set_index("Regime")
dtab = pd.DataFrame(diag).set_index("Regime")

print(f"Krisenzustand = {krise} (Spuren {np.round(spuren, 3)}); h = 1/252")
print(f"Paare: 376 gesamt, 13 Nahtstellen verworfen, {n_krise} Krise / {n_ruhig} ruhig\n")
print("Punktschaetzung (bedingte ML):")
print(tab.round(4).to_string(), "\n")
print("Residuendiagnostik (p-Werte):")
print(dtab.round(4).to_string(), "\n")

for name, zeile in tab.iterrows():
    if not (0 < zeile["b"] < 1):
        print(f"BEFUND {name}: b = {zeile['b']:.4f} ausserhalb (0,1) -> keine messbare Rueckkehr")

hetero = (dtab[["BP (Niveau) p", "ARCH-LM(1) p"]] < 0.05).any().any()
print("Heteroskedastizitaet (alpha = 5 %):", "JA -> Wild Bootstrap in Schritt 6" if hetero
      else "nein -> normaler Residuen-Bootstrap in Schritt 6")

tab.join(dtab).to_csv(BASIS / "Abgaben" / "ar1_schaetzung.csv")
