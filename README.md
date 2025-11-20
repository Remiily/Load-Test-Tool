# LoadTest Enterprise

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

**Suite Empresarial de Pruebas de Carga Web y Análisis de Rendimiento**

Herramienta profesional para pruebas de seguridad autorizadas y análisis de rendimiento.

[Características](#-características) • [Instalación](#-instalación) • [Uso](#-uso) • [Documentación](#-documentación) • [Contribuir](#-contribuir)

</div>

---

## 📋 Tabla de Contenidos

- [Resumen](#-resumen)
- [Características](#-características)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Inicio Rápido](#-inicio-rápido)
- [Uso](#-uso)
- [Configuración](#-configuración)
- [Herramientas Soportadas](#-herramientas-soportadas)
- [Reportes](#-reportes)
- [Panel Web](#-panel-web)
- [Ejemplos](#-ejemplos)
- [Sistema de Auto-Actualización](#-sistema-de-auto-actualización)
- [Solución de Problemas](#-solución-de-problemas)
- [Contribuir](#-contribuir)
- [Licencia](#-licencia)
- [Descargo de Responsabilidad](#-descargo-de-responsabilidad)

---

## 🎯 Resumen

**LoadTest Enterprise** es una suite completa de pruebas de carga web y análisis de rendimiento diseñada para profesionales de seguridad y equipos DevOps. Proporciona capacidades avanzadas para pruebas de estrés, análisis de rendimiento y evaluación de seguridad de aplicaciones y servicios web.

### Capacidades Clave

- **Integración Multi-Herramienta**: Soporta 40+ herramientas estándar de la industria para pruebas de carga
- **Monitoreo Inteligente**: Monitoreo de recursos en tiempo real con throttling automático
- **Reportes Avanzados**: Reportes HTML completos con métricas detalladas y recomendaciones
- **Interfaz Web**: Panel web moderno para configuración y monitoreo fácil
- **Auto-Instalación**: Instalación automática de herramientas de prueba requeridas
- **Listo para Empresa**: Diseño profesional adecuado para entornos corporativos

---

## ✨ Características

### Características Principales

- 🔄 **Múltiples Modos de Ataque**: MIXED, CONSTANT, BURST, RAMP_UP
- 📊 **Monitoreo en Tiempo Real**: Métricas de CPU, memoria y red
- 🎯 **Gestión Inteligente de Recursos**: Throttling automático basado en recursos del sistema
- 📈 **Reportes Completos**: Reportes HTML detallados con gráficos y recomendaciones
- 🌐 **Panel Web**: Interfaz web moderna para configuración y monitoreo
- 🔧 **Auto-Instalación de Herramientas**: Instala automáticamente herramientas de prueba faltantes
- 🛡️ **Características de Seguridad**: Bypass de WAF, modo stealth, soporte de proxy
- ⚡ **Alto Rendimiento**: Optimizado para máximo throughput
- 📱 **Multi-Protocolo**: Soporte para HTTP/1.1, HTTP/2, WebSocket
- 🎨 **UI Profesional**: Diseño y branding listo para empresas

### Características Avanzadas

- **Connection Pooling**: Conexiones reutilizables para mejor rendimiento
- **Optimización TCP**: Optimizaciones avanzadas de la pila TCP
- **Multiplexing HTTP/2**: Soporte para protocolo HTTP/2
- **Rate Adaptive**: Ajuste dinámico de tasa basado en respuesta del servidor
- **Gestión de Memoria**: Monitoreo y throttling inteligente de memoria
- **Pruebas Distribuidas**: Soporte para pruebas distribuidas multi-nodo
- **Fingerprinting**: Fingerprinting y análisis automático del target
- **Detección de Vulnerabilidades**: Análisis de headers de seguridad y detección de vulnerabilidades

---

## 📦 Requisitos

### Requisitos del Sistema

- **Python**: 3.7 o superior
- **Sistema Operativo**: Windows, Linux, o macOS
- **RAM**: Mínimo 2GB (4GB+ recomendado)
- **Red**: Conexión a internet para pruebas de target

### Dependencias de Python

- Flask
- Flask-Cors
- requests
- urllib3
- psutil

### Herramientas Opcionales

La herramienta soporta 40+ herramientas de prueba externas. Ver [Herramientas Soportadas](#-herramientas-soportadas) para la lista completa. Las herramientas se pueden instalar automáticamente usando:

```bash
python loadtest.py --install-tools
```

---

## 🚀 Instalación

### Instalación Rápida

#### Linux/macOS

```bash
# Clonar el repositorio
git clone https://github.com/Remiily/Load-Test-Tool.git
cd Load-Test-Tool

# Ejecutar script de instalación
chmod +x install.sh
./install.sh
```

#### Windows

```bash
# Clonar el repositorio
git clone https://github.com/Remiily/Load-Test-Tool.git
cd Load-Test-Tool

# Ejecutar script de instalación
install.bat
```

### Instalación Manual

1. **Instalar dependencias de Python:**

```bash
pip install -r requirements.txt
```

2. **Verificar instalación:**

```bash
python loadtest.py --show-tools
```

3. **Instalar herramientas de prueba (opcional):**

```bash
python loadtest.py --install-tools
```

### Instalación con Entorno Virtual (Recomendado)

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
# En Linux/macOS:
source venv/bin/activate
# En Windows:
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

Para instrucciones detalladas de instalación, ver [INSTALL.md](INSTALL.md).

---

## 🏃 Inicio Rápido

### Uso Básico

```bash
# Ejecutar una prueba de carga básica
python loadtest.py -t https://example.com -d 60 -p MODERATE

# Iniciar panel web
python loadtest.py --web

# Verificar herramientas disponibles
python loadtest.py --show-tools

# Instalar herramientas faltantes
python loadtest.py --install-tools
```

### Panel Web

Inicia la interfaz web:

```bash
python loadtest.py --web
```

Luego abre tu navegador en: `http://localhost:5000`

---

## 📖 Uso

### Interfaz de Línea de Comandos

#### Sintaxis Básica

```bash
python loadtest.py -t <target> [opciones]
```

#### Argumentos Requeridos

- `-t, --target`: URL del target o dirección IP

#### Opciones Comunes

```bash
# Duración y nivel de potencia
-d, --duration <segundos>     Duración de la prueba (default: 60)
-p, --power <nivel>           Nivel de potencia: TEST, LIGHT, MODERATE, MEDIUM, 
                              HEAVY, EXTREME, DEVASTATOR, APOCALYPSE, GODMODE

# Conexiones y threads
-c, --connections <num>       Máximo de conexiones (default: 10000)
--threads <num>               Máximo de threads (default: 400)

# Modo de ataque
-m, --mode <modo>             Modo de ataque: MIXED, CONSTANT, BURST, RAMP_UP

# Opciones avanzadas
--bypass-waf                  Activar técnicas de bypass de WAF
--stealth                     Activar modo stealth
--large-payloads              Usar payloads grandes
--no-auto-throttle            Desactivar throttling automático
--no-memory-monitoring        Desactivar monitoreo de memoria

# Otras opciones
--web                         Iniciar panel web
--web-port <puerto>           Puerto para panel web (default: 5000)
--show-tools                  Mostrar estado de herramientas disponibles
--install-tools               Instalar herramientas faltantes
--show-params                 Mostrar todos los parámetros configurables
--check-update                Verificar si hay actualizaciones disponibles
--update                      Actualizar la herramienta desde GitHub
--no-auto-update-check        Desactivar verificación automática de actualizaciones
--debug                       Activar modo debug
--dry-run                     Simulación sin ejecutar
```

#### Ejemplos

```bash
# Prueba ligera por 30 segundos
python loadtest.py -t https://example.com -d 30 -p LIGHT

# Prueba de carga pesada con conexiones personalizadas
python loadtest.py -t https://example.com -d 120 -p HEAVY -c 20000 --threads 500

# Modo stealth con bypass de WAF
python loadtest.py -t https://example.com -d 60 -p MODERATE --stealth --bypass-waf

# Modo de ataque burst
python loadtest.py -t https://example.com -d 60 -p MEDIUM -m BURST

# Panel web en puerto personalizado
python loadtest.py --web --web-port 8080

# Verificar actualizaciones
python loadtest.py --check-update

# Actualizar la herramienta
python loadtest.py --update
```

---

## ⚙️ Configuración

### Niveles de Potencia

| Nivel | Multiplicador | Descripción |
|-------|--------------|-------------|
| TEST | 1x | Carga mínima para pruebas |
| LIGHT | 3x | Carga ligera |
| MODERATE | 8x | Carga moderada (default) |
| MEDIUM | 16x | Carga media |
| HEAVY | 30x | Carga pesada |
| EXTREME | 60x | Carga extrema |
| DEVASTATOR | 120x | Carga muy alta |
| APOCALYPSE | 250x | Carga máxima |
| GODMODE | 500x | Carga extrema máxima |

### Modos de Ataque

- **MIXED**: Combina múltiples técnicas de ataque
- **CONSTANT**: Tasa constante de requests
- **BURST**: Patrón de ráfagas con intervalos
- **RAMP_UP**: Carga gradualmente creciente

### Umbrales de Memoria

- **Advertencia**: 60% - Advertencia temprana
- **Crítico**: 75% - Acción inmediata
- **OOM**: 85% - Detener para prevenir reinicio del sistema
- **Emergencia**: 90% - Terminación agresiva de procesos

---

## 🛠️ Herramientas Soportadas

LoadTest Enterprise soporta 40+ herramientas estándar de la industria en múltiples categorías:

### Pruebas de Carga HTTP
- wrk, vegeta, bombardier, hey, ab, siege
- h2load, locust, k6, artillery, tsung, jmeter

### Pruebas Layer 4
- hping3, nping, slowhttptest, masscan, zmap

### Pruebas WebSocket
- websocat, wscat

### Herramientas Avanzadas
- gatling, tsung, wrk2, drill, http2bench, weighttp, httperf, autocannon

### Herramientas Especializadas
- goldeneye, hulk, slowloris, y más

### Estado de Herramientas

Verificar qué herramientas están instaladas:

```bash
python loadtest.py --show-tools
```

Instalar herramientas faltantes automáticamente:

```bash
python loadtest.py --install-tools
```

---

## 📊 Reportes

### Generación de Reportes

Los reportes se generan automáticamente después de cada ejecución de prueba y se guardan en el directorio `loadtest_output/reports/`.

### Contenido de Reportes

- **Información General**: Target, duración, nivel de potencia
- **Estadísticas**: Requests enviados, respuestas recibidas, tasas de error
- **Códigos HTTP**: Distribución de códigos de estado HTTP
- **Análisis de Latencia**: Percentiles P50, P75, P90, P95, P99
- **Métricas de Rendimiento**: RPS, throughput, tiempos de respuesta
- **Análisis de Errores**: Desglose detallado de errores
- **Recomendaciones**: Recomendaciones accionables basadas en resultados
- **Gráficos**: Representación visual de métricas

### Ver Reportes

Los reportes se guardan como archivos HTML. Ábrelos en cualquier navegador web:

```bash
# Los reportes se guardan en:
loadtest_output/reports/report_YYYYMMDD_HHMMSS.html
```

---

## 🌐 Panel Web

El panel web proporciona una interfaz moderna para:

- **Configuración**: Configuración fácil de parámetros de prueba
- **Monitoreo en Tiempo Real**: Estadísticas y métricas en vivo
- **Gestión de Herramientas**: Ver e instalar herramientas de prueba
- **Visualización de Reportes**: Navegar y ver reportes generados
- **Fingerprinting**: Análisis del target y recomendaciones
- **Control de Ataques**: Iniciar/detener pruebas desde la interfaz

### Iniciar el Panel Web

```bash
python loadtest.py --web
```

Acceder en: `http://localhost:5000`

---

## 💡 Ejemplos

### Ejemplo 1: Prueba de Carga Básica

```bash
python loadtest.py -t https://api.example.com -d 60 -p MODERATE
```

### Ejemplo 2: Prueba de Estrés con Configuración Personalizada

```bash
python loadtest.py -t https://example.com \
  -d 300 \
  -p HEAVY \
  -c 50000 \
  --threads 1000 \
  -m RAMP_UP
```

### Ejemplo 3: Pruebas de Seguridad

```bash
python loadtest.py -t https://example.com \
  -d 120 \
  -p MEDIUM \
  --stealth \
  --bypass-waf \
  --large-payloads
```

### Ejemplo 4: Uso del Panel Web

```bash
# Iniciar panel web
python loadtest.py --web

# Acceder en navegador
# http://localhost:5000
```

---

## 🔄 Sistema de Auto-Actualización

LoadTest Enterprise incluye un sistema de actualización automática que verifica nuevas versiones desde GitHub.

### Características

- **Verificación Automática**: Verifica actualizaciones una vez al día cuando ejecutas la herramienta
- **Verificación Manual**: Usa `--check-update` para verificar manualmente actualizaciones
- **Actualización con Un Clic**: Usa `--update` para descargar e instalar actualizaciones automáticamente
- **Actualizaciones Seguras**: Crea backups de archivos antes de actualizar
- **Comparación de Versiones**: Compara versión local con versión en GitHub

### Uso

```bash
# Verificar actualizaciones manualmente
python loadtest.py --check-update

# Actualizar a la última versión
python loadtest.py --update

# Desactivar verificación automática de actualizaciones
python loadtest.py --no-auto-update-check -t https://example.com
```

### Cómo Funciona

1. **Verificación Automática**: Cuando ejecutas la herramienta, verifica automáticamente actualizaciones (una vez cada 24 horas)
2. **Detección de Versión**: Compara tu versión local con la versión en GitHub
3. **Descarga Segura**: Descarga archivos y crea backups antes de reemplazar
4. **Actualización de Archivos**: Actualiza archivos principales (loadtest.py, loadtest_web.py, requirements.txt, etc.)
5. **Reinicio Requerido**: Después de actualizar, reinicia la herramienta para usar la nueva versión

### Proceso de Actualización

Cuando ejecutas `--update`, la herramienta:

1. Verifica si hay una versión más nueva disponible
2. Descarga archivos actualizados desde GitHub
3. Crea backups de archivos existentes (extensión `.backup`)
4. Reemplaza archivos con nuevas versiones
5. Muestra un resumen de archivos actualizados

### Repositorio

La herramienta verifica actualizaciones desde: `https://github.com/Remiily/Load-Test-Tool`

---

## 🔧 Solución de Problemas

### Problemas Comunes

#### Problema: "No module named 'flask'"

**Solución:**
```bash
pip install Flask Flask-Cors
```

#### Problema: "Tool not found"

**Solución:**
```bash
# Instalar herramientas faltantes
python loadtest.py --install-tools

# O instalar manualmente
# Linux: sudo apt install <tool-name>
# macOS: brew install <tool-name>
# Windows: choco install <tool-name>
```

#### Problema: "Permission denied"

**Solución:**
- En Linux/macOS, algunas herramientas pueden requerir sudo para instalación
- Usar entorno virtual para evitar problemas de permisos

#### Problema: "Memory errors"

**Solución:**
- Reducir nivel de potencia: `-p LIGHT` o `-p MODERATE`
- Reducir conexiones: `-c 5000`
- Activar auto-throttle (default): El monitoreo de memoria está activado por defecto

#### Problema: "Web panel not starting"

**Solución:**
```bash
# Verificar si el puerto está disponible
# Probar puerto diferente
python loadtest.py --web --web-port 8080

# Verificar si loadtest_web.py existe
ls loadtest_web.py
```

#### Problema: "Update failed"

**Solución:**
```bash
# Verificar conexión a internet
# Verificar que GitHub sea accesible
# Intentar actualización manual descargando archivos desde GitHub

# Restaurar desde backup si es necesario
# Los archivos de backup tienen extensión .backup
```

Para más ayuda con solución de problemas, ver [INSTALL.md](INSTALL.md).

---

## 🤝 Contribuir

¡Aceptamos contribuciones! Por favor sigue estos pasos:

1. Fork el repositorio
2. Crea una rama de característica (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Guías de Contribución

- Seguir guías de estilo PEP 8
- Agregar comentarios para código complejo
- Actualizar documentación según sea necesario
- Probar tus cambios exhaustivamente
- Asegurar compatibilidad hacia atrás

---

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

---

## ⚠️ Descargo de Responsabilidad

**IMPORTANTE**: Esta herramienta está diseñada **solo para pruebas de seguridad autorizadas y análisis de rendimiento**.

- Solo usar en sistemas que posees o tienes permiso escrito explícito para probar
- El uso no autorizado de esta herramienta puede violar leyes y regulaciones
- Los autores y contribuidores no son responsables del uso indebido de este software
- Siempre cumplir con leyes y regulaciones aplicables
- Usar responsablemente y éticamente

**Al usar esta herramienta, aceptas usarla solo para propósitos legítimos y aceptas plena responsabilidad por tus acciones.**

---

## 📞 Soporte

- **Documentación**: Ver [INSTALL.md](INSTALL.md) para instrucciones detalladas de instalación
- **Issues**: Reportar problemas en la página de GitHub Issues
- **Preguntas**: Abrir una discusión en GitHub Discussions

---

## 🙏 Agradecimientos

- Todos los desarrolladores de las herramientas de prueba soportadas
- La comunidad de código abierto
- Profesionales de seguridad que proporcionaron retroalimentación

---

<div align="center">

**LoadTest Enterprise** - Pruebas de Carga Web Profesionales y Análisis de Rendimiento

Hecho con ❤️ para la comunidad de seguridad y DevOps

</div>
