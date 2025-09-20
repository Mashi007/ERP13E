#!/usr/bin/env python3
"""
WSGI Entry Point - Ultra Simple
"""

import os
from datetime import datetime
from flask import Flask, jsonify, request, session, redirect

# Crear app Flask
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'simple-key')

# Health check simple
@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}), 200

# Login simple
@app.route('/')
@app.route('/login')
def login():
    return '''
    <html><body style="margin:50px;font-family:Arial;">
    <h2>ERP13 Login</h2>
    <form method="POST" action="/do_login">
        <p><input type="text" name="username" placeholder="Usuario" required></p>
        <p><input type="password" name="password" placeholder="Password" required></p>
        <p><button type="submit">Login</button></p>
    </form>
    <p>Demo: admin/admin123</p>
    </body></html>
    '''

@app.route('/do_login', methods=['POST'])
def do_login():
    if request.form.get('username') == 'admin' and request.form.get('password') == 'admin123':
        session['logged_in'] = True
        return redirect('/dashboard')
    return redirect('/login')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect('/login')
    return '''
    <html><body style="margin:20px;font-family:Arial;">
    <h1>ERP13 Dashboard</h1>
    <p>Sistema funcionando. <a href="/logout">Logout</a></p>
    </body></html>
    '''

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# WSGI variable que Railway espera
application = app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
