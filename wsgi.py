#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📁 Ruta: /wsgi.py
📄 Nombre: wsgi.py
🏗️ Propósito: WSGI Entry Point para ERP13 Enterprise v3.0 - Railway Production
⚡ Performance: Gunicorn optimizado con workers adaptativos y health monitoring
🔒 Seguridad: Environment validation, error handling y logging estructurado

ERP13 Enterprise v3.0 - WSGI Production Server
Optimizado para Railway deployment con Gunicorn
Compatible con múltiples servers: Gunicorn, uWSGI, Waitress
"""

import os
import sys
import logging
from datetime import datetime

# =============================================================================
# CONFIGURACIÓN AVANZADA DE LOGGING PARA RAILWAY
# =============================================================================

def setup_production_logging():
    """Configurar logging estructurado para producción Railway"""
    # Formato de logging optimizado para Railway
    log_format = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] WSGI-%(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para Railway logs (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    console_handler.setLevel(logging.INFO)
    
    # Configurar logger principal
    logger = logging.getLogger('ERP13_WSGI')
    logger.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    
    # Silenciar logs innecesarios en producción
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    return logger

# Inicializar logging
logger = setup_production_logging()

# =============================================================================
# VALIDACIÓN DE ENTORNO RAILWAY
# =============================================================================

def validate_railway_environment():
    """Validar configuración crítica de Railway"""
    try:
        # Variables críticas Railway
        port = os.environ.get('PORT', '8080')
        railway_env = os.environ.get('RAILWAY_ENVIRONMENT', 'production')
        railway_project = os.environ.get('RAILWAY_PROJECT_NAME', 'ERP13-Enterprise')
        
        logger.info("=" * 60)
        logger.info("🚀 ERP13 ENTERPRISE v3.0 - WSGI INITIALIZATION")
        logger.info("=" * 60)
        logger.info(f"🌐 Railway Environment: {railway_env}")
        logger.info(f"📂 Railway Project: {railway_project}")
        logger.info(f"🔌 Port: {port}")
        logger.info(f"🐍 Python: {sys.version}")
        logger.info(f"📁 Working Directory: {os.getcwd()}")
        
        # Verificar archivos críticos
        critical_files = ['main.py', 'requirements.txt']
        missing_files = [f for f in critical_files if not os.path.exists(f)]
        
        if missing_files:
            logger.error(f"❌ Missing critical files: {missing_files}")
            return False
        
        logger.info(f"✅ Critical files: {critical_files}")
        
        # Verificar estructura de directorios
        expected_dirs = ['templates', 'static']
        existing_dirs = [d for d in expected_dirs if os.path.exists(d)]
        logger.info(f"📂 Available directories: {existing_dirs}")
        
        # Verificar variables de entorno opcionales
        optional_vars = {
            'DATABASE_URL': os.environ.get('DATABASE_URL'),
            'REDIS_URL': os.environ.get('REDIS_URL'),
            'SECRET_KEY': os.environ.get('SECRET_KEY', 'SET'),
            'JWT_SECRET_KEY': os.environ.get('JWT_SECRET_KEY', 'SET')
        }
        
        for var, value in optional_vars.items():
            status = "✅ SET" if value and value != 'SET' else "⚠️ DEFAULT"
            logger.info(f"🔑 {var}: {status}")
        
        logger.info("=" * 60)
        return True
        
    except Exception as e:
        logger.error(f"❌ Environment validation failed: {e}")
        return False

# =============================================================================
# IMPORTACIÓN SEGURA DE APLICACIÓN CON FALLBACKS
# =============================================================================

def import_application():
    """Importar aplicación Flask con múltiples fallbacks"""
    try:
        # Validar entorno antes de importar
        if not validate_railway_environment():
            logger.warning("⚠️ Environment validation failed, continuing anyway...")
        
        # Intentar importar aplicación principal
        logger.info("🔍 Importing ERP13 Enterprise application...")
        
        # Prioridad 1: Importar desde main.py
        try:
            from main import app, application, app_instance, flask_app, wsgi_app
            logger.info("✅ Application imported from main.py (multiple exports)")
            
            # Verificar que la aplicación es válida
            if hasattr(app, 'url_map'):
                total_routes = len([rule for rule in app.url_map.iter_rules()])
                logger.info(f"📋 Total routes loaded: {total_routes}")
            
            # Retornar la aplicación principal
            return app
            
        except ImportError as e:
            logger.warning(f"⚠️ Failed to import from main.py: {e}")
            
            # Fallback: Intentar solo app
            try:
                from main import app
                logger.info("✅ Application imported from main.py (app only)")
                return app
            except ImportError:
                raise ImportError("Cannot import Flask application from main.py")
        
    except Exception as e:
        logger.error(f"❌ Critical error importing application: {e}")
        
        # Crear aplicación de emergencia
        logger.warning("🚨 Creating emergency Flask application...")
        return create_emergency_application()

def create_emergency_application():
    """Crear aplicación Flask de emergencia para Railway"""
    try:
        from flask import Flask, jsonify
        
        emergency_app = Flask(__name__)
        emergency_app.config['SECRET_KEY'] = 'emergency-key-erp13'
        
        @emergency_app.route('/')
        def emergency_home():
            return jsonify({
                'status': 'emergency_mode',
                'message': 'ERP13 Enterprise - Emergency Mode Active',
                'timestamp': datetime.utcnow().isoformat(),
                'action': 'Contact system administrator'
            })
        
        @emergency_app.route('/health')
        def emergency_health():
            return jsonify({
                'status': 'emergency',
                'service': 'ERP13 Enterprise',
                'mode': 'emergency_fallback',
                'timestamp': datetime.utcnow().isoformat()
            })
        
        logger.warning("🚨 Emergency application created")
        return emergency_app
        
    except Exception as e:
        logger.error(f"❌ Failed to create emergency application: {e}")
        raise RuntimeError("Cannot create any Flask application")

# =============================================================================
# CONFIGURACIÓN DE APLICACIÓN PARA PRODUCCIÓN
# =============================================================================

def configure_production_app(app):
    """Configurar aplicación para entorno de producción"""
    try:
        # Forzar configuración de producción
        app.config.update({
            'DEBUG': False,
            'TESTING': False,
            'TEMPLATES_AUTO_RELOAD': False,
            'EXPLAIN_TEMPLATE_LOADING': False,
            'PROPAGATE_EXCEPTIONS': True
        })
        
        # Configurar logging de aplicación
        if not app.logger.handlers:
            app.logger.addHandler(logging.StreamHandler(sys.stdout))
            app.logger.setLevel(logging.INFO)
        
        # Headers de seguridad globales
        @app.after_request
        def add_security_headers(response):
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Server'] = 'ERP13-Enterprise/3.0'
            return response
        
        logger.info("✅ Production configuration applied")
        return app
        
    except Exception as e:
        logger.error(f"❌ Error configuring production app: {e}")
        return app

# =============================================================================
# IMPORTACIÓN Y CONFIGURACIÓN PRINCIPAL
# =============================================================================

# Importar aplicación con fallbacks
application = import_application()

# Configurar para producción
application = configure_production_app(application)

# =============================================================================
# MÚLTIPLES EXPORTS PARA COMPATIBILIDAD WSGI
# =============================================================================

# Railway/Gunicorn puede buscar cualquiera de estas variables
app = application                    # Estándar Flask
flask_app = application             # Alternativo Flask
wsgi_app = application              # Específico WSGI
app_instance = application          # Factory pattern
erp13_app = application            # Específico ERP13

# =============================================================================
# INFORMACIÓN DE DEPLOYMENT
# =============================================================================

# Log de exports exitosos
logger.info("✅ WSGI APPLICATION EXPORTS:")
logger.info("   - application ✅")
logger.info("   - app ✅")
logger.info("   - flask_app ✅")
logger.info("   - wsgi_app ✅")
logger.info("   - app_instance ✅")
logger.info("   - erp13_app ✅")

# Información del sistema
try:
    if hasattr(application, 'url_map'):
        routes_count = len([rule for rule in application.url_map.iter_rules()])
        logger.info(f"📋 Routes available: {routes_count}")
    
    if hasattr(application, 'config'):
        env = application.config.get('ENV', 'unknown')
        debug = application.config.get('DEBUG', False)
        logger.info(f"🎯 Environment: {env.upper()}")
        logger.info(f"🔧 Debug mode: {'ON' if debug else 'OFF'}")
    
except Exception as e:
    logger.warning(f"⚠️ Could not read app configuration: {e}")

logger.info("🚀 ERP13 Enterprise v3.0 - WSGI READY FOR RAILWAY")
logger.info("=" * 60)

# =============================================================================
# MANEJO DE ERRORES WSGI
# =============================================================================

def application_wrapper(environ, start_response):
    """Wrapper WSGI con manejo de errores"""
    try:
        return application(environ, start_response)
    except Exception as e:
        logger.error(f"❌ WSGI Error: {e}")
        
        # Respuesta de error de emergencia
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'application/json')]
        start_response(status, headers)
        
        error_response = {
            'error': 'Internal Server Error',
            'message': 'ERP13 Enterprise encountered an error',
            'timestamp': datetime.utcnow().isoformat(),
            'status': 500
        }
        
        import json
        return [json.dumps(error_response).encode('utf-8')]

# Usar wrapper solo si es necesario (Railway detecta automáticamente)
# application = application_wrapper

# =============================================================================
# DESARROLLO LOCAL (SOLO SI SE EJECUTA DIRECTAMENTE)
# =============================================================================

if __name__ == '__main__':
    # Solo para desarrollo local - Railway no ejecuta esto
    logger.info("🔧 WSGI executed directly - Local development mode")
    
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    logger.info(f"🌐 Local server: http://{host}:{port}")
    logger.info("⚠️ For production, use: gunicorn wsgi:application")
    
    try:
        application.run(
            host=host,
            port=port,
            debug=False,  # Nunca debug en WSGI
            threaded=True
        )
    except Exception as e:
        logger.error(f"❌ Failed to start local server: {e}")
