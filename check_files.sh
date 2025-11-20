#!/bin/bash
# Script para verificar que todos los archivos necesarios estén presentes

echo "🔍 Verificando archivos necesarios..."
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

ERRORS=0

# Verificar archivos principales
files=(
    "hexstrike.py"
    "hexstrike_web.py"
    "requirements.txt"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file"
    else
        echo "❌ $file NO ENCONTRADO"
        ERRORS=$((ERRORS + 1))
    fi
done

# Verificar carpeta templates
if [ -d "templates" ]; then
    if [ -f "templates/index.html" ]; then
        echo "✓ templates/index.html"
    else
        echo "❌ templates/index.html NO ENCONTRADO"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo "❌ Carpeta templates NO ENCONTRADA"
    ERRORS=$((ERRORS + 1))
fi

# Verificar carpeta static (opcional)
if [ ! -d "static" ]; then
    mkdir -p static
    echo "✓ Carpeta static creada"
fi

echo ""

if [ $ERRORS -eq 0 ]; then
    echo "✅ Todos los archivos necesarios están presentes"
    exit 0
else
    echo "❌ Faltan $ERRORS archivo(s)"
    echo ""
    echo "Asegúrate de copiar todos los archivos del proyecto:"
    echo "  - hexstrike.py"
    echo "  - hexstrike_web.py"
    echo "  - requirements.txt"
    echo "  - templates/ (carpeta completa)"
    exit 1
fi

