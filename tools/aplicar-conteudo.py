#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aplica o conteúdo verificado (tools/conteudo/*) aos JSON de public/data.

Fonte única da verdade textual: tools/conteudo/. Este script é idempotente: as imagens são lidas do
JSON existente (e, para os protozoários, de tools/protozoarios_import.json) e os textos são
integralmente gerados a partir das afirmações verificadas.

Uso:  python3 tools/aplicar-conteudo.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from conteudo import nema, plat, proto, extras, refs as refmod  # noqa: E402
from conteudo.cdc_detalhe import EXTRA as CDC_EXTRA  # noqa: E402

DATA = ROOT / "public" / "data"
HOJE = "2026-10-23"

SEC_FIELDS = ("Tamanho", "Morfologia", "Traços", "Doença", "Patogenia", "Clínica", "Ciclo", "Diagnóstico",
              "Tratamento", "Prevenção", "Bancada", "Diferencial", "Taxonomia", "Lâmina")


def by_sec(claims, sec, key=None):
    return [c for c in claims if c["sec"] == sec and (key is None or c["key"] == key)]


def join(cl, sep=" "):
    return sep.join(c["text"] for c in cl) or None


def build_specimen(sp, old_images):
    cl = sp["claims"] + CDC_EXTRA.get(sp["id"], [])
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


SOBRENOME_CONFIRMADO = {"Micael Oliveira", "Elias Barros"}  # nomes completos informados no próprio documento


def proto_images():
    """Lê tools/protozoarios_import.json (gerado de docs/fontes/Laminas_de_Protozoarios.docx).

    Cada imagem vira um registro por espécie. Imagem composta (legenda "De cima para baixo (...)") é um
    único arquivo referenciado por cada espécie que mostra. Crédito: só o que a legenda diz; quando o nome
    não traz sobrenome, o texto avisa "sobrenome a confirmar". Sem autoria na legenda -> "a confirmar".
    """
    imp = json.loads((ROOT / "tools" / "protozoarios_import.json").read_text(encoding="utf-8"))
    nomes = {"entamoeba_histolytica": "Entamoeba histolytica", "giardia_lamblia": "Giardia duodenalis",
             "endolimax_nana": "Endolimax nana", "entamoeba_coli": "Entamoeba coli",
             "chilomastix_mesnili": "Chilomastix mesnili", "blastocystis_sp": "Blastocystis sp.",
             "iodamoeba_buetschlii": "Iodamoeba buetschlii"}
    res = {}
    for im in imp["imagens"]:
        autor = im["autoria_na_legenda"]
        especies = im.get("especies", [im["especie"]])
        composta = len(especies) > 1
        for sp in especies:
            n = len(res.setdefault(sp, [])) + 1
            if autor:
                credit = f"{autor} (autoria indicada na legenda do documento de lâminas)"
                if autor not in SOBRENOME_CONFIRMADO:
                    credit += "; sobrenome a confirmar"
            else:
                credit = "Autoria não informada no documento de origem (a confirmar)"
            cap = f"{im['legenda_docx'].removeprefix('Figura. ').removeprefix('Figura ')}"
            cap += " Identificação conforme a legenda do documento; aumento, coloração e técnica não foram informados."
            if composta:
                cap += " Imagem única com três espécies: a mesma foto aparece em cada ficha."
            if "mesnili" not in im["legenda_docx"] and "Chilomastix" in im["legenda_docx"]:
                cap += " A legenda indica apenas o gênero Chilomastix."
            if "hystolitica" in im["legenda_docx"]:
                cap += " A legenda reúne E. histolytica e E. díspar, que a microscopia não distingue."
            res.setdefault(sp, [])
            res[sp].append({
                "id": f"pz{n:02d}",
                "file": im["arquivo"],
                "width": im["tamanho_final"][0],
                "height": im["tamanho_final"][1],
                "type": "microfotografia",
                "kind": "campo",
                "lamina": None,
                "confidence": "documento",
                "alt": f"Fotografia de lâmina de {nomes[sp]} (legenda do documento de lâminas de protozoários)",
                "caption": cap,
                "credit": credit,
                "license": None,
                "sourceFile": f"Laminas_de_Protozoarios.docx ({im['midia_origem']})",
                "hotspots": [],
                "creditStatus": "informado" if autor else "a-confirmar",
            })
    return res


