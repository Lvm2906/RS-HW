# [Repository copy: absolute Windows paths replaced by paths relative to the repository root; code otherwise unchanged]
from pathlib import Path
BASIS = Path(__file__).resolve().parent.parent
# Datenquelle: hmm_input_changes.csv (Level/Slope/Curvature je Datum) 
#            + key_events.csv (Krisenmarker für den Plot)
#
# Seed: random_state = 42 (fix wegen reproduzierbarkeit)
#
# covariance_type = "full": bewusst, da Level, Slope und Curvature voneinander abhängen


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

print (model.monitor_.converged)

streuung_0 = np.trace(model.covars_[0])
streuung_1 = np.trace(model.covars_[1])

krise = int(np.argmax([streuung_0, streuung_1]))

print (model.means_)

print ("------------------------------")

print (model.covars_)

print ("------------------------------")

print (model.transmat_)

print ("------------------------------")

print ( f"Regime {krise} ist Krise (Streuung {max(streuung_0, streuung_1):.4f})" )

p_krise = model.predict_proba(X)[:, krise]

ziel = pl.Path(__file__).with_name("crisis_plot.png")

events = pd.read_csv(str(BASIS / "Code" / "key_events.csv"), parse_dates=["date"])

plt.figure(figsize=(12, 4))
plt.plot(datum, p_krise)
for d in events["date"]:
    plt.axvline(d, color="red", linestyle="--", alpha=0.3)
plt.xlabel("Datum")
plt.ylabel("P(Krise)")
plt.title("Smoothed P(Krise) über die Zeit")
plt.savefig(ziel, dpi=150, bbox_inches="tight")





