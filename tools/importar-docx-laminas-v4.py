#!/usr/bin/env python3
"""Importa as lâminas do documento "Laminas_Parasitologia_v4.docx" (tabela 16×2; cada célula = 1 figura).

Cada figura tem 2 imagens (foto à esquerda, "ampliação digital" à direita) e uma legenda em parágrafos:
  1) "Figura N. <identificação>"   2) "Grupo: ... | Objetiva: ...*"   3) descrição [fontes]   4) "Obs.: ..." (opcional)

Reprodutível e sem invenção:
- as imagens são gravadas como estão no docx (JPEG q88, no máx. 1600 px; as do docx têm 1100 px / 440 px);
- nada é deduzido além do que a legenda diz; a espécie vem de um mapa explícito (SPECIES) por trecho da legenda;
- fotos que já existem no catálogo são detectadas por hash perceptual (dHash 16×16) e NÃO são duplicadas;
- "Lâmina feita/obtida por <nome>" é registrada como preparo da lâmina, não como autoria da foto.

Uso: python3 tools/importar-docx-laminas-v4.py docs/fontes/Laminas_Parasitologia_v4.docx
Saída: public/assets/img/<módulo>/..._v4fNN*.jpg e tools/laminas_v4_import.json
"""
import glob, hashlib, io, json, os, re, sys, zipfile
from xml.etree import ElementTree as ET
from PIL import Image, ImageOps

NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, 'public', 'assets', 'img')
MAX_SIDE = 1600
# trecho da legenda (minúsculas) -> (módulo, id da espécie no atlas); ordem importa (mais específico primeiro)
SPECIES = [
    ('trichuris trichiura', ('nematelmintos', 'trichuris_trichiura')),
    ('ascaris lumbricoides', ('nematelmintos', 'ascaris_lumbricoides')),
    ('strongyloides stercoralis', ('nematelmintos', 'strongyloides_stercoralis')),
    ('hymenolepis nana', ('platelmintos', 'hymenolepis_nana')),
    ('taenia sp', ('platelmintos', 'taenia_sp')),
    ('entamoeba histolytica', ('protozoarios', 'entamoeba_histolytica')),
    ('entamoeba coli', ('protozoarios', 'entamoeba_coli')),
    ('endolimax nana', ('protozoarios', 'endolimax_nana')),
    ('iodamoeba b', ('protozoarios', 'iodamoeba_buetschlii')),
    ('blastocystis', ('protozoarios', 'blastocystis_sp')),
    ('giardia duodenalis', ('protozoarios', 'giardia_lamblia')),
    ('chilomastix mesnili', ('protozoarios', 'chilomastix_mesnili')),
    ('estrutura não identificada', ('artefatos', 'nao_identificada')),
]


def dhash(im, n=16):
    g = ImageOps.autocontrast(im.convert('L').resize((n + 1, n), Image.LANCZOS))
    px = list(g.tobytes()); bits = 0
    for y in range(n):
        for x in range(n):
            bits = (bits << 1) | (px[y * (n + 1) + x] > px[y * (n + 1) + x + 1])
    return bits


def existentes():
    out = {}
    for f in glob.glob(os.path.join(IMG, '**', '*.jp*g'), recursive=True):
        rel = os.path.relpath(f, IMG).replace(os.sep, '/')
        if '_v4f' in rel or rel.startswith('brand/'):
            continue  # só o acervo anterior (e nunca as saídas deste próprio importador)
        out[rel] = dhash(Image.open(f))
    return out


def save(im, rel):
    if max(im.size) > MAX_SIDE:
        k = MAX_SIDE / max(im.size); im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    dest = os.path.join(IMG, rel); os.makedirs(os.path.dirname(dest), exist_ok=True)
    im.save(dest, 'JPEG', quality=88, optimize=True)
    return list(im.size)


