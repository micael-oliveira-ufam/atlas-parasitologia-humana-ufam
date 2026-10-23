#!/usr/bin/env bash
# =============================================================================
# atlas-docker.sh — constrói e executa o Atlas Digital de Parasitologia em Docker
# (nginx não-root, somente leitura, com os mesmos cabeçalhos de segurança do Cloudflare).
#
# Uso:  tools/atlas-docker.sh <comando> [opções]
#
# Comandos
#   up              constrói a imagem, (re)cria o contêiner e testa    (padrão)
#   build           só constrói a imagem
#   down            para e remove o contêiner (a imagem permanece)
#   restart         reinicia o contêiner
#   status          estado, saúde, porta, versão do conteúdo (sha256)
#   logs [-f]       mostra os logs (-f para acompanhar)
#   test            testes de fumaça HTTP contra o contêiner em execução
#   link            gera um link aleatório https://*.trycloudflare.com (Cloudflare Quick Tunnel)
#   unlink          encerra o túnel
#   save [arquivo]  exporta a imagem (.tar.gz) para levar a outro servidor
#   install-docker  instala o Docker via apt (Debian/Ubuntu; pede sudo)
#   help            esta ajuda
#
# Opções
#   -p, --port N        porta publicada no host            (padrão 8080)
#   -b, --bind IP       interface do host                  (padrão 0.0.0.0 = acessível pela rede)
#       --local         atalho para --bind 127.0.0.1 (só esta máquina / atrás de proxy reverso)
#   -n, --name NOME     nome do contêiner                  (padrão atlas-parasitologia)
#       --no-cache      constrói sem cache
#
# Variáveis de ambiente opcionais
#   BASE_IMAGE          imagem base (padrão nginxinc/nginx-unprivileged:1.27-alpine)
#   CLOUDFLARED_IMAGE   imagem do túnel (padrão cloudflare/cloudflared:latest)
# =============================================================================
set -Eeuo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

NAME="atlas-parasitologia"
PORT="8080"
BIND="0.0.0.0"
NO_CACHE=""
BASE_IMAGE="${BASE_IMAGE:-nginxinc/nginx-unprivileged:1.27-alpine}"
CLOUDFLARED_IMAGE="${CLOUDFLARED_IMAGE:-cloudflare/cloudflared:latest}"
IMAGE_REPO="atlas-parasitologia"
STAGE=""
trap '[[ -n "$STAGE" ]] && rm -rf "$STAGE"' EXIT

# ---------- utilidades ----------
if [[ -t 1 ]]; then B=$'\033[1m'; G=$'\033[32m'; Y=$'\033[33m'; R=$'\033[31m'; Z=$'\033[0m'; else B=""; G=""; Y=""; R=""; Z=""; fi
info() { printf '%s==>%s %s\n' "$B" "$Z" "$*"; }
ok()   { printf '%s ok%s  %s\n' "$G" "$Z" "$*"; }
warn() { printf '%saviso%s %s\n' "$Y" "$Z" "$*" >&2; }
die()  { printf '%serro%s  %s\n' "$R" "$Z" "$*" >&2; exit 1; }
usage() { awk '/^# =+$/ {c++; if (c==2) exit; next} c==1 {sub(/^# ?/, ""); print}' "${BASH_SOURCE[0]}"; }

need_docker() {
  command -v docker >/dev/null 2>&1 || die "Docker não encontrado. Instale (tools/atlas-docker.sh install-docker) ou veja https://docs.docker.com/engine/install/"
  docker info >/dev/null 2>&1 || die "Não consegui falar com o daemon do Docker. Ele está rodando? Seu usuário está no grupo 'docker' (ou use sudo)?"
}

