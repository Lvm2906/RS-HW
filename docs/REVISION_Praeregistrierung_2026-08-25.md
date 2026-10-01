# Überarbeitung — `PRAEREGISTRIERUNG_Permutationstest_2026-08-25.md`

**Prüfer:** Cowork · **Datum:** 25.08.2026 · **Ergebnis: freigegeben nach drei Ergänzungen.**
Der Entwurf wurde gegen die Dateien nachgerechnet. **Alle Zahlen stimmen** — 13 Wechsel
(Positionen 9, 14, 22, 41, 47, 64, 108, 141, 148, 295, 358, 366, 368), 14 Segmente,
7 Krisenepisoden, 139 Krisentage; Nähe-Abdeckung 38/62/83 Tage bei k = 1/2/3
(10,08 / 16,45 / 22,02 %); erwartete Treffer 26 × 0,1645 = 4,277 ≈ 4,28; 18/377 = 0,0477,
19/377 = 0,0504, 1/377 = 0,00265; Zweitspezifikation 17 Wechsel / 9 Episoden / 133 Krisentage /
8 abweichende Tage. Aufbau, α-Regelung und Limitationen: kein Einwand.

---

## 1. PFLICHT — §5, Achse (ii): „eine je Episode" ist nicht definiert

So wie es dasteht, bliebe nach dem Blick aufs Ergebnis entscheidbar, was eine Episode ist —
genau der Freiheitsgrad, den die Vorab-Registrierung schließen soll. **Bitte einsetzen:**

> Als **eine Episode** gelten aufeinanderfolgende Zeilen desselben thematischen Strangs, zwischen
> denen höchstens **14 Kalendertage** liegen; die Episode wird durch ihre **erste** Zeile (den
> Auslöser) vertreten. Angewandt auf den Hormus-Strang: 07.06., 14.06., 20.06. und 22.06. bilden
> **eine** Episode, vertreten durch den 07.06. (Zuordnung nach B5 → 08.06.). Der 28.02. und der
> 15.04. bleiben eigenständig (46 bzw. 53 Kalendertage Abstand zur jeweils nächsten Zeile).
> **Ereigniszahl der Zweitspezifikation: 23.**

---

## 2. KLARSTELLUNG — §4: Nähe-Maske ist nicht zirkulär

Die Maske wird aus dem festen Regimepfad gebildet und rotiert **nicht** mit; nur die Ereignisse
rotieren. Das ist richtig so — die Sample-Ränder sind echt, die Naht ist bedeutungslos. Es gehört
aber auf Papier, sonst fragt ein Gutachter danach. **Bitte einsetzen:**

> Die Nähe-Maske wird **nicht-zirkulär** gebildet: Sie beschreibt den festen Regimepfad, dessen
> Ränder echte Sample-Grenzen sind. Da der randnächste Wechsel **8 Positionen** vom Sample-Ende
> und **9** vom Anfang entfernt liegt, stimmt sie für k ≤ 3 mit der zirkulären Variante **exakt**
> überein (38 / 62 / 83 Tage in beiden Fällen). Der Wrap-around betrifft also ausschließlich die
> Ereignisse, nicht die Maske.

---

## 3. KLARSTELLUNG — §4: Einheit der Verschiebung

Ein halber Satz, damit die Operationalisierung eindeutig ist:

> Die Verschiebung um τ bewegt die Ereignisse um **τ Handelstage** (Indexpositionen), nicht um
> Kalendertage.

---

## 4. EMPFEHLUNG — Commit vor dem Lauf

Die Datei **ins Git-Repository committen, bevor das Skript läuft.** Dann ist „geschrieben, bevor
T_obs berechnet wurde" nicht behauptet, sondern über den Commit-Zeitstempel belegbar — und das
öffentliche Repository ist ohnehin zugesagt. Kostet eine Minute und ist der Unterschied zwischen
einer Vorab-Registrierung und der Erzählung einer solchen.

---

## Sonst nichts

Keine Änderung an α, an der Spezifikationsstruktur, am Berichtsraster oder an den Limitationen.
Das 2 × 2 × 3-Raster mit genau einer Testzelle ist die sauberste hier mögliche Lösung des
Multiplizitätsproblems. Der Selbsttest enthält die korrigierten Werte (T_obs = 0, τ = 5 → 3,
τ = 3 → **2**).

**Nach diesen drei Ergänzungen ist der Testlauf frei.**
