# Facharzt KRK – S3-Leitlinie Quiz

True/False-Lern-App für die Facharztprüfung Viszeralchirurgie.
Alle Fragen sind **direkt aus den deutschen S3-Leitlinien** belegt, mit
Empfehlungs-Nummer, Evidenzgrad, Konsensstärke und PDF-Seite.

## Stack
Reines HTML/CSS/JS, kein Build. Läuft offline als PWA.

## Lokal starten
```bash
cd ~/Desktop/facharzt-app
python3 -m http.server 8080
# → http://localhost:8080
```

Direkt im Browser per `file://` öffnen geht **nicht** (Service Worker + fetch brauchen HTTP).

## Auf dem iPhone als App speichern
1. Projekt-Ordner via Tunnel/Server erreichbar machen (z. B. `ngrok http 8080` oder GitHub Pages).
2. Im Safari öffnen → Teilen → "Zum Home-Bildschirm".
3. Offline-Modus funktioniert nach erstem Öffnen (Service Worker cached alles).

## Struktur
```
facharzt-app/
├── index.html              App (single-file)
├── manifest.webmanifest    PWA-Manifest
├── sw.js                   Service Worker (offline cache)
├── icon.svg                App-Icon
├── data/questions.json     Alle Fragen
├── leitlinien/             Original-PDFs (read-only Referenz)
└── scripts/                Extraktions-Notizen pro Kapitel
```

## Frage-Schema
Siehe `data/questions.json` und das Schema in den Projekt-Notizen.
Jede Frage MUSS belegt sein durch:
- `empfehlung_nr` (z. B. "7.13")
- `leitlinie_wortlaut` (Original-Zitat)
- `seite_pdf` (zur Verifikation)

Ohne diese Felder: Frage nicht aufnehmen.
