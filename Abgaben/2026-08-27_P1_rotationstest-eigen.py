# 2026-08-27_P1_rotationstest-eigen

from pathlib import Path

import numpy as np
import pandas as pd
import hmmlearn.hmm as hmm

seed = 42
BASIS = Path(__file__).parent.parent

# 377 Handelstage (03.01.2025–26.06.2026) · 26 Ereignisse · Seed 42
# In diesem Code wird eine Rotationstest-Analyse durchgeführt, um zu prüfen, ob dokumentierte Ereignisse häufiger nahe an Regimewechseln liegen als unter Zufall.
# 1. Wir verwenden den zirkulären Shift, da bei freier Permutation die Klumpung der Ereignisse zerstört werden würde und auch ihre zeitliche Anordnung. Diese Methode verwenden auch Lotwick & Silverman (1982) in der räumlichen Statistik, wir übertragen das Prinzip auf die Zeitreihenanalyse.
# 2. Wir verwenden den Zählvektor statt des Ja/Nein-Vektors. Die Zählweise selbst ist eine vorab registrierte Entscheidung: D1 wählt Ereignisse (26) statt Ereignistage (25), weil nach B5 der 20.06. auf den 22.06. wandert, wo schon ein Ereignis liegt, und B6 beide als eigenständige Akte führt. Der Zählvektor (np.add.at) setzt diese Wahl technisch um — er ersetzt sie nicht. Ein boolescher Vektor würde das zweite Ereignis lautlos löschen und damit ohne Fehlermeldung gegen D1 testen; assert v.sum() == 26 macht das sichtbar.
# 3. Wir zählen alle Verschiebungen vollständig auf, statt zu ziehen: Eine zyklische Verschiebung ist durch τ vollständig bestimmt, und τ kann nur 377 Werte annehmen — die Menge der möglichen Verschiebungen ist endlich und klein. Deshalb ist p exakt statt geschätzt und der Lauf billiger obendrein.
# 4. Wir zählen τ = 0 mit, da diese die unverschobene Beobachtung ist, und fehlt diese, dann kann p = 0 werden. Nach Phipson & Smyth darf p nicht = 0 sein. p = 0 behauptet, die Beobachtung sei unter H0 unmöglich, sie ist aber eine der 377 zulässigen. Diese behandeln jedoch zufällige Permutationen, wir übertragen somit nur dieses Prinzip.

def maske_bauen(wechsel, k, n):
    maske = np.zeros(n, dtype=int)
    for w in wechsel:
        start = max(0, w-k)
        ende = min(n-1, w + k)
        maske[start:ende+1] = 1
    return maske

def teststatistik(v, maske):
    return int(np.dot(v, maske))

def rotationstest(v, maske):
    n = len(v)
    T_obs = teststatistik(v, maske)
    null = np.zeros(n, dtype=int)
    for tau in range(n):
        null[tau] = teststatistik(np.roll(v, tau), maske)
    assert null[0] == T_obs, "tau=0 muss T_obs reproduzieren"
    p = (null >= T_obs).mean()
    return T_obs, null, p

def selbsttest():
    n = 10
    v = np.zeros(n, dtype=int)
    np.add.at(v, [2, 3, 4], 1)
    maske = maske_bauen(wechsel=[8], k=2, n=n)

    assert list(np.flatnonzero(maske)) == [6, 7, 8, 9], f"Maske war {np.flatnonzero(maske)}"
    assert teststatistik(v, maske) == 0, f"T_obs war {teststatistik(v, maske)}"
    assert teststatistik(np.roll(v, 5), maske) == 3, f"T(5) war {teststatistik(np.roll(v, 5), maske)}"
    assert teststatistik(np.roll(v, 3), maske) == 2, f"T(3) war {teststatistik(np.roll(v, 3), maske)}"
    print("Selbsttest gruen")

selbsttest()

df = pd.read_csv(BASIS / "Code" / "hmm_input_changes.csv", parse_dates=["Datum"])

datum = df["Datum"]

X = df[["Level", "Slope", "Curvature"]].to_numpy()
assert X.shape == (377, 3), f"Form war {X.shape}"

model = hmm.GaussianHMM(n_components=2, covariance_type="full", n_iter=100, random_state=seed)
model.fit(X)
assert model.monitor_.converged, "Hmm nicht konvergiert"
assert model.monitor_.iter < model.monitor_.n_iter, \
    f"EM am Iterationslimit abgebrochen ({model.monitor_.iter})"

