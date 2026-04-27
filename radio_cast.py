"""
RadioAI - Cast Script con Edge TTS
Corre en paralelo a la app web (server.py).

Instalar dependencias:
    pip install pychromecast edge-tts flask

Uso:
    python radio_cast.py

Voces disponibles en español (las mejores):
    es-AR-ElenaNeural     ← Argentina femenina ⭐
    es-AR-TomasNeural     ← Argentina masculina ⭐
    es-MX-DaliaNeural     ← México femenina
    es-MX-JorgeNeural     ← México masculino
    es-ES-AlvaroNeural    ← España masculina
"""

import os, sys, time, threading, tempfile, socket, asyncio

# ── dependencias ──────────────────────────────────────────────
try:
    import edge_tts
except ImportError:
    print("❌ Falta edge-tts. Corré: pip install edge-tts")
    sys.exit(1)

try:
    import pychromecast
except ImportError:
    print("❌ Falta pychromecast. Corré: pip install pychromecast")
    sys.exit(1)

try:
    from flask import Flask, request, jsonify, send_file
except ImportError:
    print("❌ Falta flask. Corré: pip install flask")
    sys.exit(1)

# ── config ────────────────────────────────────────────────────
API_PORT   = 9999
AUDIO_PORT = 9998
AUDIO_FILE = os.path.join(tempfile.gettempdir(), "radioai_announce.mp3")

# Voces disponibles — cambiá según preferencia
VOICE = "es-AR-TomasNeural"   # DJ masculino argentino
# VOICE = "es-AR-ElenaNeural" # DJ femenina argentina

# Estilo del locutor (Edge TTS SSML)
RATE   = "-5%"    # velocidad (-10% más lento, +10% más rápido)
PITCH  = "-3Hz"   # tono (-5Hz más grave, neutro = +0Hz)
VOLUME = "+10%"   # volumen

# ── TTS con Edge ──────────────────────────────────────────────
async def text_to_mp3_async(text, filepath):
    communicate = edge_tts.Communicate(
        text,
        voice=VOICE,
        rate=RATE,
        pitch=PITCH,
        volume=VOLUME,
    )
    await communicate.save(filepath)
    print(f"   💾 Audio generado ({VOICE})")

def text_to_mp3(text, filepath):
    asyncio.run(text_to_mp3_async(text, filepath))

# ── buscar Google Home ────────────────────────────────────────
def find_google_home():
    print("🔍 Buscando dispositivos Chromecast/Google Home en la red...")
    chromecasts, browser = pychromecast.get_chromecasts(timeout=10)
    if not chromecasts:
        print("⚠️  No se encontró ningún dispositivo.")
        print("   Verificá que la PC y el Google Home estén en el mismo WiFi.")
        return None, None
    for cc in chromecasts:
        print(f"   📻 {cc.name}  ({cc.host}:{cc.port})")
    cast = chromecasts[0]
    cast.wait()
    print(f"✅ Usando: {cast.name}\n")
    return cast, browser

# ── IP local ──────────────────────────────────────────────────
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()

# ── servidor de audio (para que el Chromecast descargue el MP3) ──
audio_app = Flask("audio_server")

@audio_app.route("/announce.mp3")
def serve_audio():
    return send_file(AUDIO_FILE, mimetype="audio/mpeg")

def start_audio_server():
    audio_app.run(host="0.0.0.0", port=AUDIO_PORT, debug=False, use_reloader=False)

# ── castear al Google Home ────────────────────────────────────
def cast_audio(cast, local_ip):
    url = f"http://{local_ip}:{AUDIO_PORT}/announce.mp3"
    print(f"   📡 Enviando al {cast.name}: {url}")
    mc = cast.media_controller
    mc.play_media(url, "audio/mpeg")
    mc.block_until_active(timeout=10)
    # Esperar que termine
    while True:
        time.sleep(1)
        mc.update_status()
        state = mc.status.player_state if mc.status else None
        if state in ("IDLE", "UNKNOWN", None, "PAUSED"):
            break
    print("   ✅ Anuncio terminado")

# ── API ───────────────────────────────────────────────────────
api_app = Flask("radio_api")
cast_device = None
local_ip    = None

@api_app.after_request
def cors(resp):
    resp.headers["Access-Control-Allow-Origin"]  = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return resp

@api_app.route("/announce", methods=["POST"])
def announce():
    data = request.json or {}
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "Sin texto"}), 400
    print(f"\n🎙️  Anunciando: {text[:100]}...")
    try:
        text_to_mp3(text, AUDIO_FILE)
        if cast_device:
            cast_audio(cast_device, local_ip)
        else:
            print("   ⚠️  Sin Chromecast disponible")
            return jsonify({"error": "Sin Chromecast"}), 503
        return jsonify({"ok": True})
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return jsonify({"error": str(e)}), 500

@api_app.route("/status")
def status():
    return jsonify({
        "ok": True,
        "device": cast_device.name if cast_device else None,
        "voice": VOICE,
        "ip": local_ip
    })

@api_app.route("/test")
def test():
    """Prueba rápida — abrí http://127.0.0.1:9999/test en el navegador"""
    sample = "Buenas tardes, esto es Radio AI. Sonando con la mejor música, ahora en tu Google Home."
    text_to_mp3(sample, AUDIO_FILE)
    if cast_device:
        cast_audio(cast_device, local_ip)
        return jsonify({"ok": True, "msg": f"Prueba enviada a {cast_device.name}"})
    return jsonify({"ok": False, "msg": "Sin dispositivo Chromecast"})

@api_app.route("/voices")
def voices():
    """Lista las voces en español disponibles"""
    import subprocess, json as _json
    try:
        result = subprocess.run(
            ["edge-tts", "--list-voices"],
            capture_output=True, text=True, timeout=15
        )
        lines = [l for l in result.stdout.splitlines() if "es-" in l.lower()]
        return "<pre>" + "\n".join(lines) + "</pre>"
    except Exception as e:
        return str(e)

# ── main ──────────────────────────────────────────────────────
if __name__ == "__main__":
    local_ip = get_local_ip()
    print(f"\n🖥️  IP de la PC: {local_ip}")
    print(f"🎙️  Voz: {VOICE}  (rate={RATE} pitch={PITCH})\n")

    cast_device, browser = find_google_home()

    # Servidor de audio en thread
    threading.Thread(target=start_audio_server, daemon=True).start()
    print(f"🎵 Servidor de audio listo en http://{local_ip}:{AUDIO_PORT}/announce.mp3")

    print(f"\n✅ API lista en http://127.0.0.1:{API_PORT}")
    print(f"   🔊 Prueba:  http://127.0.0.1:{API_PORT}/test")
    print(f"   📋 Estado: http://127.0.0.1:{API_PORT}/status")
    print(f"   🗣️  Voces:  http://127.0.0.1:{API_PORT}/voices\n")

    api_app.run(host="127.0.0.1", port=API_PORT, debug=False, use_reloader=False)
