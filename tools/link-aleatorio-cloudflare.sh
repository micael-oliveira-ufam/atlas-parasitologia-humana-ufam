#!/usr/bin/env bash
# Publica o atlas com um link aleatório https://<palavras>.trycloudflare.com (Cloudflare Quick Tunnel).
# O link só funciona enquanto este script estiver rodando e o computador ligado/online.
set -euo pipefail
cd "$(dirname "$0")/.."
PORT="${PORT:-8080}"
command -v cloudflared >/dev/null || { echo "cloudflared não encontrado. Instale: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/"; exit 1; }
python3 tools/servir.py "$PORT" & SRV=$!
trap 'kill $SRV 2>/dev/null' EXIT
sleep 1
echo ">> Procure abaixo a linha com https://....trycloudflare.com"
cloudflared tunnel --url "http://127.0.0.1:$PORT"
