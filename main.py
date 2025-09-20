#!/usr/bin/env python3
"""
ERP13 Enterprise - VERSIÓN MINIMAL QUE FUNCIONA
Basado en logs de conversaciones exitosas anteriores
"""

import os
import logging
from datetime import datetime
from flask import Flask, jsonify, render_template_string, request, session, redirect, url_for

# Logging básico
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ERP13')

# Crear aplicación Flask básica
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'erp13-key-basic')

# Variables globales simples
start_time = datetime.utcnow()

# ========== HEALTH CHECK SIMPLE ==========
@app.route('/health')
def health():
    """Health check básico que funciona"""
    return jsonify({
        'status': 'healthy',
        'service': 'ERP13-Enterprise',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

# ========== RUTAS BÁSICAS ==========
@app.route('/')
def index():
    """Página principal simple"""
    if 'logged_in' in session:
        return redirect('/dashboard')
    return redirect('/login')

@app.route('/login')
def login_page():
    """Página de login simple"""
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>ERP13 Login</title></head>
    <body style="margin:50px;font-family:Arial;">
        <h2>ERP13 Enterprise Login</h2>
        <form method="POST" action="/do_login">
            <p><input type="text" name="username" placeholder="Usuario" required style="padding:10px;"></p>
            <p><input type="password" name="password" placeholder="Contraseña" required style="padding:10px;"></p>
            <p><button type="submit" style="padding:10px;">Iniciar Sesión</button></p>
        </form>
        <p><small>Demo: admin/admin123</small></p>
    </body>
    </html>
    '''

@app.route('/do_login', methods=['POST'])
def do_login():
    """Proceso de login simple"""
    username = request.form.get('username')
    password = request.form.get('password')
    
    if username == 'admin' and password == 'admin123':
        session['logged_in'] = True
        session['username'] = username
        logger.info(f"Login exitoso: {username}")
        return redirect('/dashboard')
    
    return redirect('/login')

@app.route('/dashboard')
def dashboard():
    """Dashboard simple"""
    if 'logged_in' not in session:
        return redirect('/login')
    
    username = session.get('username', 'Usuario')
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>ERP13 Dashboard</title>
        <style>
            body {{ margin:0; font-family:Arial; }}
            .header {{ background:#2c3e50; color:white; padding:20px; }}
            .content {{ padding:20px; }}
            .card {{ background:#f8f9fa; padding:20px; margin:10px 0; border-radius:5px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>ERP13 Enterprise Dashboard</h1>
            <p>Bienvenido, {username} | <a href="/logout" style="color:white;">Cerrar Sesión</a></p>
        </div>
        <div class="content">
            <div class="card">
                <h3>📊 Métricas</h3>
                <p>Clientes: 1,247 | Facturas: 847 | Ventas: $2.3M</p>
            </div>
            <div class="card">
                <h3>🔧 Accesos Rápidos</h3>
                <p><a href="/clientes">Clientes</a> | <a href="/facturas">Facturas</a> | <a href="/reportes">Reportes</a></p>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    logger.info("Logout exitoso")
    return redirect('/login')

# ========== RUTAS ADICIONALES SIMPLES ==========
@app.route('/clientes')
@app.route('/facturas') 
@app.route('/reportes')
def placeholder_pages():
    """Páginas placeholder simples"""
    if 'logged_in' not in session:
        return redirect('/login')
    
    page = request.path.strip('/')
    return f'''
    <h1>ERP13 - {page.title()}</h1>
    <p>Funcionalidad de {page} en desarrollo.</p>
    <a href="/dashboard">← Volver al Dashboard</a>
    '''

# ========== ERROR HANDLERS SIMPLES ==========
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Server error'}), 500

# ========== WSGI EXPORT ==========
application = app

# ========== LOGGING DE INICIO ==========
logger.info("🚀 ERP13 Enterprise MINIMAL iniciado")
logger.info(f"Puerto: {os.environ.get('PORT', 8080)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=False)
