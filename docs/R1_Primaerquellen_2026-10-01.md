# Prüfbericht R1: Primärquellen für sechs Ereignisse in `key_events.csv`

**Datum:** 01.10.2026 · **Geprüft:** `Code/key_events.csv` (Zeilen 17, 18, 20, 23, 25, 26 = E1–E6, voller Wortlaut), `Morning Briefing/Markt-Briefing-2026-05-29 … 06-23.pdf` (nur als Spur), Methodik-Regeln aus `Code/METHODIK.md` §7.

**Nichts geändert.** Keine Änderung an `key_events.csv`, `Paper/`, `Abgaben/`, `COCKPIT_BRIEFING.md` oder `FORTSCHRITT.json`. Einzige neue Datei ist dieser Bericht.

**Zeitzonen:** EDT = UTC−4, MESZ = UTC+2, Golfstaaten = UTC+3. Mit „Handelstag“ ist der Handelstags-Index in `hmm_input_changes.csv` gemeint. 28.05., 29.05., 01.06., 05.06., 08.06., 15.06. und 22.06. liegen alle im Index (per Skript geprüft).

**Vorbehalt zu den Zitaten:** Ich habe die Seiten mit einem Abruf-Werkzeug gelesen, das den Text maschinell extrahiert. Nach deiner Regel „nur am Volltext verifizierte Primärzitate“ gilt deshalb: Jedes Zitat unten vor der Übernahme ins Paper einmal am Original im Browser gegenlesen. Die Fakten (Datum, Zahl, Akteur) sind davon nicht betroffen.

**Rang der Quellen:**

- Rang 1: amtliche Stelle
- Rang 2: Agentur. Bei „AP (via PBS)“ und „Reuters (via …)“ ist der Agenturtext auf einer Partnerseite gedruckt.
- Rang 3: große Zeitung
- „o. R.“: Medium außerhalb der Rangliste (Al Jazeera, The National, Axios, JPost, PTI). Es stützt nur ergänzend.

---

## 1 Gesamturteil

Alle sechs Ereignisse haben stattgefunden. Für jedes gibt es mindestens eine Quelle von Rang 1 oder 2.

- **Voll bestätigt: 1 (E5).**
- **Teilweise bestätigt: 4 (E1, E2, E4, E6).** Der Kern ist belegt, aber je ein Bestandteil ist unbelegt oder ungenau.
- **Widerspricht beim Datum: 1 (E3).**
- **Nicht gefunden: 0.**

Drei Befunde brauchen deine Entscheidung:

- **E3:** Der Raketenangriff war nicht am Wochenende. CENTCOM datiert ihn auf **Freitag, 05.06.**, in der Nacht. Die CSV hat 07.06.
- **E2:** Der vorläufige Deal wurde schon am **Do 28.05.** öffentlich. Am 29./30.05. verlangte Trump Änderungen. Die Beschreibung „wartet auf Trumps Zustimmung“ war am 31.05. also schon überholt.
- **E6:** Die „zollfreie Wiederöffnung“ steht nicht im Fahrplan vom 22.06. Sie stammt aus dem Abkommen vom 14.06. „Brent ~77,5 USD“ ist für den 22.06. nicht belegt: Reuters meldet rund 79–80 USD.

---

## 2 Tabelle

