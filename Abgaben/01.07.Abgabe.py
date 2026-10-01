# [Repository copy: absolute Windows paths replaced by paths relative to the repository root; code otherwise unchanged]
from pathlib import Path
BASIS = Path(__file__).resolve().parent.parent
import numpy as np
import pandas as pd
import sklearn as skLearn

np.random.seed(42)

df = pd.read_csv(str(BASIS / "Code" / "yields.csv"), parse_dates=["date"])

zinsen = df[["3M", "6M", "1Y", "2Y", "3Y", "5Y", "7Y", "10Y", "15Y", "20Y", "30Y"]]

datum = df["date"]

scaler = skLearn.preprocessing.StandardScaler ()

zinsen_skaliert = scaler.fit_transform ( zinsen )


modell = skLearn.decomposition.PCA(n_components=3)

pca = modell.fit_transform (zinsen_skaliert)


laufzeiten = ["3M", "6M", "1Y", "2Y", "3Y", "5Y", "7Y", "10Y", "15Y", "20Y", "30Y"]

loadings = pd.DataFrame(modell.components_, columns=laufzeiten, index=["Level", "Slope", "Curvature"])

scores = pd.DataFrame(pca, columns=["Level", "Slope", "Curvature"])

scores.insert(0,"Datum", datum.values)

scores_sorted = scores.sort_values("Datum")

aenderungen = scores_sorted[["Level", "Slope", "Curvature"]].diff()

aenderungen.insert(0, "Datum", scores_sorted["Datum"])

scores_final = aenderungen.copy()

scores_final_sauber = scores_final.dropna()

abstaende = scores_final_sauber["Datum"].diff().dt.days


# ENTSCHEIDUNG / KOMMENTAR:
# Die Abstände sind bewusst ungleichmäßig:
#   1 Tag  = normale aufeinanderfolgende Handelstage
#   3 Tage = Wochenenden (Fr -> Mo)
#   4-5 Tage = Feiertage (Ostern, Weihnachten/Neujahr, Mai-Feiertag)
# Das sind KEINE fehlenden Daten, sondern handelsfreie Tage (Wochenende/Feiertag),
# an denen es an den Zinsmärkten keine Kurse gibt.
# -> Entscheidung: Lücken AKZEPTIEREN. Kein Auffüllen/Interpolieren, weil das
#    künstliche Zinsänderungen erfinden würde, die real nie stattfanden.

scores_final_sauber.to_csv(str(BASIS / "Code" / "hmm_input_changes.csv"), index=False)

print ("CSV gespeichert.")