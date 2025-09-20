from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <h1>ERP13 Enterprise</h1>
    <p>Sistema funcionando correctamente</p>
    <p><a href="/login">Login</a> | <a href="/health">Health Check</a></p>
    """

@app.route('/login')
def login():
    return """
    <h2>ERP13 - Sistema de Login</h2>
    <p>Página de autenticación</p>
    <p><a href="/">Volver al inicio</a></p>
    """

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "app": "ERP13 Enterprise",
        "environment": "production",
        "version": "3.0.0"
    })

if __name__ == '__main__':
    app.run(debug=True)
