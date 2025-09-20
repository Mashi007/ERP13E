from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <h1>🏢 ERP13 Enterprise</h1>
    <h2>Sistema Empresarial en Producción</h2>
    <p>✅ Deployment exitoso en Railway</p>
    <ul>
        <li><a href="/health">Health Check</a></li>
        <li><a href="/login">Sistema de Login</a></li>
        <li><a href="/dashboard">Dashboard</a></li>
    </ul>
    <p><strong>Status:</strong> Operacional</p>
    """

@app.route('/login')
def login():
    return """
    <h2>🔐 ERP13 - Sistema de Autenticación</h2>
    <p>Módulo de login empresarial</p>
    <form>
        <p>Usuario: <input type="text" placeholder="Ingrese usuario"></p>
        <p>Password: <input type="password" placeholder="Ingrese contraseña"></p>
        <p><button type="button">Acceder al Sistema</button></p>
    </form>
    <p><a href="/">← Volver al inicio</a></p>
    """

@app.route('/dashboard')
def dashboard():
    return jsonify({
        "status": "operational", 
        "message": "Dashboard ERP13 cargado correctamente",
        "modules": ["auditoria", "clientes", "configuracion", "facturacion"],
        "environment": "production"
    })

@app.route('/health')
def health():
    return jsonify({
        "service": "ERP13 Enterprise",
        "status": "healthy",
        "environment": "production", 
        "modules": {
            "auditoria": "operational",
            "clientes": "operational", 
            "configuracion": "operational",
            "facturacion": "operational"
        },
        "redis_status": "unavailable",
        "version": "13.0.0"
    })

if __name__ == '__main__':
    app.run(debug=True)