spuren = [np.trace(model.covars_[i]) for i in range(2)]
krise = int(np.argmax(spuren))
print("Kovarianz-Spuren:", np.round(spuren, 3), "-> Krisenzustand:", krise)

pfad = model.predict(X)
wechsel = np.flatnonzero(np.diff(pfad) !=0) + 1
print("Anzahl Wechsel:", len(wechsel))

for k_ in (1, 2, 3):
    print(f"k={k_}: Maske deckt {maske_bauen(wechsel, k_, len(datum)).sum()} Tage")

ereignisse = pd.read_csv(BASIS / "Code" / "key_events.csv", parse_dates=["date"])
handelstage = df["Datum"].to_numpy()

pos = np.searchsorted(handelstage, ereignisse["date"].to_numpy(), side="left")
assert pos.max() < len(handelstage), "Ereignis liegt hinter dem letzten Handelstag"

v= np.zeros(len(handelstage), dtype=int)
np.add.at(v, pos, 1)
assert v.sum() == 26, f"Kontrollsumme war {v.sum()}, erwartet 26"

zugeordnet = handelstage[pos]
verschoben = ereignisse["date"].to_numpy() != zugeordnet
print("Nach B5 verschoben:", verschoben.sum())
for d, z in zip(ereignisse["date"][verschoben], zugeordnet[verschoben]):
    print(f"{d.date()} -> {pd.Timestamp(z).date()}")
print("Tage mit zwei Ereignissen:", np.flatnonzero(v == 2))

maske = maske_bauen(wechsel, k=2, n=len(v))
T_obs, null, p = rotationstest(v, maske)
print(f"Primaerzelle (Viterbi, alle 26, k=2): T_obs = {T_obs}, p = {p:.4f}")

post_krise = model.predict_proba(X)[:, krise]
pfad_05 = (post_krise > 0.5).astype(int)
wechsel_05 = np.flatnonzero(np.diff(pfad_05) != 0) + 1

daten = ereignisse["date"]
assert daten.is_monotonic_increasing, "key_events.csv ist nicht nach Datum sortiert"
ist_hormus = ereignisse["event"].str.startswith("hormus_").to_numpy()

behalten, vorher = [], None
for i in range(len(ereignisse)):
    if not ist_hormus[i]:
        behalten.append(i)
    else:
        if vorher is None or (daten.iloc[i] - daten.iloc[vorher]).days > 14:
            behalten.append(i)
        vorher = i

v_ep = np.zeros(len(handelstage), dtype=int)
np.add.at(v_ep, pos[behalten], 1)
assert v_ep.sum() == 22, f"Episodenzahl war {v_ep.sum()}, erwartet 22"
assert (v_ep <= 1).all(), "Episoden sollen auf 22 eindeutigen Handelstagen liegen"

print("Wechsel 0.5-Kreuzung:", len(wechsel_05))

assert v_ep.sum() == 22

zeilen = []
for wname, w in {"viterbi": wechsel, "kreuzung": wechsel_05}.items():
    for ename, ev in {"alle26": v, "episoden22": v_ep}.items():
        for k in(1, 2, 3):
            m = maske_bauen(w, k, len(ev))
            T, null, p = rotationstest(ev, m)
            # Erwartungswert unter H0: Ereigniszahl x Anteil der Maskentage am Sample.
            # Ohne ihn ist nicht lesbar, warum T_obs = 9 bei Erwartung 4,276 nicht signifikant ist.
            erwartet = ev.sum() * m.sum() / len(ev)
            # Nur die Primaerzelle ist der Test (Praereg. §5); die uebrigen elf sind
            # angemeldete Robustheitspruefungen - berichtet, nicht gegen alpha geprueft.
            rolle = "TEST" if (wname, ename, k) == ("viterbi", "alle26", 2) else "Robustheit"
            zeilen.append({"rolle": rolle, "wechsel": wname, "ereignisse": ename, "k": k,
                           "mask_tage": int(m.sum()), "T_obs": T,
                           "E_T_H0": round(erwartet, 3), "p": round(p, 4)})

tabelle = pd.DataFrame(zeilen)
print(tabelle.to_string(index=False))
tabelle.to_csv(BASIS / "Abgaben" / "rotationstest.csv", index=False)
