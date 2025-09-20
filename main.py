#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📁 Ruta: /app/main.py
📄 Nombre: MainApplication.py
🏗️ Propósito: Aplicación Flask principal con health checks integrados
⚡ Performance: Configuración optimizada para Railway
🔒 Seguridad: Manejo robusto de errores y logging

ERP13 Enterprise - Aplicación Principal
Arquitectura modular optimizada para Railway deployment
"""

import os
import sys
import logging
from datetime import datetime, timezone
from flask import Flask, jsonify, request, render_template
from werkzeug.exceptions import HTTPException

# 📦 IMPORTACIONES CONDICIONALES CON FALLBACKS
try:
    from flask_sqlalchemy import SQLAlchemy
    from flask_jwt_extended import JWTManager
    from flask_redis import FlaskRedis
    EXTENSIONS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Some extensions not available: {e}")
    EXTENSIONS_AVAILABLE = False

# 🏥 IMPORTAR HEALTH CONTROLLER
try:
    from health import health_bp
    HEALTH_CONTROLLER_AVAILABLE = True
except ImportError:
    logging.warning("Health controller not available - creating fallback")
    HEALTH_CONTROLLER_AVAILABLE = False

# 🚀 CONFIGURACIÓN DE LOGGING
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class ERPConfig:
    """
    ⚙️ Configuración centralizada para ERP13 Enterprise
    Optimizada para Railway con fallbacks robustos
    """
    
    # 🌐 CONFIGURACIÓN BÁSICA
    SECRET_KEY = os.environ.get('SECRET_KEY', 'erp13-enterprise-fallback-key-2024')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = False
    
    # 🗄️ BASE DE DATOS
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or 'sqlite:///erp13_fallback.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_timeout': 20,
        'pool_recycle': -1,
        'pool_pre_ping': True
    }
    
    # 🔴 REDIS
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')
    
    # 🔐 JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hora
    JWT_ALGORITHM = 'HS256'
    
    # 🚀 RAILWAY ESPECÍFICO
    PORT = int(os.environ.get('PORT', 8080))
    HOST = '0.0.0.0'
    RAILWAY_ENVIRONMENT = os.environ.get('RAILWAY_ENVIRONMENT', 'production')

def create_app(config_class=ERPConfig):
    """
    🏭 Factory para crear la aplicación Flask
    Con configuración modular y manejo de errores robusto
    """
    
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 📝 LOGGING INICIAL
    logger.info("🚀 Iniciando ERP13 Enterprise")
    logger.info(f"🌐 Environment: {app.config['RAILWAY_ENVIRONMENT']}")
    logger.info(f"🔌 Port: {app.config['PORT']}")
    logger.info(f"🗄️ Database: {'PostgreSQL' if 'postgres' in app.config['SQLALCHEMY_DATABASE_URI'] else 'SQLite'}")
    
    # 🔧 INICIALIZAR EXTENSIONES
    if EXTENSIONS_AVAILABLE:
        try:
            # SQLAlchemy
            db = SQLAlchemy()
            db.init_app(app)
            app.extensions['db'] = db
            logger.info("✅ SQLAlchemy inicializado")
            
            # JWT
            jwt = JWTManager()
            jwt.init_app(app)
            app.extensions['jwt'] = jwt
            logger.info("✅ JWT Manager inicializado")
            
            # Redis
            redis_client = FlaskRedis()
            redis_client.init_app(app)
            app.extensions['redis'] = redis_client
            logger.info("✅ Redis inicializado")
            
        except Exception as e:
            logger.warning(f"⚠️ Error inicializando extensiones: {e}")
    else:
        logger.warning("⚠️ Ejecutando sin extensiones - modo fallback")
    
    # 🏥 REGISTRAR HEALTH CONTROLLER
    if HEALTH_CONTROLLER_AVAILABLE:
        app.register_blueprint(health_bp)
        logger.info("✅ Health controller registrado")
    else:
        # 🚨 FALLBACK HEALTH ENDPOINT
        @app.route('/health')
        def fallback_health():
            return jsonify({
                'status': 'healthy',
                'service': 'ERP13 Enterprise',
                'version': '1.0.0',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'mode': 'fallback'
            })
        logger.info("⚠️ Health endpoint fallback registrado")
    
    # 🏠 RUTAS PRINCIPALES
    @app.route('/')
    def index():
        """
        🏠 Página principal del ERP
        """
        try:
            # Intentar renderizar template si existe
            return render_template('index.html', 
                                 system_name='ERP13 Enterprise',
                                 version='1.0.0',
                                 environment=app.config['RAILWAY_ENVIRONMENT'])
        except Exception as e:
            # Fallback a respuesta JSON
            logger.warning(f"Template index.html no disponible: {e}")
            return jsonify({
                'service': 'ERP13 Enterprise',
                'version': '1.0.0',
                'status': 'running',
                'environment': app.config['RAILWAY_ENVIRONMENT'],
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'message': 'Sistema ERP funcionando correctamente',
                'endpoints': {
                    'health': '/health',
                    'health_detailed': '/health/detailed',
                    'api': '/api/v1/',
                    'docs': '/docs'
                }
            })
    
    @app.route('/api/v1/status')
    def api_status():
        """
        📊 Estado de la API
        """
        return jsonify({
            'api_version': '1.0.0',
            'service': 'ERP13 Enterprise',
            'status': 'operational',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'features': {
                'database': 'postgresql' if 'postgres' in app.config['SQLALCHEMY_DATABASE_URI'] else 'sqlite',
                'cache': 'redis',
                'authentication': 'jwt',
                'environment': app.config['RAILWAY_ENVIRONMENT']
            }
        })
    
    @app.route('/docs')
    def api_docs():
        """
        📚 Documentación básica de la API
        """
        return jsonify({
            'service': 'ERP13 Enterprise API',
            'version': '1.0.0',
            'documentation': {
                'health_checks': {
                    'basic': '/health',
                    'detailed': '/health/detailed',
                    'readiness': '/health/ready',
                    'liveness': '/health/live'
                },
                'api_endpoints': {
                    'status': '/api/v1/status',
                    'version': '/api/v1/version'
                },
                'system': {
                    'info': '/',
                    'metrics': '/metrics'
                }
            },
            'environment': app.config['RAILWAY_ENVIRONMENT'],
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
    
    # 🚨 MANEJO DE ERRORES
    @app.errorhandler(404)
    def not_found(error):
        """
        🔍 Manejo de errores 404
        """
        return jsonify({
            'error': 'Not Found',
            'message': 'El recurso solicitado no existe',
            'status_code': 404,
            'service': 'ERP13 Enterprise',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """
        💥 Manejo de errores 500
        """
        logger.error(f"Internal server error: {error}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Error interno del servidor',
            'status_code': 500,
            'service': 'ERP13 Enterprise',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        """
        🛡️ Manejo general de excepciones
        """
        if isinstance(e, HTTPException):
            return e
        
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        return jsonify({
            'error': 'Unexpected Error',
            'message': 'Error inesperado del sistema',
            'status_code': 500,
            'service': 'ERP13 Enterprise',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500
    
    # 📊 LOGGING DE REQUESTS
    @app.before_request
    def log_request_info():
        """
        📝 Log de requests para debugging
        """
        if app.config['DEBUG']:
            logger.debug(f"Request: {request.method} {request.url}")
    
    @app.after_request
    def log_response_info(response):
        """
        📝 Log de responses para debugging
        """
        if app.config['DEBUG']:
            logger.debug(f"Response: {response.status_code}")
        return response
    
    # ✅ CONFIRMACIÓN DE INICIALIZACIÓN
    logger.info("✅ ERP13 Enterprise inicializado correctamente")
    
    return app

# 🚀 CREAR INSTANCIA DE LA APLICACIÓN
app = create_app()

# 📊 CONTEXTO DE APLICACIÓN PARA SCRIPTS
def create_app_context():
    """
    🔧 Crear contexto de aplicación para scripts y comandos
    """
    with app.app_context():
        yield app

if __name__ == '__main__':
    """
    🎯 Punto de entrada principal para desarrollo local
    Para producción usar: gunicorn wsgi:application
    """
    
    logger.info("🚀 Iniciando ERP13 Enterprise en modo desarrollo")
    
    # Configuración para desarrollo local
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )
