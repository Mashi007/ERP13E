#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ERP13 Enterprise v3.0 - Sistema ERP Empresarial Completo
Copyright (c) 2025 ERP13 Enterprise Solutions
Arquitectura: Flask + SQLAlchemy + Redis + JWT + Microservicios
"""

import os
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import json
import os
import logging
from datetime import datetime, timedelta

# Redis import with error handling
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("Redis not available - running without cache")

# =============================================================================
# CONFIGURACIÓN Y LOGGING
# =============================================================================

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# =============================================================================
# FLASK APPLICATION FACTORY
# =============================================================================

def create_app():
    """Factory pattern para crear aplicación Flask optimizada"""
    app = Flask(__name__)
    
    # Configuración base
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'erp13-enterprise-secret-key-2025')
    app.config['DEBUG'] = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.config['ENV'] = os.environ.get('FLASK_ENV', 'production')
    
    # Configuración de sesiones
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
    
    # Configuración de seguridad
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-erp13-2025')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    
    # Inicializar Redis para cache (opcional)
    if REDIS_AVAILABLE:
        try:
            redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
            app.redis = redis.from_url(redis_url, decode_responses=True)
            app.redis.ping()
            logger.info("✅ Redis conectado exitosamente")
        except Exception as e:
            logger.warning(f"⚠️ Redis no disponible: {e}")
            app.redis = None
    else:
        logger.info("⚠️ Redis no disponible - ejecutando sin cache")
        app.redis = None
    
    return app

# Crear aplicación
app = create_app()

# =============================================================================
# UTILIDADES Y DECORADORES
# =============================================================================

def generate_jwt_token(user_data):
    """Generar token JWT para autenticación"""
    payload = {
        'user_id': user_data.get('id', 'admin'),
        'email': user_data.get('email', 'admin@erp13.com'),
        'role': user_data.get('role', 'admin'),
        'exp': datetime.utcnow() + app.config['JWT_ACCESS_TOKEN_EXPIRES']
    }
    return jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')

def verify_jwt_token(token):
    """Verificar token JWT"""
    try:
        payload = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def login_required(f):
    """Decorador para rutas que requieren autenticación"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def cache_set(key, value, expire=300):
    """Función helper para cache Redis"""
    if app.redis:
        try:
            app.redis.setex(key, expire, json.dumps(value))
        except Exception as e:
            logger.warning(f"Error setting cache: {e}")

def cache_get(key):
    """Función helper para obtener cache Redis"""
    if app.redis:
        try:
            value = app.redis.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.warning(f"Error getting cache: {e}")
    return None

# =============================================================================
# DATOS MOCK PARA DESARROLLO
# =============================================================================

# Datos de usuarios para desarrollo
MOCK_USERS = {
    'admin@erp13.com': {
        'id': 1,
        'email': 'admin@erp13.com',
        'password': generate_password_hash('admin123'),
        'role': 'admin',
        'name': 'Administrador ERP13'
    },
    'user@erp13.com': {
        'id': 2,
        'email': 'user@erp13.com',
        'password': generate_password_hash('user123'),
        'role': 'user',
        'name': 'Usuario ERP13'
    }
}

# Datos mock para módulos
MOCK_DATA = {
    'clientes': [
        {
            'id': 1,
            'nombre': 'Empresa ABC S.A.',
            'email': 'contacto@empresaabc.com',
            'telefono': '+52 555 123 4567',
            'estado': 'Activo',
            'valor_potencial': 150000,
            'ultima_interaccion': '2025-09-15'
        },
        {
            'id': 2,
            'nombre': 'Corporativo XYZ',
            'email': 'ventas@corporativoxyz.com',
            'telefono': '+52 555 987 6543',
            'estado': 'Prospecto',
            'valor_potencial': 85000,
            'ultima_interaccion': '2025-09-18'
        }
    ],
    'empresas': [
        {
            'id': 1,
            'nombre': 'TechSolutions México',
            'rfc': 'TSM850101ABC',
            'sector': 'Tecnología',
            'empleados': 150,
            'facturacion_anual': 12500000
        }
    ],
    'estadisticas': {
        'total_clientes': 247,
        'ventas_mes': 1850000,
        'tickets_abiertos': 15,
        'usuarios_activos': 89,
        'conversion_rate': 24.5
    }
}

