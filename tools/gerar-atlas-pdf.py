#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera o "Atlas em PDF/DOCX" (material de estudo) a partir dos mesmos JSON do site e do app.

Diferente do Documento de Revisão (auditoria), este é o atlas para o estudante: por espécie, fotos das lâminas
com legenda e crédito, morfologia, critérios, doença, diagnóstico, tratamento (fármacos citados, sem doses) e profilaxia.
Nada é escrito à mão aqui: todo o texto vem de public/data (reprodutível; o hash dos JSON vai na ficha técnica).

Uso:  python3 tools/gerar-atlas-pdf.py
      (gera public/assets/downloads/Atlas_Parasitologia_Humana_UFAM.docx e converte para .pdf com o soffice)
"""
import hashlib, importlib.util, io, json, subprocess, sys, tempfile
from datetime import date
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "public" / "data"
IMG = ROOT / "public" / "assets" / "img"
OUT = ROOT / "public" / "assets" / "downloads"
NOME = "Atlas_Parasitologia_Humana_UFAM"
TEAL, INK, MUTED = RGBColor(0x0B, 0x6B, 0x62), RGBColor(0x14, 0x20, 0x1F), RGBColor(0x56, 0x65, 0x5F)
ACC = {"teal": "0B6B62", "amber": "A2600D", "violet": "5B3F94"}
J = lambda p: json.loads((DATA / p).read_text(encoding="utf-8"))
CONF = {"confirmada": "identificação confirmada", "alta": "identificação de alta confiança", "media": "identificação de média confiança (a confirmar)",
        "documento": "identificação conforme legenda dos autores do documento de lâminas"}


def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr(); sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), hexcolor); tcPr.append(sh)


def field(par, instr):
    for t, txt in (("begin", None), (None, instr), ("end", None)):
        r = par.add_run()
        if t:
            e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), t); r._r.append(e)
        else:
            e = OxmlElement("w:instrText"); e.set(qn("xml:space"), "preserve"); e.text = txt; r._r.append(e)


class Doc:
    def __init__(self):
        self.d = Document()
        s = self.d.sections[0]
        s.page_width, s.page_height = Cm(21), Cm(29.7)
        s.left_margin = s.right_margin = Cm(1.9); s.top_margin = Cm(1.9); s.bottom_margin = Cm(1.8)
        st = self.d.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(10)
        st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
        for n, sz in (("Heading 1", 20), ("Heading 2", 14), ("Heading 3", 11.5)):
            h = self.d.styles[n]; h.font.name = "Calibri"; h.font.size = Pt(sz); h.font.bold = True; h.font.color.rgb = TEAL
            h.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")

    def secao(self, rodape=True, reiniciar=False):
        """Nova seção em página nova. rodape=False deixa o rodapé vazio (capa e contracapa); reiniciar=True recomeça a numeração em 1."""
        sec = self.d.add_section(WD_SECTION.NEW_PAGE)
        for e in sec._sectPr.findall(qn("w:footerReference")):
            sec._sectPr.remove(e)          # add_section copia a referência; remove para criar um rodapé próprio
        sec.footer.is_linked_to_previous = False
        if rodape:
            fp = sec.footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = fp.add_run("Atlas Digital de Parasitologia Humana · UFAM — material de apoio ao ensino · página "); r.font.size = Pt(8); r.font.color.rgb = MUTED
            field(fp, "PAGE")
        if reiniciar:
            pg = OxmlElement("w:pgNumType"); pg.set(qn("w:start"), "1"); sec._sectPr.find(qn("w:pgMar")).addnext(pg)
        return sec

    def h(self, t, lvl=2, color=None):
        p = self.d.add_heading(t, lvl)
        if getattr(self, "_pb", False):
            p.paragraph_format.page_break_before = True; self._pb = False
        if color:
            for r in p.runs:
                r.font.color.rgb = RGBColor.from_string(color)
        p.paragraph_format.keep_with_next = True
        return p

    def p(self, t, bold=False, italic=False, size=None, color=None, after=4, align=None):
        par = self.d.add_paragraph(); r = par.add_run(t); r.bold = bold; r.italic = italic
        if size: r.font.size = Pt(size)
        if color: r.font.color.rgb = color
        par.paragraph_format.space_after = Pt(after)
        if align: par.alignment = align
        return par

    def kv(self, k, v):
        if not v:
            return
        par = self.d.add_paragraph(); a = par.add_run(k + ": "); a.bold = True; par.add_run(str(v)); par.paragraph_format.space_after = Pt(2)

    def bullets(self, items):
        for it in items or []:
            par = self.d.add_paragraph(style="List Bullet"); par.add_run(str(it)); par.paragraph_format.space_after = Pt(1)

    def pagebreak(self):
        self._pb = True   # a próxima página começa no próximo título (evita página em branco)


_cache = {}


def jpeg(path, maxside=900):
    """JPEG reduzido (q78) para o PDF não ficar gigante; o original do site não é alterado."""
    if path not in _cache:
        im = Image.open(path).convert("RGB")
        if max(im.size) > maxside:
            k = maxside / max(im.size); im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
        b = io.BytesIO(); im.save(b, "JPEG", quality=78, optimize=True); _cache[path] = b.getvalue()
    return io.BytesIO(_cache[path])


def _pic(par, path, maxw=7.9, maxh=8.6):
    """Insere a imagem dentro de uma caixa maxw x maxh (cm), mantendo a proporção; assim os dois lados do par ficam com altura comparável."""
    w, h = Image.open(path).size
    k = min(maxw / w, maxh / h)
    par.add_run().add_picture(jpeg(path), width=Cm(w * k), height=Cm(h * k))


def _cell(c, file, titulo, im, legenda=None):
    par = c.paragraphs[0]; par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    try:
        _pic(par, IMG / file)
    except Exception as e:  # nunca omite em silêncio
        par.add_run(f"[imagem não incorporada: {e}]")
    cap = c.add_paragraph(); cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = cap.add_run(titulo); r.bold = True; r.font.size = Pt(8)
    if legenda:
        q = c.add_paragraph(); q.alignment = WD_ALIGN_PARAGRAPH.CENTER; q2 = q.add_run(legenda); q2.font.size = Pt(7)
    cr = c.add_paragraph(); cr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r3 = cr.add_run((im.get("credit") or "Crédito não informado (origem a confirmar)") + " · " + CONF.get(im.get("confidence"), "identificação a confirmar"))
    r3.italic = True; r3.font.size = Pt(7); r3.font.color.rgb = MUTED


def _row(D, esq, dir_):
    """Uma linha com duas imagens lado a lado (esq, dir_ = (arquivo, título, imagem-origem, legenda)); a linha não é quebrada entre páginas."""
    t = D.d.add_table(rows=1, cols=2); t.alignment = WD_TABLE_ALIGNMENT.CENTER
    trPr = t.rows[0]._tr.get_or_add_trPr(); cs = OxmlElement("w:cantSplit"); trPr.append(cs)
    for c, x in zip(t.rows[0].cells, (esq, dir_)):
        if x:
            _cell(c, *x)
            for par in c.paragraphs[:-1]:
                par.paragraph_format.keep_with_next = True
    D.d.add_paragraph().paragraph_format.space_after = Pt(2)


def _pares(ims):
    """Pares (campo/foto, ampliação) da MESMA lâmina: (1) 'campo geral' + 'detalhe ampliado' com o mesmo número de lâmina;
    (2) foto + ampliação digital do documento v4. Devolve (pares, fotos_sem_ampliação)."""
    pares, usadas = [], set()
    por_lam = {}
    for im in ims:
        if im.get("lamina"):
            por_lam.setdefault(im["lamina"], {})[im.get("kind")] = im
    for n in sorted(por_lam):
        v = por_lam[n]
        if "campo" in v and "detalhe" in v:
            c, d = v["campo"], v["detalhe"]
            pares.append(((c["file"], f"Lâmina {int(n):02d} · campo geral", c, c.get("caption")),
                          (d["file"], f"Lâmina {int(n):02d} · detalhe ampliado (foto)", d, d.get("caption"))))
            usadas.update((c["id"], d["id"]))
    for im in ims:
        det = im.get("detail")
        if det and det.get("file") and im["id"] not in usadas:
            tag = f"Fig. {im['figure']} · " if im.get("figure") else ""
            pares.append(((im["file"], tag + "foto da lâmina", im, im.get("caption")),
                          (det["file"], tag + (det.get("label") or "ampliação digital"), im, None)))
            usadas.add(im["id"])
    return pares, [im for im in ims if im["id"] not in usadas]


def photos(D, s):
    ims = [i for i in s["images"] if i["type"] == "microfotografia"]
    if not ims:
        D.p("Esta espécie ainda não tem fotos de lâmina neste atlas.", italic=True, color=MUTED); return
    pares, soltas = _pares(ims)
    D.h("Fotos de lâminas", 3)
    if pares:
        D.p("Cada linha mostra a mesma lâmina à esquerda e a sua ampliação à direita, para comparar o campo geral com os detalhes.", italic=True, size=8.5, color=MUTED).paragraph_format.keep_with_next = True
        for esq, dir_ in pares:
            _row(D, esq, dir_)
    if soltas:
        if pares:
            D.p("Outras fotos desta espécie (sem ampliação disponível no material de origem):", bold=True, size=9).paragraph_format.keep_with_next = True
        else:
            D.p("Fotos desta espécie (o material de origem não traz ampliação para elas):", bold=True, size=9).paragraph_format.keep_with_next = True
        for k in range(0, len(soltas), 2):
            lote = soltas[k:k + 2]
            xs = []
            for im in lote:
                tag = f"Fig. {im['figure']} · " if im.get("figure") else (f"Lâmina {int(im['lamina']):02d} · " if im.get("lamina") else "")
                xs.append((im["file"], tag + (im.get("alt") or ""), im, im.get("caption")))
            _row(D, xs[0], xs[1] if len(xs) > 1 else None)


def especie(D, m, s):
    acc = ACC.get(m.get("accent"), "0B6B62")
    D.h(s["commonName"], 2, acc)
    D.p(s["scientificName"], italic=True, color=MUTED, after=2)
    D.kv("Categoria", s.get("category")); D.kv("Doença", s.get("disease")); D.kv("Estágio de referência", s.get("evolutionaryStage"))
    if s.get("status") == "revisar":
        D.p("EM REVISÃO: " + (s.get("reviewNote") or "conteúdo ainda não validado pela literatura."), bold=True, color=RGBColor(0xA1, 0x26, 0x2B))
    photos(D, s)
    if s.get("morphologyDescription"):
        D.h("Morfologia", 3); D.p(s["morphologyDescription"])
    if s.get("keyDiagnosticFeatures"):
        D.h("Critérios-chave de identificação", 3); D.bullets(s["keyDiagnosticFeatures"])
    D.kv("Dimensões de referência (livro-texto, não medidas nas fotos)", s.get("approxSizeMicrons"))
    c = s.get("transmissionAndCycle") or {}
    if any(c.values()):
        D.h("Ciclo e transmissão", 3)
        for k, lab in (("transmissionRoute", "Transmissão"), ("infectiveForm", "Forma infectante"), ("diagnosticForm", "Forma diagnóstica"), ("habitat", "Habitat"), ("cycleType", "Tipo de ciclo")):
            D.kv(lab, c.get(k))
    if s.get("pathogenesis") or s.get("clinicalManifestations"):
        D.h("Doença e clínica", 3); D.p(s.get("pathogenesis") or ""); D.bullets(s.get("clinicalManifestations"))
    d = s.get("diagnosticMethods") or {}
    if any(d.values()):
        D.h("Diagnóstico laboratorial", 3); D.kv("Método de escolha", d.get("goldStandard")); D.kv("Amostra", d.get("sampleType")); D.kv("Observação técnica", d.get("technicalObservation"))
        if d.get("alternatives"):
            D.kv("Alternativas", "; ".join(d["alternatives"]))
    if s.get("treatment"):
        D.h("Tratamento (fármacos citados; sem doses)", 3); D.bullets(s["treatment"])
    if s.get("prophylaxis"):
        D.h("Profilaxia", 3); D.bullets(s["prophylaxis"])
    if s.get("differentialDiagnosis"):
        D.h("Diagnóstico diferencial", 3); D.p(s["differentialDiagnosis"])
    if s.get("benchTip"):
        D.kv("Dica de bancada", s["benchTip"])
    D.pagebreak()


WHITE = RGBColor(0xFF, 0xFF, 0xFF)
SOFT = RGBColor(0xE8, 0xF1, 0xF5)
SITE_URL = "https://micael-oliveira-ufam.github.io/atlas-parasitologia-humana-ufam/"


def _arte():
    sp = importlib.util.spec_from_file_location("arte_livro", ROOT / "tools" / "arte_livro.py")
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m


def fullbleed(par, path, descr):
    """Imagem de página inteira ANCORADA atrás do texto (o texto da capa/capítulos continua sendo texto, selecionável)."""
    run = par.add_run(); run.add_picture(str(path), width=Cm(21), height=Cm(29.7))
    inline = run._r.xpath(".//wp:inline")[0]
    anchor = parse_xml('<wp:anchor xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" distT="0" distB="0" distL="0" distR="0" '
                       'simplePos="0" relativeHeight="0" behindDoc="1" locked="1" layoutInCell="1" allowOverlap="1"><wp:simplePos x="0" y="0"/>'
                       '<wp:positionH relativeFrom="page"><wp:posOffset>0</wp:posOffset></wp:positionH>'
                       '<wp:positionV relativeFrom="page"><wp:posOffset>0</wp:posOffset></wp:positionV></wp:anchor>')
    docpr = inline.find(qn("wp:docPr")); docpr.set("descr", descr)   # texto alternativo (a arte é decorativa)
    anchor.append(inline.find(qn("wp:extent")))
    anchor.append(parse_xml('<wp:effectExtent xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" l="0" t="0" r="0" b="0"/>'))
    anchor.append(parse_xml('<wp:wrapNone xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"/>'))
    anchor.append(docpr); anchor.append(inline.find(qn("wp:cNvGraphicFramePr"))); anchor.append(inline.find(qn("a:graphic")))
    inline.getparent().replace(inline, anchor)


def P(D, t, size=10, color=None, bold=False, italic=False, before=0, after=0, align=None, left=0.0, right=0.0, keep=False, spacing=None):
    """Parágrafo de página especial, com espaçamentos em pontos e recuo em cm."""
    par = D.d.add_paragraph(); r = par.add_run(t)
    if spacing: r._r.get_or_add_rPr().append(parse_xml(f'<w:spacing xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:val="{spacing}"/>'))
    r.bold = bold; r.italic = italic; r.font.size = Pt(size)
    if color is not None: r.font.color.rgb = color
    f = par.paragraph_format; f.space_before = Pt(before); f.space_after = Pt(after); f.left_indent = Cm(left); f.right_indent = Cm(right); f.keep_with_next = keep
    if align is not None: par.alignment = align
    return par


def capa(D, site, arte, tmp, mark):
    img = arte.capa(Path(tmp) / "capa.jpg", mark)
    first = D.d.add_paragraph(); first.paragraph_format.space_after = Pt(0)
    fullbleed(first, img, "Capa: campo de microscópio com ovo, larva e cisto estilizados")
    C = WD_ALIGN_PARAGRAPH.CENTER
    P(D, "LAMINÁRIO INTERATIVO DE ENSINO E DIAGNÓSTICO", 10.5, SOFT, bold=True, before=372, after=8, align=C, spacing=40)
    P(D, "Atlas Digital de", 36, WHITE, bold=True, after=0, align=C)
    P(D, "Parasitologia Humana", 40, WHITE, bold=True, after=10, align=C)
    P(D, "Nematelmintos  ·  Platelmintos  ·  Protozoários", 14, SOFT, italic=True, after=0, align=C)
    P(D, site.get("institution", ""), 13, WHITE, bold=True, before=88, after=1, align=C)
    P(D, site.get("course", ""), 11.5, SOFT, after=10, align=C)
    P(D, " · ".join(d["name"] for d in site.get("developers", [])), 10.5, WHITE, after=1, align=C)
    if site.get("advisor"):
        P(D, f"Orientação: {site['advisor']['name']}", 10.5, SOFT, after=8, align=C)
    P(D, f"Edição de {date.today().strftime('%d/%m/%Y')}  ·  material de apoio ao ensino", 9, SOFT, italic=True, align=C)


def abertura_capitulo(D, m, n, sp, img_path):
    """Página de abertura de capítulo: arte colorida do módulo + título + cartão com descrição e lista de espécies."""
    L = WD_ALIGN_PARAGRAPH.LEFT
    first = D.d.add_paragraph(); first.paragraph_format.page_break_before = True; first.paragraph_format.space_after = Pt(0)
    fullbleed(first, img_path, f"Abertura do capítulo {n}: {m['title']} (ilustração estilizada)")
    r = first.add_run("CAPÍTULO")
    r._r.get_or_add_rPr().append(parse_xml('<w:spacing xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:val="60"/>'))
    r.bold = True; r.font.size = Pt(13); r.font.color.rgb = SOFT
    first.paragraph_format.space_before = Pt(26)
    P(D, str(n), 120, WHITE, bold=True, after=0, align=L)
    t = D.d.add_heading(m["title"], 1); t.paragraph_format.keep_with_next = True; t.paragraph_format.space_before = Pt(0); t.paragraph_format.space_after = Pt(4)
    for rr in t.runs:
        rr.font.size = Pt(40); rr.font.color.rgb = WHITE
    P(D, m.get("subtitle", ""), 14, SOFT, italic=True, after=0, align=L)
    nf = sum(1 for s in sp for i in s["images"] if i["type"] == "microfotografia")
    P(D, m.get("description", ""), 10.5, INK, before=78, after=6, left=0.7, right=0.7)
    P(D, f"{len(sp)} espécies  ·  {nf} fotografias de lâmina", 10, TEAL if m.get("accent") == "teal" else RGBColor.from_string(ACC.get(m.get("accent"), "0B6B62")), bold=True, after=5, left=0.7)
    for s in sp:
        par = D.d.add_paragraph(); par.paragraph_format.left_indent = Cm(0.7); par.paragraph_format.space_after = Pt(2)
        a = par.add_run("•  " + s["commonName"].split(" (")[0]); a.bold = True; a.font.size = Pt(10.5); a.font.color.rgb = INK
        b = par.add_run("  " + s["scientificName"]); b.italic = True; b.font.size = Pt(9.5); b.font.color.rgb = MUTED
        if s.get("status") == "revisar":
            c = par.add_run("  (em revisão)"); c.font.size = Pt(8.5); c.font.color.rgb = RGBColor(0xA1, 0x26, 0x2B)
    D.pagebreak()


def referencias(D, refs):
    D.pagebreak()
    D.h("Referências", 1)
    D.p("Fontes que sustentam as afirmações científicas deste atlas. O campo \"acesso\" diz o que foi lido de cada uma (texto completo, resumo etc.).", italic=True, size=9, color=MUTED)
    for r in sorted(refs, key=lambda x: (x.get("citation") or x.get("short") or "").lower()):
        par = D.d.add_paragraph(); par.paragraph_format.space_after = Pt(3); par.paragraph_format.left_indent = Cm(0.5); par.paragraph_format.first_line_indent = Cm(-0.5)
        x = par.add_run(r.get("citation") or r.get("short") or r.get("id", "")); x.font.size = Pt(8.5)
        extra = " ".join(filter(None, [f"DOI: {r['doi']}." if r.get("doi") else "", f"PMID: {r['pmid']}." if r.get("pmid") else "", f"URL: {r['url']}." if r.get("url") else ""]))
        if extra:
            y = par.add_run(" " + extra); y.font.size = Pt(8); y.font.color.rgb = MUTED
        if r.get("access"):
            z = par.add_run(f" [acesso: {r['access']}]"); z.italic = True; z.font.size = Pt(8); z.font.color.rgb = TEAL


def contracapa(D, site, nrefs, sha, arte, tmp, mark):
    D.secao(rodape=False)
    img = arte.contracapa(Path(tmp) / "contracapa.jpg", mark)
    first = D.d.add_paragraph(); first.paragraph_format.space_after = Pt(0)
    fullbleed(first, img, "Contracapa: campo de microscópio com a marca do atlas e organismos estilizados")
    C = WD_ALIGN_PARAGRAPH.CENTER
    t = P(D, "Fim", 46, TEAL, bold=True, before=282, after=0, align=C)
    P(D, "Obrigado por estudar com este atlas.", 13, MUTED, italic=True, after=14, align=C)
    P(D, "Equipe", 10, TEAL, bold=True, after=2, left=1.0, right=1.0)
    for d in site.get("developers", []):
        P(D, f"{d['name']} — {d['role']}", 10, INK, after=1, left=1.0, right=1.0)
    if site.get("advisor"):
        P(D, f"{site['advisor']['name']} — {site['advisor']['role']}", 10, INK, after=1, left=1.0, right=1.0)
    P(D, f"{site.get('institution', '')} · {site.get('course', '')}", 10, INK, after=10, left=1.0, right=1.0)
    P(D, "Versão interativa", 10, TEAL, bold=True, after=2, left=1.0, right=1.0)
    P(D, SITE_URL, 9.5, INK, after=10, left=1.0, right=1.0)
    P(D, "Sobre este material", 10, TEAL, bold=True, after=2, left=1.0, right=1.0)
    P(D, f"Material de apoio ao ensino: não substitui livros-texto, normas laboratoriais nem avaliação clínica. As {nrefs} fontes científicas estão na seção Referências. "
         "As ilustrações da capa, das aberturas de capítulo e desta página são arte original e estilizada, sem escala e sem valor diagnóstico; as fotografias das lâminas estão nas fichas, com crédito e legenda.",
      9, MUTED, after=8, left=1.0, right=1.0)
    P(D, f"Edição gerada em {date.today().strftime('%d/%m/%Y')} · SHA-256 dos dados: {sha[:16]}…", 8, MUTED, italic=True, left=1.0, right=1.0)


def main():
    reg = J("modulos.json"); site = reg["site"]
    h = hashlib.sha256()
    for f in sorted(DATA.rglob("*.json")):
        h.update(f.read_bytes())
    D = Doc()
    arte = _arte(); tmp = tempfile.mkdtemp(prefix="atlas-arte-")
    mark = ROOT / "public" / "assets" / "brand" / "atlas-mark-512.png"
    capa(D, site, arte, tmp, mark)
    D.secao(rodape=True, reiniciar=True)   # a capa não leva rodapé; a numeração recomeça na ficha técnica
    D.h("Ficha técnica", 2)
    D.kv("Edição", f"gerada em {date.today().strftime('%d/%m/%Y')} a partir dos dados do site")
    D.kv("Desenvolvimento", site.get("developer"))
    if site.get("advisor"):
        D.kv("Orientação", f"{site['advisor']['name']} — {site['advisor']['role']}")
    D.kv("SHA-256 dos dados (public/data)", h.hexdigest())
    D.h("Como usar e limites", 2)
    D.bullets([
        "Material de apoio ao ensino: não substitui livros-texto, normas laboratoriais nem avaliação clínica.",
        "As legendas e identificações das fotos mais recentes são dos autores do documento de lâminas; só parte delas foi conferida com fonte oficial (ver site, seção Sobre).",
        "A autoria das fotos é indicada somente quando consta no documento de origem; \"a confirmar\" significa que não foi informada.",
        "As imagens deste PDF foram reduzidas para limitar o tamanho do arquivo; as do site têm até 1600 px. As dimensões citadas são valores de livro-texto, não medidas feitas nas fotos.",
        "Tratamento: apenas fármacos citados, sem doses; siga diretrizes vigentes e prescrição.",
        "Espécies marcadas \"em revisão\" têm texto ainda não validado pela literatura.",
    ])
    D.h("Conteúdo", 2)
    for m in reg["modules"]:
        sp = J(m["dataFile"].replace("data/", "", 1))["specimens"]
        D.p(f"{m['title']}: " + "; ".join(s["commonName"].split(" (")[0] for s in sp if s["status"] != "rascunho"), after=3)
    D.pagebreak()
    for m in sorted(reg["modules"], key=lambda x: x["order"]):
        sp = [s for s in J(m["dataFile"].replace("data/", "", 1))["specimens"] if s["status"] != "rascunho"]
        n = m["order"]; kind = {"nematelmintos": "nem", "platelmintos": "pla", "protozoarios": "pro"}.get(m["id"], "nem")
        abertura_capitulo(D, m, n, sp, arte.capitulo(Path(tmp) / f"cap{n}.jpg", m.get("accent", "teal"), kind, n, len(sp)))
        for s in sp:
            especie(D, m, s)
    art = J("artefatos.json")
    D.pagebreak()
    D.h("Guia de artefatos", 1)
    D.p(art["dica"])
    for a in art["itens"]:
        D.h(a["nome"], 3); D.kv("Confundida com", a["confundidaCom"]); D.kv("Como diferenciar", a["comoDiferenciar"])
    refs = J("referencias.json")["items"]
    referencias(D, refs)
    contracapa(D, site, len(refs), h.hexdigest(), arte, tmp, mark)
    OUT.mkdir(parents=True, exist_ok=True)
    docx = OUT / f"{NOME}.docx"; D.d.save(docx)
    print("DOCX:", docx, round(docx.stat().st_size / 1e6, 1), "MB")
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(OUT), str(docx)], check=True, capture_output=True)
    pdf = OUT / f"{NOME}.pdf"; print("PDF :", pdf, round(pdf.stat().st_size / 1e6, 1), "MB")
    man = {"geradoEm": date.today().isoformat(), "dadosSha256": h.hexdigest(), "arquivos": {}}
    for f in sorted(OUT.glob("*")):
        if f.suffix in (".pdf", ".docx"):
            man["arquivos"][f.name] = {"bytes": f.stat().st_size, "sha256": hashlib.sha256(f.read_bytes()).hexdigest()}
    (OUT / "manifest.json").write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
