#!/usr/bin/env python3
"""Verificações estáticas do app Flutter que NÃO exigem o SDK do Flutter.

1. Sintaxe de todos os .dart (tree-sitter-dart, se instalado).
2. Imports relativos/`package:atlas_parasitologia` resolvem para arquivos existentes.
3. Contrato de dados: chaves/tipos que models.dart lê existem nos JSON de assets/.
4. Todo arquivo de imagem referenciado existe e está num diretório declarado no pubspec
   (a declaração de diretório de assets do Flutter NÃO é recursiva).
5. manifest.json confere com os arquivos (sha256 de cada um e combinado).

Uso: python3 tool/verify_contract.py   (código de saída 0 = tudo ok)
Isto NÃO substitui `flutter analyze` / `flutter test`.
"""
import glob, hashlib, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
fails, notes = [], []


def fail(msg):
    fails.append(msg)


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


# 1 -- sintaxe -------------------------------------------------------------
dart_files = sorted(glob.glob('lib/**/*.dart', recursive=True) + glob.glob('test/**/*.dart', recursive=True))
try:
    import tree_sitter_dart as tsd
    from tree_sitter import Language, Parser
    parser = Parser(Language(tsd.language()))

    def has_error(n):
        return n.type == 'ERROR' or n.is_missing or any(has_error(c) for c in n.children)

    for f in dart_files:
        if has_error(parser.parse(open(f, 'rb').read()).root_node):
            fail(f'sintaxe: erro de parsing em {f}')
    notes.append(f'sintaxe: {len(dart_files)} arquivos .dart analisados (tree-sitter-dart)')
except ImportError:
    notes.append('sintaxe: tree-sitter-dart ausente; verificação PULADA')

# 2 -- imports ---------------------------------------------------------------
imp = re.compile(r"""^\s*(?:import|export)\s+['"]([^'"]+)['"]""", re.M)
for f in dart_files:
    for target in imp.findall(open(f, encoding='utf-8').read()):
        if target.startswith('dart:') or target.startswith('package:flutter'):
            continue
        if target.startswith('package:atlas_parasitologia/'):
            path = os.path.join('lib', target[len('package:atlas_parasitologia/'):])
        elif target.startswith('package:'):
            if 'flutter_test' not in target and 'path' not in target:
                fail(f'import de pacote não declarado no pubspec: {target} ({f})')
            continue
        else:
            path = os.path.normpath(os.path.join(os.path.dirname(f), target))
        if not os.path.exists(path):
            fail(f'import não resolve: {target} em {f}')
notes.append('imports: relativos resolvidos')

# 3 -- contrato de dados ---------------------------------------------------------
def load(p):
    with open(p, encoding='utf-8') as fh:
        return json.load(fh)

def need(obj, keys, where, types=None):
    for k in keys:
        if k not in obj:
            fail(f'contrato: {where} sem chave "{k}"')
        elif types and k in types and not isinstance(obj[k], types[k]):
            fail(f'contrato: {where}.{k} com tipo {type(obj[k]).__name__}, esperado {types[k]}')

reg = load('assets/data/modulos.json')
need(reg, ['modules'], 'modulos.json', {'modules': list})
counts = {}
img_files = []
for m in reg['modules']:
    need(m, ['id', 'order', 'title', 'dataFile', 'status'], f'módulo {m.get("id")}')
    dfp = os.path.join('assets', m['dataFile'])
    if not os.path.exists(dfp):
        fail(f'dataFile ausente: {dfp}')
        continue
    d = load(dfp)
    need(d, ['specimens'], dfp, {'specimens': list})
    n = 0
    for s in d['specimens']:
        need(s, ['id', 'commonName', 'scientificName', 'status', 'images'], f'espécie {s.get("id")}')
        if s.get('status') != 'rascunho':
            n += 1
        for im in s.get('images', []):
            need(im, ['id', 'file', 'type', 'alt'], f'imagem {im.get("id")}')
            img_files.append(im['file'])
    counts[m['id']] = n

prot = load('assets/data/protocolos.json')
need({'p': prot}, ['p'], 'protocolos.json', {'p': list})
for p in prot:
    need(p, ['id', 'title', 'reagentsAndMaterials', 'stepByStep', 'refs'], f'protocolo {p.get("id")}')
