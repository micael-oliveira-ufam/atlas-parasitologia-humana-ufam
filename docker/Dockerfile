# Atlas Digital de Parasitologia Humana — imagem de produção (somente arquivos estáticos).
# O contexto de build é montado por tools/atlas-docker.sh (contém apenas public/ e docker/).
ARG BASE_IMAGE=nginxinc/nginx-unprivileged:1.27-alpine
FROM ${BASE_IMAGE}

ARG CONTENT_SHA256=desconhecido
LABEL org.opencontainers.image.title="Atlas Digital de Parasitologia Humana" \
      org.opencontainers.image.description="Site estático (nginx não-root)" \
      atlas.content-sha256="${CONTENT_SHA256}"

COPY docker/atlas-headers.conf /etc/nginx/atlas-headers.conf
COPY docker/nginx.conf         /etc/nginx/conf.d/default.conf
COPY public/                   /usr/share/nginx/html/

EXPOSE 8080
HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -q -O /dev/null http://127.0.0.1:8080/healthz || exit 1
