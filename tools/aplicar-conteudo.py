#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aplica o conteúdo verificado (tools/conteudo/*) aos JSON de public/data.

Fonte única da verdade textual: tools/conteudo/. Este script é idempotente: as imagens são lidas do
JSON existente (e, para os protozoários, de tools/protozoarios_import.json) e os textos são
integralmente gerados a partir das afirmações verificadas.

Uso:  python3 tools/aplicar-conteudo.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from conteudo import nema, plat, proto, extras, refs as refmod  # noqa: E402

DATA = ROOT / "public" / "data"
HOJE = "2026-10-23"

SEC_FIELDS = ("Tamanho", "Morfologia", "Traços", "Doença", "Patogenia", "Clínica", "Ciclo", "Diagnóstico",
              "Tratamento", "Prevenção", "Bancada", "Diferencial", "Taxonomia", "Lâmina")


def by_sec(claims, sec, key=None):
    return [c for c in claims if c["sec"] == sec and (key is None or c["key"] == key)]


def join(cl, sep=" "):
    return sep.join(c["text"] for c in cl) or None


def build_specimen(sp, old_images):
    cl = sp["claims"]
    for c in cl:
        assert c["sec"] in SEC_FIELDS, (sp["id"], c["sec"])
    tax = dict(sp["tax"])
    taxonomy = {k: tax[k] for k in ("phylum", "class", "order", "family", "genus", "species") if k in tax}
    taxonomy["note"] = tax.get("nota")
    taxonomy["ncbi"] = tax.get("ncbi")
    taxonomy["source"] = "ncbi_tax"

    def one(sec, key):
        l = by_sec(cl, sec, key)
        return l[0]["text"] if l else None

    def many(sec, key):
        return [c["text"] for c in by_sec(cl, sec, key)]

    gold = join(by_sec(cl, "Diagnóstico", "gold"))
    obs = join(by_sec(cl, "Diagnóstico", "obs"))
    out = {
        "id": sp["id"],
        "commonName": sp["commonName"],
        "scientificName": sp["scientificName"],
        "taxonomy": taxonomy,
        "category": sp["category"],
        "evolutionaryStage": sp["stage"],
        "status": "revisar" if sp.get("revisao") else "publicado",
        "approxSizeMicrons": join(by_sec(cl, "Tamanho"), " · "),
        "morphologyDescription": join(by_sec(cl, "Morfologia")) or "",
        "keyDiagnosticFeatures": [c["text"] for c in by_sec(cl, "Traços")],
        "disease": join(by_sec(cl, "Doença")),
        "pathogenesis": join(by_sec(cl, "Patogenia")),
        "clinicalManifestations": [c["text"] for c in by_sec(cl, "Clínica")],
        "diagnosticMethods": {
            "goldStandard": gold,
            "alternatives": many("Diagnóstico", "alt"),
            "sampleType": join(by_sec(cl, "Diagnóstico", "sample")),
            "technicalObservation": obs,
        },
        "transmissionAndCycle": {
            "transmissionRoute": one("Ciclo", "route"),
            "infectiveForm": one("Ciclo", "infective"),
            "diagnosticForm": one("Ciclo", "diagnostic"),
            "habitat": one("Ciclo", "habitat"),
            "cycleType": one("Ciclo", "cycleType"),
        },
        "treatment": [c["text"] for c in by_sec(cl, "Tratamento")],
        "prophylaxis": [c["text"] for c in by_sec(cl, "Prevenção")],
        "benchTip": join(by_sec(cl, "Bancada")),
        "differentialDiagnosis": join(by_sec(cl, "Diferencial")),
        "images": old_images,
    }
    if sp.get("revisao"):
        out["reviewNote"] = sp["revisao"]
    # lista completa de afirmações verificadas (inclui taxonomia e observações de lâmina)
    out["verification"] = [
        {"id": f"{sp['id']}#{i + 1:02d}", "section": c["sec"], "text": c["text"], "status": c["st"],
         "refs": c["refs"], "evidence": c["ev"], "note": c["nota"], **({"before": c["antes"]} if c["antes"] else {})}
        for i, c in enumerate(cl)
    ]
    out["removed"] = [{"before": r["antes"], "reason": r["motivo"], "field": r["campo"]} for r in sp["removidos"]]
    # remove chaves nulas para manter o JSON enxuto (o app trata ausência como null)
    for k in list(out):
        if out[k] is None:
            del out[k]
    for k in list(out["diagnosticMethods"]):
        if out["diagnosticMethods"][k] in (None, []):
            del out["diagnosticMethods"][k]
    for k in list(out["transmissionAndCycle"]):
        if out["transmissionAndCycle"][k] is None:
            del out["transmissionAndCycle"][k]
    return out


