#!/usr/bin/env python3
"""Prepara fotos originais do celular/microscópio para o atlas.
- reduz para no máx. 2000 px no maior lado (ajuste com --max)
- REMOVE metadados EXIF (inclui GPS e data), respeitando a orientação da foto
- salva JPEG (qualidade 86) e imprime o trecho JSON com width/height
Uso:  python3 tools/preparar-imagem.py FOTO.jpg --saida public/assets/img/nematelmintos/ascaris_lumbricoides_lam05_detalhe.jpg
Requer: pip install pillow"""
import argparse, json, sys
from PIL import Image, ImageOps
ap = argparse.ArgumentParser(); ap.add_argument('entrada'); ap.add_argument('--saida', required=True); ap.add_argument('--max', type=int, default=2000)
a = ap.parse_args()
im = ImageOps.exif_transpose(Image.open(a.entrada)).convert('RGB')   # aplica rotação do EXIF antes de descartá-lo
im.thumbnail((a.max, a.max), Image.LANCZOS)
im.save(a.saida, 'JPEG', quality=86, optimize=True)                  # sem exif=...: metadados não são gravados
print(json.dumps({'file': a.saida.split('assets/img/')[-1], 'width': im.width, 'height': im.height}, ensure_ascii=False))
