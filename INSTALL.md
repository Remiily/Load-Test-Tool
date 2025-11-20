# HEXSTRIKE ULTIMATE - Guía de Instalación

## Requisitos Previos

- Python 3.7 o superior
- pip (gestor de paquetes de Python)
- Sistema operativo: Linux, macOS, o Windows

## Instalación Rápida

### 1. Instalar Dependencias de Python

```bash
# Opción 1: Usando requirements.txt
pip install -r requirements.txt

# Opción 2: Instalación manual
pip install Flask Flask-Cors requests urllib3 psutil

# Si usas Python 3 específicamente:
pip3 install -r requirements.txt
```

### 2. Verificar Instalación

```bash
# Verificar que Python puede importar las dependencias
python -c "import flask; import flask_cors; import requests; import psutil; print('✓ Todas las dependencias están instaladas')"
```

### 3. Ejecutar Panel Web

```bash
python hexstrike.py --web
```

Luego abre tu navegador en: `http://localhost:5000`

## Instalación en Linux (Kali/Debian/Ubuntu)

```bash
# Instalar Python y pip si no están instalados
sudo apt update
sudo apt install python3 python3-pip -y

# Instalar dependencias
pip3 install -r requirements.txt

# Ejecutar
python3 hexstrike.py --web
```

## Instalación en Windows

```powershell
# Asegúrate de tener Python instalado
# Descargar desde: https://www.python.org/downloads/

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python hexstrike.py --web
```

## Instalación en macOS

```bash
# Instalar Python y pip si no están instalados
brew install python3

# Instalar dependencias
pip3 install -r requirements.txt

# Ejecutar
python3 hexstrike.py --web
```

## Instalación con Entorno Virtual (Recomendado)

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
# En Linux/Mac:
source venv/bin/activate
# En Windows:
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python hexstrike.py --web
```

## Estructura de Archivos

Asegúrate de tener esta estructura:

```
hexstrike/
├── hexstrike.py          # Script principal
├── hexstrike_web.py      # Panel web
├── requirements.txt      # Dependencias
├── templates/            # Templates HTML
│   └── index.html       # Panel web
├── README.md            # Documentación
└── INSTALL.md           # Esta guía
```

## Solución de Problemas

### Error: "No module named 'flask'"
```bash
pip install Flask Flask-Cors
```

### Error: "No module named 'requests'"
```bash
pip install requests urllib3
```

### Error: "No module named 'psutil'"
```bash
pip install psutil
```

### Error: "hexstrike_web.py no encontrado"
- Asegúrate de que `hexstrike_web.py` esté en el mismo directorio que `hexstrike.py`
- Verifica que el archivo existe: `ls -la hexstrike_web.py` (Linux/Mac) o `dir hexstrike_web.py` (Windows)

### Error: "templates/index.html no encontrado"
- Asegúrate de que la carpeta `templates` exista con el archivo `index.html`
- Verifica: `ls -la templates/` (Linux/Mac) o `dir templates\` (Windows)

## Herramientas Externas Opcionales

Para máximo rendimiento, también puedes instalar herramientas externas (opcionales):

```bash
# En Linux/Debian/Ubuntu
sudo apt install wrk vegeta hping3 apache2-utils siege -y

# O instalar automáticamente desde el script:
python hexstrike.py --install-tools
```

## Verificar Instalación Completa

```bash
# Verificar herramientas instaladas
python hexstrike.py --show-tools

# Ver todos los parámetros
python hexstrike.py --show-params

# Probar panel web
python hexstrike.py --web
```

¡Listo! Ya puedes usar HEXSTRIKE ULTIMATE.

