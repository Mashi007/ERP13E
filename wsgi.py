#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📁 Ruta: /app/wsgi.py
📄 Nombre: wsgi_enterprise_fixed.py
🏗️ Propósito: Entry point WSGI para Railway optimizado
⚡ Performance: Lazy loading + health checks robustos
🔒 Seguridad: Validación completa antes de inicialización
"""

import os
import sys
import logging
from pathlib import Path

# Configuración de logging ANTES de cualquier import
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] WSGI-%(name)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger('ERP13_WSGI')

def initialize_wsgi():
    """Inicialización robusta del WSGI con validaciones"""
    logger.info("=" * 60)
    logger.info("🚀 ERP13 ENTERPRISE v3.0 - WSGI INITIALIZATION")
    logger.info("=" * 60)
    
    # Información del entorno
    logger.info(f"🌐 Railway Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'development')}")
    logger.info(f"📂 Railway Project: {os.environ.get('RAILWAY_PROJECT_NAME', 'unknown')}")
    logger.info(f"🔌 Port: {os.environ.get('PORT', '8080')}")
    logger.info(f"🐍 Python: {sys.version}")
    logger.info(f"📁 Working Directory: {os.getcwd()}")
    
    # Verificar archivos críticos
    critical_files = ['main.py', 'requirements.txt']
    files_exist = [f for f in critical_files if Path(f).exists()]
    logger.info(f"✅ Critical files: {files_exist}")
    
    # Verificar estructura de templates
    template_dir = Path('templates')
    if template_dir.exists():
        template_count = len(list(template_dir.glob('**/*.html')))
        logger.info(f"📄 Templates found: {template_count}")
        
        # Verificar templates críticos
        critical_templates = [
            'templates/layout.html',
            'templates/login.html', 
            'templates/dashboard.html',
            'templates/errors/404.html',
            'templates/errors/500.html'
        ]
        
        for template in critical_templates:
            if Path(template).exists():
                logger.info(f"  ✅ {template}")
            else:
                logger.warning(f"  ⚠️ MISSING: {template}")
    else:
        logger.error("❌ Templates directory not found!")
    
    # Verificar directorios disponibles
    dirs = [d for d in Path('.').iterdir() if d.is_dir() and not d.name.startswith('.')]
    logger.info(f"📂 Available directories: {[d.name for d in dirs]}")
    
    # Verificar variables de entorno
    env_vars = ['DATABASE_URL', 'REDIS_URL', 'SECRET_KEY', 'JWT_SECRET_KEY']
    for var in env_vars:
        value = os.environ.get(var)
        if value and value != 'default':
            logger.info(f"🔑 {var}: ✅ CONFIGURED")
        else:
            logger.warning(f"🔑 {var}: ⚠️ DEFAULT")
    
    logger.info("=" * 60)

# Ejecutar inicialización
initialize_wsgi()

# Importar aplicación con manejo de errores robusto
logger.info("🔍 Importing ERP13 Enterprise application...")

try:
    # Intentar importar con el patrón factory
    from main import create_app
    logger.info("✅ Factory pattern imported from main.py")
    
    # Crear aplicación con configuración de producción
    app = create_app('production')
    application = app  # Railway busca 'application'
    
    # Configurar para producción
    if os.environ.get('RAILWAY_ENVIRONMENT') == 'production':
        app.config['DEBUG'] = False
        app.config['TESTING'] = False
        logger.info("✅ Production configuration applied")
    
except ImportError as e:
    logger.warning(f"⚠️ Factory pattern not found: {e}")
    
    try:
        # Fallback: importar app directamente
        from main import app
        application = app  # Railway busca 'application'
        logger.info("✅ Application imported from main.py (app only)")
        
        # Configurar para producción
        if os.environ.get('RAILWAY_ENVIRONMENT') == 'production':
            app.config['DEBUG'] = False
            app.config['TESTING'] = False
            logger.info("✅ Production configuration applied")
            
    except ImportError as e2:
        logger.error(f"❌ Failed to import application: {e2}")
        
        # Crear aplicación mínima de emergencia
        from flask import Flask, jsonify
        
        app = Flask(__name__)
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'emergency-key')
        
        @app.route('/health')
        def health():
            return jsonify({
                'status': 'emergency',
                'message': 'Application import failed - emergency mode',
                'error': str(e2)
            }), 503
        
        @app.route('/')
        def index():
            return jsonify({
                'status': 'error',
                'message': 'ERP13 Enterprise initialization failed',
                'details': 'Check logs for more information'
            }), 503
        
        application = app
        logger.error("⚠️ Running in emergency mode")

# Múltiples exports para compatibilidad máxima
flask_app = app
wsgi_app = app.wsgi_app
app_instance = app
erp13_app = app

# Logging de verificación final
logger.info("✅ WSGI APPLICATION EXPORTS:")
logger.info("   - application ✅")
logger.info("   - app ✅")
logger.info("   - flask_app ✅")
logger.info("   - wsgi_app ✅")
logger.info("   - app_instance ✅")
logger.info("   - erp13_app ✅")

# Verificar rutas disponibles
with app.app_context():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(str(rule))
    logger.info(f"📋 Routes available: {len(routes)}")

# Verificar configuración final
logger.info(f"🎯 Environment: {app.config.get('ENV', 'UNKNOWN')}")
logger.info(f"🔧 Debug mode: {'ON' if app.config.get('DEBUG') else 'OFF'}")

logger.info("🚀 ERP13 Enterprise v3.0 - WSGI READY FOR RAILWAY")
logger.info("=" * 60)

# Export principal para Gunicorn
__all__ = ['application', 'app']
