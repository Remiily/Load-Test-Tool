#!/usr/bin/env python3
"""
LoadTest Enterprise - Web Panel
Panel de control web para configuración y monitoreo
"""

from flask import Flask, render_template, request, jsonify, send_from_directory, Response
try:
    from flask_cors import CORS  # type: ignore
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False
    # CORS no disponible, pero no es crítico
    CORS = None
import json
import threading
import time
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import subprocess
import sys
import os

# Importar funciones del módulo principal
sys.path.insert(0, str(Path(__file__).parent))
# Establecer modo web panel ANTES de importar para evitar validaciones
import os
os.environ['LOADTEST_WEB_PANEL'] = '1'
import loadtest
# Forzar modo web panel
loadtest.WEB_PANEL_MODE = True
loadtest._NETWORK_CHECK_ENABLED = False
from loadtest import (
    TARGET, DURATION, POWER_LEVEL, ATTACK_MODE, MAX_CONNECTIONS, MAX_THREADS,
    USE_LARGE_PAYLOADS, WAF_BYPASS, STEALTH_MODE, AUTO_THROTTLE, MEMORY_MONITORING,
    MEMORY_THRESHOLD_WARN, MEMORY_THRESHOLD_CRITICAL, MEMORY_THRESHOLD_OOM,
    PAYLOAD_SIZE_KB, POWER_LEVELS, TOOLS, attack_stats, monitoring_active,
    OUTPUT_DIR, REPORTS_DIR, LOGS_DIR, VERSION, validate_critical_variables,
    fingerprint_target, generate_report, show_tool_status, detect_all_tools,
    generate_stress_recommendations, recommend_tools_from_fingerprint,
    run_autodiagnostic, DOMAIN, IP_ADDRESS, TARGET_TYPE, NETWORK_TYPE
)

# Acceso a variables globales del módulo loadtest
def get_loadtest_var(var_name):
    return getattr(loadtest, var_name, None)

# Configurar rutas de templates y static
script_dir = Path(__file__).parent.absolute().resolve()
templates_dir = script_dir / "templates"
static_dir = script_dir / "static"

# Crear directorios si no existen
templates_dir.mkdir(exist_ok=True)
static_dir.mkdir(exist_ok=True)

app = Flask(__name__, 
            template_folder=str(templates_dir),
            static_folder=str(static_dir))
CORS(app)

# Estado global del servidor
current_attack_process = None
attack_config = {}
attack_history = []

# Variables globales de proxies (inicializadas desde loadtest o configuración)
PROXY_LIST = get_loadtest_var('PROXY_LIST') or []
PROXY_ROTATION = get_loadtest_var('PROXY_ROTATION') or "round-robin"

@app.route('/')
def index():
    """Página principal del panel"""
    return render_template('index.html', version=VERSION)

@app.route('/api/config', methods=['GET'])
def get_config():
    """Obtiene la configuración actual"""
    return jsonify({
        "target": TARGET,
        "duration": DURATION,
        "power_level": POWER_LEVEL,
        "attack_mode": ATTACK_MODE,
        "max_connections": MAX_CONNECTIONS,
        "max_threads": MAX_THREADS,
        "use_large_payloads": USE_LARGE_PAYLOADS,
        "waf_bypass": WAF_BYPASS,
        "stealth_mode": STEALTH_MODE,
        "auto_throttle": AUTO_THROTTLE,
        "memory_monitoring": MEMORY_MONITORING,
        "memory_threshold_warn": MEMORY_THRESHOLD_WARN,
        "memory_threshold_critical": MEMORY_THRESHOLD_CRITICAL,
        "memory_threshold_oom": MEMORY_THRESHOLD_OOM,
        "payload_size_kb": PAYLOAD_SIZE_KB,
        "power_levels": POWER_LEVELS,
        "attack_modes": ["MIXED", "CONSTANT", "BURST", "RAMP_UP"],
        "socket_attack": get_loadtest_var('SOCKET_REUSE') or True,
        "tcp_optimization": get_loadtest_var('TCP_OPTIMIZATION') or True,
        "keep_alive_pooling": get_loadtest_var('KEEP_ALIVE_POOLING') or True,
        "connection_warmup": get_loadtest_var('CONNECTION_WARMUP') or True,
        "rate_adaptive": get_loadtest_var('RATE_ADAPTIVE') or True,
        "connection_pool_size": get_loadtest_var('CONNECTION_POOL_SIZE') or 1000,
        "max_payload_mb": get_loadtest_var('MAX_PAYLOAD_SIZE_MB') or 10,
        # Configuración avanzada de timeouts
        "connect_timeout": get_loadtest_var('CONNECT_TIMEOUT') or 3.0,
        "read_timeout": get_loadtest_var('READ_TIMEOUT') or 6.0,
        "max_retries": get_loadtest_var('MAX_RETRIES') or 0,
        "retry_backoff_factor": get_loadtest_var('RETRY_BACKOFF_FACTOR') or 0.3,
        # Configuración de rotación
        "user_agent_rotation_interval": get_loadtest_var('USER_AGENT_ROTATION_INTERVAL') or 100,
        "ip_rotation_interval": get_loadtest_var('IP_ROTATION_INTERVAL') or 50,
        "header_rotation_interval": get_loadtest_var('HEADER_ROTATION_INTERVAL') or 200,
        # Configuración de rate limiting
        "rate_limit_base": get_loadtest_var('RATE_LIMIT_BASE') or 100,
        "rate_limit_max": get_loadtest_var('RATE_LIMIT_MAX') or 10000,
        "rate_limit_min": get_loadtest_var('RATE_LIMIT_MIN') or 10,
        "rate_adaptive_factor": get_loadtest_var('RATE_ADAPTIVE_FACTOR') or 1.1,
        # Configuración de backoff
        "backoff_strategy": get_loadtest_var('BACKOFF_STRATEGY') or "exponential",
        "backoff_max_delay": get_loadtest_var('BACKOFF_MAX_DELAY') or 5.0,
        "backoff_min_delay": get_loadtest_var('BACKOFF_MIN_DELAY') or 0.1,
        # Técnicas de evasión individuales
        "evasion_techniques": get_loadtest_var('EVASION_TECHNIQUES') or {},
        # Configuración de proxies
        "proxy_list": get_loadtest_var('PROXY_LIST') or [],
        "proxy_rotation": get_loadtest_var('PROXY_ROTATION') or "round-robin",
        # Configuración HTTP/2 y HTTP/3
        "http2_multiplexing": get_loadtest_var('HTTP2_MULTIPLEXING') or True,
        "http3_quic": get_loadtest_var('HTTP3_QUIC') or False,
        # Análisis avanzado
        "pattern_analysis_enabled": get_loadtest_var('PATTERN_ANALYSIS_ENABLED') or True,
        "auto_tuning_enabled": get_loadtest_var('AUTO_TUNING_ENABLED') or True,
        "security_analysis_enabled": get_loadtest_var('SECURITY_ANALYSIS_ENABLED') or True
    })
    
    # Obtener datos de análisis avanzado desde attack_stats
    attack_stats_actual = get_loadtest_var('attack_stats') or {}
    config["pattern_analysis"] = attack_stats_actual.get("pattern_analysis", {})
    config["auto_tuning"] = attack_stats_actual.get("auto_tuning", {})
    config["security_analysis"] = attack_stats_actual.get("security_analysis", {})

