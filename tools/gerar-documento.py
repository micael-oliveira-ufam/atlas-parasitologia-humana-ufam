#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera o Documento de Revisão (DOCX) a partir dos JSON de public/data — a mesma fonte do site e do app.

O documento NÃO tem conteúdo próprio: tudo o que ele mostra vem dos JSON; por isso app, site e documento
concordam por construção. A conferência cruzada é feita por tools/conferir-documento.py.

Uso:  python3 tools/gerar-documento.py            (gera o DOCX em docs/)
      soffice --headless --convert-to pdf --outdir docs docs/Atlas_Parasitologia_Documento_de_Revisao.docx
"""
import hashlib
import json
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "public" / "data"
IMG = ROOT / "public" / "assets" / "img"
OUT = ROOT / "docs" / "Atlas_Parasitologia_Documento_de_Revisao.docx"

TEAL = RGBColor(0x0F, 0x76, 0x6E)
ST_COLOR = {"confirmado": "DFF3E4", "corrigido": "FDF0C8", "ressalva": "FBD9DC", "observacao": "E6EEF0", "removido": "FBD9DC"}
ST_LABEL = {"confirmado": "Confirmado", "corrigido": "Corrigido", "ressalva": "Ressalva", "observacao": "Observação da lâmina", "removido": "Removido"}
CONF_LABEL = {"confirmada": "confirmada pelo autor", "alta": "alta confiança", "media": "média (a confirmar)",
              "documento": "conforme legenda do documento de origem"}


def J(p):
    return json.loads((DATA / p).read_text(encoding="utf-8"))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def shade(cell, hex_):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_)
    tcPr.append(shd)


def repeat_header(row):
    trPr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:tblHeader")
    el.set(qn("w:val"), "true")
    trPr.append(el)


def no_split(row):
    trPr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:cantSplit")
    el.set(qn("w:val"), "true")
    trPr.append(el)


def add_field(par, instr):
    r = par.add_run()
    for t, txt in (("begin", None), (None, instr), ("end", None)):
        if t:
            e = OxmlElement("w:fldChar")
            e.set(qn("w:fldCharType"), t)
        else:
            e = OxmlElement("w:instrText")
            e.set(qn("xml:space"), "preserve")
            e.text = txt
        r._r.append(e)


class Doc:
    def __init__(self):
        self.d = Document()
        s = self.d.sections[0]
        s.page_width, s.page_height = Cm(21), Cm(29.7)
        s.left_margin = s.right_margin = Cm(1.8)
        s.top_margin = s.bottom_margin = Cm(1.8)
        st = self.d.styles["Normal"]
        st.font.name = "Calibri"
        st.font.size = Pt(10.5)
        st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
        for n, sz in (("Heading 1", 18), ("Heading 2", 14), ("Heading 3", 12)):
            h = self.d.styles[n]
            h.font.name = "Calibri"
            h.font.size = Pt(sz)
            h.font.color.rgb = TEAL
            h.font.bold = True
        fp = s.footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        fp.add_run("Atlas de Parasitologia Humana — Documento de Revisão — página ").font.size = Pt(8)
        add_field(fp, "PAGE")

    def h(self, text, lvl=1):
        return self.d.add_heading(text, level=lvl)

    def p(self, text="", bold=False, italic=False, size=None, color=None, align=None, space=4):
        par = self.d.add_paragraph()
        r = par.add_run(text)
        r.bold, r.italic = bold, italic
        if size:
            r.font.size = Pt(size)
        if color:
            r.font.color.rgb = color
        if align:
            par.alignment = align
        par.paragraph_format.space_after = Pt(space)
        return par

    def kv(self, k, v):
        if v in (None, "", []):
            return
        par = self.d.add_paragraph()
        a = par.add_run(f"{k}: ")
        a.bold = True
        par.add_run(str(v))
        par.paragraph_format.space_after = Pt(2)

    def bullets(self, items):
        for it in items or []:
            par = self.d.add_paragraph(style="List Bullet")
            par.add_run(str(it))
            par.paragraph_format.space_after = Pt(1)

    def numbered(self, items):
        for i, it in enumerate(items or [], 1):
            par = self.d.add_paragraph()
            par.add_run(f"{i}. ").bold = True
            par.add_run(str(it))
            par.paragraph_format.left_indent = Cm(0.6)
            par.paragraph_format.first_line_indent = Cm(-0.6)
            par.paragraph_format.space_after = Pt(1)

    def table(self, header, rows, widths, size=8, shades=None):
        t = self.d.add_table(rows=1, cols=len(header))
        t.style = "Table Grid"
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False
        for i, hd in enumerate(header):
            c = t.rows[0].cells[i]
            c.text = ""
            r = c.paragraphs[0].add_run(hd)
            r.bold = True
            r.font.size = Pt(size)
            shade(c, "CFE8E4")
        repeat_header(t.rows[0])
        for ri, row in enumerate(rows):
            cells = t.add_row().cells
            no_split(t.rows[-1])
            for i, v in enumerate(row):
                cells[i].text = ""
                par = cells[i].paragraphs[0]
                par.paragraph_format.space_after = Pt(0)
                run = par.add_run("" if v is None else str(v))
                run.font.size = Pt(size)
                if shades and shades[ri] and i == shades[ri][0]:
                    shade(cells[i], shades[ri][1])
        tblPr = t._tbl.tblPr
        lay = OxmlElement("w:tblLayout")
        lay.set(qn("w:type"), "fixed")
        tblPr.append(lay)
        for i, w in enumerate(widths):
            t.columns[i].width = Cm(w)
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(w)
        self.d.add_paragraph().paragraph_format.space_after = Pt(2)
        return t

    def pagebreak(self):
        self.d.add_page_break()


def main():
    mods = J("modulos.json")
    site = mods["site"]
    refs = J("referencias.json")
    ritems = refs["items"]
    rmap = {r["id"]: r for r in ritems}
    short = lambda i: rmap[i]["short"] if i in rmap else i
    quiz = J("quiz.json")
    arte = J("artefatos.json")
    prot = J("protocolos.json")
    manifest_p = ROOT / "flutter_app" / "assets" / "data" / "manifest.json"
    manifest = json.loads(manifest_p.read_text(encoding="utf-8")) if manifest_p.exists() else None
    review = refs["review"]

    specs = []
    for m in sorted(mods["modules"], key=lambda x: x["order"]):
        for s in J(f"modulos/{m['id']}.json")["specimens"]:
            specs.append((m, s))
    all_claims = [c for _, s in specs for c in s["verification"]]
    n_st = lambda st: sum(1 for c in all_claims if c["status"] == st)
    n_removed = sum(len(s.get("removed", [])) for _, s in specs)
    n_img = sum(len(s["images"]) for _, s in specs)

    D = Doc()

    # ---------------- capa ----------------
    seal = ROOT / "public" / "assets" / "img" / "brand" / "ufam_brasao.png"
    if seal.exists():
        par = D.d.add_paragraph()
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par.add_run().add_picture(str(seal), width=Cm(3.6))
    D.p(site["institution"], bold=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER)
    D.p(site["course"], size=11, align=WD_ALIGN_PARAGRAPH.CENTER)
    D.p("", space=18)
    D.p(site["title"], bold=True, size=24, color=TEAL, align=WD_ALIGN_PARAGRAPH.CENTER)
    D.p("Documento de revisão e correção: lâminas, descrições, metodologias, fontes e verificação afirmação a afirmação",
        size=13, align=WD_ALIGN_PARAGRAPH.CENTER)
    D.p("", space=14)
    D.p("Desenvolvedores", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space=2)
    for p_ in site["developers"]:
        D.p(f"{p_['name']} — {p_['role']}", align=WD_ALIGN_PARAGRAPH.CENTER, space=1)
    D.p("", space=6)
    D.p("Orientação", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space=2)
    D.p(f"{site['advisor']['name']} — {site['advisor']['role']}", align=WD_ALIGN_PARAGRAPH.CENTER)
    D.p("", space=14)
    D.p(f"Data da revisão bibliográfica: {review['reviewedOn'][8:10]}/{review['reviewedOn'][5:7]}/{review['reviewedOn'][:4]}",
        align=WD_ALIGN_PARAGRAPH.CENTER, space=1)
    D.p("Documento gerado automaticamente a partir dos mesmos arquivos de dados do site e do aplicativo (tools/gerar-documento.py).",
        italic=True, size=9, align=WD_ALIGN_PARAGRAPH.CENTER)
    D.pagebreak()

    # ---------------- 1. escopo e metodologia da revisão ----------------
    D.h("1. Escopo, método e como revisar este documento")
    D.p("Este documento reúne, em um único arquivo, todo o conteúdo científico exibido no aplicativo e no site: fichas das espécies, "
        "lâminas (imagens) com legendas e créditos, protocolos laboratoriais, guia de artefatos, banco de questões e referências. "
        "O aplicativo e o site leem os mesmos arquivos JSON de que este documento é gerado; portanto, corrigir o texto na fonte "
        "(tools/conteudo/) e regenerar atualiza os três.")
    D.h("1.1 Método de verificação", 2)
    D.p(review["scope"])
    D.p("Cada afirmação exibida nas fichas de espécie é um registro com: identificador, seção, texto, status, referências e "
        "trecho de evidência. Os status são:")
    D.bullets([
        "Confirmado — a fonte lida sustenta a afirmação como escrita.",
        "Corrigido — a fonte lida contradiz ou precisa o texto anterior; o texto anterior é preservado no campo “Antes”.",
        "Ressalva — a afirmação é usual/didática, mas a fonte lida não a sustenta integralmente; a limitação é descrita na nota.",
        "Observação da lâmina — descrição feita pelos autores sobre a própria fotografia; não é afirmação de literatura.",
        "Retirado — texto anterior sem fonte lida; removido do aplicativo e listado na seção 9.",
    ])
    D.h("1.2 Limites desta verificação (leia antes de citar)", 2)
    D.p(review["notValidation"])
    D.p(review["sourceAccessNote"])
    D.p("Não revisado:", bold=True, space=1)
    D.bullets(review["notReviewed"])
    D.h("1.3 Números do acervo", 2)
    D.table(["Item", "Quantidade"], [
        ["Espécies", len(specs)], ["Imagens (lâminas e figuras)", n_img],
        ["Afirmações verificadas", len(all_claims)],
        ["— confirmadas", n_st("confirmado")], ["— corrigidas", n_st("corrigido")],
        ["— com ressalva", n_st("ressalva")], ["— observações das lâminas", n_st("observacao")],
        ["Itens do texto anterior retirados", n_removed],
        ["Protocolos", len(prot)], ["Itens do guia de artefatos", len(arte["itens"])],
        ["Questões", len(quiz)], ["Referências", len(ritems)],
    ], [9, 4], size=9)

    # ---------------- 2. equipe ----------------
    D.h("2. Instituição e equipe")
    D.kv("Instituição", site["institution"])
    D.kv("Curso", site["course"])
    for p_ in site["developers"]:
        D.kv(p_["role"], p_["name"])
    D.kv(site["advisor"]["role"], site["advisor"]["name"])
    D.pagebreak()

    # ---------------- 3. espécies ----------------
    D.h("3. Fichas das espécies, lâminas e verificação")
    D.p("Para cada espécie: (a) classificação; (b) lâminas com legenda, crédito e arquivo de origem; (c) texto exibido no aplicativo; "
        "(d) tabela de afirmações verificadas; (e) itens retirados.", italic=True)
    for n, (m, s) in enumerate(specs, 1):
        D.h(f"3.{n} {s['commonName']} — {s['scientificName']}", 2)
        D.kv("Módulo", m["title"])
        D.kv("ID no app", s["id"])
        D.kv("Categoria", s["category"])
        D.kv("Estágio", s["evolutionaryStage"])
        D.kv("Status no app", s["status"])
        if s.get("reviewNote"):
            D.kv("Nota de revisão", s["reviewNote"])
        t = s["taxonomy"]
        D.h("Classificação", 3)
        for k, lab in (("phylum", "Filo"), ("class", "Classe"), ("order", "Ordem"), ("family", "Família"), ("genus", "Gênero"), ("species", "Espécie")):
            D.kv(lab, t.get(k))
        D.kv("NCBI Taxonomy ID", t.get("ncbi"))
        D.kv("Nota taxonômica", t.get("note"))
        D.h("Lâminas e imagens", 3)
        for im in s["images"]:
            pth = IMG / im["file"]
            if pth.exists():
                par = D.d.add_paragraph()
                try:
                    par.add_run().add_picture(str(pth), width=Cm(6.0))
                except Exception as e:  # imagem ilegível: registra no texto, nunca omite em silêncio
                    par.add_run(f"[imagem não pôde ser incorporada: {e}]")
            rows = [
                ["ID da imagem", im["id"]], ["Arquivo (no pacote)", im["file"]],
                ["Tipo", im["type"] + (f" · {im['kind']}" if im.get("kind") else "")],
                ["Lâmina nº", im.get("lamina") if im.get("lamina") else "—"],
                ["Identificação", CONF_LABEL.get(im.get("confidence"), im.get("confidence") or "—")],
                ["Legenda", im.get("caption") or "—"], ["Texto alternativo", im["alt"]],
                ["Crédito / autoria", im.get("credit") or "NÃO INFORMADO (origem a confirmar)"],
                ["Situação do crédito", im.get("creditStatus") or "—"],
                ["Arquivo de origem", im.get("sourceFile") or "—"],
                ["Data (nome do arquivo)", im.get("date") or "—"], ["Licença", im.get("license") or "não definida"],
                ["Dimensões (px)", f"{im['width']} × {im['height']}"],
            ]
            D.table(["Campo", "Valor"], rows, [4.2, 13.2], size=8)
        D.h("Texto exibido no aplicativo", 3)
        D.kv("Tamanho", s.get("approxSizeMicrons"))
        D.kv("Morfologia", s.get("morphologyDescription"))
        if s.get("keyDiagnosticFeatures"):
            D.p("Características-chave:", bold=True, space=1)
            D.bullets(s["keyDiagnosticFeatures"])
        D.kv("Doença", s.get("disease"))
        D.kv("Patogenia", s.get("pathogenesis"))
        if s.get("clinicalManifestations"):
            D.p("Manifestações clínicas:", bold=True, space=1)
            D.bullets(s["clinicalManifestations"])
        d = s.get("diagnosticMethods", {})
        D.kv("Diagnóstico — método principal", d.get("goldStandard"))
        D.kv("Diagnóstico — amostra", d.get("sampleType"))
        if d.get("alternatives"):
            D.p("Diagnóstico — outros métodos:", bold=True, space=1)
            D.bullets(d["alternatives"])
        D.kv("Diagnóstico — observação técnica", d.get("technicalObservation"))
        c = s.get("transmissionAndCycle", {})
        D.kv("Ciclo", c.get("cycleType"))
        D.kv("Habitat", c.get("habitat"))
        D.kv("Via de transmissão", c.get("transmissionRoute"))
        D.kv("Forma infectante", c.get("infectiveForm"))
        D.kv("Forma diagnóstica", c.get("diagnosticForm"))
        if s.get("treatment"):
            D.p("Tratamento (fármacos citados; doses não reproduzidas):", bold=True, space=1)
            D.bullets(s["treatment"])
        if s.get("prophylaxis"):
            D.p("Prevenção:", bold=True, space=1)
            D.bullets(s["prophylaxis"])
        D.kv("Diagnóstico diferencial", s.get("differentialDiagnosis"))
        D.kv("Dica de bancada", s.get("benchTip"))

        D.h("Afirmações verificadas", 3)
        rows, sh = [], []
        for v in s["verification"]:
            ev = v.get("evidence") or ""
            if v.get("note"):
                ev += ("\n" if ev else "") + "Nota: " + v["note"]
            if v.get("before"):
                ev += ("\n" if ev else "") + "Antes: " + v["before"]
            rows.append([v["id"], v["section"], v["text"], ST_LABEL.get(v["status"], v["status"]),
                         "; ".join(short(r) for r in v["refs"]) or "—", ev or "—"])
            sh.append((3, ST_COLOR.get(v["status"], "FFFFFF")))
        D.table(["ID", "Seção", "Afirmação", "Status", "Fontes", "Evidência / nota"], rows, [1.9, 1.5, 5.2, 1.6, 2.5, 4.7], size=7, shades=sh)
        if s.get("removed"):
            D.p(f"Itens do texto anterior retirados ({len(s['removed'])}):", bold=True, space=1)
            D.table(["Campo", "Texto anterior", "Motivo da retirada"], [[r["field"], r["before"], r["reason"]] for r in s["removed"]],
                    [2.5, 7.4, 7.5], size=7, shades=[(0, ST_COLOR["removido"])] * len(s["removed"]))
    D.pagebreak()

    # ---------------- 4. protocolos ----------------
    D.h("4. Metodologias (protocolos laboratoriais)")
    D.p("Protocolos revisados em 17/10/2026 contra as fontes listadas; não foram revisados novamente em 23/10/2026. "
        "Procedimento didático: antes de uso em rotina, adotar e validar no POP do laboratório.", italic=True)
    for n, p_ in enumerate(prot, 1):
        D.h(f"4.{n} {p_['title']}", 2)
        D.kv("ID", p_["id"])
        D.kv("Nome popular", p_.get("popularName"))
        D.kv("Indicação", p_.get("indication"))
        D.kv("Princípio", p_.get("principle"))
        D.p("Reagentes e materiais:", bold=True, space=1)
        D.bullets(p_.get("reagentsAndMaterials"))
        D.p("Passo a passo:", bold=True, space=1)
        D.numbered(p_.get("stepByStep"))
        D.p("Vantagens:", bold=True, space=1)
        D.bullets(p_.get("advantages"))
        D.p("Limitações:", bold=True, space=1)
        D.bullets(p_.get("limitations"))
        D.p("Parasitos detectados:", bold=True, space=1)
        D.bullets(p_.get("keyParasitesDetected"))
        if p_.get("intensity"):
            D.p("Classificação de intensidade (dados do protocolo):", bold=True, space=1)
            D.p(json.dumps(p_["intensity"], ensure_ascii=False, indent=1), size=8)
        D.p("Evidências:", bold=True, space=1)
        for e in p_.get("evidence", []):
            D.bullets([f"{e['text']}  [{'; '.join(short(r) for r in e['refs'])}]"])
        D.p("Verificação item a item:", bold=True, space=1)
        D.table(["Item", "Status", "Nota", "Fontes"],
                [[v["item"], ST_LABEL.get(v["status"], v["status"]), v["note"], "; ".join(short(r) for r in v["refs"]) or "—"] for v in p_["verification"]],
                [4, 2, 8, 3.4], size=7, shades=[(1, ST_COLOR.get(v["status"], "FFFFFF")) for v in p_["verification"]])
        D.kv("Referências do protocolo", "; ".join(short(r) for r in p_["refs"]))
    D.pagebreak()

    # ---------------- 5. artefatos ----------------
    D.h("5. Guia de artefatos")
    D.kv("Dica geral", arte["dica"])
    for n, a in enumerate(arte["itens"], 1):
        D.h(f"5.{n} {a['nome']}", 3)
        D.kv("Confundida com", a["confundidaCom"])
        D.kv("Como diferenciar", a["comoDiferenciar"])
        D.kv("Status", ST_LABEL.get(a.get("status"), a.get("status")))
        D.kv("Fontes", "; ".join(short(r) for r in a.get("refs", [])))
        D.kv("Evidência", a.get("evidencia"))
    if arte.get("removidos"):
        D.p("Itens do guia anterior retirados:", bold=True, space=1)
        D.table(["Item anterior", "Motivo"], [[f"{r['item']}: {r['antes']}", r["motivo"]] for r in arte["removidos"]],
                [7, 10.4], size=8)

    # ---------------- 6. quiz ----------------
    D.h("6. Banco de questões")
    D.p("As alternativas são embaralhadas a cada sessão no app; aqui aparecem na ordem do arquivo, com a correta destacada.", italic=True)
    for n, q in enumerate(quiz, 1):
        D.h(f"6.{n} {q['title']}", 3)
        D.kv("ID", q["id"])
        D.kv("Categoria / módulo", f"{q['category']} / {q['module']}")
        D.kv("Contexto", q.get("context"))
        D.kv("Pergunta", q["question"])
        for i, o in enumerate(q["options"]):
            par = D.d.add_paragraph()
            r = par.add_run(f"{chr(65 + i)}) {o}" + ("   ← correta" if i == q["correctIndex"] else ""))
            r.bold = i == q["correctIndex"]
            par.paragraph_format.left_indent = Cm(0.6)
            par.paragraph_format.space_after = Pt(0)
        D.kv("Explicação", q["explanation"])
        D.kv("Pérola de bancada", q.get("fieldPearl"))
        D.kv("Fontes", "; ".join(short(r) for r in q.get("refs", [])))
    D.pagebreak()

    # ---------------- 7. referências ----------------
    D.h("7. Referências")
    D.p("‘Acesso nesta revisão’ informa o que foi efetivamente lido (texto completo, resumo ou trechos extraídos).", italic=True)
    D.h("7.1 Bibliografia de base da disciplina (não consultada nesta revisão)", 2)
    D.bullets(site["references"])
    D.p(site["referencesNote"], italic=True, size=9)
    D.h("7.2 Referências citadas no atlas", 2)
    rows = []
    for r in ritems:
        ids = " · ".join(x for x in [("DOI " + r["doi"]) if r.get("doi") else "", ("PMID " + r["pmid"]) if r.get("pmid") else "", r.get("url") or ""] if x)
        rows.append([r["id"], r.get("group", ""), r["citation"] + (f"\n{ids}" if ids else ""), r.get("access", "")])
    D.table(["ID", "Grupo", "Citação", "Acesso nesta revisão"], rows, [2.4, 2.2, 8.8, 4.0], size=7)

    # ---------------- 8. créditos das imagens (consolidado) ----------------
    D.h("8. Créditos das imagens (quadro consolidado)")
    rows = [[s["commonName"], im["id"], im["file"], im.get("credit") or "NÃO INFORMADO", im.get("creditStatus") or "—"] for _, s in specs for im in s["images"]]
    D.table(["Espécie", "Imagem", "Arquivo", "Crédito", "Situação"], rows, [3.2, 1.4, 6.2, 4.8, 1.8], size=7)
    pend = [r for r in rows if r[4] in ("a-confirmar", "—") or r[3] == "NÃO INFORMADO"]
    D.p(f"{len(rows)} imagens; {len(pend)} com autoria ausente ou a confirmar. Nenhuma autoria foi presumida: onde o documento de origem não "
        "nomeia o autor, o crédito aparece como “a confirmar”.", bold=True)

    # ---------------- 9. histórico de alterações ----------------
    D.h("9. Histórico de alterações em relação à versão anterior (v4.2)")
    D.p("A versão anterior do texto está arquivada em acervo-nao-publicado/versao_anterior_v4.2/. Abaixo, tudo o que foi corrigido ou retirado.", italic=True)
    D.h("9.1 Afirmações corrigidas", 2)
    rows = []
    for _, s in specs:
        for v in s["verification"]:
            if v["status"] == "corrigido":
                rows.append([v["id"], v.get("before", ""), v["text"], "; ".join(short(r) for r in v["refs"])])
    D.table(["ID", "Antes", "Depois", "Fontes"], rows, [2, 5.5, 6.5, 3.4], size=7)
    D.h("9.2 Itens retirados por falta de fonte lida", 2)
    rows = [[s["commonName"], r["field"], r["before"], r["reason"]] for _, s in specs for r in s.get("removed", [])]
    D.table(["Espécie", "Campo", "Texto anterior", "Motivo"], rows, [2.8, 2.2, 6.2, 6.2], size=7)

    # ---------------- 10. reprodutibilidade ----------------
    D.h("10. Reprodutibilidade e integridade")
    D.p("Arquivos de origem e somas SHA-256:", bold=True, space=1)
    src = ROOT / "docs" / "fontes"
    for f in sorted(src.glob("*")):
        if f.is_file():
            D.kv(f.name, sha(f))
    if manifest:
        D.kv("Manifesto de dados do app (arquivos)", manifest.get("fileCount") or len(manifest.get("files", [])))
        D.kv("SHA-256 combinado do manifesto", manifest.get("combinedSha256"))
    D.p("Para regenerar tudo a partir da fonte:", bold=True, space=1)
    D.bullets([
        "python3 tools/aplicar-conteudo.py — gera os JSON de public/data a partir de tools/conteudo/",
        "node tools/validar-dados.mjs — valida estrutura, referências, status e cobertura das afirmações",
        "python3 flutter_app/tool/sync_assets.py — copia os dados para o app e gera o manifesto com SHA-256",
        "python3 tools/gerar-documento.py — gera este documento; depois, soffice --headless --convert-to pdf",
        "python3 tools/conferir-documento.py — confere que o documento contém todo o conteúdo dos JSON",
    ])
    D.h("10.1 Pendências conhecidas", 2)
    D.bullets([
        "O código Dart do aplicativo não foi compilado nem executado no ambiente de produção deste material (sem Flutter/Android SDK); "
        "foi verificado apenas por análise sintática e de contrato (tool/verify_contract.py). Rode flutter analyze e flutter test.",
        "As citações de evidência são os trechos devolvidos por um leitor automático de páginas; confirmar na fonte antes de citar.",
        "Autoria das fotografias ainda não informada no documento de origem: ver seção 8 (imagens “a confirmar”).",
        "A identificação das espécies nas fotos de protozoários segue as legendas do documento de lâminas e não foi confirmada de forma independente.",
        "Imagens externas (S. mansoni; Giardia e E. histolytica ext01) estão sem crédito: confirmar origem e licença ou substituir.",
        "Não foi encontrada fonte para a morfologia do cisto de Chilomastix mesnili; nenhuma descrição foi afirmada.",
        "Questionário anterior (DSEI/malária) foi arquivado, não verificado nem reaproveitado.",
        "Livros-texto da disciplina não foram consultados.",
    ])
    cp = D.d.core_properties
    cp.title = site['title'] + ' — Documento de Revisão'
    cp.author = 'Micael Davi Lima de Oliveira; Elias de Souza Barros (orientação: Profa. Dra. Jaila Dias Borges Lalwani)'
    cp.subject = 'Revisão e verificação científica'
    OUT.parent.mkdir(exist_ok=True)
    D.d.save(OUT)
    print("gerado:", OUT, f"({OUT.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
