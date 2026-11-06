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

## Atualização de 06/11/2026 — lâminas de protozoários
- Documento-fonte substituído por `Laminas_de_Protozoarios.docx` (25 imagens). Versão anterior arquivada em `acervo-nao-publicado/versao_anterior_laminas_v5/`.
- Imagens extraídas por `tools/importar-docx-protozoarios.py` (recorte pelo srcRect do docx, máximo 1600 px); 27 registros em 25 arquivos; a lâmina composta (De cima para baixo: E. coli, Endolimax, Iodamoeba) é compartilhada.
- Novas espécies **em revisão** (sem morfologia exibida): *Blastocystis* sp. (CDC DPDx lido em 06/11/2026) e *Iodamoeba buetschlii* (worldspecies, lido em 06/11/2026; grafia “butschlii” tratada como sinônimo). Taxid NCBI da Iodamoeba **não confirmado**.
- Fotos externas de *E. histolytica* e *Giardia* removidas do módulo (arquivadas em `acervo-nao-publicado/imagens_externas_removidas_v5/`).
- Autoria: somente o que a legenda informa; sem sobrenome, “sobrenome a confirmar”; sem autoria, “Autoria não informada (a confirmar)”.
- Site: seções sem conteúdo deixam de aparecer nas espécies em revisão (correção em `specimen.js`).
- Morfologia e doença detalhadas de todas as 15 espécies a partir de páginas oficiais do CDC (DPDx e CDC), lidas em 06/11/2026 (`tools/conteudo/cdc_detalhe.py`): 73 registros novos; afirmações verificadas passaram de 274 para 347. Os trechos são paráfrases do leitor automático de páginas, sinalizadas como tal em cada registro; conferir o trecho literal antes de citar.
- Dados ausentes na página do CDC ficam marcados como ressalva (ex.: dimensões dos ovos de *S. stercoralis*, flagelos da *Giardia*, cercária e miracídio da *Schistosoma*, cisto da *Chilomastix*, sintomas do *Blastocystis*).
- Retirado: "flagelos (8)" da *Giardia* (não reconfirmado na leitura de 06/11/2026); "papel em doença incerto" da *Chilomastix* (a página diz apenas "considered nonpathogenic").
- *Blastocystis* e *Iodamoeba* passam a exibir morfologia (seguem "em revisão" pela literatura ainda não validada).

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
