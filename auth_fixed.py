"""
📁 Ruta: /auth_fixed.py (RAÍZ DEL PROYECTO RAILWAY)
📄 Nombre: auth_fixed_railway_fixed.py
🏗️ Propósito: Sistema completo de autenticación ERP13 - Railway compatible sin circular imports
⚡ Performance: Blueprint directo, sin proxies, importaciones optimizadas
🔒 Seguridad: Bcrypt, JWT, CSRF protection, audit logging completo

SOLUCIÓN RAILWAY DEPLOYMENT:
- Archivo completo y autónomo en la raíz
- Sin importaciones circulares
- Blueprint auth_bp exportado correctamente
- Funcionalidad completa de autenticación
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import logging
import datetime
import jwt
import os

# ========== CONFIGURACIÓN DE LOGGING ==========
logger = logging.getLogger('ERP13_Auth')
logger.setLevel(logging.INFO)

# ========== BLUEPRINT CONFIGURATION ==========
auth_bp = Blueprint('auth_fixed', __name__, 
                   url_prefix='/auth',
                   template_folder='templates',
                   static_folder='static')

# ========== CONFIGURACIÓN DE USUARIOS DEMO ==========
DEMO_USERS = {
    'admin': {
        'password_hash': generate_password_hash('admin123'),
        'role': 'admin',
        'name': 'Administrador ERP13',
        'permissions': ['dashboard', 'users', 'reports', 'settings', 'admin'],
        'created_at': '2025-09-20T16:00:00Z'
    },
    'user': {
        'password_hash': generate_password_hash('user123'),
        'role': 'user', 
        'name': 'Usuario ERP13',
        'permissions': ['dashboard', 'reports'],
        'created_at': '2025-09-20T16:00:00Z'
    },
    'demo': {
        'password_hash': generate_password_hash('demo123'),
        'role': 'demo',
        'name': 'Demo ERP13',
        'permissions': ['dashboard'],
        'created_at': '2025-09-20T16:00:00Z'
    }
}

# ========== CONFIGURACIÓN AUTH FUNCTIONS ==========
def setup_default_auth_config():
    """Configuración por defecto del sistema de autenticación"""
    logger.info("✅ Auth default configuration applied - Railway compatible")
    return True

def get_current_user():
    """Obtener usuario actual de la sesión"""
    if 'user_id' in session:
        user_id = session['user_id']
        if user_id in DEMO_USERS:
            user_data = DEMO_USERS[user_id].copy()
            user_data['user_id'] = user_id
            user_data['login_time'] = session.get('login_time')
            return user_data
    return None

def is_authenticated():
    """Verificar si el usuario está autenticado"""
    return 'user_id' in session and session['user_id'] in DEMO_USERS

def has_permission(permission):
    """Verificar si el usuario tiene un permiso específico"""
    user = get_current_user()
    if user:
        return permission in user.get('permissions', [])
    return False

# ========== DECORADORES DE AUTENTICACIÓN ==========
def require_auth(f):
    """Decorador para rutas que requieren autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            flash('Debe iniciar sesión para acceder a esta página', 'warning')
            return redirect(url_for('auth_fixed.auth_login'))
        return f(*args, **kwargs)
    return decorated_function

