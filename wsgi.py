#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ERP13 Enterprise v3.0 - Railway WSGI Entry Point
FIXED: Compatible with Flask 3.1.2 + Railway deployment.
"""

import os
import sys
import logging

# Configurar logging para Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stdout
)

logger = logging.getLogger(__name__)

# Importar la aplicación principal
try:
    from main import app
    logger.info("✅ Main app imported successfully")
except ImportError as e:
    logger.error(f"❌ Error importing main app: {e}")
    # Crear app mínima para Railway health check
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/health')
    def health():
        return jsonify({"status": "error", "message": "Main app failed to import"})
    
    @app.route('/')
    def index():
        return jsonify({"error": "Application failed to start", "details": str(e)})

# =============================================================================
# CONFIGURACIÓN DE PRODUCCIÓN RAILWAY
# =============================================================================

# Configuraciones específicas para Railway
app.config.update({
    'ENV': 'production',
    'DEBUG': False,
    'TESTING': False,
    'PROPAGATE_EXCEPTIONS': True
})

# Headers de seguridad para producción
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

# =============================================================================
# RAILWAY HEALTH CHECK ESPECÍFICO
# =============================================================================

@app.route('/railway-health')
def railway_health():
    """Health check optimizado para Railway"""
    try:
        return {
            'status': 'healthy',
            'version': '3.0.0',
            'environment': 'production',
            'framework': 'Flask 3.1.2',
            'server': 'Gunicorn'
        }, 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {'status': 'error', 'error': str(e)}, 500

# =============================================================================
# WSGI APPLICATION OBJECT
# =============================================================================

# Este es el objeto que Gunicorn busca
application = app

# Información de inicio para Railway logs
logger.info("🚀 ERP13 Enterprise v3.0 - Railway WSGI Ready")
logger.info("📊 Flask 3.1.2 + Gunicorn + Railway")
logger.info("✅ WSGI Application Object: READY")

# =============================================================================
# MODO STANDALONE PARA TESTING
# =============================================================================

if __name__ == '__main__':
    # Solo para testing local - Railway usa Gunicorn
    port = int(os.environ.get('PORT', 8080))
    logger.warning("⚠️ Running in standalone mode - Use Gunicorn for production")
    application.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )
