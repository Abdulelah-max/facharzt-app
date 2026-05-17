# Pending Changes — wird gesammelt eingespielt, wenn User Review fertig

## 1. F4 (Empf. 7.4) — Erklärung erweitern um PET-CT-Mechanismus

Aktuelle Erklärung ist zu mechanistisch dünn. Neu (knapp):

> PET-CT findet okkulte extrahepatische Streuung (Peritoneum, mediastinale LK, Lunge, Knochen) oder zusätzliche Leberherde, die das CT übersah → kurative Resektion entfällt, weil R0 nicht mehr erreichbar. Ruers-RCT: futile Laparotomien 45 % → 28 %, kein Überlebensvorteil.

## 2. Erklärungs-Stil — generell KÜRZEN

User-Feedback: nach Klick auf Richtig/Falsch nur **knappe, logische Kurz-Begründung**.
"Muss nicht lang sein, sonst wird langweilig."

→ Refaktorieren:
- `explanation` Feld bleibt kurz (1-2 Sätze, Kernlogik)
- `leitlinie_wortlaut` (kursiv) bleibt als zweiter Block — der ist okay weil identisches Zitat aus LL
- Lange Hintergrund-Infos / Studien (Ruers etc.) → entweder gar nicht oder in optionales Detail-Feld

Beispiel-Stil:
- **Vorher:** "Empfehlung 7.5 (EK, Konsens) macht eine explizite Ausnahme: 'mit Ausnahme von T1-Tumoren'. Bei T1-Karzinomen ist die CEA-Bestimmung nicht gefordert. CA 19-9 und CA 125 werden nicht als Standard empfohlen (nur diskutiert)."
- **Nachher:** "T1-Tumoren sind explizit ausgenommen. CA 19-9 / CA 125 sind kein Standard."

## 3. Neue Fragen F6–F10 (Kap. 7.6, 7.8, 7.10, 7.12, 7.13)

Liegen User zur Review vor. Noch nicht freigegeben.

Nach Freigabe: ins `data/questions.json` schreiben mit IDs:
- krk_7_6_a, krk_7_8_a, krk_7_10_a, krk_7_12_a, krk_7_13_a

## 4. Reload-Strategie

Wenn alle Änderungen drin: Safari reload (Cmd-R) reicht — Service Worker hat Network-First für `questions.json`, also wird die neue Datei geholt.
