#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ERP13 Enterprise WSGI Entry Point - Railway Compatible
Corregido: Sin conflictos de rutas, manejo seguro de fallback
"""

import os
import sys
import logging
from datetime import datetime

# =============================================================================
# CONFIGURACIÓN DE LOGGING
# =============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stdout
)

logger = logging.getLogger('ERP13_WSGI')

# =============================================================================
# VARIABLES DE ENTORNO
# =============================================================================
PORT = int(os.environ.get('PORT', 8080))
WORKERS = int(os.environ.get('WEB_CONCURRENCY', 2))
ENV = os.environ.get('FLASK_ENV', 'production')

logger.info(f"🌐 Environment: {ENV}")
logger.info(f"⚙️ Workers: {WORKERS}")
logger.info(f"🔌 Port: {PORT}")
logger.info("🚀 ERP13E Enterprise - WSGI application initializing")

# =============================================================================
# IMPORTACIÓN SEGURA DE LA APLICACIÓN
# =============================================================================

def create_fallback_app(error_msg):
    """Crear aplicación de fallback en caso de error"""
    from flask import Flask, jsonify
    
    fallback_app = Flask(__name__)
    
    @fallback_app.route('/health')
    def fallback_health():
        return jsonify({
            'status': 'degraded',
            'message': 'Main application failed to load',
            'error': str(error_msg),
            'timestamp': datetime.utcnow().isoformat(),
            'version': 'wsgi-fallback-1.0'
        }), 503
    
    @fallback_app.route('/')
    def fallback_index():
        return jsonify({
            'status': 'error',
            'message': 'ERP13 Enterprise is temporarily unavailable',
            'error': 'Application startup failed',
            'support': 'Check logs for details'
        }), 503
    
    @fallback_app.after_request
    def add_fallback_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Server'] = 'ERP13E-Fallback'
        return response
    
    return fallback_app

# Intentar importar la aplicación principal
application = None

try:
    from main import app as main_app
    logger.info("✅ Main application imported successfully")
    
    if main_app is None:
        raise ValueError("Main application is None")
    
    # Usar la aplicación principal
    application = main_app
    
    # Configuraciones para producción
    application.config.update({
        'ENV': ENV,
        'DEBUG': False,
        'TESTING': False,
        'PROPAGATE_EXCEPTIONS': True
    })
    
    logger.info("✅ Application configured for production")
    
except ImportError as import_error:
    logger.error(f"❌ Failed to import main application: {import_error}")
    application = create_fallback_app(import_error)
    logger.info("🔄 Fallback application created due to import error")
    
except Exception as general_error:
    logger.error(f"❌ Critical error during application setup: {general_error}")
    application = create_fallback_app(general_error)
    logger.info("🚨 Fallback application created due to critical error")

# =============================================================================
# AGREGAR HEALTH CHECKS ADICIONALES SOLO SI ES LA APP PRINCIPAL
# =============================================================================

def add_additional_health_checks():
    """Agregar health checks adicionales solo a la aplicación principal"""
    try:
        # Verificar si tenemos la aplicación principal (no fallback)
        if hasattr(application, 'config') and application.config.get('ENV'):
            
            @application.route('/health/wsgi')
            def wsgi_health():
                """Health check específico para WSGI layer"""
                try:
                    return {
                        'status': 'healthy',
                        'component': 'wsgi',
                        'port': PORT,
                        'workers': WORKERS,
                        'environment': ENV,
                        'timestamp': datetime.utcnow().isoformat(),
                        'version': 'ERP13E-WSGI-3.1'
                    }, 200
                except Exception as health_error:
                    logger.error(f"WSGI health check failed: {health_error}")
                    return {
                        'status': 'error',
                        'component': 'wsgi',
                        'error': str(health_error),
                        'timestamp': datetime.utcnow().isoformat()
                    }, 500
            
            @application.route('/health/detailed')
            def detailed_health():
                """Health check detallado"""
                try:
                    try:
                        import psutil
                        memory = psutil.virtual_memory()
                        cpu_percent = psutil.cpu_percent(interval=0.1)
                        
                        system_metrics = {
                            'memory_percent': round(memory.percent, 2),
                            'memory_available_mb': round(memory.available / (1024 * 1024), 2),
                            'cpu_percent': round(cpu_percent, 2)
                        }
                    except ImportError:
                        system_metrics = 'psutil_not_available'
                    
                    return {
                        'status': 'healthy',
                        'timestamp': datetime.utcnow().isoformat(),
                        'system': system_metrics,
                        'application': {
                            'environment': ENV,
                            'port': PORT,
                            'workers': WORKERS,
                            'flask_version': getattr(application, '__version__', 'unknown')
                        }
                    }, 200
                    
                except Exception as detailed_error:
                    logger.error(f"Detailed health check failed: {detailed_error}")
                    return {
                        'status': 'degraded',
                        'error': str(detailed_error),
                        'timestamp': datetime.utcnow().isoformat()
                    }, 500
            
            @application.route('/metrics')
            def metrics():
                """Endpoint de métricas"""
                try:
                    return {
                        'service': 'ERP13E',
                        'version': '3.1',
                        'environment': ENV,
                        'workers': WORKERS,
                        'port': PORT,
                        'timestamp': datetime.utcnow().isoformat()
                    }, 200
                except Exception as metrics_error:
                    logger.error(f"Metrics failed: {metrics_error}")
                    return {'error': str(metrics_error)}, 500
            
            logger.info("✅ Additional health checks registered")
            
    except Exception as health_setup_error:
        logger.warning(f"Could not add additional health checks: {health_setup_error}")

# Agregar health checks si es posible
add_additional_health_checks()

# =============================================================================
# CONFIGURACIÓN FINAL
# =============================================================================

# Headers de seguridad
@application.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY' 
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Server'] = 'ERP13E-Enterprise'
    return response

# Log final
logger.info("✅ WSGI application ready")
logger.info(f"✅ Application type: {type(application).__name__}")
logger.info("✅ Health checks: /health, /health/wsgi, /health/detailed, /metrics")

# =============================================================================
# PUNTO DE ENTRADA PARA GUNICORN
# =============================================================================

if __name__ == "__main__":
    logger.warning("⚠️ Running standalone - Use Gunicorn for production")
    application.run(host='0.0.0.0', port=PORT, debug=False)
