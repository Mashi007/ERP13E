#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📁 Ruta: /health.py
📄 Nombre: health.py
🏗️ Propósito: Health check independiente para Railway
⚡ Performance: Endpoint ultra-simple sin dependencias
🔒 Seguridad: Sin exposición de información sensible

ERP13 Enterprise - Health Check Service
"""

from flask import Blueprint, jsonify
from datetime import datetime, timezone
import os

# 🏥 BLUEPRINT SIMPLE PARA HEALTH CHECK
health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
def health():
    """
    🏥 Health check básico para Railway
    Sin dependencias externas para máxima confiabilidad
    """
    try:
        return jsonify({
            'status': 'healthy',
            'service': 'ERP13 Enterprise',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'version': '1.0.0',
            'environment': os.environ.get('RAILWAY_ENVIRONMENT', 'production')
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'service': 'ERP13 Enterprise',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500

@health_bp.route('/health/ready')
def readiness():
    """
    🔄 Readiness probe - indica si la app está lista para recibir tráfico
    """
    return jsonify({
        'status': 'ready',
        'service': 'ERP13 Enterprise',
        'timestamp': datetime.now(timezone.utc).isoformat()
    }), 200

@health_bp.route('/health/live')
def liveness():
    """
    💗 Liveness probe - indica si la app está viva
    """
    return jsonify({
        'status': 'alive',
        'service': 'ERP13 Enterprise', 
        'timestamp': datetime.now(timezone.utc).isoformat()
    }), 200