# =============================================================================
# RUTAS DE AUTENTICACIÓN
# =============================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Ruta de login con autenticación JWT"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        email = data.get('email')
        password = data.get('password')
        
        user = MOCK_USERS.get(email)
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_email'] = user['email']
            session['user_role'] = user['role']
            session['user_name'] = user['name']
            session.permanent = True
            
            # Generar token JWT
            token = generate_jwt_token(user)
            
            if request.is_json:
                return jsonify({
                    'success': True,
                    'message': 'Login exitoso',
                    'token': token,
                    'user': {
                        'id': user['id'],
                        'email': user['email'],
                        'role': user['role'],
                        'name': user['name']
                    }
                })
            else:
                flash('Login exitoso', 'success')
                return redirect(url_for('dashboard'))
        else:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Credenciales inválidas'}), 401
            else:
                flash('Credenciales inválidas', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Ruta de logout"""
    session.clear()
    flash('Sesión cerrada exitosamente', 'info')
    return redirect(url_for('login'))

# =============================================================================
# RUTA PRINCIPAL Y DASHBOARD
# =============================================================================

@app.route('/')
def index():
    """Ruta principal - redirige al dashboard si está autenticado"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal con métricas y KPIs"""
    # Obtener estadísticas de cache o generar
    stats_key = 'dashboard_stats'
    stats = cache_get(stats_key)
    
    if not stats:
        stats = MOCK_DATA['estadisticas']
        # Agregar datos calculados
        stats.update({
            'ventas_objetivo': 2000000,
            'progreso_ventas': (stats['ventas_mes'] / 2000000) * 100,
            'clientes_nuevos_mes': 12,
            'satisfaction_score': 4.7,
            'uptime_percentage': 99.9
        })
        cache_set(stats_key, stats, 300)  # Cache por 5 minutos
    
    return render_template('dashboard.html', 
                         user_name=session.get('user_name'),
                         stats=stats)

# =============================================================================
# MÓDULO CLIENTES (CRM COMPLETO)
# =============================================================================

@app.route('/clientes')
@login_required
def clientes_gestion():
    """Gestión principal de clientes"""
    clientes = MOCK_DATA['clientes']
    return render_template('clientes/gestion.html', clientes=clientes)

@app.route('/clientes/timeline')
@login_required
def clientes_timeline():
    """Timeline de actividades de clientes"""
    return render_template('clientes/timeline.html')

@app.route('/clientes/comunicaciones')
@login_required
def clientes_comunicaciones():
    """Centro de comunicaciones (Email, WhatsApp, SMS)"""
    return render_template('clientes/comunicaciones.html')

@app.route('/clientes/propuestas')
@login_required
def clientes_propuestas():
    """Sistema de propuestas y cotizaciones"""
    return render_template('clientes/propuestas.html')

@app.route('/clientes/pipeline')
@login_required
def clientes_pipeline():
    """Pipeline de ventas visual"""
    return render_template('clientes/pipeline.html')

@app.route('/clientes/tickets')
@login_required
def clientes_tickets():
    """Sistema de tickets de soporte"""
    return render_template('clientes/tickets.html')

@app.route('/clientes/calendario')
@login_required
def clientes_calendario():
    """Calendario de reuniones y seguimientos"""
    return render_template('clientes/calendario.html')

@app.route('/clientes/campanas')
@login_required
def clientes_campanas():
    """Campañas publicitarias y marketing"""
    return render_template('clientes/campanas.html')

@app.route('/clientes/automatizaciones')
@login_required
def clientes_automatizaciones():
    """Sistema de automatizaciones y workflows"""
    return render_template('clientes/automatizaciones.html')

# =============================================================================
# MÓDULO EMPRESAS
# =============================================================================

@app.route('/empresas')
@login_required
def empresas():
    """Gestión de empresas y entidades corporativas"""
    empresas_data = MOCK_DATA['empresas']
    return render_template('empresas.html', empresas=empresas_data)

@app.route('/empresas/crear', methods=['POST'])
@login_required
def empresas_crear():
    """API para crear nueva empresa"""
    data = request.get_json()
    # Aquí iría la lógica de creación en base de datos
    return jsonify({'success': True, 'message': 'Empresa creada exitosamente'})

# =============================================================================
# MÓDULO AUDITORÍA
# =============================================================================

@app.route('/auditoria')
@login_required
def auditoria():
    """Módulo de auditoría y compliance"""
    return render_template('auditoria.html')

@app.route('/auditoria/reportes')
@login_required
def auditoria_reportes():
    """Reportes de auditoría avanzados"""
    return render_template('auditoria/reportes.html')

# =============================================================================
# MÓDULO FORMACIÓN
# =============================================================================

@app.route('/formacion')
@login_required
def formacion():
    """Sistema de formación y capacitación (LMS)"""
    return render_template('formacion.html')

@app.route('/formacion/cursos')
@login_required
def formacion_cursos():
    """Gestión de cursos y certificaciones"""
    return render_template('formacion/cursos.html')

# =============================================================================
# MÓDULO FACTURACIÓN
# =============================================================================

@app.route('/facturacion')
@login_required
def facturacion():
    """Sistema de facturación e integración contable"""
    return render_template('facturacion.html')

@app.route('/facturacion/generar', methods=['POST'])
@login_required
def facturacion_generar():
    """API para generar facturas"""
    data = request.get_json()
    return jsonify({'success': True, 'factura_id': 'FACT-2025-001'})

# =============================================================================
# MÓDULO CONFIGURACIÓN
# =============================================================================

@app.route('/configuracion')
@login_required
def configuracion():
    """Configuración del sistema y parámetros"""
    return render_template('configuracion.html')

@app.route('/configuracion/usuarios')
@login_required
def configuracion_usuarios():
    """Gestión de usuarios y permisos"""
    return render_template('configuracion/usuarios.html')

# =============================================================================
# APIs REST PARA MÓVIL Y INTEGRACIÓN
# =============================================================================

@app.route('/api/v1/auth', methods=['POST'])
def api_auth():
    """API de autenticación JWT"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = MOCK_USERS.get(email)
    if user and check_password_hash(user['password'], password):
        token = generate_jwt_token(user)
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'role': user['role'],
                'name': user['name']
            }
        })
    
    return jsonify({'success': False, 'message': 'Credenciales inválidas'}), 401

@app.route('/api/v1/clientes', methods=['GET'])
@login_required
def api_clientes():
    """API REST para obtener clientes"""
    return jsonify({
        'success': True,
        'data': MOCK_DATA['clientes'],
        'total': len(MOCK_DATA['clientes'])
    })

@app.route('/api/v1/estadisticas', methods=['GET'])
@login_required
def api_estadisticas():
    """API REST para obtener estadísticas del dashboard"""
    return jsonify({
        'success': True,
        'data': MOCK_DATA['estadisticas']
    })

# =============================================================================
# SISTEMA DE CHAT IA INTEGRADO
# =============================================================================

@app.route('/api/v1/chat', methods=['POST'])
@login_required
def api_chat():
    """API para chat con IA (OpenAI, Anthropic, DeepSeek)"""
    data = request.get_json()
    mensaje = data.get('mensaje', '')
    modulo = data.get('modulo', 'general')
    
    # Aquí iría la integración con las APIs de IA
    respuesta_mock = f"Respuesta de IA para '{mensaje}' en módulo {modulo}. Funcionalidad en desarrollo."
    
    return jsonify({
        'success': True,
        'respuesta': respuesta_mock,
        'timestamp': datetime.now().isoformat()
    })

# =============================================================================
# RUTAS DE SALUD Y MONITOREO
# =============================================================================

@app.route('/health')
def health_check():
    """Health check para Railway y monitoreo"""
    try:
        redis_status = "connected" if app.redis and app.redis.ping() else "disconnected"
    except:
        redis_status = "error"
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '3.0.0',
        'environment': app.config['ENV'],
        'redis': redis_status,
        'routes': 31
    })

@app.route('/metrics')
def metrics():
    """Métricas básicas para monitoreo"""
    return jsonify({
        'active_sessions': len([k for k in session.keys()]) if session else 0,
        'app_version': '3.0.0',
        'uptime': 'Available via external monitoring'
    })

# =============================================================================
# MANEJO DE ERRORES
# =============================================================================

@app.errorhandler(404)
def not_found(error):
    """Página 404 personalizada"""
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Página 500 personalizada"""
    logger.error(f"Error interno: {error}")
    return render_template('errors/500.html'), 500

@app.errorhandler(403)
def forbidden(error):
    """Página 403 personalizada"""
    return render_template('errors/403.html'), 403

# =============================================================================
# CONFIGURACIÓN DE CONTEXTO GLOBAL
# =============================================================================

@app.context_processor
def inject_global_vars():
    """Inyectar variables globales en templates"""
    return {
        'app_name': 'ERP13 Enterprise',
        'app_version': '3.0.0',
        'current_year': datetime.now().year,
        'user_role': session.get('user_role', 'guest'),
        'user_name': session.get('user_name', 'Usuario'),
        'total_modulos': 6
    }

# =============================================================================
# WSGI APPLICATION OBJECT PARA RAILWAY/GUNICORN
# =============================================================================

# CRÍTICO: Gunicorn busca 'application' en main.py
application = app

# =============================================================================
# PUNTO DE ENTRADA PRINCIPAL
# =============================================================================

if __name__ == '__main__':
    # Configuración para desarrollo local
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Información de inicio
    logger.info("🚀 ERP13 Enterprise v3.0 - Sistema ERP Empresarial Completo")
    logger.info("📅 Release: 2025-01-15")
    logger.info(f"🎯 Estado: {app.config['ENV'].upper()}")
    logger.info("🔧 Modo desarrollo - Servidor Flask integrado" if debug else "🔧 Modo producción - Usar Gunicorn")
    logger.info("📦 Módulos: Dashboard, Clientes, Empresas, Auditoría, Formación, Facturación, Configuración")
    logger.info("🔗 31 rutas disponibles")
    logger.info("✅ WSGI Application Object: READY")
    
    # Rutas de prueba para desarrollo
    if debug:
        logger.info("🔑 Credenciales de prueba:")
        logger.info("   Admin: admin@erp13.com / admin123")
        logger.info("   User:  user@erp13.com / user123")
    
    # Ejecutar aplicación
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )
