#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ERP13 Enterprise - Main Application
Railway Compatible Flask Application
"""

import os
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Crear aplicación Flask
app = Flask(__name__)

# Configuración de la aplicación
app.config.update({
    'SECRET_KEY': os.environ.get('SECRET_KEY', 'erp13-enterprise-secret-key-2025'),
    'ENV': os.environ.get('FLASK_ENV', 'production'),
    'DEBUG': False,
    'PERMANENT_SESSION_LIFETIME': timedelta(hours=24),
    'SESSION_COOKIE_SECURE': False,  # Railway maneja HTTPS
    'SESSION_COOKIE_HTTPONLY': True,
    'SESSION_COOKIE_SAMESITE': 'Lax'
})

logger.info("ERP13 Enterprise Application initializing...")

# ============================================================================
# HEALTH CHECKS PARA RAILWAY
# ============================================================================

@app.route('/health')
def health_check():
    """Health check principal para Railway"""
    try:
        return jsonify({
            'status': 'healthy',
            'version': '3.1.0',
            'service': 'ERP13-Enterprise',
            'timestamp': datetime.utcnow().isoformat(),
            'environment': app.config['ENV']
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/health/ready')
def readiness_check():
    """Readiness check para Railway"""
    return jsonify({
        'status': 'ready',
        'checks': {
            'flask_app': True,
            'config_loaded': bool(app.config.get('SECRET_KEY')),
            'routes_available': True
        }
    }), 200

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def render_fallback_template(template_name, **kwargs):
    """Renderizar template con fallback HTML"""
    try:
        return render_template(template_name, **kwargs)
    except Exception as e:
        logger.warning(f"Template {template_name} not found, using fallback: {e}")
        
        # Templates de fallback básicos
        if template_name == 'login.html':
            return f"""
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>ERP13 Enterprise - Login</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        margin: 0;
                        padding: 0;
                        min-height: 100vh;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                    }}
                    .login-container {{
                        background: white;
                        padding: 40px;
                        border-radius: 10px;
                        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
                        width: 100%;
                        max-width: 400px;
                    }}
                    .logo {{
                        text-align: center;
                        margin-bottom: 30px;
                    }}
                    .logo h1 {{
                        color: #333;
                        margin: 0;
                        font-size: 28px;
                    }}
                    .form-group {{
                        margin-bottom: 20px;
                    }}
                    label {{
                        display: block;
                        margin-bottom: 5px;
                        color: #555;
                        font-weight: 500;
                    }}
                    input[type="text"], input[type="password"] {{
                        width: 100%;
                        padding: 12px;
                        border: 2px solid #ddd;
                        border-radius: 6px;
                        font-size: 16px;
                        box-sizing: border-box;
                        transition: border-color 0.3s;
                    }}
                    input[type="text"]:focus, input[type="password"]:focus {{
                        outline: none;
                        border-color: #667eea;
                    }}
                    .btn-login {{
                        width: 100%;
                        padding: 12px;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        border: none;
                        border-radius: 6px;
                        font-size: 16px;
                        font-weight: 600;
                        cursor: pointer;
                        transition: opacity 0.3s;
                    }}
                    .btn-login:hover {{
                        opacity: 0.9;
                    }}
                    .alert {{
                        padding: 10px;
                        margin-bottom: 20px;
                        border-radius: 4px;
                    }}
                    .alert-error {{
                        background-color: #f8d7da;
                        color: #721c24;
                        border: 1px solid #f5c6cb;
                    }}
                    .alert-success {{
                        background-color: #d4edda;
                        color: #155724;
                        border: 1px solid #c3e6cb;
                    }}
                    .demo-credentials {{
                        margin-top: 20px;
                        padding: 15px;
                        background: #f8f9fa;
                        border-radius: 6px;
                        font-size: 14px;
                        color: #6c757d;
                    }}
                </style>
            </head>
            <body>
                <div class="login-container">
                    <div class="logo">
                        <h1>ERP13 Enterprise</h1>
                        <p style="color: #666; margin: 0;">Sistema de Gestión Empresarial</p>
                    </div>
                    
                    {{% for message in get_flashed_messages() %}}
                        <div class="alert alert-error">{{{{ message }}}}</div>
                    {{% endfor %}}
                    
                    <form method="POST" action="/login">
                        <div class="form-group">
                            <label for="username">Usuario:</label>
                            <input type="text" id="username" name="username" required>
                        </div>
                        
                        <div class="form-group">
                            <label for="password">Contraseña:</label>
                            <input type="password" id="password" name="password" required>
                        </div>
                        
                        <button type="submit" class="btn-login">Iniciar Sesión</button>
                    </form>
                    
                    <div class="demo-credentials">
                        <strong>Credenciales de prueba:</strong><br>
                        Usuario: <code>admin</code><br>
                        Contraseña: <code>admin123</code>
                    </div>
                </div>
            </body>
            </html>
            """
        
        elif template_name == 'dashboard.html':
            return f"""
            <!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Dashboard - ERP13 Enterprise</title>
                <style>
                    * {{
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                    }}
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background-color: #f5f5f5;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 1rem 2rem;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    }}
                    .logo h1 {{
                        font-size: 24px;
                    }}
                    .user-info {{
                        display: flex;
                        align-items: center;
                        gap: 1rem;
                    }}
                    .btn-logout {{
                        background: rgba(255,255,255,0.2);
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 4px;
                        text-decoration: none;
                        cursor: pointer;
                    }}
                    .btn-logout:hover {{
                        background: rgba(255,255,255,0.3);
                    }}
                    .container {{
                        max-width: 1200px;
                        margin: 0 auto;
                        padding: 2rem;
                    }}
                    .stats-grid {{
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                        gap: 1.5rem;
                        margin-bottom: 2rem;
                    }}
                    .stat-card {{
                        background: white;
                        padding: 1.5rem;
                        border-radius: 8px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        text-align: center;
                    }}
                    .stat-number {{
                        font-size: 2.5rem;
                        font-weight: bold;
                        color: #667eea;
                        margin-bottom: 0.5rem;
                    }}
                    .stat-label {{
                        color: #666;
                        font-size: 1rem;
                    }}
                    .modules-grid {{
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                        gap: 1.5rem;
                    }}
                    .module-card {{
                        background: white;
                        padding: 1.5rem;
                        border-radius: 8px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        text-align: center;
                        text-decoration: none;
                        color: inherit;
                        transition: transform 0.2s;
                    }}
                    .module-card:hover {{
                        transform: translateY(-2px);
                        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
                    }}
                    .module-icon {{
                        font-size: 3rem;
                        margin-bottom: 1rem;
                    }}
                    .alert {{
                        padding: 1rem;
                        margin-bottom: 1rem;
                        border-radius: 4px;
                    }}
                    .alert-success {{
                        background-color: #d4edda;
                        color: #155724;
                        border: 1px solid #c3e6cb;
                    }}
                </style>
            </head>
            <body>
                <header class="header">
                    <div class="logo">
                        <h1>ERP13 Enterprise</h1>
                    </div>
                    <div class="user-info">
                        <span>Bienvenido, {{{{ session.get('username', 'Usuario') }}}}</span>
                        <a href="/logout" class="btn-logout">Cerrar Sesión</a>
                    </div>
                </header>
                
                <div class="container">
                    {{% for message in get_flashed_messages() %}}
                        <div class="alert alert-success">{{{{ message }}}}</div>
                    {{% endfor %}}
                    
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-number">156</div>
                            <div class="stat-label">Total Clientes</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">23</div>
                            <div class="stat-label">Facturas Pendientes</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">$45,678</div>
                            <div class="stat-label">Ingresos del Mes</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">12</div>
                            <div class="stat-label">Productos Stock Bajo</div>
                        </div>
                    </div>
                    
                    <h2 style="margin-bottom: 1.5rem; color: #333;">Módulos del Sistema</h2>
                    
                    <div class="modules-grid">
                        <a href="/clientes" class="module-card">
                            <div class="module-icon">👥</div>
                            <h3>Clientes</h3>
                            <p>Gestión de clientes y contactos</p>
                        </a>
                        
                        <a href="/facturas" class="module-card">
                            <div class="module-icon">📄</div>
                            <h3>Facturación</h3>
                            <p>Emisión y control de facturas</p>
                        </a>
                        
                        <a href="/productos" class="module-card">
                            <div class="module-icon">📦</div>
                            <h3>Productos</h3>
                            <p>Inventario y catálogo</p>
                        </a>
                        
                        <a href="/reportes" class="module-card">
                            <div class="module-icon">📊</div>
                            <h3>Reportes</h3>
                            <p>Análisis y estadísticas</p>
                        </a>
                        
                        <a href="/configuracion" class="module-card">
                            <div class="module-icon">⚙️</div>
                            <h3>Configuración</h3>
                            <p>Ajustes del sistema</p>
                        </a>
                    </div>
                </div>
            </body>
            </html>
            """
        
        else:
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>ERP13 Enterprise</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }}
                    .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }}
                    h1 {{ color: #333; }}
                    .btn {{ background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>ERP13 Enterprise</h1>
                    <p>Módulo: {template_name}</p>
                    <a href="/dashboard" class="btn">Volver al Dashboard</a>
                </div>
            </body>
            </html>
            """

