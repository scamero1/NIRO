import sys
import os
import time
import subprocess
import webbrowser

# URL de la aplicación web
APP_URL = "https://niro-tv.online"

def open_browser():
    """Abre el navegador en modo App apuntando a la web"""
    
    # Lista de navegadores soportados para modo App
    browsers = [
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Vivaldi\Application\vivaldi.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Opera\launcher.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Opera GX\launcher.exe")
    ]
    
    # Intentar abrir en modo App
    for browser in browsers:
        if os.path.exists(browser):
            try:
                print(f"Abriendo NIRO en: {APP_URL}")
                subprocess.Popen([browser, f"--app={APP_URL}", "--force-renderer-accessibility"])
                return
            except Exception as e:
                print(f"Error abriendo navegador: {e}")
    
    # Fallback a navegador predeterminado
    print("Abriendo en navegador predeterminado...")
    webbrowser.open(APP_URL)

if __name__ == '__main__':
    print(f"Iniciando NIRO...")
    print(f"Conectando a: {APP_URL}")
    
    open_browser()
    
    # Mantener la consola abierta brevemente si se ejecuta directamente
    time.sleep(2)

