# QC — Qualitätssicherung der Fragen

Ziel: **jede Frage wird mindestens 2× kontrolliert** und gegen die aktuelle
S3-Leitlinie abgeglichen. Nichts aus dem Gedächtnis — alles muss aus dem
Leitlinien-PDF in `../leitlinien/` belegbar sein.

## Die zwei Checks

| | Was | Wie |
|---|---|---|
| **Check 1** | Stimmt der `leitlinie_wortlaut` wörtlich mit der Leitlinie überein? | **automatisch** via `python3 qc/verify.py` |
| **Check 2** | Ist der Fachinhalt + die Richtig/Falsch-Wertung korrekt? | **manuell/klinisch** — Häkchen in `REVIEW.md` |

## Ablauf

1. Leitlinie-PDF liegt in `../leitlinien/` (z. B. `pankreas-v3.1.pdf`).
   Neue Leitlinie? In `verify.py` unter `PDFS` ergänzen.
2. Nach **jeder** Inhaltsänderung an `data/questions.json`:
   ```bash
   python3 qc/verify.py
   ```
3. Ergebnisse:
   - `qc-report.md` — alle ⚠️/❌-Treffer mit Wortlaut vs. PDF-Text zum Gegenlesen.
   - `REVIEW.md` — Liste ALLER Fragen mit Check-1-Status + Häkchen-Spalte für Check 2.
   - `qc-log.json` — maschinenlesbares Protokoll (für Verlauf/Diffs).
4. ⚠️ PRUEFEN / ❌ MISMATCH gegenlesen. Häufige harmlose Ursachen:
   Gedankenstrich „3 – 4", Aufzählungs-Bullets, Silbentrennung im PDF, oder
   bewusst zitierter Hintergrund-Text. Echte Abweichung → Frage korrigieren.

## Status-Bedeutung (Check 1)

- ✅ **OK** — Wortlaut inhaltlich in der zitierten Empfehlung belegt (≥ 85 %).
- ⚠️ **PRUEFEN** — Teil-Übereinstimmung (65–85 %), meist Formatierung; kurz prüfen.
- ❌ **MISMATCH** — < 65 %, unbedingt gegenlesen.
- ❔ **KEINE_BOX** — `empfehlung_nr` nicht im PDF gefunden (Nummer prüfen).

> Check 1 ist ein Sieb, kein Urteil: er findet Abweichungen vom Wortlaut, ersetzt
> aber nicht den klinischen Check 2.

## Automatik (Git-Hook)

Ein pre-commit-Hook lässt `verify.py` bei **jedem Commit, der `data/questions.json`
ändert**, automatisch laufen und committet den aktualisierten Report mit.
Einmalig pro Clone aktivieren:

```bash
git config core.hooksPath qc/hooks
```

Der Hook blockiert nie — er warnt nur, wenn eine Frage nicht automatisch belegt ist.

## Check-1-Herkunft (`via` im qc-log)

- `Empfehlung` — Wortlaut steht in der zitierten Empfehlung.
- `Hintergrund` — wörtlich im Hintergrund-Text derselben Empfehlung (z. B. Nuancen-Frage).
- `Leitlinie` — wörtlich an anderer Stelle der Leitlinie (Empf.-Nr. ggf. prüfen).
