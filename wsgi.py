#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ERP13 Enterprise v3.0 - Railway WSGI Entry Point
Copyright (c) 2025 ERP13 Enterprise Solutions

Railway Production Deployment Configuration
Optimizado para Gunicorn + Performance + Auto-scaling
"""

import os
import sys
import logging
from main import app

# =============================================================================
# CONFIGURACIÓN DE LOGGING PARA RAILWAY
# =============================================================================

# Configurar logging para Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stdout
)

logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURACIÓN DE PRODUCCIÓN RAILWAY
# =============================================================================

# Configuraciones específicas para Railway
app.config.update({
    'ENV': 'production',
    'DEBUG': False,
    'TESTING': False,
    'PROPAGATE_EXCEPTIONS': True
})

# Configuración de seguridad para producción
app.config.update({
    'SESSION_COOKIE_SECURE': True,
    'SESSION_COOKIE_HTTPONLY': True,
    'SESSION_COOKIE_SAMESITE': 'Lax',
    'PERMANENT_SESSION_LIFETIME': 86400,  # 24 horas
})

# =============================================================================
# OPTIMIZACIONES DE PERFORMANCE PARA RAILWAY
# =============================================================================

# Configurar headers de seguridad
@app.after_request
def add_security_headers(response):
    """Agregar headers de seguridad para producción"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; font-src 'self' https://cdnjs.cloudflare.com; img-src 'self' data: https:;"
    return response

# Configurar compresión de respuestas
@app.after_request
def add_performance_headers(response):
    """Agregar headers de performance"""
    if response.content_type.startswith('text/') or response.content_type.startswith('application/json'):
        response.headers['Cache-Control'] = 'public, max-age=300'
    return response

# =============================================================================
# MANEJO DE ERRORES EN PRODUCCIÓN
# =============================================================================

@app.errorhandler(Exception)
def handle_exception(e):
    """Manejo global de excepciones en producción"""
    logger.error(f"Error no manejado: {str(e)}", exc_info=True)
    
    # En producción, no mostrar detalles del error
    return {
        'error': 'Error interno del servidor',
        'message': 'Por favor contacte al administrador del sistema',
        'status': 500
    }, 500

# =============================================================================
# CONFIGURACIÓN ESPECÍFICA RAILWAY
# =============================================================================

# Puerto configurado por Railway
PORT = int(os.environ.get('PORT', 8080))

# Workers configurados para Railway
WEB_CONCURRENCY = int(os.environ.get('WEB_CONCURRENCY', 2))

# =============================================================================
# INICIALIZACIÓN DE APLICACIÓN
# =============================================================================

# Información de inicio para Railway logs
logger.info("🚀 ERP13 Enterprise v3.0 - Sistema ERP Empresarial Completo")
logger.info("📅 Release: 2025-01-15")
logger.info("🎯 Estado: PRODUCTION")
logger.info("🔧 Modo producción - Servidor WSGI Railway")
logger.info("📦 Módulos: Dashboard, Empresas, Auditoría, Formación, Facturación, Configuración")
logger.info("🔗 31 rutas disponibles")

# Verificar configuración crítica
required_config = ['SECRET_KEY']
missing_config = [key for key in required_config if not os.environ.get(key)]

if missing_config:
    logger.warning(f"⚠️ Variables de entorno faltantes: {missing_config}")
    logger.warning("🔧 Usando valores por defecto - Configure en Railway para producción")
else:
    logger.info("✅ Configuración de producción validada")

# Verificar conectividad Redis (opcional)
try:
    if hasattr(app, 'redis') and app.redis:
        app.redis.ping()
        logger.info("✅ Redis conectado - Cache habilitado")
except Exception as e:
    logger.warning(f"⚠️ Redis no disponible - Cache deshabilitado: {e}")

# =============================================================================
# WSGI APPLICATION OBJECT
# =============================================================================

# Este es el objeto que Gunicorn busca
application = app

# También exportar como 'app' para compatibilidad
app = application

# =============================================================================
# CONFIGURACIÓN GUNICORN RECOMENDADA
# =============================================================================

"""
Configuración Gunicorn recomendada para Railway:

gunicorn --bind 0.0.0.0:$PORT \
         --workers $WEB_CONCURRENCY \
         --worker-class gthread \
         --threads 4 \
         --timeout 120 \
         --keep-alive 5 \
         --max-requests 1000 \
         --max-requests-jitter 100 \
         --preload \
         --access-logfile - \
         --error-logfile - \
         --log-level info \
         wsgi:application

Variables de entorno Railway recomendadas:
- PORT=8080 (auto-configurado)
- WEB_CONCURRENCY=2 (ajustar según recursos)
- GUNICORN_WORKERS=2
- GUNICORN_THREADS=4
- GUNICORN_TIMEOUT=120
"""

# =============================================================================
# HEALTH CHECK ESPECÍFICO PARA RAILWAY
# =============================================================================

@app.route('/railway-health')
def railway_health():
    """Health check específico para Railway monitoring"""
    import psutil
    import time
    
    try:
        # Información del sistema
        cpu_percent = psutil.cpu_percent()
        memory_info = psutil.virtual_memory()
        
        health_data = {
            'status': 'healthy',
            'timestamp': time.time(),
            'version': '3.0.0',
            'environment': 'production',
            'system': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory_info.percent,
                'memory_available_mb': memory_info.available // 1024 // 1024
            },
            'application': {
                'port': PORT,
                'workers': WEB_CONCURRENCY,
                'modules_loaded': 6,
                'routes_available': 31
            }
        }
        
        return health_data, 200
        
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        return {
            'status': 'degraded',
            'error': str(e),
            'timestamp': time.time()
        }, 500

# =============================================================================
# MODO STANDALONE PARA TESTING
# =============================================================================

if __name__ == '__main__':
    # Solo para testing local - Railway usa Gunicorn
    logger.warning("⚠️ Ejecutando en modo standalone - Use Gunicorn para producción")
    application.run(
        host='0.0.0.0',
        port=PORT,
        debug=False,
        threaded=True
    )
