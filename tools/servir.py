#!/usr/bin/env python3
"""Servidor local do atlas (sem dependências). Replica os cabeçalhos de public/_headers
(inclui a CSP), para que o teste local se comporte como em produção.
Uso: python3 tools/servir.py [porta]   (padrão 8080)"""
import http.server, os, sys, functools
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public')
CSP = "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'"
class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Content-Security-Policy', CSP)
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()
    def log_message(self, f, *a): sys.stderr.write('[atlas] ' + f % a + '\n')
if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    handler = functools.partial(H, directory=ROOT)
    with http.server.ThreadingHTTPServer(('127.0.0.1', port), handler) as s:
        print(f'Atlas em http://127.0.0.1:{port}  (Ctrl+C para parar)'); s.serve_forever()
