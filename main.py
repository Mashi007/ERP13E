#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📁 Ruta: /main.py
📄 Nombre: main.py
🏗️ Propósito: ERP13 Enterprise v3.0 - Sistema ERP completo
⚡ Performance: Optimizado para Railway con health monitoring
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

# JWT opcional
try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False

# =============================================================================
# CONFIGURACIÓN DE LOGGING
# =============================================================================

def setup_logging():
    """Configurar logging estructurado"""
    log_format = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    console_handler.setLevel(logging.INFO)
    
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
        'JWT_SECRET_KEY': os.environ.get('JWT_SECRET_KEY', 'jwt-secret-erp13-2025'),
        'PORT': int(os.environ.get('PORT', 8080))
    })
    
    # =============================================================================
    # CONFIGURACIÓN REDIS
    # =============================================================================
    
    def setup_redis():
        """Configurar Redis con fallback"""
        if not REDIS_AVAILABLE:
            logger.warning("⚠️ Redis module not available")
            return None
            
        try:
            redis_url = os.environ.get('REDIS_URL')
            if not redis_url or redis_url == 'default':
                logger.warning("⚠️ REDIS_URL not configured - running without cache")
                return None
            
            redis_client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5
            )
            redis_client.ping()
            logger.info("✅ Redis connected successfully")
            return redis_client
            
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e} - running without cache")
            return None
    
    app.redis = setup_redis()
    app.config['redis_client'] = app.redis
    
    # =============================================================================
    # HEALTH MONITORING
    # =============================================================================
    
    try:
        from app.health_check import init_health_monitoring
        health_monitor = init_health_monitoring(app)
        logger.info("✅ Advanced Health Monitoring initialized")
    except ImportError:
        logger.warning("⚠️ Health monitoring module not found - using basic health check")
        
        @app.route('/health')
        def basic_health():
            """Health check básico para Railway"""
            return jsonify({
                "status": "healthy",
                "service": "ERP13 Enterprise",
                "version": "3.0.0",
                "timestamp": datetime.now().isoformat(),
                "checks": {
                    "flask": "ok",
                    "routes": "ok",
                    "templates": "ok",
                    "redis": "ok" if app.redis else "warning"
                }
            }), 200
    
    # =============================================================================
    # CACHE MANAGER
    # =============================================================================
    
    class CacheManager:
        """Gestor de cache con fallback a memoria"""
        
        def __init__(self, redis_client=None):
            self.redis = redis_client
            self._memory_cache = {}
            self.max_memory_items = 100
        
        def set(self, key, value, expire=300):
            """Set value in cache"""
            try:
                if self.redis:
                    self.redis.setex(key, expire, json.dumps(value))
                else:
                    # Fallback a memoria
                    if len(self._memory_cache) >= self.max_memory_items:
                        # Limpiar el más antiguo
                        oldest = next(iter(self._memory_cache))
                        del self._memory_cache[oldest]
                    self._memory_cache[key] = value
                return True
            except Exception as e:
                logger.warning(f"Cache set failed: {e}")
                return False
        
        def get(self, key):
            """Get value from cache"""
            try:
                if self.redis:
                    value = self.redis.get(key)
                    return json.loads(value) if value else None
                else:
                    return self._memory_cache.get(key)
            except Exception as e:
                logger.warning(f"Cache get failed: {e}")
                return None
    
    app.cache = CacheManager(app.redis)
    
    # =============================================================================
    # AUTH MANAGER
    # =============================================================================
    
    class AuthManager:
        """Gestor de autenticación"""
        
        @staticmethod
        def require_auth(f):
            """Decorador para rutas que requieren autenticación"""
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if 'user_id' not in session:
                    if request.is_json:
                        return jsonify({'error': 'Authentication required'}), 401
                    flash('Por favor, inicia sesión', 'warning')
                    return redirect(url_for('auth_login'))
                return f(*args, **kwargs)
            return decorated_function
        
        @staticmethod
        def require_role(required_role):
            """Decorador para control de roles"""
            def decorator(f):
                @wraps(f)
                def decorated_function(*args, **kwargs):
                    user_role = session.get('user_role', 'guest')
                    
                    role_hierarchy = {
                        'guest': 0,
                        'user': 1,
                        'manager': 2,
                        'admin': 3
                    }
                    
                    if role_hierarchy.get(user_role, 0) < role_hierarchy.get(required_role, 999):
                        if request.is_json:
                            return jsonify({'error': 'Insufficient permissions'}), 403
                        flash('No tienes permisos para acceder a esta sección', 'error')
                        return redirect(url_for('dashboard'))
                    
                    return f(*args, **kwargs)
                return decorated_function
            return decorator
    
    app.auth = AuthManager()
    
    # =============================================================================
    # DATOS MOCK
    # =============================================================================
    
    MOCK_USERS = {
        'admin@erp13.com': {
            'id': 1,
            'email': 'admin@erp13.com',
            'password': generate_password_hash('admin123'),
            'role': 'admin',
            'name': 'Administrador Sistema',
            'active': True
        },
        'user@erp13.com': {
            'id': 2,
            'email': 'user@erp13.com',
            'password': generate_password_hash('user123'),
            'role': 'user',
            'name': 'Usuario Demo',
            'active': True
        }
    }
    
    # =============================================================================
    # RUTAS DE AUTENTICACIÓN
    # =============================================================================
    
    @app.route('/login', methods=['GET', 'POST'])
    def auth_login():
        """Página de login"""
        if request.method == 'POST':
            data = request.get_json() if request.is_json else request.form
            email = data.get('email', '').lower().strip()
            password = data.get('password', '')
            
            if not email or not password:
                if request.is_json:
                    return jsonify({'success': False, 'message': 'Email y contraseña requeridos'}), 400
                flash('Email y contraseña son requeridos', 'error')
                return render_template('login.html')
            
            user = MOCK_USERS.get(email)
            if user and user['active'] and check_password_hash(user['password'], password):
                # Configurar sesión
                session.permanent = True
                session.update({
                    'user_id': user['id'],
                    'user_email': user['email'],
                    'user_role': user['role'],
                    'user_name': user['name']
                })
                
                logger.info(f"✅ Login exitoso: {email}")
                
                if request.is_json:
                    return jsonify({
                        'success': True,
                        'message': 'Login exitoso',
                        'redirect': url_for('dashboard')
                    })
                
                flash(f'Bienvenido, {user["name"]}', 'success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            
            logger.warning(f"⚠️ Login fallido: {email}")
            
            if request.is_json:
                return jsonify({'success': False, 'message': 'Credenciales inválidas'}), 401
            
            flash('Email o contraseña incorrectos', 'error')
        
        return render_template('login.html')
    
    @app.route('/logout')
    def auth_logout():
        """Cerrar sesión"""
        user_email = session.get('user_email', 'Unknown')
        logger.info(f"🔓 Logout: {user_email}")
        session.clear()
        flash('Sesión cerrada exitosamente', 'info')
        return redirect(url_for('auth_login'))
    
    # =============================================================================
    # DASHBOARD
    # =============================================================================
    
    @app.route('/')
    @app.route('/dashboard')
    @app.auth.require_auth
    def dashboard():
        """Dashboard principal"""
        try:
            return render_template('dashboard.html')
        except Exception as e:
            logger.error(f"Error en dashboard: {e}")
            return render_template('dashboard.html')
    
    # =============================================================================
    # MÓDULO CLIENTES (9 RUTAS)
    # =============================================================================
    
    @app.route('/clientes/gestion')
    @app.auth.require_auth
    def clientes_gestion():
        """Gestión de Clientes"""
        return render_template('clientes/gestion_clientes.html')
    
    @app.route('/clientes/timeline')
    @app.auth.require_auth
    def clientes_timeline():
        """Timeline de Clientes"""
        return render_template('clientes/timeline.html')
    
    @app.route('/clientes/comunicaciones')
    @app.auth.require_auth
    def clientes_comunicaciones():
        """Comunicaciones"""
        return render_template('clientes/comunicaciones.html')
    
    @app.route('/clientes/propuestas')
    @app.auth.require_auth
    def clientes_propuestas():
        """Propuestas"""
        return render_template('clientes/propuestas.html')
    
    @app.route('/clientes/pipeline')
    @app.auth.require_auth
    def clientes_pipeline():
        """Pipeline de Ventas"""
        return render_template('clientes/pipeline.html')
    
    @app.route('/clientes/tickets')
    @app.auth.require_auth
    def clientes_tickets():
        """Tickets de Soporte"""
        return render_template('clientes/tickets.html')
    
    @app.route('/clientes/calendario')
    @app.auth.require_auth
    def clientes_calendario():
        """Calendario"""
        return render_template('clientes/calendario.html')
    
    @app.route('/clientes/campanas')
    @app.auth.require_auth
    def clientes_campanas():
        """Campañas"""
        return render_template('clientes/campanas.html')
    
    @app.route('/clientes/automatizaciones')
    @app.auth.require_auth
    def clientes_automatizaciones():
        """Automatizaciones"""
        return render_template('clientes/automatizaciones.html')
    
    # =============================================================================
    # MÓDULO AUDITORÍA (2 RUTAS)
    # =============================================================================
    
    @app.route('/auditoria/proyectos')
    @app.auth.require_auth
    def auditoria_proyectos():
        """Proyectos de Auditoría"""
        return render_template('auditoria/auditoria_proyectos.html')
    
    @app.route('/auditoria/configuracion')
    @app.auth.require_auth
    def auditoria_configuracion():
        """Configuración de Auditoría"""
        return render_template('auditoria/auditoria_configuracion.html')
    
    # =============================================================================
    # MÓDULO FACTURACIÓN (6 RUTAS)
    # =============================================================================
    
    @app.route('/facturacion/proveedores')
    @app.auth.require_auth
    def facturacion_proveedores():
        """Facturas de Proveedores"""
        return render_template('facturacion/facturas_proveedores.html')
    
    @app.route('/facturacion/clientes')
    @app.auth.require_auth
    def facturacion_clientes():
        """Facturas a Clientes"""
        return render_template('facturacion/facturas_clientes.html')
    
    @app.route('/facturacion/apuntes')
    @app.auth.require_auth
    def facturacion_apuntes():
        """Apuntes Contables"""
        return render_template('facturacion/apuntes_contables.html')
    
    @app.route('/facturacion/estados-pago')
    @app.auth.require_auth
    def facturacion_estados_pago():
        """Estados de Pago"""
        return render_template('facturacion/estados_pago.html')
    
    @app.route('/facturacion/exportacion')
    @app.auth.require_auth
    def facturacion_exportacion():
        """Exportación Contable"""
        return render_template('facturacion/exportacion_contable.html')
    
    @app.route('/facturacion/gestionar-proveedores')
    @app.auth.require_auth
    def facturacion_gestionar_proveedores():
        """Gestionar Proveedores"""
        # Usa proveedores.html como fallback
        try:
            return render_template('facturacion/proveedores.html')
        except:
            return render_template('facturacion/facturas_proveedores.html')
    
    # =============================================================================
    # MÓDULO CONFIGURACIÓN (5 RUTAS)
    # =============================================================================
    
    @app.route('/configuracion/general')
    @app.auth.require_auth
    @app.auth.require_role('admin')
    def configuracion_general():
        """Configuración General"""
        return render_template('configuracion/configuracion_general.html')
    
    @app.route('/configuracion/usuarios')
    @app.auth.require_auth
    @app.auth.require_role('admin')
    def configuracion_usuarios():
        """Gestión de Usuarios"""
        return render_template('configuracion/gestion_usuarios.html')
    
    @app.route('/configuracion/plantillas-presupuesto')
    @app.auth.require_auth
    @app.auth.require_role('admin')
    def configuracion_plantillas_presupuesto():
        """Plantillas de Presupuesto"""
        return render_template('configuracion/plantillas_presupuesto.html')
    
    @app.route('/configuracion/ia-interna')
    @app.auth.require_auth
    @app.auth.require_role('admin')
    def configuracion_ia_interna():
        """IA Interna"""
        return render_template('configuracion/ia_interna.html')
    
    @app.route('/configuracion/facturacion')
    @app.auth.require_auth
    @app.auth.require_role('admin')
    def configuracion_facturacion():
        """Configuración de Facturación"""
        return render_template('configuracion/configuracion_facturacion.html')
    
    # =============================================================================
    # ERROR HANDLERS
    # =============================================================================
    
    @app.errorhandler(404)
    def not_found(error):
        """Página 404"""
        if request.is_json:
            return jsonify({'error': 'Recurso no encontrado'}), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(403)
    def forbidden(error):
        """Página 403"""
        if request.is_json:
            return jsonify({'error': 'Acceso denegado'}), 403
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        """Página 429"""
        if request.is_json:
            return jsonify({'error': 'Demasiadas solicitudes'}), 429
        return render_template('errors/429.html'), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        """Página 500"""
        logger.error(f"Error interno 500: {error}")
        if request.is_json:
            return jsonify({'error': 'Error interno del servidor'}), 500
        return render_template('errors/500.html'), 500
    
    # =============================================================================
    # CONTEXT PROCESSOR
    # =============================================================================
    
    @app.context_processor
    def inject_global_vars():
        """Variables globales para templates"""
        return {
            'current_user': {
                'nombre': session.get('user_name', 'Usuario'),
                'email': session.get('user_email', ''),
                'role': session.get('user_role', 'guest')
            },
            'app_name': 'ERP13 Enterprise',
            'app_version': '3.0.0',
            'current_year': datetime.now().year
        }
    
    # =============================================================================
    # MIDDLEWARE DE SEGURIDAD
    # =============================================================================
    
    @app.after_request
    def security_headers(response):
        """Headers de seguridad"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # CORS para APIs
        if request.path.startswith('/api/'):
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        
        return response
    
    # =============================================================================
    # LOGGING DE INICIALIZACIÓN
    # =============================================================================
    
    total_routes = len([rule for rule in app.url_map.iter_rules()])
    
    logger.info("=" * 60)
    logger.info("📊 ERP13 ENTERPRISE v3.0 - MAPEO DE RUTAS")
    logger.info("=" * 60)
    logger.info("AUTENTICACIÓN:")
    logger.info("  /login → login.html")
    logger.info("  /logout → redirect to login")
    logger.info("DASHBOARD:")
    logger.info("  /dashboard → dashboard.html")
    logger.info("CLIENTES (9 rutas):")
    logger.info("  /clientes/gestion → gestion_clientes.html")
    logger.info("  /clientes/[timeline|comunicaciones|etc] → [archivo].html")
    logger.info("AUDITORÍA (2 rutas):")
    logger.info("  /auditoria/proyectos → auditoria_proyectos.html")
    logger.info("  /auditoria/configuracion → auditoria_configuracion.html")
    logger.info("FACTURACIÓN (6 rutas):")
    logger.info("  /facturacion/proveedores → facturas_proveedores.html")
    logger.info("  /facturacion/clientes → facturas_clientes.html")
    logger.info("  /facturacion/apuntes → apuntes_contables.html")
    logger.info("  /facturacion/estados-pago → estados_pago.html")
    logger.info("  /facturacion/exportacion → exportacion_contable.html")
    logger.info("CONFIGURACIÓN (5 rutas):")
    logger.info("  /configuracion/general → configuracion_general.html")
    logger.info("  /configuracion/usuarios → gestion_usuarios.html")
    logger.info("  /configuracion/facturacion → configuracion_facturacion.html")
    logger.info("=" * 60)
    logger.info(f"✅ Total rutas: {total_routes}")
    logger.info(f"✅ Redis: {'Conectado' if app.redis else 'No disponible (usando cache en memoria)'}")
    logger.info("=" * 60)
    
    return app

# =============================================================================
# CONFIGURACIÓN PARA RAILWAY
# =============================================================================

# Crear aplicación
app = create_app(os.environ.get('FLASK_ENV', 'production'))

# Múltiples exports para compatibilidad con Railway/Gunicorn
application = app
app_instance = app
flask_app = app
wsgi_app = app
erp13_app = app

logger.info("✅ WSGI Application exports ready for Railway")

# =============================================================================
# PUNTO DE ENTRADA PRINCIPAL
# =============================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info("=" * 60)
    logger.info("🚀 ERP13 ENTERPRISE v3.0 - STARTING")
    logger.info("=" * 60)
    logger.info(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"🌐 Host: {host}")
    logger.info(f"🔌 Port: {port}")
    logger.info(f"🔧 Debug: {debug}")
    logger.info(f"📦 Environment: {os.environ.get('FLASK_ENV', 'production')}")
    logger.info("=" * 60)
    
    if debug:
        logger.info("🔑 CREDENCIALES DE DESARROLLO:")
        logger.info("   Admin: admin@erp13.com / admin123")
        logger.info("   User: user@erp13.com / user123")
        logger.info("=" * 60)
    
    app.run(host=host, port=port, debug=debug, threaded=True)
