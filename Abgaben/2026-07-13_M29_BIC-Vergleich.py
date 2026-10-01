# [Repository copy: absolute Windows paths replaced by paths relative to the repository root; code otherwise unchanged]
from pathlib import Path
BASIS = Path(__file__).resolve().parent.parent
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from hmmlearn import hmm

seed = 42

X = pd.read_csv(str(BASIS / "Code" / "hmm_input_changes.csv"), index_col="Datum")

print( X.head())
print( X.shape)

m1 = hmm.GaussianHMM(n_components=1, covariance_type="full", n_iter=100, random_state=42).fit(X)

m2 = hmm.GaussianHMM(n_components=2, covariance_type="full", n_iter=100, random_state=42).fit(X)

print( "1 Regime converged:",m1.monitor_.converged)
print( "2 Regime converged:", m2.monitor_.converged)

logL_1 = m1.score(X)

logL_2 = m2.score(X)

print (logL_1)
print (logL_2)

# Parameterzahl k
# m1: k1 = 0 + 0 + 3 + 6 = 9
# m2: k2 = 1 + 2 + 6 + 12 = 21

k1 = 9

k2 = 21


BIC_1_hand = -2 * logL_1 + 9 * np.log(377)

BIC_2_hand = -2 * logL_2 + 21 * np.log(377)


BIC_1 = m1.bic(X)

BIC_2 = m2.bic(X)

print (BIC_1)
print (BIC_2)


print (BIC_1_hand)
print (BIC_2_hand)

print (np.isclose(BIC_1, BIC_1_hand))
print (np.isclose(BIC_2, BIC_2_hand))

delta = BIC_1 - BIC_2

daten = {
    "log L": [logL_1, logL_2],
    "k": [9,21],
    "BIC": [BIC_1, BIC_2],

}

df = pd.DataFrame(daten, index=["1 Regime", "2 Regime"])

print (df.round(2))
print (f"\nΔBIC = {abs(delta):.2f} zugunsten {'2 Regime' if delta > 0 else '1 Regime'}")



#Ergebnis
#------------------------------------------
#               Level     Slope  Curvature
#Datum                                    
#2025-01-03  0.777950 -0.126868  -0.239924
#2025-01-06  0.860038  0.236086   0.133435
#2025-01-07 -0.152618 -0.068859   0.339356
#2025-01-08  0.829235  0.009492   0.263113
#2025-01-09  0.088191 -0.125076  -0.130558
#(377, 3)
#1 Regime converged: True
#2 Regime converged: True
#95.95602005717764
#235.59878188335924
#-138.52183342732317
#-346.6204148303102
#-138.52183342732317
#-346.6204148303102
#True
#True
#           log L   k     BIC
#1 Regime   95.96   9 -138.52
#2 Regime  235.60  21 -346.62
#
#ΔBIC = 208.10 zugunsten 2 Regime

#Notiz
#Regime 2 hat ein niedrigeres BIC als Regime 1 mit einem Delta von 208.10.
#Das heißt, dass von 2 Regimen ausgegangen werden sollte, da die Anpassung, trotz Bestrafung der vergleichweisen hohen Parameterzahl, trotzdem besser ist.



