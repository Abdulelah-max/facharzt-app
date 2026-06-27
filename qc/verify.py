#!/usr/bin/env python3
"""
QC / Verifikation der Quiz-Fragen gegen die echten S3-Leitlinien-PDFs.

CHECK 1 (automatisch, dieses Skript): Für jede Frage wird der gespeicherte
`leitlinie_wortlaut` mit dem tatsächlichen Empfehlungs-/Statement-Text der
Leitlinie abgeglichen. Dazu wird die passende Empfehlungs-Box (über
`empfehlung_nr`) aus dem PDF extrahiert und bereinigt (Spalten-Labels raus),
dann der Anteil der Wortlaut-Inhaltswörter berechnet, der in dieser Box steht
(Token-Mengen-Abgleich — robust gegen pdftotext-Worttrennungen).
  coverage ≥ 0.85 -> OK        (inhaltlich belegt)
  0.65–0.85       -> PRUEFEN   (teilweise; ggf. paraphrasiert/gekürzt)
  < 0.65          -> MISMATCH  (gegenlesen!)
  Box/Nr fehlt    -> KEINE_BOX

CHECK 2 (klinisch/Logik, manuell): in qc/REVIEW.md mit Häkchen abhaken
(Fachinhalt + Richtig/Falsch-Wertung gegen die Empfehlung geprüft).

Nutzung:   python3 qc/verify.py
Ausgaben:  qc/qc-log.json, qc/qc-report.md, qc/REVIEW.md
Voraussetzung: poppler (pdftotext) + PDFs in leitlinien/.
Nach JEDER Inhaltsänderung erneut laufen lassen ("regelmäßig überprüfen").
"""
import re, json, os, subprocess, sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QFILE = os.path.join(ROOT, "data", "questions.json")
CACHE = os.path.join(ROOT, "qc", "cache")
os.makedirs(CACHE, exist_ok=True)

# Leitlinie-ID -> PDF (im leitlinien/-Ordner). Neue Leitlinien hier ergänzen.
PDFS = {
    "krk": "leitlinien/krk-v3.2.pdf",
    "pankreas": "leitlinien/pankreas-v3.1.pdf",
}
OK_T, PRUEF_T = 0.85, 0.65

HEAD = re.compile(r"^\s*(\d{1,2}\.\d{1,2}[a-z]?)\s+(Evidenzbasierte Empfehlung|Konsensbasierte Empfehlung|Evidenzbasiertes Statement|Konsensbasiertes Statement|Statement)\b")
LABEL = re.compile(r"^\s*(Empfehlungsgrad|Empfehlungs\s*grad|Level of Evidence|Expertenkonsens|EK|[ABC0]|1a|1b|2a|2b|2c|3a|3b|3|4|5|geprüft 20\d\d|modifiziert 20\d\d|neu 20\d\d|bestätigt 20\d\d|geändert 20\d\d)\s{2,}(.*)$")
DROP = re.compile(r"^\s*(Empfehlungsgrad|Level of Evidence|Expertenkonsens|EK|[ABC0]|1a|1b|2a|2b|2c|3a|3b|3|4|5|Starker Konsens|Konsens|Mehrheitliche.*|Mehrheitlicher.*|Dissens|Kein Konsens|Konsensstärke.*|geprüft 20\d\d.*|modifiziert 20\d\d.*|neu 20\d\d.*|bestätigt 20\d\d.*|\d{1,3})\s*$")
PAGEHDR = re.compile(r"^\s*\d{1,2}\.\d{1,2}\b.+?\s+\d{2,3}\s*$")
FOOTER = re.compile(r"inienprogramm|Leitlinienprogramm")
WORD = re.compile(r"[a-zäöüß0-9]+", re.I)


