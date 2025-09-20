#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📁 Ruta: /app/wsgi.py
📄 Nombre: wsgi.py
🏗️ Propósito: Entry point WSGI compatible con Railway y ERP13 Enterprise
⚡ Performance: Auto-detección de aplicación, logging estructurado
🔒 Seguridad: Validación de entorno, manejo robusto de errores

ERP13 Enterprise - Sistema ERP Modular
Optimizado para Railway deployment con auto-recovery
"""

import os
import sys
import logging
from datetime import datetime, timezone

# 🚀 CONFIGURACIÓN DE LOGGING ESTRUCTURADO
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/erp13_wsgi.log', mode='a')
    ]
)
logger = logging.getLogger('ERP13.WSGI')

# 🔧 VALIDACIÓN DE ENTORNO RAILWAY
def validate_environment():
    """Validar configuración crítica de Railway"""
    try:
        port = os.environ.get('PORT', '8080')
        env = os.environ.get('RAILWAY_ENVIRONMENT', 'production')
        
        logger.info(f"🚀 ERP13 Enterprise iniciando...")
        logger.info(f"🌐 Entorno: {env}")
        logger.info(f"🔌 Puerto: {port}")
        logger.info(f"📁 Directorio: {os.getcwd()}")
        logger.info(f"🐍 Python: {sys.version}")
        
        # Verificar estructura de archivos críticos
        files_to_check = ['app.py', 'main.py', 'application.py', 'server.py']
        found_files = [f for f in files_to_check if os.path.exists(f)]
        logger.info(f"📋 Archivos encontrados: {found_files}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error en validación de entorno: {e}")
        return False

# 🔍 AUTO-DETECCIÓN DE APLICACIÓN
def detect_application():
    """Auto-detectar y cargar aplicación Flask/Django"""
    try:
        # Prioridad 1: app.py con variable 'app'
        if os.path.exists('app.py'):
            logger.info("🔍 Intentando cargar desde app.py...")
            try:
                from app import app
                logger.info("✅ Aplicación cargada desde app.py")
                return app
            except ImportError as e:
                logger.warning(f"⚠️ Error cargando app.py: {e}")
        
        # Prioridad 2: main.py con variable 'app'
        if os.path.exists('main.py'):
            logger.info("🔍 Intentando cargar desde main.py...")
            try:
                from main import app
                logger.info("✅ Aplicación cargada desde main.py")
                return app
            except ImportError as e:
                logger.warning(f"⚠️ Error cargando main.py: {e}")
        
        # Prioridad 3: application.py con variable 'application'
        if os.path.exists('application.py'):
            logger.info("🔍 Intentando cargar desde application.py...")
            try:
                from application import application as app
                logger.info("✅ Aplicación cargada desde application.py")
                return app
            except ImportError as e:
                logger.warning(f"⚠️ Error cargando application.py: {e}")
        
        # Prioridad 4: Crear aplicación de emergencia
        logger.warning("⚠️ No se encontró aplicación principal, creando emergencia...")
        return create_emergency_app()
        
    except Exception as e:
        logger.error(f"❌ Error crítico en detección de aplicación: {e}")
        return create_emergency_app()

# 🚨 APLICACIÓN DE EMERGENCIA
def create_emergency_app():
    """Crear aplicación Flask de emergencia para diagnóstico"""
    try:
        from flask import Flask, jsonify, request
        
        emergency_app = Flask(__name__)
        
        @emergency_app.route('/')
        def health():
            return jsonify({
                'status': 'emergency_mode',
                'service': 'ERP13 Enterprise',
                'message': 'Aplicación principal no encontrada',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'environment': os.environ.get('RAILWAY_ENVIRONMENT', 'unknown'),
                'python_version': sys.version,
                'files_in_directory': os.listdir('.'),
                'working_directory': os.getcwd()
            })
        
        @emergency_app.route('/health')
        def health_check():
            return jsonify({
                'status': 'healthy_emergency',
                'checks': {
                    'wsgi': 'loaded',
                    'flask': 'available',
                    'environment': 'railway'
                }
            })
        
        @emergency_app.route('/debug')
        def debug_info():
            return jsonify({
                'environment_variables': dict(os.environ),
                'sys_path': sys.path,
                'current_directory': os.getcwd(),
                'directory_contents': os.listdir('.'),
                'python_executable': sys.executable
            })
        
        @emergency_app.errorhandler(500)
        def internal_error(error):
            return jsonify({
                'error': 'Internal Server Error',
                'message': str(error),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 500
        
        logger.info("🚨 Aplicación de emergencia creada exitosamente")
        return emergency_app
        
    except Exception as e:
        logger.error(f"❌ Error crítico creando aplicación de emergencia: {e}")
        # Último recurso: aplicación mínima
        from flask import Flask
        minimal_app = Flask(__name__)
        
        @minimal_app.route('/')
        def minimal():
            return "ERP13 Enterprise - Emergency Mode"
        
        return minimal_app

# 🚀 INICIALIZACIÓN PRINCIPAL
if __name__ != "__main__":
    # Modo WSGI (Gunicorn)
    logger.info("🔧 Iniciando en modo WSGI (Gunicorn)")
    
    # Validar entorno
    if not validate_environment():
        logger.error("❌ Validación de entorno falló")
    
    # Detectar y cargar aplicación
    application = detect_application()
    
    if application:
        logger.info("✅ WSGI application lista para Gunicorn")
        
        # Configurar aplicación para production
        if hasattr(application, 'config'):
            application.config['ENV'] = 'production'
            application.config['DEBUG'] = False
            application.config['TESTING'] = False
        
    else:
        logger.error("❌ No se pudo crear application")
        raise RuntimeError("Failed to create WSGI application")

else:
    # Modo desarrollo directo
    logger.info("🔧 Iniciando en modo desarrollo")
    
    if not validate_environment():
        logger.warning("⚠️ Validación de entorno falló en desarrollo")
    
    app = detect_application()
    
    if app:
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=True)
    else:
        logger.error("❌ No se pudo iniciar aplicación en desarrollo")

# 📊 LOGS FINALES
logger.info("🏁 wsgi.py cargado completamente")
logger.info(f"📊 Variables exportadas: {'application' if 'application' in locals() else 'ninguna'}")
