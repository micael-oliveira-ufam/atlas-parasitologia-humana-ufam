# Como adicionar lâminas (ex.: módulo de Protozoários)

O atlas é **orientado a dados**: nenhuma alteração de código é necessária para adicionar lâminas ou módulos.

## 1. Adicionar fotos a uma espécie (ou criar uma espécie nova)
Cada **espécie** é um objeto em `public/data/modulos/<modulo>.json` com uma **galeria** `images[]` (uma entrada por foto). Modelo completo em `docs/modelo-lamina.json`.
1. Prepare a foto original (retira EXIF/GPS e reduz o tamanho):
   `python3 tools/preparar-imagem.py FOTO.jpg --saida public/assets/img/protozoarios/giardia_duodenalis_lam01_detalhe.jpg`
   (o comando imprime `width` e `height` para colar no JSON; requer `pip install pillow`).
2. Acrescente a entrada em `images[]` (ou crie a espécie copiando `docs/modelo-lamina.json`).
3. `node tools/validar-dados.mjs` (ids únicos, arquivo existente, dimensões reais, marcadores 0–100, imagens órfãs…).
4. Teste: `python3 tools/servir.py` → http://127.0.0.1:8080.

### Campos de cada imagem (integridade científica)
| Campo | Regra |
|---|---|
| `type` | `microfotografia` (foto de lâmina real), `ilustracao` ou `externa` (figura de terceiros). O site mostra selo diferente para cada um. |
| `kind` / `lamina` | `detalhe` (ampliação do parasito) ou `campo` (campo geral); `lamina` é o número da lâmina. |
| `confidence` | `confirmada` (conferida por você/docente), `alta` ou `media` (aparece como “a confirmar”). Fotos de identificação duvidosa **não devem ser publicadas**: guarde em `acervo-nao-publicado/`. |
| `credit` / `license` | Quem fotografou e sob que uso. Vazio = o site mostra “origem a confirmar”. Figuras de livros/artigos exigem permissão. |
| `creditStatus` | `informado` (autoria declarada) ou `a-confirmar` (o site exibe a etiqueta “Autoria a confirmar”). |
| `date` / `dateBasis` | Data da foto (`AAAA-MM-DD`) e de onde ela veio (ex.: “data no nome do arquivo da câmera”). Opcional. |
| `hotspots` | Marcadores opcionais por imagem; `x`,`y` em % (0–100, origem no canto superior esquerdo): x = pixel_x/largura×100. |
| `sourceFile` | Nome do arquivo original (rastreabilidade). |

Campos da espécie: `status` = `publicado` · `revisar` (faixa vermelha; exige `reviewNote`) · `rascunho` (oculto). `approxSizeMicrons` deve ser valor de literatura com fonte, ou medida real feita sobre foto com escala.

## 2. Substituir miniaturas por originais
As fotos atuais vieram do PDF em miniatura (360×360 e 480×640 px). Para trocar: rode `preparar-imagem.py` no original usando **o mesmo nome de arquivo** e atualize `width`/`height` no JSON (o validador acusa divergência).

## 3. Criar um novo módulo (ex.: Artrópodes, Helmintos de tecido)
1. Crie `public/data/modulos/<id>.json` com `{ "specimens": [] }`.
2. Crie a pasta `public/assets/img/<id>/`.
3. Em `public/data/modulos.json`, acrescente à lista `modules`:
```json
{ "id": "artropodes", "order": 4, "title": "Artrópodes", "subtitle": "…", "description": "…",
  "status": "ativo", "accent": "teal", "dataFile": "data/modulos/artropodes.json" }
```
`accent` aceita `teal`, `amber` ou `violet`; `status` aceita `ativo` ou `em-construcao`. O menu, a página inicial, a busca e o quiz (via `module` nas questões) passam a reconhecê-lo automaticamente.

## 4. Quiz
Em `public/data/quiz.json`, cada questão tem `module` (`nematelmintos`, `platelmintos`, `protozoarios` ou `geral`) e `correctIndex` (posição da resposta certa em `options`, começando em 0). As alternativas são embaralhadas a cada tentativa.