V4_REFS = {1: "dpdx_tri", 2: "dpdx_asc", 3: "dpdx_hym", 4: "dpdx_taen", 5: "dpdx_giar", 6: "dpdx_intam", 7: "dpdx_art",
           8: "dpdx_ent", 9: "dpdx_blasto", 10: "dpdx_stro", 11: "garcia_2018", 12: "dpdx_chilo", 13: "dpdx_amoeb"}
# Ressalvas do ATLAS sobre legendas do documento (a legenda em si é dos autores e é mantida como escrita).
V4_NOTAS = {
    31: ("Atenção: os detalhes do cisto citados na legenda (6–10 µm, forma de limão, saliência hialina anterior, 1 núcleo) não constam "
         "na página do CDC citada ([12]), que só descreve o trofozoíto; a fonte [11] (Garcia et al., 2018) não foi lida nesta revisão."),
}


def v4_registros():
    """Lê tools/laminas_v4_import.json (gerado de docs/fontes/Laminas_Parasitologia_v4.docx).

    Devolve (por_especie, anexos, artefatos):
      por_especie: id da espécie -> imagens novas (foto + 'detail' = ampliação digital do documento);
      anexos: arquivo já existente no catálogo -> {'detail', 'caption_add'} (foto repetida: não duplica, só anexa a ampliação);
      artefatos: figuras 'Estrutura não identificada' (não são atribuídas a nenhuma espécie).
    Crédito: o documento NÃO informa o autor das fotos. "Lâmina feita/obtida por X" é preparo da lâmina, não autoria da foto.
    """
    imp = json.loads((ROOT / "tools" / "laminas_v4_import.json").read_text(encoding="utf-8"))
    por_esp, anexos, arte = {}, {}, []
    for r in sorted(imp["figuras"], key=lambda x: x["figura"]):
        n = r["figura"]
        limpa = lambda t: re.sub(r"\s*\[[\d,\s]+\]", "", t or "").strip()
        grupo = re.sub(r"\s*\|\s*Objetiva:.*$", "", r["grupo"]).replace("Grupo:", "").strip()
        obj = (r.get("objetiva_legenda") or "").replace("*", "").strip()
        refs = [V4_REFS[k] for k in r["refs_numeros"]]
        partes = [f"Figura {n} do documento de lâminas v4 — {r['identificacao']}.", f"Grupo (conforme o documento): {grupo}.", limpa(r["descricao"]), limpa(r["obs"])]
        cap = " ".join(x for x in partes if x)
        if obj:
            cap += (f" Objetiva estimada: {obj} (estimada pelos autores a partir do tamanho aparente das estruturas; não foi registrada na foto: a confirmar)."
                    " Identificação por morfologia em fotografia, sem micrometria; validar na lâmina original.")
        if n in V4_NOTAS:
            cap += " " + V4_NOTAS[n]
        if r["lamina_preparada_por"]:
            credit = (f"Autoria da foto não informada no documento (a confirmar). Lâmina preparada por {r['lamina_preparada_por']} "
                      "(sobrenome a confirmar), conforme a legenda")
        else:
            credit = "Autoria não informada no documento de origem (a confirmar)"
        detail = {"file": r["arquivo_ampliacao"], "width": r["tamanho_ampliacao"][0], "height": r["tamanho_ampliacao"][1],
                  "label": "Ampliação digital (conforme o documento de lâminas)"}
        if r["foto_ja_no_catalogo"]:
            anexos[r["foto_ja_no_catalogo"]] = {"detail": detail, "caption_add": f" {cap}", "refs": refs}
            continue
        reg = {"id": f"v4f{n:02d}", "file": r["arquivo_foto"], "width": r["tamanho_foto"][0], "height": r["tamanho_foto"][1],
               "type": "microfotografia", "kind": "campo", "lamina": None, "figure": n, "confidence": "documento",
               "alt": f"Fotografia de lâmina: {r['identificacao']} (Figura {n} do documento de lâminas v4)",
               "caption": cap, "credit": credit, "license": None,
               "sourceFile": f"Laminas_Parasitologia_v4.docx ({r['midia_foto']})", "hotspots": [],
               "creditStatus": "a-confirmar", "refs": refs, "detail": detail}
        if r["modulo"] == "artefatos":
            arte.append(reg)
        else:
            por_esp.setdefault(r["especie"], []).append(reg)
    return por_esp, anexos, arte


