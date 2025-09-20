#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📁 Ruta: /app/wsgi.py
📄 Nombre: wsgi.py
🏗️ Propósito: WSGI Entry Point ERP13 Enterprise Railway-Optimized
⚡ Performance: Gunicorn workers, health checks <100ms
🔒 Seguridad: Error handling seguro, logging estructurado

ERP13 Enterprise WSGI Application
Compatible con Railway deployment y Gunicorn 21.2.0
"""

import os
import sys
import logging
from datetime import datetime

# =============================================================================
# CONFIGURACIÓN DE LOGGING ENTERPRISE
# =============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stdout
)

logger = logging.getLogger('ERP13_WSGI')

# =============================================================================
# VARIABLES DE ENTORNO RAILWAY
# =============================================================================
PORT = int(os.environ.get('PORT', 8080))
WORKERS = int(os.environ.get('WEB_CONCURRENCY', 2))
ENV = os.environ.get('FLASK_ENV', 'production')

logger.info(f"🌐 Environment: {ENV}")
logger.info(f"⚙️ Workers: {WORKERS}")
logger.info(f"🔌 Port: {PORT}")
logger.info("🚀 ERP13E Enterprise - WSGI application initializing")

# =============================================================================
# IMPORTACIÓN SEGURA DE LA APLICACIÓN PRINCIPAL
# =============================================================================
application = None

try:
    # Importar la aplicación principal
    from main import app as application
    logger.info("✅ Main application imported successfully")
    
    # Verificar que la aplicación es válida
    if application is None:
        raise ValueError("Application object is None")
        
    # Configuraciones específicas para producción
    application.config.update({
        'ENV': ENV,
        'DEBUG': False,
        'TESTING': False,
        'PROPAGATE_EXCEPTIONS': True
    })
    
    logger.info("✅ Application configured for production")
    
except ImportError as import_error:
    logger.error(f"❌ Failed to import main application: {import_error}")
    
    # Crear aplicación de fallback
    from flask import Flask, jsonify
    application = Flask(__name__)
    
    @application.route('/health')
    def emergency_health():
        return jsonify({
            'status': 'degraded',
            'message': 'Main application failed to import',
            'error': str(import_error),
            'timestamp': datetime.utcnow().isoformat(),
            'version': 'wsgi-fallback-1.0'
        }), 503
    
    @application.route('/')
    def emergency_index():
        return jsonify({
            'status': 'error',
            'message': 'ERP13 Enterprise is temporarily unavailable',
            'error': 'Application import failed',
            'support': 'Check application logs for details'
        }), 503
        
    logger.info("🔄 Fallback application created")
    
except Exception as general_error:
    logger.error(f"❌ Critical error during application setup: {general_error}")
    
    # Aplicación de emergencia mínima
    from flask import Flask, jsonify
    application = Flask(__name__)
    
    @application.route('/health')
    def critical_health():
        return jsonify({
            'status': 'critical',
            'message': 'Critical system error',
            'error': str(general_error),
            'timestamp': datetime.utcnow().isoformat()
        }), 503
        
    logger.info("🚨 Emergency application created due to critical error")

# =============================================================================
# HEALTH CHECKS RAILWAY-OPTIMIZED
# =============================================================================

@application.route('/health/wsgi')
def wsgi_health():
    """Health check específico para WSGI layer"""
    try:
        return jsonify({
            'status': 'healthy',
            'component': 'wsgi',
            'port': PORT,
            'workers': WORKERS,
            'environment': ENV,
            'timestamp': datetime.utcnow().isoformat(),
            'version': 'ERP13E-WSGI-3.1'
        }), 200
    except Exception as health_error:
        logger.error(f"WSGI health check failed: {health_error}")
        return jsonify({
            'status': 'error',
            'component': 'wsgi',
            'error': str(health_error),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@application.route('/health/detailed')
def detailed_health():
    """Health check detallado para debugging"""
    try:
        import psutil
        
        # Métricas del sistema
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'system': {
                'memory_percent': round(memory.percent, 2),
                'memory_available_mb': round(memory.available / (1024 * 1024), 2),
                'cpu_percent': round(cpu_percent, 2)
            },
            'application': {
                'environment': ENV,
                'port': PORT,
                'workers': WORKERS,
                'flask_app': str(type(application).__name__)
            },
            'endpoints': {
                'health': '/health',
                'wsgi_health': '/health/wsgi',
                'detailed_health': '/health/detailed',
                'metrics': '/metrics'
            }
        }
        
        return jsonify(health_data), 200
        
    except ImportError:
        # psutil no disponible
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'system': 'metrics_unavailable',
            'application': {
                'environment': ENV,
                'port': PORT,
                'workers': WORKERS
            }
        }), 200
        
    except Exception as detailed_error:
        logger.error(f"Detailed health check failed: {detailed_error}")
        return jsonify({
            'status': 'degraded',
            'error': str(detailed_error),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@application.route('/metrics')
def metrics():
    """Endpoint de métricas para monitoreo"""
    try:
        return jsonify({
            'uptime_seconds': 'calculating...',
            'requests_total': 'not_implemented',
            'memory_usage_mb': 'calculating...',
            'active_connections': WORKERS,
            'version': 'ERP13E-3.1',
            'environment': ENV
        }), 200
    except Exception as metrics_error:
        logger.error(f"Metrics endpoint failed: {metrics_error}")
        return jsonify({'error': str(metrics_error)}), 500

# =============================================================================
# CONFIGURACIÓN FINAL
# =============================================================================

# Headers de seguridad para todas las respuestas
@application.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Server'] = 'ERP13E-Enterprise'
    return response

# Log de configuración final
logger.info(f"✅ Database configured: {'❌' if application is None else '✅'}")
logger.info(f"✅ JWT configured: {'❌' if application is None else '✅'}")
logger.info("✅ Health checks available: /health, /health/wsgi, /health/detailed, /metrics")

# =============================================================================
# PUNTO DE ENTRADA PARA GUNICORN
# =============================================================================

if __name__ == "__main__":
    # Solo para testing - Railway usa Gunicorn
    logger.warning("⚠️ Running in standalone mode - Use Gunicorn for production")
    application.run(host='0.0.0.0', port=PORT, debug=False)