refs = load('assets/data/referencias.json')
need(refs, ['items', 'review'], 'referencias.json', {'items': list, 'review': dict})
ref_ids = {r['id'] for r in refs['items']}
for p in prot:
    for r in p.get('refs', []):
        if r not in ref_ids:
            fail(f'protocolo {p["id"]} cita referência inexistente: {r}')
    for e in p.get('evidence', []):
        for r in e.get('refs', []):
            if r not in ref_ids:
                fail(f'protocolo {p["id"]}: evidência cita referência inexistente: {r}')
    for v in p.get('verification', []):
        for r in v.get('refs', []):
            if r not in ref_ids:
                fail(f'protocolo {p["id"]}: verificação cita referência inexistente: {r}')
quiz = load('assets/data/quiz.json')
for q in quiz:
    need(q, ['id', 'question', 'options', 'correctIndex', 'explanation'], f'quiz {q.get("id")}')
    if not (isinstance(q.get('correctIndex'), int) and 0 <= q['correctIndex'] < len(q.get('options', []))):
        fail(f'quiz {q.get("id")}: correctIndex fora do intervalo')
need(load('assets/data/artefatos.json'), ['itens'], 'artefatos.json', {'itens': list})
notes.append(f'contrato: espécies por módulo {counts}; protocolos {len(prot)}; referências {len(refs["items"])}; quiz {len(quiz)}')

# 4 -- imagens e declaração de assets -------------------------------------------
pub = open('pubspec.yaml', encoding='utf-8').read()
declared = set(re.findall(r'^\s*-\s+(assets/[^\s]+/)\s*$', pub, re.M))
for fl in sorted(set(img_files)):
    path = os.path.join('assets', 'img', fl)
    if not os.path.exists(path):
        fail(f'imagem referenciada não existe: {path}')
    elif os.path.dirname(path) + '/' not in declared:
        fail(f'diretório não declarado no pubspec: {os.path.dirname(path)}/')
for dpath in ['assets/data/', 'assets/data/modulos/']:
    if dpath not in declared:
        fail(f'pubspec não declara {dpath}')
notes.append(f'imagens: {len(set(img_files))} arquivos referenciados, todos presentes e em diretórios declarados')

# 4b -- identidade visual
for bf in ['brand/logo_mark.png', 'brand/logo_tile.png', 'brand/logo.svg', 'brand/ufam_logo.png', 'brand/ufam_brasao.png']:
    if not os.path.exists(bf):
        fail(f'arquivo de marca ausente: {bf}')
for bf in ['brand/logo_mark.png', 'brand/logo_tile.png', 'brand/ufam_logo.png', 'brand/ufam_brasao.png']:
    if f'- {bf}' not in pub:
        fail(f'pubspec não declara {bf}')
for dart in dart_files:
    for ref in re.findall(r"Image\.asset\(\s*'(brand/[^']+)'", open(dart, encoding='utf-8').read()):
        if not os.path.exists(ref):
            fail(f'{dart} referencia asset inexistente: {ref}')
notes.append('marca: brand/ presente, declarada no pubspec e referenciada corretamente')

# 5 -- manifesto --------------------------------------------------------------
man = load('assets/data/manifest.json')
entries = []
for rel, h in sorted(man['files'].items()) if isinstance(man['files'], dict) else sorted((x['path'], x['sha256']) for x in man['files']):
    p = os.path.join('assets', rel)
    if not os.path.exists(p):
        fail(f'manifesto lista arquivo ausente: {rel}')
    elif sha(p) != h:
        fail(f'sha256 diverge: {rel}')
    entries.append((rel, h))
comb = hashlib.sha256(''.join(f'{r}\0{h}\n' for r, h in entries).encode()).hexdigest()
if comb != man['combinedSha256']:
    fail('sha256 combinado diverge do manifesto')
on_disk = {os.path.relpath(p, 'assets') for p in glob.glob('assets/**/*', recursive=True) if os.path.isfile(p)} - {'data/manifest.json'}
if on_disk != {r for r, _ in entries}:
    fail(f'arquivos em assets/ fora do manifesto: {sorted(on_disk ^ {r for r, _ in entries})[:5]}')
notes.append(f'manifesto: {len(entries)} arquivos conferidos; sha256 combinado {comb[:12]}…')

print('\n'.join('• ' + n for n in notes))
if fails:
    print('\nFALHAS:')
    print('\n'.join('  ✗ ' + f for f in fails))
    sys.exit(1)
print('\nOK — nenhuma falha. (Isto não substitui flutter analyze / flutter test.)')