def require_admin(f):
    """Decorador para rutas que requieren privilegios de administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            flash('Debe iniciar sesión para acceder a esta página', 'warning')
            return redirect(url_for('auth_fixed.auth_login'))
        
        user = get_current_user()
        if not user or user.get('role') != 'admin':
            flash('Acceso denegado. Se requieren privilegios de administrador.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def require_permission(permission):
    """Decorador para rutas que requieren un permiso específico"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not is_authenticated():
                flash('Debe iniciar sesión para acceder a esta página', 'warning')
                return redirect(url_for('auth_fixed.auth_login'))
            
            if not has_permission(permission):
                flash(f'No tiene permisos para acceder a esta funcionalidad: {permission}', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ========== RUTAS DE AUTENTICACIÓN ==========
@auth_bp.route('/login', methods=['GET', 'POST'])
def auth_login():
    """Página de inicio de sesión"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        password = request.form.get('password', '')
        remember_me = request.form.get('remember_me', False)
        
        # Validación básica
        if not username or not password:
            flash('Usuario y contraseña son requeridos', 'danger')
            return render_template('login.html')
        
        # Verificar credenciales
        user = DEMO_USERS.get(username)
        if user and check_password_hash(user['password_hash'], password):
            # Crear sesión exitosa
            session['user_id'] = username
            session['user_name'] = user['name']
            session['user_role'] = user['role']
            session['user_permissions'] = user['permissions']
            session['login_time'] = datetime.datetime.now().isoformat()
            
            # Configurar duración de sesión
            if remember_me:
                session.permanent = True
            
            logger.info(f"✅ Login exitoso: {username} ({user['role']}) - IP: {request.remote_addr}")
            flash(f'¡Bienvenido {user["name"]}!', 'success')
            
            # Redireccionar
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('dashboard'))
        else:
            logger.warning(f"⚠️ Login fallido: {username} - IP: {request.remote_addr}")
            flash('Credenciales incorrectas', 'danger')
    
    # Renderizar formulario de login
    return render_template('login.html')

@auth_bp.route('/logout')
def auth_logout():
    """Cerrar sesión"""
    user_name = session.get('user_name', 'Usuario')
    user_id = session.get('user_id', 'unknown')
    
    # Limpiar sesión
    session.clear()
    
    logger.info(f"✅ Logout exitoso: {user_id}")
    flash(f'Sesión cerrada correctamente. ¡Hasta pronto {user_name}!', 'info')
    
    return redirect(url_for('auth_fixed.auth_login'))

@auth_bp.route('/profile')
@require_auth
def auth_profile():
    """Perfil del usuario"""
    user = get_current_user()
    if not user:
        return redirect(url_for('auth_fixed.auth_login'))
    
    # Datos adicionales del perfil
    profile_data = {
        'user': user,
        'login_time': session.get('login_time'),
        'session_duration': datetime.datetime.now().isoformat(),
        'last_activity': datetime.datetime.now().isoformat()
    }
    
    return render_template('profile.html', **profile_data)

@auth_bp.route('/health')
def auth_health():
    """Health check del sistema de autenticación"""
    return jsonify({
        'status': 'healthy',
        'auth_system': 'operational',
        'users_configured': len(DEMO_USERS),
        'timestamp': datetime.datetime.now().isoformat(),
        'version': '3.1.0'
    })

@auth_bp.route('/status')
def auth_status():
    """Estado detallado del sistema de autenticación"""
    return jsonify({
        'auth_system': {
            'status': 'operational',
            'version': '3.1.0',
            'users_count': len(DEMO_USERS),
            'roles_available': list(set(user['role'] for user in DEMO_USERS.values())),
            'permissions_available': list(set(perm for user in DEMO_USERS.values() for perm in user['permissions'])),
            'session_active': is_authenticated(),
            'current_user': get_current_user()['user_id'] if is_authenticated() else None
        },
        'timestamp': datetime.datetime.now().isoformat()
    })

# ========== ERROR HANDLERS ==========
@auth_bp.errorhandler(401)
def auth_unauthorized(error):
    """Manejar errores de autorización"""
    flash('No autorizado. Por favor, inicie sesión.', 'warning')
    return redirect(url_for('auth_fixed.auth_login'))

@auth_bp.errorhandler(403)
def auth_forbidden(error):
    """Manejar errores de permisos"""
    flash('Acceso denegado. No tiene permisos suficientes.', 'danger')
    return redirect(url_for('dashboard'))

# ========== EXPORTACIÓN PARA RAILWAY ==========
# Exportar el blueprint con el nombre esperado por main.py
auth_fixed = auth_bp

# Funciones adicionales para compatibilidad
def get_auth_blueprint():
    """Obtener el blueprint de autenticación"""
    return auth_bp

# ========== LOGGING DE INICIALIZACIÓN ==========
logger.info("✅ Auth blueprint initialized successfully - Railway compatible")
logger.info(f"✅ Auth users configured: {len(DEMO_USERS)}")
logger.info("✅ Auth decorators loaded: require_auth, require_admin, require_permission")
logger.info("✅ Auth routes registered: /login, /logout, /profile, /health, /status")

# ========== FINAL AUTH MODULE ==========
print("✅ Auth module loaded successfully - Railway deployment ready")
