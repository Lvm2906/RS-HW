# METHODIK & PROJEKT-BRIEFING — Regime-Switching Hull-White / HMM

**Stand: 2026-06-01. Diese Fassung ersetzt die vorige (2026-05-31) und ist die
verbindliche Referenz.** Ein zentraler Richtungswechsel ist eingearbeitet: Das
Projekt ist jetzt eine **Regime-Switching-HMM-Arbeit**, nicht mehr die frühere
Hull-White-Case-Study (siehe §5 und Anhang A).

---

## 0. Für Cowork: Was dieses Dokument ist

Dies ist die zentrale Orientierung für die Umsetzung. Es beschreibt **was gebaut
werden soll** (Architektur, §2), **wie gearbeitet wird** (§4), **was sich gerade
geändert hat und noch umzubauen ist** (§5, §8), und es bewahrt die **verifizierte
Pipeline-Doku** (§6–§7). Bei Konflikt zwischen diesem Dokument und älteren Notizen
gilt dieses Dokument; bei Konflikt zwischen diesem Dokument und dem finalen Exposé
(`Expose_RS-HW.docx`) gilt das Exposé, denn dort sind die Forschungsfrage und die
methodischen Entscheidungen festgeschrieben.

---

## 1. Ziel der Arbeit

Ein 12–15-seitiges Working Paper plus öffentliches GitHub-Repository. *[Persönliche Angabe in der Repository-Kopie entfernt.]*

