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
    "magen": "leitlinien/magen-v3.1.pdf",
    "oesophagus": "leitlinien/oesophagus-v4.0.pdf",
    "schilddruese": "leitlinien/schilddruese-v1.0.pdf",
    "hcc": "leitlinien/hcc-v5.pdf",
    "analkarzinom": "leitlinien/analkarzinom-v1.1.pdf",
    "colitis_ulcerosa": "leitlinien/colitis-ulcerosa-v7.0.pdf",
    "morbus_crohn": "leitlinien/morbus-crohn-v4.0.pdf",
    "divertikulitis": "leitlinien/divertikulitis-v3.0.pdf",
    "haemorrhoiden": "leitlinien/haemorrhoiden-v2019.pdf",
    "pilonidalsinus": "leitlinien/pilonidalsinus-v3.0.pdf",
    "bariatrie": "leitlinien/bariatrie-v2018.pdf",
    "gist": "leitlinien/weichgewebesarkome-v1.1.pdf",
}
OK_T, PRUEF_T = 0.85, 0.65

HEAD = re.compile(r"^\s*(\d{1,2}\.\d{1,2}[a-z]?)\.?\s+(Evidenz- und konsensbasierte Empfehlung|Evidenz- und konsensbasiertes Statement|Evidenzbasierte Empfehlung|Konsensbasierte Empfehlung|Evidenzbasiertes Statement|Konsensbasiertes Statement|Statement)\b")
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
    """{empfehlung_nr: {'rec': Empfehlungstext bis 'Hintergrund',
                        'region': Empfehlung + Hintergrund bis zur nächsten Box}}."""
    lines = text.split("\n")
    starts = [(i, HEAD.match(l).group(1)) for i, l in enumerate(lines) if HEAD.match(l)]
    out = {}
    for k, (i, nr) in enumerate(starts):
        end = starts[k + 1][0] if k + 1 < len(starts) else min(i + 120, len(lines))
        rec, region, in_rec = [], [], True
        for bl in lines[i + 1:end]:
            if not bl.strip():
                continue
            if bl.strip().startswith("Hintergrund"):
                in_rec = False
                continue
            c = clean_line(bl)
            if not c:
                continue
            region.append(c)
            if in_rec:
                rec.append(c)
        # Silbentrennung am Zeilenende reparieren: "wer- den"/"Nach- sorge" -> "werden"/"Nachsorge"
        dehyph = lambda t: re.sub(r"(?<=\w)-\s+(?=\w)", "", re.sub(r"\s+", " ", t))
        rec_t = dehyph(" ".join(rec)).strip()
        reg_t = dehyph(" ".join(region)).strip()
        if nr not in out or len(rec_t) > len(out[nr]["rec"]):
            out[nr] = {"rec": rec_t, "region": reg_t}
    return out


def verbatim_in(wortlaut, region_norm, k=8):
    """True, wenn eine k-Wort-Kette des Wortlauts wörtlich im (norm.) Abschnitt steht."""
    words = WORD.findall((wortlaut or "").lower())
    if len(words) < k:
        s = " ".join(words)
        return bool(s) and s in region_norm
    for j in range(0, len(words) - k + 1):
        if " ".join(words[j:j + k]) in region_norm:
            return True
    return False


# Zweispaltige Journal-Leitlinien (Z Gastroenterol): vor dem Korpus entzerren.
JOURNAL = {"morbus_crohn", "divertikulitis"}

def decolumnize(text):
    """Zweispalten-PDF (pdftotext -layout) pro Seite in Lesereihenfolge bringen."""
    out = []
    for page in text.split("\f"):
        lines = page.split("\n")
        width = max((len(l) for l in lines), default=0)
        if width < 40:
            out.extend(lines); continue
        dens = [0] * (width + 1)
        for l in lines:
            for i, ch in enumerate(l):
                if ch != " " and i <= width:
                    dens[i] += 1
        lo, hi = int(width * 0.33), int(width * 0.66)
        best_start, best_len, cur_start, cur_len = None, 0, None, 0
        for i in range(lo, hi + 1):
            if dens[i] <= 1:
                if cur_start is None: cur_start = i
                cur_len += 1
                if cur_len > best_len: best_len, best_start = cur_len, cur_start
            else:
                cur_start, cur_len = None, 0
        if best_start is None or best_len < 3:
            out.extend(lines); continue
        gutter = best_start + best_len // 2
        left = [l[:gutter].rstrip() for l in lines if l[:gutter].strip()]
        right = [l[gutter:].rstrip() for l in lines if l[gutter:].strip()]
        out.extend(left); out.append(""); out.extend(right); out.append("")
    return "\n".join(out)