sha256_stdin() { if command -v sha256sum >/dev/null 2>&1; then sha256sum | cut -d' ' -f1; else shasum -a 256 | cut -d' ' -f1; fi; }
sha256_file()  { if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1"; else shasum -a 256 "$1"; fi; }

# Hash reprodutível do conteúdo publicado (nomes + conteúdos, em ordem estável)
content_hash() {
  ( cd "$PROJECT_DIR/public" && find . -type f -print0 | LC_ALL=C sort -z | while IFS= read -r -d '' f; do
      printf '%s  %s\n' "$(sha256_file "$f" | cut -d' ' -f1)" "$f"; done ) | sha256_stdin
}

http_get() { # http_get URL [curl-args...]  -> corpo em stdout
  if command -v curl >/dev/null 2>&1; then curl -fsS --max-time 5 "$@"; else wget -qO- "$1"; fi
}
http_head() { if command -v curl >/dev/null 2>&1; then curl -sS -I --max-time 5 "$1"; else wget -S --spider -O /dev/null "$1" 2>&1; fi; }

container_exists()  { docker container inspect "$1" >/dev/null 2>&1; }
container_running() { [[ "$(docker container inspect -f '{{.State.Running}}' "$1" 2>/dev/null || echo false)" == "true" ]]; }

host_url_hint() {
  local ip=""
  if [[ "$BIND" == "127.0.0.1" ]]; then echo "http://127.0.0.1:${PORT}"; return; fi
  ip="$(hostname -I 2>/dev/null | awk '{print $1}')" || true
  echo "http://127.0.0.1:${PORT}   (na rede: http://${ip:-<IP-do-servidor>}:${PORT})"
}

# ---------- comandos ----------
cmd_build() {
  need_docker
  [[ -f "$PROJECT_DIR/public/index.html" ]] || die "public/index.html não encontrado em $PROJECT_DIR"
  [[ -f "$PROJECT_DIR/docker/Dockerfile" ]] || die "docker/Dockerfile não encontrado"
  if command -v node >/dev/null 2>&1 && [[ -f "$SCRIPT_DIR/validar-dados.mjs" ]]; then
    info "Validando dados antes de construir"
    node "$SCRIPT_DIR/validar-dados.mjs" | tail -3 || die "Os dados têm erros; corrija antes de publicar."
  else
    warn "node não encontrado: pulando tools/validar-dados.mjs"
  fi

  local sha
  sha="$(content_hash)"
  # Contexto de build mínimo e com permissões normalizadas (evita vazar legacy/, docs/, acervo-nao-publicado/
  # e garante que o usuário não-root do nginx consiga ler os arquivos mesmo com umask restritivo).
  STAGE="$(mktemp -d)"
  cp -R "$PROJECT_DIR/public" "$STAGE/public"
  cp -R "$PROJECT_DIR/docker" "$STAGE/docker"
  chmod -R u+rwX,go+rX "$STAGE"

  info "Construindo ${IMAGE_REPO}:${sha:0:12}  (conteúdo sha256 ${sha:0:12}…, base ${BASE_IMAGE})"
  # shellcheck disable=SC2086
  docker build $NO_CACHE \
    --build-arg "BASE_IMAGE=${BASE_IMAGE}" \
    --build-arg "CONTENT_SHA256=${sha}" \
    -t "${IMAGE_REPO}:latest" -t "${IMAGE_REPO}:${sha:0:12}" \
    -f "$STAGE/docker/Dockerfile" "$STAGE"
  ok "Imagem pronta: ${IMAGE_REPO}:latest (= ${IMAGE_REPO}:${sha:0:12})"
}

cmd_run() {
  need_docker
  docker image inspect "${IMAGE_REPO}:latest" >/dev/null 2>&1 || die "Imagem inexistente; rode 'build' ou 'up'."
  if [[ ! "$PORT" =~ ^[0-9]+$ ]] || (( PORT < 1 || PORT > 65535 )); then die "Porta inválida: $PORT"; fi
  if container_exists "${NAME}-tunnel"; then
    warn "Removendo o túnel antigo (ele perde a conexão quando o site é recriado). Rode 'link' de novo se quiser."
    docker rm -f "${NAME}-tunnel" >/dev/null
  fi
  if container_exists "$NAME"; then info "Substituindo contêiner existente '$NAME'"; docker rm -f "$NAME" >/dev/null; fi

  info "Iniciando '$NAME' em ${BIND}:${PORT}"
  docker run -d --name "$NAME" \
    --restart unless-stopped \
    --publish "${BIND}:${PORT}:8080" \
    --read-only --tmpfs /tmp:rw,noexec,nosuid,size=16m \
    --cap-drop ALL --security-opt no-new-privileges:true \
    --pids-limit 100 --memory 256m \
    --log-opt max-size=10m --log-opt max-file=3 \
    "${IMAGE_REPO}:latest" >/dev/null

  info "Aguardando o contêiner ficar saudável"
  local i status=""
  for i in $(seq 1 40); do
    status="$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}sem-healthcheck{{end}}' "$NAME" 2>/dev/null || true)"
    container_running "$NAME" || { docker logs --tail 30 "$NAME" >&2 || true; die "O contêiner parou logo após iniciar (veja os logs acima)."; }
    [[ "$status" == "healthy" ]] && break
    sleep 1
  done
  [[ "$status" == "healthy" ]] || { docker logs --tail 30 "$NAME" >&2 || true; die "Contêiner não ficou saudável em 40 s (estado: ${status:-desconhecido})."; }
  ok "Contêiner saudável"
}

cmd_test() {
  need_docker
  container_running "$NAME" || die "Contêiner '$NAME' não está rodando."
  local base="http://127.0.0.1:${PORT}" fail=0 t hdr
  check() { # check "descrição" comando...
    local d="$1"; shift
    if "$@" >/dev/null 2>&1; then ok "$d"; else printf '%s FALHA%s %s\n' "$R" "$Z" "$d"; fail=1; fi
  }
  info "Testes HTTP em $base"
  check "GET /healthz = ok"                      bash -c "[[ \"\$(curl -fsS --max-time 5 '$base/healthz')\" == ok* ]]"
  check "GET / devolve o index.html do atlas"    bash -c "curl -fsS --max-time 5 '$base/' | grep -q 'Atlas Digital de Parasitologia'"
  check "GET /data/modulos.json é JSON válido"   bash -c "curl -fsS --max-time 5 '$base/data/modulos.json' | python3 -c 'import sys,json; json.load(sys.stdin)' 2>/dev/null || curl -fsS --max-time 5 '$base/data/modulos.json' | grep -q '\"modules\"'"
  check "GET /assets/js/main.js"                 curl -fsS --max-time 5 -o /dev/null "$base/assets/js/main.js"
  hdr="$(http_head "$base/" || true)"
  check "cabeçalho Content-Security-Policy"      bash -c "grep -qi '^content-security-policy:' <<<\"\$1\"" _ "$hdr"
  check "cabeçalho X-Content-Type-Options"       bash -c "grep -qi '^x-content-type-options: *nosniff' <<<\"\$1\"" _ "$hdr"
  t="$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 "$base/_headers" || true)"
  check "/_headers não é exposto (HTTP $t)"      test "$t" = "404"
  t="$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 "$base/nao-existe" || true)"
  check "caminho inexistente = 404 (HTTP $t)"    test "$t" = "404"
  # uma imagem qualquer registrada no banco de dados
  local img; img="$(find "$PROJECT_DIR/public/assets/img" -type f \( -name '*.jpg' -o -name '*.jpeg' \) | head -1 || true)"
  if [[ -n "$img" ]]; then
    local rel="${img#"$PROJECT_DIR"/public/}"
    check "imagem ${rel##*/} servida (HTTP 200)" bash -c "[[ \"\$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 '$base/$rel')\" == 200 ]]"
  fi
  (( fail == 0 )) && ok "Todos os testes passaram" || die "Algum teste falhou."
}

cmd_up() { cmd_build; cmd_run; cmd_test; echo; ok "Atlas no ar: $(host_url_hint)"
  echo "   Próximos passos: 'link' (link aleatório Cloudflare) · 'logs -f' · 'status' · 'down'"
  echo "   Em servidor público, coloque HTTPS na frente (proxy reverso ou Cloudflare Tunnel); veja docs/DOCKER.md."; }

cmd_down() { need_docker
  container_exists "${NAME}-tunnel" && { docker rm -f "${NAME}-tunnel" >/dev/null; ok "Túnel removido"; }
  if container_exists "$NAME"; then docker rm -f "$NAME" >/dev/null; ok "Contêiner '$NAME' removido"; else warn "Contêiner '$NAME' não existe"; fi; }

cmd_restart() { need_docker; container_exists "$NAME" || die "Contêiner '$NAME' não existe; use 'up'."; docker restart "$NAME" >/dev/null; ok "Reiniciado"; }

cmd_status() { need_docker
  if ! container_exists "$NAME"; then warn "Contêiner '$NAME' não existe. Use: tools/atlas-docker.sh up"; return 0; fi
  local st hl img sha cur
  st="$(docker inspect -f '{{.State.Status}}' "$NAME")"
  hl="$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}-{{end}}' "$NAME")"
  img="$(docker inspect -f '{{.Config.Image}}' "$NAME")"
  sha="$(docker image inspect -f '{{index .Config.Labels "atlas.content-sha256"}}' "$img" 2>/dev/null || echo '?')"
  printf '%-18s %s\n' "contêiner:" "$NAME ($st, saúde: $hl)"
  printf '%-18s %s\n' "portas:" "$(docker port "$NAME" 2>/dev/null | tr '\n' ' ')"
  printf '%-18s %s\n' "imagem:" "$img"
  printf '%-18s %s\n' "conteúdo sha256:" "$sha"
  cur="$(content_hash)"
  printf '%-18s %s\n' "conteúdo atual:" "$cur  $( [[ "$cur" == "$sha" ]] && echo '(imagem em dia)' || echo '(há mudanças em public/: rode up)')"
  if container_running "${NAME}-tunnel"; then
    printf '%-18s %s\n' "link Cloudflare:" "$(docker logs "${NAME}-tunnel" 2>&1 | grep -Eo 'https://[a-z0-9-]+\.trycloudflare\.com' | tail -1)"
  fi
}

cmd_logs() { need_docker; container_exists "$NAME" || die "Contêiner '$NAME' não existe."; docker logs --tail 100 "$@" "$NAME"; }

cmd_link() { need_docker
  container_running "$NAME" || die "Suba o site primeiro: tools/atlas-docker.sh up"
  container_exists "${NAME}-tunnel" && docker rm -f "${NAME}-tunnel" >/dev/null
  info "Abrindo Cloudflare Quick Tunnel (${CLOUDFLARED_IMAGE})"
  docker run -d --name "${NAME}-tunnel" --restart unless-stopped \
    --network "container:${NAME}" \
    "$CLOUDFLARED_IMAGE" tunnel --no-autoupdate --url "http://127.0.0.1:8080" >/dev/null
  local url="" i
  for i in $(seq 1 45); do
    url="$(docker logs "${NAME}-tunnel" 2>&1 | grep -Eo 'https://[a-z0-9-]+\.trycloudflare\.com' | head -1 || true)"
    [[ -n "$url" ]] && break
    container_running "${NAME}-tunnel" || { docker logs --tail 20 "${NAME}-tunnel" >&2; die "O túnel parou (veja acima)."; }
    sleep 1
  done
  [[ -n "$url" ]] || { docker logs --tail 20 "${NAME}-tunnel" >&2; die "Não apareceu um link em 45 s."; }
  ok "Link aleatório: ${B}${url}${Z}"
  echo "   Ele muda se o túnel for recriado e deixa de funcionar após 'unlink'/'down'."
}
cmd_unlink() { need_docker; if container_exists "${NAME}-tunnel"; then docker rm -f "${NAME}-tunnel" >/dev/null; ok "Túnel encerrado"; else warn "Não há túnel"; fi; }

cmd_save() { need_docker
  local out="${1:-${IMAGE_REPO}-$(date +%Y%m%d).tar.gz}"
  docker image inspect "${IMAGE_REPO}:latest" >/dev/null 2>&1 || die "Imagem inexistente; rode 'build'."
  info "Exportando ${IMAGE_REPO}:latest -> $out"
  docker save "${IMAGE_REPO}:latest" | gzip > "$out"
  sha256_file "$out" | tee "${out}.sha256"
  ok "No servidor de destino:  gunzip -c $(basename "$out") | docker load   &&   rode o contêiner (veja docs/DOCKER.md)"
}

cmd_install_docker() {
  command -v docker >/dev/null 2>&1 && { ok "Docker já instalado: $(docker --version)"; return 0; }
  [[ -r /etc/os-release ]] || die "Sistema não reconhecido."
  # shellcheck disable=SC1091
  . /etc/os-release
  case "${ID:-}${ID_LIKE:-}" in *debian*|*ubuntu*) ;; *) die "install-docker só automatiza Debian/Ubuntu. Veja https://docs.docker.com/engine/install/";; esac
  local SUDO=""; [[ $EUID -ne 0 ]] && SUDO="sudo"
  info "Instalando o pacote docker.io da distribuição (via apt)"
  $SUDO apt-get update
  $SUDO apt-get install -y docker.io curl
  $SUDO systemctl enable --now docker || warn "Não consegui habilitar o serviço via systemctl."
  if [[ $EUID -ne 0 ]]; then $SUDO usermod -aG docker "$USER" && warn "Saia e entre na sessão para usar 'docker' sem sudo."; fi
  ok "Docker instalado: $(docker --version 2>/dev/null || true)"
}

