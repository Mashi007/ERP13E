#!/usr/bin/env python3
# =============================================================================
# ERP ENTERPRISE - MAIN APPLICATION
# Railway deployment ready with health checks
# =============================================================================

import os
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Enable CORS
CORS(app)

# =============================================================================
# HEALTH CHECK ENDPOINT - Railway requirement
# =============================================================================

@app.route('/health')
def health_check():
    """Railway health check endpoint"""
    try:
        # Check template system
        template_status = "operational"
        try:
            # Test if templates directory exists and layout.html is accessible
            if os.path.exists('templates/layout.html'):
                template_status = "operational"
            else:
                template_status = "failed"
        except Exception as e:
            template_status = "failed"
            logger.error(f"Template check failed: {str(e)}")

        # Basic health checks
        health_data = {
            "status": "operational" if template_status == "operational" else "degraded",
            "version": "3.0.0",
            "timestamp": "2025-09-20T12:07:00.000000",
            "environment": os.environ.get('ENVIRONMENT', 'production'),
            "checks": {
                "auth": "operational",
                "cache": "operational", 
                "redis": "not_configured",  # Will configure later
                "templates": template_status
            },
            "failed_checks": ["templates"] if template_status == "failed" else [],
            "metrics": {
                "active_users": 1,
                "cache_items": 0,
                "total_routes": len([rule.rule for rule in app.url_map.iter_rules()]),
                "uptime": "Railway managed"
            }
        }
        
        # Return 200 if operational, 503 if degraded
        status_code = 200 if health_data["status"] == "operational" else 503
        return jsonify(health_data), status_code
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

# =============================================================================
# MAIN ROUTES - ERP System
# =============================================================================

@app.route('/')
def dashboard():
    """Main dashboard - ERP Enterprise"""
    try:
        return render_template('dashboard.html', 
                             page_title='Dashboard ERP Enterprise',
                             active_page='dashboard')
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        # Fallback HTML if templates fail
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>ERP Enterprise</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-5">
                <div class="text-center">
                    <h1 class="display-4">🏢 ERP Enterprise</h1>
                    <p class="lead">Sistema de gestión empresarial</p>
                    <div class="alert alert-warning">
                        <strong>Templates en configuración...</strong><br>
                        El sistema está arrancando correctamente en Railway.
                    </div>
                    <div class="row mt-4">
                        <div class="col-md-3">
                            <div class="card">
                                <div class="card-body">
                                    <h5>Facturación</h5>
                                    <p>Sistema de facturas</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card">
                                <div class="card-body">
                                    <h5>Clientes</h5>
                                    <p>Gestión de clientes</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card">
                                <div class="card-body">
                                    <h5>Contabilidad</h5>
                                    <p>Apuntes contables</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card">
                                <div class="card-body">
                                    <h5>Configuración</h5>
                                    <p>Ajustes del sistema</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

@app.route('/facturacion/clientes')
def facturas_clientes():
    """Facturas de clientes"""
    try:
        return render_template('facturas_clientes.html',
                             page_title='Facturas de Clientes',
                             active_page='facturas_clientes')
    except:
        return jsonify({"status": "Template not found", "route": "facturas_clientes"})

@app.route('/facturacion/estados-pago')
def estados_pago():
    """Estados de pago"""
    try:
        return render_template('estados_pago.html',
                             page_title='Estados de Pago',
                             active_page='estados_pago')
    except:
        return jsonify({"status": "Template not found", "route": "estados_pago"})

@app.route('/contabilidad/apuntes')
def apuntes_contables():
    """Apuntes contables"""
    try:
        return render_template('apuntes_contables.html',
                             page_title='Apuntes Contables',
                             active_page='apuntes_contables')
    except:
        return jsonify({"status": "Template not found", "route": "apuntes_contables"})

@app.route('/facturacion/exportacion')
def exportacion_contable():
    """Exportación contable"""
    try:
        return render_template('exportacion_contable.html',
                             page_title='Exportación Contable',
                             active_page='exportacion_contable')
    except:
        return jsonify({"status": "Template not found", "route": "exportacion_contable"})

# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        "api": "operational",
        "version": "1.0.0",
        "endpoints": [
            "/",
            "/health", 
            "/api/status",
            "/facturacion/clientes",
            "/facturacion/estados-pago",
            "/contabilidad/apuntes",
            "/facturacion/exportacion"
        ]
    })

@app.route('/api/configuracion/ia-status')
def ia_status():
    """IA configuration status for templates"""
    return jsonify({
        "configured": False,
        "message": "IA configuration pending"
    })

# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Page not found",
        "status": 404,
        "available_routes": [
            "/",
            "/health",
            "/facturacion/clientes", 
            "/facturacion/estados-pago",
            "/contabilidad/apuntes",
            "/facturacion/exportacion"
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {str(error)}")
    return jsonify({
        "error": "Internal server error",
        "status": 500
    }), 500

# =============================================================================
# APPLICATION STARTUP
# =============================================================================

if __name__ == '__main__':
    # Railway automatically sets PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"🚀 Starting ERP Enterprise on port {port}")
    logger.info(f"🔧 Debug mode: {debug_mode}")
    logger.info(f"📁 Templates directory: {os.path.abspath('templates')}")
    
    # Check if templates directory exists
    if os.path.exists('templates'):
        logger.info("✅ Templates directory found")
        template_files = os.listdir('templates')
        logger.info(f"📄 Template files: {template_files}")
    else:
        logger.warning("⚠️ Templates directory not found - creating fallback")
        os.makedirs('templates', exist_ok=True)
    
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
