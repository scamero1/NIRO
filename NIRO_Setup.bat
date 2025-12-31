@echo off
color 0b
title Instalador de NIRO
cls
echo.
echo  ========================================================
echo        INSTALADOR DE NIRO (Version PC)
echo  ========================================================
echo.
echo  [1/3] Detectando entorno...

:: Check for WebView2
reg query "HKLM\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}" >nul 2>&1
if %errorlevel% equ 0 (
    echo    > WebView2 Runtime detectado (Compatible con Modo App).
) else (
    echo    > WebView2 Runtime NO detectado. Se recomienda instalar Microsoft Edge para la mejor experiencia.
)

set "URL=http://localhost:8001"
set "NAME=NIRO"
set "PSScript=%temp%\CreateShortcut_%RANDOM%.ps1"
set "EXE_PATH=%~dp0dist\NIRO_App.exe"
if not exist "%EXE_PATH%" set "EXE_PATH=%~dp0NIRO_App.exe"

echo  [2/3] Configurando acceso directo...

(
echo $ErrorActionPreference = "Stop"
echo $WshShell = New-Object -ComObject WScript.Shell
echo $DesktopPath = [Environment]::GetFolderPath("Desktop"^)
echo $Url = "%URL%"
echo $Name = "%NAME%"
echo $ExePath = "%EXE_PATH%"
echo.
echo if (Test-Path $ExePath^) {
echo     Write-Host "    > Ejecutable detectado: $ExePath"
echo     $ShortcutFile = "$DesktopPath\$Name.lnk"
echo     $Shortcut = $WshShell.CreateShortcut($ShortcutFile^)
echo     $Shortcut.TargetPath = $ExePath
echo     $Shortcut.WorkingDirectory = [System.IO.Path]::GetDirectoryName($ExePath^)
echo     $Shortcut.Description = "NIRO Streaming Server & App"
echo     $Shortcut.Save(^)
echo     Write-Host "    > Acceso directo a la Aplicacion creado."
echo } else {
echo     Write-Host "    > Ejecutable no encontrado. Configurando acceso Web..."
echo     # Lista de navegadores soportados para modo App
echo     $Browsers = @(
echo         "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
echo         "C:\Program Files\Microsoft\Edge\Application\msedge.exe",
echo         "C:\Program Files\Google\Chrome\Application\chrome.exe",
echo         "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
echo         "C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
echo         "$env:LOCALAPPDATA\Vivaldi\Application\vivaldi.exe",
echo         "$env:LOCALAPPDATA\Programs\Opera\launcher.exe",
echo         "$env:LOCALAPPDATA\Programs\Opera GX\launcher.exe"
echo     ^)
echo.
echo     $Target = ""
echo     foreach ($B in $Browsers^) {
echo         if (Test-Path $B^) {
echo             $Target = $B
echo             break
echo         }
echo     }
echo.
echo     if ($Target -ne ""^) {
echo         Write-Host "    > Navegador compatible detectado: $Target"
echo         $ShortcutFile = "$DesktopPath\$Name.lnk"
echo         $Shortcut = $WshShell.CreateShortcut($ShortcutFile^)
echo         $Shortcut.TargetPath = $Target
echo         $Shortcut.Arguments = "--app=$Url --force-renderer-accessibility"
echo         $Shortcut.IconLocation = "$Target,0"
echo         $Shortcut.Description = "$Name Streaming Client"
echo         $Shortcut.Save(^)
echo         Write-Host "    > App Web instalada correctamente."
echo     } else {
echo         Write-Host "    > No se detecto navegador para App. Creando acceso web basico..."
echo         $UrlFile = "$DesktopPath\$Name.url"
echo         "[InternetShortcut]" ^| Out-File -FilePath $UrlFile -Encoding ASCII
echo         "URL=$Url" ^| Out-File -FilePath $UrlFile -Encoding ASCII -Append
echo         "IconIndex=0" ^| Out-File -FilePath $UrlFile -Encoding ASCII -Append
echo         "IconFile=C:\Windows\System32\url.dll" ^| Out-File -FilePath $UrlFile -Encoding ASCII -Append
echo         Write-Host "    > Acceso directo Web creado."
echo     }
echo }
) > "%PSScript%"
) > "%PSScript%"

if not exist "%PSScript%" (
    color 0c
    echo.
    echo  [ERROR] No se pudo crear el script temporal.
    pause
    exit /b
)

echo  [3/3] Aplicando cambios...
powershell -ExecutionPolicy Bypass -File "%PSScript%"

if %errorlevel% neq 0 (
    color 0c
    echo.
    echo  [ERROR] Algo salio mal con PowerShell.
    echo  Intentando metodo alternativo basico...
    
    echo [InternetShortcut] > "%userprofile%\Desktop\NIRO.url"
    echo URL=http://localhost:8001 >> "%userprofile%\Desktop\NIRO.url"
    echo IconIndex=0 >> "%userprofile%\Desktop\NIRO.url"
    echo IconFile=C:\Windows\System32\url.dll >> "%userprofile%\Desktop\NIRO.url"
    
    echo  Se ha creado un acceso directo basico en el escritorio.
    pause
) else (
    color 0a
    echo.
    echo  ========================================================
    echo     INSTALACION COMPLETADA
    echo  ========================================================
    echo.
    echo  Ya puedes usar NIRO desde tu escritorio.
    timeout /t 5 >nul
)

del "%PSScript%"