def require_login(f):
    """Decorador para rutas que requieren autenticación"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debe iniciar sesión para acceder a esta página', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ============================================================================
# RUTAS DE AUTENTICACIÓN
# ============================================================================

@app.route('/')
def index():
    """Página principal - redirige al dashboard si está autenticado"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login de usuarios"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash('Debe ingresar usuario y contraseña', 'error')
            return render_fallback_template('login.html')
        
        # Validación de credenciales (base de datos simplificada)
        valid_users = {
            'admin': {'password': 'admin123', 'role': 'admin', 'name': 'Administrador'},
            'user': {'password': 'user123', 'role': 'user', 'name': 'Usuario'},
            'demo': {'password': 'demo123', 'role': 'demo', 'name': 'Demo User'}
        }
        
        if username in valid_users and valid_users[username]['password'] == password:
            session['user_id'] = hash(username)
            session['username'] = username
            session['role'] = valid_users[username]['role']
            session['name'] = valid_users[username]['name']
            session.permanent = True
            
            logger.info(f"Login successful: {username}")
            flash(f'Bienvenido al sistema ERP13 Enterprise, {valid_users[username]["name"]}', 'success')
            return redirect(url_for('dashboard'))
        else:
            logger.warning(f"Login failed for user: {username}")
            flash('Credenciales inválidas. Verifique usuario y contraseña.', 'error')
    
    return render_fallback_template('login.html')

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    username = session.get('username', 'Unknown')
    session.clear()
    logger.info(f"Logout successful: {username}")
    flash('Sesión cerrada correctamente', 'success')
    return redirect(url_for('login'))