| Nr | Urteil | Quelle (Rang, Titel, URL, Datum/Uhrzeit) | Zitat ≤ 15 Wörter | Abweichung Datum | Abweichung Beschreibung / Same-Day | Vorschlag `source` |
|---|---|---|---|---|---|---|
| **E1** 28.05. `cpi_surprise` | teilweise | **Rang 1:** BEA, „Personal Income and Outlays, April 2026“ (BEA 26-25). https://www.bea.gov/news/2026/personal-income-and-outlays-april-2026 · PDF https://www.bea.gov/sites/default/files/2026-05/pi0426.pdf. Erschienen **Do 28.05.2026, 08:30 EDT** (14:30 MESZ). | „the PCE price index for April increased 3.8 percent“ | keine | 3,8 % J/J ✓ und Kern 3,3 % J/J ✓ (BEA, gleicher Absatz). **„Marktreaktion verhalten“ ist nicht belegt:** Ich habe keine Agentur- oder Zeitungsquelle öffnen können. Die einzige Spur ist TheStreet (nicht zulässig), Überschrift „Nasdaq, S&P 500 set new record despite highest PCE reading“. Das spricht eher gegen „verhalten“. Same-Day: ok. | `BEA Personal Income and Outlays (April) 28.05.2026 / Markt-Briefing 29.05.2026` |
| **E2** 31.05. `hormus_deeskalation` | teilweise | **Rang 2:** AP (via PBS), „U.S. and Iranian negotiators reach tentative deal to extend ceasefire and start new nuclear talks“. https://www.pbs.org/newshour/world/u-s-and-iranian-negotiators-reach-tentative-deal-to-extend-ceasefire-and-start-new-nuclear-talks. PBS-Stand 29.05.2026, 09:40 EDT; Ereignis „Thursday“ = 28.05. · **o. R.:** Axios, „Scoop: U.S. and Iran reach deal but need Trump's final approval“, 28.05.2026, 14:12 ET. https://www.axios.com/2026/05/28/iran-peace-deal-trump-approval · **Rang 2:** AP (via PBS), „Trump says not to rush as U.S. nears potential Iran deal“, 24.05.2026, 15:18 EDT. https://www.pbs.org/newshour/world/trump-says-not-to-rush-as-u-s-nears-potential-iran-deal · **o. R.:** Axios, „Trump requests edits to Iran deal his envoys negotiated“, 30.05.2026. https://www.axios.com/2026/05/31/trump-iran-deal-changes-nuclear · **o. R.:** Al Jazeera, 28.05.2026, 18:21 (Tasnim-Dementi). https://www.aljazeera.com/news/2026/5/28/us-and-iran-reach-tentative-deal-for-60-day-truce-extension-officials-say | AP: „reached a tentative agreement Thursday to extend the ceasefire … by 60 days“ | Das Ereignis wurde am **28.05.** öffentlich (Axios 14:12 ET = 20:12 MESZ, nach Börsenschluss in Europa). 31.05. ist das registrierte Wirkdatum aus der Zusammenlegung vom 31.05. (METHODIK §7). Am 31.05. selbst ist kein neuer Schritt belegt. → Befund B2 | ✓ 60 Tage, Hormus (Axios: Durchfahrt „unrestricted“), wartet auf Trump (Stand 28.05.). ✓ Signal um den 25.05.: AP vom 24.05. meldet, die USA stünden kurz vor einer Einigung. ✓ Iran-Dementi 28.05. (Tasnim laut Al Jazeera). **Gefechte:** AP verortet sie am **28.05.** (Kuwait fängt Raketen und Drohnen ab), Al Jazeera am 28./29.05. Die Angabe „29.05.“ trifft also nur teilweise zu. **Überholt am 31.05.:** Trump verlangte am 29.05. im Situation Room Änderungen (Axios 30.05.). **Brent ~93–97 / WTI ~91** und „entschärft akute Inflationssorgen“: nicht an einer zulässigen Quelle belegt. Same-Day: keine späteren Fakten. | `AP 28.05.2026 / Axios 28.+30.05.2026 / Markt-Briefing 30.+31.05.2026` |
| **E3** 07.06. `hormus_eskalation` | **widerspricht (Datum)** | **Rang 1:** US CENTCOM Public Release, „CENTCOM Forces Defeat Missiles, Drones Launched by Iran“, datiert **05.06.2026**, Tampa. https://www.centcom.mil/MEDIA/PUBLIC-RELEASES/Article/4510668/centcom-forces-defeat-missiles-drones-launched-by-iran/ · Spiegel bei DVIDS mit dem Zeitstempel „06.05.2026 22:20“, also 5. Juni (Zeitzone auf der Seite nicht angegeben). https://www.dvidshub.net/news/567021/centcom-forces-defeat-missiles-drones-launched-iran · **o. R.:** Al Jazeera, 06.06.2026, 07:51 UTC. https://www.aljazeera.com/news/2026/6/6/us-intercepts-iranian-attacks-as-israel-continues-to-bomb-lebanon · **o. R.:** Middle East Eye Liveblog, 06.06.2026, 04:27 BST · **o. R.:** The National, 06.06.2026. https://www.thenationalnews.com/news/gulf/2026/06/06/iran-attacks-kuwait-and-bahrain-with-seven-ballistic-missiles/ | Al Jazeera: „seven ballistic missiles were fired towards Kuwait and Bahrain late on Friday night“ | **CSV 07.06. (So) gegenüber Quellen: Freitag 05.06. spätabends.** Öffentlich wurde es in der Nacht zum Sa 06.06. (MEE 04:27 BST = 03:27 UTC). Das Briefing vom 07.06. schreibt „am Samstag“. Das ist falsch. → Befund B1 | ✓ Iran feuert 7 ballistische Raketen Richtung Kuwait und Bahrain (6 abgefangen, 1 verfehlt das Ziel; CENTCOM). ✓ Hormus „largely closed off“ (Al Jazeera) bzw. „effectively blocked“ (The National). **✗ „Wochenend-Eskalation“:** Der Angriff war Freitagnacht. Same-Day: ok. | `US CENTCOM Press Release 05.06.2026 / Markt-Briefing 07.06.2026` |
| **E4** 14.06. `hormus_deeskalation` | teilweise | **Rang 2:** AP (via PBS), „Deal is reached to end Iran war and Trump orders stop to U.S. naval blockade“, Dateline Islamabad, **14.06.2026, 18:10 EDT** (= 15.06., 00:10 MESZ). https://www.pbs.org/newshour/world/deal-is-reached-to-end-iran-war-and-trump-orders-stop-to-us-naval-blockade · **o. R.:** Al Jazeera, 14.06.2026, 22:43 UTC. https://www.aljazeera.com/news/2026/6/14/us-iran-ceasefire-deal-announced-trump-says-strait-of-hormuz-reopening · **Rang 2:** Reuters (via Oil & Gas 360), 12.06.2026, 13:22 GMT. https://www.oilandgas360.com/oil-falls-to-near-two-month-lows-as-trump-calls-off-threatened-strikes-on-iran/ | AP: „reached an agreement to end the war and open the Strait of Hormuz“ | keine (Sonntag 14.06. ✓) | ✓ Beide Seiten bestätigen: Trump auf Social Media, Irans Vize-Außenminister Gharibabadi im Staatsfernsehen „on Sunday“. ✓ Krieg seit 28.02. ✓ Hormus-Öffnung („toll free opening“). **Präzisierung:** Die Unterzeichnung war erst für Freitag in der Schweiz geplant. Iran wollte vorher nicht umsetzen. **Brent ~87 am 12.06.:** Reuters meldet um 13:22 GMT **88,11 USD (−2,5 %)**, Schlusskurs nicht gefunden. ~87 ist damit nicht exakt belegt. **Quellenangabe in der CSV:** Das Briefing vom 14.06. (So, 07:00 Uhr) enthält die Bestätigung noch nicht, erst das vom 15.06. Same-Day: ok (Brent stammt vom Freitag davor). | `AP 14.06.2026 / Markt-Briefing 15.06.2026` |
| **E5** 20.06. `hormus_eskalation` | **bestätigt** | **Rang 2:** AP (via PBS), „U.S. and Iran to talk Sunday in Switzerland as Tehran says it closed Strait of Hormuz again“, **20.06.2026, 19:04 EDT**. https://www.pbs.org/newshour/world/u-s-and-iran-to-talk-sunday-in-switzerland-as-tehran-says-it-closed-strait-of-hormuz-again · **Rang 1:** US CENTCOM, „Commercial Vessels Flow Through Open Strait of Hormuz“, 20.06.2026, Tampa. https://www.centcom.mil/MEDIA/PUBLIC-RELEASES/Article/4522490/commercial-vessels-flow-through-open-strait-of-hormuz/ · **o. R.:** Jerusalem Post (nach Mehr/Fars), 20.06.2026, 16:45 UTC. https://www.jpost.com/middle-east/article-899969 | AP (CENTCOM-Sprecher Capt. Tim Hawkins): „Iran does not control the Strait of Hormuz.“ | keine (Samstag 20.06. ✓) | ✓ Iran erklärt Hormus für geschlossen. Laut Mehr ordnete das gemeinsame Oberkommando die Schließung an, Begründung Libanon. ✓ CENTCOM bestreitet die Kontrolle (wörtlich) und meldet 55 Transits. ✓ „nur Tage nach der Wiederöffnung“ (AP: Schiffe fuhren wieder nach Unterzeichnung „earlier in the week“). **Same-Day, Grenzfall:** Der Satz „Marktreaktion … erst am nächsten Handelstag Montag 22.06.“ nennt keine Zahl, beschreibt aber einen Sachverhalt vom 22.06. Er ist nur insofern unkritisch, als der 20.06. ein Samstag ist. | `AP 20.06.2026 / US CENTCOM Press Release 20.06.2026 / Markt-Briefing 22.06.2026` |
| **E6** 22.06. `hormus_deeskalation` | teilweise | **Rang 1:** Eidg. Departement für auswärtige Angelegenheiten (EDA), „Memorandum of Understanding between the USA and Iran“. https://www.eda.admin.ch/en/memorandum-of-understanding-between-the-usa-and-iran. Gespräche ab So 21.06., durch die Nacht; gemeinsame Erklärung Pakistan/Katar am **22.06.** · **o. R.:** PTI (via Business Standard), **22.06.2026, 09:37 IST** (= 04:07 UTC). https://www.business-standard.com/world-news/us-iran-agree-on-roadmap-for-final-deal-within-60-days-at-swiss-talks-126062200083_1.html · **Rang 2:** Reuters (via Arab News), 22.06.2026, 08:24 UTC. https://www.arabnews.com/node/2648092/amp · **Rang 2:** Reuters (via Offshore Technology), 22.06.2026, 09:54 UTC. https://www.offshore-technology.com/news/brent-crude-iran-export-waivers/ · **o. R.:** Al Jazeera, „Key outcomes …“, 22.06.2026. https://www.aljazeera.com/news/2026/6/22/what-are-the-key-outcomes-of-the-iran-us-talks-in-switzerland-what-next | EDA: „an agreement on a roadmap aimed at reaching a final agreement within 60 days“ | keine (Mo 22.06. ✓; Erklärung vor Börsenöffnung in Europa) | ✓ Fahrplan in der Schweiz (Bürgenstock), finales Abkommen binnen 60 Tagen. **✗ „zollfreie Wiederöffnung“:** Laut EDA und Al Jazeera enthält der Fahrplan keine Zollregelung. Vereinbart wurde ein Kommunikationskanal „for safe passage“. Zollfrei war das Abkommen vom 14.06. (AP 14.06.; AP 20.06.: Trump droht nach 60 Tagen mit Gebühren). **✗ „Brent ~77,5 USD“:** Reuters meldet **79,38 USD** (07:16 saudische Zeit) und **79,96 USD** (08:15 GMT). Schlusskurs nicht gefunden. 77,5 kommt nur im Briefing vom 23.06. vor und könnte ein Stand vom 23.06. sein. Dann wäre es ein Same-Day-Verstoß. **„tiefster Stand seit Anfang März“:** nicht belegt und als superlative Rangierung nach METHODIK §7 ohnehin verboten. | `Gemeinsame Erklärung Pakistan/Katar via EDA 22.06.2026 / Reuters 22.06.2026 / Markt-Briefing 23.06.2026` |