def pdf_to_text(pdf_rel):
    pdf = os.path.join(ROOT, pdf_rel)
    if not os.path.exists(pdf):
        return None
    txt = os.path.join(CACHE, os.path.basename(pdf) + ".txt")
    if not os.path.exists(txt) or os.path.getmtime(txt) < os.path.getmtime(pdf):
        try:
            subprocess.run(["pdftotext", "-layout", pdf, txt], check=True)
        except Exception as e:
            print(f"  ! pdftotext fehlgeschlagen für {pdf_rel}: {e}")
            return None
    return open(txt, encoding="utf-8", errors="replace").read()


def clean_line(line):
    if FOOTER.search(line) or PAGEHDR.match(line) or DROP.match(line):
        return None
    m = LABEL.match(line)
    return (m.group(2) if m else line).strip()


def parse_boxes(text):
    """{empfehlung_nr: bereinigter Empfehlungstext (bis 'Hintergrund')}."""
    lines = text.split("\n")
    starts = [(i, HEAD.match(l).group(1)) for i, l in enumerate(lines) if HEAD.match(l)]
    out = {}
    for k, (i, nr) in enumerate(starts):
        end = starts[k + 1][0] if k + 1 < len(starts) else min(i + 90, len(lines))
        parts = []
        for bl in lines[i + 1:end]:
            if not bl.strip():
                continue
            if bl.strip().startswith("Hintergrund"):
                break
            c = clean_line(bl)
            if c:
                parts.append(c)
        body = re.sub(r"\s+", " ", " ".join(parts)).strip()
        if nr not in out or len(body) > len(out[nr]):
            out[nr] = body
    return out


def toks(s):
    return set(w for w in WORD.findall((s or "").lower()) if len(w) >= 4)


def get_box(boxes, nr):
    if not nr:
        return None
    if nr in boxes:
        return boxes[nr]
    if nr[-1].isalpha() and nr[:-1] in boxes:   # 5.13b -> 5.13
        return boxes[nr[:-1]]
    return None


