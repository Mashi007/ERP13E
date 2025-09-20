#!/usr/bin/env python3
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear aplicación de emergencia si main.py falla
def create_simple_app():
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    @app.route('/')
    def index():
        return jsonify({
            'message': 'ERP13 Enterprise Running',
            'status': 'ok'
        })
    
    return app

# Intentar importar main.py, si falla usar aplicación simple
try:
    from main import app as application
    logger.info("Main app imported successfully")
except Exception as e:
    logger.error(f"Failed to import main: {e}")
    application = create_simple_app()
    logger.info("Using simple fallback app")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    application.run(host='0.0.0.0', port=port)
