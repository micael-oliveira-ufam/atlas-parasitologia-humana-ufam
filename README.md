# Atlas Digital de Parasitologia Humana — v5 (UFAM · modular, estático + app Android)

Universidade Federal do Amazonas (UFAM) · Desenvolvimento: Micael Davi Lima de Oliveira e Elias de Souza Barros · Orientação: Profa. Dra. Jaila Dias Borges Lalwani.

**Documento de revisão (todas as lâminas, descrições, metodologias, fontes e verificação afirmação a afirmação):** `docs/Atlas_Parasitologia_Documento_de_Revisao.docx` (e `.pdf`). Veja `docs/REVISAO_V5.md` para o fluxo de correção e a reprodução.

## 📱 Baixar o aplicativo (somente Android)

**[⬇️ Atlas-Parasitologia-v2.0.0.apk](https://github.com/micael-oliveira-ufam/atlas-parasitologia-humana-ufam/releases/download/v2.0.0/Atlas-Parasitologia-v2.0.0.apk)** · [todas as versões](https://github.com/micael-oliveira-ufam/atlas-parasitologia-humana-ufam/releases)

> ⚠️ O aplicativo é **apenas para Android** (não existe versão para iPhone/iOS). No iPhone ou no computador, use o site.
> Instalação: baixe o APK no celular, abra o arquivo e permita a instalação de fontes desconhecidas quando o Android pedir.
> SHA-256 do APK: `92cdd08fcfe07c0d67c6356724617c9fdf0607f9ccd13fd13d6a75b4cb74cd44`

**Site:** https://micael-oliveira-ufam.github.io/atlas-parasitologia-humana-ufam/

Site 100 % estático (HTML + CSS + JavaScript puro, **sem build, sem backend, sem dependências**), pronto para Cloudflare.

```
public/                  ← TUDO que é publicado (Cloudflare serve esta pasta)
  index.html
  _headers               ← cabeçalhos de segurança/cache (Cloudflare Pages)
  assets/{css,js,img}/
  data/
    modulos.json         ← registro dos módulos + créditos do site
    modulos/             ← uma lâmina-lista por módulo
      nematelmintos.json
      platelmintos.json
      protozoarios.json
    quiz.json  protocolos.json  artefatos.json
tools/                   ← servidor local, link Cloudflare, atlas-docker.sh, validador, preparar-imagem.py (não publicados)
docker/                  ← Dockerfile + nginx.conf usados por tools/atlas-docker.sh
acervo-nao-publicado/    ← fotos que não foram para o site
docs/                    ← guias (adicionar lâminas/módulos, migração, Docker, REVISAO_LITERATURA.md)
legacy/                  ← dados originais intactos + relatório de migração
```

## 0. Publicar grátis no GitHub Pages
Veja `docs/GITHUB_PAGES.md` (workflow `.github/workflows/pages.yml` já incluído).

## 1. Ver localmente
```bash
python3 tools/servir.py          # http://127.0.0.1:8080
```
É preciso servir por HTTP: abrir `index.html` com duplo clique (file://) não carrega os JSON.

## 2. Gerar um link aleatório do Cloudflare (Quick Tunnel)
Requer o [`cloudflared`](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/) instalado (sem conta).
```bash
./tools/link-aleatorio-cloudflare.sh        # Linux/macOS
tools\link-aleatorio-cloudflare.bat         # Windows
```
O terminal imprime um endereço `https://<palavras-aleatórias>.trycloudflare.com`. **O link só existe enquanto o script estiver rodando e o computador ligado**; um novo link é gerado a cada execução. Serve para demonstrações e aulas.

## 2b. Docker (servidor próprio)
```bash
tools/atlas-docker.sh up      # constrói, sobe e testa em http://IP:8080  (veja docs/DOCKER.md)
tools/atlas-docker.sh link    # link aleatório trycloudflare.com a partir do contêiner
```

## 3. Hospedagem permanente: Cloudflare Pages
- **Painel:** Workers & Pages → Create → Pages → *Upload assets* → arraste a pasta `public/`.
- **Linha de comando:** `npx wrangler pages deploy public --project-name=atlas-parasitologia`

Não há comando de build; o diretório de saída é `public`. O endereço permanente é `<nome-do-projeto>.pages.dev` (o nome é escolhido por você); cada deploy também ganha um endereço próprio com prefixo hash. O arquivo `_headers` é aplicado automaticamente (CSP restritiva: só recursos do próprio site, nenhuma fonte/CDN externa).

## 4. Validar os dados antes de publicar
```bash
node tools/validar-dados.mjs
```
Verifica ids únicos, existência e dimensões reais das imagens, faixa dos marcadores, status válidos, índice de resposta do quiz etc.

## 5. Adicionar lâminas ou módulos
Veja `docs/ADICIONAR_LAMINAS.md`. Resumo: foto em `public/assets/img/<modulo>/` + objeto em `public/data/modulos/<modulo>.json`.

## Rotas
`#/` início · `#/m/<modulo>` · `#/m/<modulo>/<id>` · `#/quiz` · `#/protocolos` · `#/artefatos` · `#/busca?q=…` · `#/sobre` (roteamento por hash: não exige regras de redirecionamento no Cloudflare).

## Estado atual dos dados
Fotos reais de lâmina (21 lâminas, importadas do PDF *Resumo de lâminas — Nematelmintos*), organizadas em galerias por espécie:

| Módulo | Espécies | Observação |
|---|---|---|
| Nematelmintos | Ancilostomídeo, *Ascaris*, *Enterobius*, *Strongyloides*, *Trichuris* (14 lâminas) | |
| Platelmintos | *Taenia* sp., *H. nana* (7 lâminas) + *Schistosoma* (em revisão, imagem externa) | |
| Protozoários | *Giardia*, *Entamoeba* — ambas em revisão (imagens externas); módulo “em construção” | |

Pontos de atenção: as fotos estão em **miniatura** (substituir pelos originais com `tools/preparar-imagem.py`); #20–#23 têm crédito marcado “a confirmar”; marcadores estruturais ainda não foram refeitos. Detalhes em **`docs/MIGRACAO.md`**. `acervo-nao-publicado/` guarda as lâminas #1 e #14 (fora do site).

## Testes realizados
Protocolos: conferidos com a literatura em 17/10/2026 (não é validação analítica; ver `docs/REVISAO_LITERATURA.md`).

Navegador headless (Chromium) sob a CSP de produção: rotas de módulo, espécie (troca de imagem na galeria, zoom, imagem ampliada ao clicar), busca, artefatos, sobre, quiz e protocolos, sem erros de console nem requisições com falha; sem rolagem horizontal em 390 px; validador com testes negativos.

## Aplicativo Android (Flutter)

Versão offline em `flutter_app/` — veja `docs/ANDROID.md` (inclui o que foi e o que **não** foi verificado). Gerar o APK: `cd flutter_app && tool/build_apk.sh`.
