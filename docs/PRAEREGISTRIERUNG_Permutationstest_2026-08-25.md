# Vorab-Registrierung — Exakter Rotationstest: Regimewechsel ↔ dokumentierte Ereignisse

**Projekt RS-HW · verfasst 25.08.2026, vor dem ersten Testlauf · verbindlich für Forschungsfrage (a) · Grundlage `Code/METHODIK.md` §2/§7**
Datenstand am 25.08.2026 gegen die Dateien nachgezählt: **377 Handelstage** (03.01.2025–26.06.2026, `hmm_input_changes.csv`) · **26 Ereignisse, davon 21 auf Handelstagen** (`key_events.csv`).

**1 Hypothesen und Niveau.** **H₀:** Die zeitliche Lage der Ereignisse ist unabhängig von der Lage der Regimewechsel; der Ereignisvektor ist austauschbar mit jeder seiner 377 zyklischen Verschiebungen. **H₁:** Ereignisse liegen häufiger innerhalb von ±k Handelstagen um einen Regimewechsel als unter H₀ erwartet. **Einseitig** nach oben („näher als Zufall"), **α = 0,05**, gültig **ausschließlich für die Primärspezifikation** (Viterbi, k = 2, alle 26 Ereignisse). Erreichbare p-Werte sind Vielfache von 1/377; der kleinste ist **0,00265**, und α = 0,05 verlangt, dass höchstens **18** der 377 Verschiebungen T(τ) ≥ T_obs erfüllen (18/377 = 0,0477; 19/377 = 0,0504).

**2 Die sechs Definitionen, vor dem Lauf fixiert.**

| # | Festlegung | Grund |
|---|---|---|
| **B1** | Regimepfad **smoothed** (Informationsstand = volle Reihe x₁…x_T), *nicht* filtered. | Frage (a) ist deskriptiv. |
| **B2** | Wechsel = **Übergang der Viterbi-Zustandsfolge**, Krisenzustand über die größere Kovarianz-Spur (0,133 / 0,568 → Index 1) → **13 Wechsel**, 14 Segmente, 7 Krisenepisoden, 139 Krisentage. | Ein Wechsel ist Eigenschaft der Zustands*folge*; der geschwellte Randposterior ist kein Folgen-Schätzer (Bishop 13.2.5). Viterbi nutzt dieselbe Voll-Sample-Information — kein Look-ahead. |
| **B3** | Teststatistik = **Zählvariante**: T = Zahl der Ereignisse innerhalb ±k Handelstagen eines Wechsels. Abstandsvariante ausgeschlossen, wird nicht nachgereicht. | Direkt interpretierbar, koppelt an das fixierte k. |
| **B4** | **k = 2** primär, Sensitivität k ∈ {1,2,3}. | US-Abend-Releases erreichen die Euro-Kurve erst am Folgetag. |
| **B5** | Nicht-Handelstage → **nächster** Handelstag: 28.02.→02.03., 31.05.→01.06., 07.06.→08.06., 14.06.→15.06., 20.06.→22.06. | Rückwärts wäre Look-ahead; Ausschluss kostete 5 Ereignisse. |
| **B6** | Cluster **nicht konsolidiert**; zusammengelegt wird nur derselbe Akt in derselben Richtung. Juni-Kette bleibt vierzeilig. | Abkommen und Blockade sind zwei Ereignisse. |

**3 Zählweise (D1).** Gezählt werden **Ereignisse (26), nicht Ereignistage (25)**: durch B5 fallen 20.06. und 22.06. auf denselben Handelstag, zählen aber einzeln, weil Frage (a) Ereignisse betrifft und B6 sie als eigenständige Akte führt. Technisch **Integer-Zählvektor** (`np.add.at`), nicht boolesch — ein Ja/Nein-Vektor verschluckt die Kollision. **Kontrollsumme: 26.**

**4 Nullverteilung und p-Wert (D2–D4).** **Exakte Aufzählung aller 377 zyklischen Verschiebungen** (`np.roll`, wrap-around), **kein** Ziehen — die Rotationsgruppe ist endlich und klein, die Aufzählung damit billiger *und* exakt. Der Regimepfad bleibt fest, nur die Ereignisse rotieren; die inneren Ereignisabstände bleiben unter H₀ erhalten. **p = #{τ ∈ {0,…,376} : T(τ) ≥ T_obs} / 377, τ = 0 eingeschlossen.** Die Verschiebung um τ bewegt die Ereignisse um **τ Handelstage (Indexpositionen), nicht um Kalendertage**.

Die Nähe-Maske wird einmal vor der Schleife aus den 13 Wechseln berechnet, und zwar **nicht-zirkulär**: Sie beschreibt den festen Regimepfad, dessen Ränder echte Sample-Grenzen sind. Da der randnächste Wechsel 9 Positionen vom Anfang und 8 vom Ende entfernt liegt, stimmt sie für k ≤ 3 mit der zirkulären Variante **exakt** überein (38 / 62 / 83 Tage in beiden Fällen). Der Wrap-around betrifft also nur die Ereignisse, nicht die Maske.

Erwartete Treffer unter H₀ — allein aus Regimepfad und Ereignis*zahl*, ohne deren Lage (nachgerechnet 25.08.2026):

| Spezifikation (Nähe-Abdeckung k = 1/2/3) | k=1 | k=2 | k=3 |
|---|---|---|---|
| **Viterbi, primär** (38 / 62 / 83 Tage = 10,1 / 16,4 / 22,0 %) | 2,62 | **4,28** | 5,72 |
| 0,5-Kreuzung, sekundär (12,7 / 19,4 / 25,2 %) | 3,31 | 5,03 | 6,55 |

**5 Angemeldete Zweitspezifikationen.** Drei Achsen: (i) **0,5-Kreuzung** als alternative Wechsel-Definition (17 Wechsel, 9 Episoden, 133 Krisentage; Widerspruch zu Viterbi an 8 von 377 Tagen = 2,1 %); (ii) **alle Ereigniszeilen vs. eine je Episode**; (iii) **k ∈ {1,2,3}**.

*Episodendefinition, vorab fixiert (Herleitung: METHODIK §7):* Ein **Strang** ist die Menge aller Zeilen mit `event`-Präfix `hormus_`; jede übrige Zeile ist eine eigene Strang-Einheit. Innerhalb eines Strangs bilden aufeinanderfolgende Zeilen mit **höchstens 14 Kalendertagen** Abstand eine Episode, vertreten durch ihre **erste** Zeile. Konkret verschmelzen nur 31.05.–22.06. zu einer Episode (Vertreter 31.05., B5 → 01.06.); 28.02. und 15.04. bleiben eigenständig. **Ereigniszahl der Zweitspezifikation: 22** auf 22 eindeutigen Handelstagen.

Berichtsraster 2 × 2 × 3 = **12 Zellen**, von denen genau eine — Viterbi, alle Zeilen, k = 2 — der Test ist; die übrigen elf sind Robustheitsprüfungen: vollständig berichtet, nicht gegen α getestet. *Kippt die Schlussfolgerung zwischen Primär- und Zweitspezifikation, wird das berichtet — es ist ein Ergebnis, keine Auswahlgelegenheit.*

**6 Limitationen.** **E1 Wrap-around:** Rotationstests setzen näherungsweise Stationarität voraus; beim Umlauf wird Juni 2026 an Januar 2025 geklebt — eine bedeutungslose Naht, offengelegt, keine Entwertung. **E2 Power:** 16 der 26 Ereignisse liegen im ab April 2026 nahezu durchgehenden Krisenblock ohne Wechsel; die Trennschärfe stammt praktisch vollständig aus den 10 davor (9 in 2025). Ein nicht-signifikantes Ergebnis ist deshalb **kein** Beleg für Abwesenheit eines Zusammenhangs. **E3 Milde Zirkularität:** Rekord-Yield-Tage (v. a. 05.03.2025, +30 bp) sind Ereignisse und zugleich Extrembewegungen der getesteten Reihe. **E4 Ermessensakt:** Die vier Auswahlkriterien standen vorab fest, ihre Zuordnung zu den Briefings war nicht vollautomatisch. **E5 Abbruchkriterium** (wörtlich, METHODIK §2): „Findet das HMM faktisch nur den April-2026-Bruch oder [übersteigt die Übereinstimmung Regimewechsel↔Ereignis das Permutations-Zufallsniveau nicht], wird das als **diagnostiziertes Negativ-Ergebnis** berichtet ('gaußsche, yield-only Zustände tracken statistische Struktur statt ökonomischer Regime'), inklusive Diagnose und Abhilfen (t-verteilte Emissionen, Jump Models) — **nicht** das Modell zum Funktionieren zwingen."

**7 Reproduzierbarkeit.** `hmmlearn.GaussianHMM`, `n_components=2`, `covariance_type="full"`, `random_state=42`, 27 Iterationen; Seed, Datenstand und Skriptname im Skriptkopf, Ergebnisraster als CSV in `Abgaben/`. **Selbsttest vor dem Lauf:** 10 Tage, Ereignisse {2,3,4}, ein Wechsel an Tag 8, k = 2 → T_obs = 0; τ = 5 → 3; τ = 3 → 2.

---
*Geschrieben, bevor T_obs oder ein p-Wert berechnet oder eingesehen wurde.*
