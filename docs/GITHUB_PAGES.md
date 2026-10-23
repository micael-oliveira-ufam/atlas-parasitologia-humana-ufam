# Publicar o site no GitHub Pages (gratuito)

O site é 100 % estático e usa só caminhos relativos, então funciona em `https://SEU-USUARIO.github.io/NOME-DO-REPOSITORIO/`.

## Passo a passo
1. Crie um repositório no GitHub (público, para Pages gratuito) e envie o projeto:
   ```bash
   cd atlas-parasitologia
   git init -b main
   git add . && git commit -m "Atlas de Parasitologia v5"
   git remote add origin https://github.com/SEU-USUARIO/NOME-DO-REPOSITORIO.git
   git push -u origin main
   ```
2. No GitHub: **Settings → Pages → Build and deployment → Source: GitHub Actions** (uma única vez).
3. O workflow `.github/workflows/pages.yml` roda a cada push em `main` que altere `public/`: valida os dados (`tools/validar-dados.mjs`) e publica a pasta `public/`. Acompanhe em **Actions**; o link final aparece no job *deploy*.
4. Para atualizar: corrija em `tools/conteudo/`, rode `python3 tools/aplicar-conteudo.py`, faça commit e push.

## Observações
- `public/.nojekyll` evita o processamento Jekyll. O arquivo `public/_headers` é específico do Cloudflare e é ignorado pelo GitHub Pages (que define seus próprios cabeçalhos).
- A navegação usa `#/` (hash), portanto não precisa de regra de redirecionamento.
- Repositório privado só tem Pages em planos pagos; o conteúdo publicado é sempre público. Antes de publicar, confira os créditos pendentes (fotos “a confirmar”) e as imagens externas sem licença documentada.
- Um domínio próprio pode ser definido em Settings → Pages → Custom domain.
