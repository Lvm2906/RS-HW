# Ergebnis — Exakter Rotationstest: Regimewechsel ↔ dokumentierte Ereignisse

**Gerechnet 26.08.2026 · Skript `Code/permutationstest.py` · Rohtabelle `Abgaben/permutationstest_ergebnisse.csv`**
Design vollständig vorab registriert in `PRAEREGISTRIERUNG_Permutationstest_2026-08-25.md` / `Code/METHODIK.md` §2, §7. Der Selbsttest (D6) lief vor dem Hauptlauf und lieferte exakt die registrierten Werte (T_obs = 0, τ = 5 → 3, τ = 3 → 2). Die Primärzelle wurde zusätzlich mit einer unabhängigen Zweitimplementierung nachgerechnet (Abstandsrechnung statt Maske, ohne `np.roll`) — identisch.

## 1 Das Ergebnis in einem Satz

**Die Primärspezifikation ist nicht signifikant: T_obs = 9, erwartet unter H₀ 4,276, exakter p-Wert 0,1088 > α = 0,05.** Damit greift das vorab registrierte **Abbruchkriterium** (METHODIK §2): Das Ergebnis wird als **diagnostiziertes Negativergebnis** berichtet. Es wird nicht nachgebessert, keine Spezifikation nachgereicht, keine Zelle nachträglich zur Hauptzelle erklärt.

## 2 Alle zwölf Rasterzellen

Getestet wird ausschließlich die fett gesetzte Zelle. Die übrigen elf sind angemeldete Robustheitsprüfungen: berichtet, nicht gegen α geprüft.

| Regimepfad | Ereignisse | k | T_obs | E[T\|H₀] | T_obs/E | p (exakt) |
|---|---|---|---|---|---|---|
| Viterbi | alle Zeilen (26) | 1 | 6 | 2,621 | 2,29 | 0,0902 |
| **Viterbi** | **alle Zeilen (26)** | **2** | **9** | **4,276** | **2,10** | **0,1088** |
| Viterbi | alle Zeilen (26) | 3 | 13 | 5,724 | 2,27 | 0,0610 |
| Viterbi | eine je Episode (22) | 1 | 5 | 2,218 | 2,25 | 0,0981 |
| Viterbi | eine je Episode (22) | 2 | 8 | 3,618 | 2,21 | 0,0716 |
| Viterbi | eine je Episode (22) | 3 | 12 | 4,844 | 2,48 | 0,0186 |
| 0,5-Kreuzung | alle Zeilen (26) | 1 | 6 | 3,310 | 1,81 | 0,1857 |
| 0,5-Kreuzung | alle Zeilen (26) | 2 | 9 | 5,034 | 1,79 | 0,1592 |
| 0,5-Kreuzung | alle Zeilen (26) | 3 | 13 | 6,552 | 1,98 | 0,0796 |
| 0,5-Kreuzung | eine je Episode (22) | 1 | 5 | 2,801 | 1,79 | 0,1671 |
| 0,5-Kreuzung | eine je Episode (22) | 2 | 8 | 4,260 | 1,88 | 0,0955 |
| 0,5-Kreuzung | eine je Episode (22) | 3 | 12 | 5,544 | 2,16 | 0,0292 |

**Interne Kontrolle:** Der Mittelwert der exakten Nullverteilung stimmt in jeder Zelle auf drei Nachkommastellen mit n × Nähe-Abdeckung überein (Primärzelle: 4,2759 vs. 4,2759). Das ist eine unabhängige Bestätigung, dass Maske, Zählvektor und Rotation korrekt zusammenspielen.

## 3 Was die Zahlen sagen — und was nicht

**Die Richtung stimmt, die Trennschärfe nicht.** In allen zwölf Zellen liegt T_obs über der H₀-Erwartung, mit Verhältnissen zwischen 1,79 und 2,48. Beobachtet werden also durchgehend rund doppelt so viele ereignisnahe Regimewechsel wie bei zufälliger Ereignislage. Trotzdem ist das Ergebnis nicht signifikant, und der Grund ist die **Form der Nullverteilung**, nicht die Größe des Effekts.

**Warum p trotz Faktor 2 bei 0,109 liegt.** Die exakte Nullverteilung der Primärzelle reicht von 0 bis 12 bei einem Mittel von 4,28; 41 der 377 Verschiebungen erreichen T ≥ 9. Der Grund ist die doppelte Clusterung: Die Ereignisse häufen sich im Juni 2026 (Hormus-Kette), und die Regimewechsel häufen sich ebenfalls am Sample-Ende (Positionen 295, 358, 366, 368). Jede Rotation, die das Ereignis-Cluster auf das Wechsel-Cluster schiebt, erzeugt einen hohen Wert. Genau das soll der zirkuläre Shift-Test abbilden — er vergleicht eine geclusterte Beobachtung mit einer geclusterten Nullverteilung. **Ein gewöhnlicher Permutationstest hätte die Ereignisse unabhängig gestreut, eine viel engere Nullverteilung erzeugt und mit hoher Wahrscheinlichkeit ein signifikantes Ergebnis geliefert — ein Artefakt.** Die 2026-08-05 getroffene Designentscheidung für den Rotationstest ist damit im Ergebnis sichtbar geworden.

**Welche neun Ereignisse treffen** (Primärzelle, ±2 Handelstage um einen Viterbi-Wechsel): Schuldenbremse-Reform 05.03.2025 · Tarif-Schock 02.04.2025 · EZB-Senkung 05.06.2025 · Hormus-Beginn (02.03.2026 nach B5) · Hormus-Deeskalation (01.06.2026 nach B5) · US-CPI 10.06.2026 · EZB-Erhöhung 11.06.2026 · Hormus-Abkommen (15.06.2026 nach B5) · Fed-Hold 17.06.2026. Bemerkenswert, aber **nicht** als Beleg verwertbar: Darunter sind die drei größten Einzelschocks des Samples.

**Der Wert der Vorab-Registrierung, in einer Zeile belegt.** Zwei Robustheitszellen liegen unter 0,05 — Viterbi / eine je Episode / k = 3 mit p = 0,0186 und 0,5-Kreuzung / eine je Episode / k = 3 mit p = 0,0292. Ohne die am 25./26.08. **vor** dem Lauf fixierte Regel „α gilt nur für Viterbi, alle Zeilen, k = 2" wäre hier eine signifikante Hauptaussage wählbar gewesen. Dass sie nicht gewählt wird, ist der Punkt. Beide Werte werden berichtet, nicht verschwiegen — aber als das, was sie sind: eine von zwölf Zellen ohne Vorrang, in einem Raster, in dem bei zwölf Vergleichen einzelne p-Werte unter 0,05 auch unter H₀ zu erwarten sind.

## 4 Einordnung nach dem Abbruchkriterium

Die drei Erfolgsbedingungen aus METHODIK §2: (1) BIC bevorzugt zwei Regime — **erfüllt** (ΔBIC 208,10). (2) Die smoothed Posteriors sind an den meisten Tagen entschieden — **erfüllt** (81,2 % der Tage über 0,9 oder unter 0,1). (3) Die Übereinstimmung Regimewechsel ↔ Ereignis übersteigt das Permutations-Zufallsniveau — **nicht erfüllt** (p = 0,1088).

**Berichtsform, wörtlich aus METHODIK §2:** diagnostiziertes Negativergebnis — „gaußsche, yield-only Zustände tracken statistische Struktur statt ökonomischer Regime", inklusive Diagnose und Abhilfen (t-verteilte Emissionen, Jump Models), **nicht** das Modell zum Funktionieren zwingen.

**Was das Ergebnis ausdrücklich nicht ist (E2):** kein Beleg für die Abwesenheit eines Zusammenhangs. 16 der 26 Ereignisse liegen im ab April 2026 nahezu durchgehenden Krisenblock, in dem es kaum Wechsel gibt; die Trennschärfe stammt praktisch vollständig aus den 10 Ereignissen davor. Bei dieser Ereigniszahl und 13 Wechseln ist der Test schlicht zu schwach, um einen Effekt der beobachteten Größe von Zufall zu trennen. Die korrekte Sprache fürs Paper ist deshalb nicht „kein Zusammenhang", sondern: *the point estimate is consistent with the hypothesised direction (roughly twice the chance level in every specification), but the exact rotation test cannot distinguish it from clustering-driven chance at this sample size.*

## 5 Folgen fürs Paper

- Forschungsfrage (a) wird als **Negativergebnis mit Diagnose** berichtet, nicht als Fehlschlag versteckt und nicht in ein Positivergebnis umgedeutet.
- Die vollständige Zwölf-Zellen-Tabelle gehört in den Ergebnisteil, nicht in den Anhang — sie ist zusammen mit der Vorab-Registrierung das methodische Alleinstellungsmerkmal.
- Der Abschnitt „warum Rotationstest statt Permutationstest" bekommt durch die breite Nullverteilung (0–12, Mittel 4,28) sein empirisches Argument.
- Forschungsfrage (b) — Stufe 2 — ist davon **unberührt**: Sie prüft, ob sich (a, σ) zwischen den Regimen unterscheiden, und setzt nicht voraus, dass die Regime mit Ereignissen zusammenfallen.

---
**Korrektur 30.09.2026 (Cowork, beim Schreiben des Papers gegen die Dateien geprüft):** §4 E2 („16 der 26 Ereignisse liegen im ab April 2026 nahezu durchgehenden Krisenblock, in dem es kaum Wechsel gibt; die Trennschärfe stammt praktisch vollständig aus den 10 Ereignissen davor") trifft für den **Viterbi-Pfad** nicht zu: Von den 16 Ereignissen ab April 2026 liegen 8 im Krisenregime; der Juni 2026 ist zu 85 % ruhig und enthält 9 Ereignisse und 3 der 13 Wechsel; von den 9 Treffern stammen 5 aus den späten und 4 aus den frühen Ereignissen. Die Schwäche des Tests kommt aus der gemeinsamen Clusterung von Ereignissen und Wechseln (breite Nullverteilung), nicht aus fehlenden Wechseln. Die Aussage stammt aus HANDOVER §2.7 (05.08., vor Festlegung des Viterbi-Pfads). Ergebnis und p-Wert unberührt. Das Paper verwendet die korrigierte Fassung.
