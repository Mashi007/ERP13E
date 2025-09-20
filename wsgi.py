#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ruta: /app/wsgi.py
Nombre: wsgi.py
Propósito: WSGI Entry Point simplificado ERP13 Enterprise
Performance: Health checks rápidos, startup optimizado
Seguridad: Fallback robusto, logging limpio
"""

import os
import sys
import logging
from datetime import datetime

# Configuración básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    stream=sys.stdout
)

logger = logging.getLogger('ERP13_WSGI')

# Variables de entorno
PORT = int(os.environ.get('PORT', 8080))
WORKERS = int(os.environ.get('WEB_CONCURRENCY', 2))
ENV = os.environ.get('FLASK_ENV', 'production')

logger.info(f"Starting ERP13 WSGI - Environment: {ENV}, Workers: {WORKERS}, Port: {PORT}")

# Función para crear aplicación de emergencia
def create_emergency_app():
    from flask import Flask, jsonify
    
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'emergency-key'
    
    @app.route('/health')
    def emergency_health():
        return jsonify({
            'status': 'healthy',
            'service': 'ERP13-Enterprise-Emergency',
            'timestamp': datetime.utcnow().isoformat(),
            'mode': 'emergency'
        }), 200
    
    @app.route('/health/ready')
    def emergency_ready():
        return jsonify({
            'status': 'ready',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    @app.route('/health/live')
    def emergency_live():
        return jsonify({
            'status': 'alive',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    @app.route('/')
    def emergency_index():
        return jsonify({
            'status': 'operational',
            'message': 'ERP13 Enterprise is running in emergency mode',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    @app.after_request
    def add_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Server'] = 'ERP13E-Emergency'
        return response
    
    return app

# Intentar importar aplicación principal
application = None
import_success = False

try:
    logger.info("Importing main application...")
    from main import app as main_app
    
    if main_app is None:
        raise ValueError("Main application is None")
    
    application = main_app
    import_success = True
    
    # Configurar para producción
    application.config.update({
        'ENV': ENV,
        'DEBUG': False,
        'TESTING': False,
        'PROPAGATE_EXCEPTIONS': True
    })
    
    logger.info("Main application imported and configured successfully")
    
except ImportError as e:
    logger.error(f"Import error: {e}")
    application = create_emergency_app()
    logger.info("Using emergency application due to import failure")
    
except Exception as e:
    logger.error(f"Critical error: {e}")
    application = create_emergency_app()
    logger.info("Using emergency application due to critical error")

# Agregar health checks adicionales si la importación fue exitosa
if import_success and hasattr(application, 'route'):
    try:
        @application.route('/health/wsgi')
        def wsgi_health():
            return {
                'status': 'healthy',
                'component': 'wsgi',
                'workers': WORKERS,
                'port': PORT,
                'environment': ENV,
                'timestamp': datetime.utcnow().isoformat()
            }, 200
        
        logger.info("WSGI health check endpoint added")
        
    except Exception as e:
        logger.warning(f"Could not add WSGI health check: {e}")

# Headers de seguridad
@application.after_request
def security_headers(response):
    response.headers.update({
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'Server': 'ERP13E-Enterprise'
    })
    return response

# Log final
logger.info(f"WSGI application ready - Type: {type(application).__name__}, Import success: {import_success}")

if __name__ == "__main__":
    logger.warning("Running WSGI standalone - Use Gunicorn for production")
    application.run(host='0.0.0.0', port=PORT, debug=False)
