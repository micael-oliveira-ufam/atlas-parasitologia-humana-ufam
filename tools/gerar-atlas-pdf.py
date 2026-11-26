#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera o "Atlas em PDF/DOCX" (material de estudo) a partir dos mesmos JSON do site e do app.

Diferente do Documento de Revisão (auditoria), este é o atlas para o estudante: por espécie, fotos das lâminas
com legenda e crédito, morfologia, critérios, doença, diagnóstico, tratamento (fármacos citados, sem doses) e profilaxia.
Nada é escrito à mão aqui: todo o texto vem de public/data (reprodutível; o hash dos JSON vai na ficha técnica).

Uso:  python3 tools/gerar-atlas-pdf.py
      (gera public/assets/downloads/Atlas_Parasitologia_Humana_UFAM.docx e converte para .pdf com o soffice)
"""
import hashlib, io, json, subprocess, sys
from datetime import date
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
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
        fp = s.footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = fp.add_run("Atlas Digital de Parasitologia Humana · UFAM — material de apoio ao ensino · página "); r.font.size = Pt(8); r.font.color.rgb = MUTED
        field(fp, "PAGE")

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


def main():
    reg = J("modulos.json"); site = reg["site"]
    h = hashlib.sha256()
    for f in sorted(DATA.rglob("*.json")):
        h.update(f.read_bytes())
    D = Doc()
    logo = ROOT / "public" / "assets" / "brand" / "atlas-logo-1200.png"
    if logo.exists():
        D.d.add_paragraph().add_run().add_picture(str(logo), width=Cm(12))
    D.p(site["title"], bold=True, size=24, color=TEAL, after=2)
    D.p(site.get("institution", ""), size=12, color=MUTED, after=2)
    D.p(site.get("course", ""), size=11, color=MUTED, after=14)
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
        D.h(m["title"], 1, ACC.get(m.get("accent")))
        D.p(m.get("subtitle", ""), italic=True, color=MUTED); D.p(m.get("description", "")); D.pagebreak()
        for s in sp:
            especie(D, m, s)
    arte = J("artefatos.json")
    D.h("Guia de artefatos", 1)
    D.p(arte["dica"])
    for a in arte["itens"]:
        D.h(a["nome"], 3); D.kv("Confundida com", a["confundidaCom"]); D.kv("Como diferenciar", a["comoDiferenciar"])
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