---

## 3 Befunde, die deine Entscheidung brauchen

Ich schlage zu keinem Befund eine Datumsänderung vor (Regel 4). Ich beschreibe nur, was die Quellen sagen und welche Folge das unter den registrierten Regeln hätte.

**B1 – E3: Ereignistag ist Freitag 05.06., nicht Sonntag 07.06.**

- **Beleg:** Der CENTCOM-Release ist auf den 05.06.2026 datiert. Er sagt „On June 5 … intercepted“. Laut Al Jazeera wurden die Raketen „late on Friday night“ abgefeuert. Öffentlich wurde es in der Nacht zum 06.06. (MEE 04:27 BST).
- **Folge, drei Lesarten:**
  - Kalendertag 07.06. (so in der CSV) → nach der Regel 08.06.
  - Öffentlich am Sa 06.06. (UTC) → ebenfalls 08.06.
  - Ereignistag Fr 05.06. → **05.06.** Das ist ein Handelstag, an dem schon `payroll_surprise` liegt. Es entstünde eine zweite Kollision wie bei B5 (20.06./22.06.).
- **Zur Uhrzeit:** Der Angriff fiel nach Börsenschluss in Europa. Für eine Kurve vom 05.06. war er also noch nicht bekannt. Das spricht inhaltlich für 08.06.
- **Entscheiden musst du:** Welcher Tag gilt als „Ereignistag“ (Geschehen oder Veröffentlichung, und in welcher Zeitzone)? Und wird die Abweichung im Paper offengelegt? Unabhängig davon ist das Wort „Wochenend-Eskalation“ sachlich falsch.

