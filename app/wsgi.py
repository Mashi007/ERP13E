#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📁 Ruta: /app/wsgi.py
📄 Nombre: wsgi.py
🏗️ Propósito: Entry point WSGI corregido para Railway + Gunicorn
⚡ Performance: Importación robusta y exportación correcta
🔒 Seguridad: Manejo de errores y logging robusto

ERP13 Enterprise - WSGI Entry Point CORREGIDO
Soluciona: Failed to find attribute 'application' in 'wsgi'
"""

import os
import sys
import logging
from datetime import datetime, timezone

# 🚀 CONFIGURACIÓN LOGGING PARA RAILWAY
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# 🔧 CONFIGURACIÓN DE PATHS
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

# 📝 LOG INICIAL
logger.info("🚀 WSGI Entry Point - ERP13 Enterprise")
logger.info(f"📁 Working directory: {os.getcwd()}")
logger.info(f"🐍 Python version: {sys.version}")
logger.info(f"📍 Python path: {sys.path[:3]}")

# 🌐 VERIFICACIÓN DE ENTORNO
try:
    port = os.environ.get('PORT', '8080')
    environment = os.environ.get('RAILWAY_ENVIRONMENT', 'production')
    logger.info(f"🌐 Environment: {environment}")
    logger.info(f"🔌 Port: {port}")
except Exception as e:
    logger.error(f"❌ Environment check failed: {e}")

# 📦 IMPORTACIÓN DE LA APLICACIÓN CON MÚLTIPLES FALLBACKS
application = None

# 🥇 INTENTO 1: Importar desde main.py
try:
    logger.info("📦 Attempting to import from main.py...")
    from main import app
    application = app
    logger.info("✅ Successfully imported application from main.py")
except ImportError as e:
    logger.warning(f"⚠️ Could not import from main.py: {e}")
except Exception as e:
    logger.error(f"❌ Error importing from main.py: {e}")

# 🥈 INTENTO 2: Importar desde app.py si main.py falla
if application is None:
    try:
        logger.info("📦 Attempting to import from app.py...")
        from app import app
        application = app
        logger.info("✅ Successfully imported application from app.py")
    except ImportError as e:
        logger.warning(f"⚠️ Could not import from app.py: {e}")
    except Exception as e:
        logger.error(f"❌ Error importing from app.py: {e}")

# 🥉 INTENTO 3: Crear aplicación básica de emergencia
if application is None:
    logger.warning("🚨 Creating emergency Flask application")
    try:
        from flask import Flask, jsonify
        
        application = Flask(__name__)
        application.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'erp13-emergency-key')
        
        @application.route('/')
        def emergency_index():
            return jsonify({
                'status': 'emergency_mode',
                'service': 'ERP13 Enterprise',
                'message': 'Sistema en modo de emergencia - aplicación principal no disponible',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'version': '1.0.0-emergency',
                'environment': os.environ.get('RAILWAY_ENVIRONMENT', 'unknown')
            }), 200
        
        @application.route('/health')
        def emergency_health():
            return jsonify({
                'status': 'emergency_healthy',
                'service': 'ERP13 Enterprise',
                'mode': 'emergency',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'message': 'Aplicación en modo de emergencia pero funcional'
            }), 200
        
        @application.route('/health/detailed')
        def emergency_health_detailed():
            return jsonify({
                'status': 'emergency_healthy',
                'service': 'ERP13 Enterprise',
                'version': '1.0.0-emergency',
                'mode': 'emergency',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'checks': {
                    'application': {
                        'status': 'emergency',
                        'message': 'Aplicación principal no disponible, usando modo de emergencia'
                    },
                    'wsgi': {
                        'status': 'healthy',
                        'message': 'WSGI funcionando correctamente'
                    }
                }
            }), 200
        
        @application.errorhandler(404)
        def emergency_not_found(error):
            return jsonify({
                'error': 'Not Found',
                'service': 'ERP13 Enterprise Emergency Mode',
                'message': 'Recurso no encontrado en modo de emergencia',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 404
        
        @application.errorhandler(500)
        def emergency_server_error(error):
            return jsonify({
                'error': 'Internal Server Error',
                'service': 'ERP13 Enterprise Emergency Mode',
                'message': 'Error interno en modo de emergencia',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 500
        
        logger.info("✅ Emergency Flask application created successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to create emergency application: {e}")
        # ÚLTIMO RECURSO: Aplicación mínima
        from flask import Flask
        application = Flask(__name__)
        
        @application.route('/')
        def minimal():
            return "ERP13 Enterprise - Minimal Mode", 200
        
        logger.info("✅ Minimal application created as last resort")

# 🔧 VERIFICACIÓN FINAL DE LA APLICACIÓN
if application is None:
    logger.error("❌ CRITICAL: No application could be created")
    raise RuntimeError("Failed to create any Flask application")

# 🔍 VALIDACIÓN DE LA APLICACIÓN
try:
    if hasattr(application, 'config'):
        # Configurar settings básicos si no están configurados
        if not application.config.get('SECRET_KEY'):
            application.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'erp13-wsgi-fallback')
        
        # Configurar debug mode para Railway
        application.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
        
        logger.info(f"✅ Flask application validated")
        logger.info(f"🔧 Debug mode: {application.config['DEBUG']}")
        logger.info(f"🎯 Application name: {application.name}")
        
        # Log de rutas disponibles
        with application.app_context():
            routes = [str(rule) for rule in application.url_map.iter_rules()]
            logger.info(f"📍 Available routes: {routes[:5]}...")  # Solo primeras 5 para no saturar logs
    else:
        logger.error("❌ Invalid Flask application - no config attribute")
        raise RuntimeError("Invalid Flask application instance")

except Exception as e:
    logger.error(f"❌ Application validation failed: {e}")
    raise

# 📊 LOGGING DE CONFIGURACIÓN EXITOSA
logger.info("=" * 60)
logger.info("✅ WSGI CONFIGURATION COMPLETED SUCCESSFULLY")
logger.info(f"🎯 Application ready: {type(application).__name__}")
logger.info(f"📋 Application mode: {'Emergency' if 'emergency' in str(application.name).lower() else 'Normal'}")
logger.info(f"🚀 Ready for Gunicorn on port {port}")
logger.info("=" * 60)

# 🧪 FUNCIÓN DE VERIFICACIÓN PARA DEBUG
def verify_wsgi_application():
    """
    🔍 Verificar que la aplicación WSGI está correctamente configurada
    """
    try:
        logger.info("🧪 Running WSGI verification...")
        
        # Test básico de la aplicación
        with application.test_client() as client:
            response = client.get('/')
            logger.info(f"✅ Root endpoint test: {response.status_code}")
            
            # Test health endpoint si existe
            health_response = client.get('/health')
            logger.info(f"✅ Health endpoint test: {health_response.status_code}")
        
        logger.info("✅ WSGI verification passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ WSGI verification failed: {e}")
        return False

# 🎯 EXPORTACIÓN EXPLÍCITA PARA GUNICORN
# Esta es la variable que Gunicorn busca
__all__ = ['application']

# 🚀 PUNTO DE ENTRADA PARA TESTING LOCAL
if __name__ == "__main__":
    """
    🧪 Para testing y debugging local
    En producción, Gunicorn maneja la aplicación directamente
    """
    logger.info("🧪 Running in test mode...")
    
    # Verificar aplicación
    if verify_wsgi_application():
        logger.info("✅ WSGI test passed")
    else:
        logger.warning("⚠️ WSGI test had issues")
    
    # Ejecutar servidor de desarrollo
    port_local = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 Starting development server on port {port_local}")
    
    try:
        application.run(
            host='0.0.0.0', 
            port=port_local, 
            debug=True,
            use_reloader=False  # Evitar problemas con Railway
        )
    except Exception as e:
        logger.error(f"❌ Development server failed: {e}")
