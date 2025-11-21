#!/usr/bin/env python3
"""
Servidor de tracking para LoadTest Enterprise
Recibe y almacena datos de tracking de instancias de la herramienta

USO:
    python tracking_server.py

El servidor escuchará en http://localhost:8080/track
Los datos se almacenarán en tracking_data.json
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime
from pathlib import Path
import sys

app = Flask(__name__)
CORS(app)

TRACKING_FILE = Path("tracking_data.json")

def load_tracking_data():
    """Carga datos de tracking existentes"""
    if TRACKING_FILE.exists():
        try:
            with open(TRACKING_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {"events": []}
    return {"events": []}

def save_tracking_data(data):
    """Guarda datos de tracking"""
    try:
        with open(TRACKING_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error guardando datos: {e}")
        return False

@app.route('/track', methods=['POST', 'GET'])
def track():
    """Endpoint para recibir datos de tracking"""
    try:
        if request.method == 'POST':
            # Obtener datos del POST
            data = request.form.to_dict() or request.json or {}
        else:
            # Obtener datos del GET
            data = request.args.to_dict()
        
        # Agregar timestamp de recepción
        data['received_at'] = datetime.now().isoformat()
        data['server_ip'] = request.remote_addr
        
        # Cargar datos existentes
        tracking_data = load_tracking_data()
        
        # Agregar nuevo evento
        if 'events' not in tracking_data:
            tracking_data['events'] = []
        
        tracking_data['events'].append(data)
        
        # Mantener solo los últimos 1000 eventos
        if len(tracking_data['events']) > 1000:
            tracking_data['events'] = tracking_data['events'][-1000:]
        
        # Guardar datos
        save_tracking_data(tracking_data)
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Tracking recibido: {data.get('status', 'unknown')} - {data.get('hostname', 'unknown')}")
        
        return jsonify({"status": "success", "message": "Tracking data received"}), 200
        
    except Exception as e:
        print(f"Error procesando tracking: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/events', methods=['GET'])
def get_events():
    """Obtiene todos los eventos de tracking"""
    try:
        tracking_data = load_tracking_data()
        return jsonify(tracking_data), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/events/latest', methods=['GET'])
def get_latest_events():
    """Obtiene los últimos N eventos"""
    try:
        limit = int(request.args.get('limit', 50))
        tracking_data = load_tracking_data()
        events = tracking_data.get('events', [])
        return jsonify({"events": events[-limit:], "total": len(events)}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/events/<status>', methods=['GET'])
def get_events_by_status(status):
    """Obtiene eventos filtrados por status"""
    try:
        tracking_data = load_tracking_data()
        events = [e for e in tracking_data.get('events', []) if e.get('status') == status]
        return jsonify({"events": events, "count": len(events)}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Obtiene estadísticas de tracking"""
    try:
        tracking_data = load_tracking_data()
        events = tracking_data.get('events', [])
        
        stats = {
            "total_events": len(events),
            "unique_hostnames": len(set(e.get('hostname', 'unknown') for e in events)),
            "unique_ips": len(set(e.get('ip', 'unknown') for e in events)),
            "status_counts": {},
            "latest_event": events[-1] if events else None
        }
        
        # Contar por status
        for event in events:
            status = event.get('status', 'unknown')
            stats['status_counts'][status] = stats['status_counts'].get(status, 0) + 1
        
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    """Página de inicio del servidor de tracking"""
    return """
    <html>
    <head>
        <title>LoadTest Enterprise - Tracking Server</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #1a1a1a; color: #00ff00; }
            h1 { color: #00ff00; }
            .endpoint { background: #2a2a2a; padding: 10px; margin: 10px 0; border-left: 3px solid #00ff00; }
            code { background: #000; padding: 2px 5px; }
        </style>
    </head>
    <body>
        <h1>🔒 LoadTest Enterprise - Tracking Server</h1>
        <p>Servidor de tracking activo</p>
        <h2>Endpoints disponibles:</h2>
        <div class="endpoint">
            <strong>POST /track</strong> - Recibir datos de tracking
        </div>
        <div class="endpoint">
            <strong>GET /events</strong> - Obtener todos los eventos
        </div>
        <div class="endpoint">
            <strong>GET /events/latest?limit=50</strong> - Últimos N eventos
        </div>
        <div class="endpoint">
            <strong>GET /events/&lt;status&gt;</strong> - Eventos por status
        </div>
        <div class="endpoint">
            <strong>GET /stats</strong> - Estadísticas de tracking
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║     LoadTest Enterprise - Tracking Server                    ║
    ║                                                              ║
    ║  🌐 Servidor: http://localhost:8080                          ║
    ║  📊 Endpoint: http://localhost:8080/track                     ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=8080, debug=False)