@app.route('/api/config', methods=['POST'])
def set_config():
    """Actualiza la configuración"""
    global TARGET, DURATION, POWER_LEVEL, ATTACK_MODE, MAX_CONNECTIONS, MAX_THREADS
    global USE_LARGE_PAYLOADS, WAF_BYPASS, STEALTH_MODE, AUTO_THROTTLE, MEMORY_MONITORING
    global MEMORY_THRESHOLD_WARN, MEMORY_THRESHOLD_CRITICAL, MEMORY_THRESHOLD_OOM, PAYLOAD_SIZE_KB
    global SOCKET_REUSE, TCP_OPTIMIZATION, KEEP_ALIVE_POOLING, CONNECTION_WARMUP, RATE_ADAPTIVE
    global CONNECTION_POOL_SIZE, MAX_PAYLOAD_SIZE_MB
    global CONNECT_TIMEOUT, READ_TIMEOUT, MAX_RETRIES, RETRY_BACKOFF_FACTOR
    global USER_AGENT_ROTATION_INTERVAL, IP_ROTATION_INTERVAL, HEADER_ROTATION_INTERVAL
    global RATE_LIMIT_BASE, RATE_LIMIT_MAX, RATE_LIMIT_MIN, RATE_ADAPTIVE_FACTOR
    global BACKOFF_STRATEGY, BACKOFF_MAX_DELAY, BACKOFF_MIN_DELAY, EVASION_TECHNIQUES
    global PROXY_LIST, PROXY_ROTATION, HTTP2_MULTIPLEXING, HTTP3_QUIC
    
    data = request.json
    
    # Actualizar variables globales en el módulo loadtest
    if "target" in data:
        TARGET = data["target"]
        loadtest.TARGET = data["target"]
    if "duration" in data:
        DURATION = int(data["duration"])
        loadtest.DURATION = int(data["duration"])
    if "power_level" in data:
        POWER_LEVEL = data["power_level"]
        loadtest.POWER_LEVEL = data["power_level"]
        loadtest.MULTIPLIER = POWER_LEVELS.get(data["power_level"], 8)
    if "attack_mode" in data:
        ATTACK_MODE = data["attack_mode"]
        loadtest.ATTACK_MODE = data["attack_mode"]
    if "max_connections" in data:
        MAX_CONNECTIONS = int(data["max_connections"])
        loadtest.MAX_CONNECTIONS = int(data["max_connections"])
    if "max_threads" in data:
        MAX_THREADS = int(data["max_threads"])
        loadtest.MAX_THREADS = int(data["max_threads"])
    if "use_large_payloads" in data:
        USE_LARGE_PAYLOADS = bool(data["use_large_payloads"])
        loadtest.USE_LARGE_PAYLOADS = bool(data["use_large_payloads"])
    if "waf_bypass" in data:
        WAF_BYPASS = bool(data["waf_bypass"])
        loadtest.WAF_BYPASS = bool(data["waf_bypass"])
    if "stealth_mode" in data:
        STEALTH_MODE = bool(data["stealth_mode"])
        loadtest.STEALTH_MODE = bool(data["stealth_mode"])
    if "auto_throttle" in data:
        AUTO_THROTTLE = bool(data["auto_throttle"])
        loadtest.AUTO_THROTTLE = bool(data["auto_throttle"])
    if "memory_monitoring" in data:
        MEMORY_MONITORING = bool(data["memory_monitoring"])
        loadtest.MEMORY_MONITORING = bool(data["memory_monitoring"])
    if "memory_threshold_warn" in data:
        MEMORY_THRESHOLD_WARN = int(data["memory_threshold_warn"])
        loadtest.MEMORY_THRESHOLD_WARN = int(data["memory_threshold_warn"])
    if "memory_threshold_critical" in data:
        MEMORY_THRESHOLD_CRITICAL = int(data["memory_threshold_critical"])
        loadtest.MEMORY_THRESHOLD_CRITICAL = int(data["memory_threshold_critical"])
    if "memory_threshold_oom" in data:
        MEMORY_THRESHOLD_OOM = int(data["memory_threshold_oom"])
        loadtest.MEMORY_THRESHOLD_OOM = int(data["memory_threshold_oom"])
    if "payload_size_kb" in data:
        PAYLOAD_SIZE_KB = int(data["payload_size_kb"])
        loadtest.PAYLOAD_SIZE_KB = int(data["payload_size_kb"])
    if "socket_attack" in data:
        SOCKET_REUSE = bool(data["socket_attack"])
        loadtest.SOCKET_REUSE = bool(data["socket_attack"])
    if "tcp_optimization" in data:
        TCP_OPTIMIZATION = bool(data["tcp_optimization"])
        loadtest.TCP_OPTIMIZATION = bool(data["tcp_optimization"])
    if "keep_alive_pooling" in data:
        KEEP_ALIVE_POOLING = bool(data["keep_alive_pooling"])
        loadtest.KEEP_ALIVE_POOLING = bool(data["keep_alive_pooling"])
    if "connection_warmup" in data:
        CONNECTION_WARMUP = bool(data["connection_warmup"])
        loadtest.CONNECTION_WARMUP = bool(data["connection_warmup"])
    if "rate_adaptive" in data:
        RATE_ADAPTIVE = bool(data["rate_adaptive"])
        loadtest.RATE_ADAPTIVE = bool(data["rate_adaptive"])
    if "connection_pool_size" in data:
        CONNECTION_POOL_SIZE = int(data["connection_pool_size"])
        loadtest.CONNECTION_POOL_SIZE = int(data["connection_pool_size"])
    if "max_payload_mb" in data:
        MAX_PAYLOAD_SIZE_MB = int(data["max_payload_mb"])
        loadtest.MAX_PAYLOAD_SIZE_MB = int(data["max_payload_mb"])
    
    # Configuración de timeouts
    if "connect_timeout" in data:
        loadtest.CONNECT_TIMEOUT = float(data["connect_timeout"])
    if "read_timeout" in data:
        loadtest.READ_TIMEOUT = float(data["read_timeout"])
    if "max_retries" in data:
        loadtest.MAX_RETRIES = int(data["max_retries"])
    if "retry_backoff_factor" in data:
        loadtest.RETRY_BACKOFF_FACTOR = float(data["retry_backoff_factor"])
    
    # Técnicas de evasión
    if "evasion_techniques" in data:
        evasion_techs = data["evasion_techniques"]
        if isinstance(evasion_techs, dict):
            for tech, enabled in evasion_techs.items():
                if hasattr(loadtest, 'EVASION_TECHNIQUES'):
                    loadtest.EVASION_TECHNIQUES[tech] = bool(enabled)
    
    # Configuración de proxies
    if "proxy_list" in data:
        proxy_data = data["proxy_list"]
        if isinstance(proxy_data, str):
            # Si es string (lista de proxies separados por \n), cargar usando load_proxy_list
            loadtest.load_proxy_list(proxy_string=proxy_data)
        elif isinstance(proxy_data, list):
            # Si es lista, asignar directamente
            PROXY_LIST = proxy_data
            loadtest.PROXY_LIST = proxy_data
        else:
            PROXY_LIST = []
            loadtest.PROXY_LIST = []
    if "proxy_rotation" in data:
        PROXY_ROTATION = data["proxy_rotation"]
        loadtest.PROXY_ROTATION = data["proxy_rotation"]
    
    # Análisis avanzado
    if "pattern_analysis_enabled" in data:
        loadtest.PATTERN_ANALYSIS_ENABLED = bool(data["pattern_analysis_enabled"])
    if "auto_tuning_enabled" in data:
        loadtest.AUTO_TUNING_ENABLED = bool(data["auto_tuning_enabled"])
    if "security_analysis_enabled" in data:
        loadtest.SECURITY_ANALYSIS_ENABLED = bool(data["security_analysis_enabled"])
    
    attack_config.update(data)
    
    return jsonify({"status": "success", "message": "Configuración actualizada"})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Obtiene estadísticas avanzadas en tiempo real"""
    # Obtener attack_stats directamente del módulo loadtest para asegurar sincronización
    attack_stats_actual = get_loadtest_var('attack_stats') or attack_stats
    
    vulns = get_loadtest_var('VULNERABILITIES') or []
    ports = get_loadtest_var('OPEN_PORTS') or []
    endpoints = get_loadtest_var('DISCOVERED_ENDPOINTS') or []
    
    requests_sent = attack_stats_actual.get("requests_sent", 0)
    responses_received = attack_stats_actual.get("responses_received", 0)
    errors_count = len(attack_stats_actual.get("errors", []))
    latencies = attack_stats_actual.get("latencies", [])[-100:]  # Últimas 100
    
    # Calcular métricas avanzadas
    elapsed_time = 0
    start_time = attack_stats_actual.get("start_time")
    if start_time:
        # Manejar tanto datetime como string ISO
        if isinstance(start_time, str):
            from dateutil import parser as date_parser
            try:
                start_time = date_parser.parse(start_time)
            except:
                start_time = None
        if start_time:
            elapsed_time = (datetime.now() - start_time).total_seconds()
    
    # Calcular RPS - usar avg_rps del módulo si está disponible y es más reciente
    avg_rps = requests_sent / elapsed_time if elapsed_time > 0.1 else 0  # Evitar división por tiempo muy pequeño
    peak_rps = attack_stats_actual.get("peak_rps", 0)
    current_avg_rps = attack_stats_actual.get("avg_rps", 0)
    
    # Si avg_rps del módulo está disponible y es mayor que 0, usarlo (más preciso)
    if current_avg_rps > 0:
        avg_rps = current_avg_rps
    elif elapsed_time > 0.1:
        # Calcular RPS basado en requests y tiempo transcurrido
        avg_rps = requests_sent / elapsed_time
    
    # Calcular tasas
    response_rate = (responses_received / requests_sent * 100) if requests_sent > 0 else 0
    error_rate = (errors_count / requests_sent * 100) if requests_sent > 0 else 0
    
    # Análisis de códigos HTTP (convertir defaultdict a dict normal para JSON)
    http_codes_raw = attack_stats_actual.get("http_codes", {})
    if hasattr(http_codes_raw, 'keys'):
        http_codes = {int(k): int(v) for k, v in http_codes_raw.items() if v > 0}
    else:
        http_codes = dict(http_codes_raw) if http_codes_raw else {}
    success_responses = sum(count for code, count in http_codes.items() if 200 <= code < 300)
    success_rate = (success_responses / requests_sent * 100) if requests_sent > 0 else 0
    
    # Análisis de latencias
    latency_stats = {}
    if latencies:
        sorted_latencies = sorted(latencies)
        latency_stats = {
            "avg": sum(latencies) / len(latencies),
            "min": min(latencies),
            "max": max(latencies),
            "p50": sorted_latencies[int(len(sorted_latencies) * 0.50)],
            "p75": sorted_latencies[int(len(sorted_latencies) * 0.75)],
            "p90": sorted_latencies[int(len(sorted_latencies) * 0.90)],
            "p95": sorted_latencies[int(len(sorted_latencies) * 0.95)],
            "p99": sorted_latencies[int(len(sorted_latencies) * 0.99)]
        }
    
    # Información de memoria si está disponible
    memory_info = {}
    try:
        import psutil
        memory = psutil.virtual_memory()
        memory_info = {
            "percent": memory.percent,
            "used_gb": round(memory.used / (1024**3), 2),
            "total_gb": round(memory.total / (1024**3), 2)
        }
    except:
        pass
    
    # Obtener duración configurada
    duration = get_loadtest_var('DURATION') or 60
    
    # Debug logging (solo en modo debug)
    debug_mode = getattr(loadtest, 'DEBUG_MODE', False)
    if debug_mode and requests_sent > 0:
        print(f"DEBUG [get_stats]: requests_sent={requests_sent}, rps_current={avg_rps:.2f}, errors={errors_count}, monitoring_active={get_loadtest_var('monitoring_active')}")
    
    response_data = {
        "requests_sent": int(requests_sent),
        "responses_received": int(responses_received),
        "http_codes": http_codes,
        "latencies": [float(l) for l in latencies] if latencies else [],
        "latency_stats": latency_stats,
        "errors": int(errors_count),
        "error_rate": round(error_rate, 2),
        "monitoring_active": get_loadtest_var('monitoring_active') if get_loadtest_var('monitoring_active') is not None else (monitoring_active if 'monitoring_active' in globals() else False),
        "start_time": start_time.isoformat() if start_time and hasattr(start_time, 'isoformat') else (start_time if isinstance(start_time, str) else None),
        "elapsed_time": round(elapsed_time, 2),
        "duration": int(duration),
        "remaining_time": max(0, int(duration - elapsed_time)) if duration > 0 else 0,
        "vulnerabilities_count": len(vulns),
        "open_ports_count": len(ports),
        "discovered_endpoints_count": len(endpoints),
        "rps": {
            "current": round(avg_rps, 2),
            "average": round(current_avg_rps, 2),
            "peak": round(peak_rps, 2)
        },
        "rates": {
            "response_rate": round(response_rate, 2),
            "success_rate": round(success_rate, 2),
            "error_rate": round(error_rate, 2)
        },
        "memory": memory_info,
        "attack_techniques": attack_stats_actual.get("attack_techniques", []),
        "bytes_sent": int(attack_stats_actual.get("bytes_sent", 0)),
        "bytes_received": int(attack_stats_actual.get("bytes_received", 0)),
        # Análisis de patrones
        "pattern_analysis": attack_stats_actual.get("pattern_analysis", {}),
        # Auto-tuning
        "auto_tuning": attack_stats_actual.get("auto_tuning", {}),
        # Análisis de seguridad
        "security_analysis": attack_stats_actual.get("security_analysis", {})
    }
    
    return jsonify(response_data)

@app.route('/api/tools', methods=['GET'])
def get_tools():
    """Obtiene estado de herramientas"""
    tools_status = detect_all_tools()
    return jsonify({
        "tools": tools_status,
        "categories": TOOLS
    })

@app.route('/api/reports', methods=['GET'])
def get_reports():
    """Lista reportes disponibles"""
    reports = []
    if REPORTS_DIR.exists():
        for file in REPORTS_DIR.glob("report_*.html"):
            reports.append({
                "name": file.name,
                "path": str(file.relative_to(REPORTS_DIR)),
                "size": file.stat().st_size,
                "modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
            })
    return jsonify({"reports": sorted(reports, key=lambda x: x["modified"], reverse=True)})

@app.route('/api/history', methods=['GET'])
def get_history():
    """Obtiene el historial de ataques"""
    try:
        limit = int(request.args.get('limit', 100))
        from loadtest import get_history as loadtest_get_history
        history = loadtest_get_history(limit=limit)
        
        # Formatear historial para el frontend
        formatted_history = []
        for entry in history:
            # El historial ahora viene con estructura simplificada
            # Si tiene full_report, usar esos datos, sino usar los datos directos
            if "full_report" in entry:
                report = entry.get("full_report", {})
                metadata = report.get('metadata', {})
                stats = report.get('statistics', {})
                performance = report.get('performance', {})
                
                formatted_history.append({
                    "id": entry.get("id", metadata.get('timestamp', '')),
                    "timestamp": entry.get("timestamp", metadata.get('timestamp', '')),
                    "target": entry.get("target", metadata.get('target', '')),
                    "domain": entry.get("domain", metadata.get('domain', '')),
                    "duration": entry.get("duration", metadata.get('duration', 0)),
                    "elapsed_time": metadata.get('elapsed_time', entry.get("duration", 0)),
                    "power_level": entry.get("power_level", metadata.get('power_level', '')),
                    "attack_mode": entry.get("attack_mode", metadata.get('attack_mode', '')),
                    "requests_sent": entry.get("requests_sent", stats.get('requests_sent', 0)),
                    "responses_received": entry.get("responses_received", stats.get('responses_received', 0)),
                    "errors": entry.get("errors", stats.get('errors', 0)),
                    "avg_rps": round(entry.get("avg_rps", stats.get('avg_rps', 0)), 2),
                    "peak_rps": round(entry.get("peak_rps", stats.get('peak_rps', 0)), 2),
                    "success_rate": round(entry.get("success_rate", stats.get('success_rate', 0)), 2),
                    "error_rate": round(stats.get('error_rate', 0), 2),
                    "avg_latency_ms": round(entry.get("avg_latency_ms", performance.get('avg_latency_ms', 0)), 2),
                    "p95_latency_ms": round(entry.get("p95_latency_ms", performance.get('p95_latency_ms', 0)), 2),
                    "p99_latency_ms": round(performance.get('p99_latency_ms', 0), 2),
                    "http_codes": stats.get('http_codes', {}),
                    "files": report.get('files', {}),
                    "has_full_report": True
                })
            else:
                # Formato simplificado del historial
                formatted_history.append({
                    "id": entry.get("id", ''),
                    "timestamp": entry.get("timestamp", ''),
                    "target": entry.get("target", ''),
                    "domain": entry.get("domain", ''),
                    "duration": entry.get("duration", 0),
                    "elapsed_time": entry.get("duration", 0),
                    "power_level": entry.get("power_level", ''),
                    "attack_mode": entry.get("attack_mode", ''),
                    "requests_sent": entry.get("requests_sent", 0),
                    "responses_received": entry.get("responses_received", 0),
                    "errors": entry.get("errors", 0),
                    "avg_rps": round(entry.get("avg_rps", 0), 2),
                    "peak_rps": round(entry.get("peak_rps", 0), 2),
                    "success_rate": round(entry.get("success_rate", 0), 2),
                    "error_rate": 0,
                    "avg_latency_ms": round(entry.get("avg_latency_ms", 0), 2),
                    "p95_latency_ms": round(entry.get("p95_latency_ms", 0), 2),
                    "p99_latency_ms": 0,
                    "http_codes": {},
                    "files": {},
                    "has_full_report": False
                })
        
        return jsonify({
            "status": "success",
            "history": formatted_history,
            "total": len(formatted_history)
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/history/<report_id>', methods=['GET'])
def get_history_report(report_id):
    """Obtiene un reporte específico del historial"""
    try:
        from loadtest import HISTORY_DIR, get_history
        import json
        
        # Obtener historial
        history = get_history(limit=1000)
        
        # Buscar reporte por ID
        report_entry = None
        for entry in history:
            if entry.get('id') == report_id or entry.get('timestamp', '').startswith(report_id):
                report_entry = entry
                break
        
        if not report_entry:
            return jsonify({"status": "error", "message": "Reporte no encontrado"}), 404
        
        # Si tiene full_report, devolverlo
        if 'full_report' in report_entry:
            full_report = report_entry['full_report']
            # Generar HTML del reporte
            from loadtest import generate_html_report
            html_content = generate_html_report(full_report)
            
            return Response(html_content, mimetype='text/html')
        else:
            # Generar reporte básico
            return jsonify({
                "status": "success",
                "report": report_entry
            })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/history/<report_id>/pdf', methods=['GET'])
def get_history_report_pdf(report_id):
    """Exporta un reporte del historial a PDF"""
    try:
        from loadtest import get_history, export_report_to_pdf
        import json
        
        # Obtener historial
        history = get_history(limit=1000)
        
        # Buscar reporte por ID
        report_entry = None
        for entry in history:
            if entry.get('id') == report_id or entry.get('timestamp', '').startswith(report_id):
                report_entry = entry
                break
        
        if not report_entry:
            return jsonify({"status": "error", "message": "Reporte no encontrado"}), 404
        
        # Si tiene full_report, generar PDF
        if 'full_report' in report_entry:
            full_report = report_entry['full_report']
            pdf_data = export_report_to_pdf(full_report)
            
            return Response(
                pdf_data,
                mimetype='application/pdf',
                headers={
                    'Content-Disposition': f'attachment; filename=report_{report_id}.pdf'
                }
            )
        else:
            return jsonify({
                "status": "error",
                "message": "Reporte completo no disponible"
            }), 404
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
        
        history_file = HISTORY_DIR / f"history_{report_id}.json"
        if not history_file.exists():
            return jsonify({
                "status": "error",
                "message": "Reporte no encontrado"
            }), 404
        
        with open(history_file, 'r', encoding='utf-8') as f:
            entry = json.load(f)
        
        # Retornar el reporte completo si existe
        report = entry.get("full_report", entry)
        
        return jsonify({
            "status": "success",
            "report": report
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/reports/<path:filename>/pdf', methods=['GET'])
def export_report_to_pdf(filename):
    """Exporta un reporte a PDF"""
    try:
        # Importar reportlab (opcional - se maneja con try/except)
        from reportlab.lib.pagesizes import letter, A4  # type: ignore
        from reportlab.lib import colors  # type: ignore
        from reportlab.lib.units import inch  # type: ignore
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak  # type: ignore
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # type: ignore
        from reportlab.lib.enums import TA_CENTER, TA_LEFT  # type: ignore
        from io import BytesIO
        import json
        
        # Buscar el reporte JSON correspondiente
        report_json_path = None
        if REPORTS_DIR.exists():
            # Intentar encontrar el JSON correspondiente al HTML
            base_name = filename.replace('.html', '')
            json_file = REPORTS_DIR / f"{base_name}.json"
            if json_file.exists():
                report_json_path = json_file
        
        if not report_json_path:
            return jsonify({
                "status": "error",
                "message": "Reporte JSON no encontrado"
            }), 404
        
        # Cargar reporte
        with open(report_json_path, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        # Crear PDF en memoria
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#00ff88'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#00d9ff'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Contenido del PDF
        story = []
        
        # Título
        story.append(Paragraph("LoadTest Enterprise", title_style))
        story.append(Paragraph("Security Operations Center - Attack Report", styles['Title']))
        story.append(Spacer(1, 0.3*inch))
        
        # Metadata
        metadata = report.get('metadata', {})
        metadata_data = [
            ['Target', metadata.get('target', 'N/A')],
            ['Domain', metadata.get('domain', 'N/A')],
            ['IP Address', metadata.get('ip_address', 'N/A')],
            ['Timestamp', metadata.get('timestamp', 'N/A')],
            ['Duration', f"{metadata.get('duration', 0)}s"],
            ['Power Level', metadata.get('power_level', 'N/A')],
            ['Attack Mode', metadata.get('attack_mode', 'N/A')],
        ]
        
        metadata_table = Table(metadata_data, colWidths=[2*inch, 4*inch])
        metadata_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#1a1a2e')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#2a2a3e'))
        ]))
        story.append(metadata_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Estadísticas
        story.append(Paragraph("Statistics", heading_style))
        stats = report.get('statistics', {})
        stats_data = [
            ['Metric', 'Value'],
            ['Requests Sent', format(stats.get('requests_sent', 0), ',')],
            ['Responses Received', format(stats.get('responses_received', 0), ',')],
            ['Average RPS', f"{stats.get('avg_rps', 0):.2f}"],
            ['Peak RPS', f"{stats.get('peak_rps', 0):.2f}"],
            ['Success Rate', f"{stats.get('success_rate', 0):.2f}%"],
            ['Error Rate', f"{stats.get('error_rate', 0):.2f}%"],
            ['Response Rate', f"{stats.get('response_rate', 0):.2f}%"],
            ['Throughput', f"{stats.get('throughput_mbps', 0):.2f} Mbps"],
            ['Bytes Sent', format(stats.get('bytes_sent', 0), ',')],
            ['Bytes Received', format(stats.get('bytes_received', 0), ',')],
        ]
        
        stats_table = Table(stats_data, colWidths=[3*inch, 3*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#00ff88')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#2a2a3e'))
        ]))
        story.append(stats_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Performance Metrics - Mejorado con más información
        story.append(Paragraph("Performance Metrics", heading_style))
        performance = report.get('performance', {})
        perf_data = [
            ['Metric', 'Value'],
            ['Average Latency', f"{performance.get('avg_latency_ms', 0):.2f} ms"],
            ['Min Latency', f"{performance.get('min_latency_ms', 0):.2f} ms"],
            ['Max Latency', f"{performance.get('max_latency_ms', 0):.2f} ms"],
            ['P50 Latency', f"{performance.get('p50_latency_ms', 0):.2f} ms"],
            ['P75 Latency', f"{performance.get('p75_latency_ms', 0):.2f} ms"],
            ['P90 Latency', f"{performance.get('p90_latency_ms', 0):.2f} ms"],
            ['P95 Latency', f"{performance.get('p95_latency_ms', 0):.2f} ms"],
            ['P99 Latency', f"{performance.get('p99_latency_ms', 0):.2f} ms"],
            ['Std Deviation', f"{performance.get('std_dev_ms', 0):.2f} ms"],
        ]
        
        # Agregar información de tiempos de respuesta si está disponible
        response_times = performance.get('response_times', {})
        if response_times:
            story.append(Spacer(1, 0.2*inch))
            response_data = [
                ['Response Time Metric', 'Value'],
                ['First Response', f"{response_times.get('first_response_ms', 0):.2f} ms"],
                ['Last Response', f"{response_times.get('last_response_ms', 0):.2f} ms"],
            ]
            response_table = Table(response_data, colWidths=[3*inch, 3*inch])
            response_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#00d9ff')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#2a2a3e'))
            ]))
            story.append(response_table)
        
        perf_table = Table(perf_data, colWidths=[3*inch, 3*inch])
        perf_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#00d9ff')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#2a2a3e'))
        ]))
        story.append(perf_table)
        
        # Construir PDF
        doc.build(story)
        
        # Preparar respuesta
        buffer.seek(0)
        pdf_filename = filename.replace('.html', '.pdf')
        
        return Response(
            buffer.getvalue(),
            mimetype='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename={pdf_filename}'
            }
        )
    except ImportError:
        return jsonify({
            "status": "error",
            "message": "reportlab no está instalado. Instala con: pip install reportlab"
        }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/reports/<path:filename>')
def serve_report(filename):
    """Sirve un reporte"""
    return send_from_directory(str(REPORTS_DIR), filename)

@app.route('/api/start', methods=['POST'])
def start_attack():
    """Inicia un ataque"""
    global current_attack_process
    
    if current_attack_process and current_attack_process.is_alive():
        return jsonify({"status": "error", "message": "Ya hay un ataque en ejecución"}), 400
    
    # Validar target
    if not TARGET:
        return jsonify({"status": "error", "message": "Target no especificado"}), 400
    
    if not validate_critical_variables():
        return jsonify({"status": "error", "message": "Target inválido"}), 400
    
    # Iniciar ataque en thread separado
    def run_attack():
        try:
            # Importar y ejecutar main del módulo loadtest
            import loadtest
            
            # Sincronizar estado antes de iniciar
            loadtest.WEB_PANEL_MODE = True
            loadtest.DEBUG_MODE = True  # Activar debug para logging completo
            loadtest.monitoring_active = True  # Asegurar que monitoring_active esté activo
            
            # Sincronizar variables globales
            loadtest.TARGET = TARGET
            loadtest.DURATION = DURATION
            loadtest.POWER_LEVEL = POWER_LEVEL
            loadtest.ATTACK_MODE = ATTACK_MODE
            loadtest.MAX_CONNECTIONS = MAX_CONNECTIONS
            loadtest.MAX_THREADS = MAX_THREADS
            loadtest.WAF_BYPASS = WAF_BYPASS
            loadtest.USE_LARGE_PAYLOADS = USE_LARGE_PAYLOADS
            loadtest.STEALTH_MODE = STEALTH_MODE
            loadtest.AUTO_THROTTLE = AUTO_THROTTLE
            loadtest.MEMORY_MONITORING = MEMORY_MONITORING
            
            # Resetear estadísticas de ataque ANTES de iniciar
            # Asegurar que estamos usando el mismo objeto attack_stats
            attack_stats_ref = loadtest.attack_stats
            if not attack_stats_ref:
                # Si no existe, crear uno nuevo
                attack_stats_ref = {
                    "start_time": None,
                    "end_time": None,
                    "requests_sent": 0,
                    "responses_received": 0,
                    "http_codes": defaultdict(int),
                    "latencies": [],
                    "errors": [],
                    "peak_rps": 0,
                    "avg_rps": 0,
                    "last_request_count": 0,
                    "bytes_sent": 0,
                    "bytes_received": 0,
                    "attack_techniques": []
                }
                loadtest.attack_stats = attack_stats_ref
            
            # Resetear todas las estadísticas
            attack_stats_ref["start_time"] = datetime.now()
            attack_stats_ref["end_time"] = None
            attack_stats_ref["requests_sent"] = 0
            attack_stats_ref["responses_received"] = 0
            attack_stats_ref["http_codes"] = defaultdict(int)
            attack_stats_ref["latencies"] = []
            attack_stats_ref["errors"] = []
            attack_stats_ref["peak_rps"] = 0
            attack_stats_ref["avg_rps"] = 0
            attack_stats_ref["last_request_count"] = 0
            attack_stats_ref["bytes_sent"] = 0
            attack_stats_ref["bytes_received"] = 0
            attack_stats_ref["attack_techniques"] = []
            
            # Forzar actualización inmediata y verificar
            loadtest.log_message("INFO", f"📊 [WEB] Estadísticas reseteadas - start_time: {attack_stats_ref['start_time']}, id: {id(attack_stats_ref)}", context="start_attack", force_console=True)
            print(f"DEBUG [start_attack]: attack_stats id={id(attack_stats_ref)}, loadtest.attack_stats id={id(loadtest.attack_stats)}")
            
            loadtest.log_message("INFO", "🚀 [WEB] Iniciando ataque desde panel web", context="start_attack", force_console=True)
            
            # Configurar sys.argv para simular línea de comandos
            original_argv = sys.argv
            sys.argv = ['loadtest.py', '-t', TARGET, '-d', str(DURATION), '-p', POWER_LEVEL]
            if WAF_BYPASS:
                sys.argv.append('--bypass-waf')
            if USE_LARGE_PAYLOADS:
                sys.argv.append('--large-payloads')
            if STEALTH_MODE:
                sys.argv.append('--stealth')
            if not AUTO_THROTTLE:
                sys.argv.append('--no-auto-throttle')
            if not MEMORY_MONITORING:
                sys.argv.append('--no-memory-monitoring')
            sys.argv.extend(['--connections', str(MAX_CONNECTIONS), '--threads', str(MAX_THREADS)])
            
            loadtest.main()
            sys.argv = original_argv
            
            # Generar reporte automáticamente al finalizar
            try:
                if loadtest.attack_stats.get("requests_sent", 0) > 0:
                    loadtest.generate_report()
                    loadtest.log_message("INFO", "📄 [WEB] Reporte generado automáticamente", context="start_attack", force_console=True)
            except Exception as e:
                loadtest.log_message("ERROR", f"Error generando reporte: {e}", context="start_attack")
                
        except Exception as e:
            import traceback
            error_msg = f"Error ejecutando ataque: {e}\n{traceback.format_exc()}"
            print(error_msg)
            # Loggear el error
            try:
                import loadtest
                loadtest.log_message("ERROR", f"❌ [WEB] {error_msg}", context="start_attack", force_console=True)
            except:
                pass
    
    current_attack_process = threading.Thread(target=run_attack, daemon=True)
    current_attack_process.start()
    
    return jsonify({"status": "success", "message": "Ataque iniciado"})

@app.route('/api/stop', methods=['POST'])
def stop_attack():
    """Detiene el ataque actual y limpia recursos con mejor sincronización"""
    global monitoring_active
    
    # Sincronizar estado en ambos módulos
    monitoring_active = False
    loadtest.monitoring_active = False
    
    # Limpiar conexiones y recursos
    try:
        if hasattr(loadtest, 'ConnectionManager'):
            loadtest.ConnectionManager.clear_sessions()
            loadtest.log_message("INFO", "🔌 [STOP] Sesiones de conexión limpiadas", context="stop_attack")
    except Exception as e:
        loadtest.log_message("ERROR", f"Error limpiando sesiones: {e}", context="stop_attack")
    
    # Usar función mejorada de cleanup
    try:
        if hasattr(loadtest, 'cleanup_all_processes'):
            loadtest.cleanup_all_processes(force=False)
            loadtest.log_message("INFO", "🧹 [STOP] Procesos limpiados usando cleanup mejorado", context="stop_attack")
        else:
            # Fallback a método básico
            for process in loadtest.running_processes[:]:
                try:
                    process.terminate()
                    process.wait(timeout=2)
                except:
                    try:
                        process.kill()
                    except:
                        pass
            loadtest.running_processes.clear()
            loadtest.log_message("INFO", "🧹 [STOP] Procesos terminados", context="stop_attack")
    except Exception as e:
        loadtest.log_message("ERROR", f"Error limpiando procesos: {e}", context="stop_attack")
    
    # Resetear estadísticas de ataque
    try:
        loadtest.attack_stats["start_time"] = None
        loadtest.attack_stats["end_time"] = datetime.now()
        loadtest.log_message("INFO", "📊 [STOP] Estadísticas de ataque reseteadas", context="stop_attack")
    except:
        pass
    
    return jsonify({
        "status": "success", 
        "message": "Ataque detenido y recursos liberados",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/tool-recommendations', methods=['GET'])
def get_tool_recommendations():
    """Obtiene recomendaciones de herramientas basadas en fingerprint"""
    try:
        # Intentar cargar fingerprint más reciente
        fingerprint = None
        try:
            fingerprint_file = REPORTS_DIR / f"fingerprint_{DOMAIN.replace('.', '_').replace(':', '_')}.json"
            if fingerprint_file.exists():
                with open(fingerprint_file, "r", encoding="utf-8") as f:
                    fingerprint = json.load(f)
        except:
            pass
        
        # Obtener recomendaciones
        recommendations = recommend_tools_from_fingerprint(fingerprint)
        
        return jsonify({
            "status": "success",
            "recommendations": recommendations
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/autodiagnostic', methods=['GET', 'POST'])
def run_autodiagnostic_endpoint():
    """Ejecuta autodiagnóstico completo y retorna reporte"""
    try:
        # Ejecutar autodiagnóstico en thread separado para no bloquear
        import threading
        diagnostic_result = {"status": "running", "report": None, "error": None}
        
        def run_diagnostic():
            try:
                diagnostic_report = run_autodiagnostic()
                diagnostic_result["status"] = "completed"
                diagnostic_result["report"] = diagnostic_report
            except Exception as e:
                diagnostic_result["status"] = "error"
                diagnostic_result["error"] = str(e)
        
        # Si es GET, ejecutar y esperar (para mostrar en web)
        if request.method == 'GET':
            run_diagnostic()
            if diagnostic_result["status"] == "error":
                return jsonify({
                    "status": "error",
                    "message": diagnostic_result["error"]
                }), 500
            return jsonify({
                "status": "success",
                "report": diagnostic_result["report"]
            })
        else:
            # POST: ejecutar en background
            thread = threading.Thread(target=run_diagnostic, daemon=True)
            thread.start()
            return jsonify({
                "status": "started",
                "message": "Autodiagnóstico iniciado"
            })
    except Exception as e:
        import traceback
        return jsonify({
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc() if getattr(loadtest, 'DEBUG_MODE', False) else None
        }), 500

@app.route('/api/fingerprint', methods=['POST'])
def run_fingerprint():
    """Ejecuta fingerprint del target"""
    global TARGET
    data = request.json
    target = data.get("target", TARGET)
    
    if not target or not target.strip():
        return jsonify({"status": "error", "message": "Target no especificado"}), 400
    
    try:
        # Actualizar TARGET en ambos módulos
        target = target.strip()
        TARGET = target
        loadtest.TARGET = target
        
        # Limpiar variables previas
        loadtest.DOMAIN = ""
        loadtest.IP_ADDRESS = ""
        loadtest.TARGET_TYPE = "DOMAIN"
        loadtest.NETWORK_TYPE = "PUBLIC"
        
        # Validar y parsear target
        validation_result = validate_critical_variables()
        print(f"DEBUG: validate_critical_variables() retornó: {validation_result}")
        print(f"DEBUG: TARGET={loadtest.TARGET}, DOMAIN={loadtest.DOMAIN}, IP={loadtest.IP_ADDRESS}")
        
        if not validation_result:
            # Validación falló - obtener información de debug
            debug_info = {
                "target_original": target,
                "target_after_validation": loadtest.TARGET,
                "domain": loadtest.DOMAIN,
                "ip_address": loadtest.IP_ADDRESS,
                "target_type": loadtest.TARGET_TYPE,
                "network_type": loadtest.NETWORK_TYPE,
                "protocol": getattr(loadtest, 'PROTOCOL', None),
                "port": getattr(loadtest, 'PORT', None)
            }
            print(f"DEBUG [validate_critical_variables failed]: {debug_info}")
            return jsonify({
                "status": "error", 
                "message": "Target inválido después de validación",
                "debug": debug_info
            }), 400
        
        # Si la validación fue exitosa, ejecutar fingerprint
        # Asegurar que está en modo web panel
        loadtest.WEB_PANEL_MODE = True
        print(f"DEBUG: Ejecutando fingerprint_target() para {loadtest.TARGET}")
        
        try:
            fingerprint = fingerprint_target()
        except Exception as fingerprint_error:
            import traceback
            error_trace = traceback.format_exc()
            print(f"DEBUG: Error en fingerprint_target(): {fingerprint_error}")
            print(f"DEBUG: Traceback: {error_trace}")
            debug_mode = getattr(loadtest, 'DEBUG_MODE', False)
            return jsonify({
                "status": "error", 
                "message": f"Error ejecutando fingerprint: {str(fingerprint_error)}",
                "error_type": type(fingerprint_error).__name__,
                "traceback": error_trace if debug_mode else None
            }), 500
        
        # Generar recomendaciones automáticas de stress (con manejo de errores)
        stress_recommendations = {}
        try:
            stress_recommendations = generate_stress_recommendations(fingerprint)
        except Exception as rec_error:
            import traceback
            print(f"DEBUG: Error generando recomendaciones: {rec_error}")
            print(f"DEBUG: Traceback recomendaciones: {traceback.format_exc()}")
            stress_recommendations = {"error": str(rec_error), "message": "No se pudieron generar recomendaciones"}
        
        # Generar recomendaciones de herramientas basadas en fingerprint
        tool_recommendations = {}
        try:
            tool_recommendations = recommend_tools_from_fingerprint(fingerprint)
        except Exception as tool_rec_error:
            import traceback
            print(f"DEBUG: Error generando recomendaciones de herramientas: {tool_rec_error}")
            print(f"DEBUG: Traceback recomendaciones de herramientas: {traceback.format_exc()}")
            tool_recommendations = {"error": str(tool_rec_error), "message": "No se pudieron generar recomendaciones de herramientas"}
        
        # Asegurar que el fingerprint sea serializable a JSON
        # Convertir cualquier objeto datetime o no serializable
        try:
            # Intentar serializar para verificar que es válido
            json.dumps(fingerprint, default=str)
        except Exception as json_error:
            print(f"DEBUG: Error serializando fingerprint: {json_error}")
            # Limpiar objetos no serializables convirtiendo todo a string donde sea necesario
            fingerprint_clean = {}
            for key, value in fingerprint.items():
                try:
                    json.dumps(value, default=str)
                    fingerprint_clean[key] = value
                except:
                    fingerprint_clean[key] = str(value) if value is not None else None
            fingerprint = fingerprint_clean
        
        return jsonify({
            "status": "success", 
            "fingerprint": fingerprint,
            "stress_recommendations": stress_recommendations,
            "tool_recommendations": tool_recommendations,
            "fingerprint_status": fingerprint.get("status", "completed"),
            "completed_at": fingerprint.get("completed_at", datetime.now().isoformat())
        })
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"DEBUG: Error general en run_fingerprint(): {e}")
        print(f"DEBUG: Traceback: {error_trace}")
        debug_mode = getattr(loadtest, 'DEBUG_MODE', False)
        return jsonify({
            "status": "error", 
            "message": str(e),
            "error_type": type(e).__name__,
            "traceback": error_trace if debug_mode else None
        }), 500

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """Obtiene recomendaciones de configuración basadas en fingerprint"""
    try:
        data = request.json or {}
        fingerprint = data.get("fingerprint")
        
        recommendations = generate_stress_recommendations(fingerprint)
        return jsonify({"status": "success", "recommendations": recommendations})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/generate-command', methods=['POST'])
def generate_command():
    """Genera la línea de comando basada en recomendaciones"""
    try:
        data = request.json or {}
        tool_recommendations = data.get("tool_recommendations", {})
        stress_recommendations = data.get("stress_recommendations", {})
        target = data.get("target", TARGET)
        
        if not target:
            return jsonify({"status": "error", "message": "Target no especificado"}), 400
        
        # Obtener parámetros óptimos
        optimal_params = tool_recommendations.get("optimal_parameters", {})
        
        # Construir línea de comando
        cmd_parts = ["python", "loadtest.py"]
        cmd_parts.extend(["-t", target])
        
        # Duración
        duration = stress_recommendations.get("recommended_duration") or optimal_params.get("duration") or DURATION
        cmd_parts.extend(["-d", str(duration)])
        
        # Power level
        power_level = optimal_params.get("power_level") or stress_recommendations.get("recommended_power_level") or POWER_LEVEL
        cmd_parts.extend(["-p", power_level])
        
        # Conexiones
        max_connections = optimal_params.get("max_connections") or stress_recommendations.get("recommended_connections") or MAX_CONNECTIONS
        cmd_parts.extend(["--connections", str(max_connections)])
        
        # Threads
        max_threads = optimal_params.get("max_threads") or stress_recommendations.get("recommended_threads") or MAX_THREADS
        cmd_parts.extend(["--threads", str(max_threads)])
        
        # WAF bypass
        if optimal_params.get("waf_bypass") or stress_recommendations.get("recommended_waf_bypass"):
            cmd_parts.append("--bypass-waf")
        
        # Stealth mode
        if optimal_params.get("stealth_mode") or stress_recommendations.get("recommended_stealth"):
            cmd_parts.append("--stealth")
        
        # Large payloads
        if stress_recommendations.get("recommended_large_payloads"):
            cmd_parts.append("--large-payloads")
        
        # Attack mode (siempre MIXED para usar recomendaciones)
        cmd_parts.extend(["--mode", "MIXED"])
        
        # Construir comando final
        command = " ".join(cmd_parts)
        
        return jsonify({
            "status": "success",
            "command": command,
            "parameters": {
                "target": target,
                "duration": duration,
                "power_level": power_level,
                "max_connections": max_connections,
                "max_threads": max_threads,
                "waf_bypass": optimal_params.get("waf_bypass", False),
                "stealth_mode": optimal_params.get("stealth_mode", False),
                "expected_sessions": tool_recommendations.get("expected_sessions", "N/A")
            }
        })
    except Exception as e:
        import traceback
        return jsonify({
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc() if getattr(loadtest, 'DEBUG_MODE', False) else None
        }), 500

@app.route('/api/start-recommended', methods=['POST'])
def start_recommended_attack():
    """Inicia un ataque con parámetros recomendados del fingerprint"""
    global current_attack_process, TARGET, DURATION, POWER_LEVEL, MAX_CONNECTIONS, MAX_THREADS, WAF_BYPASS, STEALTH_MODE, ATTACK_MODE, PROXY_LIST, PROXY_ROTATION
    
    if current_attack_process and current_attack_process.is_alive():
        return jsonify({"status": "error", "message": "Ya hay un ataque en ejecución"}), 400
    
    try:
        data = request.json or {}
        tool_recommendations = data.get("tool_recommendations", {})
        stress_recommendations = data.get("stress_recommendations", {})
        target = data.get("target") or TARGET or loadtest.TARGET
        
        # Si aún no hay target, intentar obtenerlo del fingerprint guardado
        if not target or not target.strip():
            # Intentar obtener del fingerprint si está disponible en loadtest
            if hasattr(loadtest, 'DOMAIN') and loadtest.DOMAIN:
                target = loadtest.DOMAIN
                if hasattr(loadtest, 'PROTOCOL') and loadtest.PROTOCOL:
                    port = getattr(loadtest, 'PORT', None)
                    if port and port not in [80, 443]:
                        target = f"{loadtest.PROTOCOL}://{target}:{port}"
                    else:
                        target = f"{loadtest.PROTOCOL}://{target}"
        
        if not target or not target.strip():
            return jsonify({
                "status": "error", 
                "message": "Target no especificado. Asegúrate de haber ejecutado un fingerprint primero o especifica el target en la configuración."
            }), 400
        
        # Normalizar target (quitar espacios y asegurar formato correcto)
        target = target.strip()
        
        # Log del target recibido para debugging
        loadtest.log_message("INFO", f"🎯 [START-RECOMMENDED] Target recibido: '{target}'", context="start_recommended_attack", force_console=True)
        
        # Obtener parámetros óptimos
        optimal_params = tool_recommendations.get("optimal_parameters", {})
        
        # Aplicar parámetros recomendados
        TARGET = target
        DURATION = stress_recommendations.get("recommended_duration") or optimal_params.get("duration") or DURATION
        POWER_LEVEL = optimal_params.get("power_level") or stress_recommendations.get("recommended_power_level") or POWER_LEVEL
        MAX_CONNECTIONS = optimal_params.get("max_connections") or stress_recommendations.get("recommended_connections") or MAX_CONNECTIONS
        MAX_THREADS = optimal_params.get("max_threads") or stress_recommendations.get("recommended_threads") or MAX_THREADS
        WAF_BYPASS = optimal_params.get("waf_bypass", False) or stress_recommendations.get("recommended_waf_bypass", False)
        STEALTH_MODE = optimal_params.get("stealth_mode", False) or stress_recommendations.get("recommended_stealth", False)
        ATTACK_MODE = "MIXED"  # Siempre MIXED para usar recomendaciones
        
        # Sincronizar con loadtest - IMPORTANTE: actualizar TARGET primero
        loadtest.TARGET = TARGET
        loadtest.DURATION = DURATION
        loadtest.POWER_LEVEL = POWER_LEVEL
        loadtest.MAX_CONNECTIONS = MAX_CONNECTIONS
        loadtest.MAX_THREADS = MAX_THREADS
        loadtest.WAF_BYPASS = WAF_BYPASS
        loadtest.STEALTH_MODE = STEALTH_MODE
        loadtest.ATTACK_MODE = ATTACK_MODE
        
        # Aplicar parámetros adicionales si existen
        if "connect_timeout" in optimal_params:
            loadtest.CONNECT_TIMEOUT = optimal_params["connect_timeout"]
        if "read_timeout" in optimal_params:
            loadtest.READ_TIMEOUT = optimal_params["read_timeout"]
        if "multiplier" in optimal_params:
            loadtest.MULTIPLIER = optimal_params["multiplier"]
        if "pool_connections" in optimal_params:
            loadtest.CONNECTION_POOL_SIZE = optimal_params["pool_connections"]
        if "keep_alive" in optimal_params:
            loadtest.KEEP_ALIVE_POOLING = optimal_params["keep_alive"]
        
        # Validar target DESPUÉS de sincronizar todas las variables
        # IMPORTANTE: La función validate_critical_variables() usa las variables globales del módulo loadtest
        # Asegurarse de que todas las variables necesarias estén actualizadas antes de validar
        try:
            # Forzar actualización de variables críticas antes de validar
            # La validación puede modificar TARGET, así que guardar el original
            original_target = loadtest.TARGET
            
            # Asegurar que PROTOCOL y PORT estén definidos si no lo están
            if not hasattr(loadtest, 'PROTOCOL') or not loadtest.PROTOCOL:
                loadtest.PROTOCOL = "https" if target.startswith("https://") else "http"
            if not hasattr(loadtest, 'PORT') or not loadtest.PORT:
                if ":" in target and target.count(":") > 1:  # Puede tener puerto
                    try:
                        from urllib.parse import urlparse
                        parsed = urlparse(target if "://" in target else f"http://{target}")
                        loadtest.PORT = parsed.port or (443 if loadtest.PROTOCOL == "https" else 80)
                    except:
                        loadtest.PORT = 443 if loadtest.PROTOCOL == "https" else 80
                else:
                    loadtest.PORT = 443 if loadtest.PROTOCOL == "https" else 80
            
            # Llamar a la validación (modifica variables globales de loadtest)
            # IMPORTANTE: validate_critical_variables() usa las variables globales del módulo loadtest
            # Asegurarse de que TARGET esté correctamente establecido antes de validar
            loadtest.log_message("DEBUG", f"🔍 [START-RECOMMENDED] Antes de validar - TARGET: '{loadtest.TARGET}', PROTOCOL: {getattr(loadtest, 'PROTOCOL', 'N/A')}, PORT: {getattr(loadtest, 'PORT', 'N/A')}", context="start_recommended_attack", force_console=True)
            
            validation_result = validate_critical_variables()
            
            loadtest.log_message("DEBUG", f"🔍 [START-RECOMMENDED] Después de validar - TARGET: '{loadtest.TARGET}', Resultado: {validation_result}", context="start_recommended_attack", force_console=True)
            
            if not validation_result:
                # Obtener más información sobre el error para debugging
                error_details = {
                    "target_original": original_target,
                    "target_after_validation": loadtest.TARGET,
                    "target_type": getattr(loadtest, 'TARGET_TYPE', 'N/A'),
                    "domain": getattr(loadtest, 'DOMAIN', 'N/A'),
                    "ip_address": getattr(loadtest, 'IP_ADDRESS', 'N/A'),
                    "protocol": getattr(loadtest, 'PROTOCOL', 'N/A'),
                    "port": getattr(loadtest, 'PORT', 'N/A')
                }
                
                # Log del error para debugging
                loadtest.log_message("ERROR", f"❌ [START-RECOMMENDED] Validación falló. Target original: '{original_target}', Target después: '{loadtest.TARGET}'", context="start_recommended_attack", force_console=True)
                
                return jsonify({
                    "status": "error", 
                    "message": f"Target inválido después de aplicar parámetros. Ver detalles para más información.",
                    "details": error_details
                }), 400
            
            # Si la validación fue exitosa, actualizar TARGET local con el valor validado
            TARGET = loadtest.TARGET
            
        except Exception as validation_error:
            import traceback
            error_trace = traceback.format_exc()
            loadtest.log_message("ERROR", f"❌ [START-RECOMMENDED] Excepción en validación: {str(validation_error)}\n{error_trace}", context="start_recommended_attack", force_console=True)
            return jsonify({
                "status": "error",
                "message": f"Error validando target: {str(validation_error)}",
                "traceback": error_trace if getattr(loadtest, 'DEBUG_MODE', False) else None
            }), 400
        
        # Generar comando para mostrar (después de validación exitosa)
        cmd_parts = ["python", "loadtest.py", "-t", TARGET, "-d", str(DURATION), "-p", POWER_LEVEL,
                     "--connections", str(MAX_CONNECTIONS), "--threads", str(MAX_THREADS), "--mode", "MIXED"]
        if WAF_BYPASS:
            cmd_parts.append("--bypass-waf")
        if STEALTH_MODE:
            cmd_parts.append("--stealth")
        # Agregar proxies al comando si están configurados
        if PROXY_LIST:
            # Si hay proxies, mostrar en el comando (usar archivo si es posible)
            cmd_parts.append("--proxy-file")
            cmd_parts.append("proxies.txt")
            cmd_parts.append("--proxy-rotation")
            cmd_parts.append(PROXY_ROTATION or "round-robin")
        command = " ".join(cmd_parts)
        
        # Iniciar ataque en thread separado (usar la misma lógica que start_attack)
        def run_recommended_attack():
            try:
                import loadtest
                import sys
                from collections import defaultdict
                
                # Sincronizar estado antes de iniciar
                loadtest.WEB_PANEL_MODE = True
                loadtest.DEBUG_MODE = True
                loadtest.monitoring_active = True
                
                # Sincronizar variables globales
                loadtest.TARGET = TARGET
                loadtest.DURATION = DURATION
                loadtest.POWER_LEVEL = POWER_LEVEL
                loadtest.ATTACK_MODE = ATTACK_MODE
                loadtest.MAX_CONNECTIONS = MAX_CONNECTIONS
                loadtest.MAX_THREADS = MAX_THREADS
                loadtest.WAF_BYPASS = WAF_BYPASS
                loadtest.USE_LARGE_PAYLOADS = USE_LARGE_PAYLOADS
                loadtest.STEALTH_MODE = STEALTH_MODE
                loadtest.AUTO_THROTTLE = AUTO_THROTTLE
                loadtest.MEMORY_MONITORING = MEMORY_MONITORING
                
                # Asegurar que los proxies configurados estén cargados - SIGUIENDO LÓGICA DEL SCRIPT EXITOSO
                if PROXY_LIST:
                    loadtest.PROXY_LIST = PROXY_LIST
                    loadtest.log_message("INFO", f"✅ [RECOMMENDED] {len(PROXY_LIST)} proxy(s) cargado(s) para ataque devastador", context="start_recommended_attack", force_console=True)
                if PROXY_ROTATION:
                    loadtest.PROXY_ROTATION = PROXY_ROTATION
                
                # Resetear estadísticas
                attack_stats_ref = loadtest.attack_stats
                if attack_stats_ref:
                    attack_stats_ref["start_time"] = datetime.now()
                    attack_stats_ref["end_time"] = None
                    attack_stats_ref["requests_sent"] = 0
                    attack_stats_ref["responses_received"] = 0
                    attack_stats_ref["http_codes"] = defaultdict(int)
                    attack_stats_ref["latencies"] = []
                    attack_stats_ref["errors"] = []
                    attack_stats_ref["peak_rps"] = 0
                    attack_stats_ref["avg_rps"] = 0
                    attack_stats_ref["is_recommended_attack"] = True  # Marcar como ataque recomendado
                
                loadtest.log_message("INFO", "🚀 [RECOMMENDED] Iniciando ataque recomendado desde panel web", context="start_recommended_attack", force_console=True)
                
                # Configurar sys.argv para simular línea de comandos
                original_argv = sys.argv
                sys.argv = ['loadtest.py', '-t', TARGET, '-d', str(DURATION), '-p', POWER_LEVEL]
                if WAF_BYPASS:
                    sys.argv.append('--bypass-waf')
                if USE_LARGE_PAYLOADS:
                    sys.argv.append('--large-payloads')
                if STEALTH_MODE:
                    sys.argv.append('--stealth')
                if not AUTO_THROTTLE:
                    sys.argv.append('--no-auto-throttle')
                sys.argv.extend(['--connections', str(MAX_CONNECTIONS), '--threads', str(MAX_THREADS), '--mode', 'MIXED'])
                
                loadtest.main()
                sys.argv = original_argv
            except Exception as e:
                loadtest.log_message("ERROR", f"Error en ataque recomendado: {e}", context="start_recommended_attack", force_console=True)
        
        current_attack_process = threading.Thread(target=run_recommended_attack, daemon=True)
        current_attack_process.start()
        
        return jsonify({
            "status": "success",
            "message": "Ataque recomendado iniciado",
            "command": command,
            "parameters": {
                "target": TARGET,
                "duration": DURATION,
                "power_level": POWER_LEVEL,
                "max_connections": MAX_CONNECTIONS,
                "max_threads": MAX_THREADS,
                "waf_bypass": WAF_BYPASS,
                "stealth_mode": STEALTH_MODE,
                "proxies_loaded": len(PROXY_LIST) if PROXY_LIST else 0,
                "proxy_rotation": PROXY_ROTATION or "round-robin",
                "expected_sessions": tool_recommendations.get("expected_sessions", "N/A")
            }
        })
    except Exception as e:
        import traceback
        return jsonify({
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc() if getattr(loadtest, 'DEBUG_MODE', False) else None
        }), 500

@app.route('/api/apply-recommendations', methods=['POST'])
def apply_recommendations():
    """Aplica recomendaciones automáticas a la configuración"""
    data = request.json
    recommendations = data.get("recommendations", {})
    
    if not recommendations:
        return jsonify({"status": "error", "message": "No se proporcionaron recomendaciones"}), 400
    
    # Aplicar recomendaciones
    config_update = {
        "power_level": recommendations.get("recommended_power_level", POWER_LEVEL),
        "duration": recommendations.get("recommended_duration", DURATION),
        "max_connections": recommendations.get("recommended_connections", MAX_CONNECTIONS),
        "max_threads": recommendations.get("recommended_threads", MAX_THREADS),
        "waf_bypass": recommendations.get("recommended_waf_bypass", WAF_BYPASS),
        "stealth_mode": recommendations.get("recommended_stealth", STEALTH_MODE),
        "use_large_payloads": recommendations.get("recommended_large_payloads", USE_LARGE_PAYLOADS)
    }
    
    # Actualizar configuración
    result = set_config()
    if result.status_code == 200:
        return jsonify({
            "status": "success", 
            "message": "Recomendaciones aplicadas",
            "applied_config": config_update
        })
    else:
        return result

@app.route('/api/params', methods=['GET'])
def show_all_params():
    """Muestra todos los parámetros configurables"""
    return jsonify({
        "version": VERSION,
        "target_config": {
            "target": TARGET,
            "domain": DOMAIN,
            "ip_address": IP_ADDRESS,
            "target_type": TARGET_TYPE,
            "network_type": NETWORK_TYPE,
            "protocol": get_loadtest_var('PROTOCOL'),
            "port": get_loadtest_var('PORT')
        },
        "attack_config": {
            "duration": DURATION,
            "power_level": POWER_LEVEL,
            "multiplier": POWER_LEVELS.get(POWER_LEVEL, 0),
            "attack_mode": ATTACK_MODE,
            "attack_pattern": get_loadtest_var('ATTACK_PATTERN'),
            "max_connections": MAX_CONNECTIONS,
            "max_threads": MAX_THREADS,
            "payload_size_kb": PAYLOAD_SIZE_KB,
            "use_large_payloads": USE_LARGE_PAYLOADS
        },
        "monitoring_config": {
            "memory_monitoring": MEMORY_MONITORING,
            "auto_throttle": AUTO_THROTTLE,
            "memory_threshold_warn": MEMORY_THRESHOLD_WARN,
            "memory_threshold_critical": MEMORY_THRESHOLD_CRITICAL,
            "memory_threshold_oom": MEMORY_THRESHOLD_OOM
        },
        "evasion_config": {
            "waf_bypass": WAF_BYPASS,
            "stealth_mode": STEALTH_MODE,
            "proxy_list": get_loadtest_var('PROXY_LIST') or [],
            "proxy_rotation": get_loadtest_var('PROXY_ROTATION') or 'round-robin'
        },
        "system_config": {
            "debug_mode": get_loadtest_var('DEBUG_MODE') or False,
            "dry_run": get_loadtest_var('DRY_RUN') or False,
            "network_mode": get_loadtest_var('NETWORK_MODE') or 'AUTO'
        },
        "power_levels": POWER_LEVELS,
        "available_tools": TOOLS
    })

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Obtiene los logs más recientes con soporte para streaming"""
    try:
        lines = int(request.args.get('lines', 200))
        log_type = request.args.get('type', 'debug')  # 'debug' o 'general'
        last_position = int(request.args.get('last_position', 0))  # Para streaming
        
        # Buscar archivo de log más reciente
        log_files = []
        if LOGS_DIR.exists():
            # Buscar logs del día actual
            today = datetime.now().strftime('%Y%m%d')
            log_files.extend(list(LOGS_DIR.glob(f"loadtest_*{today}.log")))
            log_files.extend(list(LOGS_DIR.glob(f"loadtest_debug_{today}.log")))
            
            # Si no hay del día actual, buscar el más reciente
            if not log_files:
                log_files = sorted(LOGS_DIR.glob("loadtest_*.log"), key=lambda x: x.stat().st_mtime, reverse=True)
        
        if log_files:
            log_file = log_files[0]  # Usar el más reciente
            
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                # Si hay last_position, leer desde ahí (streaming)
                if last_position > 0:
                    try:
                        f.seek(last_position)
                        new_lines = f.readlines()
                        current_position = f.tell()
                        return jsonify({
                            "status": "success",
                            "logs": new_lines,
                            "position": current_position,
                            "total_lines": 0  # No necesario en streaming
                        })
                    except:
                        # Si falla, leer desde el final
                        f.seek(0, 2)  # Ir al final
                        current_position = f.tell()
                        return jsonify({
                            "status": "success",
                            "logs": [],
                            "position": current_position,
                            "total_lines": 0
                        })
                else:
                    # Lectura normal
                    all_lines = f.readlines()
                    recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                    return jsonify({
                        "status": "success",
                        "logs": recent_lines,
                        "position": 0,
                        "total_lines": len(all_lines)
                    })
        else:
            return jsonify({
                "status": "error",
                "message": "No se encontraron logs",
                "logs": [],
                "position": 0,
                "total_lines": 0
            })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "logs": [],
            "position": 0,
            "total_lines": 0
        }), 500

