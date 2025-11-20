@echo off
REM HEXSTRIKE ULTIMATE - Script de Instalación para Windows

echo ╔═══════════════════════════════════════════════════════════╗
echo ║     HEXSTRIKE ULTIMATE - Instalación Automática           ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no encontrado. Por favor instálalo primero.
    echo Descarga desde: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✓ Python encontrado
python --version
echo.

REM Verificar pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip no encontrado. Instalando...
    python -m ensurepip --upgrade
)

echo ✓ pip encontrado
pip --version
echo.

REM Instalar dependencias
echo 📦 Instalando dependencias de Python...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ✓ Dependencias instaladas correctamente
echo.

REM Verificar instalación
echo 🔍 Verificando instalación...
python -c "import flask; import flask_cors; import requests; import psutil; print('✓ Todas las dependencias están instaladas')"
if errorlevel 1 (
    echo ❌ Error verificando dependencias
    pause
    exit /b 1
)

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║  ✓ Instalación completada exitosamente                    ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo Para iniciar el panel web:
echo   python hexstrike.py --web
echo.
echo O verificar herramientas:
echo   python hexstrike.py --show-tools
echo.
pause

