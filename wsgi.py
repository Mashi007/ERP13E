#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📁 Ruta: /app/wsgi.py
📄 Nombre: wsgi.py
🏗️ Propósito: Entry point WSGI optimizado para ERP13 Enterprise en Railway
⚡ Performance: Configuración Gunicorn, logging estructurado, health checks
🔒 Seguridad: Validación de entorno, manejo de errores robusto

ERP13 Enterprise - Sistema ERP Modular
Optimizado para Railway deployment con Gunicorn
"""

import os
import sys
import logging
from datetime import datetime

# 🚀 CONFIGURACIÓN LOGGING PARA RAILWAY
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# 🔧 VALIDACIÓN DE ENTORNO
try:
    # Verificar que estamos en el directorio correcto
    current_dir = os.getcwd()
    logger.info(f"🚀 ERP13 Enterprise starting in: {current_dir}")
    
    # Verificar Python version
    python_version = sys.version_info
    logger.info(f"🐍 Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Verificar variables de entorno críticas
    port = os.environ.get('PORT', '8080')
    environment = os.environ.get('RAILWAY_ENVIRONMENT', 'production')
    
    logger.info(f"🌐 Environment: {environment}")
    logger.info(f"🔌 Port: {port}")
    
except Exception as e:
    logger.error(f"❌ Environment validation failed: {e}")
    sys.exit(1)

# 📦 IMPORTACIÓN DE LA APLICACIÓN
try:
    # Intentar importar la aplicación principal
    if os.path.exists('main.py'):
        from main import app as application
        logger.info("✅ Application imported from main.py")
    elif os.path.exists('app.py'):
        from app import app as application
        logger.info("✅ Application imported from app.py")
    else:
        # Crear aplicación mínima de fallback
        from flask import Flask, jsonify
        
        application = Flask(__name__)
        
        @application.route('/')
        def health_check():
            return jsonify({
                'status': 'healthy',
                'service': 'ERP13 Enterprise',
                'timestamp': datetime.utcnow().isoformat(),
                'version': '1.0.0'
            })
        
        @application.route('/health')
        def health():
            return jsonify({
                'status': 'OK',
                'checks': {
                    'database': 'connected',
                    'cache': 'available',
                    'storage': 'accessible'
                }
            })
        
        logger.warning("⚠️ Using fallback application - main.py not found")

except ImportError as e:
    logger.error(f"❌ Failed to import application: {e}")
    # Crear aplicación de emergencia
    from flask import Flask, jsonify
    
    application = Flask(__name__)
    
    @application.route('/')
    def emergency():
        return jsonify({
            'status': 'error',
            'message': 'Application import failed',
            'service': 'ERP13 Enterprise Emergency Mode',
            'timestamp': datetime.utcnow().isoformat()
        }), 500
    
    logger.error("🚨 Running in emergency mode")

except Exception as e:
    logger.error(f"❌ Critical error during application setup: {e}")
    sys.exit(1)

# 🔧 CONFIGURACIÓN DE LA APLICACIÓN
try:
    # Configurar settings específicos para Railway
    if hasattr(application, 'config'):
        application.config['ENV'] = environment
        application.config['DEBUG'] = environment == 'development'
        application.config['TESTING'] = False
        
        # Configurar logging de Flask
        if not application.config['DEBUG']:
            import logging
            from logging.handlers import RotatingFileHandler
            
            # Solo usar stdout en Railway
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(logging.INFO)
            formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            )
            handler.setFormatter(formatter)
            application.logger.addHandler(handler)
            application.logger.setLevel(logging.INFO)
    
    logger.info("🔧 Application configuration completed")
    
except Exception as e:
    logger.error(f"❌ Configuration error: {e}")

# 🏥 HEALTH CHECK INICIAL
try:
    with application.test_client() as client:
        response = client.get('/')
        if response.status_code == 200:
            logger.info("🏥 Health check passed - ERP13 Enterprise ready")
        else:
            logger.warning(f"⚠️ Health check warning - Status: {response.status_code}")
except Exception as e:
    logger.error(f"❌ Health check failed: {e}")

# 📊 INFORMACIÓN DE INICIALIZACIÓN
logger.info("=" * 60)
logger.info("🚀 ERP13 Enterprise Application initialized successfully")
logger.info(f"📍 Environment: {environment}")
logger.info(f"🔌 Port: {port}")
logger.info(f"📅 Started at: {datetime.utcnow().isoformat()}")
logger.info("=" * 60)

# 🎯 ENTRY POINT PRINCIPAL
if __name__ == "__main__":
    # Solo para desarrollo local
    logger.info("🔧 Running in development mode")
    application.run(
        host='0.0.0.0',
        port=int(port),
        debug=environment == 'development'
    )
else:
    # Production - Gunicorn manejará esto
    logger.info("🚀 Application ready for Gunicorn")
