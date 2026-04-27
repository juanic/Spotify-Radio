# Spotify Radio AI

## Acerca de este proyecto
Este proyecto es un ejemplo **"vibecodificado" (vibecoded) con Inteligencia Artificial con fines didácticos**. Su objetivo es demostrar cómo integrar la API Web de Spotify con síntesis de voz (TTS) para crear una experiencia de radio personalizada, donde un "locutor" virtual presenta las canciones, lee información de los artistas y hace transiciones fluidas.

El proyecto cuenta con dos versiones:
- **Versión Estándar:** Utiliza las voces del sistema integradas en el navegador (`radio-spotify.html` y `server.py`).
- **Versión PRO:** Incorpora voces neuronales de alta calidad a través de la librería `edge-tts` de Microsoft.
  - `radio-spotify-pro.html`: Interfaz principal de la versión PRO.
  - `server_pro.py`: Servidor web local que sirve la interfaz web de la versión PRO y sus recursos.
  - `radio_cast.py`: Script que maneja la lógica de generación de audio (TTS) utilizando los modelos neuronales.

## Configuración y Claves Necesarias (API Keys)
Para hacer funcionar esta aplicación con todas sus características (música y clima), necesitas obtener claves gratuitas de dos servicios:

### 1. Spotify (Client ID)
1. Ve al [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).
2. Inicia sesión con tu cuenta de Spotify y crea una nueva aplicación (App).
3. Configura la **Redirect URI** a `http://localhost:8000` (o el puerto que utilices).
4. Copia el **Client ID** que te proporciona Spotify.

### 2. OpenWeather (API Key)
1. Ve a [OpenWeatherMap](https://home.openweathermap.org/users/sign_up) y crea una cuenta gratuita.
2. Dirígete a la sección de **API Keys**.
3. Genera y copia tu clave (API Key). *(Nota: a veces tarda un par de horas en activarse).*

Cuando abras la página web del proyecto, verás campos donde debes ingresar tanto tu **Client ID de Spotify** como tu **API Key de OpenWeather**.

## Seguridad y Manejo de Claves
El código de este proyecto está diseñado para no almacenar **ninguna clave (ni de Spotify ni de OpenWeather)** de forma fija (hardcodeada) en los archivos `.py` o `.html`. 

La lógica de la aplicación funciona de la siguiente manera:
- Cuando ingresas tu Client ID y tu API Key de OpenWeather en la interfaz, esos datos se guardan directamente en el **Local Storage (Almacenamiento Local) de tu navegador** (Chrome, Firefox, Edge, etc.). 
- Esto significa que la información reside únicamente en tu computadora, dentro de la memoria de tu navegador, y no se escribe en ningún archivo del código fuente.

Por lo tanto, la carpeta del proyecto puede ser compartida o subida a repositorios públicos como GitHub sin riesgo de exponer tus credenciales.

## Ejecución
Para iniciar la versión PRO:
```bash
python server_pro.py
```
Y luego abre en tu navegador: `http://localhost:8000/radio-spotify-pro.html`

## Empaquetado (Ejecutable .exe)
En la carpeta `dist` puedes encontrar una versión ejecutable de la aplicación. Si deseas generarla tú mismo (para correr la app sin necesidad de usar la consola o tener Python instalado), puedes utilizar `PyInstaller`.

Puedes compilar el proyecto ejecutando el script `build_pro.py` o utilizando directamente el archivo de especificación incluido:
```bash
pip install pyinstaller
pyinstaller RadioAI_PRO_Final.spec
```