**B2 – E2: Öffentlich wurde der Deal am Do 28.05.; am 31.05. war „wartet auf Zustimmung“ überholt.**

- **Beleg:**
  - AP und Axios melden die vorläufige Einigung am 28.05., Axios um 14:12 ET (= 20:12 MESZ, nach Börsenschluss in Europa).
  - Laut Axios vom 30.05. verlangte Trump am 29.05. Änderungen: „President Trump asked for several amendments to the deal his envoys reached“.
  - Al Jazeera am 31.05., 09:15 UTC: „Trump tightens terms“.
- **Folge:**
  - Das Datum 31.05. ist eine registrierte Entscheidung (Zusammenlegung 25.05./31.05. zum Wirkdatum). Ich rühre sie nicht an.
  - Der erste Handelstag nach dem Bekanntwerden wäre aber der **29.05.**, nicht der 01.06.
  - Die Beschreibung gibt den Stand vom 28.05. wieder. Am 31.05. lag schon Trumps Änderungswunsch vor. Das ist kein Leakage, aber die Beschreibung ist unvollständig.

**B3 – E6: Beschreibung enthält einen Bestandteil des Vorereignisses und eine unbelegte Ölzahl.**

- „zollfreie Wiederöffnung“ gehört zum Abkommen vom 14.06. (E4), nicht zum Fahrplan vom 22.06.
- „Brent ~77,5 USD (tiefster Stand seit Anfang März)“: Am 22.06. melden die Agenturen rund 79–80 USD. Ist 77,5 ein Stand vom 23.06., verstößt der Wert gegen die Same-Day-Regel. Der Superlativ verstößt in jedem Fall gegen METHODIK §7.
- **Zu entscheiden:** ob und wie die Beschreibung korrigiert wird. Das Datum ist nicht betroffen.