# ============================================================================
# DASHBOARD Y MÓDULOS PRINCIPALES
# ============================================================================

@app.route('/dashboard')
@require_login
def dashboard():
    """Dashboard principal del ERP"""
    try:
        return render_fallback_template('dashboard.html')
    except Exception as e:
        logger.error(f"Error en dashboard: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/clientes')
@require_login
def clientes():
    """Módulo de gestión de clientes"""
    return render_fallback_template('clientes.html')

@app.route('/facturas')
@require_login
def facturas():
    """Módulo de facturación"""
    return render_fallback_template('facturas.html')

@app.route('/productos')
@require_login
def productos():
    """Módulo de productos e inventario"""
    return render_fallback_template('productos.html')

@app.route('/reportes')
@require_login
def reportes():
    """Módulo de reportes y estadísticas"""
    return render_fallback_template('reportes.html')

@app.route('/configuracion')
@require_login
def configuracion():
    """Módulo de configuración del sistema"""
    return render_fallback_template('configuracion.html')

# ============================================================================
# API ENDPOINTS BÁSICOS
# ============================================================================

@app.route('/api/status')
def api_status():
    """API endpoint para verificar estado del sistema"""
    return jsonify({
        'status': 'operational',
        'version': '3.1.0',
        'modules': ['dashboard', 'clientes', 'facturas', 'productos', 'reportes', 'configuracion'],
        'authenticated': 'user_id' in session,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/session')
def api_session():
    """API endpoint para información de sesión"""
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'username': session.get('username'),
            'role': session.get('role'),
            'name': session.get('name')
        })
    else:
        return jsonify({'authenticated': False}), 401

# ============================================================================
# MANEJO DE ERRORES
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Manejo de errores 404"""
    return jsonify({
        'error': 'Página no encontrada',
        'message': 'La página solicitada no existe',
        'code': 404
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Manejo de errores 500"""
    logger.error(f"Error interno del servidor: {error}")
    return jsonify({
        'error': 'Error interno del servidor',
        'message': 'Ha ocurrido un error inesperado',
        'code': 500
    }), 500

@app.errorhandler(403)
def forbidden(error):
    """Manejo de errores 403"""
    return jsonify({
        'error': 'Acceso prohibido',
        'message': 'No tiene permisos para acceder a este recurso',
        'code': 403
    }), 403

# ============================================================================
# MIDDLEWARE Y HOOKS
# ============================================================================

@app.before_request
def before_request():
    """Middleware ejecutado antes de cada request"""
    # Agregar información de request al log (solo en desarrollo)
    if app.config['ENV'] == 'development':
        logger.debug(f"{request.method} {request.path} from {request.remote_addr}")

@app.after_request
def after_request(response):
    """Middleware ejecutado después de cada request"""
    # Headers de seguridad
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Server'] = 'ERP13E-3.1'
    
    return response

# ============================================================================
# CONFIGURACIÓN FINAL
# ============================================================================

# Configurar logging según el entorno
if app.config['ENV'] == 'production':
    logger.setLevel(logging.INFO)
else:
    logger.setLevel(logging.DEBUG)

# Log de inicialización
logger.info("ERP13 Enterprise Main Application initialized successfully")
logger.info(f"Environment: {app.config['ENV']}")
logger.info(f"Debug mode: {app.config['DEBUG']}")

# CRÍTICO: Esta línea es necesaria para que Gunicorn encuentre la aplicación
application = app

if __name__ == '__main__':
    # Configuración para desarrollo local
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info("🚀 ERP13 Enterprise v3.1 - Sistema ERP Empresarial")
    logger.info(f"🎯 Entorno: {app.config['ENV'].upper()}")
    logger.info(f"🔌 Puerto: {port}")
    logger.info("🔧 Modo desarrollo" if debug else "🔧 Modo producción")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )
