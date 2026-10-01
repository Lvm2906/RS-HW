# Audit `key_events.csv` — Zeilen nach dem 31.05.2026

**Stand:** 2026-07-27 · **Prüfer:** Cowork · **Geprüfte Datei:** `Code/key_events.csv` (28 Zeilen, 30.01.2025–28.06.2026)
**Maßstab:** `Code/METHODIK.md` §7 (Auswahlregel K1–K4 + Same-Day-Konvention)
**Anlass:** Der dokumentierte Audit („17 Events, 0 ungedeckt, K1=9 / K2=4 / K3=3 / K4=1") ist auf den **31.05.2026** datiert. Genau **17 Zeilen** liegen auf oder vor diesem Datum — die **11 Zeilen danach sind nie gegen die Auswahlregel geprüft worden.** Sie sind zugleich die Ereignisdichte, auf der der Permutationstest (Haupttest für Forschungsfrage a) stehen soll.

> **Hinweis zur Rollenverteilung:** Dieses Dokument stellt Befunde fest und benennt Entscheidungsoptionen. Die Entscheidungen selbst trifft Klaus — und zwar **vor** dem Blick auf das Testergebnis, sonst ist die Vorab-Registrierung wertlos (METHODIK §4).

---

## 1. Ergebnis in einem Absatz

Von den 11 neuen Zeilen sind **9 durch K1–K4 gedeckt**, **2 nicht** (beide `tech_selloff`). Dazu kommen **2 klare Verstöße gegen die Same-Day-Konvention** (Marktdaten des Folgetags in der Beschreibung), **1 Verdachtsfall**, ein **Ereignis-Cluster** von fünf Hormus-Zeilen in 15 Tagen, **eine Zeile außerhalb des HMM-Samples**, eine **Namens-Inkonsistenz** und ein spürbarer **Abfall der Quellenqualität** (8 von 11 Zeilen stützen sich allein auf das eigene Markt-Briefing statt auf eine Primärquelle). Keiner dieser Punkte gefährdet Stage 1 — alle betreffen den Permutationstest in Block P.

---

## 2. Zeile für Zeile (Nr. 18–28)

| Nr. | Datum | Tag | Label | Kriterium | Same-Day | Befund |
|---|---|---|---|---|---|---|
| 18 | 05.06.2026 | Fr | `tech_selloff` | **keins** | ok | Kategorie nicht gedeckt |
| 19 | 07.06.2026 | So | `hormus_eskalation` | K2 ✓ | ok | kein Handelstag |
| 20 | 10.06.2026 | Mi | `cpi_surprise` | K3 ✓ | ok | sauber (BLS-Primärquelle) |
| 21 | 11.06.2026 | Do | `ecb_hike` | K1 ✓ | ok | **vorbildlich** |
| 22 | 14.06.2026 | So | `hormus_deeskalation` | K2 ✓ | **Verstoß** | Folgetags-Marktdaten; kein Handelstag |
| 23 | 17.06.2026 | Mi | `fed_hold` | K1 ✓ | ok | **vorbildlich** (Hold mit Guidance-Änderung) |
| 24 | 20.06.2026 | Sa | `hormus_eskalation` | K2 ✓ | **fraglich** | Ölpreis-Move an einem Samstag; kein Handelstag |
| 25 | 22.06.2026 | Mo | `hormus_deeskalation` | K2 ✓ | ok | Teil des Clusters (§3.3) |
| 26 | 24.06.2026 | Mi | `tech_selloff` | **keins** | ok | Kategorie nicht gedeckt **+ zirkulär** |
| 27 | 25.06.2026 | Do | `cpi_surprise` | K3 ✓ | ok | Primärquelle (BEA) fehlt |
| 28 | 28.06.2026 | So | `hormus_eskalation` | K2 ✓ | **Verstoß** | Folgetags-Futures; kein Handelstag; **nach Sample-Ende** |

**Neue Verteilung nach Kriterium:** K1 = 2 · K2 = 5 · K3 = 2 · ungedeckt = 2.

---

## 3. Die Befunde im Einzelnen

### 3.1 Zwei Zeilen sind von keinem der vier Kriterien gedeckt

**Zeile 18 (05.06., `tech_selloff`)** und **Zeile 26 (24.06., `tech_selloff`)** beschreiben Aktienmarkt-Bewegungen ohne geldpolitischen, geopolitischen oder makro-/fiskalpolitischen Auslöser: ein Guidance-Schock eines einzelnen Unternehmens (AVGO) bzw. „BofA-Zinsnotiz + Asien-Kursrutsch, AI-Trade kühlt ab". Die Auswahlregel kennt vier Kategorien — **Unternehmens- oder Sektorschock ist keine davon.**

Zeile 18 hat einen Rettungsanker: Die Beschreibung nennt zusätzlich die US-Arbeitsmarktzahlen (+172k), und eine Makro-Überraschung, die das Briefing dominierte, wäre **K3**. Dann müsste die Zeile aber auf diesen Auslöser umgehängt werden (Label und Beschreibung führen mit dem Payroll-Wert, nicht mit AVGO).

Zeile 26 hat diesen Anker nicht — und ist der heiklere Fall: Das „Ereignis" ist hier **die Marktbewegung selbst**. Ein Validierungs-Event, das aus einer Marktbewegung definiert wird, gegen einen Regimepfad zu testen, der aus Marktdaten geschätzt wurde, ist **zirkulär**. METHODIK §7 warnt bereits in milder Form davor (Rekord-Yield-Tage); hier wäre es die harte Form.

**Optionen:** (a) fünftes Kriterium deklarieren und *begründen*, warum es dieselbe Qualität hat wie K1–K4 — dann aber konsequent das ganze Sample nach solchen Tagen durchsuchen, nicht nur die letzten Wochen; (b) Zeile 18 auf die Payroll-Überraschung umankern (K3), Zeile 26 streichen; (c) beide streichen. — **Empfehlung: (b).** Sie hält die Regel intakt, rettet den inhaltlich tragfähigen Teil und entfernt die Zirkularität.

### 3.2 Zwei Same-Day-Verstöße, ein Verdachtsfall

Die Same-Day-Konvention erlaubt nur, was **am Abend des Ereignistages** bekannt war.

- **Zeile 22 (14.06.):** „… Friedensrally am **Montag 15.06** (Dow-Rekord 51.671, Nasdaq +3,07%)". Das sind Marktdaten des **Folgetags** in der Beschreibung eines Sonntagsereignisses — genau die verbotene Kategorie („nach dem Tag wissbare" Information). Zusätzlich ist „Dow-Rekord" eine superlative Rangierung.
- **Zeile 28 (28.06.):** „… Märkte bleiben dennoch stabil (**Futures Mo +1%**)". Derselbe Fehler: Futures-Stand des Folgetags.
- **Zeile 24 (20.06., Samstag):** „Ölpreis +15%, Brent ~92 USD". An einem Samstag handelt kein Ölmarkt. Entweder stammt der Move vom Freitag (dann gehört er nicht in die Zeile eines Samstagsereignisses) oder vom Montag (dann ist es derselbe Verstoß wie oben). **Zu klären.**

**Zum Vergleich:** Die Bereinigung vom 31.05.2026 hat genau diese Sorte Formulierung in **11 von 18 Zeilen** entfernt. Der Fehlertyp ist also bekannt und dokumentiert — er ist nur beim Fortschreiben wieder eingeschlichen.

**Option:** Beschreibungen auf das Ereignis + die am selben Tag beobachtbare Reaktion kürzen (bei Wochenendereignissen: Ölpreis/Futures am Freitagsschluss oder gar keine Marktzahl). Der Ereignis-Eintrag selbst bleibt bestehen — es geht nur um die Beschreibung.

### 3.3 Fünf Hormus-Zeilen in 15 Tagen — ein Cluster, kein Ereignisstrom

14.06. Deeskalation → 20.06. Eskalation → 22.06. Deeskalation → 28.06. Eskalation, dazu 07.06. Eskalation. Alle fünf gehören zu **einem** laufenden Vorgang (US-Iran-Konflikt und Friedens-Roadmap).

Das ist deshalb heikel, weil es der Entscheidung vom 31.05.2026 widerspricht: Dort wurden zwei Deeskalations-Zeilen (25.05./31.05.) zu **einer** Zeile am Wirkdatum zusammengelegt, mit der Begründung „derselbe Deeskalations-Vorgang". Nach diesem Maßstab wären die Juni-Zeilen zu konsolidieren; nach dem Wortlaut von K2 („geopolitischer Schock mit eigenständiger Marktnarrative") sind Blockade-Schließung und Abkommen jeweils eigenständig. **Beide Lesarten sind vertretbar — aber es muss dieselbe für alle Zeilen gelten.**

Für den Permutationstest ist das kein Kosmetikproblem: Ein Cluster stark korrelierter Ereignisdaten verletzt die Austauschbarkeits-Annahme, auf der die Permutations-Nullverteilung beruht, und gewichtet zwei Juni-Wochen so stark wie das gesamte Jahr 2025.

### 3.4 Zeitliche Lage: 18 von 28 Events liegen im Dauer-Krisenblock

Nach METHODIK §3 ist die Krise „ab April 2026 nahezu durchgängig". Genau dort liegen **18 der 28 Events** (64 %), davon 11 allein im Juni. Wenn der Regimepfad in dieser Phase fast konstant ist, gibt es dort kaum Regimewechsel, an denen sich die Nähe „Ereignis ↔ Wechsel" überhaupt messen ließe.

