#!/bin/bash
# HEXSTRIKE ULTIMATE - Script de Instalación para Linux/Mac

set -e

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     HEXSTRIKE ULTIMATE - Instalación Automática           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no encontrado. Por favor instálalo primero."
    exit 1
fi

echo "✓ Python 3 encontrado: $(python3 --version)"

# Verificar si existe entorno virtual
VENV_DIR="venv"
USE_VENV=false

if [ -d "$VENV_DIR" ]; then
    echo "✓ Entorno virtual encontrado en ./venv"
    USE_VENV=true
else
    echo "📦 Creando entorno virtual (recomendado para Kali Linux)..."
    if python3 -m venv "$VENV_DIR" 2>/dev/null; then
        USE_VENV=true
        echo "✓ Entorno virtual creado"
    else
        echo "⚠️  No se pudo crear entorno virtual. Instalando globalmente..."
        echo "   (En Kali Linux, esto puede requerir --break-system-packages)"
        USE_VENV=false
    fi
fi

# Activar entorno virtual si existe
if [ "$USE_VENV" = true ]; then
    echo "🔧 Activando entorno virtual..."
    source "$VENV_DIR/bin/activate"
    PYTHON_CMD="python"
    PIP_CMD="pip"
else
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
fi

# Verificar pip
if ! command -v "$PIP_CMD" &> /dev/null; then
    echo "❌ pip no encontrado. Instalando..."
    $PYTHON_CMD -m ensurepip --upgrade
fi

echo "✓ pip encontrado: $($PIP_CMD --version)"
echo ""

# Instalar dependencias
echo "📦 Instalando dependencias de Python..."

# Intentar con entorno virtual primero, luego sin
if [ "$USE_VENV" = true ]; then
    $PIP_CMD install --upgrade pip
    $PIP_CMD install -r requirements.txt
else
    # En Kali, puede necesitar --break-system-packages o usar apt
    if $PIP_CMD install --upgrade pip 2>&1 | grep -q "externally-managed-environment"; then
        echo ""
        echo "⚠️  Entorno protegido detectado (Kali Linux)"
        echo "📦 Intentando instalar dependencias del sistema..."
        echo ""
        
        # Intentar instalar con apt si está disponible
        if command -v apt &> /dev/null; then
            echo "Instalando con apt (puede requerir sudo)..."
            echo "Para instalar manualmente, ejecuta:"
            echo "  sudo apt install python3-flask python3-flask-cors python3-requests python3-psutil"
            echo ""
            echo "O usa un entorno virtual:"
            echo "  python3 -m venv venv"
            echo "  source venv/bin/activate"
            echo "  pip install -r requirements.txt"
            echo ""
            
            # Preguntar si quiere usar --break-system-packages
            read -p "¿Deseas usar --break-system-packages? (no recomendado) [N/y]: " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                $PIP_CMD install --break-system-packages --upgrade pip
                $PIP_CMD install --break-system-packages -r requirements.txt
            else
                echo "❌ Instalación cancelada. Por favor usa un entorno virtual."
                exit 1
            fi
        else
            # Si no hay apt, sugerir entorno virtual
            echo "❌ No se puede instalar sin entorno virtual."
            echo "Por favor crea un entorno virtual:"
            echo "  python3 -m venv venv"
            echo "  source venv/bin/activate"
            echo "  pip install -r requirements.txt"
            exit 1
        fi
    else
        $PIP_CMD install --upgrade pip
        $PIP_CMD install -r requirements.txt
    fi
fi

echo ""
echo "✓ Dependencias instaladas correctamente"
echo ""

# Verificar instalación
echo "🔍 Verificando instalación..."
$PYTHON_CMD -c "import flask; import flask_cors; import requests; import psutil; print('✓ Todas las dependencias están instaladas')" || {
    echo "❌ Error verificando dependencias"
    exit 1
}

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  ✓ Instalación completada exitosamente                    ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

if [ "$USE_VENV" = true ]; then
    echo "⚠️  IMPORTANTE: Debes activar el entorno virtual antes de usar:"
    echo "  source venv/bin/activate"
    echo ""
    echo "Luego ejecuta:"
    echo "  python hexstrike.py --web"
else
    echo "Para iniciar el panel web:"
    echo "  python3 hexstrike.py --web"
fi

echo ""
echo "O verificar herramientas:"
if [ "$USE_VENV" = true ]; then
    echo "  source venv/bin/activate && python hexstrike.py --show-tools"
else
    echo "  python3 hexstrike.py --show-tools"
fi
echo ""