def main(path):
    z = zipfile.ZipFile(path)
    doc = ET.fromstring(z.read('word/document.xml'))
    rels = ET.fromstring(z.read('word/_rels/document.xml.rels'))
    tg = {r.get('Id'): r.get('Target') for r in rels}
    ex = existentes()
    figuras = []
    for tr in doc.find('.//w:tbl', NS).findall('w:tr', NS):
        for tc in tr.findall('w:tc', NS):
            paras = []
            for p in tc.findall('w:p', NS):
                t = ''.join(x.text or '' for x in p.iter('{%s}t' % NS['w'])).strip()
                if t:
                    paras.append(t)
            pics = [tg[d.find('.//a:blip', NS).get('{%s}embed' % NS['r'])] for d in tc.findall('.//w:drawing', NS)]
            m = re.match(r'Figura\s+(\d+)\.\s*(.+)', paras[0] if paras else '')
            if not m or len(pics) != 2:
                raise SystemExit(f'célula inesperada: {paras[:1]} / {len(pics)} imagens')
            figuras.append((int(m.group(1)), m.group(2).strip(), paras, pics))
    figuras.sort()
    meta = []
    for n, ident, paras, pics in figuras:
        low = ident.lower()
        alvo = next((v for k, v in SPECIES if k in low), None)
        if alvo is None:
            raise SystemExit(f'figura {n}: identificação sem espécie mapeada: {ident!r}')
        mod, sp = alvo
        grupo = next((p for p in paras if p.startswith('Grupo:')), '')
        desc = next((p for p in paras[1:] if not p.startswith(('Grupo:', 'Obs.:'))), '')
        obs = next((p for p in paras if p.startswith('Obs.:')), '')
        refs = sorted({int(x) for g in re.findall(r'\[([\d,\s]+)\]', ' '.join(paras)) for x in g.split(',') if x.strip()})
        preparo = re.search(r'Lâmina (?:feita|obtida) por ([^.]+)\.', obs)
        foto = Image.open(io.BytesIO(z.read('word/' + pics[0]))).convert('RGB')
        amp = Image.open(io.BytesIO(z.read('word/' + pics[1]))).convert('RGB')
        h = dhash(foto)
        dup = min(((k, bin(h ^ v).count('1')) for k, v in ex.items()), key=lambda kv: kv[1])
        duplicada = dup[0] if dup[1] <= 6 else None
        pasta = 'artefatos' if mod == 'artefatos' else mod
        base = f'{pasta}/{sp}_v4f{n:02d}'
        r = {'figura': n, 'modulo': mod, 'especie': sp, 'identificacao': ident, 'grupo': grupo, 'descricao': desc, 'obs': obs,
             'objetiva_legenda': (re.search(r'Objetiva:\s*([^|\n]+)', grupo) or [None, None])[1],
             'refs_numeros': refs, 'lamina_preparada_por': preparo.group(1).strip() if preparo else None,
             'midia_foto': pics[0], 'midia_ampliacao': pics[1], 'tamanho_origem_foto': list(foto.size),
             'tamanho_origem_ampliacao': list(amp.size), 'foto_ja_no_catalogo': duplicada,
             'distancia_hash': dup[1], 'legenda_completa': paras}
        if duplicada:
            r['arquivo_foto'] = duplicada
            r['tamanho_foto'] = list(Image.open(os.path.join(IMG, duplicada)).size)
        else:
            r['arquivo_foto'] = base + '.jpg'; r['tamanho_foto'] = save(foto, base + '.jpg')
        r['arquivo_ampliacao'] = base + '_ampliacao.jpg'; r['tamanho_ampliacao'] = save(amp, base + '_ampliacao.jpg')
        meta.append(r)
        print(f'Fig {n:2d} {sp:26s} foto={"(já existe: "+duplicada+")" if duplicada else r["tamanho_foto"]} amp={r["tamanho_ampliacao"]}')
    sha = hashlib.sha256(open(path, 'rb').read()).hexdigest()
    json.dump({'docx': os.path.basename(path), 'docx_sha256': sha, 'n_figuras': len(meta), 'figuras': meta},
              open(os.path.join(ROOT, 'tools', 'laminas_v4_import.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('docx sha256', sha, '| figuras', len(meta))


if __name__ == '__main__':
    main(sys.argv[1])
