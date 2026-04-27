import PyInstaller.__main__
import os
import sys

# Ruta al archivo HTML
html_file = "radio-spotify-pro.html"

# Comando para PyInstaller
# --onefile: Un solo archivo EXE
# --add-data: Incluye el HTML (en Windows el separador es ;)
# --name: Nombre del ejecutable
# --clean: Limpia temporales antes de compilar

params = [
    'server_pro.py',
    '--onefile',
    '--add-data', f'{html_file};.',
    '--name', 'RadioAI_PRO_Final',
    '--clean',
    '--console'
]


print("Iniciando compilación de RadioAI PRO...")
PyInstaller.__main__.run(params)
print("\n¡Compilación terminada! Busca el archivo en la carpeta 'dist'.")
