#!/bin/bash
# Script de configuración de seguridad
# Este script ayuda a configurar el sistema de seguridad

echo "🔒 Configurando sistema de seguridad de LoadTest Enterprise"
echo ""

# Crear archivo .auth si no existe
if [ ! -f .auth ]; then
    echo "active" > .auth
    echo "✓ Archivo .auth creado con estado 'active'"
else
    echo "✓ Archivo .auth ya existe"
fi

# Verificar permisos
chmod 600 .auth 2>/dev/null
echo "✓ Permisos configurados para .auth"

# Crear directorio de tracking si no existe
mkdir -p loadtest_output/tracking 2>/dev/null
echo "✓ Directorio de tracking creado"

echo ""
echo "✅ Configuración de seguridad completada"
echo ""
echo "Para activar el kill-switch, edita .auth y cambia 'active' a 'kill'"
echo "Para autorizar uso, asegúrate de que .auth contenga 'active'"

