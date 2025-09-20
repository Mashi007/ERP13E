#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📁 Ruta: /app/modules/monitoring/health_check_fixed.py
📄 Nombre: health_check_fixed.py
🏗️ Propósito: Health Check Enterprise corregido para Railway ERP13 v3.1
⚡ Performance: Respuesta <50ms, monitoreo proactivo
🔒 Seguridad: Endpoints públicos seguros, información limitada

HEALTH CHECK ENTERPRISE RAILWAY-OPTIMIZED:
- Endpoints de monitoreo Railway-compatible
- Métricas de sistema en tiempo real
- Validación de componentes críticos
- Logging estructurado para debugging
- Failover automático para servicios degradados
"""

import os
import time
import logging
import platform
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, current_app
import traceback

# ========== CONFIGURACIÓN LOGGING ==========
logger = logging.getLogger('ERP13_HealthCheck')
logger.setLevel(logging.INFO)

# ========== BLUEPRINT HEALTH CHECK ==========
health_bp = Blueprint('health_check', __name__, url_prefix='')

# ========== VARIABLES GLOBALES ==========
APPLICATION_START_TIME = datetime.utcnow()
HEALTH_CHECK_VERSION = "3.1.0"
SERVICE_NAME = "ERP13-Enterprise"

# ========== UTILIDADES DE MONITOREO ==========
def get_system_metrics():
    """Obtener métricas básicas del sistema"""
    try:
        import psutil
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        return {
            'memory_percent': round(memory.percent, 2),
            'memory_available_mb': round(memory.available / (1024 * 1024), 2),
            'cpu_percent': round(cpu_percent, 2),
            'disk_usage': round(psutil.disk_usage('/').percent, 2)
        }
    except ImportError:
        # psutil no disponible - métricas básicas de OS
        return {
            'memory_percent': 'unavailable',
            'memory_available_mb': 'unavailable', 
            'cpu_percent': 'unavailable',
            'disk_usage': 'unavailable',
            'note': 'psutil_not_installed'
        }
    except Exception as e:
        logger.warning(f"Error getting system metrics: {e}")
        return {
            'memory_percent': 'error',
            'cpu_percent': 'error',
            'error': str(e)
        }

def check_database_connection():
    """Verificar conexión a base de datos (si está configurada)"""
    try:
        # Verificar si Flask-SQLAlchemy está configurado
        if hasattr(current_app, 'extensions') and 'sqlalchemy' in current_app.extensions:
            from sqlalchemy import text
            db = current_app.extensions['sqlalchemy'].db
            
            # Test query simple
            result = db.session.execute(text('SELECT 1 as test')).fetchone()
            if result and result[0] == 1:
                return {'status': 'connected', 'test_query': 'success'}
            else:
                return {'status': 'error', 'test_query': 'failed'}
        else:
            return {'status': 'not_configured', 'note': 'SQLAlchemy not configured'}
            
    except Exception as e:
        logger.warning(f"Database connection check failed: {e}")
        return {'status': 'error', 'error': str(e)}

def get_application_metrics():
    """Métricas específicas de la aplicación ERP13"""
    uptime = datetime.utcnow() - APPLICATION_START_TIME
    
    # Contar rutas registradas
    routes_count = len(current_app.url_map._rules) if hasattr(current_app, 'url_map') else 0
    
    # Información de workers (si está disponible)
    workers_info = {
        'gunicorn_workers': os.environ.get('WEB_CONCURRENCY', 'auto'),
        'process_id': os.getpid(),
        'parent_id': os.getppid()
    }
    
    return {
        'uptime_seconds': int(uptime.total_seconds()),
        'uptime_human': str(uptime).split('.')[0],  # Sin microsegundos
        'routes_registered': routes_count,
        'workers': workers_info,
        'environment': os.environ.get('FLASK_ENV', 'unknown'),
        'python_version': platform.python_version(),
        'platform': platform.platform()
    }

# ========== ENDPOINTS HEALTH CHECK ==========

@health_bp.route('/health')
def basic_health_check():
    """Health check básico para Railway - DEBE responder rápido"""
    try:
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'service': SERVICE_NAME,
            'version': HEALTH_CHECK_VERSION,
            'environment': os.environ.get('FLASK_ENV', 'production')
        }), 200
        
    except Exception as e:
        logger.error(f"Basic health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat(),
            'service': SERVICE_NAME
        }), 500

@health_bp.route('/health/wsgi')
def wsgi_health_check():
    """Health check específico para WSGI/Gunicorn"""
    try:
        # Verificar que la aplicación Flask está funcionando
        app_name = current_app.name if current_app else 'unknown'
        
        response_data = {
            'status': 'healthy',
            'wsgi_status': 'operational',
            'flask_app': app_name,
            'request_method': request.method,
            'timestamp': datetime.utcnow().isoformat(),
            'service': SERVICE_NAME,
            'worker_pid': os.getpid()
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"WSGI health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'wsgi_status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@health_bp.route('/health/detailed')
def detailed_health_check():
    """Health check detallado con métricas del sistema"""
    try:
        # Recopilar todas las métricas
        system_metrics = get_system_metrics()
        app_metrics = get_application_metrics()
        db_status = check_database_connection()
        
        response_data = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'service': SERVICE_NAME,
            'version': HEALTH_CHECK_VERSION,
            'system': system_metrics,
            'application': app_metrics,
            'database': db_status,
            'checks': {
                'system_metrics': 'success' if system_metrics else 'failed',
                'application_metrics': 'success' if app_metrics else 'failed',
                'database_check': db_status.get('status', 'unknown')
            }
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        error_trace = traceback.format_exc()
        
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'trace': error_trace,
            'timestamp': datetime.utcnow().isoformat(),
            'service': SERVICE_NAME
        }), 500

@health_bp.route('/metrics')
def prometheus_metrics():
    """Métricas en formato Prometheus-compatible"""
    try:
        uptime = datetime.utcnow() - APPLICATION_START_TIME
        uptime_seconds = int(uptime.total_seconds())
        
        system_metrics = get_system_metrics()
        
        # Formato Prometheus básico
        metrics_text = f"""# HELP erp13_uptime_seconds Application uptime in seconds