def main():
    modulos = json.loads((DATA / "modulos.json").read_text(encoding="utf-8"))
    ordem_proto = ["entamoeba_histolytica", "entamoeba_coli", "endolimax_nana", "giardia_lamblia", "chilomastix_mesnili",
                   "blastocystis_sp", "iodamoeba_buetschlii"]
    sp_proto = sorted(proto.SPECIES, key=lambda s: ordem_proto.index(s["id"]))
    all_sp = {"nematelmintos": nema.SPECIES, "platelmintos": list(plat.SPECIES), "protozoarios": sp_proto}
    pimgs = proto_images()
    v4_esp, v4_anexos, v4_arte = v4_registros()
    totals = {"claims": 0, "removed": 0}
    for mod, species in all_sp.items():
        f = DATA / "modulos" / f"{mod}.json"
        cur = json.loads(f.read_text(encoding="utf-8"))
        cur_imgs = {s["id"]: s["images"] for s in cur["specimens"]}
        out = []
        for sp in species:
            if mod == "protozoarios":
                # só as fotografias do documento de lâminas; as externas sem crédito foram removidas em 06/11/2026
                imgs = list(pimgs.get(sp["id"], []))
            else:
                # idempotente: as figuras v4 são sempre reconstruídas do JSON do importador
                imgs = [i for i in cur_imgs[sp["id"]] if not str(i.get("id", "")).startswith("v4f")]
            imgs = imgs + v4_esp.get(sp["id"], [])
            for im in imgs:
                if im["file"] in v4_anexos and "detail" not in im:
                    ax = v4_anexos[im["file"]]
                    im["detail"] = ax["detail"]; im["refs"] = ax["refs"]
                    im["caption"] = (im.get("caption") or "") + ax["caption_add"]
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
            "Blastocystis sp. e Iodamoeba buetschlii (incluídas em 06/11/2026): taxonomia, morfologia e doença vêm só de páginas do CDC lidas em 06/11/2026; ciclo, diagnóstico e tratamento NÃO foram revisados e não são exibidos",
            "taxid da Iodamoeba buetschlii no NCBI: não confirmado (consulta bloqueada)",
            "Lâminas de protozoários atualizadas em 06/11/2026 a partir do documento de 25 imagens; a identificação das espécies segue as legendas do documento",
            "Lâminas do documento v4 (25/11/2026): 32 figuras; as legendas são dos autores e a identificação não foi confirmada de forma independente; só a legenda da Figura 31 (Chilomastix) foi conferida contra a página do CDC citada — os detalhes do cisto não constam nela; a fonte [11] (Garcia et al., 2018) não foi lida",
            "Autoria das fotos do documento v4 não informada; 'Lâmina feita/obtida por' (Indira, Maria Eduarda) é preparo da lâmina, com sobrenome a confirmar",
        ],
        "sourceAccessNote": ("Fontes lidas por ferramentas automáticas (leitor de páginas e PubMed). Onde só o resumo ou trechos foram lidos, isso consta em "
                             "'acesso nesta revisão' de cada referência. Documento da OMS (Bench Aids) com acesso indisponível."),
    }
    (DATA / "referencias.json").write_text(json.dumps(rf, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # artefatos e quiz
    art = dict(extras.ARTEFATOS)
    art["naoIdentificadas"] = {
        "titulo": "Estruturas sem identificação segura",
        "aviso": ("Duas fotografias do documento de lâminas v4 foram classificadas pelos próprios autores como estrutura não identificada "
                  "(grupo: indeterminado). O atlas não afirma que sejam artefatos nem parasitos: servem para treinar o olhar e a cautela. "
                  "A descrição vem da legenda do documento, que cita a página de artefatos do CDC; a identificação precisa ser validada na lâmina original."),
        "fotos": v4_arte,
    }
    (DATA / "artefatos.json").write_text(json.dumps(art, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    quiz = extras.build_quiz()
    (DATA / "quiz.json").write_text(json.dumps(quiz, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("species claims:", totals, "| quiz:", len(quiz), "| refs:", len(rf["items"]))


if __name__ == "__main__":
    main()
