#!/usr/bin/env python3
"""Importa as lâminas de protozoários de um .docx (imagem seguida de legenda "Figura ...").

Reprodutível: aplica exatamente os recortes (<a:srcRect>) que o próprio documento usa, redimensiona
para no máximo 1600 px no maior lado e grava JPEG q88 em public/assets/img/protozoarios/.
Não inventa autoria: só extrai "(Autora da foto: X)" quando está escrito na legenda.
Uso: python3 tools/importar-docx-protozoarios.py docs/fontes/Laminas_de_Protozoarios.docx
Saída: imagens + tools/protozoarios_import.json (metadados lidos do docx, para conferência).
"""
import hashlib, io, json, os, re, sys, zipfile
from xml.etree import ElementTree as ET
from PIL import Image

NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
      'pic': 'http://schemas.openxmlformats.org/drawingml/2006/picture',
      'rel': 'http://schemas.openxmlformats.org/package/2006/relationships'}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'public', 'assets', 'img', 'protozoarios')
SPECIES = {  # trecho da legenda -> id da espécie no atlas
    'Entamoeba histolytica': 'entamoeba_histolytica', 'Giardia duodenalis': 'giardia_lamblia',
    'Endolimax nana': 'endolimax_nana', 'Entamoeba coli': 'entamoeba_coli', 'Chilomastix mesnili': 'chilomastix_mesnili'}
# Recorte adicional MANUAL (px do arquivo original), além do srcRect do docx. Vazio: o recorte do
# próprio docx já exclui a barra do QuickTime Player visível na mídia original da foto 6.
EXTRA_CROP = {}
MAX_SIDE = 1600


def main(path):
    z = zipfile.ZipFile(path)
    doc = ET.fromstring(z.read('word/document.xml'))
    rels = ET.fromstring(z.read('word/_rels/document.xml.rels'))
    target = {r.get('Id'): r.get('Target') for r in rels}
    items, pending, counter = [], None, {}
    for p in doc.iter('{%s}p' % NS['w']):
        text = ''.join(t.text or '' for t in p.iter('{%s}t' % NS['w'])).strip()
        blip = p.find('.//a:blip', NS)
        if blip is not None:
            sr = p.find('.//a:srcRect', NS)
            crop = {k: int(sr.get(k, 0)) for k in 'ltrb'} if sr is not None else {k: 0 for k in 'ltrb'}
            pending = (target[blip.get('{%s}embed' % NS['r'])], crop)
        elif text and pending:
            items.append((pending, text)); pending = None
    meta = []
    os.makedirs(OUT, exist_ok=True)
    for n, ((media, crop), caption) in enumerate(items, 1):
        sp = next((v for k, v in SPECIES.items() if k.lower() in caption.lower()), None)
        if sp is None:
            raise SystemExit(f'legenda sem espécie reconhecida: {caption!r}')
        counter[sp] = counter.get(sp, 0) + 1
        im = Image.open(io.BytesIO(z.read('word/' + media))).convert('RGB')
        W, H = im.size
        l, t, r, b = (round(W * crop['l'] / 100000), round(H * crop['t'] / 100000),
                      W - round(W * crop['r'] / 100000), H - round(H * crop['b'] / 100000))
        extra = None
        if n in EXTRA_CROP and EXTRA_CROP[n][0] == 'top':
            t += EXTRA_CROP[n][1]; extra = f'topo -{EXTRA_CROP[n][1]}px (barra do QuickTime Player)'
        im = im.crop((l, t, r, b))
        if max(im.size) > MAX_SIDE:
            k = MAX_SIDE / max(im.size); im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
        name = f'{sp}_pz{counter[sp]:02d}.jpg'
        im.save(os.path.join(OUT, name), 'JPEG', quality=88, optimize=True)
        m = re.search(r'Autora? da foto:\s*([^)]+)\)', caption, re.I)
        meta.append({'ordem': n, 'especie': sp, 'arquivo': 'protozoarios/' + name, 'legenda_docx': caption,
                     'autoria_na_legenda': m.group(1).strip() if m else None,
                     'midia_origem': media, 'tamanho_origem': [W, H], 'srcRect_docx_1e5': crop,
                     'recorte_extra': extra, 'tamanho_final': list(im.size)})
        print(name, im.size, '| autoria:', meta[-1]['autoria_na_legenda'])
    sha = hashlib.sha256(open(path, 'rb').read()).hexdigest()
    json.dump({'docx': os.path.basename(path), 'docx_sha256': sha, 'imagens': meta},
              open(os.path.join(ROOT, 'tools', 'protozoarios_import.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('docx sha256', sha)


if __name__ == '__main__':
    main(sys.argv[1])
