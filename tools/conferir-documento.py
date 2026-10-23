#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Confere que o DOCX (e o PDF, se existir) contém TODO o conteúdo dos JSON, e que o app usa os mesmos JSON.

Falha (código 1) se algum texto, crédito, referência, afirmação ou pergunta do JSON não estiver no documento,
ou se os dados embutidos no app diferirem (SHA-256) dos de public/data.
Uso:  python3 tools/conferir-documento.py
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from docx import Document

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "public" / "data"
DOCX = ROOT / "docs" / "Atlas_Parasitologia_Documento_de_Revisao.docx"
PDF = DOCX.with_suffix(".pdf")


def norm(s):
    return re.sub(r"\s+", " ", str(s)).strip()


def docx_text(path):
    d = Document(str(path))
    parts = [p.text for p in d.paragraphs]
    for t in d.tables:
        for row in t.rows:
            for c in row.cells:
                parts.append(c.text)
    return norm(" ".join(parts))


def J(p):
    return json.loads((DATA / p).read_text(encoding="utf-8"))


def collect():
    """Lista (rótulo, texto) de tudo o que deve aparecer no documento."""
    items = []
    mods = J("modulos.json")
    site = mods["site"]
    for k in ("title", "institution", "course"):
        items.append((f"site.{k}", site[k]))
    for p in site["developers"] + [site["advisor"]]:
        items += [("equipe", p["name"]), ("equipe", p["role"])]
    items += [("site.referencias", r) for r in site["references"]] + [("site.referencesNote", site["referencesNote"])]
    for m in mods["modules"]:
        for s in J(f"modulos/{m['id']}.json")["specimens"]:
            sid = s["id"]
            for k in ("commonName", "scientificName", "category", "evolutionaryStage", "approxSizeMicrons", "morphologyDescription",
                      "disease", "pathogenesis", "benchTip", "differentialDiagnosis", "reviewNote"):
                if s.get(k):
                    items.append((f"{sid}.{k}", s[k]))
            for k in ("keyDiagnosticFeatures", "clinicalManifestations", "treatment", "prophylaxis"):
                items += [(f"{sid}.{k}", x) for x in s.get(k, [])]
            d = s.get("diagnosticMethods", {})
            for k in ("goldStandard", "sampleType", "technicalObservation"):
                if d.get(k):
                    items.append((f"{sid}.diag.{k}", d[k]))
            items += [(f"{sid}.diag.alt", x) for x in d.get("alternatives", [])]
            for k, v in s.get("transmissionAndCycle", {}).items():
                items.append((f"{sid}.ciclo.{k}", v))
            for k, v in s["taxonomy"].items():
                if v:
                    items.append((f"{sid}.tax.{k}", v))
            for im in s["images"]:
                for k in ("id", "file", "caption", "alt", "credit", "sourceFile", "date"):
                    if im.get(k):
                        items.append((f"{sid}.img.{im['id']}.{k}", im[k]))
            for v in s["verification"]:
                for k in ("id", "text", "evidence", "note", "before"):
                    if v.get(k):
                        items.append((f"{v['id']}.{k}", v[k]))
            for r in s.get("removed", []):
                items += [(f"{sid}.removido", r["before"]), (f"{sid}.removido.motivo", r["reason"])]
    for p in J("protocolos.json"):
        pid = p["id"]
        for k in ("title", "popularName", "indication", "principle"):
            items.append((f"{pid}.{k}", p[k]))
        for k in ("reagentsAndMaterials", "stepByStep", "advantages", "limitations", "keyParasitesDetected"):
            items += [(f"{pid}.{k}", x) for x in p.get(k, [])]
        items += [(f"{pid}.evidence", e["text"]) for e in p.get("evidence", [])]
        for v in p["verification"]:
            items += [(f"{pid}.ver", v["item"]), (f"{pid}.ver.nota", v["note"])]
    a = J("artefatos.json")
    items.append(("artefatos.dica", a["dica"]))
    for it in a["itens"]:
        for k in ("nome", "confundidaCom", "comoDiferenciar", "evidencia"):
            if it.get(k):
                items.append((f"artefato.{k}", it[k]))
    for r in a.get("removidos", []):
        items += [("artefato.removido", r["antes"]), ("artefato.removido.motivo", r["motivo"])]
    for q in J("quiz.json"):
        for k in ("id", "title", "question", "explanation", "context", "fieldPearl"):
            if q.get(k):
                items.append((f"quiz.{q['id']}.{k}", q[k]))
        items += [(f"quiz.{q['id']}.opt", o) for o in q["options"]]
    refs = J("referencias.json")
    items += [(f"ref.{r['id']}", r["citation"]) for r in refs["items"]]
    items += [(f"ref.{r['id']}.id", r["id"]) for r in refs["items"]]
    items += [(f"ref.{r['id']}.acesso", r["access"]) for r in refs["items"] if r.get("access")]
    rv = refs["review"]
    items += [("review.scope", rv["scope"]), ("review.notValidation", rv["notValidation"]), ("review.sourceAccessNote", rv["sourceAccessNote"])]
    items += [("review.notReviewed", x) for x in rv["notReviewed"]]
    return items


def main():
    if not DOCX.exists():
        sys.exit("DOCX não encontrado: rode tools/gerar-documento.py")
    txt = docx_text(DOCX)
    items = collect()
    missing = [(l, t) for l, t in items if norm(t) not in txt]
    print(f"DOCX: {len(items)} trechos do JSON conferidos; ausentes: {len(missing)}")
    for l, t in missing[:20]:
        print("  AUSENTE", l, "→", norm(t)[:90])
    bad = len(missing)
    if PDF.exists():
        pdf = norm(subprocess.run(["pdftotext", "-raw", str(PDF), "-"], capture_output=True, text=True).stdout)
        pdfc = pdf.replace(" ", "")
        miss_pdf = [(l, t) for l, t in items if norm(t).replace(" ", "") not in pdfc and len(norm(t)) > 3]
        print(f"PDF : ausentes {len(miss_pdf)} (quebras de linha/hífen na diagramação podem gerar falsos positivos)")
        for l, t in miss_pdf[:8]:
            print("  ?", l, "→", norm(t)[:80])
    # app × site: os JSON embutidos no app devem ser idênticos aos de public/data
    man = json.loads((ROOT / "flutter_app" / "assets" / "data" / "manifest.json").read_text(encoding="utf-8"))
    diff = 0
    for f in sorted(DATA.rglob("*.json")):
        rel = f.relative_to(DATA)
        if rel.name == "manifest.json":
            continue
        app = ROOT / "flutter_app" / "assets" / "data" / rel
        if not app.exists():
            print("  app sem arquivo:", rel)
            diff += 1
        elif hashlib.sha256(app.read_bytes()).hexdigest() != hashlib.sha256(f.read_bytes()).hexdigest():
            print("  app ≠ site:", rel)
            diff += 1
    print(f"App × site: {diff} divergência(s) (manifesto: {man['fileCount']} arquivos)")
    sys.exit(1 if bad or diff else 0)


if __name__ == "__main__":
    main()
