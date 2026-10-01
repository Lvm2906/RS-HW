# Belegplan RS-HW — Entscheidung → Argument → Quelle → Fundstelle

**Angelegt 26.08.2026.** Ab dem 26.08.2026 recherchiert Cowork die Literaturbelege selbst (Regeländerung durch Klaus; ersetzt die frühere Aufgabenteilung mit dem Quellen-Chat, METHODIK §4). Jede Quelle wird an der Primärstelle geprüft, nicht aus dem Gedächtnis zitiert; Zugänglichkeit (frei/Paywall) ist vermerkt.

---

## B-1 · τ = 0 wird mitgezählt, p ist nie 0

**Entscheidung:** D3 der Vorab-Registrierung — p = #{τ : T(τ) ≥ T_obs} / 377, die unverschobene Anordnung eingeschlossen. Kleinster erreichbarer p-Wert 1/377 = 0,00265.

**Beleg:** Phipson, B. & Smyth, G. K. (2010): *Permutation P-values Should Never Be Zero: Calculating Exact P-values When Permutations Are Randomly Drawn.* Statistical Applications in Genetics and Molecular Biology **9**(1), Article 39. DOI 10.2202/1544-6115.1585. **Frei zugänglich** als arXiv:1603.05766. Umsetzung: R-Paket `statmod`, Funktion `permp`.

**Was die Quelle trägt — und was nicht.** Sie trägt das Prinzip: Die beobachtete Anordnung ist selbst eine der unter H₀ zulässigen Anordnungen; sie aus der Zählung zu streichen behauptet Unmöglichkeit und unterschätzt den p-Wert systematisch. **Sie trägt nicht direkt unseren Fall.** Phipson & Smyth behandeln den Fall *zufällig gezogener* Permutationen und leiten dafür den Schätzer (b+1)/(m+1) her. Wir zählen die Rotationsgruppe **vollständig** auf; dort ist p ≥ 1/377 keine Korrektur, sondern eine automatische Folge der vollständigen Aufzählung. Die Quelle ist also als *Begründung des Prinzips* zu zitieren, nicht als Rechenvorschrift. So im Paper formulieren — ein Gutachter, der die Arbeit kennt, merkt den Unterschied sofort.

---

## B-2 · Zirkulärer Shift statt unabhängiger Permutation

**Entscheidung:** METHODIK §2, Entscheidungsregister #29/#30 — der Ereignisvektor wird als Ganzes zyklisch verschoben (wrap-around), damit die Ereignis-Klumpung unter H₀ erhalten bleibt; alle 377 Verschiebungen werden aufgezählt.

**Beleg (Ursprung):** Lotwick, H. W. & Silverman, B. W. (1982): *Methods for analysing spatial processes of several types of points.* Journal of the Royal Statistical Society, Series B **44**(3), 406–413. Das ist die Standardreferenz für den toroidalen (wrap-around) Verschiebungstest: Ein Prozess bleibt fest, der andere wird wiederholt zufällig verschoben; das erzeugt eine Nullverteilung unter Unabhängigkeit, **ohne die interne Struktur des verschobenen Prozesses zu zerstören**. Genau das ist unser Argument. Paywall (JSTOR); in R umgesetzt als `IndTestPP::TestIndLS`.

**Beleg (moderne Einordnung und Kritik):** Mrkvička, T., Dvořák, J., González, J. A. & Mateu, J. (2020): *Revisiting the random shift approach for testing in spatial statistics.* Spatial Statistics **42**, 100430. DOI 10.1016/j.spasta.2020.100430. **Frei zugänglich** als arXiv:1911.00240.

**Transfer 2D → 1D:** Beide Quellen sind räumlich (Torus = Rechteck mit verklebten Rändern). Unser Fall ist der eindimensionale Spezialfall — der Torus wird zum Kreis, die zyklische Verschiebung um τ Indexpositionen ist die 1D-Rotation. Der Transfer ist unmittelbar, sollte im Paper aber **ausgesprochen** werden, statt so zu tun, als sei die Quelle über Zeitreihen. Eine ebenso etablierte, eigenständig zitierbare Zeitreihen-Referenz für genau diesen Test habe ich bei der Recherche **nicht** gefunden; die belastbare Linie läuft über die räumliche Statistik.

