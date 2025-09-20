#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📁 Ruta: /app/main.py
📄 Nombre: main.py
🏗️ Propósito: Aplicación principal ERP13 Enterprise v3.1 - HOTFIX CORREGIDO
⚡ Performance: Optimizado para Railway, multi-worker Gunicorn
🔒 Seguridad: Configuración de producción, logging seguro
"""

import os
import sys
import logging
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, session, request, flash, jsonify

# ========== CONFIGURACIÓN LOGGING ENTERPRISE ==========
def setup_logging():
    """Configurar logging estructurado para Railway"""
    logger = logging.getLogger('ERP13_HOTFIX')
    logger.setLevel(logging.INFO)
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    if not logger.handlers:
        logger.addHandler(handler)
    
    return logger

# Inicializar logging
logger = setup_logging()

# ========== CONFIGURACIÓN FLASK ==========
def create_erp_application():
    """Factory para crear aplicación ERP13 Enterprise"""
    
    logger.info("🚀 Creating ERP13 Enterprise HOTFIX application")
    
    # Crear aplicación Flask
    app = Flask(__name__)
    
    # ========== CONFIGURACIÓN BÁSICA ==========
    app.config.update(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'erp13-enterprise-production-key-v3.1'),
        DEBUG=False,
        TESTING=False,
        ENV='production',
        SESSION_COOKIE_SECURE=False,  # Cambiar a True en HTTPS
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=3600,
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,
        JSON_SORT_KEYS=False,
        JSONIFY_PRETTYPRINT_REGULAR=False
    )
    
    # ========== HEALTH CHECK BÁSICO INTEGRADO ==========
    @app.route('/health')
    def basic_health_check():
        """Health check básico integrado"""
        try:
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'service': 'ERP13-Enterprise',
                'version': '3.1.0'
            }), 200
        except Exception as health_error:
            logger.error(f"Health check failed: {health_error}")
            return jsonify({
                'status': 'unhealthy',
                'error': str(health_error),
                'timestamp': datetime.utcnow().isoformat()
            }), 500
    
    @app.route('/health/wsgi')
    def wsgi_health_check():
        """Health check WSGI específico"""
        return jsonify({
            'status': 'healthy',
            'wsgi': 'operational',
            'timestamp': datetime.utcnow().isoformat(),
            'worker_pid': os.getpid()
        }), 200
    
    @app.route('/health/detailed')
    def detailed_health_check():
        """Health check detallado"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'ERP13-Enterprise',
            'version': '3.1.0',
            'environment': 'production',
            'worker_pid': os.getpid()
        }), 200
    
    # ========== REGISTRO DE AUTH BLUEPRINT ==========
    try:
        from auth_fixed import auth_bp
        app.register_blueprint(auth_bp)
        logger.info("✅ Auth blueprint registered successfully")
    except ImportError:
        logger.warning("⚠️ Auth blueprint not found - using fallback routes")
        
        # Rutas de auth fallback
        @app.route('/login')
        def fallback_login():
            return '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>ERP13 Enterprise Login</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body { font-family: Arial, sans-serif; margin: 50px; }
                    .login-form { max-width: 400px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; }
                    input[type="text"], input[type="password"] { width: 100%; padding: 10px; margin: 10px 0; }
                    button { width: 100%; padding: 10px; background: #007bff; color: white; border: none; }
                </style>
            </head>
            <body>
                <div class="login-form">
                    <h2>ERP13 Enterprise Login</h2>
                    <form method="POST" action="/do_login">
                        <input type="text" name="username" placeholder="Usuario" required>
                        <input type="password" name="password" placeholder="Contraseña" required>
                        <button type="submit">Iniciar Sesión</button>
                    </form>
                    <p><small>Demo: admin/admin123</small></p>
                </div>
            </body>
            </html>
            '''
        
        @app.route('/do_login', methods=['POST'])
        def fallback_do_login():
            username = request.form.get('username')
            password = request.form.get('password')
            
            if username == 'admin' and password == 'admin123':
                session['user_id'] = 1
                session['username'] = username
                logger.info(f"✅ Login successful: {username}")
                return redirect(url_for('dashboard'))
            else:
                logger.warning(f"❌ Login failed: {username}")
                return redirect(url_for('fallback_login'))
                
        logger.info("✅ Fallback auth routes configured")
    
    # ========== RUTAS PRINCIPALES ==========
    @app.route('/')
    def index():
        """Ruta principal"""
        if 'user_id' in session:
            return redirect(url_for('dashboard'))
        else:
            logger.info("🔒 Index redirect to login")
            return redirect(url_for('fallback_login'))
    
    @app.route('/dashboard')
    def dashboard():
        """Dashboard principal del ERP"""
        if 'user_id' not in session:
            return redirect(url_for('fallback_login'))
        
        username = session.get('username', 'Usuario')
        
        dashboard_html = f'''
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>ERP13 Enterprise Dashboard</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container-fluid">
                <div class="row">
                    <div class="col-md-2 bg-dark text-white p-3">
                        <h4><i class="fas fa-chart-line me-2"></i>ERP13</h4>
                        <hr>
                        <nav class="nav flex-column">
                            <a class="nav-link text-white" href="/dashboard">
                                <i class="fas fa-chart-pie me-2"></i>Dashboard
                            </a>
                            <a class="nav-link text-white" href="/clientes">
                                <i class="fas fa-users me-2"></i>Clientes
                            </a>
                            <a class="nav-link text-white" href="/facturas">
                                <i class="fas fa-file-invoice me-2"></i>Facturas
                            </a>
                            <a class="nav-link text-white" href="/logout">
                                <i class="fas fa-sign-out-alt me-2"></i>Cerrar Sesión
                            </a>
                        </nav>
                    </div>
                    <div class="col-md-10 p-4">
                        <h1>Dashboard Principal</h1>
                        <p>Bienvenido, <strong>{username}</strong></p>
                        <div class="row">
                            <div class="col-md-3">
                                <div class="card bg-primary text-white">
                                    <div class="card-body">
                                        <h5>1,247</h5>
                                        <p>Clientes Activos</p>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="card bg-success text-white">
                                    <div class="card-body">
                                        <h5>847</h5>
                                        <p>Facturas del Mes</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        '''
        
        return dashboard_html
    
    @app.route('/logout')
    def logout():
        """Cerrar sesión"""
        username = session.get('username', 'Unknown')
        session.clear()
        logger.info(f"✅ Logout successful: {username}")
        return redirect(url_for('fallback_login'))
    
    # ========== ERROR HANDLERS ==========
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            'error': 'Página no encontrada',
            'status': 404,
            'timestamp': datetime.utcnow().isoformat()
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({
            'error': 'Error interno del servidor',
            'status': 500,
            'timestamp': datetime.utcnow().isoformat()
        }), 500
    
    logger.info("🚀 ERP13 Enterprise application created successfully")
    return app

# ========== CREAR APLICACIÓN ==========
try:
    application = create_erp_application()
    app = application  # Alias para compatibilidad
    
    logger.info("✅ Application instance created successfully")
    
except Exception as creation_error:
    logger.error(f"❌ Failed to create application: {creation_error}")
    raise

# ========== WSGI COMPLIANCE ==========
if __name__ == '__main__':
    logger.warning("⚠️ Running in standalone mode")
    application.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 8080)),
        debug=False
    )
else:
    logger.info("✅ WSGI mode activated")
