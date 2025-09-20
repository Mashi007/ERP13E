#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📁 Ruta: /wsgi.py
📄 Nombre: wsgi.py
🏗️ Propósito: Entry point WSGI para ERP13E - Importa desde main.py
⚡ Performance: Importación directa optimizada para Railway
🔒 Seguridad: Validación de entorno y manejo de errores

ERP13 Enterprise - WSGI Gateway
Compatible con configuración Railway actual
"""

import os
import sys
import logging
from datetime import datetime

# 🚀 CONFIGURACIÓN DE LOGGING PARA RAILWAY
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] ERP13E: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('ERP13E.WSGI')

def log_environment():
    """Registrar información del entorno"""
    logger.info("🚀 ERP13 Enterprise iniciando...")
    logger.info(f"📁 Directorio: {os.getcwd()}")
    logger.info(f"🐍 Python: {sys.version.split()[0]}")
    logger.info(f"🌐 FLASK_ENV: {os.environ.get('FLASK_ENV', 'not_set')}")
    logger.info(f"🔌 PORT: {os.environ.get('PORT', 'not_set')}")

# 📊 IMPORTAR APLICACIÓN DESDE MAIN.PY
try:
    log_environment()
    
    # Verificar que main.py existe
    if not os.path.exists('main.py'):
        raise FileNotFoundError("main.py no encontrado")
    
    logger.info("🔍 Importando aplicación desde main.py...")
    
    # Importar la aplicación Flask desde main.py
    from main import app as application
    
    logger.info("✅ Aplicación importada exitosamente desde main.py")
    logger.info(f"🏷️ Tipo de aplicación: {type(application).__name__}")
    
    # Configurar para production
    if hasattr(application, 'config'):
        application.config['ENV'] = 'production'
        application.config['DEBUG'] = False
        application.config['TESTING'] = False
        logger.info("🔧 Configuración de production aplicada")
    
    # Verificar que la aplicación tiene métodos Flask
    if hasattr(application, 'wsgi_app'):
        logger.info("✅ Aplicación Flask válida detectada")
    else:
        logger.warning("⚠️ Aplicación importada no parece ser Flask app")

except ImportError as e:
    logger.error(f"❌ Error importando desde main.py: {e}")
    logger.info("🔄 Intentando importación alternativa desde app.py...")
    
    try:
        from app import app as application
        logger.info("✅ Aplicación importada desde app.py como alternativa")
    except ImportError as e2:
        logger.error(f"❌ Error importando desde app.py: {e2}")
        logger.info("🚨 Creando aplicación de emergencia...")
        
        # Crear aplicación de emergencia
        from flask import Flask, jsonify
        application = Flask(__name__)
        
        @application.route('/')
        def emergency():
            return jsonify({
                'status': 'emergency_mode',
                'service': 'ERP13 Enterprise',
                'message': 'Aplicación principal no encontrada',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e),
                'directory_contents': os.listdir('.'),
                'python_path': sys.path[:3]
            })
        
        @application.route('/health')
        def health():
            return jsonify({
                'status': 'emergency_healthy',
                'service': 'ERP13E Emergency Mode'
            })
        
        logger.info("🚨 Aplicación de emergencia creada")

except FileNotFoundError as e:
    logger.error(f"❌ Archivo no encontrado: {e}")
    
    # Crear aplicación mínima
    from flask import Flask, jsonify
    application = Flask(__name__)
    
    @application.route('/')
    def not_found():
        return jsonify({
            'status': 'file_not_found',
            'service': 'ERP13 Enterprise',
            'message': 'main.py no encontrado',
            'directory_contents': os.listdir('.'),
            'timestamp': datetime.utcnow().isoformat()
        })
    
    @application.route('/health')
    def health_minimal():
        return jsonify({'status': 'minimal_healthy'})

except Exception as e:
    logger.error(f"❌ Error crítico: {e}")
    raise RuntimeError(f"Failed to create WSGI application: {e}")

# 🔧 CONFIGURACIÓN FINAL
if 'application' in locals():
    logger.info("✅ WSGI application lista para Gunicorn")
    logger.info(f"📊 Application object: {application}")
    
    # Agregar middleware de logging si es necesario
    if hasattr(application, 'before_request'):
        @application.before_request
        def log_request():
            logger.info(f"📥 Request: {request.method} {request.path}")
else:
    logger.error("❌ No se pudo crear application object")
    raise RuntimeError("WSGI application not created")

# 🏥 HEALTH CHECK ENDPOINT (solo si no existe)
try:
    with application.test_client() as client:
        response = client.get('/health')
        if response.status_code == 404:
            logger.info("➕ Agregando endpoint /health")
            
            @application.route('/health')
            def wsgi_health():
                return jsonify({
                    'status': 'healthy',
                    'service': 'ERP13 Enterprise',
                    'wsgi': 'active',
                    'timestamp': datetime.utcnow().isoformat()
                })
except Exception:
    # Si hay error en test_client, continuar normalmente
    pass

logger.info("🏁 wsgi.py carga completada")