---

## B-3 · Der Wrap-around ist eine Einschränkung mit Richtung (NEU, 26.08.2026)

**Befund aus B-2, der über einen Beleg hinausgeht.** Mrkvička et al. (2020) zeigen, dass der toroidale Shift **liberal** ist: Das Verkleben der Ränder zerreißt die Korrelationsstruktur an der Naht, die Austauschbarkeit unter H₀ ist verletzt, und der Test **verwirft zu oft**. Sie schlagen als Abhilfen Varianzkorrektur (Faktor 1/n), Minus-Korrektur (Randerosion) oder alternative Teststatistiken vor.

**Konsequenz für RS-HW — und warum sie hier harmlos ist.** Ein liberaler Test verzerrt zugunsten der Signifikanz. Unser Ergebnis ist **nicht** signifikant (p = 0,1088). Die Verzerrung wirkt also gegen unsere Schlussfolgerung, nicht für sie: Ein korrigierter Test hätte einen **noch größeren** p-Wert geliefert. Das Negativergebnis wird durch diesen Befund **gestützt, nicht geschwächt**. Umgekehrt gilt: Wäre das Ergebnis signifikant gewesen, wäre dieselbe Literaturstelle ein ernstes Problem geworden.

**Nicht getan:** Der Text von E1 in `PRAEREGISTRIERUNG_Permutationstest_2026-08-25.md` („bedeutungslose Naht, offengelegt, keine Entwertung") bleibt **unverändert**. Die Vorab-Registrierung ist ein historisches Dokument; sie nachträglich mit nach dem Lauf gefundener Literatur zu schärfen, würde genau die Eigenschaft zerstören, für die sie da ist. Der Befund gehört in den Limitations- und Diskussionsteil des Papers, mit Datum und der ehrlichen Angabe, dass er nach dem Testlauf gefunden wurde.


**Korrekturvermerk 01.10.2026 (Cowork, Prüfbericht K6; von Klaus freigegeben):** Zwei Aussagen dieses Abschnitts sind **zu stark**. (1) „Ein korrigierter Test hätte einen **noch größeren** p-Wert geliefert" und „Das Negativergebnis wird … **gestützt**" setzen voraus, dass die Liberalität auf unseren Fall übertragbar ist. Mrkvička et al. belegen sie für Zufallsfelder; für Punktmuster nennen sie das Problem „far more complex" und statistikabhängig (Abstract). Unser Fall — Ereignis-Zählung auf der Linie gegen eine feste, nicht-zirkuläre Maske — liegt näher am Punktmusterfall und wurde nicht untersucht. Tragfähig ist nur die bedingte Form: *Falls* der Test auch hier liberal ist, wirkt die Verzerrung gegen das berichtete Ergebnis. (2) „schlagen … Minus-Korrektur … vor" ist falsch zugeschrieben: Vorgeschlagen wird die **Varianzkorrektur** (S. 7); die Minus-(Rand-)Korrektur ist bekannt und wird von ihnen beschrieben (S. 3). Paper §5 entsprechend umformuliert („may be liberal"). Die Vorab-Registrierung bleibt unverändert.

---

## Offen — die 15 mit „Literatur nötig" markierten Entscheidungen

Aus `UEBERSICHT_RS-HW_2026-08-10.md` §5, noch nicht bearbeitet: #3 (entkoppelte Zweistufigkeit) · #4 (Änderungen statt Niveaus / Einheitswurzel) · #9 (P- vs. Q-Maß, calibration vs. estimation) · #10 (Bootstrap-CIs als Materialitätskriterium) · #11 (Permutationstest als Haupttest) · #12 (Präregistrierung) · #13 (PCA-Faktoren der Zinskurve) · #14 (Label-Switching) · #16 (BIC) · #17 (Forward-Rekursion) · #18 (Look-ahead, filtered vs. smoothed) · #20 (Zirkularität) · #22 (Data-Leakage) · #24 (Event-Study-Konvention Nicht-Handelstage) · #26 (Informationsstand vs. Dekodierer).

Für #14, #17, #26 liegt Bishop (PRML) bereits als PDF im Ordner; für #16 Rabiner (1989); für #5/#11 Hamilton (1989) und Ang & Bekaert (2002) unter `Materialien/00_Exposé/`. Dort ist die Arbeit **Zuordnung von Fundstellen**, nicht Suche.

---

## B-4 · OU-Diskretisierung, AR(1) und Rückrechnung auf (a, σ)

**Entscheidung:** METHODIK §2, Stage-2-Schätzdesign Punkt 3 — exakte Diskretisierung der OU-Dynamik liefert ein AR(1); (a, σ) folgen aus AR(1)-Koeffizient und Residuenvarianz.

**Beleg:** Brigo, D., Dalessandro, A., Neugebauer, M. & Triki, F. (2008): *A Stochastic Processes Toolkit for Risk Management*, arXiv:0812.4210, **Abschnitt 7 (Mean Reversion: The Vasicek Model)**. **Frei.** Fundstellen am Volltext geprüft (20.09.2026): SDE Gl. 47 · exakte Lösung Gl. 48 · diskrete Form Gl. 49 · Koeffizienten c, b, δ Gl. 52 · Rückrechnung α = −ln(b)/Δt Gl. 55, θ = c/(1−b) Gl. 56, σ Gl. 57 · Schätzformeln Gl. 58–60.

**Was die Quelle trägt — und was nicht.** Trägt: die vollständige Kette SDE → exakte Diskretisierung → AR(1) → (a, σ), mit Gleichungsnummern. **Trägt nicht: den MLE-Weg.** Abschnitt 7 gibt ausschließlich OLS (Gl. 58–60) und verweist für Maximum Likelihood nur auf eine andere Arbeit.

## B-5 · Maximum-Likelihood-Formeln (Ersatzbeleg für B-4)

**Beleg:** van den Berg, T. (2011): *Calibrating the Ornstein-Uhlenbeck (Vasicek) Model*. **Frei.** Enthält Least-Squares **und** Maximum Likelihood in geschlossener Form, mit durchgerechnetem Zahlenbeispiel, in dem die Schätzer für Rückkehrgeschwindigkeit und Niveau in beiden Verfahren identisch sind und nur σ abweicht (anderer Nenner der Varianzschätzung).

## B-6 · Ökonomische Bedeutung der Rückkehrgeschwindigkeit

**Beleg:** Ahlgrim, K. C., D'Arcy, S. P. & Gorvett, R. W.: *Modeling Financial Scenarios: A Framework for the Actuarial Profession*, Casualty Actuarial Society. **Frei.** SDE als Gl. 2.1; erklärt aus aktuarieller Sicht, dass die erwartete Änderung negativ ist, wenn der Satz über θ liegt, und dass allein κ das Tempo bestimmt. Für die Intuition und den Versicherungskontext, nicht für die Schätzformeln.

**Nicht verifizierbar:** Lesniewski (Baruch MFE, IRC Lecture 10) steht in `LITERATUR_BlockM.md`; der Server war von hier aus nicht abrufbar (robots/SSL). Inhalt **nicht geprüft**, daher nicht als Beleg geführt.

## B-7 · Befund: METHODIK zitiert Brigo falsch (NEU, 20.09.2026)

METHODIK §2, Stage-2-Schätzdesign Punkt 3 schreibt „MLE statt OLS (**beide Wege** in Brigo et al. 2008, Abschn. 7)". Am Volltext geprüft: **falsch** — Brigo §7 gibt nur OLS. Der Beleg ist auszutauschen (B-5), die Entscheidung bleibt. **Nicht eigenmächtig geändert.**

Inhaltlich hängt daran mehr als eine Fußnote: Für ein gaußsches AR(1) ist die *bedingte* ML-Schätzung algebraisch OLS. „MLE statt OLS" ist in dieser Lesart kein Unterschied in der Sache. Ein Unterschied entsteht erst bei der *exakten* ML-Schätzung, die zusätzlich die stationäre Randverteilung der ersten Beobachtung mitnimmt — bei sieben Episoden je Regime sind das sieben Randterme pro Regime. **ERLEDIGT 26.09.2026:** Klaus hat mit der Stufe-2-Abgabe die **bedingte** ML festgelegt und METHODIK §2 Punkt 3 ist entsprechend korrigiert (Beleg getauscht, Lesart eingetragen, h = 1/252 ergänzt). Seine Begründung gegen die exakte ML geht über das Aufwandsargument hinaus und ist in METHODIK übernommen: Die Randterme wären **fehlspezifiziert**, weil der erste Tag einer Episode unmittelbar nach einem Regimewechsel liegt und vom *anderen* Regime erzeugt wurde — er stammt also nicht aus der stationären Verteilung des eigenen Regimes.

**Korrekturvermerk 30.09.2026 (Cowork, Prüfbericht K4):** Die Aussage „Brigo §7 gibt nur OLS“ (hier und in B-4) ist **zu eng**. Am Seitenbild geprüft: Brigo S. 29 „The OLS regression provides the maximum likelihood estimator for the parameters c, b and δ“; Gl. 60 (S. 31) δ̂² = (1/n)Σ[…]² = SSR/n. Brigo trägt damit auch „bedingte ML = OLS für b, c; δ² = SSR/n“; van den Berg bleibt der Beleg für die Herleitung. Außerdem B-4: c und b stehen in **Gl. 50/51**, δ in Gl. 52 (nicht „c, b, δ Gl. 52“). Die Entscheidung ist nicht berührt.

## B-8 · Eigenleistung: Likelihood über nicht zusammenhängende Paare

Keine der drei Quellen behandelt den Fall, dass die Beobachtungen in **fragmentierte Episoden** zerfallen — sie setzen alle eine durchgehende Reihe voraus. Dass die bedingte Likelihood über die verbliebenen 132 bzw. 231 Paare faktorisiert, folgt aus der Markov-Eigenschaft des OU-Prozesses und ist im Paper als **eigene Herleitung auszuweisen**, nicht als Zitat.

---

## Schritt-6-Belege (recherchiert 26.09.2026, VOR jedem Bootstrap-Lauf)

Lesestatus je Quelle ausgewiesen: **VT** = am Volltext gelesen · **VT-Extr.** = Volltext über Textextraktion, Seitenbild nicht geprüft · **Abstract** = nur Abstract · **n. z.** = nicht zugänglich. Nicht zugängliche Quellen werden **nicht** als Beleg geführt.

### B-9 · Bootstrap nahe der Einheitswurzel ist nicht abgesichert

- **Hansen, B. E. (1999):** The Grid Bootstrap and the Autoregressive Model. *Review of Economics and Statistics* 81(4), 594–607. DOI 10.1162/003465399558463. **Frei** (Autorenseite). **VT-Extr.**, zweimal unabhängig abgefragt, konsistent. S. 595: Unter local-to-unity hat das Perzentil-t-Intervall „incorrect first-order asymptotic coverage". Tab. 1 (S. 600; AR(1) mit Konstante **und Trend**, 90 %-Intervalle, Soll je Seite 0,05): Perzentil-t bei n = 120/240, wahres α = 1: PL/PR = 0,02/0,30 bzw. 0,02/0,31; Grid-t durchgehend 0,05/0,05. **Deckt nicht:** BCa (nicht getestet), Modell ohne Trend, fragmentierte Episoden.
- **Basawa, Mallik, McCormick, Reeves & Taylor (1991):** Bootstrapping Unstable First-Order Autoregressive Processes. *Annals of Statistics* 19(2), 1098–1101. DOI 10.1214/aos/1176348142. **Frei**, **VT** (Scan). §2: bei β = 1 hat der Bootstrap-Schätzer eine andere Grenzverteilung → ungültig. **Deckt nicht:** β < 1 nahe 1, Konstante, Intervalle, BCa.
- **Bose, A. (1988):** Edgeworth Correction by Bootstrap in Autoregressions. *Annals of Statistics* 16(4), 1709–1722. DOI 10.1214/aos/1176351063. **Frei**, **VT** (Scan). Thm. 3.9: Residuen-Bootstrap gültig (o(n^−1/2)) für **festes stationäres** AR; Rem. 3.11: Genauigkeit sinkt zum Rand hin. **Deckt nicht:** Nähe zu 1, Intervall-Überdeckung.
- **Einordnung RS-HW (Eigenleistung):** n(b̂ − 1) = 132·(0,98397 − 1) = −2,1 (Krise) bzw. 231·(0,98824 − 1) = −2,7 (ruhig) — local-to-unity-Bereich. Der registrierte Residuen-Bootstrap mit BCa hat dort **keine Gültigkeitsgarantie**. σ ist davon weit weniger betroffen: für b → 1 gilt σ = δ·√(2a/(1−b²)) → δ/√h, σ hängt also fast nur an δ.

### B-10 · Verzerrung der Rückkehrgeschwindigkeit

- **Tang, C. Y. & Chen, S. X. (2009):** Parameter estimation and bias correction for diffusion processes. *Journal of Econometrics* 149, 65–81 (Heftnummer nicht verifiziert). DOI 10.1016/j.jeconom.2008.11.001. **Frei** (Autorenseite). **VT-Extr.**, zweimal abgefragt. Gl. (2.7), S. 67: E(β̂₁) = β₁ − (1+3β₁)/n + O(n⁻²) (dort Marriott & Pope 1954 / Kendall 1954 zugeschrieben). Thm. 3.2.1, S. 69: Vasicek mit **geschätztem** Niveau, führende Verzerrung von κ̂ = 4/T, T = Zeitspanne in Jahren; S. 73: T, nicht n, steuert die Verzerrung. **Deckt nicht:** fragmentierte Stichproben; Entwicklung setzt Stationarität voraus.
- **Vermerk 01.10.2026 (Cowork, Prüfbericht K6):** Thm. 3.2.1 gilt unter Bedingung (2.1), S. 66: n → ∞, δ → 0, **T = nδ → ∞**. Der nächste Term lautet −{4κ/n − 7/(κT²)}, also **+7/(κT²)** (Seitenbild S. 69; `pdftotext` verliert die Klammer und liefert das falsche Vorzeichen). Bei T = 0,52 / 0,92 J ist er an den Schätzwerten 6,3 bzw. 2,8 [1/J] groß, also fast so groß wie 4/T. Die Entwicklung legt die Größe der Verzerrung hier **nicht** fest; 7,6 / 4,4 zeigen nur, dass eine Verzerrung in der Größe der Schätzwerte nicht auszuschließen ist. Paper §5 entsprechend.
- **Phillips, P. C. B. & Yu, J. (2005):** Jackknifing Bond Option Prices. *Review of Financial Studies* 18(2). Gelesen als Cowles Foundation DP 1392 (frei), **VT** (Scan). Gl. (1), S. 6: dieselbe (1+3φ)/T-Formel für AR(1) mit Konstante. DOI noch nicht verifiziert.
- **Marriott & Pope (1954), Kendall (1954), Biometrika: n. z.** — die Formel wird über Tang & Chen Gl. (2.7) zitiert, mit Vermerk.
- **Einordnung (Eigenleistung):** T = 132/252 = 0,52 J bzw. 231/252 = 0,92 J → führende Verzerrung 4/T ≈ 7,6 bzw. 4,4 [1/J] — größer als â selbst (4,07 / 2,98). Übertragung auf 7 Episoden je Regime ist nicht durch die Quelle gedeckt.
- **Andrews, D. W. K. (1993):** Exactly Median-Unbiased Estimation of First Order Autoregressive/Unit Root Models. *Econometrica* 61(1), 139–165. DOI 10.2307/2951781. Gelesen als Cowles DP 975 (frei), **VT** (Scan, Tab. 3 visuell geprüft). Tab. 3 (nur Konstante): bei wahrem α = 1 liegt der LS-Median bei T+1 = 125 bei 0,965, bei T+1 = 200 bei 0,978. Beide b̂ liegen darüber → medianunverzerrte Schätzung wäre in beiden Regimen 1 (Eigenrechnung; gilt für eine **zusammenhängende** gaußsche Reihe, nicht für unsere Episoden).

### B-11 · BCa: Formel, Beschleunigung, B, Grenzen

- **DiCiccio, T. J. & Efron, B. (1996):** Bootstrap Confidence Intervals. *Statistical Science* 11(3), 189–228. DOI 10.1214/ss/1032280214. **Frei**, **VT**. BCa-Endpunkt Gl. (2.3); z0 Gl. (2.8) mit strikt „<"; nichtparametrische Beschleunigung Gl. (6.6), Jackknife-Form Gl. (6.7) U_i = (n−1)(θ̂₍·₎ − θ̂₍ᵢ₎) — **nur für den i.i.d.-Einstichprobenfall**. B: S. 194/201 und Erwiderung S. 226 — BCa braucht etwa 2000 Replikationen.
- **Efron, B. & Narasimhan, B. (2020):** The automatic construction of bootstrap confidence intervals. *JCGS* 29(3), 608–619. DOI 10.1080/10618600.2020.1714633. Gelesen als Autoren-Preprint 2018 (frei), **VT**; Seiten/Gleichungen nach Preprint. Wörtlich: BCa-Endpunkte „can't be trusted when recipe (2.2) calls for extreme percentiles". §3, S. 8: Monte-Carlo-Fehler der Endpunkte ohne neue Ziehungen — B Replikationen in J = 10 Gruppen teilen, gruppenweise weglassen, Jackknife-SE. **Vorzeichen-Achtung:** d_i dort mit umgekehrtem Vorzeichen zu DiCiccio & Efron.
- **Efron (1987) JASA, Efron & Tibshirani (1993), Davison & Hinkley (1997), Carpenter & Bithell (2000): n. z.** Formel wird über DiCiccio & Efron zitiert.
- **Lücke:** Keine zugängliche Quelle legt fest, welche Einheit beim Residuen-Bootstrap eines AR für die Beschleunigung weggelassen wird. Die Wahl ist als **Eigenleistung** auszuweisen.
- **Efron, B. (1994):** Missing data, imputation, and the bootstrap (with comment and rejoinder). *JASA* 89, 463–478 (DOI nicht verifiziert). JASA-Fassung Paywall, **nicht gelesen**; gelesen als **Stanford Tech. Report No. 397 (1992)**, purl.stanford.edu/vn532vb2484, frei, **VT** (Scan, OCR + Seitenbilder). TR S. 9, Gl. 2.13–2.17: â = (1/6) Σṫ³/(Σṫ²)^{3/2} aus Einflusswerten; TR S. 15, **Remark C**, Gl. 3.21–3.23: K Stichproben als ein Vektor, Beschleunigung durch Anwendung von 2.16/2.17 auf S(P*). **Trägt:** die K-Stichproben-Regel. **Trägt nicht:** die ausgeschriebene 1/n_k-Gewichtung (Folgerung, Eigenleistung) und die Jackknife-Näherung für K Stichproben. Seitenzahlen nach TR, nicht nach JASA.
- **DiCiccio & Efron (1996), S. 202, Gl. 6.14/6.15:** K-Stichproben-Intervalle „explained in Remarks C and H of Efron (1994)" — Verweis, keine Formel.
- **Efron & Tibshirani (1993), Gl. 15.36 (von scipy zitiert): n. z.** · **R `boot` 1.3-32** (Quellcode gelesen): Beschleunigung ungewichtet, Zentrierung um θ̂ — **weicht bei ungleichen n_k ab**.

### B-12 · Konfidenzintervalle für Verhältnisse

- **Franz, V. H. (2007):** Ratios: A short guide to confidence limits and proper use. arXiv:0710.2024. **Frei**, **VT-Extr.**, zweimal abgefragt. Fieller-Menge beschränkt nur, wenn der Nenner signifikant ≠ 0 ist; Verhältnis nur bei beschränktem Intervall zu berichten heißt, mit dem **bedingten** Konfidenzniveau zu arbeiten, das beliebig klein werden kann (Gleser–Hwang). Standard-Bootstrap-Intervalle für Verhältnisse können nicht unbeschränkt werden und sind daher im Grenzfall fehlerhaft; in seinen Simulationen einschließlich BCa.
- **von Luxburg, U. & Franz, V. H. (2009):** A geometric approach to confidence sets for ratios: Fieller's theorem, generalizations, and bootstrap. *Statistica Sinica* 19(3), 1095–1117. **Frei** (arXiv:0711.0198). **VT-Extr.** Abschn. 5: Bootstrap direkt auf ρ̂ kann keine unbeschränkten Mengen liefern; Konstruktion aus getrennten Intervallen für Zähler und Nenner.
- **Fieller (1954), JRSS B: n. z.** — über Franz (2007) zitieren.
- **Deckt nicht:** Replikationen mit Vorzeichenwechsel im Nenner, Zeitreihen, nichtlineare Transformation −ln(b)/h.

### B-13 · Mehrere Parameter, eine Aussage

- **Berger, R. L. & Hsu, J. C. (1996):** Bioequivalence trials, intersection–union tests and equivalence confidence sets. *Statistical Science* 11(4), 283–319. DOI 10.1214/ss/1032280304. **Frei**, **VT**. §3, Gl. (9), Thm. 1 (S. 288): Die gemeinsame Aussage „alle Komponenten weichen ab" ist zum Niveau α gültig, wenn jede Einzelprüfung zum Niveau α erfolgt — „no need for multiplicity adjustment". Erwiderung S. 316: IUT erlaubt keine Aussage über einzelne Komponenten, wenn nicht alle verworfen werden. **Deckt nicht:** die Gegenrichtung „mindestens einer weicht ab" (Korrekturbedarf) — dafür **keine** Quelle verifiziert; Bootstrap; Verhältnisparameter.
- **Berger (1982), Technometrics: n. z.**

---

## B-14 · Paper-Quellen, Volltextprüfung 30.09.2026 (vor dem Schreiben)

Lesestatus: VT = Volltext gelesen (bei Scans per OCR), VT-Extr. = Volltext über Textextraktion. Zitiert wird die **gelesene Fassung**; nicht gesehene Journal-Angaben stehen nicht im Literaturverzeichnis.

| Quelle | gelesen | Trägt im Paper | Einschränkung |
|---|---|---|---|
| Hamilton (1989), Econometrica 57(2) | VT, Scan/OCR | Markov-Kette 1. Ordnung (Gl. 2.2, S. 360); NBER-Vergleich (S. 359, 374) | — |
| Rabiner (1989), Proc. IEEE 77(2) | VT | γ_t Gl. 26–27 (S. 263); Viterbi (S. 264); **einzeln wahrscheinlichste Zustände evtl. keine gültige Folge (S. 264)**; Baum–Welch = EM, lokale Maxima (§III-C) | ersetzt Bishop als Beleg für B2 |
| Hull & White (1990), RFS 3(4) | VT | erweitertes Vasicek Gl. 3 (zeitabh. a(t), σ(t)); Drift aus Anfangskurve Gl. 16, enthält Marktpreis des Risikos | Form dr = [θ(t) − ar]dt + σdz steht **so nicht** im Paper; konstante a, σ = Spezialfall |
| Ang & Bekaert, **NBER WP 6508 (1998)** | VT, Scan/OCR | RS-Modelle erfassen Nichtlinearitäten; univariate Modelle inkonsistent, **wenn** ausgelassene Variablen Regimeinfo tragen | Datei ist WP, nicht JBES 2002 → als WP zitiert |
| Bansal & Zhou, WP Aug. 2001 | VT, OCR | RS in Short Rate + Marktpreis des Risikos | Datei ist WP; Korrelation mit NBER nur 0,15 |
| Dai, Singleton & Yang, Entwurf Apr. 2006 | VT | DTSM mit bepreistem Regimerisiko; L/H-Volatilität | Datei ist Entwurf, nicht RFS 2007 |
| Bie, Diebold, He & Li, arXiv:2408.12863v2 | VT | latente Regime ohne klare ökonomische Interpretation, „ex post rationalization" (S. 1) | stützt **nicht** die Exposé-Aussage zu „spurious high-variance state / heavy tails" |
| Nystrup, Kolm & Lindström (2021), ESWA 184 | VT (Verlagsfassung) | Jump Models als Alternative (S. 2); fehlspezifiziertes HMM → instabile Zustände, unnötige Zustände (§3.1, S. 3); Student-t-HMM bei Filion et al. (S. 11, Sekundär) | Dateiname sagt 2024 — falsch, Paper ist 2021 |
| Diebold & Li, NBER WP 10048 (2003) | VT | Faktoren als Level/Slope/Curvature interpretierbar | Nelson–Siegel-, nicht PCA-Faktoren |
| Litterman & Scheinkman (1991), J. Fixed Income, Juni 1991, S. 54–61 | **VT 30.09.** (Scan, OCR; `01_Paper-Quellen/Litterman & Scheinkman (1991).pdf`) | drei statistisch extrahierte Faktoren „level, steepness, and curvature“ (S. 54); Formen S. 57–58; Identifikation durch sukzessive Varianzmaximierung (Endnote 3, S. 61) | Überschussrenditen von US-Nullkupon-Treasuries, wöchentlich 1/1984–6/1988 (Endnote 2); Faktormodell, nicht „principal components“; „steepness“ statt „slope“; Band/Heft/DOI nicht im PDF → nicht im bib |
| Mrkvička et al. (2020), arXiv:1911.00240 v1 | VT-Extr. | Random Shift nach Lotwick & Silverman (1982); zerstört Abhängigkeit zwischen, erhält sie innerhalb der Komponenten (§1); liberal (§1, §2.1) | L&S 1982 nur sekundär zitiert |
| Phipson & Smyth (2010), arXiv:1603.05766 | VT-Extr. | **§5: erschöpfende Aufzählung p_t = (b_t+1)/(m_t+1)** — entspricht exakt unserer Formel mit m_t = 376 | Korrektur zu B-1: die Quelle deckt unseren Fall doch direkt |
| Schwarz (1978), Ann. Statist. 6(2) | **VT 30.09.** (JSTOR-Scan, OCR; `01_Paper-Quellen/Schwarz (1978).pdf`) | S. 461: „Choose the model for which log M_j(X_1,…,X_n) − ½ k_j log n is largest" ⇔ −2 ln L + k ln n minimal | hergeleitet für i.i.d.-Beobachtungen aus Exponentialfamilien (S. 462) — HMM/AR(1) sind nicht i.i.d.; Anwendung dort ist Konvention |
| Bishop (2006), PRML §13.2.5 | VT über GitHub-Spiegel, S. 629 | wie Rabiner S. 264 | nicht im Paper zitiert; **liegt entgegen „Offen"-Abschnitt oben nicht als PDF im Ordner** |
| ECB Yield Curves (Technical Notes: NSS S. 4, MTS S. 1, Fitch S. 2) + Datenportal + „Policy regarding the reuse of ESCB statistics“ (Name korrigiert 30.09.) | VT (Webseiten) | AAA, Nelson–Siegel–Svensson; Serienschlüssel existiert; Weiterverwendung mit „Source: ECB statistics", unverändert | Drittdaten-Vorbehalt (MTS, Fitch) |
| hmmlearn 0.3.3 Doku + Quellcode | VT | predict → Viterbi (Standard); predict_proba = Forward-Backward; bic = −2 logL + k log n | — |

**Fehler in `Materialien/00_Exposé/Quellen_Zusammenfassungen.md` (nur Seitenangaben/Versionen, Zitate selbst korrekt):** Ang & Bekaert „Abstract, S. 1" (Abstract unpaginiert, WP-Version); Bansal & Zhou S. 2 → S. 1; Dai et al. S. 3 → S. 1; Bie et al. S. 2 → S. 1; Nystrup S. 13 → S. 12. Exposé-Satz „states key on the volatility … (Rabiner, 1989)" — steht nicht bei Rabiner, ist eigene Designentscheidung.
