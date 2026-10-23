# Revisão v5 — fluxo de correção e reprodução

## Fonte única
Todo texto científico nasce em `tools/conteudo/` (um registro por afirmação: seção, texto, status, referências, evidência, nota e,
quando corrigido, o texto anterior). Daí saem, por construção, o **site**, o **app** e o **documento** — por isso concordam.

```
tools/conteudo/*.py ─► tools/aplicar-conteudo.py ─► public/data/*.json ─┬─► site (public/)
                                                                        ├─► flutter_app/tool/sync_assets.py ─► app (+ manifest.json com SHA-256)
                                                                        └─► tools/gerar-documento.py ─► docs/*.docx ─► (soffice) ─► .pdf
```

## Como revisar e corrigir
1. Leia `docs/Atlas_Parasitologia_Documento_de_Revisao.docx` (ou o PDF). Cada afirmação tem ID (ex.: `ancilostomideo#03`), status, fontes e evidência.
2. Corrija o texto no registro correspondente em `tools/conteudo/{nema,plat,proto,extras}.py` (referências novas em `refs.py`).
3. Regenerar e conferir:
```bash
python3 tools/aplicar-conteudo.py
node tools/validar-dados.mjs
python3 flutter_app/tool/sync_assets.py
python3 flutter_app/tool/verify_contract.py
python3 tools/gerar-documento.py
(cd docs && soffice --headless --convert-to pdf Atlas_Parasitologia_Documento_de_Revisao.docx)
python3 tools/conferir-documento.py     # falha se o documento não contiver todo o conteúdo dos JSON ou se app ≠ site
```

## Status das afirmações
confirmado · corrigido (guarda o texto anterior) · ressalva · observação da lâmina. O que não foi sustentado por fonte lida foi **retirado**
e listado (por espécie, no app, e na seção 9 do documento). A versão anterior completa está em `acervo-nao-publicado/versao_anterior_v4.2/`.

## O que NÃO foi verificado
- O código Dart nunca foi compilado nem executado aqui (sem Flutter/Android SDK): só análise sintática e de contrato. Rode `flutter analyze` e `flutter test`.
- Os trechos de evidência em inglês vêm de um leitor automático de páginas (extração/resumo): confira na fonte antes de citar.
- Protocolos: revisados em 17/10/2026, não reavaliados em 23/10/2026.
- Livros-texto da disciplina: não consultados.
- Espécie nas fotos de protozoários: conforme legenda do documento `Laminas_de_Protozoarios.docx` (SHA-256 no documento de revisão).
- Autoria: só Júlia e Maria Luiza (Chilomastix) constam no documento de origem, sem sobrenome; as outras 4 fotos estão “a confirmar”. Nada foi presumido.
- Imagens externas sem crédito (S. mansoni; Giardia e E. histolytica ext01).
