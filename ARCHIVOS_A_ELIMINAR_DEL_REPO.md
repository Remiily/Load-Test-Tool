# 🗑️ Archivos a Eliminar del Repositorio en GitHub

## ⚠️ IMPORTANTE: Estos archivos NO deben estar en GitHub

Si subiste la raíz completa del proyecto, **DEBES ELIMINAR** los siguientes archivos del repositorio en GitHub Desktop.

**NOTA:** Los scripts `.sh` (verify_before_push.sh, setup_security.sh) ya fueron eliminados localmente porque no son necesarios si usas GitHub Desktop.

### 📄 Documentación de Seguridad (ELIMINAR TODOS)

1. `SECURITY.md`
2. `SECURITY_AUTO_INIT.md`
3. `SECURITY_ADVANCED.md`
4. `SECURITY_IMPLEMENTATION.md`
5. `SECURITY_NEW_FEATURES.md`
6. `SECURITY_RECOMMENDATIONS.md`
7. `KILLSWITCH_README.md`
8. `INSTALL_SECURITY.md`

### 🔧 Scripts Sensibles (ELIMINAR TODOS)

9. `calculate_hashes.py`
10. `tracking_server.py`

### 📝 Archivos del Owner (ELIMINAR)

11. `OWNER_NOTES.md`
12. `ARCHIVOS_A_ELIMINAR_DEL_REPO.md` (este archivo también)

## 📋 Cómo Eliminarlos en GitHub Desktop

1. **Abrir GitHub Desktop**
2. **Ir a la pestaña "Changes" o "History"**
3. **Para cada archivo de la lista:**
   - Click derecho en el archivo
   - Seleccionar "Delete" o "Remove"
   - Confirmar eliminación
4. **Hacer commit:**
   - Mensaje: `Remove sensitive files from repository`
   - Click en "Commit to main"
5. **Hacer push:**
   - Click en "Push origin"

## ✅ Archivos que SÍ deben estar en GitHub

Estos archivos **SÍ deben estar** en el repositorio:

- ✅ `loadtest.py` - Script principal
- ✅ `loadtest_web.py` - Panel web
- ✅ `README.md` - Documentación pública (ya limpiado)
- ✅ `requirements.txt` - Dependencias
- ✅ `INSTALL.md` - Guía de instalación pública
- ✅ `install.sh` - Script de instalación
- ✅ `install.bat` - Script de instalación Windows
- ✅ `check_files.sh` - Script de verificación de archivos
- ✅ `templates/` - Templates del panel web
- ✅ `.gitignore` - Configuración de Git (actualizado)
- ✅ `.gitattributes` - Atributos de Git

## 🔍 Verificación

Después de eliminar los archivos, verifica que:

1. ✅ No aparecen en GitHub Desktop
2. ✅ No aparecen en el repositorio web de GitHub
3. ✅ El `.gitignore` está actualizado (ya está hecho)

## 📝 Nota

Los archivos eliminados seguirán existiendo localmente en tu máquina, pero **NO estarán en GitHub**, que es lo correcto.

Los archivos sensibles están protegidos por `.gitignore`, por lo que no se subirán accidentalmente en el futuro.

