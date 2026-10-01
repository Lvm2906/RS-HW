# [Repository copy: absolute Windows paths replaced by paths relative to the repository root; code otherwise unchanged]
from pathlib import Path
BASIS = Path(__file__).resolve().parent.parent
# 2026-07-24_M29_filtered-vs-smoothed
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

streuung = [np.trace(model.covars_[k]) for k in range(2)]

krisen_index = int(np.argmax(streuung))

print("Krisen-Index:", krisen_index)

proba = model.predict_proba(X)

p_krise = proba[:, krisen_index]

print("Länge:", len(p_krise))

print("Min/Max:", p_krise.min(), p_krise.max())

p_krise_filtered = np.array([
    model.predict_proba(X[:t+1])[-1, krisen_index]
    for t in range(len(X))
])


plt.figure(figsize=(12, 5))
plt.plot(datum, p_krise_filtered, label="filtered")
plt.plot(datum, p_krise, label="smoothed")

plt.xlabel("Datum")
plt.ylabel("P(Krise)")
plt.title("Krisenwahrscheinlichkeit: filtered vs. smoothed")
plt.legend()
plt.tight_layout()

plt.savefig(str(BASIS / "Abgaben" / "krisenwahrscheinlichkeit.png"), dpi=150)
plt.show()

# Check
import os
print("PNG existiert:", os.path.exists("krisenwahrscheinlichkeit.png"))
