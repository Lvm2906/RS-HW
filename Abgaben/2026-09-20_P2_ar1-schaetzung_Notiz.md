# 2026-09-20 · P2 · AR(1)-Schätzung je Regime — Notiz

Skript: `2026-09-20_P2_ar1-schaetzung.py` · Ausgabe: `ar1_schaetzung.csv`

## Festlegungen

- **h = 1/252.** Die Werte sind annualisiert: *a* in 1/Jahr, *σ* in Prozentpunkten pro √Jahr. Es gilt die Handelstagsuhr, Wochenenden zählen also nicht als Zeit.
- **ML-Lesart: bedingte ML**, bedingt auf den ersten Wert jedes Paares. Damit sind *b* und *c* identisch mit OLS, und δ² = SSR/n (ML-Nenner n statt n−2). Die exakte ML ist verworfen: Ihre Randterme unterstellen, dass jeder Episodenstart aus der stationären Verteilung *des Regimes* gezogen ist. Direkt nach einem Wechsel stammt der Startwert aber aus dem anderen Regime. Das präzisiert die registrierte Entscheidung „Maximum Likelihood“ und wählt nicht neu.
- **Zitierfehler METHODIK §2 Pkt. 3** (noch offen, meine Korrektur): Dort steht „beide Wege in Brigo et al. 2008, Abschn. 7“. Richtig ist: Brigo Abschn. 7 gibt nur OLS (Gl. 58–60). Die ML-Formeln stehen bei van den Berg (2011).

## Kontrollsummen

378 Zeilen yields.csv → 377 Tage auf dem Änderungsindex (Datumsgleichheit assertiert) · 376 Paare · 13 Nahtstellen verworfen · **132 Krise / 231 ruhig** ✓ · Krisenzustand = 1 (Spur 0,568 vs. 0,133)

## Punktschätzung (bedingte ML, h = 1/252)

| Regime | b | c | δ | **a** [1/J] | **σ** [pp/√J] | θ (nachr.) | n Paare |
|---|---|---|---|---|---|---|---|
| Krise | 0,9840 | 0,0326 | 0,0374 | **4,07** | **0,598** | 2,035 | 132 |
| ruhig | 0,9882 | 0,0235 | 0,0141 | **2,98** | **0,225** | 1,995 | 231 |

0 < b < 1 gilt in beiden Regimen, also ist in beiden eine Rückkehr messbar. θ ist nur nachrichtlich angegeben; es ist ein Störparameter und kein HW-θ(t).

**Keine Aussage über Signifikanz/Materialität.** Das entscheidet erst das Verhältnis-CI in Schritt 6. Anmerkung dazu: *b* liegt in beiden Regimen nahe 1, und *a* = −ln(b)/h reagiert dort sehr empfindlich auf kleine Änderungen von *b*. Außerdem ist *a* bei kurzen Stichproben bekanntlich nach oben verzerrt. Für *a* sind also breite Intervalle zu erwarten.

## Residuendiagnostik (p-Werte)

| Regime | Ljung-Box(5) | Ljung-Box(10) | Breusch-Pagan (auf Niveau) | ARCH-LM(1) | Jarque-Bera |
|---|---|---|---|---|---|
| Krise | 0,104 | 0,089 | 0,853 | 0,096 | < 0,001 |
| ruhig | 0,459 | 0,720 | 0,090 | 0,275 | 0,42 |

Ljung-Box und ARCH-LM zählen nur Lags *innerhalb* eines Segments. Ein Lag über eine Nahtstelle würde Tage verbinden, die real Wochen auseinanderliegen.

- **Restautokorrelation:** bei 5 % in keinem Regime nachweisbar. Die Kriseneffekte liegen knapp darüber (p ≈ 0,09–0,10).
- **Heteroskedastizität:** bei 5 % weder niveauabhängig (BP) noch als Clustering (ARCH) nachweisbar. Grenzfälle sind BP im ruhigen Regime (0,090) und ARCH in der Krise (0,096).
- **→ Schritt 6: normaler Residuen-Bootstrap**, keine Umstellung auf Wild Bootstrap. Dieser Schluss folgt der Regel in METHODIK §2 Pkt. 4 bei α = 5 %.
- **Nebenbefund:** Die Krisenresiduen sind klar nicht normal (JB p < 0,001, fette Ränder). Das löst nach METHODIK keinen Wechsel aus. Der Residuen-Bootstrap zieht ohnehin aus der empirischen Verteilung und setzt keine Normalität voraus. Die ML-Schätzer sind unter Nicht-Normalität als Quasi-ML zu lesen.

## Begriffspunkte

- **Estimation vs. calibration:** Hier schätze ich *a* und *σ* aus der beobachteten Geschichte des 3M-Satzes, also unter dem physischen Maß P. Das ist Estimation: Ich frage, wie sich der Zins tatsächlich bewegt hat. Calibration heißt beim Hull-White-Modell etwas anderes. Dort wird die Drift θ(t) unter dem Risikoneutralmaß Q so gewählt, dass das Modell die heutige Zinskurve exakt reproduziert, bzw. (a, σ) werden an Marktpreise von Caps oder Swaptions angepasst. Beides tue ich nicht, und ich habe auch keine solchen Preise. Deshalb schreibe ich im Paper „estimation“, und der Achsenabschnitt *c* je Regime ist nur ein Störparameter, kein θ(t).
- **Exakte Diskretisierung vs. Euler:** Beim OU-Prozess weiß man genau, wie der Wert morgen verteilt ist, wenn man den Wert heute kennt: normal, mit Mittelwert c + b·x und Streuung δ. Die AR(1)-Gleichung ist deshalb keine Annäherung an die SDE, sondern ihre exakte Form auf dem Tagesraster, für jede Schrittweite h. Euler ersetzt dagegen die Exponentialfunktion e^{−ah} durch die Gerade 1 − ah. Das ist nur für sehr kleine Schritte gut und verzerrt die Schätzung von *a* systematisch. Diesen Fehler muss man nicht in Kauf nehmen, weil es die exakte Form gibt.

## Reflexion

Die Diskretisierung ist exakt, weil der OU-Prozess eine geschlossene, normalverteilte Übergangsdichte hat: Die Steigung b = e^{−ah} ist die wahre Steigung des AR(1) und keine abgeschnittene Taylor-Reihe. Eine Euler-Diskretisierung würde b ≈ 1 − ah unterstellen. Rechnet man daraus a = (1 − b)/h zurück, kommt wegen 1 − b < −ln b systematisch ein zu kleines *a* heraus. Bei meinem h = 1/252 und a ≈ 3–4 ist dieser Fehler klein, aber er ist ein Fehler, den der exakte Weg gar nicht erst macht. Der konstante Achsenabschnitt je Regime ist ein unter P aus der Zeitreihe geschätztes Niveau, während θ(t) im Hull-White-Modell eine deterministische Funktion unter Q ist, die allein dazu dient, die heutige Anfangskurve exakt zu treffen. Von Hull-White darf das Paper trotzdem sprechen, weil *a* und *σ* in Vasicek und Hull-White dieselbe Rolle in derselben SDE spielen: θ(t) wird für das Pricing nachträglich und getrennt an die Kurve angepasst, und die dynamischen Parameter (a, σ), die ich je Regime schätze, sind genau die Eingaben, die das Hull-White-Modell darüber hinaus braucht. Behielte ich die 13 Nahtstellen-Paare, flössen künstlich große „Tagessprünge“ zwischen Tagen, die real Wochen auseinanderliegen, in die Residuen und würden δ und damit σ nach oben verzerren.
