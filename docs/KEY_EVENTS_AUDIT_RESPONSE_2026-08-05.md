# Audit-Response & Changelog — `key_events.csv`

**Datum:** 2026-08-05 · **Bezug:** `KEY_EVENTS_AUDIT_2026-07-27.md` · **Bearbeiter:** Cowork
**Grundlage:** Audit zuvor zeilenweise gegen die echten Dateien code-verifiziert (siehe unten).

---

## 0. Verifikation des Audits (vor Umsetzung)

Der Audit wurde unabhängig gegen `key_events.csv`, `METHODIK.md`, `hmm_input_changes.csv`
und alle 27 Juni-Briefings geprüft. **Ergebnis: fachlich korrekt** — alle Wochentage,
Same-Day-Verstöße, Quellen-Zählung (3/11 mit Primärquelle), Namens-Inkonsistenz und die
Kriterien-Verteilung (K1=2/K2=5/K3=2/ungedeckt=2) stimmen exakt.

**Zwei Rechen-/Formulierungs-Ungenauigkeiten im Audit (nicht substanziell):**
1. §3.3 „fünf Hormus-Zeilen in **15 Tagen**" — die fünf (07.06.–28.06.) spannen tatsächlich
   **21 Tage**; nur der enge Vierer-Cluster (14.06.–28.06.) sind 14 Tage.
2. §4 „26 Zeilen, davon **24** im Handelstags-Index" — korrekt sind **21** (26 − 5 Wochenend-
   Events). Diese Zahl ist in METHODIK §7 richtig eingetragen.

---

## 1. Umgesetzt (mit Backup in `Code/_bak/`)

`key_events.csv`: **28 → 26 Zeilen.** Verifiziert: 0 leere Felder, alle Zeilen 4 CSV-Felder,
sauberes Dateiende, 21 im Handelstags-Index / 5 Wochenende.

| # | Änderung | Zeile |
|---|---|---|
| #1 | **05.06. umgehängt** `tech_selloff` → `payroll_surprise` (K3). Beschreibung führt jetzt mit der Payroll-Überraschung (+172k vs. Konsens ~85k); AVGO-Selloff als Same-Day-Reaktion behalten. Primärquelle **BLS**. | 18 |
| #1 | **24.06. gestrichen** (`tech_selloff`) — von keinem K gedeckt + zirkulär (Ereignis = Marktbewegung selbst). | ex-26 |
| #5 | **28.06. gestrichen** (`hormus_eskalation`) — Same-Day-Verstoß (Futures Mo) + nach Sample-Ende 26.06. | ex-28 |
| #2 | **14.06. Same-Day gekürzt** — „Friedensrally Montag 15.06 / Dow-Rekord 51.671" (Folgetagsdaten) entfernt; behalten: Abkommen + Hormus-Wiederöffnung + Freitags-Brent ~87. | 22 |
| #2 | **20.06. geklärt + gekürzt** — Ölmove „+15 % / Brent ~92" ist die Reaktion am **nächsten Handelstag (Montag 22.06.)**, nicht am Samstagsereignis selbst; entfernt und im Text vermerkt. (Juneteenth-Freitag 19.06. ist irrelevant und im Euro-Index ohnehin ein regulärer Handelstag.) | 24 |
| #6 | **Primärquelle BEA** für PCE 25.06. nachgetragen. | 26 |
| #7 | **Label vereinheitlicht** `hormus_escalation` → `hormus_eskalation` (15.04.). | 11 |
| #8 | **METHODIK §7** neuer Audit-Eintrag 2026-07-27 (26 Events, K1=11/K2=8/K3=6/K4=1); §7-Kopf 17→26; §2 „18 key_events" → 26. | — |

**Neue Kriterien-Verteilung (26 Events, 0 ungedeckt): K1=11 · K2=8 · K3=6 · K4=1.**

**Primärquellen-Bilanz Juni:** 3 → 5 offizielle Primärquellen (BLS 05.06., BLS 10.06.,
ECB 11.06., FOMC 17.06., BEA 25.06.). Die verbleibenden 4 Juni-Zeilen sind geopolitisch
(Hormus, 07./14./20./22.06.) und damit methodisch korrekt briefing-basiert — die
zeitgleiche Briefing-Erfassung IST hier die Ground Truth (METHODIK §1). Keine Quelle erfunden.

**Vollständigkeits-Scan 01.–26.06. (alle Briefings gelesen):** ein Grenzfall — Eurozone-
Flash-CPI Mai 3,2 % am 02.06. (K3-fähig, aber nicht briefing-dominant → nicht aufgenommen).
Bewusst außerhalb K1–K4: BoE 18.06. & PBoC 22.06. (K1 nur EZB/Fed), Micron-Blowout 24.06.
(Earnings), G7 Evian, Juni-Flash-PMIs 23.06.

---

## 2. ENTSCHIEDEN 2026-08-05 (Klaus, vor dem Fit) — in METHODIK §7/§2 fixiert

- **#3 Cluster-Regel Hormus-Strang → NICHT konsolidieren.** Der 31.05.-Präzedenzfall trägt
  nicht: dort wurde derselbe Akt in derselber Richtung doppelt erfasst (Signal 25.05. →
  Vereinbarung 31.05.). Die Juni-Kette ist gegenläufig — Eskalation 07.06. → Abkommen
  14.06. → erneute Schließung 20.06. → Roadmap 22.06. — also eigenständige Akte mit je
  eigener Marktnarrative; Mergen würde echte Information löschen. **Explizite Regel in §7:**
  konsolidiert wird nur „gleicher Akt, gleiche Richtung (Signal → Bestätigung)"; ein
  Richtungswechsel begründet immer eine eigene Zeile (begründet 31.05. nachträglich mit).
  Die Ereignis-Abhängigkeit gehört ins **Testdesign, nicht in die Daten**: statt unabhängiger
  Permutation ein **zirkulärer Shift** des ganzen Ereignisvektors (zufälliger Offset τ,
  wrap-around über 377 Tage) — erhält die inneren Ereignis-Abstände unter H0.
  `scipy.stats.permutation_test` kann das nicht nativ; Shift-Variante selbst implementieren
  (KW31-Design). **Vorab registriert:** beide Auswertungen berichten — alle Zeilen UND eine
  Zeile je Episode. (In §2 eingetragen.)
- **#4 Zuordnungsregel → nächster Handelstag.** Ökonomisch die einzig zulässige Richtung
  (Zurückschieben = Look-ahead; Ausschluss kostete 5/26 Events inkl. `hormus_start` 28.02.).
  Code-geprüft, alle im Sample: 28.02.→02.03., 31.05.→01.06., 07.06.→08.06., 14.06.→15.06.,
  20.06.→22.06. Dazu vorab: **Nähemaß-Fenster ±k mit k ≥ 2** und **Sensitivität k ∈ {1,2,3}**
  (US-Abend-Releases erreichen die Euro-Kurve erst am Folgetag). (In §7 eingetragen.)

**Offen bleibt nur die Umsetzung:** die zirkuläre Shift-Test-Funktion für KW31 — sag
Bescheid, dann skizziere ich sie (wenige Zeilen, passt in die Design-Skizze).
