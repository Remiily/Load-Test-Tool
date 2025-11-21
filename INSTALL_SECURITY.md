# 🔒 Instalación y Configuración de Seguridad

## ⚠️ IMPORTANTE: Inicialización Automática

**El sistema de seguridad se inicializa AUTOMÁTICAMENTE al ejecutar `loadtest.py`.**

**NO necesitas ejecutar scripts adicionales ni configurar nada manualmente.**

Solo ejecuta:
```bash
python loadtest.py -t https://example.com
```

Y todo funcionará automáticamente.

## Configuración Remota (Solo para Administradores)

### 1. Configurar Archivo de Autorización en GitHub

Crea el archivo `.auth` en la raíz del repositorio GitHub con el contenido:

```
active
```

Este archivo controla si la herramienta está autorizada para ejecutarse.

**Valores permitidos:**
- `active`, `1`, `true`, `authorized` - Herramienta autorizada
- `kill`, `disable`, `0`, `false`, `unauthorized` - Activa kill-switch

**Ubicación:** `https://raw.githubusercontent.com/Remiily/Load-Test-Tool/main/.auth`

### 2. Scripts Opcionales (Solo para Desarrollo)

Los scripts como `setup_security.sh` son **opcionales** y solo para desarrollo local:

```bash
./setup_security.sh  # Opcional - solo para desarrollo
```

**Nota:** El archivo `.auth` local no afecta el sistema real. El sistema verifica el archivo en GitHub.

### 3. Configurar Servidor de Tracking (Opcional)

Si deseas recibir datos de tracking localmente:

```bash
python tracking_server.py
```

El servidor escuchará en `http://localhost:8080/track`

## Verificación

### Verificar Estado de Autorización

El sistema verifica automáticamente cada 5 minutos. Para verificar manualmente:

1. Revisa el archivo `.auth` en GitHub
2. Verifica que contenga `active`
3. La herramienta verificará en la próxima ejecución

### Ver Datos de Tracking

Si estás usando el servidor de tracking:

```bash
# Ver todos los eventos
curl http://localhost:8080/events

# Ver estadísticas
curl http://localhost:8080/stats

# Ver últimos 50 eventos
curl http://localhost:8080/events/latest?limit=50
```

## Activar Kill-Switch

Para desactivar la herramienta remotamente:

1. Edita el archivo `.auth` en GitHub
2. Cambia el contenido a: `kill`
3. La herramienta se desactivará en la próxima verificación (máximo 5 minutos)

## Restaurar Herramienta

Si la herramienta fue desactivada:

1. Cambia `.auth` a `active` en GitHub
2. Restaura los archivos desde backup:
   ```bash
   cp loadtest.py.disabled loadtest.py
   cp loadtest_web.py.disabled loadtest_web.py
   ```
3. O reinstala desde el repositorio

## Recomendaciones

1. **No compartir `.auth`**: Mantén el archivo `.auth` privado
2. **Backup regular**: Haz backup de los archivos antes de cambios importantes
3. **Monitoreo**: Revisa regularmente los datos de tracking
4. **Servidor propio**: Considera usar tu propio servidor en lugar de GitHub

## Troubleshooting

### La herramienta se desactiva sin razón

- Verifica que `.auth` contenga `active`
- Verifica conexión a Internet
- Revisa logs para más detalles

### No se reciben datos de tracking

- Verifica que el servidor de tracking esté ejecutándose
- Verifica firewall/red
- Revisa logs del servidor

### Error de permisos

- Asegúrate de tener permisos de escritura en el directorio
- Verifica permisos del archivo `.auth`

