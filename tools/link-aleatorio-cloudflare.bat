@echo off
REM Publica o atlas com link aleatorio https://....trycloudflare.com (Cloudflare Quick Tunnel).
REM O link so funciona enquanto esta janela estiver aberta. Requer Python 3 e cloudflared no PATH.
cd /d "%~dp0\.."
start "Servidor do Atlas" /min python tools\servir.py 8080
timeout /t 2 >nul
echo Procure abaixo a linha com https://....trycloudflare.com
cloudflared tunnel --url http://127.0.0.1:8080
