# LoadTest Enterprise

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

**Suite Empresarial de Pruebas de Carga Web y Análisis de Rendimiento**

Herramienta profesional para pruebas de seguridad autorizadas y análisis de rendimiento.

[Características](#-características) • [Instalación](#-instalación) • [Uso](#-uso) • [Documentación Completa](#-documentación-completa) • [Contribuir](#-contribuir)

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
- [Documentación Completa](#-documentación-completa)
  - [Sistema de Evasión Avanzado](#-sistema-de-evasión-avanzado)
  - [Auto-Configuración Inteligente](#-auto-configuración-inteligente)
  - [Despliegue Gradual de Herramientas](#-despliegue-gradual-de-herramientas)
  - [Fingerprinting y Análisis](#-fingerprinting-y-análisis)
  - [Monitoreo y Gestión de Recursos](#-monitoreo-y-gestión-de-recursos)
  - [Sistema de Reportes](#-sistema-de-reportes)
- [Herramientas Soportadas](#-herramientas-soportadas)
- [Panel Web](#-panel-web)
- [Ejemplos](#-ejemplos)
- [Sistema de Auto-Actualización](#-sistema-de-auto-actualización)
- [Seguridad y Protección](#-seguridad-y-protección)
- [Solución de Problemas](#-solución-de-problemas)
- [Contribuir](#-contribuir)
- [Licencia](#-licencia)
- [Descargo de Responsabilidad](#-descargo-de-responsabilidad)

---

## 🎯 Resumen

**LoadTest Enterprise** es una suite completa de pruebas de carga web y análisis de rendimiento diseñada para profesionales de seguridad y equipos DevOps. Proporciona capacidades avanzadas para pruebas de estrés, análisis de rendimiento y evaluación de seguridad de aplicaciones y servicios web.

### Capacidades Clave

- **Integración Multi-Herramienta**: Soporta 40+ herramientas estándar de la industria para pruebas de carga
- **Sistema de Evasión Avanzado**: 10+ técnicas de evasión funcionales y específicas por WAF
- **Auto-Configuración Inteligente**: Configuración automática basada en fingerprint del target
- **Despliegue Gradual**: Sistema de despliegue de herramientas con throttling para evitar freezes
- **Monitoreo Inteligente**: Monitoreo de recursos en tiempo real con throttling automático
- **Reportes Avanzados**: Reportes HTML completos con métricas detalladas y recomendaciones
- **Interfaz Web**: Panel web moderno y responsive para configuración y monitoreo
- **Auto-Instalación**: Instalación automática de herramientas de prueba requeridas
- **Listo para Empresa**: Diseño profesional adecuado para entornos corporativos

---

## ✨ Características

### Características Principales

- 🔄 **Múltiples Modos de Ataque**: MIXED, CONSTANT, BURST, RAMP_UP
- 🛡️ **Sistema de Evasión Avanzado**: 10+ técnicas de evasión funcionales
- 🤖 **Auto-Configuración**: Configuración automática basada en fingerprint
- 📊 **Monitoreo en Tiempo Real**: Métricas de CPU, memoria y red
- 🎯 **Gestión Inteligente de Recursos**: Throttling automático basado en recursos del sistema
- 📈 **Reportes Completos**: Reportes HTML detallados con gráficos y recomendaciones
- 🌐 **Panel Web**: Interfaz web moderna y responsive para configuración y monitoreo
- 🔧 **Auto-Instalación de Herramientas**: Instala automáticamente herramientas de prueba faltantes
- ⚡ **Alto Rendimiento**: Optimizado para máximo throughput
- 📱 **Multi-Protocolo**: Soporte para HTTP/1.1, HTTP/2, WebSocket
- 🎨 **UI Profesional**: Diseño y branding listo para empresas

### Características Avanzadas

- **Connection Pooling**: Conexiones reutilizables para mejor rendimiento
- **Optimización TCP**: Optimizaciones avanzadas de la pila TCP
- **Multiplexing HTTP/2**: Soporte para protocolo HTTP/2
- **Rate Adaptive**: Ajuste dinámico de tasa basado en respuesta del servidor
- **Gestión de Memoria**: Monitoreo y throttling inteligente de memoria
- **Fingerprinting**: Fingerprinting y análisis automático del target
- **Detección de Vulnerabilidades**: Análisis de headers de seguridad y detección de vulnerabilidades
- **Detección de WAF/CDN**: Detección automática y configuración de evasión
- **Despliegue Gradual**: Sistema de despliegue con throttling para evitar freezes

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

# Opciones de evasión
--bypass-waf                  Activar técnicas de bypass de WAF
--stealth                     Activar modo stealth (headers realistas + IP rotation)

# Opciones avanzadas
--large-payloads               Usar payloads grandes
--no-auto-throttle            Desactivar throttling automático
--no-memory-monitoring        Desactivar monitoreo de memoria
--socket-attack               Activar ataque socket-based de bajo nivel

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

# Modo stealth con bypass de WAF (evasión completa)
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

| Nivel | Multiplicador | Descripción | Uso Recomendado |
|-------|--------------|-------------|-----------------|
| TEST | 1x | Carga mínima para pruebas | Testing inicial |
| LIGHT | 3x | Carga ligera | Pruebas básicas |
| MODERATE | 8x | Carga moderada (default) | Uso general |
| MEDIUM | 16x | Carga media | Pruebas intermedias |
| HEAVY | 30x | Carga pesada | Pruebas intensivas |
| EXTREME | 60x | Carga extrema | Pruebas avanzadas |
| DEVASTATOR | 120x | Carga muy alta | Pruebas extremas |
| APOCALYPSE | 250x | Carga máxima | Pruebas máximas |
| GODMODE | 500x | Carga extrema máxima | Solo para sistemas robustos |

### Modos de Ataque

- **MIXED**: Combina múltiples técnicas de ataque y herramientas
- **CONSTANT**: Tasa constante de requests
- **BURST**: Patrón de ráfagas con intervalos
- **RAMP_UP**: Carga gradualmente creciente

### Umbrales de Memoria

- **Advertencia**: 60% - Advertencia temprana, reduce carga
- **Crítico**: 75% - Acción inmediata, reduce herramientas
- **OOM**: 85% - Detener para prevenir reinicio del sistema
- **Emergencia**: 90% - Terminación agresiva de procesos

---

## 📚 Documentación Completa

### 🛡️ Sistema de Evasión Avanzado

LoadTest Enterprise incluye un sistema completo de evasión con 10+ técnicas funcionales y específicas por WAF.

#### Técnicas de Evasión Disponibles

1. **URL Encoding**
   - Codificación de caracteres especiales en URLs
   - Aplicación automática a todos los requests
   - Soporte para encoding simple y doble

2. **Case Variation**
   - Variación de mayúsculas/minúsculas en paths y parámetros
   - Evasión de filtros basados en case-sensitive
   - Aplicación aleatoria en cada request

3. **Parameter Pollution**
   - Duplicación de parámetros en URLs
   - Múltiples valores para el mismo parámetro
   - Confusión de parsers de WAF

4. **Method Tampering**
   - Uso de métodos HTTP alternativos (GET, POST, HEAD, OPTIONS)
   - Rotación automática de métodos
   - Evasión de filtros basados en método

5. **Header Injection**
   - Inyección de headers especiales
   - Headers con caracteres codificados
   - Manipulación de headers de navegador

6. **Cookie Manipulation**
   - Generación de cookies falsas realistas
   - Rotación de cookies de sesión
   - Cookies específicas por WAF (ej: __cfduid para Cloudflare)

7. **Double Encoding**
   - Codificación doble de parámetros
   - Evasión de filtros de una sola pasada
   - Aplicación selectiva según WAF

8. **Unicode Normalization**
   - Uso de caracteres Unicode similares
   - Reemplazo de caracteres ASCII por Unicode
   - Evasión de filtros basados en ASCII

9. **Chunked Encoding**
   - Encoding fragmentado de requests
   - Evasión de análisis de payload completo
   - Desactivado para WAFs que lo detectan

10. **Protocol Mixing**
    - Mezcla de protocolos HTTP/1.1 y HTTP/2
    - Evasión de filtros específicos de protocolo
    - Aplicación automática según configuración

#### Evasión Específica por WAF

El sistema detecta automáticamente el WAF y aplica técnicas específicas:

**Cloudflare:**
- ✅ URL Encoding, Case Variation, Parameter Pollution
- ✅ Header Injection, Cookie Manipulation
- ✅ Double Encoding, Unicode Normalization
- ✅ Method Tampering
- ❌ Chunked Encoding (detectado por Cloudflare)
- ❌ Protocol Mixing

**AWS WAF:**
- ✅ Todas las técnicas activas
- ✅ Configuración completa de evasión

**Imperva:**
- ✅ URL Encoding, Case Variation, Parameter Pollution
- ✅ Cookie Manipulation, Double Encoding
- ✅ Unicode Normalization, Chunked Encoding
- ✅ Method Tampering
- ❌ Header Injection (detectado por Imperva)

**Akamai:**
- ✅ URL Encoding, Case Variation, Parameter Pollution
- ✅ Header Injection, Cookie Manipulation
- ✅ Double Encoding, Unicode Normalization
- ✅ Method Tampering, Protocol Mixing
- ❌ Chunked Encoding

**Sucuri / F5 BigIP:**
- ✅ Todas las técnicas activas
- ✅ Configuración completa

#### Headers de Evasión

El sistema genera headers realistas y rotativos:

- **User-Agent Rotation**: 12+ User-Agents realistas (Chrome, Firefox, Safari, Edge, Mobile, Bots)
- **IP Rotation**: IPs falsas realistas en 10+ headers diferentes
  - X-Forwarded-For, X-Real-IP, X-Originating-IP
  - CF-Connecting-IP (Cloudflare)
  - True-Client-IP (Cloudflare Enterprise)
  - X-Amzn-Trace-Id (AWS)
  - X-Akamai-Request-ID (Akamai)
- **Headers de Navegador Real**: Sec-Fetch-*, Viewport-Width, Width, DNT
- **Referer Rotation**: Referers realistas de buscadores
- **Origin Rotation**: Orígenes variados

#### Activación de Evasión

La evasión se activa automáticamente cuando:
- Se detecta un WAF (activación automática de WAF Bypass)
- Se activa manualmente con `--bypass-waf`
- Se activa Stealth Mode con `--stealth`

### 🤖 Auto-Configuración Inteligente

El sistema analiza automáticamente el target y configura la mejor estrategia de ataque.

#### Proceso de Auto-Configuración

1. **Fingerprinting del Target**
   - Análisis de servidor web
   - Detección de framework
   - Detección de tecnologías
   - Análisis de security headers

2. **Detección de WAF**
   - Detección automática de WAF
   - Identificación de tipo de WAF
   - Activación automática de bypass

3. **Detección de CDN**
   - Identificación de CDN
   - Ajuste de estrategia según CDN

4. **Detección de Rate Limiting**
   - Análisis de headers de rate limiting
   - Extracción de límites numéricos
   - Ajuste automático de conexiones

5. **Aplicación de Configuración**
   - Activación de técnicas de evasión específicas
   - Ajuste de parámetros (conexiones, payloads, etc.)
   - Configuración de modo de ataque

#### Ejemplo de Auto-Configuración

Cuando se detecta Cloudflare:
```
🤖 Auto-configurando estrategia de ataque...
✅ WAF Bypass activado (WAF detectado: cloudflare)
✅ Técnicas de evasión optimizadas para cloudflare
✅ Stealth Mode activado (Cloudflare detectado)
✅ Conexiones reducidas a 5000 (Cloudflare)
```

### 📦 Despliegue Gradual de Herramientas

Sistema de despliegue inteligente que evita freezes del sistema.

#### Características

- **Verificación de Recursos**: Verifica memoria y CPU antes de cada despliegue
- **Throttling Progresivo**: Aumenta delays entre despliegues progresivamente
- **Pausas Inteligentes**: Espera si recursos están altos
- **Límites Dinámicos**: Ajusta límite de herramientas según recursos disponibles

#### Proceso de Despliegue

1. Verificación inicial de recursos
2. Despliegue de herramientas prioritarias (más eficientes)
3. Pausa entre despliegues (delay progresivo)
4. Verificación continua de recursos
5. Despliegue de herramientas secundarias si hay espacio
6. Detención automática si recursos críticos

#### Beneficios

- ✅ Sin freezes del sistema
- ✅ Uso eficiente de recursos
- ✅ Despliegue controlado
- ✅ Protección del sistema

### 🔍 Fingerprinting y Análisis

Sistema completo de análisis del target antes del ataque.

#### Funciones de Fingerprinting

1. **Análisis de Servidor Web**
   - Detección de servidor (Apache, Nginx, IIS, etc.)
   - Análisis de versión
   - Detección de configuraciones

2. **Detección de Framework**
   - WordPress, Joomla, Drupal
   - Frameworks modernos (React, Angular, Vue)
   - Detección automática

3. **Detección de Tecnologías**
   - Lenguajes de programación
   - Bases de datos
   - Servicios y APIs

4. **Análisis de Security Headers**
   - HSTS, CSP, X-Frame-Options
   - Headers de rate limiting
   - Headers de seguridad faltantes

5. **Detección de Vulnerabilidades**
   - Archivos expuestos
   - Información sensible en headers
   - Configuraciones inseguras
   - Problemas SSL/TLS
   - Versiones desactualizadas

6. **Detección de WAF/CDN**
   - Cloudflare, AWS WAF, Imperva, Akamai
   - Sucuri, F5 BigIP, Barracuda
   - Detección por headers y comportamiento

7. **Escaneo de Puertos** (para IPs)
   - Escaneo de puertos comunes
   - Detección de servicios
   - Descubrimiento de endpoints

### 📊 Monitoreo y Gestión de Recursos

Sistema avanzado de monitoreo en tiempo real.

#### Métricas Monitoreadas

- **CPU**: Uso de CPU en tiempo real
- **Memoria**: Uso, disponible, porcentaje
- **Disco**: Uso y espacio disponible
- **Red**: Estadísticas de red
- **Requests**: Requests enviados, recibidos, errores
- **Latencia**: Latencia promedio, P95, P99
- **RPS**: Requests por segundo, peak RPS
- **Códigos HTTP**: Distribución de códigos de estado

#### Gestión Inteligente de Memoria

- **Umbrales Configurables**:
  - Advertencia (60%): Reduce carga
  - Crítico (75%): Reduce herramientas
  - OOM (85%): Detiene todo
  - Emergencia (90%): Termina procesos agresivamente

- **Acciones Automáticas**:
  - Reducción de workers
  - Terminación de procesos externos
  - Pausa de despliegue
  - Limpieza de recursos

#### Rate Adaptive

Ajuste dinámico de tasa según respuesta del servidor:
- Aumenta tasa si responde bien (200)
- Reduce tasa si hay rate limiting (429)
- Ajusta según errores del servidor (500+)

### 📈 Sistema de Reportes

Reportes HTML completos con análisis detallado.

#### Contenido de Reportes

1. **Información General**
   - Target, duración, nivel de potencia
   - Modo de ataque, configuración

2. **Estadísticas Generales**
   - Requests enviados
   - Responses recibidas
   - Errores
   - Duración real

3. **Métricas de Rendimiento**
   - RPS promedio y peak
   - Throughput
   - Latencia (promedio, min, max, P50, P75, P90, P95, P99)

4. **Códigos HTTP**
   - Distribución de códigos de estado
   - Porcentajes
   - Gráficos visuales

5. **Análisis de Errores**
   - Tipos de errores
   - Frecuencia
   - Patrones

6. **Recomendaciones**
   - Recomendaciones basadas en resultados
   - Sugerencias de optimización
   - Análisis de rendimiento

7. **Gráficos y Visualizaciones**
   - Gráficos de códigos HTTP
   - Gráficos de latencia
   - Visualizaciones interactivas

---

## 🛠️ Herramientas Soportadas

LoadTest Enterprise soporta 40+ herramientas estándar de la industria en múltiples categorías:

### Pruebas de Carga HTTP
- **wrk**: Herramienta de benchmarking HTTP de alto rendimiento
- **vegeta**: Herramienta de pruebas de carga HTTP
- **bombardier**: Herramienta de pruebas de carga rápida
- **hey**: Herramienta de pruebas de carga HTTP
- **ab** (Apache Bench): Herramienta clásica de benchmarking
- **siege**: Herramienta de pruebas de carga HTTP
- **h2load**: Herramienta de pruebas HTTP/2
- **locust**: Framework de pruebas de carga basado en Python
- **k6**: Herramienta de pruebas de carga moderna
- **artillery**: Herramienta de pruebas de carga y rendimiento
- **tsung**: Herramienta de pruebas de carga distribuida
- **jmeter**: Herramienta completa de pruebas de carga

### Pruebas Layer 4
- **hping3**: Herramienta de pruebas de red avanzada
- **nping**: Herramienta de pruebas de red de Nmap
- **slowhttptest**: Herramienta de pruebas de slow HTTP attacks
- **masscan**: Escáner de puertos masivo
- **zmap**: Escáner de red de Internet

### Pruebas WebSocket
- **websocat**: Cliente WebSocket de línea de comandos
- **wscat**: Cliente WebSocket interactivo

### Herramientas Avanzadas
- **gatling**: Framework de pruebas de carga
- **wrk2**: Versión mejorada de wrk
- **drill**: Herramienta de pruebas HTTP
- **http2bench**: Herramienta de benchmarking HTTP/2
- **weighttp**: Herramienta de pruebas de carga ligera
- **httperf**: Herramienta de medición de rendimiento HTTP
- **autocannon**: Herramienta de pruebas de carga rápida

### Herramientas Especializadas
- **goldeneye**: Herramienta de pruebas de carga HTTP
- **hulk**: Herramienta de pruebas de carga
- **slowloris**: Herramienta de slow HTTP attacks
- **pyloris**: Herramienta de slow HTTP attacks en Python
- **rudy**: Herramienta de slow HTTP POST attacks
- **xerxes**: Herramienta de pruebas de carga
- **hoic**: Herramienta de pruebas de carga
- **loic**: Herramienta de pruebas de carga
- **reaper**: Herramienta de pruebas de carga
- **torshammer**: Herramienta de slow HTTP attacks
- **ddos-ripper**: Herramienta de pruebas de carga

### Estado de Herramientas

Verificar qué herramientas están instaladas:

```bash
python loadtest.py --show-tools
```

Instalar herramientas faltantes automáticamente:

```bash
python loadtest.py --install-tools
```

El sistema detecta automáticamente el sistema operativo y el gestor de paquetes disponible (apt, yum, brew, choco, npm, pip) e instala las herramientas correspondientes.

---

## 🌐 Panel Web

El panel web proporciona una interfaz moderna y responsive para:

### Funcionalidades del Panel

- **Configuración Visual**: Configuración fácil de todos los parámetros
- **Flujo Guiado**: Proceso paso a paso (Target → Fingerprint → Recomendaciones → Stress Test)
- **Monitoreo en Tiempo Real**: Estadísticas y métricas en vivo
- **Gestión de Herramientas**: Ver estado e instalar herramientas
- **Visualización de Reportes**: Navegar y ver reportes generados
- **Fingerprinting Interactivo**: Ejecutar fingerprint y ver resultados
- **Control de Ataques**: Iniciar/detener pruebas desde la interfaz

### Secciones del Panel

1. **Flujo Guiado**
   - Paso 1: Definir Target
   - Paso 2: Ejecutar Fingerprint
   - Paso 3: Ver Recomendaciones
   - Paso 4: Configurar y Confirmar
   - Paso 5: Iniciar Stress Test

2. **Configuración**
   - Target y duración
   - Nivel de potencia
   - Modo de ataque
   - Recursos (conexiones, threads)
   - Técnicas de evasión
   - Optimizaciones avanzadas
   - Monitoreo

3. **Monitor**
   - Estadísticas en tiempo real
   - Gráficos de códigos HTTP
   - Gráficos de latencia
   - Métricas del sistema

4. **Reportes**
   - Lista de reportes generados
   - Visualización de reportes
   - Exportación de datos

5. **Herramientas**
   - Estado de herramientas
   - Instalación de herramientas
   - Categorización de herramientas

6. **Parámetros**
   - Vista completa de todos los parámetros
   - Valores actuales
   - Descripción de parámetros

### Iniciar el Panel Web

```bash
python loadtest.py --web
```

Acceder en: `http://localhost:5000`

Para cambiar el puerto:

```bash
python loadtest.py --web --web-port 8080
```

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

### Ejemplo 3: Pruebas de Seguridad con Evasión Completa

```bash
python loadtest.py -t https://example.com \
  -d 120 \
  -p MEDIUM \
  --stealth \
  --bypass-waf \
  --large-payloads
```

### Ejemplo 4: Prueba con Auto-Configuración

```bash
# El sistema detectará automáticamente WAF/CDN y configurará evasión
python loadtest.py -t https://example.com -d 60 -p MODERATE
```

### Ejemplo 5: Panel Web

```bash
# Iniciar panel web
python loadtest.py --web

# Acceder en navegador
# http://localhost:5000
```

### Ejemplo 6: Verificar y Instalar Herramientas

```bash
# Ver estado de herramientas
python loadtest.py --show-tools

# Instalar herramientas faltantes
python loadtest.py --install-tools
```

---

## 🔄 Sistema de Auto-Actualización

LoadTest Enterprise incluye un sistema de actualización automática que verifica nuevas versiones desde GitHub.

### Características

- **Verificación Automática**: Verifica actualizaciones una vez al día cuando ejecutas la herramienta
- **Verificación Manual**: Usa `--check-update` para verificar manualmente actualizaciones
- **One-Click Update**: Usa `--update` para descargar e instalar actualizaciones automáticamente
- **Actualizaciones Seguras**: Crea backups de archivos antes de actualizar
- **Version Comparison**: Compara versión local con versión en GitHub

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

1. **Verificación Automática**: Cuando ejecutas la herramienta, verifica actualizaciones (una vez cada 24 horas)
2. **Version Detection**: Compara tu versión local con la versión en GitHub
3. **Safe Download**: Descarga archivos y crea backups antes de reemplazar
4. **File Updates**: Actualiza archivos principales (loadtest.py, loadtest_web.py, requirements.txt, etc.)
5. **Restart Required**: Después de actualizar, reinicia la herramienta para usar la nueva versión

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

## 🔧 Funciones y Características Detalladas

### Funciones de Despliegue de Ataques

LoadTest Enterprise incluye múltiples funciones de despliegue de ataques, cada una optimizada para diferentes escenarios:

#### Ataques HTTP Estándar

1. **deploy_custom_http_attack()**
   - Ataque HTTP personalizado optimizado con Python requests
   - Usa ConnectionManager para pooling de conexiones
   - Soporte completo de técnicas de evasión
   - Rate adaptive automático
   - Pre-calentamiento de conexiones
   - **Uso**: Siempre desplegado en modo MIXED

2. **deploy_wrk_attack()**
   - Ataque con wrk (herramienta de benchmarking de alto rendimiento)
   - Optimizado para máximo throughput
   - **Límites**: Máximo 1000 conexiones, 50 threads
   - **Uso**: Modo MIXED, CONSTANT

3. **deploy_vegeta_attack()**
   - Ataque con vegeta (herramienta de pruebas de carga HTTP)
   - Control de tasa configurable
   - **Uso**: Modo MIXED, BURST

4. **deploy_bombardier_attack()**
   - Ataque con bombardier (herramienta rápida de pruebas de carga)
   - Soporte para múltiples conexiones
   - **Uso**: Modo MIXED, BURST

5. **deploy_hey_attack()**
   - Ataque con hey (herramienta de pruebas de carga HTTP)
   - Control de QPS (queries per second)
   - **Uso**: Modo MIXED, RAMP_UP

6. **deploy_ab_attack()**
   - Ataque con Apache Bench (ab)
   - Herramienta clásica de benchmarking
   - **Uso**: Modo MIXED

7. **deploy_siege_attack()**
   - Ataque con siege
   - Modo benchmark
   - **Uso**: Modo MIXED

#### Ataques de Bajo Nivel

8. **deploy_socket_based_attack()**
   - Ataque socket-based de bajo nivel
   - Máximo rendimiento usando sockets raw
   - Reutilización de sockets
   - Soporte SSL/TLS
   - **Uso**: Activado con `--socket-attack`

9. **deploy_tcp_flood_advanced()**
   - Ataque TCP flood avanzado
   - Múltiples técnicas de flooding TCP
   - **Uso**: Modo MIXED (avanzado)

10. **deploy_connection_exhaustion()**
    - Ataque de agotamiento de conexiones
    - Mantiene conexiones abiertas
    - **Uso**: Modo MIXED (avanzado)

#### Ataques Especializados

11. **deploy_slowloris()**
    - Ataque Slowloris (slow HTTP headers)
    - Envía headers lentamente
    - **Uso**: Modo MIXED

12. **deploy_rudy()**
    - Ataque RUDY (R U Dead Yet - slow HTTP POST)
    - Envía datos POST muy lentamente
    - **Uso**: Modo MIXED

13. **deploy_hoic()**
    - Ataque HOIC (High Orbit Ion Cannon)
    - Múltiples threads y conexiones
    - **Uso**: Modo MIXED

14. **deploy_slow_read_attack()**
    - Ataque de lectura lenta
    - Lee respuestas muy lentamente
    - **Uso**: Modo MIXED (avanzado)

15. **deploy_http_pipelining_flood()**
    - Ataque HTTP pipelining
    - Múltiples requests en una conexión
    - **Uso**: Modo MIXED (avanzado)

16. **deploy_ssl_renegotiation_attack()**
    - Ataque de renegociación SSL/TLS
    - Fuerza renegociaciones constantes
    - **Uso**: Modo MIXED (avanzado)

17. **deploy_fragmented_request_attack()**
    - Ataque de requests fragmentados
    - Fragmenta requests en múltiples paquetes
    - **Uso**: Modo MIXED (avanzado)

18. **deploy_http2_multiplexing_flood()**
    - Ataque HTTP/2 multiplexing
    - Múltiples streams en una conexión HTTP/2
    - **Uso**: Modo MIXED (avanzado)

19. **deploy_http_headers_bomb()**
    - Ataque de headers extremadamente grandes
    - Headers de 8KB a 32KB
    - **Uso**: Modo MIXED (avanzado)

20. **deploy_cookie_bomb()**
    - Ataque de cookies grandes
    - Múltiples cookies grandes
    - **Uso**: Modo MIXED (avanzado)

21. **deploy_method_override_attack()**
    - Ataque de métodos HTTP no estándar
    - Usa métodos como LOCK, UNLOCK, SEARCH, DEBUG
    - **Uso**: Modo MIXED (avanzado)

22. **deploy_zero_byte_attack()**
    - Ataque de zero-byte
    - Requests con payloads vacíos
    - **Uso**: Modo MIXED (avanzado)

23. **deploy_random_subdomain_attack()**
    - Ataque con subdominios aleatorios
    - Confunde CDN/WAF
    - **Uso**: Modo MIXED (avanzado)

#### Ataques Layer 4

24. **deploy_hping3_flood()**
    - Ataque con hping3
    - Flooding a nivel de red
    - **Uso**: Modo MIXED

25. **deploy_udp_flood()**
    - Ataque UDP flood
    - Saturación con paquetes UDP
    - **Uso**: Modo MIXED (avanzado)

26. **deploy_icmp_flood()**
    - Ataque ICMP flood (ping flood)
    - Saturación con pings
    - **Uso**: Modo MIXED (avanzado)

#### Herramientas de Framework

27. **deploy_locust_attack()**
    - Ataque con Locust
    - Framework de pruebas de carga basado en Python
    - **Uso**: Modo MIXED

28. **deploy_k6_attack()**
    - Ataque con k6
    - Herramienta moderna de pruebas de carga
    - **Uso**: Modo MIXED

29. **deploy_http2_attack()**
    - Ataque HTTP/2 con h2load
    - Soporte para HTTP/2 multiplexing
    - **Uso**: Modo MIXED

### Funciones de Análisis y Detección

#### Fingerprinting

- **fingerprint_target()**: Análisis completo del target
  - Detección de servidor web
  - Detección de framework
  - Detección de tecnologías
  - Análisis de security headers
  - Escaneo de vulnerabilidades
  - Escaneo de puertos (para IPs)
  - Descubrimiento de endpoints

#### Detección

- **detect_waf_advanced()**: Detección avanzada de WAF
  - Detección por headers
  - Pruebas con payloads maliciosos
  - Identificación de tipo de WAF

- **detect_cdn()**: Detección de CDN
  - Cloudflare, Akamai, Fastly, etc.
  - Detección por headers y comportamiento

- **detect_framework()**: Detección de framework
  - WordPress, Joomla, Drupal
  - Frameworks modernos

- **detect_technologies()**: Detección de tecnologías
  - Lenguajes, bases de datos, servicios

#### Análisis de Seguridad

- **analyze_security_headers()**: Análisis de security headers
  - HSTS, CSP, X-Frame-Options
  - Headers de rate limiting
  - Headers faltantes

- **scan_vulnerabilities()**: Escaneo de vulnerabilidades
  - Archivos expuestos
  - Información sensible
  - Configuraciones inseguras
  - Problemas SSL/TLS
  - Versiones desactualizadas

- **check_exposed_files()**: Verificación de archivos expuestos
- **check_information_disclosure()**: Verificación de divulgación de información
- **check_insecure_configurations()**: Verificación de configuraciones inseguras
- **check_ssl_tls_issues()**: Verificación de problemas SSL/TLS
- **check_outdated_versions()**: Verificación de versiones desactualizadas

#### Escaneo de Red

- **scan_ports_advanced()**: Escaneo avanzado de puertos
  - Detección de servicios por puerto
  - Identificación de protocolos

- **discover_endpoints_local_ip()**: Descubrimiento de endpoints en IPs locales
  - Escaneo de puertos comunes
  - Detección de servicios HTTP/HTTPS

### Funciones de Gestión y Monitoreo

#### Monitoreo

- **monitor_attack()**: Monitoreo avanzado del ataque
  - Estadísticas en tiempo real
  - Monitoreo de recursos
  - Gestión de memoria
  - Health checks de procesos

- **display_stats()**: Visualización de estadísticas
  - Requests, responses, errores
  - RPS, latencia
  - Códigos HTTP

- **check_process_health()**: Verificación de salud de procesos
  - Detección de procesos muertos
  - Reinicio automático si es necesario

#### Gestión de Recursos

- **check_system_resources()**: Verificación de recursos del sistema
  - CPU, memoria, disco
  - Validación de recursos suficientes

- **PerformanceMonitor**: Clase para monitoreo de rendimiento
  - Caché de métricas (1 segundo)
  - Reducción de llamadas a psutil
  - Métricas optimizadas

#### Gestión de Conexiones

- **ConnectionManager**: Clase para gestión de conexiones
  - Pool de sesiones HTTP reutilizables
  - Gestión thread-safe
  - Limpieza automática de recursos

### Funciones de Instalación

- **auto_install_all_tools()**: Instalación automática de todas las herramientas
  - Detección de sistema operativo
  - Detección de gestores de paquetes
  - Instalación automática

- **check_package_manager()**: Verificación de gestores de paquetes
  - apt, yum, brew, choco, npm, pip

- **get_install_commands()**: Generación de comandos de instalación
  - Comandos específicos por OS y herramienta

### Funciones de Reportes

- **generate_report()**: Generación de reporte completo
  - Recopilación de estadísticas
  - Análisis de resultados
  - Generación de recomendaciones

- **generate_html_report()**: Generación de reporte HTML
  - Reporte visual completo
  - Gráficos interactivos
  - Análisis detallado

- **generate_stress_recommendations()**: Generación de recomendaciones
  - Basadas en fingerprint
  - Configuración optimizada
  - Análisis de resultados

### Funciones de Actualización

- **check_for_updates()**: Verificación de actualizaciones
  - Comparación de versiones
  - Verificación desde GitHub

- **update_tool()**: Actualización de la herramienta
  - Descarga de archivos
  - Creación de backups
  - Reemplazo de archivos

- **auto_check_updates()**: Verificación automática
  - Una vez al día
  - Notificación de actualizaciones

### Funciones de Validación

- **validate_critical_variables()**: Validación de variables críticas
  - Target válido
  - Configuración correcta
  - Variables requeridas

- **validate_attack_config()**: Validación de configuración de ataque
  - Parámetros válidos
  - Límites razonables
  - Compatibilidad de opciones

- **validate_permissions()**: Validación de permisos
  - Permisos de sistema
  - Permisos de red
  - Permisos de archivos

- **validate_dependencies()**: Validación de dependencias
  - Módulos Python requeridos
  - Herramientas externas
  - Versiones compatibles

- **check_network_connectivity()**: Verificación de conectividad
  - Conectividad al target
  - Resolución DNS
  - Accesibilidad de red

- **check_ssl_certificate()**: Verificación de certificado SSL/TLS
  - Validez del certificado
  - Fecha de expiración
  - Cadena de certificados

### Funciones de Utilidad

- **format_number()**: Formateo de números grandes
  - Conversión a K, M, B
  - Formato legible

- **log_message()**: Sistema de logging mejorado
  - Logging a archivo
  - Logging a consola
  - Niveles de log (INFO, WARN, ERROR, CRITICAL, DEBUG)

- **print_color()**: Impresión con colores
  - Colores ANSI
  - Soporte para modo web panel
  - Formato mejorado

- **is_valid_ip()**: Validación de IP
  - Verificación de formato
  - Validación de rango

- **is_private_ip()**: Verificación de IP privada
  - Rangos privados
  - Rangos reservados

### Clases y Componentes

#### ConnectionManager

Gestor mejorado de conexiones HTTP con pooling y reutilización.

**Métodos:**
- `get_session(target_url, worker_id)`: Obtiene o crea una sesión HTTP optimizada
- `clear_sessions()`: Limpia todas las sesiones almacenadas

**Características:**
- Pool de 10 sesiones por worker
- Gestión thread-safe con locks
- Configuración optimizada automática
- Limpieza automática de recursos

#### PerformanceMonitor

Monitor mejorado de rendimiento del sistema con caching.

**Métodos:**
- `get_system_metrics()`: Obtiene métricas del sistema con caching

**Características:**
- Caché de 1 segundo
- Reducción de llamadas a psutil
- Métricas optimizadas (CPU, memoria, disco)

### Parámetros Configurables

Todos los parámetros pueden configurarse desde línea de comandos o panel web:

#### Parámetros Básicos
- `TARGET`: URL o IP del target
- `DURATION`: Duración de la prueba en segundos
- `POWER_LEVEL`: Nivel de potencia (TEST a GODMODE)
- `ATTACK_MODE`: Modo de ataque (MIXED, CONSTANT, BURST, RAMP_UP)
- `MAX_CONNECTIONS`: Máximo de conexiones simultáneas
- `MAX_THREADS`: Máximo de threads/workers

#### Parámetros de Evasión
- `WAF_BYPASS`: Activar bypass de WAF
- `STEALTH_MODE`: Activar modo stealth
- `EVASION_TECHNIQUES`: Diccionario de técnicas de evasión activas

#### Parámetros de Optimización
- `SOCKET_REUSE`: Reutilizar sockets
- `TCP_OPTIMIZATION`: Optimizaciones TCP
- `KEEP_ALIVE_POOLING`: Pool de conexiones keep-alive
- `CONNECTION_POOL_SIZE`: Tamaño del pool de conexiones
- `HTTP2_MULTIPLEXING`: Multiplexing HTTP/2
- `RATE_ADAPTIVE`: Ajuste dinámico de tasa
- `CONNECTION_WARMUP`: Pre-calentar conexiones

#### Parámetros de Monitoreo
- `MEMORY_MONITORING`: Monitoreo de memoria
- `AUTO_THROTTLE`: Throttling automático
- `MEMORY_THRESHOLD_WARN`: Umbral de advertencia (60%)
- `MEMORY_THRESHOLD_CRITICAL`: Umbral crítico (75%)
- `MEMORY_THRESHOLD_OOM`: Umbral OOM (85%)
- `MEMORY_THRESHOLD_EMERGENCY`: Umbral emergencia (90%)

#### Parámetros de Payload
- `PAYLOAD_SIZE_KB`: Tamaño de payload en KB
- `USE_LARGE_PAYLOADS`: Usar payloads grandes
- `MAX_PAYLOAD_SIZE_MB`: Máximo tamaño de payload en MB

### Archivos y Directorios

El sistema crea y gestiona los siguientes directorios:

- `loadtest_output/`: Directorio principal de salida
  - `logs/`: Archivos de log
    - `loadtest_YYYYMMDD.log`: Log general
    - `loadtest_debug_YYYYMMDD.log`: Log de debug
  - `reports/`: Reportes HTML generados
    - `report_YYYYMMDD_HHMMSS.html`: Reportes de pruebas
  - `config/`: Archivos de configuración
    - `last_update_check.txt`: Timestamp de última verificación de actualizaciones

### Flujo de Ejecución

1. **Inicialización**
   - Validación de argumentos
   - Verificación de dependencias
   - Creación de directorios
   - Verificación de recursos

2. **Fingerprinting**
   - Análisis del target
   - Detección de WAF/CDN
   - Escaneo de vulnerabilidades
   - Análisis de security headers

3. **Auto-Configuración**
   - Aplicación de técnicas de evasión específicas
   - Ajuste de parámetros según fingerprint
   - Configuración de modo de ataque

4. **Despliegue Gradual**
   - Verificación de recursos
   - Despliegue de herramientas prioritarias
   - Throttling progresivo
   - Despliegue de herramientas secundarias

5. **Monitoreo**
   - Monitoreo en tiempo real
   - Gestión de recursos
   - Ajuste dinámico de tasa
   - Health checks

6. **Finalización**
   - Limpieza de recursos
   - Generación de reportes
   - Cierre de conexiones
   - Terminación de procesos

---

## 🔒 Seguridad y Protección

LoadTest Enterprise incluye un sistema de protección empresarial integrado para prevenir uso no autorizado, robo o modificación de la herramienta.

### Características de Seguridad

- **Kill-Switch Remoto**: Control centralizado para desactivar la herramienta remotamente
- **Verificación de Integridad**: Detecta modificaciones no autorizadas del código
- **Tracking Automático**: Registra ubicación y uso de la herramienta
- **Protección Multi-Capa**: Código de protección distribuido en múltiples ubicaciones
- **Auto-Destrucción**: Se desactiva automáticamente si se detecta uso no autorizado

### Documentación de Seguridad

Para información detallada sobre el sistema de seguridad, consulta `SECURITY.md` (documento confidencial).

**Nota**: El sistema de seguridad está integrado y no puede ser desactivado o eliminado sin afectar la funcionalidad de la herramienta.

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
- El monitoreo de memoria está activado por defecto y reducirá automáticamente la carga

#### Problema: "Web panel not starting"

**Solución:**
```bash
# Verificar si el puerto está disponible
# Probar puerto diferente
python loadtest.py --web --web-port 8080

# Verificar si loadtest_web.py existe
ls loadtest_web.py
```

#### Problema: "System freeze durante despliegue"

**Solución:**
- El sistema ahora usa despliegue gradual automático
- Si persiste, reducir número de herramientas: `MAX_TOOLS_DEPLOY` se ajusta automáticamente
- Verificar recursos del sistema antes de iniciar

#### Problema: "WAF bloqueando requests"

**Solución:**
- Activar bypass automático: `--bypass-waf`
- Activar stealth mode: `--stealth`
- El sistema detecta WAF automáticamente y activa evasión

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

## 💡 Mejores Prácticas

### Configuración Recomendada

#### Para Pruebas Básicas
```bash
python loadtest.py -t https://example.com -d 60 -p MODERATE
```

#### Para Pruebas con WAF
```bash
# El sistema detectará y configurará automáticamente
python loadtest.py -t https://example.com -d 60 -p MODERATE --bypass-waf
```

#### Para Pruebas Intensivas
```bash
python loadtest.py -t https://example.com -d 300 -p HEAVY -c 20000 --threads 500
```

#### Para Pruebas de Seguridad
```bash
python loadtest.py -t https://example.com -d 120 -p MEDIUM --stealth --bypass-waf
```

### Optimización de Recursos

- **Monitoreo de Memoria**: Siempre activado por defecto
- **Throttling Automático**: Se ajusta según recursos disponibles
- **Despliegue Gradual**: Evita freezes del sistema
- **Límites Dinámicos**: Se ajustan según memoria disponible

### Uso del Panel Web

1. **Iniciar Panel**: `python loadtest.py --web`
2. **Usar Flujo Guiado**: Proceso paso a paso recomendado
3. **Ejecutar Fingerprint**: Análisis automático del target
4. **Aplicar Recomendaciones**: Configuración optimizada automática
5. **Monitorear en Tiempo Real**: Ver estadísticas durante la prueba

### Gestión de Herramientas

- **Verificar Estado**: `python loadtest.py --show-tools`
- **Instalar Automáticamente**: `python loadtest.py --install-tools`
- **El sistema detecta automáticamente**: OS y gestor de paquetes

### Actualizaciones

- **Verificación Automática**: Una vez al día
- **Verificación Manual**: `python loadtest.py --check-update`
- **Actualización**: `python loadtest.py --update`
- **Backups Automáticos**: Se crean antes de actualizar

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