@app.route('/api/system-info', methods=['GET'])
def get_system_info():
    """Obtiene información del sistema"""
    try:
        import psutil
        
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return jsonify({
            "status": "success",
            "system": {
                "cpu_percent": cpu_percent,
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": round(memory.total / (1024**3), 2),
                "memory_used_gb": round(memory.used / (1024**3), 2),
                "memory_percent": memory.percent,
                "disk_total_gb": round(disk.total / (1024**3), 2),
                "disk_used_gb": round(disk.used / (1024**3), 2),
                "disk_percent": disk.percent
            }
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint mejorado con verificación de componentes críticos"""
    try:
        health_status = {
            "status": "healthy",
            "version": VERSION,
            "timestamp": datetime.now().isoformat(),
            "components": {}
        }
        
        # Verificar componentes críticos
        try:
            # Verificar que loadtest está importado correctamente
            health_status["components"]["loadtest_module"] = "ok" if hasattr(loadtest, 'VERSION') else "error"
            
            # Verificar directorios
            history_dir = get_loadtest_var('HISTORY_DIR')
            health_status["components"]["directories"] = {
                "output": "ok" if OUTPUT_DIR and OUTPUT_DIR.exists() else "error",
                "logs": "ok" if LOGS_DIR and LOGS_DIR.exists() else "error",
                "reports": "ok" if REPORTS_DIR and REPORTS_DIR.exists() else "error",
                "history": "ok" if history_dir and history_dir.exists() else "error"
            }
            
            # Verificar estado de ataque
            monitoring = get_loadtest_var('monitoring_active')
            running_procs = get_loadtest_var('running_processes') or []
            health_status["components"]["attack_status"] = {
                "monitoring_active": monitoring if monitoring is not None else False,
                "has_active_processes": len(running_procs) > 0,
                "process_count": len(running_procs)
            }
            
            # Verificar recursos del sistema
            try:
                import psutil
                memory = psutil.virtual_memory()
                cpu = psutil.cpu_percent(interval=0.1)
                health_status["components"]["system"] = {
                    "cpu_percent": cpu,
                    "memory_percent": memory.percent,
                    "memory_available_gb": round(memory.available / (1024**3), 2),
                    "status": "ok" if memory.percent < 90 and cpu < 95 else "warning"
                }
            except:
                health_status["components"]["system"] = {"status": "unavailable"}
            
            # Determinar estado general
            all_ok = (
                health_status["components"].get("loadtest_module") == "ok" and
                all(v == "ok" for v in health_status["components"].get("directories", {}).values())
            )
            
            if not all_ok:
                health_status["status"] = "degraded"
                
        except Exception as e:
            health_status["status"] = "error"
            health_status["error"] = str(e)
        
        return jsonify(health_status)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "version": VERSION,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/attack-status', methods=['GET'])
def get_attack_status():
    """Obtiene el estado del ataque actual"""
    try:
        # Obtener monitoring_active y attack_stats del módulo loadtest directamente
        monitoring_active_actual = get_loadtest_var('monitoring_active') or monitoring_active
        attack_stats_actual = get_loadtest_var('attack_stats') or attack_stats
        requests_sent = attack_stats_actual.get("requests_sent", 0)
        is_running = monitoring_active_actual and (requests_sent > 0 or attack_stats_actual.get("start_time") is not None)
        
        start_time_val = attack_stats_actual.get("start_time")
        if start_time_val and hasattr(start_time_val, 'isoformat'):
            start_time_str = start_time_val.isoformat()
        elif isinstance(start_time_val, str):
            start_time_str = start_time_val
        else:
            start_time_str = None
        
        return jsonify({
            "status": "success",
            "attack": {
                "is_running": is_running,
                "monitoring_active": monitoring_active_actual,
                "start_time": start_time_str,
                "requests_sent": requests_sent,
                "responses_received": attack_stats_actual.get("responses_received", 0),
                "errors_count": len(attack_stats_actual.get("errors", []))
            }
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    # Verificación de autorización antes de iniciar panel web
    try:
        if hasattr(loadtest, '_verify_authorization'):
            if not loadtest._verify_authorization():
                print("Acceso no autorizado. Panel desactivado.")
                sys.exit(1)
    except Exception:
        pass  # Continuar si hay error en verificación
    
    print(f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║         LoadTest Enterprise Panel Web v{VERSION}             ║
    ║                                                              ║
    ║  🌐 Panel Web: http://localhost:5000                        ║
    ║  Plataforma Profesional de Pruebas de Seguridad             ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)

