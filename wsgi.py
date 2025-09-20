#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📁 Ruta: /app/wsgi.py
📄 Nombre: wsgi.py
🏗️ Propósito: WSGI Entry Point consolidado ERP13 Enterprise v3.1
⚡ Performance: Gunicorn optimizado, health checks nativos, manejo de errores robusto
🔒 Seguridad: Fallback seguro, logging auditado, headers de seguridad

WSGI ENTERPRISE ENTRY POINT:
- Importación segura de aplicación principal
- Fallback automático en caso de errores
- Health checks independientes para Railway
- Configuración production-ready
- Logging estructurado para debugging
"""

import os
import sys
import logging
from datetime import datetime

# ============================================================================
# CONFIGURACIÓN DE LOGGING ENTERPRISE
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stdout
)

logger = logging.getLogger('ERP13_WSGI')

# ============================================================================
# VARIABLES DE ENTORNO RAILWAY
# ============================================================================
PORT = int(os.environ.get('PORT', 8080))
WORKERS = int(os.environ.get('WEB_CONCURRENCY', 2))
ENV = os.environ.get('FLASK_ENV', 'production')

logger.info("🚀 ERP13 Enterprise WSGI - Iniciando aplicación")
logger.info(f"🌐 Environment: {ENV}")
logger.info(f"⚙️ Workers: {WORKERS}")
logger.info(f"🔌 Port: {PORT}")

# ============================================================================
# APLICACIÓN DE FALLBACK ENTERPRISE
# ============================================================================
def create_emergency_app():
    """Crear aplicación de emergencia standalone"""
    from flask import Flask, jsonify
    
    emergency_app = Flask(__name__)
    emergency_app.config['SECRET_KEY'] = 'emergency-fallback-key'
    
    @emergency_app.route('/health')
    def emergency_health():
        return jsonify({
            'status': 'degraded',
            'message': 'Running in emergency mode',
            'service': 'ERP13-Enterprise-Emergency',
            'timestamp': datetime.utcnow().isoformat(),
            'mode': 'fallback'
        }), 503
    
    @emergency_app.route('/health/ready')
    def emergency_ready():
        return jsonify({
            'status': 'not_ready',
            'message': 'Main application failed to start',
            'timestamp': datetime.utcnow().isoformat()
        }), 503
    
    @emergency_app.route('/health/live')
    def emergency_live():
        return jsonify({
            'status': 'alive',
            'mode': 'emergency',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    @emergency_app.route('/')
    def emergency_index():
        return jsonify({
            'status': 'emergency_mode',
            'message': 'ERP13 Enterprise is starting up, please try again in a moment',
            'service': 'ERP13-Enterprise',
            'timestamp': datetime.utcnow().isoformat(),
            'retry_after': 30
        }), 503
    
    @emergency_app.errorhandler(404)
    def emergency_404(error):
        return jsonify({
            'error': 'Not found in emergency mode',
            'message': 'Service is temporarily unavailable',
            'status': 503
        }), 503
    
    @emergency_app.after_request
    def emergency_headers(response):
        response.headers.update({
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'Server': 'ERP13E-Emergency',
            'Retry-After': '30'
        })
        return response
    
    logger.info("🚨 Emergency application created")
    return emergency_app

# ============================================================================
# IMPORTACIÓN SEGURA DE LA APLICACIÓN PRINCIPAL
# ============================================================================
application = None
import_success = False

try:
    # Intentar importar la aplicación principal
    logger.info("📥 Attempting to import main application...")
    
    from main import app as main_application
    
    if main_application is None:
        raise ValueError("Main application is None")
    
    # Verificar que la aplicación es válida
    if not hasattr(main_application, 'config'):
        raise ValueError("Invalid Flask application object")
    
    # Usar la aplicación principal
    application = main_application
    import_success = True
    
    logger.info("✅ Main application imported successfully")
    
    # Configuraciones específicas para WSGI/Gunicorn
    application.config.update({
        'ENV': ENV,
        'DEBUG': False,
        'TESTING': False,
        'PROPAGATE_EXCEPTIONS': True,
        'PREFERRED_URL_SCHEME': 'https' if ENV == 'production' else 'http'
    })
    
    logger.info("✅ Application configured for WSGI deployment")
    
except ImportError as import_error:
    logger.error(f"❌ ImportError: {import_error}")
    logger.error("📋 Available modules in current directory:")
    try:
        for item in os.listdir('.'):
            if item.endswith('.py'):
                logger.error(f"   - {item}")
    except Exception:
        pass
    
    application = create_emergency_app()
    logger.info("🔄 Using emergency application due to import failure")
    
except Exception as general_error:
    logger.error(f"❌ Critical error during application setup: {general_error}")
    logger.error(f"📍 Error type: {type(general_error).__name__}")
    
    application = create_emergency_app()
    logger.info("🚨 Using emergency application due to critical error")

# ============================================================================
# HEALTH CHECKS WSGI LAYER
# ============================================================================
def add_wsgi_health_checks():
    """Agregar health checks específicos del layer WSGI"""
    try:
        if import_success and hasattr(application, 'route'):
            
            @application.route('/health/wsgi')
            def wsgi_health():
                """Health check específico para WSGI layer"""
                try:
                    return {
                        'status': 'healthy',
                        'component': 'wsgi',
                        'gunicorn': {
                            'workers': WORKERS,
                            'port': PORT,
                            'environment': ENV
                        },
                        'application': {
                            'imported': import_success,
                            'type': type(application).__name__,
                            'routes': len(application.url_map._rules)
                        },
                        'timestamp': datetime.utcnow().isoformat(),
                        'version': 'ERP13E-WSGI-3.1'
                    }, 200
                except Exception as e:
                    logger.error(f"WSGI health check failed: {e}")
                    return {
                        'status': 'error',
                        'component': 'wsgi',
                        'error': str(e),
                        'timestamp': datetime.utcnow().isoformat()
                    }, 500
            
            @application.route('/health/layers')
            def layers_health():
                """Health check de todas las capas"""
                layers = {
                    'wsgi': 'healthy',
                    'flask': 'healthy' if import_success else 'degraded',
                    'application': 'healthy' if import_success else 'emergency',
                    'gunicorn': 'configured',
                    'railway': 'connected'
                }
                
                overall_status = 'healthy' if all(
                    status in ['healthy', 'configured', 'connected'] 
                    for status in layers.values()
                ) else 'degraded'
                
                return {
                    'status': overall_status,
                    'layers': layers,
                    'timestamp': datetime.utcnow().isoformat()
                }, 200 if overall_status == 'healthy' else 503
            
            logger.info("✅ WSGI health checks added successfully")
            
    except Exception as e:
        logger.warning(f"Could not add WSGI health checks: {e}")

# Agregar health checks si es posible
add_wsgi_health_checks()

# ============================================================================
# MIDDLEWARE WSGI ENTERPRISE
# ============================================================================
@application.after_request
def wsgi_security_headers(response):
    """Headers de seguridad para WSGI layer"""
    response.headers.update({
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Server': 'ERP13E-Enterprise-WSGI',
        'X-Powered-By': 'ERP13Enterprise'
    })
    
    # Headers específicos para Railway
    if ENV == 'production':
        response.headers.update({
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'"
        })
    
    return response

# ============================================================================
# LOGGING DE INICIALIZACIÓN WSGI
# ============================================================================
logger.info("✅ WSGI application ready for deployment")
logger.info(f"📊 Application type: {type(application).__name__}")
logger.info(f"🔧 Import success: {import_success}")

if import_success:
    logger.info(f"📋 Total routes: {len(application.url_map._rules)}")
    logger.info("🏥 Health endpoints: /health, /health/ready, /health/live, /health/wsgi, /health/layers")
else:
    logger.info("🚨 Running in emergency mode - limited functionality")

logger.info("🛡️ Security headers: Configured")
logger.info("🚀 Ready for Gunicorn deployment")

# ============================================================================
# PUNTO DE ENTRADA PARA GUNICORN
# ============================================================================
if __name__ == "__main__":
    logger.warning("⚠️ Running WSGI standalone - Use Gunicorn for production")
    logger.info(f"🔌 Starting development server on port {PORT}")
    
    if application:
        application.run(
            host='0.0.0.0',
            port=PORT,
            debug=False,
            threaded=True
        )
    else:
        logger.error("❌ No application available to run")
        sys.exit(1)
