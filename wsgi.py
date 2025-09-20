#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ERP13 Enterprise - WSGI Entry Point
Compatible con Railway deployment.
"""

import os
import sys
import logging
from datetime import datetime

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] ERP13E: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('ERP13E.WSGI')

try:
    logger.info("🚀 ERP13 Enterprise iniciando...")
    logger.info(f"📁 Directorio: {os.getcwd()}")
    logger.info(f"🐍 Python: {sys.version.split()[0]}")
    logger.info(f"🌐 FLASK_ENV: {os.environ.get('FLASK_ENV', 'production')}")
    logger.info(f"🔌 PORT: {os.environ.get('PORT', '8080')}")
    
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

    # Verificar que es una aplicación Flask válida
    if hasattr(application, 'wsgi_app'):
        logger.info("✅ Aplicación Flask válida detectada")
    else:
        logger.warning("⚠️ Aplicación importada no parece ser Flask app")

except ImportError as e:
    logger.error(f"❌ Error importando desde main.py: {e}")
    logger.info("🔄 Intentando importación desde app.py...")
    
    try:
        from app import app as application
        logger.info("✅ Aplicación importada desde app.py")
    except ImportError as e2:
        logger.error(f"❌ Error importando desde app.py: {e2}")
        
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
            }), 200
        
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
            'message': 'main.py no encontrado en el repositorio',
            'directory_contents': os.listdir('.'),
            'timestamp': datetime.utcnow().isoformat()
        })
    
    @application.route('/health')
    def health_minimal():
        return jsonify({'status': 'minimal_healthy'}), 200

except Exception as e:
    logger.error(f"❌ Error crítico: {e}")
    raise RuntimeError(f"Failed to create WSGI application: {e}")

# Verificación final
if 'application' in locals():
    logger.info("✅ WSGI application lista para Gunicorn")
    logger.info(f"📊 Application object: {application}")
else:
    logger.error("❌ No se pudo crear application object")
    raise RuntimeError("WSGI application not created")

logger.info("🏁 wsgi.py carga completada")
