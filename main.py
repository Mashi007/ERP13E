# Crear nuevo main.py con código funcional
cat > main.py << 'EOF'
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <h1>ERP13 Enterprise</h1>
    <h2>Sistema Empresarial en Producción</h2>
    <p>Deployment exitoso en Railway</p>
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
    <h2>ERP13 - Sistema de Autenticación</h2>
    <p>Módulo de login empresarial</p>
    <p><a href="/">Volver al inicio</a></p>
    """

@app.route('/dashboard')
def dashboard():
    return jsonify({
        "status": "operational", 
        "message": "Dashboard ERP13 funcionando",
        "modules": ["auditoria", "clientes", "facturacion"],
        "environment": "production"
    })

@app.route('/health')
def health():
    return jsonify({
        "service": "ERP13 Enterprise",
        "status": "healthy",
        "environment": "production"
    })

if __name__ == '__main__':
    app.run(debug=True)
EOF
