# QC-Report — Check 1 (automatischer Wortlaut-Abgleich)

`leitlinie_wortlaut` gegen den echten Empfehlungstext im PDF (lokalisiert über `empfehlung_nr`, Token-Abgleich).

**Gesamt 248** · ✅ OK 240 · ⚠️ PRUEFEN 4 · ❌ MISMATCH 4 · ❔ KEINE_BOX 0 · KEIN_PDF 0

> OK = inhaltlich belegt. PRUEFEN/MISMATCH = gegenlesen (paraphrasiert, gekürzt oder echter Fehler). KEINE_BOX = Empf.-Nr. nicht im PDF gefunden (Nummer prüfen).

## Zu prüfen (coverage aufsteigend)

### krk_9_7_b — MISMATCH (cov 0.13) · krk Empf. 9.7 · S.183
- **Frage (R):** Bei einem Stadium-II-Kolonkarzinom mit MSI-H-Status soll laut S3-LL keine adjuvante 5-Fluorouracil-Monotherapie eingesetzt werden — dieser Tumortyp profitiert nicht davon.
- **Wortlaut (App):** Der MSI-/MMR-Status sollte insbesondere genutzt werden, um eine Subgruppe (10-15 %) von Patienten im UICC-Stadium II zu identifizieren, die ein sehr geringes Rezidivrisiko haben und bei denen der Nutzen einer Fluoropyrimidin-basierten antitumoralen Therapie nicht nachgewiesen werden konnte. Die Durchführung einer adjuvanten Chemotherapie ist bei diesen Patienten nicht zu empfehlen.
- **Leitlinie (PDF):** Bei Patienten im Stadium II soll vor der Indikationsstellung für eine adjuvante Che- motherapie der Mikrosatellitenstatus bestimmt werden. [660], [775], [776], [777]

### krk_9_5_b — MISMATCH (cov 0.16) · krk Empf. 9.5 · S.181
- **Frage (R):** Auch im Kolonkarzinom-Stadium II ohne Risikofaktoren sollte laut S3-LL die Option einer adjuvanten Chemotherapie mit dem Patienten besprochen werden, da ein leichter Nutzen aus der QUASAR-Studie ableitbar bleibt.
- **Wortlaut (App):** Aufgrund der positiven Ergebnisse der QUASAR Studie kann der Nutzen einer adjuvanten Therapie im Stadium II ohne Risikofaktoren nicht gänzlich ausgeschlossen werden. Deshalb sollte eine Therapie in diesem Stadium zumindest in Betracht gezogen werden, in jedem Fall sollten die Vorteile und Risiken einer solchen Therapie mit dem Patienten besprochen werden.
- **Leitlinie (PDF):** Bei Patienten mit einem kurativ resezierten Kolonkarzinom im Stadium II kann eine adjuvante Chemotherapie durchgeführt werden. [755], [756], [757], [758], [759]

### pank_6_20_a — MISMATCH (cov 0.46) · pankreas Empf. 6.20 · S.117
- **Frage (R):** Eine perioperative Antibiotikaprophylaxe sollte laut S3-LL bei Pankreasresektion immer erfolgen — unabhängig vom Stent-Status.
- **Wortlaut (App):** Eine perioperative Antibiotikaprophylaxe sollte immer erfolgen. Hierbei sollte die Prophylaxe unterschiedslos zwischen Patienten mit und ohne Stent erfolgen.
- **Leitlinie (PDF):** Eine perioperative Antibiotikaprophylaxe sollte immer erfolgen. [234], [332], [333], [334]

### krk_9_1_a — MISMATCH (cov 0.5) · krk Empf. 9.1 · S.176
- **Frage (R):** Die adjuvante Chemotherapie eines Kolonkarzinoms sollte laut S3-LL baldmöglichst postoperativ eingeleitet werden — in RCTs erfolgte der Beginn innerhalb von 8 Wochen.
- **Wortlaut (App):** Die adjuvante Chemotherapie sollte baldmöglichst postoperativ eingeleitet werden. In den randomisierten Studien wurde die adjuvante Chemotherapie innerhalb von 8 Wochen eingeleitet.
- **Leitlinie (PDF):** Die adjuvante Chemotherapie sollte baldmöglichst postoperativ eingeleitet wer- den. [735], [736], [737]