# Boxen mit rechter Meta-Spalte (Grad/Konsens neben dem Text, z. B. Bariatrie):
# rechte Spalte vor dem Korpus abtrennen, sonst landet sie mitten im Wortlaut.
RIGHTCOL = {"bariatrie"}
RIGHTMETA = re.compile(r"^(Empfehlungsgrad|Expertenkonsens|Evidenz(grad|level)|Starker Konsens|starker Konsens|Konsens|Mehrheitliche|Mehrheitlicher|Dissens|Kein Konsens|EK|[ABC0]|\d[ab]?)\b")

def strip_rightmeta(line):
    parts = re.split(r" {6,}", line)
    while len(parts) > 1 and RIGHTMETA.match(parts[-1].strip()):
        parts.pop()
    return "    ".join(parts)


def toks(s):
    return set(w for w in WORD.findall((s or "").lower()) if len(w) >= 4)


def norm(s):
    return " ".join(WORD.findall((s or "").lower()))


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
    boxes_by, corpus_by = {}, {}
    for ll, pdf in PDFS.items():
        t = pdf_to_text(pdf)
        boxes_by[ll] = parse_boxes(t) if t else None
        if t:
            base = decolumnize(t) if ll in JOURNAL else t   # Journal-PDFs entzerren
            if ll in RIGHTCOL:                               # rechte Meta-Spalte abtrennen
                base = "\n".join(strip_rightmeta(l) for l in base.split("\n"))
            base = re.sub(r"(?<=\w)-\n\s*(?=\w)", "", base)  # Silbentrennung über Zeilen
            cleaned = " ".join(c for c in (clean_line(l) for l in base.split("\n")) if c)
            # Silbentrennung verschmelzen, aber Aufzählungen (X- und/oder/bzw Y) bewahren
            corpus_by[ll] = norm(re.sub(r"(?<=\w)-\s+(?!(?:und|oder|bzw|sowie|beziehungsweise)\b)(?=\w)", "", cleaned))
        else:
            corpus_by[ll] = None
        print(f"  {ll}: {str(len(boxes_by[ll])) + ' Empfehlungs-Boxen' if t else 'PDF fehlt'}")

    log = []
    for q in questions:
        ll = (q.get("leitlinie") or {}).get("id")
        boxes = boxes_by.get(ll)
        box = get_box(boxes, q.get("empfehlung_nr")) if boxes else None
        wl = q.get("leitlinie_wortlaut", "")
        wt = toks(wl)
        cov = (len(wt & toks(box["rec"])) / len(wt)) if (box and wt) else 0.0
        vb = verbatim_in(wl, norm(box["region"])) if box else False
        if boxes is None:
            st, via = "KEIN_PDF", "-"
        elif box is None:
            # andere Leitlinien-Formate (z. B. DGVS): kein Onkologie-Box-Kopf ->
            # Wortlaut verbatim (8-Gramm) im gesamten Leitlinientext suchen
            if corpus_by.get(ll) and verbatim_in(wl, corpus_by[ll]):
                st, via = "OK", "Leitlinie"
            else:
                st, via = "KEINE_BOX", "-"
        elif cov >= OK_T:
            st, via = "OK", "Empfehlung"
        elif vb:
            st, via = "OK", "Hintergrund"   # wörtlich im Hintergrund-Text der Empfehlung belegt
        elif corpus_by.get(ll) and verbatim_in(wl, corpus_by[ll]):
            st, via = "OK", "Leitlinie"     # wörtlich an anderer Stelle der Leitlinie belegt
        elif cov >= PRUEF_T:
            st, via = "PRUEFEN", "-"
        else:
            st, via = "MISMATCH", "-"
        log.append({
            "id": q["id"], "leitlinie": ll, "empfehlung_nr": q.get("empfehlung_nr"),
            "kapitel": q.get("kapitel"), "seite_pdf": q.get("seite_pdf"), "answer": q.get("answer"),
            "check1_auto": {"status": st, "coverage": round(cov, 2), "via": via},
            "statement": q.get("statement"),
            "leitlinie_wortlaut": wl,
            "leitlinie_pdf": (box["rec"] if box else ""),
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
