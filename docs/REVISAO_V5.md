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
- Novas espécies **em revisão** (morfologia da página do CDC exibida; texto ainda não validado pela literatura): *Blastocystis* sp. (CDC DPDx lido em 06/11/2026) e *Iodamoeba buetschlii* (worldspecies, lido em 06/11/2026; grafia “butschlii” tratada como sinônimo). Taxid NCBI da Iodamoeba **não confirmado**.
- Fotos externas de *E. histolytica* e *Giardia* removidas do módulo (arquivadas em `acervo-nao-publicado/imagens_externas_removidas_v5/`).
- Autoria: somente o que a legenda informa; sem sobrenome, “sobrenome a confirmar”; sem autoria, “Autoria não informada (a confirmar)”.
- Site: seções sem conteúdo deixam de aparecer nas espécies em revisão (correção em `specimen.js`).
- Morfologia e doença detalhadas de todas as 15 espécies a partir de páginas oficiais do CDC (DPDx e CDC), lidas em 06/11/2026 (`tools/conteudo/cdc_detalhe.py`): 73 registros novos; afirmações verificadas passaram de 274 para 347. Os trechos são paráfrases do leitor automático de páginas, sinalizadas como tal em cada registro; conferir o trecho literal antes de citar.
- Dados ausentes na página do CDC ficam marcados como ressalva (ex.: dimensões dos ovos de *S. stercoralis*, flagelos da *Giardia*, cercária e miracídio da *Schistosoma*, cisto da *Chilomastix*, sintomas do *Blastocystis*).
- Retirado: "flagelos (8)" da *Giardia* (não reconfirmado na leitura de 06/11/2026); "papel em doença incerto" da *Chilomastix* (a página diz apenas "considered nonpathogenic").
- *Blastocystis* e *Iodamoeba* passam a exibir morfologia (seguem "em revisão" pela literatura ainda não validada).

## Atualização de 25/11/2026 — lâminas v4 e nova interface
- Fonte: `docs/fontes/Laminas_Parasitologia_v4.docx` (tabela de 32 figuras; cada uma com foto + "ampliação digital" 440×440). Importação reprodutível: `python3 -I tools/importar-docx-laminas-v4.py docs/fontes/Laminas_Parasitologia_v4.docx` → `tools/laminas_v4_import.json` (hash do docx e metadados de cada figura).
- Resultado: 29 fotos novas em espécies existentes; a Fig. 32 coincidiu (hash perceptual, distância ≤ 6) com foto já no catálogo (*E. histolytica*, pz02) e só recebeu a ampliação; 2 figuras (Fig. 2 e 7) são "estrutura não identificada" e ficam em **Artefatos → Estruturas sem identificação segura**, sem atribuição a espécie.
- Legendas, identificações e a "objetiva estimada (40×)" são **dos autores do documento**; apenas a Fig. 31 foi conferida com a página do CDC (os detalhes do cisto não constam nessa página; a fonte Garcia 2018, citada na legenda, **não foi lida**). Referências numeradas da legenda foram mapeadas para as fontes DPDx já lidas.
- Autoria das fotos: **não informada** no documento. "Lâmina feita/obtida por Indira / Maria Eduarda" é preparo da lâmina, não autoria da foto; sobrenomes "a confirmar".
- Resolução: fotos 1100 px e ampliações 440 px (limite do docx); 45 imagens abaixo de 800 px aparecem como aviso no validador.
- Removidas do repositório 4 imagens externas antigas de *E. histolytica* e *Giardia* (sem crédito; já estavam retiradas da exibição).
- Site: nova interface (tokens de design, tema claro/escuro, menu lateral no celular, cartões com mosaico). **Zoom reescrito**: a ficha tem galeria estática (a rolagem da página não é capturada); tocar abre visualizador em tela cheia com pinça, toque duplo, arrastar, roda/teclado, deslizar para trocar ou fechar, botão "voltar" do celular fecha o visualizador, brilho/contraste e alternância foto/ampliação. Testado em Chromium (Pixel 5 emulado e desktop) com eventos de toque via CDP; **não** testado em aparelho físico.
- Marcadores estruturais (hotspots): nenhum registro os usa; o painel foi removido da ficha (o motor de zoom mantém suporte).
- App Flutter: **não** recebeu a nova interface/zoom nem exibe `detail`, `figure` e a seção de estruturas sem identificação; apenas os dados e imagens foram sincronizados (`sync_assets.py`; testes Dart ajustados: 52 referências; protozoários 42 registros em 40 arquivos). Dart não foi compilado.

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