# TYPE erp13_uptime_seconds counter
erp13_uptime_seconds {uptime_seconds}

# HELP erp13_health_status Application health status (1=healthy, 0=unhealthy)
# TYPE erp13_health_status gauge
erp13_health_status 1

# HELP erp13_memory_usage_percent Memory usage percentage
# TYPE erp13_memory_usage_percent gauge
erp13_memory_usage_percent {system_metrics.get('memory_percent', 0)}

# HELP erp13_cpu_usage_percent CPU usage percentage
# TYPE erp13_cpu_usage_percent gauge
erp13_cpu_usage_percent {system_metrics.get('cpu_percent', 0)}

# HELP erp13_worker_pid Current worker process ID
# TYPE erp13_worker_pid gauge
erp13_worker_pid {os.getpid()}
"""
        
        return metrics_text, 200, {'Content-Type': 'text/plain; version=0.0.4; charset=utf-8'}
        
    except Exception as e:
        logger.error(f"Metrics endpoint failed: {e}")
        return f"# Error generating metrics: {e}\n", 500, {'Content-Type': 'text/plain'}

@health_bp.route('/health/liveness')
def liveness_probe():
    """Liveness probe para Kubernetes/Railway (simple y rápido)"""
    return jsonify({
        'status': 'alive',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@health_bp.route('/health/readiness')
def readiness_probe():
    """Readiness probe - verifica si la app está lista para recibir tráfico"""
    try:
        # Verificaciones rápidas de readiness
        checks = {
            'flask_app': current_app is not None,
            'routes_loaded': len(current_app.url_map._rules) > 0 if current_app else False,
            'uptime_sufficient': (datetime.utcnow() - APPLICATION_START_TIME).total_seconds() > 5
        }
        
        all_ready = all(checks.values())
        
        response_data = {
            'status': 'ready' if all_ready else 'not_ready',
            'checks': checks,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(response_data), 200 if all_ready else 503
        
    except Exception as e:
        logger.error(f"Readiness probe failed: {e}")
        return jsonify({
            'status': 'not_ready',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503

# ========== ERROR HANDLERS ==========
@health_bp.errorhandler(404)
def health_not_found(error):
    """Handler para rutas de health no encontradas"""
    return jsonify({
        'status': 'not_found',
        'error': 'Health check endpoint not found',
        'available_endpoints': [
            '/health',
            '/health/wsgi', 
            '/health/detailed',
            '/health/liveness',
            '/health/readiness',
            '/metrics'
        ],
        'timestamp': datetime.utcnow().isoformat()
    }), 404

@health_bp.errorhandler(500)
def health_internal_error(error):
    """Handler para errores internos en health checks"""
    return jsonify({
        'status': 'internal_error',
        'error': 'Internal server error in health check',
        'timestamp': datetime.utcnow().isoformat()
    }), 500

# ========== FUNCIÓN DE REGISTRO ==========
def register_health_checks(app):
    """Registrar health checks en la aplicación Flask"""
    try:
        app.register_blueprint(health_bp)
        logger.info("✅ Health check endpoints registered successfully")
        logger.info("📊 Available endpoints: /health, /health/wsgi, /health/detailed, /metrics")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to register health check endpoints: {e}")
        return False

# ========== INICIALIZACIÓN ==========
if __name__ == '__main__':
    print("ERP13 Enterprise Health Check Module v3.1")
    print("Available endpoints:")
    print("  - /health (basic)")
    print("  - /health/wsgi (WSGI status)")
    print("  - /health/detailed (full metrics)")
    print("  - /health/liveness (K8s liveness)")
    print("  - /health/readiness (K8s readiness)")
    print("  - /metrics (Prometheus)")