def main():
    questions = json.load(open(QFILE, encoding="utf-8"))
    boxes_by = {}
    for ll, pdf in PDFS.items():
        t = pdf_to_text(pdf)
        boxes_by[ll] = parse_boxes(t) if t else None
        print(f"  {ll}: {str(len(boxes_by[ll])) + ' Empfehlungs-Boxen' if t else 'PDF fehlt'}")

    log = []
    for q in questions:
        ll = (q.get("leitlinie") or {}).get("id")
        boxes = boxes_by.get(ll)
        box = get_box(boxes, q.get("empfehlung_nr")) if boxes else None
        wt = toks(q.get("leitlinie_wortlaut", ""))
        cov = (len(wt & toks(box)) / len(wt)) if (box and wt) else 0.0
        if boxes is None:
            st = "KEIN_PDF"
        elif box is None:
            st = "KEINE_BOX"
        else:
            st = "OK" if cov >= OK_T else ("PRUEFEN" if cov >= PRUEF_T else "MISMATCH")
        log.append({
            "id": q["id"], "leitlinie": ll, "empfehlung_nr": q.get("empfehlung_nr"),
            "kapitel": q.get("kapitel"), "seite_pdf": q.get("seite_pdf"), "answer": q.get("answer"),
            "check1_auto": {"status": st, "coverage": round(cov, 2)},
            "statement": q.get("statement"),
            "leitlinie_wortlaut": q.get("leitlinie_wortlaut"),
            "leitlinie_pdf": box or "",
        })

    json.dump(log, open(os.path.join(ROOT, "qc", "qc-log.json"), "w"), ensure_ascii=False, indent=2)

    by = Counter(e["check1_auto"]["status"] for e in log)
    flagged = [e for e in log if e["check1_auto"]["status"] in ("PRUEFEN", "MISMATCH", "KEINE_BOX")]
    rep = ["# QC-Report — Check 1 (automatischer Wortlaut-Abgleich)\n",
           "`leitlinie_wortlaut` gegen den echten Empfehlungstext im PDF (lokalisiert über `empfehlung_nr`, Token-Abgleich).\n",
           f"**Gesamt {len(log)}** · ✅ OK {by.get('OK',0)} · ⚠️ PRUEFEN {by.get('PRUEFEN',0)} · "
           f"❌ MISMATCH {by.get('MISMATCH',0)} · ❔ KEINE_BOX {by.get('KEINE_BOX',0)} · KEIN_PDF {by.get('KEIN_PDF',0)}\n",
           "> OK = inhaltlich belegt. PRUEFEN/MISMATCH = gegenlesen (paraphrasiert, gekürzt oder echter Fehler). "
           "KEINE_BOX = Empf.-Nr. nicht im PDF gefunden (Nummer prüfen).\n"]
    if flagged:
        rep.append("## Zu prüfen (coverage aufsteigend)\n")
        for e in sorted(flagged, key=lambda x: x["check1_auto"]["coverage"]):
            s = e["check1_auto"]
            rep.append(f"### {e['id']} — {s['status']} (cov {s['coverage']}) · {e['leitlinie']} Empf. {e['empfehlung_nr']} · S.{e['seite_pdf']}")
            rep.append(f"- **Frage ({'R' if e['answer'] else 'F'}):** {e['statement']}")
            rep.append(f"- **Wortlaut (App):** {e['leitlinie_wortlaut']}")
            rep.append(f"- **Leitlinie (PDF):** {(e['leitlinie_pdf'][:400] or '— nicht gefunden —')}\n")
    open(os.path.join(ROOT, "qc", "qc-report.md"), "w").write("\n".join(rep))

    icon = {"OK": "✅", "PRUEFEN": "⚠️", "MISMATCH": "❌", "KEINE_BOX": "❔", "KEIN_PDF": "❔"}
    rv = ["# Review-Liste — jede Frage 2× kontrollieren\n",
          "- **Check 1 (Wortlaut ⇄ Leitlinie):** automatisch via `python3 qc/verify.py` (Spalte unten).",
          "- **Check 2 (klinisch/Logik):** manuell — ☐ → ☑, wenn Fachinhalt UND Richtig/Falsch-Wertung gegen die Empfehlung geprüft.\n",
          f"_Letzter Auto-Lauf: {len(log)} Fragen · ✅ {by.get('OK',0)} · ⚠️ {by.get('PRUEFEN',0)} · ❌ {by.get('MISMATCH',0)} · ❔ {by.get('KEINE_BOX',0)+by.get('KEIN_PDF',0)}_\n",
          "Details zu ⚠️/❌ siehe `qc/qc-report.md`.\n"]
    groups = defaultdict(list)
    for e in log:
        groups[(e["leitlinie"], e["kapitel"])].append(e)
    for (ll, kap), items in sorted(groups.items(), key=lambda x: (x[0][0] or "", x[0][1] or "")):
        rv.append(f"\n## {ll} · {kap}  ({len(items)})\n")
        rv.append("| ID | Empf. | S. | R/F | Check 1 | Check 2 |")
        rv.append("|---|---|---|:--:|:--:|:--:|")
        for e in sorted(items, key=lambda x: x["id"]):
            rf = "R" if e["answer"] else "F"
            rv.append(f"| {e['id']} | {e['empfehlung_nr']} | {e['seite_pdf']} | {rf} | {icon[e['check1_auto']['status']]} | ☐ |")
    open(os.path.join(ROOT, "qc", "REVIEW.md"), "w").write("\n".join(rv))

    print(f"\nGESAMT {len(log)} | ✅ OK {by.get('OK',0)} | ⚠️ PRUEFEN {by.get('PRUEFEN',0)} | "
          f"❌ MISMATCH {by.get('MISMATCH',0)} | ❔ KEINE_BOX {by.get('KEINE_BOX',0)} | KEIN_PDF {by.get('KEIN_PDF',0)}")
    print("Geschrieben: qc/qc-log.json, qc/qc-report.md, qc/REVIEW.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