# ---------- análise de argumentos ----------
CMD="${1:-up}"; [[ $# -gt 0 ]] && shift || true
EXTRA=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    -p|--port)  [[ $# -ge 2 ]] || die "$1 exige um valor"; PORT="$2"; shift 2;;
    -b|--bind)  [[ $# -ge 2 ]] || die "$1 exige um valor"; BIND="$2"; shift 2;;
    --local)    BIND="127.0.0.1"; shift;;
    -n|--name)  [[ $# -ge 2 ]] || die "$1 exige um valor"; NAME="$2"; shift 2;;
    --no-cache) NO_CACHE="--no-cache"; shift;;
    -h|--help)  usage; exit 0;;
    *)          EXTRA+=("$1"); shift;;
  esac
done
[[ "$NAME" =~ ^[a-zA-Z0-9][a-zA-Z0-9_.-]*$ ]] || die "Nome de contêiner inválido: $NAME"
[[ "$PORT" =~ ^[0-9]+$ ]] && (( PORT >= 1 && PORT <= 65535 )) || die "Porta inválida: $PORT"

case "$CMD" in
  up)              cmd_up;;
  build)           cmd_build;;
  run)             cmd_run;;
  down|stop)       cmd_down;;
  restart)         cmd_restart;;
  status)          cmd_status;;
  logs)            cmd_logs "${EXTRA[@]+"${EXTRA[@]}"}";;
  test)            cmd_test;;
  link)            cmd_link;;
  unlink)          cmd_unlink;;
  save)            cmd_save "${EXTRA[@]+"${EXTRA[@]}"}";;
  install-docker)  cmd_install_docker;;
  help|-h|--help)  usage;;
  *)               usage; die "Comando desconhecido: $CMD";;
esac