def proto_images():
    imp = json.loads((ROOT / "tools" / "protozoarios_import.json").read_text(encoding="utf-8"))
    nomes = {"entamoeba_histolytica": "Entamoeba histolytica", "giardia_lamblia": "Giardia duodenalis",
             "endolimax_nana": "Endolimax nana", "entamoeba_coli": "Entamoeba coli", "chilomastix_mesnili": "Chilomastix mesnili"}
    res = {}
    for im in imp["imagens"]:
        sp = im["especie"]
        n = len(res.setdefault(sp, [])) + 1
        autor = im["autoria_na_legenda"]
        entry = {
            "id": f"pz{n:02d}",
            "file": im["arquivo"],
            "width": im["tamanho_final"][0],
            "height": im["tamanho_final"][1],
            "type": "microfotografia",
            "kind": "campo",
            "lamina": None,
            "confidence": "documento",
            "alt": f"Fotografia de lâmina de {nomes[sp]} (legenda do documento de lâminas de protozoários)",
            "caption": f"{im['legenda_docx']} Identificação conforme a legenda do documento; aumento, coloração e técnica não foram informados.",
            "credit": (f"{autor} (autora da foto; sobrenome a confirmar) — documento de lâminas de Protozoários"
                       if autor else "Autoria não informada no documento de origem (a confirmar)"),
            "license": None,
            "sourceFile": f"Laminas_de_Protozoarios.docx ({im['midia_origem']})",
            "hotspots": [],
            "creditStatus": "informado" if autor else "a-confirmar",
        }
        res[sp].append(entry)
    return res


def main():
    modulos = json.loads((DATA / "modulos.json").read_text(encoding="utf-8"))
    ordem_proto = ["entamoeba_histolytica", "entamoeba_coli", "endolimax_nana", "giardia_lamblia", "chilomastix_mesnili"]
    sp_proto = sorted(proto.SPECIES, key=lambda s: ordem_proto.index(s["id"]))
    all_sp = {"nematelmintos": nema.SPECIES, "platelmintos": list(plat.SPECIES), "protozoarios": sp_proto}
    pimgs = proto_images()
    totals = {"claims": 0, "removed": 0}
    for mod, species in all_sp.items():
        f = DATA / "modulos" / f"{mod}.json"
        cur = json.loads(f.read_text(encoding="utf-8"))
        cur_imgs = {s["id"]: s["images"] for s in cur["specimens"]}
        out = []
        for sp in species:
            if mod == "protozoarios":
                imgs = list(pimgs.get(sp["id"], []))
                # mantém imagens externas herdadas (sem crédito) ao final
                imgs += [i for i in cur_imgs.get(sp["id"], []) if i.get("type") == "externa"]
            else:
                imgs = cur_imgs[sp["id"]]
            s = build_specimen(sp, imgs)
            totals["claims"] += len(s["verification"])
            totals["removed"] += len(s["removed"])
            out.append(s)
        f.write_text(json.dumps({"specimens": out}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(mod, [s["id"] for s in out])

    # módulos e site
    site = {k: v for k, v in extras.SITE.items()}
    modulos["site"] = site
    for m in modulos["modules"]:
        m.update(extras.MODULES.get(m["id"], {}))
    (DATA / "modulos.json").write_text(json.dumps(modulos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # referências (acrescenta/atualiza as novas; mantém as antigas)
    rf = json.loads((DATA / "referencias.json").read_text(encoding="utf-8"))
    items = {i["id"]: i for i in rf["items"]}
    for r in refmod.NEW_REFS:
        items[r["id"]] = r
    rf["items"] = list(items.values())
    rf["review"] = {
        "reviewedOn": HOJE,
        "status": "conferido-na-literatura",
        "scope": ("Todas as afirmações científicas das fichas de espécie (morfologia, tamanhos, ciclo, patogenia, clínica, diagnóstico, "
                  "tratamento, prevenção, taxonomia), o banco de questões e o guia de artefatos foram refeitos a partir de fontes lidas "
                  "em 23/10/2026; os protocolos foram conferidos em 17/10/2026. Cada afirmação traz status (confirmado, corrigido, ressalva "
                  "ou observação), referências e o trecho-evidência. O que não pôde ser sustentado foi retirado e consta na lista de removidos."),
        "notValidation": ("Isto é uma conferência bibliográfica, não uma validação analítica nem aconselhamento clínico. As citações literais em inglês "
                          "são as devolvidas por um leitor automático de páginas (que extrai trechos): recomenda-se conferir na fonte antes de "
                          "citar. Doses e esquemas terapêuticos não são reproduzidos. Antes de uso em rotina ou diagnóstico, o procedimento precisa "
                          "ser adotado e validado no POP do laboratório."),
        "notReviewed": [
            "Livros-texto da bibliografia geral da disciplina (listados em Informações) — não consultados",
            "Identificação das espécies nas fotografias das lâminas — feita pelos autores; não foi confirmada de forma independente",
            "Artigos originais dos métodos clássicos (Lutz, Hoffman, Faust, Graham, Rugai) — não localizados",
        ],
        "sourceAccessNote": ("Fontes lidas por ferramentas automáticas (leitor de páginas e PubMed). Onde só o resumo ou trechos foram lidos, isso consta em "
                             "'acesso nesta revisão' de cada referência. Documento da OMS (Bench Aids) com acesso indisponível."),
    }
    (DATA / "referencias.json").write_text(json.dumps(rf, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # artefatos e quiz
    (DATA / "artefatos.json").write_text(json.dumps(extras.ARTEFATOS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    quiz = extras.build_quiz()
    (DATA / "quiz.json").write_text(json.dumps(quiz, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("species claims:", totals, "| quiz:", len(quiz), "| refs:", len(rf["items"]))


if __name__ == "__main__":
    main()