**B4 – E4: Falsches Briefing als Quelle angegeben.**

- `Markt-Briefing 14.06.2026` enthält nur Trumps Ankündigung vom Freitag und „kurz vor einem Abkommen“. Die Bestätigung durch beide Seiten steht erst im Briefing vom **15.06.** Das Datum 14.06. ist durch AP belegt.

**B5 – E1: „Marktreaktion verhalten“.** Nicht belegt. Die einzige (unzulässige) Spur spricht von Rekordständen. Zu entscheiden: streichen oder belegen.

**Nebenbefund (betrifft keine CSV-Zeile):**

- Das Briefing vom 22.06. meldet „Brent +14,9 % auf 92,56 USD“. Reuters meldet für denselben Morgen eine Eröffnung bei 82,30 USD und danach 79,38 USD. Die Zahl im Briefing ist falsch.
- Die Briefings vom 20./21.06. melden die Schweizer Gespräche als „abgesagt“. AP schreibt am 20.06., die Unterhändler seien auf dem Weg in die Schweiz.
- Das bestätigt die Ausgangsannahme: Die Briefings sind als Beleg unbrauchbar.

---

## 4 Was nicht geprüft werden konnte

- **Schlusskurse Brent** am 29.05., 12.06. und 22.06.: CNBC antwortet mit 403. Reuters-Schlussmeldungen habe ich nicht gefunden. Aggregatoren (Trading Economics, Fortune-Preisseite) sind nicht zulässig.
- **E2 Brent ~93–97 / WTI ~91:** Keine zulässige Quelle geöffnet. Wikipedia verweist auf CNBC (27.05.: 94,29); die Seite ist nicht abrufbar.
- **E1 Marktreaktion:** Keine Agenturmeldung zum Börsenschluss am 28.05. gefunden.
- **Reuters- und AP-Originalseiten:** Reuters-Text nur über Partnerseiten (Arab News, Offshore Technology, Oil & Gas 360), AP über PBS. Bloomberg (28.05.) und France 24 (06.06.) sperren den Abruf.
- **NYT** zu Trumps Änderungswunsch (29./30.05.): nicht geöffnet. Belegt über Axios.
- **Genaue Uhrzeit des CENTCOM-Release vom 05.06.:** DVIDS zeigt 22:20 ohne Zeitzone.

