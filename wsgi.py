#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📁 Ruta: /app/wsgi.py  
📄 Nombre: wsgi.py
🏗️ Propósito: WSGI Entry Point corregido para Railway ERP13 Enterprise v3.1
⚡ Performance: Optimizado para Gunicorn multi-worker
🔒 Seguridad: Sin errores de sintaxis, configuración robusta
"""

import os
import sys
import logging
from datetime import datetime

# Configuración de path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Configuración logging
def setup_wsgi_logging():
    logger = logging.getLogger('wsgi')
    logger.setLevel(logging.INFO)
    
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    if not logger.handlers:
        logger.addHandler(handler)
    
    return logger

wsgi_logger = setup_wsgi_logging()

# Configurar variables de entorno
def configure_railway_environment():
    defaults = {
        'FLASK_ENV': 'production',
        'PYTHONPATH': '/app',
        'PORT': '8080',
        'WEB_CONCURRENCY': '2'
    }
    
    for key, value in defaults.items():
        if key not in os.environ:
            os.environ[key] = value
    
    wsgi_logger.info(f"Environment: {os.environ.get('FLASK_ENV')}")
    wsgi_logger.info(f"Workers: {os.environ.get('WEB_CONCURRENCY')}")
    wsgi_logger.info(f"Port: {os.environ.get('PORT')}")

configure_railway_environment()

# Importar y crear aplicación
try:
    wsgi_logger.info("🚀 ERP13E Enterprise - WSGI application initializing")
    
    from main_fixed import create_erp_application
    
    application = create_erp_application()
    
    if application is None:
        raise RuntimeError("Application creation returned None")
    
    wsgi_logger.info("🚀 ERP13E Enterprise - WSGI application initialized successfully")
    wsgi_logger.info(f"Environment: {application.config.get('ENV', 'unknown')}")
    wsgi_logger.info(f"Workers: {os.environ.get('WEB_CONCURRENCY', 'auto')}")
    wsgi_logger.info("Health checks available: /health, /health/wsgi, /health/detailed")
    
except ImportError as import_error:
    wsgi_logger.error(f"❌ Failed to import main application: {import_error}")
    sys.exit(1)
except Exception as creation_error:
    wsgi_logger.error(f"❌ Failed to create WSGI application: {creation_error}")
    sys.exit(1)

# Exportar aplicación
app = application

# Verificación
if __name__ == '__main__':
    wsgi_logger.info("⚠️ WSGI module loaded directly")
    wsgi_logger.info(f"✅ Application object created: {type(application)}")
    
    try:
        with application.test_client() as client:
            response = client.get('/health')
            wsgi_logger.info(f"✅ Health check test: {response.status_code}")
    except Exception as test_error:
        wsgi_logger.error(f"❌ Application test failed: {test_error}")
else:
    wsgi_logger.info("✅ WSGI module imported successfully")