Das ist **kein Datenfehler**, sondern eine **Power-Aussage**, die ins Permutationsdesign gehört: Der Test wird seine Trennschärfe fast vollständig aus den 10 Events vor April 2026 ziehen. Das vorab registrierte Abbruchkriterium (METHODIK §2, Fallback) ist damit realistischerweise erreichbar — und genau dafür wurde es formuliert.

### 3.5 Sechs Events liegen auf Nicht-Handelstagen, eines nach Sample-Ende

`hmm_input_changes.csv` enthält 377 **Handelstage** vom 03.01.2025 bis **26.06.2026**. Sechs Events lassen sich diesem Index nicht direkt zuordnen: 28.02.2026 (Sa), 31.05. (So), 07.06. (So), 14.06. (So), 20.06. (Sa) und 28.06. (So) — Letzteres liegt zusätzlich **nach dem Sample-Ende**.

Die Zuordnungsregel ist ein **Freiheitsgrad, den ein Gutachter angreift**, wenn sie nicht vorab feststeht: auf den nächsten Handelstag schieben? Auf den vorherigen? Ganz ausschließen? Bei einem Nähe-Maß mit ±k-Tage-Fenster kann das über Signifikanz entscheiden. Zeile 28 (28.06.) hat gar keine Zuordnung, solange das Sample am 26.06. endet — entweder Zeile raus oder Sample bis Ende Juni verlängern (dann aber Refit und alle Kennzahlen neu).

### 3.6 Quellenqualität und Benennung

- **Primärquellen:** Von den 11 neuen Zeilen haben nur 3 eine (BLS, ECB, FOMC). Acht stützen sich allein auf das **eigene Markt-Briefing**. Die ersten 17 Zeilen zitieren durchgehend ECB/FOMC/Reuters/CNBC/Washington Post/S&P Global. METHODIK §6 beschreibt `key_events.csv` als „manuell kuratiert **mit Primärquellen**" — der Standard ist beim Fortschreiben gesunken. Für ein Paper mit öffentlichem Repo ist die Primärquelle das, was die Ground Truth überhaupt zur Ground Truth macht.
- **Namens-Inkonsistenz:** Zeile 11 heißt `hormus_escalation` (englisch), die Zeilen 19/24/28 `hormus_eskalation` (deutsch). Jede Gruppierung oder Auswertung nach Ereignistyp zerfällt daran lautlos.

---

## 4. Was zu entscheiden ist (vor dem Permutationsdesign)

1. **Kategorie `tech_selloff`:** K5 deklarieren, umankern oder streichen (§3.1). — *Empfehlung: Zeile 18 auf K3 umankern, Zeile 26 streichen.*
2. **Same-Day-Bereinigung** der Zeilen 22 und 28, Klärung von Zeile 24 (§3.2).
3. **Cluster-Regel** für den Hormus-Strang: konsolidieren wie am 31.05. oder alle behalten — einheitlich für das ganze Sample (§3.3).
4. **Zuordnungsregel für Nicht-Handelstage** vorab schriftlich festlegen (§3.5).
5. **Sample-Grenze:** Zeile 28 streichen oder Sample bis 30.06. verlängern (§3.5). *Empfehlung: streichen — ein Refit in der Handover-Woche ist es nicht wert.*
6. **Primärquellen nachtragen** für die acht briefing-only-Zeilen (§3.6).
7. **Label-Schreibweise vereinheitlichen** (§3.6).
8. **Audit-Zähler in METHODIK §7 aktualisieren** — mit neuem Datum, neuer Gesamtzahl und der Kriterienverteilung, damit dieser Fall nicht ein drittes Mal auftritt.

Bei Umsetzung der Empfehlungen (18 umgehängt, 26 und 28 gestrichen) stünde `key_events.csv` bei **26 Zeilen**, davon 24 im Handelstags-Index.

---

## 5. Was dieser Audit **nicht** geprüft hat

- Die **inhaltliche Richtigkeit** der Ereignisse und Zahlen (Vote-Splits, Indexstände, Brent-Niveaus) — das wäre eine Quellenverifikation, keine Regelprüfung.
- Die ersten 17 Zeilen — sie gelten laut METHODIK §7 als am 31.05.2026 geprüft.
- **Vollständigkeit:** Ob zwischen dem 01.06. und dem 26.06.2026 ein Ereignis *fehlt*, das K1–K4 erfüllt, lässt sich nur durch erneutes Durchgehen aller Briefings dieses Zeitraums feststellen. Angesichts der Ereignisdichte im Juni ist das ein realer Restposten.