---

## 5 Teil B: Angaben aus `Paper/refs.bib`

Crossref (api.crossref.org) und später auch doi.org haben nach wenigen Anfragen mit „429 rate limited“ geantwortet. Project Euclid blockt per Bot-Schutz, MIT Press und Taylor & Francis mit 403. Geprüft ist deshalb, wohin die DOIs auflösen (doi.org-Handle-API). Die Verlags-URL enthält Band, Heft und Titel. Die **Seitenzahlen** ließen sich bei Project Euclid nicht prüfen.

| Schlüssel | Ergebnis | Beleg |
|---|---|---|
| `hansen1999` 10.1162/003465399558463 | **gefunden.** Löst auf eine URL mit Bd. 81, Heft 4, S. 594–607 auf. Das stimmt mit refs.bib überein. Titel am Verlag nicht gesehen (403). | https://direct.mit.edu/rest/article/81/4/594-607/57169 |
| `diciccio1996` 10.1214/ss/1032280214 | **gefunden.** Statistical Science Bd. 11, Heft 3, „Bootstrap confidence intervals“ ✓. Seiten 189–228 **nicht geprüft**. | https://projecteuclid.org/journals/statistical-science/volume-11/issue-3/Bootstrap-confidence-intervals/10.1214/ss/1032280214.full |
| `bergerhsu1996` 10.1214/ss/1032280304 | **gefunden.** Bd. 11, Heft 4, Titel ✓. Seiten 283–319 **nicht geprüft**. | https://projecteuclid.org/journals/statistical-science/volume-11/issue-4/Bioequivalence-trials-intersection-union-tests-and-equivalence-confidence-sets/10.1214/ss/1032280304.full |
| `bose1988` 10.1214/aos/1176351063 | **gefunden.** Annals of Statistics Bd. 16, Heft 4, Titel ✓. Seiten 1709–1722 **nicht geprüft**. | https://projecteuclid.org/journals/annals-of-statistics/volume-16/issue-4/Edgeworth-Correction-by-Bootstrap-in-Autoregressions/10.1214/aos/1176351063.full |
| `schwarz1978` 10.1214/aos/1176344136 | **gefunden.** Bd. 6, Heft 2, Titel ✓. Seiten 461–464 **nicht geprüft**. | https://projecteuclid.org/journals/annals-of-statistics/volume-6/issue-2/Estimating-the-Dimension-of-a-Model/10.1214/aos/1176344136.full |
| `efron1994` (JASA) | **nicht geprüft.** Die Verlagsseite liefert 403. Nur der Suchtreffer-Titel nennt „JASA Vol 89, No 426“ und DOI 10.1080/01621459.1994.10476768. Den Treffer habe ich nicht geöffnet, daher nicht bestätigt. Seiten des Artikels allein bzw. mit Kommentar und Erwiderung: **nicht geprüft**. **refs.bib zitiert aber den Technical Report.** Laut Stanford ist das „EFS NSF 397“ vom **Juli 1992** ✓. | https://statistics.stanford.edu/technical-reports/missing-data-imputation-and-bootstrap |
| `vonluxburg2009` | **gefunden.** Statistica Sinica **Bd. 19, Heft 3 (2009), S. 1095–1117**. refs.bib zitiert die arXiv-Fassung 0711.0198v1. Die Angaben stehen dort nicht im Eintrag; das ist kein Fehler. | https://www3.stat.sinica.edu.tw/sstest/j19n3/j19n312/j19n312.html |
| `mrkvicka2020` 10.1016/j.spasta.2020.100430 | **gefunden.** **Online seit 25.02.2020**, Druckausgabe **Bd. 42, April 2021**, Artikel 100430 (ScienceDirect). Crossref: created 2020-02-25, issued 2021-04. Stimmt mit refs.bib überein („Spatial Statistics 42 (2021), 100430“). | https://www.sciencedirect.com/science/article/abs/pii/S2211675320300245 · https://api.crossref.org/works/10.1016/j.spasta.2020.100430 |

**Abweichend: keine.** Was offen ist, ist nicht geprüft, nicht widersprochen.
