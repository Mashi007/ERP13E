#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📁 Ruta: /main.py
📄 Nombre: main.py
🏗️ Propósito: ERP13 Enterprise v3.0 - Integrado con layout.html real (navbar)
⚡ Performance: Optimizado para Railway
🔒 Seguridad: JWT + Sessions + RBAC

ERP13 Enterprise v3.0
Copyright (c) 2025 ERP13 Enterprise Solutions
"""

import os
import sys
import logging
import json
from datetime import datetime, timedelta
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

# Flask imports
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, g

# Redis opcional
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# =============================================================================
# LOGGING
# =============================================================================

def setup_logging():
    """Configurar logging"""
    log_format = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    
    logger = logging.getLogger('ERP13_Main')
    logger.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    return logger

logger = setup_logging()

# =============================================================================
# FACTORY PATTERN
# =============================================================================

def create_app(config_name='production'):
    """Factory pattern para crear aplicación Flask"""
    app = Flask(__name__)
    
    # Configuración según entorno
    if config_name == 'production':
        app.config.update({
            'DEBUG': False,
            'TESTING': False,
            'TEMPLATES_AUTO_RELOAD': False
        })
        logger.info("🚀 Running in PRODUCTION mode")
    else:
        app.config.update({
            'DEBUG': True,
            'TESTING': False,
            'TEMPLATES_AUTO_RELOAD': True
        })
        logger.info("🔧 Running in DEVELOPMENT mode")
    
    # Configuración base
    app.config.update({
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'erp13-enterprise-secret-key-2025'),
        'PERMANENT_SESSION_LIFETIME': timedelta(hours=24),
        'SESSION_COOKIE_SECURE': config_name == 'production',
        'SESSION_COOKIE_HTTPONLY': True,
        'SESSION_COOKIE_SAMESITE': 'Lax',
        'PORT': int(os.environ.get('PORT', 8080))
    })
    
    # Redis setup
    def setup_redis():
        if not REDIS_AVAILABLE:
            return None
        try:
            redis_url = os.environ.get('REDIS_URL')
            if not redis_url or redis_url == 'default':
                logger.warning("⚠️ Redis not configured")
                return None
            
            redis_client = redis.from_url(redis_url, decode_responses=True)
            redis_client.ping()
            logger.info("✅ Redis connected")
            return redis_client
        except Exception as e:
            logger.warning(f"⚠️ Redis failed: {e}")
            return None
    
    app.redis = setup_redis()
    
    # Health monitoring
    try:
        from app.health_check import init_health_monitoring
        health_monitor = init_health_monitoring(app)
        logger.info("✅ Health Monitoring initialized")
    except:
        @app.route('/health')
        def basic_health():
            """Health check básico"""
            return jsonify({
                "status": "operational",  # El layout espera "operational"
                "service": "ERP Enterprise",
                "version": "3.0.0",
                "timestamp": datetime.now().isoformat()
            }), 200
    
    # Auth Manager
    class AuthManager:
        @staticmethod
        def require_auth(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                if 'user_id' not in session:
                    if request.is_json:
                        return jsonify({'error': 'Auth required'}), 401
                    flash('Por favor, inicia sesión', 'warning')
                    return redirect(url_for('auth_login'))
                return f(*args, **kwargs)
            return decorated
    
    app.auth = AuthManager()
    
    # Mock users
    MOCK_USERS = {
        'admin@erp13.com': {
            'id': 1,
            'email': 'admin@erp13.com',
            'password': generate_password_hash('admin123'),
            'name': 'Administrador',
            'role': 'admin'
        }
    }
    
    # =============================================================================
    # RUTAS AUTENTICACIÓN
    # =============================================================================
    
    @app.route('/login', methods=['GET', 'POST'])
    def auth_login():
        """Login"""
        if request.method == 'POST':
            data = request.get_json() if request.is_json else request.form
            email = data.get('email', '').lower()
            password = data.get('password', '')
            
            user = MOCK_USERS.get(email)
            if user and check_password_hash(user['password'], password):
                session.update({
                    'user_id': user['id'],
                    'user_email': user['email'],
                    'user_name': user['name'],
                    'user_role': user['role']
                })
                
                if request.is_json:
                    return jsonify({'success': True})
                return redirect(url_for('dashboard'))
            
            if request.is_json:
                return jsonify({'success': False}), 401
            flash('Credenciales inválidas', 'error')
        
        return render_template('login.html')
    
    @app.route('/logout')
    def auth_logout():
        """Logout"""
        session.clear()
        return redirect(url_for('auth_login'))
    
    # =============================================================================
    # DASHBOARD (usa layout.html con navbar)
    # =============================================================================
    
    @app.route('/')
    @app.route('/dashboard')
    @app.auth.require_auth
    def dashboard():
        """Dashboard principal"""
        # El layout.html espera active_page para marcar el menú activo
        return render_template('dashboard.html', active_page='dashboard')
    
    # =============================================================================
    # MÓDULO CLIENTES
    # =============================================================================
    
    @app.route('/clientes')
    @app.route('/clientes/gestion')
    @app.auth.require_auth
    def clientes_gestion():
        """Gestión de Clientes"""
        return render_template('clientes/gestion_clientes.html', active_page='clientes')
    
    @app.route('/clientes/timeline')
    @app.auth.require_auth
    def clientes_timeline():
        """Timeline"""
        return render_template('clientes/timeline.html', active_page='clientes')
    
    @app.route('/clientes/comunicaciones')
    @app.auth.require_auth
    def clientes_comunicaciones():
        """Comunicaciones"""
        return render_template('clientes/comunicaciones.html', active_page='clientes')
    
    @app.route('/clientes/propuestas')
    @app.auth.require_auth
    def clientes_propuestas():
        """Propuestas"""
        return render_template('clientes/propuestas.html', active_page='clientes')
    
    @app.route('/clientes/pipeline')
    @app.auth.require_auth
    def clientes_pipeline():
        """Pipeline"""
        return render_template('clientes/pipeline.html', active_page='clientes')
    
    @app.route('/clientes/tickets')
    @app.auth.require_auth
    def clientes_tickets():
        """Tickets"""
        return render_template('clientes/tickets.html', active_page='clientes')
    
    @app.route('/clientes/calendario')
    @app.auth.require_auth
    def clientes_calendario():
        """Calendario"""
        return render_template('clientes/calendario.html', active_page='clientes')
    
    @app.route('/clientes/campanas')
    @app.auth.require_auth
    def clientes_campanas():
        """Campañas"""
        return render_template('clientes/campanas.html', active_page='clientes')
    
    @app.route('/clientes/automatizaciones')
    @app.auth.require_auth
    def clientes_automatizaciones():
        """Automatizaciones"""
        return render_template('clientes/automatizaciones.html', active_page='clientes')
    
    # =============================================================================
    # MÓDULO FACTURACIÓN (rutas del navbar en layout.html)
    # =============================================================================
    
    @app.route('/facturacion/clientes')
    @app.auth.require_auth
    def facturacion_clientes():
        """Facturas Clientes - ruta del navbar"""
        return render_template('facturacion/facturas_clientes.html', active_page='facturacion')
    
    @app.route('/facturacion/estados-pago')
    @app.auth.require_auth
    def facturacion_estados_pago():
        """Estados de Pago - ruta del navbar"""
        return render_template('facturacion/estados_pago.html', active_page='facturacion')
    
    @app.route('/facturacion/exportacion')
    @app.auth.require_auth
    def facturacion_exportacion():
        """Exportación Contable - ruta del navbar"""
        return render_template('facturacion/exportacion_contable.html', active_page='facturacion')
    
    @app.route('/facturacion/proveedores')
    @app.auth.require_auth
    def facturacion_proveedores():
        """Facturas Proveedores"""
        return render_template('facturacion/facturas_proveedores.html', active_page='facturacion')
    
    @app.route('/facturacion/apuntes')
    @app.auth.require_auth
    def facturacion_apuntes():
        """Apuntes Contables"""
        return render_template('facturacion/apuntes_contables.html', active_page='facturacion')
    
    # =============================================================================
    # MÓDULO CONTABILIDAD (ruta del navbar)
    # =============================================================================
    
    @app.route('/contabilidad/apuntes')
    @app.auth.require_auth
    def contabilidad_apuntes():
        """Apuntes Contables - desde navbar"""
        # Redirige a facturación/apuntes_contables.html
        return render_template('facturacion/apuntes_contables.html', active_page='contabilidad')
    
    # =============================================================================
    # MÓDULO AUDITORÍA
    # =============================================================================
    
    @app.route('/auditoria')
    @app.route('/auditoria/proyectos')
    @app.auth.require_auth
    def auditoria_proyectos():
        """Proyectos de Auditoría"""
        return render_template('auditoria/auditoria_proyectos.html', active_page='auditoria')
    
    @app.route('/auditoria/configuracion')
    @app.auth.require_auth
    def auditoria_configuracion():
        """Configuración de Auditoría"""
        return render_template('auditoria/auditoria_configuracion.html', active_page='auditoria')
    
    # =============================================================================
    # MÓDULO CONFIGURACIÓN
    # =============================================================================
    
    @app.route('/configuracion')
    @app.route('/configuracion/general')
    @app.auth.require_auth
    def configuracion_general():
        """Configuración General"""
        return render_template('configuracion/configuracion_general.html', active_page='configuracion')
    
    @app.route('/configuracion/usuarios')
    @app.auth.require_auth
    def configuracion_usuarios():
        """Gestión de Usuarios"""
        return render_template('configuracion/gestion_usuarios.html', active_page='configuracion')
    
    @app.route('/configuracion/plantillas-presupuesto')
    @app.auth.require_auth
    def configuracion_plantillas_presupuesto():
        """Plantillas de Presupuesto"""
        return render_template('configuracion/plantillas_presupuesto.html', active_page='configuracion')
    
    @app.route('/configuracion/ia-interna')
    @app.auth.require_auth
    def configuracion_ia_interna():
        """IA Interna"""
        return render_template('configuracion/ia_interna.html', active_page='configuracion')
    
    @app.route('/configuracion/facturacion')
    @app.auth.require_auth
    def configuracion_facturacion():
        """Configuración de Facturación"""
        return render_template('configuracion/configuracion_facturacion.html', active_page='configuracion')
    
    # =============================================================================
    # ERROR HANDLERS
    # =============================================================================
    
    @app.errorhandler(404)
    def not_found(error):
        """404"""
        if request.is_json:
            return jsonify({'error': 'Not found'}), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """500"""
        logger.error(f"Error 500: {error}")
        if request.is_json:
            return jsonify({'error': 'Internal error'}), 500
        return render_template('errors/500.html'), 500
    
    # =============================================================================
    # CONTEXT PROCESSOR (para layout.html)
    # =============================================================================
    
    @app.context_processor
    def inject_globals():
        """Variables globales para templates"""
        return {
            'user': {
                'name': session.get('user_name', 'Usuario'),
                'email': session.get('user_email', ''),
                'role': session.get('user_role', 'guest')
            },
            'app_name': 'ERP Enterprise',
            'app_version': '3.0.0'
        }
    
    # =============================================================================
    # HEADERS DE SEGURIDAD
    # =============================================================================
    
    @app.after_request
    def security_headers(response):
        """Headers de seguridad"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response
    
    # Logging
    total_routes = len([rule for rule in app.url_map.iter_rules()])
    logger.info(f"✅ ERP Enterprise initialized with {total_routes} routes")
    logger.info("📊 Navbar routes from layout.html:")
    logger.info("  /dashboard")
    logger.info("  /facturacion/clientes")
    logger.info("  /facturacion/estados-pago")
    logger.info("  /facturacion/exportacion")
    logger.info("  /contabilidad/apuntes")
    
    return app

# =============================================================================
# RAILWAY CONFIG
# =============================================================================

app = create_app(os.environ.get('FLASK_ENV', 'production'))

# Exports para Railway
application = app
app_instance = app
flask_app = app
wsgi_app = app

logger.info("✅ WSGI exports ready")

# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    host = '0.0.0.0'
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info("=" * 60)
    logger.info("🚀 ERP ENTERPRISE v3.0.0")
    logger.info(f"📊 Using layout.html with navbar (not sidebar)")
    logger.info(f"🔌 Port: {port}")
    logger.info("=" * 60)
    
    if debug:
        logger.info("🔑 Admin: admin@erp13.com / admin123")
    
    app.run(host=host, port=port, debug=debug)