### krk_5_17_a — PRUEFEN (cov 0.66) · krk Empf. 5.17 · S.71
- **Frage (F):** Bei einem Kolonkarzinom eines MSH6- oder PMS2-Anlageträgers soll laut S3-LL regelhaft eine erweiterte (sub)totale Kolektomie wegen der hohen Metachronierate erfolgen.
- **Wortlaut (App):** Bei Kolonkarzinomen bei Anlageträgern für das Lynch-Syndrom mit Mutation in einem Hochrisiko-Gen (MLH1/MSH2/EPCAM) sollte die Option einer lokalisationsbezogenen onkologischen Resektion versus einer erweiterten onkologischen Resektion (subtotale Kolektomie) besprochen werden. Bei MSH6 oder PMS2 soll eine prophylaktisch erweiterte Resektion nicht regelhaft erfolgen.
- **Leitlinie (PDF):** Bei Kolonkarzinomen bei Anlageträgern für das Lynch-Syndrom mit Mutation in einem Hochrisiko-Gen (MLH1/MSH2/EPCAM) sollte die Option einer lokalisations- bezogenen onkologischen Resektion versus einer erweiterten onkologischen Re- sektion (subtotale Kolektomie) besprochen werden. [196]

### krk_8_2_a — PRUEFEN (cov 0.7) · krk Empf. 8.2 · S.156
- **Frage (R):** Im pathologischen Resektat-Befund eines KRK sollen laut S3-LL u.a. pT, pN (mind. 12 LK), L/V/Pn, R-Klassifikation, Abstand zu Resektionsrändern (beim Rektum auch CRM), Regressionsgrad (nach Neoadjuvanz), MSI-Status und Mutationsstatus relevanter Gene enthalten sein.
- **Wortlaut (App):** Folgende Angaben sollen durch den Pathologen am Resektat erhoben werden: Tumortyp nach WHO; pT, Tumorgröße, Lokalisation; pN; Anzahl untersuchter LK (mindestens 12); Grading; L/V/Pn-Status; Abstand zu Resektionsrändern (Rektum auch CRM); R-Klassifikation; Regressionsgrad (Rektum nach Neoadjuvanz); MSI-Status; Mutationsstatus; Budding; bei pT1 Risiko-Score; TME-Präparat-Qualität.
- **Leitlinie (PDF):** Folgende Angaben sollen durch den Pathologen am Resektat erhoben werden: • Tumortyp nach WHO-Klassifikation • Tumorinvasionstiefe (pT-Klassifikation) • Tumorgröße • Lokalisation des Tumors • Status der regionäre Lymphknoten (pN-Klassifikation) • Anzahl der untersuchten Lymphknoten inkl. Verhältnis von untersuchten zu befallenen Lymphknoten • Mindestanzahl der zu untersuchenden Lymphknoten: 12 • Gr

### krk_6_15_a — PRUEFEN (cov 0.77) · krk Empf. 6.15 · S.114
- **Frage (R):** Bei Patienten mit 3-4 low-risk-Adenomen (LRA) sollte laut S3-LL eine Kontroll-Koloskopie nach 3-5 Jahren empfohlen werden — bei ≥5 LRA verkürzt auf <3 Jahre.
- **Wortlaut (App):** Bei Patienten mit 3-4 low-risk-Adenomen sollte eine Kontrollkoloskopie nach 3-5 Jahren empfohlen werden. Bei Patienten mit ≥ 5 low-risk-Adenomen sollte das Kontrollintervall < 3 Jahre betragen.
- **Leitlinie (PDF):** Bei Patienten mit 3 – 4 low-risk-Adenomen sollte eine Kontrollkoloskopie nach 3 – 5 Jahren empfohlen werden.

### krk_11_3_a — PRUEFEN (cov 0.78) · krk Empf. 11.3 · S.245
- **Frage (F):** Die regelmäßige Bestimmung des CEA-Wertes in der KRK-Nachsorge ist laut S3-LL eindeutig mit einer Reduktion der krebsbedingten Mortalität assoziiert.
- **Wortlaut (App):** Der Nutzen der Bestimmung des karzinoembryonalen Antigens (CEA) in der Nachsorge des kolorektalen Karzinoms ist nicht eindeutig.
- **Leitlinie (PDF):** Der Nutzen der Bestimmung des karzinoembryonalen Antigens (CEA) in der Nach- sorge des kolorektalen Karzinoms – insbesondere bei Patienten mit prätherapeu- tisch nicht erhöhten Werten – wird kontrovers diskutiert. Die Bestimmung von CEA bei prätherapeutisch erhöhten CEA-Werten kann nach kurativ intendierter Therapie erfolgen. [983], [984], [985]
