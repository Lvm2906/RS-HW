# Numerische Robustheit des Stage-1-Fits — Schritt 4

**Gerechnet 20.09.2026 · Skript `Code/robustheit_startwerte.py` · Rohtabelle `Abgaben/robustheit_startwerte.csv`**
Schließt den seit KW29 offenen Punkt **HANDOVER §2.4**: Die Reproduzierbarkeitsaussage ruhte bisher allein auf dem festen Seed 42.

## Was geprüft wurde

24 Startwerte (0–19, 42, 123, 999, 2026). Variiert wurde **ausschließlich** `random_state` — es setzt über die k-means-Initialisierung den EM-Startpunkt. Modell, Daten und Spezifikation sind unverändert (377×3, K = 2, `covariance_type="full"`, `n_iter=100`). Das ist kein Designeingriff und berührt keine vorab registrierte Entscheidung.

Verglichen wurde gegen den im Paper verwendeten Fit mit Seed 42, und zwar nicht nur auf Kennzahlen, sondern **tagesweise auf dem Viterbi-Pfad** — denn auf dem Pfad ruht alles Weitere: Regimewechsel, Rotationstest, Stufe-2-Trennung.

## Ergebnis

| Kriterium | Befund über alle 24 Startwerte |
|---|---|
| Konvergenz | **24 von 24**, keiner am Iterationslimit (max. 73 von 100) |
| Iterationen | 15 bis 73 |
| log L | 235,5974 bis 235,6013 — **Spannweite 0,0039** |
| Spur ruhig | 0,1327–0,1328 — Spannweite 0,0001 |
| Spur Krise | 0,5673–0,5683 — Spannweite 0,0010 |
| Krisentage (Viterbi) | **139 in jedem einzelnen Lauf** |
| Regimewechsel | **13 in jedem einzelnen Lauf** |
| Abweichung zum Seed-42-Pfad | **0 Tage — in allen 24 Läufen identisch** |

**Der Regimepfad ist über alle geprüften Startwerte exakt derselbe.** Damit sind auch alle davon abhängigen Größen unverändert: Nähe-Masken 38/62/83, T_obs = 9, p = 0,1088. Der Rotationstest musste dafür nicht neu gerechnet werden — er hängt ausschließlich am Pfad, und der ist bitgleich.

Die log-L-Streuung von 0,0039 ist Konvergenztoleranz, kein zweites Optimum: Alle Läufe landen in derselben Mulde und unterscheiden sich nur darin, wie weit sie hineingelaufen sind, bevor das Abbruchkriterium griff.

## Der interessanteste Nebenbefund: Label-Switching ist real

**Der Krisenzustand liegt in 13 von 24 Läufen auf Index 1, in 11 von 24 auf Index 0.** Welcher der beiden Zustände die Nummer 1 bekommt, ist reine Initialisierungssache und ohne inhaltliche Bedeutung — hmmlearn garantiert keine Reihenfolge.

Damit ist die durchgehend angewandte Regel, den Krisenzustand über die **größere Kovarianz-Spur** zu identifizieren statt über die Zustandsnummer, nicht länger nur gute Praxis, sondern an diesem Datensatz als notwendig belegt: Ein Skript, das `state == 1` hart verdrahtet hätte, wäre in **11 von 24 Läufen** auf das ruhige Regime gelaufen und hätte Krisen- und Ruhephasen vertauscht — ohne Fehlermeldung. Diese Zahl gehört ins Paper, sie ist der konkrete Beleg für eine Entscheidung, die sonst wie Formalismus aussieht.

## Grenze der Aussage

24 Startwerte sind kein Beweis, dass die Likelihood kein zweites lokales Optimum besitzt — sie zeigen, dass keiner der geprüften Startpunkte in ein anderes fällt. Die korrekte Formulierung fürs Paper ist entsprechend: *across 24 initialisations the fit converges to the same solution and yields an identical decoded path*, nicht „das globale Optimum wurde gefunden".

## Fürs Paper

- Die Tabelle oben als kleines Robustheits-Exhibit oder als Absatz im Methodenteil.
- Satz zur Reproduzierbarkeit kann jetzt lauten: nicht „mit Seed 42 reproduzierbar", sondern **„unabhängig vom Startwert"** — das ist die stärkere und ab jetzt belegte Aussage.
- Label-Switching-Befund (11/24) in die Methoden-Fußnote zur Regime-Identifikation.
