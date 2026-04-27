import os, webbrowser, tempfile, uuid, subprocess, sys, asyncio, atexit, threading
from flask import Flask, request, send_file, send_from_directory

app = Flask(__name__)

def get_resource_path(relative_path):
    """Obtiene la ruta del recurso, compatible con PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

PORT = 8889
HOST = "127.0.0.1"
FOLDER = os.path.dirname(os.path.abspath(__file__))
APP_FILE = get_resource_path("radio-spotify-pro.html")

# Configuración de Voz Pro
VOICE  = "es-AR-TomasNeural"
RATE   = "-5%"
PITCH  = "-3Hz"
VOLUME = "+10%"

@app.route("/")
def handle_root():
    return handle_index()

def cleanup_old_files():
    """Borra archivos TTS viejos para ahorrar espacio"""
    import time
    now = time.time()
    tmp_dir = tempfile.gettempdir()
    try:
        for f in os.listdir(tmp_dir):
            if f.startswith("pro_tts_") and f.endswith(".mp3"):
                path = os.path.join(tmp_dir, f)
                if os.path.getmtime(path) < now - 300:
                    os.remove(path)
    except: pass

atexit.register(cleanup_old_files)



@app.route("/radio-spotify-pro.html")
def handle_index():
    code = request.args.get("code", "")
    try:
        with open(APP_FILE, "r", encoding="utf-8") as f:
            html = f.read()
        if code:
            inject = f'<script>window.__SPOTIFY_CODE__ = "{code}";</script>'
            html = html.replace("</head>", inject + "</head>", 1)
        return html
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route("/tts")
def handle_tts():
    cleanup_old_files()
    text = request.args.get("text", "")
    if not text: return "No text", 400
    
    filename = f"pro_tts_{uuid.uuid4().hex}.mp3"
    filepath = os.path.join(tempfile.gettempdir(), filename)
    
    print(f"[PRO TTS] Generando: {text[:50]}...")
    
    try:
        import edge_tts
        async def gen():
            communicate = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH)
            await communicate.save(filepath)
        
        asyncio.run(gen())
        return send_file(filepath, mimetype="audio/mpeg")
    except Exception as e:
        print(f"[PRO TTS] Error: {e}")
        return str(e), 500

@app.route('/<path:path>')
def send_static(path):
    return send_from_directory(FOLDER, path)

def open_in_chrome(url):
    """Intenta abrir la URL en Google Chrome específicamente"""
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    ]
    
    launched = False
    for path in chrome_paths:
        if os.path.exists(path):
            try:
                subprocess.Popen([path, url])
                launched = True
                break
            except: continue
    
    if not launched:
        # Fallback al navegador por defecto si no hay Chrome
        webbrowser.open(url)

if __name__ == "__main__":
    url = f"http://{HOST}:{PORT}/radio-spotify-pro.html"
    print(f"RadioAI PRO en {url}")
    print(f"Abriendo Chrome...")
    
    # Abrir el navegador en un hilo separado para que no bloquee app.run
    threading.Timer(1.5, lambda: open_in_chrome(url)).start()
    
    app.run(host=HOST, port=PORT, debug=False)


