# [Repository copy: absolute Windows paths replaced by paths relative to the repository root; code otherwise unchanged]
from pathlib import Path
BASIS = Path(__file__).resolve().parent.parent
# 2026-07-28_M30_crisis-sanity-check.py
import pandas as pd
import numpy as np
import hmmlearn.hmm as hmm
import matplotlib.pyplot as plt 
import pathlib as pl


seed = 42

df = pd.read_csv(str(BASIS / "Code" / "hmm_input_changes.csv"), parse_dates=["Datum"])

datum = df["Datum"] 

X = df[["Level", "Slope", "Curvature"]].to_numpy()

model = hmm.GaussianHMM(n_components=2, covariance_type="full", n_iter=100, random_state=seed)

model.fit(X)

print ("Konvergiert:", model.monitor_.converged)

streuung = [np.trace(model.covars_[k]) for k in range(2)]

krisen_index = int(np.argmax(streuung))

print("Krisen-Index:", krisen_index)

proba = model.predict_proba(X)

p_krise = proba[:, krisen_index]

ctx = pd.read_csv(str(BASIS / "Code" / "context_events.csv"), parse_dates=["date"])

crisis = ctx[ctx["regime"] == "crisis"]

print ("Krisen-Tage gesamt:", len(crisis))

print ("Erstes Datum :", crisis["date"].min().date())

print ("Letztes Datum:", crisis["date"].max().date())

handelstage = set(datum)

krisen_tage = set(crisis["date"])

im_index = krisen_tage & handelstage

weggefallen = krisen_tage - handelstage

print("Krisen-Tage im Index:", len(im_index))
print("Weggefallen:", len(weggefallen))

print ("Weggefallene Daten:")
for d in sorted(weggefallen):
    print(" ", pd.Timestamp(d).date())

mask = datum.isin(krisen_tage).to_numpy()

p_getaggt = p_krise[mask]

treffer = (p_getaggt > 0.5).mean()

mittel_getaggt = p_getaggt.mean()

basisrate = (p_krise > 0.5).mean()

entschiedenheit = ((p_krise > 0.9) | (p_krise < 0.1)).mean()

tabelle = pd.DataFrame(
    {"Wert": [treffer, mittel_getaggt, basisrate, entschiedenheit]},
    index=[
        "(a) Trefferquote @0.5 (getaggt)",
        "(b) mittleres P(Krise) (getaggt)",
        "(c) Basisrate P>0.5 (alle 377)",
        "(c) Entschiedenheit P>0.9|<0.1",
    ],
)
print(tabelle.round(3))

plt.figure(figsize=(12, 5))
plt.plot(datum, p_krise, label="P(Krise) smoothed")
plt.axvspan(
    crisis["date"].min(),
    crisis["date"].max(),
    color="red",
    alpha=0.15,
    label="getaggter Krisen-Zeitraum",
)
plt.xlabel("Datum")
plt.ylabel("P(Krise)")
plt.title("Krisenwahrscheinlichkeit (smoothed) mit getaggtem Zeitraum")
plt.legend()
plt.tight_layout()
plt.savefig(
    str(BASIS / "Abgaben" / "schritt6_smoothed_getaggt.png"),
    dpi=150,
)
plt.show()

# Sanity-Check Krisen-Regime (M30) — Notiz

# Das getaggte Kontext-File weist 58 Krisen-Tage aus (08.04.2026 bis 29.06.2026)
# Nach Abgleich mit den 377 Handelstagen bleiben 47 Tage übrig, 11 fallen weg
# — davon 10 Wochenendtage und der 29.06. als Tag hinter dem Sample-Ende, also vollständig erklärbar.
# Auf den 47 getaggten Tagen liegt die Trefferquote bei Schwelle 0,5 bei 0,66 und das mittlere P(Krise) bei 0,662. 
# Zum Vergleich beträgt die Basisrate über alle 377 Tage nur 0,353, die Entschiedenheit (P > 0,9 oder P < 0,1) 0,812. Da die Trefferquote mit 0,66 fast doppelt so hoch ist wie die Basisrate von 0,353,
#  zeigt der Check, dass das HMM-Krisenregime tatsächlich mit den extern getaggten Krisen-Tagen zusammenfällt und nicht bloß zufällig oft „Krise" meldet;
# die hohe Entschiedenheit bestätigt, dass das Modell an den meisten Tagen klar Position bezieht. Der Check zeigt nicht, dass das Modell Krisen vorhersagt: der smoothed-Pfad nutzt die gesamte Zeitreihe (Rückschau),
#  es ist also eine In-Sample-Beschreibung, keine Prognose. Ebenso wenig belegt er Kausalität oder die Korrektheit der Tags selbst
# — diese werden hier als Referenz angenommen, nicht validiert.
#
# Reflexionsfrage
#
# Einordnung: 
# Die hohe Trefferquote allein beantwortet die Forschungsfrage (a) noch nicht, denn sie misst nur, ob getaggte Tage erkannt werden, nicht wie viele Fehlalarme das Modell an ruhigen Tagen produziert.
# Deshalb ist die Basisrate entscheidend — erst der Abstand zwischen Trefferquote (0,66) und Basisrate (0,353) ist Evidenz; ein generell „trigger-happy" Regime, das die Krisentage nur zufällig mitnimmt, lässt sich mit diesem Check nicht ausschließen.
# Der smoothed-Pfad ist hier trotzdem zulässig, weil es sich um eine rückblickende Beschreibung der Regime-Zuordnung handelt und nicht um eine Prognose; die Regel „prädiktive Aussagen brauchen den filtered-Pfad" gilt weiter, greift aber nur, sobald eine Echtzeit-Aussage zum Tag $t$ gemacht wird.
# Für eine reine In-Sample-Validierung ist es sogar korrekt, die volle Information der gesamten Reihe zu nutzen. 
# Was dieser Sanity-Check prinzipiell nicht leisten kann, liefert erst der Permutationstest gegen die key_events: eine Signifikanzaussage, ob die Übereinstimmung über reinen Zufall hinausgeht (p-Wert gegen eine Nullverteilung).
#
#
#
