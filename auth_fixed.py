#!/usr/bin/env python3
"""
📁 Ruta: /app/auth_fixed.py
📄 Nombre: auth_fixed.py  
🏗️ Propósito: Authentication module ERP13 Enterprise v3.1 - COMPLETO
⚡ Performance: Optimizado Railway, función setup_default_auth_config incluida
🔒 Seguridad: Demo users con validación robusta
"""

from flask import Blueprint, session, redirect, url_for, jsonify, flash
import logging
from datetime import datetime, timedelta
from functools import wraps

logger = logging.getLogger('ERP13_Auth')

# Blueprint de autenticación
auth_bp = Blueprint('auth_fixed', __name__)

# Usuarios demo
DEMO_USERS = {
    'admin': {
        'password': 'admin123',
        'role': 'administrator',
        'email': 'admin@erp13.com'
    },
    'user': {
        'password': 'user123', 
        'role': 'user',
        'email': 'user@erp13.com'
    }
}

def setup_default_auth_config(app):
    """Configuración por defecto de autenticación - FUNCIÓN REQUERIDA POR MAIN.PY"""
    app.config.setdefault('SESSION_PERMANENT', True)
    app.config.setdefault('PERMANENT_SESSION_LIFETIME', timedelta(hours=24))
    
    # Configurar secret key si no existe
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = 'erp13-enterprise-fallback-key'
    
    logger.info("✅ Auth default configuration applied")
    return True

def validate_credentials(username, password):
    """Validar credenciales demo"""
    if username in DEMO_USERS:
        if DEMO_USERS[username]['password'] == password:
            return True, DEMO_USERS[username]
    return False, None

def create_session(username, user_data):
    """Crear sesión de usuario"""
    try:
        session.permanent = True
        session['user_id'] = username
        session['username'] = username
        session['logged_in'] = True
        session['role'] = user_data['role']
        session['email'] = user_data['email']
        session['login_time'] = datetime.now().isoformat()
        
        logger.info(f"Session created for user: {username}")
        return True
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        return False

@auth_bp.route('/health')
def auth_health():
    """Health check del módulo auth"""
    return jsonify({
        'status': 'healthy',
        'module': 'auth_fixed',
        'timestamp': datetime.now().isoformat(),
        'users_available': len(DEMO_USERS)
    })

def login_required(f):
    """Decorador login required"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('auth_login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    """Decorador admin required"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('auth_login'))
        if session.get('role') != 'administrator':
            flash('Acceso denegado. Se requieren permisos de administrador.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated

def get_current_user():
    """Obtener usuario actual"""
    if session.get('logged_in'):
        return {
            'username': session.get('username'),
            'role': session.get('role'),
            'email': session.get('email')
        }
    return None

# Exportar funciones para main.py
__all__ = [
    'auth_bp',
    'setup_default_auth_config',
    'login_required', 
    'admin_required',
    'get_current_user',
    'validate_credentials',
    'create_session'
]
