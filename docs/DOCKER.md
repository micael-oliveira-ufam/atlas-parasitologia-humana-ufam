# Executar o Atlas em Docker (servidor)

Imagem de produção baseada em **nginx não-root** (`nginxinc/nginx-unprivileged:1.27-alpine`), contendo só `public/`.
Tudo é controlado por **`tools/atlas-docker.sh`** (bash).

## Requisitos
Docker Engine 23+ (BuildKit), `bash`, `curl`. Opcional: `node` (o script valida os dados antes de construir). Em Debian/Ubuntu sem Docker: `tools/atlas-docker.sh install-docker`.

## Início rápido
```bash
tools/atlas-docker.sh up                 # valida → constrói → sobe → testa   (http://IP-DO-SERVIDOR:8080)
tools/atlas-docker.sh up --port 80       # outra porta
tools/atlas-docker.sh up --local         # só 127.0.0.1 (para ficar atrás de proxy reverso)
tools/atlas-docker.sh link               # link aleatório https://….trycloudflare.com (Cloudflare Quick Tunnel)
```

| Comando | O que faz |
|---|---|
| `up` | `build` + recria o contêiner + espera ficar saudável + `test` |
| `build` / `down` / `restart` | construir a imagem / remover o contêiner / reiniciar |
| `status` | estado, saúde, portas, **sha256 do conteúdo** da imagem e se `public/` mudou desde o build |
| `logs [-f]` | logs do nginx |
| `test` | 9 testes HTTP (saúde, página, JSON, JS, imagem, CSP, `nosniff`, `/_headers` oculto, 404) |
| `link` / `unlink` | abre/fecha um túnel Cloudflare temporário em um contêiner auxiliar |
| `save [arq.tar.gz]` | exporta a imagem + arquivo `.sha256` para levar a outro servidor |
| `install-docker` | instala `docker.io` via apt (Debian/Ubuntu) |

Opções: `-p/--port`, `-b/--bind`, `--local`, `-n/--name`, `--no-cache`. Variáveis: `BASE_IMAGE`, `CLOUDFLARED_IMAGE`.

## O que o script garante
- **Contexto mínimo:** só `public/` e `docker/` entram na imagem (nunca `legacy/`, `docs/`, `acervo-nao-publicado/`, `tools/`). Permissões são normalizadas para o usuário não-root do nginx ler tudo.
- **Rastreabilidade:** a imagem recebe a etiqueta `atlas.content-sha256` (hash de nomes+conteúdo de `public/`) e a tag `atlas-parasitologia:<12 primeiros dígitos>`. Mesmo conteúdo ⇒ mesmo hash. Para fixar também a base, use `BASE_IMAGE=nginxinc/nginx-unprivileged@sha256:<digest>`.
- **Endurecimento do contêiner:** sistema de arquivos somente leitura (`/tmp` em tmpfs sem exec), `--cap-drop ALL`, `no-new-privileges`, limite de 256 MB e 100 processos, logs rotacionados, `--restart unless-stopped` (volta após reinício do servidor) e `HEALTHCHECK`.
- **Cabeçalhos** idênticos aos de `public/_headers` (CSP restritiva, `nosniff`, `frame-ancestors 'none'`…), gzip, `data/*` sem cache (edições aparecem de imediato) e imagens com revalidação (1 h + ETag), então trocar uma foto mantendo o nome funciona.

## Publicar em um servidor
**A. Construir no servidor:** copie o projeto (`scp -r`/git) e rode `tools/atlas-docker.sh up`.
**B. Construir aqui, levar a imagem:**
```bash
tools/atlas-docker.sh save                         # gera atlas-parasitologia-AAAAMMDD.tar.gz (+ .sha256)
# no servidor:
sha256sum -c atlas-parasitologia-*.tar.gz.sha256
gunzip -c atlas-parasitologia-*.tar.gz | docker load
docker run -d --name atlas-parasitologia --restart unless-stopped -p 80:8080 --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=16m --cap-drop ALL --security-opt no-new-privileges:true atlas-parasitologia:latest
```
**Atualizar conteúdo:** edite `public/` (ex.: JSON/fotos), rode `node tools/validar-dados.mjs` e `tools/atlas-docker.sh up` (indisponível por poucos segundos).

## HTTPS (obrigatório para uso público)
O contêiner serve HTTP. Opções:
1. **Cloudflare Tunnel permanente** (sem abrir portas): crie o túnel no painel Zero Trust e rode `docker run -d --restart unless-stopped --network container:atlas-parasitologia cloudflare/cloudflared tunnel --no-autoupdate run --token <TOKEN>` apontando o serviço para `http://localhost:8080`.
2. **Caddy** (certificado automático) no host, com o atlas em `--local --port 8080`:
   ```
   atlas.seudominio.com {
       reverse_proxy 127.0.0.1:8080
   }
   ```
3. **nginx/Traefik + Certbot** como proxy reverso para `127.0.0.1:8080`.
Com firewall (ex.: `ufw`), libere 80/443 e **não** a 8080 quando usar proxy (`--local` já a restringe ao host). Lembre: portas publicadas pelo Docker contornam regras do `ufw`; por isso `--local` é a forma segura.

## Verificação realizada (e limites)
Testado neste ambiente com um daemon Docker real: sintaxe do script, validação de argumentos, **build**, contêiner somente-leitura sem capabilities, healthcheck, `test` (9/9), `status`, `logs`, `restart`, detecção de mudança em `public/`, `save` + `.sha256`, `down`, e que a imagem **não** contém `legacy/`/`acervo-nao-publicado/`.
**Não foi possível testar** (o ambiente bloqueia Docker Hub e outros registros): o **nginx real** (`docker/nginx.conf` foi revisado, mas não passou por `nginx -t`), o comportamento da imagem `nginx-unprivileged` com `--read-only`, e `link` (imagem `cloudflared`). Os testes do fluxo usaram uma imagem-base substituta mínima (servidor Python com os mesmos cabeçalhos). **No seu servidor, rode `tools/atlas-docker.sh up`: o `test` embutido valida o nginx de verdade** e, se algo falhar, `logs` mostra o motivo (o ponto mais provável de ajuste seria o `--read-only`; nesse caso remova-o da linha `docker run` em `cmd_run`).
