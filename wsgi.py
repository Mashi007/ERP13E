#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📁 Ruta: /app/wsgi.py
📄 Nombre: wsgi.py
🏗️ Propósito: WSGI Entry Point para Railway ERP13 Enterprise v3.1
⚡ Performance: Optimizado para Gunicorn multi-worker
🔒 Seguridad: Configuración de producción Railway-compatible

WSGI ENTRY POINT ENTERPRISE:
- Cumple especificaciones WSGI 1.0
- Compatible con Gunicorn workers
- Error handling robusto
- Logging estructurado para Railway
- Health check integration
"""

import os
import sys
import logging
from datetime import datetime

# ========== CONFIGURACIÓN PATH ==========
# Asegurar que el directorio actual está en el path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# ========== CONFIGURACIÓN LOGGING WSGI ==========
def setup_wsgi_logging():
    """Configurar logging específico para WSGI"""
    logger = logging.getLogger('wsgi')
    logger.setLevel(logging.INFO)
    
    # Handler para Railway logs
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    
    # Formato optimizado para Railway
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    if not logger.handlers:
        logger.addHandler(handler)
    
    return logger

# Inicializar logging WSGI
wsgi_logger = setup_wsgi_logging()

# ========== VARIABLES DE ENTORNO RAILWAY ==========
def configure_railway_environment():
    """Configurar variables de entorno específicas para Railway"""
    
    # Variables por defecto para Railway
    defaults = {
        'FLASK_ENV': 'production',
        'PYTHONPATH': '/app',
        'PORT': '8080',
        'WEB_CONCURRENCY': '2',
        'GUNICORN_WORKERS': '2',
        'GUNICORN_THREADS': '4',
        'GUNICORN_TIMEOUT': '120'
    }
    
    # Aplicar defaults solo si no están configuradas
    for key, value in defaults.items():
        if key not in os.environ:
            os.environ[key] = value
    
    wsgi_logger.info(f"🌐 Environment: {os.environ.get('FLASK_ENV')}")
    wsgi_logger.info(f"⚙️ Workers: {os.environ.get('WEB_CONCURRENCY')}")
    wsgi_logger.info(f"🔌 Port: {os.environ.get('PORT')}")

# Configurar entorno
configure_railway_environment()

# ========== IMPORTAR Y CREAR APLICACIÓN ==========
try:
    wsgi_logger.info("🚀 ERP13E Enterprise - WSGI application initializing")
    
    # Importar la función de creación de aplicación
    from main import create_erp_application, logger as main_logger
    
    # Crear la aplicación
    application = create_erp_application()
    
    # Verificar que la aplicación es válida
    if application is None:
        raise RuntimeError("Application creation returned None")
    
    # Registrar información de la aplicación
    wsgi_logger.info("🚀 ERP13E Enterprise - WSGI application initialized successfully")
    wsgi_logger.info(f"Environment: {application.config.get('ENV', 'unknown')}")
    wsgi_logger.info(f"Workers: {os.environ.get('WEB_CONCURRENCY', 'auto')}")
    wsgi_logger.info(f"Database configured: {'✅' if 'DATABASE_URL' in os.environ else '❌'}")
    wsgi_logger.info(f"JWT configured: {'✅' if 'SECRET_KEY' in application.config else '❌'}")
    wsgi_logger.info("Health checks available: /health, /health/wsgi, /health/detailed, /metrics")
    
except ImportError as e:
    wsgi_logger.error(f"❌ Failed to import main application: {e}")
    sys.exit(1)
except Exception as e:
    wsgi_logger.error(f"❌ Failed to create WSGI application: {e}")
    sys.exit(1)

# ========== WSGI APPLICATION WRAPPER ==========
def wsgi_application(environ, start_response):
    """
    WSGI Application Wrapper con error handling robusto
    
    Args:
        environ: WSGI environment dictionary
        start_response: WSGI start_response callable
    
    Returns:
        WSGI response iterator
    """
    try:
        # Llamar a la aplicación Flask
        return application(environ, start_response)
        
    except Exception as e:
        wsgi_logger.error(f"WSGI Application Error: {e}")
        
        # Respuesta de error en caso de fallo crítico
        status = '500 Internal Server Error'
        headers = [
            ('Content-Type', 'application/json'),
            ('X-ERP13-Error', 'wsgi-handler')
        ]
        
        start_response(status, headers)
        
        error_response = {
            'error': 'WSGI Handler Error',
            'status': 500,
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'ERP13-Enterprise-WSGI'
        }
        
        return [str(error_response).encode('utf-8')]

# ========== HEALTH CHECK WSGI ==========
def wsgi_health_check(environ, start_response):
    """Health check directo a nivel WSGI"""
    if environ.get('PATH_INFO') == '/wsgi-health':
        status = '200 OK'
        headers = [('Content-Type', 'application/json')]
        start_response(status, headers)
        
        response = {
            'status': 'healthy',
            'wsgi': 'operational',
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'ERP13-Enterprise-WSGI'
        }
        
        return [str(response).encode('utf-8')]
    else:
        return wsgi_application(environ, start_response)

# ========== EXPORTAR APLICACIÓN ==========
# Esta es la variable que Gunicorn buscará
app = application

# Verificación final
if __name__ == '__main__':
    wsgi_logger.info("⚠️ WSGI module loaded directly - Use Gunicorn for production")
    wsgi_logger.info(f"✅ Application object created: {type(application)}")
    wsgi_logger.info(f"✅ WSGI callable available: {callable(application)}")
    
    # Test básico de la aplicación
    try:
        with application.test_client() as client:
            response = client.get('/health')
            wsgi_logger.info(f"✅ Health check test: {response.status_code}")
    except Exception as e:
        wsgi_logger.error(f"❌ Application test failed: {e}")
else:
    wsgi_logger.info("✅ WSGI module imported successfully")
    wsgi_logger.info("🔧 Ready for Gunicorn deployment")

# ========== CONFIGURACIÓN GUNICORN RECOMENDADA ==========
"""
RAILWAY GUNICORN CONFIGURATION:

Command line para Railway:
gunicorn --bind 0.0.0.0:$PORT --workers $WEB_CONCURRENCY --worker-class gthread --threads 4 --timeout 120 --keep-alive 5 --max-requests 1000 --max-requests-jitter 100 --preload --access-logfile - --error-logfile - --log-level info wsgi:application

Variables de entorno Railway:
- PORT=8080 (auto-configurado por Railway)
- WEB_CONCURRENCY=2 (ajustar según plan)
- FLASK_ENV=production
- SECRET_KEY=your-secret-key
- PYTHONPATH=/app

Procfile para Railway:
web: gunicorn --bind 0.0.0.0:$PORT --workers $WEB_CONCURRENCY --worker-class gthread --threads 4 --timeout 120 wsgi:application

railway.toml (opcional):
[build]
builder = "NIXPACKS"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
"""