> **Klarstellung 2026-08-25:** Das Projekt ist **keine Bachelorarbeit**, sondern ein
> eigenständiges Forschungsprojekt (so auch das Exposé: „research proposal", „conducted
> independently"). Es gelten keine Prüfungsordnungs-Formalia, sondern die selbst gesetzte
> Grenze: **maximal 20 Seiten Fließtext**; Formeln, Tabellen, Abbildungen und
> Literaturverzeichnis zählen nicht mit. Zielumfang bleibt 12–15 Seiten.
> **Sprache: Englisch.** Abgabe: **30.09.2026**. Eine einseitige Fassung
(das Exposé) dient als Betreuungsanfrage an Lehrstühle für Computational/
Mathematical Finance.

Inhaltlich: ein **Regime-Switching-Ansatz für die Short-Rate-Dynamik** auf einem
selbst aufgebauten EZB-AAA-Yield-Curve-Datensatz. Ein Hidden-Markov-Modell erkennt
unüberwacht Marktregime aus der Yield-Dynamik; ein Hull-White-Short-Rate-Modell
wird regime-bedingt geschätzt; die Regime werden gegen real-time dokumentierte
Ereignisse validiert.

Das Alleinstellungsmerkmal ist **nicht** das Modell (Regime-Switching-Zinsmodelle
existieren), sondern der **selbst gebaute Euroraum-Datensatz** plus die
**Validierung gegen zeitgleich, nicht ex post erfasste Ereignisse**.

---

## 2. Festgelegte Forschungsfrage & Architektur (verbindlich)

### Zwei falsifizierbare Forschungsfragen

- **(a) Detektion:** Fallen blind aus der Yield-Dynamik per HMM erkannte Regime
  mit extern dokumentierten geld- und geopolitischen Ereignissen über das
  Zufallsniveau hinaus zusammen?
- **(b) Schätzung:** Unterscheiden sich die geschätzten Short-Rate-Parameter
  (Mean Reversion *a*, Volatilität *σ*) über Regime hinaus über die
  Schätzunsicherheit, und ist die regime-bedingte Spezifikation der
  Ein-Regime-Spezifikation vorzuziehen?

### Architektur A — zweistufig, entkoppelt

**Stage 1 — Regimeerkennung (HMM).**
- Gauß-Emissions-HMM, geschätzt per Baum-Welch.
- Emissionen auf den **Tagesänderungen** von Level / Slope / Curvature der Kurve
  (NICHT auf den Niveaus — Niveaus sind nahe Einheitswurzel und würden Zins-Epochen
  statt Krise/Ruhe trennen). Auf Änderungen keyt das HMM auf die Varianz, also
  Hochvol- vs. Niedrigvol-Regime.
- Output: **smoothed** Regimepfad (für die deskriptive Frage a) UND **filtered**
  Regimepfad (für jeden Prognose-/Bewertungsanspruch — nur Information bis t, kein
  Look-ahead). Diese Trennung ist verbindlich.
- **Präzisierung 2026-08-10 (B1/B2):** „smoothed" legt den **Informationsstand** fest
  (die ganze Reihe x₁…x_T darf einfließen), **nicht den Dekodierer**. Für die Definition
  der *Regimewechsel* im Permutationstest wird der Pfad per **Viterbi** dekodiert — auch
  Viterbi konditioniert auf x₁…x_T, ist also ebenfalls ein Voll-Sample-Objekt und
  erzeugt kein zusätzliches Look-ahead. Begründung, Zahlen und die mitlaufende
  Zweitspezifikation: §7, Abschnitt „Regimewechsel-Definition (B2)".

**Stage 2 — Regime-bedingte Schätzung (Hull-White).**
- One-Factor Hull-White. (*a*, *σ*) werden **unter dem physischen Maß** aus der
  Zeitreihe des **3M-Satzes als Short-Rate-Proxy** geschätzt, durch Diskretisierung
  der HW-Dynamik. Das ist **Estimation**, keine Q-Maß-Kalibrierung an Derivatepreise
  (wir haben keine Caps/Swaptions). Das Wort „calibration" ist ausschließlich für
  das Anpassen der deterministischen Drift *θ(t)* an die Anfangskurve reserviert.
- **Bootstrap-Konfidenzintervalle** auf (*a*, *σ*), damit ein echter Regime-Unterschied
  von Schätzrauschen getrennt werden kann. „Material" in RQ(b) = CIs überlappen nicht
  / Verhältnis-CI schließt 1 aus.

### Stage-2-Schätzdesign (entschieden 2026-08-25, vor jeder Schätzung)

Vier Festlegungen, die das Prinzip oben operationalisieren. Sie stehen **vor** dem ersten
Schätzlauf fest, aus demselben Grund wie beim Shift-Test.

1. **Trennung der Zeitreihe nach Regime: harter Viterbi-Pfad.** Jeder Handelstag gehört zu
   genau einem Regime, entschieden über die Viterbi-Zustandsfolge — dieselbe Definition wie
   für die Regimewechsel in §7. Keine Gewichtung mit Posterior-Wahrscheinlichkeiten; das
   hielte zwei verschiedene Regimebegriffe nebeneinander.
2. **Nahtstellen werden verworfen.** Die Regime sind fragmentiert (Viterbi: 14 Segmente, je
   7 pro Regime). Klebte man die Tage eines Regimes aneinander, entstünde an jeder Naht eine
   „Tagesdifferenz" zwischen Tagen, die real Wochen auseinanderliegen — künstliche,
   systematisch große Sprünge, die σ nach oben verzerren. Die Übergangspaare an den
   Segmentgrenzen werden daher **ausgeschlossen**. Kosten: **13 von 376 Paaren (3,46 %)** — 14 Segmente haben 13 Nahtstellen, nicht 14. Gegenprobe: 376 − 132 − 231 = 13.
   Es verbleiben **132 Paare im Krisenregime** und **231 im ruhigen** — für ein AR(1) mit
   zwei Parametern reichlich.
3. **Schätzweg: bedingte Maximum Likelihood.** Die exakte Diskretisierung der OU-Dynamik liefert
   ein AR(1); (a, σ) folgen aus dem AR(1)-Koeffizienten und der Residuenvarianz.

   **Präzisiert 2026-09-26 (Klaus, mit der Stufe-2-Abgabe):** Verwendet wird die **bedingte**
   ML-Schätzung, bedingt auf den ersten Wert jedes Paares. Für das gaußsche AR(1) liefert sie b
   und c wie OLS; der Unterschied liegt allein im Nenner der Varianzschätzung (ML: δ² = SSR/n,
   nicht n−2). **Die exakte ML wird bewusst nicht verwendet**, und zwar nicht nur aus Aufwands-,
   sondern aus Spezifikationsgründen: Sie setzte voraus, dass der erste Tag jeder Episode aus der
   stationären Verteilung N(θ, σ²/2a) *desselben* Regimes stammt. Eine Episode beginnt aber
   unmittelbar nach einem Regimewechsel — ihr Startwert wurde vom *anderen* Regime erzeugt. Die
   sieben Randterme je Regime wären daher fehlspezifiziert. Das präzisiert die registrierte
   Entscheidung „Maximum Likelihood" und wählt sie nicht neu.

   **Belegkorrektur 2026-09-26:** Die frühere Angabe „MLE statt OLS (beide Wege in Brigo et al.
   2008, Abschn. 7)" war **falsch** — am Volltext geprüft gibt Abschnitt 7 ausschließlich den
   OLS-Weg (Gl. 58–60) und verweist für Maximum Likelihood lediglich auf eine andere Arbeit.
   Richtig ist: **Diskretisierung, AR(1)-Form und Rückrechnung** nach Brigo, Dalessandro,
   Neugebauer & Triki (2008), Abschn. 7, Gl. 47–57; die **geschlossenen ML-Formeln** nach
   van den Berg (2011). Beide frei zugänglich, Fundstellen in `BELEGPLAN.md` B-4 und B-5.

   **Korrekturvermerk 2026-09-30 (Cowork, Prüfbericht K4; Entscheidung unverändert):** Die
   Belegkorrektur vom 26.09. ist selbst teilweise falsch. Brigo et al. (2008) schreiben auf S. 29
   ausdrücklich „The OLS regression provides the maximum likelihood estimator for the parameters c,
   b and δ“, und Gl. 60 (S. 31) ist δ̂² = (1/n)Σ[…]², also SSR/n — die bedingte ML. Für ML *in
   geschlossener Form mit Herleitung* bleibt van den Berg (2011) der bessere Beleg; Brigo trägt die
   Aussage „bedingte ML = OLS für b, c; δ² = SSR/n“ aber ebenfalls. Zudem stehen c und b bei Brigo
   in Gl. 50/51 (nicht 52). Das Paper zitiert seit der K4-Umsetzung „eqs. 49–52“.
   *Nebenbefund zur Begründung gegen die exakte ML:* Die erste Krisenepisode beginnt am
   Stichprobenanfang, nicht nach einem Regimewechsel; das Argument gilt für 13 von 14 Episoden
   (im Paper so präzisiert).

   **Zeitschritt:** h = 1/252 (ein Handelstag als Jahresbruchteil), damit sind a in „pro Jahr"
   und σ in Prozentpunkten pro √Jahr angegeben. Wochenenden und Feiertage zählen nicht als Zeit.
4. **Bootstrap: Residuen-Bootstrap, episodenweise regeneriert.**
   - **Kein Block-Bootstrap** — er verlangte eine Blocklänge als frei gewählten Parameter,
     und die Episoden sind dafür zu kurz (Krisenregime: 63, 44, 9, 8, 7, 6, 2 Tage).
   - Verfahren: Residuen des geschätzten AR(1) mit Zurücklegen ziehen, je Episode eine neue
     Reihe vom ersten beobachteten Wert der Episode aus rekursiv erzeugen, neu schätzen.
   - **B = 2000** Replikationen, **BCa-Intervalle auf 95 %** (BCa statt Perzentil, weil σ
     nach unten beschränkt und rechtsschief ist), **fester Seed**.
   - **Gepaarte Replikationen:** In jeder Replikation werden *beide* Regime neu gezogen und
     in derselben Replikation die Verhältnisse a_Krise/a_ruhig und σ_Krise/σ_ruhig gebildet.
   - **Primäres Materialitätskriterium ist das Verhältnis-CI** (schließt es die 1 aus?). Die
     Überlappung der beiden Einzel-CIs wird nur deskriptiv berichtet — sie ist ein anderer,
     konservativerer und statistisch unsauberer Test. Damit ist die Doppelformulierung in
     §2 („CIs überlappen nicht / Verhältnis-CI schließt 1 aus") zugunsten des zweiten Teils
     aufgelöst.
   - **Residuendiagnostik wird berichtet** (Ljung-Box auf Restautokorrelation,
     Heteroskedastizität). Zeigt sich Heteroskedastizität, wird auf den **Wild Bootstrap**
     umgestellt (Residuen mit zufälligem ±1 multipliziert) — hiermit vorab angemeldet.
   - **Festlegungen 28.09.2026 (Klaus, vor dem ersten Bootstrap-Lauf).** Schließen Lücken dieses
     Punkts, wählen nichts neu. Belege mit Lesestatus: `BELEGPLAN.md` B-9 bis B-13.
     - **(A) Gerechnet wird wie registriert.** Befund vom 26.09.: n(b̂−1) = −2,1 (Krise) / −2,7 (ruhig)
       liegt im local-to-unity-Bereich, in dem der Standard-Bootstrap ungültig ist bzw. schlecht
       abdeckt (Basawa et al. 1991; Hansen 1999); BCa ist dafür in keiner Quelle abgesichert, und â ist
       stark nach oben verzerrt (Tang & Chen 2009: führend ≈ 4/T). Das wird als belegte Einschränkung
       berichtet. **Kein** Zusatzverfahren (Grid-Bootstrap, Andrews-Intervall) — das wäre eine
       nachgereichte Spezifikation.
     - **(1) Replikationen mit b* ≥ 1 bleiben drin.** a* = −ln(b*)/h für alle b* > 0, auch a* ≤ 0;
       σ* nach derselben Formel (stetig über b = 1 hinweg, Grenzwert δ/√h). Die Zahl der Replikationen
       mit b* ≥ 1 wird je Regime berichtet. Kein Ausschluss — Ausschließen wäre Bedingen, und das
       bedingte Konfidenzniveau kann beliebig klein werden (Franz 2007). **Deutungsregel:** Schließt
       das BCa-Einzelintervall von a_Krise oder a_ruhig die 0 ein, wird das a-Verhältnisintervall
       berichtet, gilt aber als **nicht interpretierbar** (Fieller-Fall: korrekte Konfidenzmenge
       unbeschränkt, ein Bootstrap-Intervall kann das nicht abbilden; Franz 2007, von Luxburg & Franz
       2009).
       *Befund 29.09.2026 (Cowork, Fehler im eigenen Vorschlag; Regel NICHT geändert):* Die
       Fieller-Begründung trägt nur für den **Nenner** (a_ruhig): Die Konfidenzmenge eines Verhältnisses
       wird unbeschränkt, wenn der Nenner nicht signifikant von 0 verschieden ist (Franz 2007). Enthält
       nur das Intervall des **Zählers** (a_Krise) die 0, bleibt die Fieller-Menge beschränkt; sie enthält
       dann lediglich die 0. Für den Zählerfall ist die registrierte Regel also **strenger, als die Quelle
       verlangt**, und ihre Begründung dort nicht Fieller. Genau dieser Fall ist eingetreten (a_Krise
       [−3,82; 11,68] enthält 0, a_ruhig [0,50; 5,47] nicht). Die Schlussfolgerung hängt daran nicht: Auch
       als interpretierbar gelesen, enthält das a-Verhältnis-Intervall [−1,05; 5,68] die 1. Im Paper
       offenlegen.
     - **(2) Beschleunigung per Jackknife über Paare:** je ein Paar weglassen, Statistik neu geschätzt;
       Formel DiCiccio & Efron (1996) Gl. 6.6/6.7 (Vorzeichenkonvention dort). *Präzisiert am selben
       Tag, vor dem Lauf:* Für Einzelparameter eines Regimes läuft der Jackknife nur über dessen Paare
       (132 bzw. 231) — Gl. 6.7 unverändert. Für die Verhältnisse werden Einflusswerte **je Regime**
       gebildet, U_ki = (n_k − 1)(θ̂₍·k₎ − θ̂₍ki₎), und mit 1/n_k gewichtet zusammengeführt:
       â = (1/6) · Σ_k Σ_i (U_ki/n_k)³ / [Σ_k Σ_i (U_ki/n_k)²]^{3/2}.
       *Korrektur 28.09.2026, vor dem Lauf:* Eine erste Fassung dieses Absatzes (12:24 UTC) setzte die
       U_ki ungewichtet in Gl. 6.6 ein; das ist für ungleiche n_k falsch skaliert. Die gewichtete Form
       reduziert sich für ein Regime exakt auf Gl. 6.6 (die n-Potenzen kürzen sich) und entspricht der
       Mehrstichproben-Formel in `scipy.stats.bootstrap` (Quellcode verweist auf Efron & Tibshirani 1993,
       Gl. 15.36 — das Buch selbst ist **nicht** am Volltext geprüft). Begründung: Σ_i U_ki²/n_k² ist der
       Jackknife-Varianzbeitrag von Regime k, die Nenner-Summe also die Gesamtvarianz des Verhältnisses.
       *Volltextprüfung 29.09.2026:* Primärbeleg für den K-Stichproben-Fall ist **Efron (1994)**, JASA 89,
       463–478, gelesen als Stanford Tech. Report 397 (1992), **Remark C** mit Gl. 2.16/2.17 und 3.21–3.23:
       Die Stichproben werden zu einem Vektor der Länge Σn_k verbunden und die Einstichproben-Formel auf
       S(P*) angewandt. Die Gewichte 1/n_k sind dort **nicht ausgedruckt**, sondern folgen daraus
       (Einfluss von Punkt ki in S = (N/n_k)·U_ki, N kürzt sich) — Herleitung Eigenleistung, gegengerechnet.
       Der Verweis bei DiCiccio & Efron (S. 202) auf „Remarks C and H“ bezieht sich auf die JASA-Fassung;
       Remark H ist in der TR-Fassung anders belegt und nicht geprüft. **Bekannte Unschärfe:** Die Quellen
       formulieren die Regel mit exakten Einflusswerten (Gl. 6.5 / 2.16); verwendet wird wie registriert die
       Jackknife-Näherung (Gl. 6.7). Gegengerechnet 29.09. mit numerisch differenzierten Einflusswerten:
       â weicht um höchstens 0,0015 ab, die BCa-Grenzen um höchstens 0,023 (a Krise oben) — jeweils kleiner
       als der MC-Standardfehler derselben Grenze. **Abweichung zu R `boot::boot.ci`:** dort ungewichtet
       und um θ̂ statt um den Jackknife-Mittelwert zentriert — bei ungleichen n_k ein anderer Wert.
       z0 nach DiCiccio & Efron Gl. 2.8 mit strikt „<"; Perzentile per linearer Interpolation
       (`np.quantile`, Standardmethode). Die Wahl der Einheit ist Eigenleistung (keine Quelle deckt den
       Residuen-Bootstrap eines AR); Begründung: Die bedingte Likelihood faktorisiert über die Paare
       (B-8), sie sind die unabhängigen Beiträge.
     - **(3) B = 2000 bleibt.** Für jeden BCa-Endpunkt wird das Perzentil berichtet, auf dem er landet;
       keine feste Schwelle, Einordnung nach Efron & Narasimhan (2020).
     - **(4) Berichtsform RQ(b), Intersection–Union-Prinzip:** Die gemeinsame Aussage „(a, σ)
       unterscheiden sich über Regime" wird nur getroffen, wenn **beide** Verhältnisintervalle die 1
       ausschließen, jeweils zu 95 % ohne Korrektur (Berger & Hsu 1996, Thm. 1). Einzelbefunde werden
       deskriptiv berichtet, nicht als eigene Hauptaussage.
     - **(5) Monte-Carlo-Fehler der Endpunkte:** Gruppen-Jackknife über die vorhandenen 2000
       Replikationen, J = 10 Gruppen (Efron & Narasimhan 2020, §3); keine weiteren Seeds.
       *Abweichung, vermerkt 28.09.2026 (nach dem Referenzlauf, vor Klaus' Lauf):* Efron & Narasimhan
       (Preprint S. 8) teilen die Replikationen **zufällig** in J Gruppen, ohne dafür einen Grund zu
       nennen. Hier werden **zusammenhängende Blöcke** in Erzeugungsreihenfolge verwendet (1–200,
       201–400, …). Begründung (Eigenleistung): Die Replikationen sind gegeben die Daten unabhängig und
       gleich verteilt und liegen unsortiert in Erzeugungsreihenfolge vor; jede von den Werten
       unabhängige Aufteilung liefert daher austauschbare Gruppen und ist in der Verteilung einer
       zufälligen gleich. Die feste Aufteilung erspart einen weiteren Zufallsschritt mit eigenem Seed.
       Die Blockteilung stand im Code vor dem ersten Lauf, dokumentiert wird sie erst hier; der
       MC-Standardfehler ist rein deskriptiv und geht in keine Entscheidungsregel ein.
     - **Konvention Quantil, vermerkt 28.09.2026:** DiCiccio & Efron (1996) definieren G als empirische
       Verteilungsfunktion (Gl. 2.2) und lassen offen, wie G⁻¹ bei nicht ganzzahligem B·p ausgewertet
       wird (Volltextsuche ohne Treffer). Festgelegt ist lineare Interpolation zwischen benachbarten
       Ordnungsstatistiken (`np.quantile`, Standard; so auch `scipy.stats.bootstrap`). Eigene
       Konvention, keine Quelle; Unterschied zur Ordnungsstatistik höchstens ein Nachbarwert.
     - **Nachrichtlich, kein Verfahrenswechsel:** Die Bootstrap-Verzerrung mean(θ*) − θ̂ wird
       berichtet, die Punktschätzung **nicht** korrigiert. Seed 42; Ziehungen als Indexmatrizen
       einmal erzeugt und gespeichert, damit beide Implementierungen dieselben Replikationen rechnen.

**Validierung.**
- Frage (a): **zirkulärer Shift-Test** (fixiert 2026-08-05, NICHT unabhängige
  Permutation): Der gesamte Ereignisvektor wird um einen zufälligen Offset τ **zyklisch
  über die 377 Handelstage verschoben** (wrap-around); das liefert die Nullverteilung der
  Nähe von Ereignis und Regimewechsel und **erhält die inneren Ereignis-Abstände unter
  H0**. Begründung: Die Ereignis-Clusterung (Iran-Krieg mit rascher Eskalations-/
  Deeskalationsfolge) ist eine Welt-Eigenschaft, kein Artefakt — unabhängiges Permutieren
  verglich eine geclusterte Beobachtung mit einer ungeclusterten Nullverteilung und
  verzerrte den Test. `scipy.stats.permutation_test` bietet den Shift nicht nativ (selbst
  implementieren). Hauptanker sind die `key_events` über das ganze Fenster (Stand
  2026-07-27: 26; davon 21 im Handelstags-Index — siehe §7). **Vorab registriert:** beide
  Auswertungen berichten — (i) alle Zeilen, (ii) eine Zeile je Episode; hält die Aussage
  nur in einer Variante, ist das ein Ergebnis, keine Panne.
- Die crisis-Tags (`context_events.csv`) sind ein **einseitiger Konsistenz-Check**
  — **58 Tags, 08.04.–29.06.2026, davon 47 im Handelstags-Index** (Stand 25.08.2026
  verifiziert; die frühere Angabe „≈29" stammte aus dem Exposé-Stand vom Juni)
  („erkennt das Modell die bekannte Krise als crisis?"), nicht der Haupttest.
- Vorab definiertes **Abbruchkriterium / Negativ-Ergebnis** (siehe unten).

### Modellselektion & Erfolgskriterium

- **Stage-1-BIC:** 1 vs. 2 Zustände. Hier wird der Komplexitäts-Penalty für die
  Regime-Struktur (Übergangsmatrix, Emissionen) erhoben.
- **Stage-2-BIC:** regime-bedingt vs. ein Regime — **bedingt auf den Regimepfad**
  (siehe §9, Pflicht-Klarstellung im Paper).
  **Festlegung 28.09.2026 (Klaus, vor der Rechnung):** Beide Modelle werden auf **denselben 363 Paaren**
  geschätzt (13 Nahtstellen verworfen wie in Stufe 2) — ein BIC-Vergleich setzt dieselben
  Beobachtungen voraus. Ein-Regime-Modell: ein AR(1) (b, c, δ) über alle 363 Paare; Zwei-Regime-Modell:
  je Regime eigenes (b, c, δ). Bedingte gaußsche Log-Likelihood am ML-Punkt, k = 3 bzw. 6, n = 363,
  BIC = −2 ln L + k ln n. Der Regimepfad selbst ist gegeben und wird **nicht** als Parameter gezählt —
  seine Strafe steckt im Stage-1-BIC (§9.1). Wegen nicht-normaler Krisenresiduen ist ln L als
  Quasi-Likelihood zu lesen.
- **Detektion gilt als erfolgreich nur,** wenn (1) das 2-Regime-Modell per BIC
  bevorzugt ist, (2) die smoothed Posteriors an den meisten Tagen entschieden sind,
  (3) die Übereinstimmung Regimewechsel↔Ereignis das Permutations-Zufallsniveau
  übersteigt.
### Signifikanzniveau (entschieden 2026-08-25, vor dem Testlauf)

**α = 0,05, einseitig** (die Alternative lautet „näher als Zufall", nicht „anders als Zufall").
Damit ist die bisherige Lücke geschlossen: §2 sprach nur davon, dass die Übereinstimmung „das
Permutations-Zufallsniveau übersteigt", ohne Schwelle — eine Vorab-Registrierung ohne α ist
unvollständig.

- Das Niveau ist nicht zahnlos: Der exakte Rotationstest zählt alle 377 zyklischen
  Verschiebungen auf, der kleinste erreichbare p-Wert ist damit **1/377 = 0,00265**. Erreichbare
  p-Werte sind Vielfache von 1/377; α = 0,05 verlangt, dass T_obs unter den obersten ~18
  Verschiebungen liegt.
- **α gilt ausschließlich für die Primärspezifikation** (Viterbi-Wechsel, k = 2, alle 26
  Ereignisse). Die angemeldeten Zweitspezifikationen — 0,5-Kreuzung als Wechsel-Definition,
  k ∈ {1,3}, „eine Zeile je Episode" — sind **Robustheitsprüfungen**: Ihre p-Werte werden
  vollständig berichtet, aber nicht gegen α getestet. Das Berichtsraster umfasst
  2 (Wechsel-Definition: Viterbi / 0,5-Kreuzung) × 2 (B6: alle Zeilen / eine je Episode)
  × 3 (k ∈ {1,2,3}) = **12 Zellen**, von denen genau eine der Test ist. Ohne diese Festlegung
  wäre bei zwölf Kombinationen unklar, welcher p-Wert „der Test" ist, und das multiple Testen
  bliebe unadressiert. *(Korrigiert 26.08.2026: die Erstfassung nannte „acht Kombinationen" —
  nachgezählt sind es 2 × 2 × 3 = 12.)*
- Kippt die Schlussfolgerung zwischen Primär- und Zweitspezifikation, wird **das** berichtet —
  es ist ein Ergebnis, keine Auswahlgelegenheit.

- **Fallback (vorab registriert):** Findet das HMM faktisch nur den April-2026-Bruch
  oder scheitert (3), wird das als **diagnostiziertes Negativ-Ergebnis** berichtet
  („gaußsche, yield-only Zustände tracken statistische Struktur statt ökonomischer
  Regime"), inklusive Diagnose und Abhilfen (t-verteilte Emissionen, Jump Models) —
  **nicht** das Modell zum Funktionieren zwingen.

---

## 3. Scope — bewusst ausgeschlossen (Negativliste)

Vier Designentscheidungen sind vorab fixiert, um die Frage auf kurzem Sample
identifizierbar zu halten. Cowork soll diese Grenzen NICHT eigenmächtig aufweichen:

1. **K = 2 Regime** (crisis/normal). Kein drittes Regime — die Krise ist ab April
   2026 nahezu durchgängig, ein drittes würde aus zu wenigen Tagen geschätzt.
2. **One-Factor Hull-White.** Kein zweiter Faktor (G2++) — würde den Regime-Effekt
   mit Querschnitts-Flexibilität konfundieren.
3. **Nur Euroraum-AAA-Yields.** Kein Vergleichsmarkt — die Event-Validierung ist um
   die Euroraum-Narrative gebaut und würde nicht übertragen.
4. **Voll integriertes, Markov-moduliertes HW** (latenter Zustand steuert die
   SDE-Parameter, gemeinsame Schätzung) ist die **benannte Weiterführung**, bewusst
   vertagt. Gehört in den Discussion-Teil, wird NICHT gebaut.

---

## 4. Wie wir arbeiten (Arbeitsweise & Rollenverteilung)

### Grundprinzipien

- **Stufenweise, mit Halt vor jeder Festlegung.** Große Entscheidungen werden
  benannt und bestätigt, bevor gebaut wird — nicht implizit während des Baus
  getroffen.
- **Ehrlichkeit zu Schwächen als Stärke.** Grenzen werden als bewusst abgesteckter
  Geltungsbereich formuliert, nicht versteckt. Ein scharfer Gutachter sieht sie ohnehin.
- **Falsifizierbarkeitssprache:** „wir prüfen, ob" / „die Ergebnisse legen nahe",
  nicht „wir beweisen" / „zeigt".
- **Kostenlose Quellen zuerst.** Bei Paywall aktiv freie Versionen suchen.
- **Keine erfundenen Fakten, Zahlen, Quellen.** Im Zweifel kennzeichnen, nicht
  behaupten. Datenfakten nur aus dem verifizierten Daten-Vollständigkeitsbericht.
- **Reproduzierbarkeit:** Jede Spalte in den CSVs muss bis zur Primärquelle durch
  **Ausführen eines Skripts** rückführbar sein, nicht durch Behauptung.

### Rollen der einzelnen Arbeitsstränge

- **Cowork (du):** Umsetzung — Tagesplan, Code, Pipeline, Abgaben-/Fristenprüfung,
  Ausführung der To-Dos aus §8. Das operative Bauen.
- **Strategie-Chat:** die großen Fragen — Konzepte erklären, Paper-Argumentation
  reviewen, Strategie anpassen. Macht ausdrücklich NICHT Tagesplan
  oder Abgabenprüfung.
- **Quellen-Chat:** ~~ausschließlich Literaturrecherche~~ — **aufgehoben 2026-08-26 (Klaus).**
  Die Literaturrecherche liegt ab diesem Datum bei Cowork; Belege werden an der Primärstelle
  geprüft und in `BELEGPLAN.md` geführt (Entscheidung → Argument → Quelle → Fundstelle).
- **Sprach-Chat:** ausschließlich wissenschaftliches Englisch.
- **Paper-Skelett-Chat:** ausschließlich die Section-Architektur des Papers.

*[Abschnitt mit persönlichen Angaben in der Repository-Kopie entfernt.]*

---

## 5. WICHTIG — Richtungswechsel: von Case-Study zu Regime-Switching

**Bis 2026-05-30** war das Projekt als Hull-White-**Case-Study** unter einem
Stress-Event gerahmt: HW pro Handelstag aus der Querschnitts-Yieldkurve kalibriert,
das Regime nur Metadaten, kein HMM. Dieser Abschnitt der alten METHODIK ist
**abgelöst** *[Persönliche Begründung in der Repository-Kopie entfernt.]*

**Konsequenz für die Pipeline (Stand 2026-06-01): Sie ist noch auf die Case-Study
eingerichtet und muss umgebaut werden.** Was das konkret heißt, steht in §8. Wichtig:
Die crisis-only-`context_events.csv` muss dafür **nicht** mit `normal`-Tagen
aufgefüllt werden — das HMM läuft unüberwacht auf den Yield-Änderungen über das volle
Sample und braucht keine vorab gelabelten Normaltage. Der alte 3-Regime-Backfill-Plan
ist damit gegenstandslos.

---

## 6. Datenartefakte & Reproduktion (Pipeline-Referenz)

| Datei | Inhalt | Erzeuger | Quelle |
|---|---|---|---|
| `yields.csv` | EZB AAA-Yieldkurve, 11 Laufzeiten | `build_yields.py` | EZB SDW REST-API |
| `context_prices.csv` | Aktien/FX/Rohstoffe/Anleihen + Fed Funds | `build_context.py` (`build_prices`) | yfinance + FRED |
| `context_events.csv` | Tageszustand (regime/event) pro Briefing-Tag | `build_context.py` (`extract_events_from_pdfs`) | Briefing-PDFs + Regex-Heuristik |
| `context.csv` | Merge auf `date` (Preise links, Events rechts) | `build_context.py` (`merge_context`) | obige drei |
| `key_events.csv` | Manuell kuratierte Schlüsselereignisse mit Primärquellen | manuell + WebSearch-Verifikation | EZB/Fed/Reuters/CNBC etc. |

### `yields.csv` — verifizierter Stand
- **378 Handelstage, 02.01.2025–26.06.2026, 11 Laufzeiten (3M, 6M, 1Y, 2Y, 3Y, 5Y,
  7Y, 10Y, 15Y, 20Y, 30Y), 0 % fehlend.** *(Korrigiert 26.09.2026 gegen die Datei; die
  frühere Angabe „357 Handelstage bis 28.05.2026" stammt aus der Zeit vor der Aktualisierung der Datei, mtime 29.06.2026)*
  Die Änderungsbildung kostet den ersten Tag: `hmm_input_changes.csv` hat **377 Tage,
  03.01.2025–26.06.2026**, datumsgleich mit Zeile 2–378 von `yields.csv` (geprüft).
- Serien-Schlüssel: `B.U2.EUR.4F.G_N_A.SV_C_YM.SR_<MATURITY>` (EZB SDW, Endpoint
  `https://data-api.ecb.europa.eu/service/data/YC/...`). Im Exposé als
  `YC.B.U2.EUR.4F.G_N_A.SV_C_YM` zitiert — dieselbe Reihe.
- Reproduktion: `python build_yields.py` (Default ab 2025-01-01; `--start`, `--end`
  für andere Fenster).
- Caveats: T+1-Publikations-Lag; EZB revidiert Historie gelegentlich 1–2
  Geschäftstage rückwirkend.
- **Offen (zu beheben):** `build_context.py` lädt die Yields NICHT; die Herkunft
  ruht allein auf dem Seriencode → im Paper „bezogen aus EZB-Serie …", NICHT
  „skriptbasiert reproduzierbar". To-Do: EZB-Download in die Pipeline integrieren.

### `context_prices.csv`
- yfinance (kein Key): `^GSPC, ^IXIC, ^GDAXI, EURUSD=X, BZ=F, GC=F, ^VIX, ^TNX`;
  FRED (kein Key): `DFF`.
- Reproduktion: `python build_context.py` (Volllauf) bzw. `--no-events` (nur Preise).
- Caveats: yfinance inoffiziell; Skript erst nach US-Close laufen lassen; FRED `DFF`
  mit 1–2 Tagen Lag.

### `context_events.csv` — regime/event je Briefing-Tag
- Schema `date, regime, event`. `regime` ∈ {crisis, normal}; `event` aus geschlossenem
  Muster-Set via `EVENT_PATTERNS` (Dominanz-Reihenfolge, erster Treffer gewinnt).
- **Quellenbasiert & skriptreproduzierbar** seit den drei Verschärfungen vom
  2026-05-31: `ezb_hold/hike` nur bei Entscheidung am Briefing-Tag; `risk_off` nur bei
  Gesamtmarkt-Trigger; `hormus_eskalation` nur bei akutem Vorfall (Hedge-Kontext
  verworfen). Einziger verbleibender manueller Tag: 2026-04-16 (Bild-PDF, kein OCR).
- **Die Yields werden bei der Tag-Erzeugung nie gelesen → kein Look-ahead.**
- Merge `context.csv`: LEFT JOIN (Preise Grundtabelle). Sanity-Checks: Zeilenzahl ==
  `context_prices.csv`; getaggte Tage == Zeilen `context_events.csv` minus preislose
  Tage; keine Stale-Tags.

---

## 7. `key_events.csv` — Auswahlregel & Same-Day-Konvention

**26 Events** (Stand 2026-07-27; zuvor 17 — Fortschreibung siehe Audit-Zeile unten),
Schema `date, event, description, source`. Reine externe
Validierungs-Ground-Truth, **kein Modell-Input**.

### Auswahlregel (deklariert, vor dem ersten Fit fixiert) — mind. eines von vier Kriterien
1. Geldpolitische Entscheidung mit Signalwert (EZB/Fed): Cut/Hike ODER Hold mit
   Dissens/Guidance-Änderung — NICHT jede Routine-Sitzung.
2. Geopolitischer Schock mit eigenständiger Marktnarrative (Hormus, Tarif-Schock).
3. Makroökonomische ODER fiskalpolitische Überraschung, die ein Briefing als
   Tagesthema dominierte (z.B. CPI/PCE, PMI; fiskalpolitisch: Schuldenbremse-Reform).
4. Institutioneller Führungswechsel bei EZB/Fed, der die Reaktionsfunktion verändert
   — nur der datierbare entscheidende Akt (Warsh: eine Zeile am Bestätigungsdatum
   13.05., prozedurale Schritte bewusst draußen).

Audit 2026-05-31: 17 Events, 0 ungedeckt (K1=9, K2=4, K3=3, K4=1). (Die beiden hormus_deeskalation-Zeilen 25.05./31.05. wurden zu einer Zeile am Wirkdatum 31.05. zusammengelegt — derselbe Deeskalations-Vorgang, erst signalisiert, dann vorlaeufig vereinbart.)

Audit 2026-07-27 (Fortschreibung Zeilen 18–28, gegen die Datei code-verifiziert): **26 Events, 0 ungedeckt (K1=11, K2=8, K3=6, K4=1).** Änderungen: `tech_selloff` 05.06. auf die Payroll-Überraschung umgehängt (K3, Label `payroll_surprise`, Primärquelle BLS); `tech_selloff` 24.06. gestrichen (von keinem Kriterium gedeckt + zirkulär: „Ereignis" = Marktbewegung selbst); `hormus_eskalation` 28.06. gestrichen (Same-Day-Verstoß + nach Sample-Ende 26.06.); Same-Day-Beschreibungen 14.06. und 20.06. auf kontemporäre Fakten gekürzt (Folgetags-/Montags-Marktdaten entfernt); Label `hormus_escalation`→`hormus_eskalation` vereinheitlicht; Primärquellen BLS (Payrolls) und BEA (PCE) nachgetragen. Von den 26 Events liegen **21 im Handelstags-Index** (`hmm_input_changes.csv`), 5 auf Wochenendtagen (28.02., 31.05., 07.06., 14.06., 20.06.). Vollständigkeits-Scan 01.–26.06. (alle Briefings gelesen): ein Grenzfall (Eurozone-Flash-CPI Mai 3,2 % am 02.06., nicht briefing-dominant → nicht aufgenommen); BoE/PBoC/Micron/G7/Juni-Flash-PMIs bewusst außerhalb K1–K4. **ENTSCHIEDEN 2026-08-05 (Klaus, vor dem Fit) — Details in der Regel-Subsection unten:** (a) Cluster wird NICHT konsolidiert (gegenläufige, eigenständige Akte); die Ereignis-Abhängigkeit wird im Test über den zirkulären Shift abgefangen (§2). (b) Nicht-Handelstage → nächster Handelstag.

### Konsolidierungs- und Zuordnungsregeln (fixiert 2026-08-05, vor dem Fit)

**Konsolidierungsregel.** Konsolidiert wird nur, was **denselben Akt in derselben
Richtung** mehrfach erfasst (Signal → Bestätigung). Ein **Richtungswechsel begründet
immer eine eigene Zeile.** Damit ist die Zusammenlegung vom 31.05. begründet (Signal
25.05. → vorläufige Vereinbarung 31.05., beides Deeskalation), und die gegenläufige
Juni-Kette bleibt **vierzeilig**: Eskalation 07.06. → Abkommen 14.06. → erneute
Schließung 20.06. → Roadmap 22.06. Ein Abkommen und eine Blockade sind nicht dasselbe
Ereignis mit umgekehrtem Vorzeichen, sondern zwei Ereignisse; sie zu mergen würde echte
Information löschen. Die verbleibende Ereignis-Abhängigkeit ist ein **Testdesign-Thema**,
kein Datenthema — sie wird über den zirkulären Shift-Test abgefangen (§2), nicht durch
Wegmitteln in den Daten.

**Zuordnungsregel Nicht-Handelstage.** Ereignisse an Nicht-Handelstagen werden dem
**nächsten Handelstag** zugeordnet (ökonomisch die einzig zulässige Richtung: eine
Nachricht kann sich frühestens am nächsten Handelstag im Preis niederschlagen;
Zurückschieben unterstellte Look-ahead, Ausschluss kostete 5/26 Events inkl. des
Krisen-Auslösers `hormus_start` 28.02.). Konkret, code-geprüft im Sample: 28.02.→02.03.,
31.05.→01.06., 07.06.→08.06., 14.06.→15.06., 20.06.→22.06. **Nähemaß-Fenster ±k
Handelstage mit k ≥ 2** (US-Abend-Releases erreichen die Euro-Kurve erst am Folgetag —
bei k = 1 hinge das Ergebnis an der Ein-Tages-Zuordnung); **Sensitivität über
k ∈ {1, 2, 3} berichtet.** Hinweis: Juneteenth (19.06.) schließt nur den US-Aktienmarkt,
nicht die Euro-Kurve — 19.06. ist in `hmm_input_changes.csv` ein regulärer Handelstag.

### Regimewechsel-Definition (B2) — entschieden und eingetragen 2026-08-10, vor dem Testlauf

**Worum es ging.** Der Permutationstest misst, wie nah die Ereignisse an den
*Regimewechseln* liegen. Dafür muss definiert sein, wann der Regimepfad überhaupt als
„gewechselt" gilt. Das gefittete HMM liefert pro Handelstag zwei verschiedene Dinge:

- **P(crisis)** aus `predict_proba` — die geglättete Wahrscheinlichkeit **für den
  einzelnen Tag** (Randverteilung, punktweise);
- den **Viterbi-Pfad** aus `predict` — die wahrscheinlichste **Zustandsfolge** über alle
  Tage hinweg.

Zur Wahl standen: **(a)** P(crisis) kreuzt die 0,5-Schwelle · **(b)** Übergang im
Viterbi-Pfad · **(c)** 0,5-Kreuzung mit Mindestverweildauer m (Läufe kürzer als m Tage
werden geglättet).

**Die Zahlen** (ereignis-blind allein aus dem Regimepfad, Seed 42, `covariance_type="full"`,
code-verifiziert 05. und 10.08.2026 — sie verraten *nicht*, ob Ereignisse nah an Wechseln liegen,
und verletzen die Vorab-Registrierung daher nicht):

| Definition | Wechsel | Krisen-Episoden | Krisentage | Nähe-Abdeckung bei k=2 |
|---|---|---|---|---|
| (a) 0,5-Kreuzung | 17 | 9 | 133 | 19,4 % |
| **(b) Viterbi** | **13** | **7** | **139** | **16,4 %** |
| (c) m = 3 | 13 | 7 | 130 | 16,4 % |
| (c) m = 5 | 9 | 5 | 131 | — |

*Episoden inklusive der links-zensierten ersten Episode: Beide Pfade starten am
03.01.2025 bereits im Krisenzustand. Dieser Beginn ist **kein beobachteter Wechsel** —
die Wechselmenge enthält ausschließlich innere Übergänge. Ohne die Rand-Episode gezählt
sind es jeweils eine weniger (8 / 6 / 6 / 4); die Konvention „mit Rand-Episode" gilt.*
„Nähe-Abdeckung" = Anteil aller 377 Handelstage, die innerhalb von ±k Tagen um einen
Wechsel liegen. Das ist zugleich die **Zufalls-Basisrate** des Rotationstests.

**ENTSCHIEDEN 2026-08-10 (Klaus, nach Gegenlesen im Strategie-Chat; Vorlage und Verifikation 05.08.): (b) Viterbi als Primärspezifikation, (a) als vorab registrierte
Zweitspezifikation, jeweils mit Sensitivität k ∈ {1, 2, 3}.**

Begründung:

1. **Kein Konflikt mit der smoothed-Vorgabe aus §2.** Diese Vorgabe regelt den
   *Informationsstand* (ganze Reihe statt nur bis t) und ist unabhängig davon, wie aus
   der Verteilung ein Pfad gemacht wird. Viterbi nutzt dieselbe volle Information; das
   Look-ahead-Argument, das filtered von smoothed trennt, ist hier nicht berührt.
2. **Ein Wechsel ist eine Eigenschaft der Zustands*folge*, kein Merkmal eines einzelnen
   Tages.** Der geschwellte Randposterior ist kein Folgen-Schätzer: Er kann eine Sequenz
   erzeugen, die unter dem Modell die Wahrscheinlichkeit null hat (Bishop, PRML 13.2.5).
   Genau daher rührt das Pendeln um die Schwelle („Chatter") in (a) — es ist Symptom
   einer falschen Schätzerklasse, keine Kosmetik. Viterbi ist der Folgen-Schätzer.
3. **(c) behandelt das Symptom statt der Ursache** und kauft dafür einen frei wählbaren
   Parameter m ein, der selbst vorab zu registrieren und sensitivitätszuprüfen wäre. Zur
   Klarstellung, weil eine frühere Fassung dieses Arguments das falsch behauptet hat:
   (c) ist **nicht** dasselbe wie (b). Die Pfade weichen an **11 Tagen** voneinander ab,
   während (c) nur **3 Tage** von (a) entfernt liegt (die Abweichungsmengen sind
   disjunkt). Dass (c) m=3 und (b) beide auf 13 Wechsel kommen, ist eine Koinzidenz
   dieses Datensatzes. Aufschlussreich ist gerade das: Läge Viterbi nur am Wegglätten
   kurzer Läufe, müsste es nahe bei (c) liegen — es liegt weiter entfernt als (a),
   entscheidet also tatsächlich auf Basis der Sequenz-Likelihood neu.
4. **Das Risiko ist klein, der Gewinn messbar.** (a) und (b) widersprechen sich nur an
   **8 von 377 Tagen (2,1 %)** — die Regime liegen also praktisch gleich; Viterbi
   entfernt vor allem das Pendeln. Zugleich sinkt die Zufalls-Basisrate von 19,4 % auf
   16,4 % (k=2), der Test wird also **schärfer** — was bei der dünnen Power (nur 10 der
   26 Events liegen vor dem Dauer-Krisenblock ab April 2026) zählt.

**Operativ.** Wechselvektor = Vorzeichenwechsel der Viterbi-Zustandsfolge
(`model.predict(X)`), Krisenzustand über die **größere Kovarianz-Spur** identifiziert
(label-switching-sicher, wie im ganzen Projekt) → **13 Wechsel**. Derselbe Test läuft
zusätzlich mit (a) und wird berichtet. Kippt die Schlussfolgerung zwischen (a) und (b),
ist **das** das Ergebnis — es wird berichtet, nicht ausgewählt.

**Erwartete Treffer unter H₀** (nur aus Regimepfad und Ereignis*zahl* berechnet, ohne die
Lage der Ereignisse — gehört in den Power-Abschnitt des Test-Designs):

| | k=1 | k=2 | k=3 |
|---|---|---|---|
| (a) 0,5-Kreuzung | 3,31 | 5,03 | 6,55 |
| **(b) Viterbi** | **2,62** | **4,28** | **5,72** |

*(gerechnet mit 26 Ereignissen; siehe offener Punkt unten)*

### Teststatistik und Zählweise (B3, D1) — entschieden 2026-08-25, vor dem Testlauf

**B3 — Teststatistik: die Zählvariante.** Gezählt wird, **wie viele Ereignisse innerhalb von
±k Handelstagen eines Regimewechsels liegen**. Die Alternative (mittlerer Abstand jedes
Ereignisses zum nächstgelegenen Wechsel) ist damit ausgeschlossen und wird **nicht**
nachgereicht. Begründung: Die Zählvariante ist unmittelbar interpretierbar, koppelt direkt an
das ohnehin festgelegte Fenster k und hängt nicht davon ab, wie weit entfernte Ereignisse
gewichtet werden.

**D1 — Gezählt werden Ereignisse (26), nicht Ereignistage (25).** Durch die Zuordnung
20.06. → 22.06. fallen zwei Ereignisse auf denselben Handelstag. Sie zählen **einzeln**, weil
Forschungsfrage (a) Ereignisse betrifft und die Konsolidierungsregel oben den 20.06. und den
22.06. ausdrücklich als zwei eigenständige Akte führt; sie über das Datums-Mapping doch noch
zu verschmelzen, würde diese Entscheidung stillschweigend rückgängig machen. **Technisch:**
Zählvektor (`np.add.at`) statt booleschem Vektor — mit einem Ja/Nein-Vektor verschwindet ein
Ereignis lautlos (25 statt 26). Kontrollsumme im Skript: 26.

### Episodendefinition für die Zweitspezifikation (entschieden 2026-08-26, vor dem Testlauf)

Die in §2 angemeldete Zweitauswertung „eine Zeile je Episode" war bis hierher nicht operationalisiert
— und damit nach dem Blick aufs Ergebnis noch wählbar. Sie wird deshalb hier geschlossen:

**Ein *Strang* ist die Menge aller Zeilen mit `event`-Präfix `hormus_`; jede übrige Zeile bildet für
sich eine Strang-Einheit. Innerhalb eines Strangs gehören aufeinanderfolgende Zeilen zu derselben
Episode, wenn zwischen ihnen höchstens 14 Kalendertage liegen. Vertreten wird eine Episode durch ihre
erste Zeile (den Auslöser).**

Angewandt auf `key_events.csv` (code-verifiziert 26.08.2026): Der Hormus-Strang hat 7 Zeilen mit den
Abständen 46 · 46 · 7 · 7 · 6 · 2 Kalendertagen. Der 28.02. und der 15.04. bleiben damit eigenständig;
**31.05., 07.06., 14.06., 20.06. und 22.06. bilden eine Episode, vertreten durch den 31.05.**
(Zuordnung nach B5 → 01.06.). Alle übrigen 19 Zeilen sind je eine eigene Episode.
**Ereigniszahl der Zweitspezifikation: 22, auf 22 eindeutigen Handelstagen** — die Kollision vom
22.06. entfällt hier, weil beide betroffenen Zeilen in derselben Episode liegen.

Warum die Strang-Definition ausgezählt statt „thematisch" formuliert ist: Eine bloß thematische
Formulierung verlagert den Freiheitsgrad nur von „Was ist eine Episode?" auf „Was ist ein Strang?".
Nachgerechnet ergäbe eine breitere Strangfassung 21 Ereignisse (wenn `cpi_surprise` 28.05. und 10.06.
als ein Strang gelten — Abstand 13 Tage) bzw. 20 (wenn zusätzlich `fed_hold` 29.04. und
`fed_chair_change` 13.05. als „Fed"-Strang gelten — Abstand exakt 14 Tage). Die Zahl wäre also
zwischen 20 und 22 wählbar geblieben. Mit der obigen Auszählung ist sie determiniert.

Damit sind **alle sechs Designfragen (B1–B6) sowie D1 entschieden**; das Testdesign ist
vollständig vorab registriert und der Testlauf freigegeben.

**Herleitung im Detail:** `AUDIT_Permutationstest-B2_Regimewechsel_2026-08-05.md`
(Optionen und Rohzahlen) und `B2_GEGENLESEN_2026-08-05.md` (Verifikation, inkl. der
Korrektur zu Punkt 3).

### Same-Day-Konvention für `description` (Leakage-Schutz)
Nur **kontemporäre Fakten** (am Briefing-Abend bekannt): Niveau, Tages-%-Move,
Vote-Split, Index-/PMI-Stand, das Ereignis selbst. **Verboten:** kumulative Aggregate
(Mehrtages-/Monatsfenster), superlative Ex-post-Rangierungen, nach dem Tag wissbare
Korrekturen. Bereinigt 2026-05-31 — betroffen waren **11 von 18 Zeilen** (die frühere
Behauptung „ein Eintrag" war eine Untertreibung um eine Größenordnung).

### Leakage-Beleg & Restrisiko
- Beleg, dass die Auswahl an der Nachrichtenlage hängt, nicht an der Yield-Bewegung:
  Tarif-Schock 2025-04-02 ist drin, obwohl die Bund-Rendite an dem Tag flach war
  (+0,2 bp, 5. Perzentil).
- Bei der Validierung yield-basierter Regime gegen Events sollten die wenigen
  Rekord-Yield-Tage (v. a. 2025-03-05, +30 bp) gesondert behandelt oder der
  Zusammenhang offengelegt werden (milde Zirkularität).

---

## 8. Offene Aufgaben — Pipeline-Umbau (To-Do, nach Priorität)

**HOCH — der Kern des Umbaus von Case-Study auf HMM:**
1. **HMM-Stage bauen** (`hmmlearn` o. Ä.): Gauß-Emissionen auf Tagesänderungen von
   Level/Slope/Curvature → smoothed UND filtered Regimepfad als neues Artefakt
   (z. B. `regime_path.csv`).
2. **Stage 2 umstellen:** (*a*, *σ*) regime-bedingt aus der 3M-Zeitreihe unter P-Maß
   schätzen (Diskretisierung), mit Bootstrap-CIs. NICHT pro Tag aus der
   Querschnittskurve (das war die Case-Study-Logik).
3. **Validierung implementieren:** Permutationstest (Event-Daten gegen fixen
   Regimepfad), Stage-1-BIC (1 vs. 2), Stage-2-BIC (bedingt), Abbruchkriterium.
4. **yields.csv-Herkunft skriptbasiert machen:** EZB-Download in die Pipeline ziehen.

**MITTEL:**
5. `yields.csv` und Kontextrand gleichlaufen lassen (Staleness 28.05. vs. 29.05.).
6. Briefing 2026-04-16 per OCR nachziehen (mögliche Ereignis-Lücke).

**Erledigt / bewusst nicht zu tun:**
- 3-Regime-Backfill von `context_events.csv` → **gegenstandslos** (HMM ist
  unüberwacht, braucht keine Normaltage).
- Auswahl- und Same-Day-Regel für `key_events` → deklariert und angewandt.

---

## 9. Für das Methodik-Kapitel des Papers vormerken (nicht im Exposé)

1. **Stage-2-BIC ist ein bedingter Vergleich** (auf den Regimepfad bedingt). Explizit
   schreiben, dass der Stage-1-BIC den Penalty für die Regime-Struktur trägt — sonst
   liest sich der Komplexitäts-Penalty zu günstig fürs Mehr-Regime-Modell.
2. **Anwendung der a-priori-Kriterien war ein Ermessensakt.** Die Kriterien standen
   vorab fest, ihre Zuordnung zu den Briefings war nicht vollautomatisch — ehrlich
   benennen.
3. **Same-Day-Bereinigungsregel als reproduzierbares Verfahren dokumentieren,** mit
   dem Tarif-Schock 02.04. als Leakage-Beleg.
4. **Rekord-Yield-Tage** bei der yield-basierten Regime-Validierung gesondert
   behandeln (milde Zirkularität offenlegen).

---

## Anhang A — Abgelöst: crisis-only-Case-Study-Rahmung (historisch, 2026-05-30)

Die frühere Rahmung („Hull-White-Kalibrierung als Case-Study eines Stress-Events,
Regime nur Metadaten, kein HMM, HW pro Tag aus der Querschnittskurve") ist **nicht
mehr gültig**. Sie ist hier nur als Historie vermerkt, damit alte Verweise im Code
oder in Briefings einordbar bleiben. Maßgeblich ist §2. Wer auf Formulierungen wie
„case study", „Regime ist nur Metadaten" oder „pro Handelstag kalibriert" stößt:
das gehört zur abgelösten Fassung und ist gegen §2 zu ersetzen.

---

## Workflow Wochen-Sync (unverändert gültig)

1. Neue Briefing-PDFs in `Morning Briefing/` ablegen.
2. `python build_context.py --briefings "<Pfad>"` → `context_prices.csv` +
   `context_events.csv` + `context.csv`.
3. `context_events.csv` manuell prüfen (Heuristik-Schwächen, Bild-PDF-Tage).
4. `python build_yields.py` → EZB-AAA-Kurve aktualisieren.
5. `key_events.csv` prüfen: neues Schlüsselereignis? Nach Auswahlregel (§7) mit
   verifizierter Quelle und Same-Day-Beschreibung eintragen.
6. Sanity-Checks laufen lassen.

**Sicherheits-Schutz (seit 2026-05-30):** `build_context.py` überschreibt
`context_events.csv` nicht mehr bei fehlendem/leerem `--briefings`-Pfad oder
`--no-events`, damit manuelle Edits geschützt bleiben.
