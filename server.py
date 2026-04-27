import http.server
import socketserver
import webbrowser
import os
import urllib.parse

PORT = 8888
HOST = "127.0.0.1"
FOLDER = os.path.dirname(os.path.abspath(__file__))

# Leer el HTML de la app
APP_FILE = os.path.join(FOLDER, "radio-spotify.html")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FOLDER, **kwargs)

    def do_GET(self):
        print(f"[DEBUG] path: {self.path}")

        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        # Spotify callback con ?code=
        if "code" in params or "error" in params:
            print(f"[DEBUG] Codigo OAuth recibido!")
            try:
                with open(APP_FILE, "r", encoding="utf-8") as f:
                    html = f.read()
                # Inyectar el code directamente en el HTML via script
                code = params.get("code", [""])[0]
                inject = f"""
<script>
  // Código OAuth inyectado por el server
  window.__SPOTIFY_CODE__ = "{code}";
</script>
"""
                html = html.replace("</head>", inject + "</head>", 1)
                encoded = html.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(encoded)))
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                self.wfile.write(encoded)
                print(f"[DEBUG] HTML servido con código inyectado")
            except Exception as e:
                print(f"[ERROR] {e}")
                self.send_error(500, str(e))
        else:
            super().do_GET()

    def log_message(self, format, *args):
        pass

print(f"RadioAI server en http://{HOST}:{PORT}")
print(f"Carpeta: {FOLDER}")
print(f"Abriendo navegador...")
webbrowser.open(f"http://{HOST}:{PORT}/radio-spotify.html")

socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer((HOST, PORT), Handler) as httpd:
    print("Esperando... (Ctrl+C para detener)\n")
    httpd.serve_forever()

