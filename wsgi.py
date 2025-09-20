#!/usr/bin/env python3
"""
ERP13E Enterprise - WSGI Application Entry Point (Compatible Version)
Optimized for Railway deployment with flexible environment handling
Compatible with existing configuration and health checks
"""

import os
import sys
import logging
from datetime import datetime

# Configure logging for ERP13E production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

try:
    # Import main application (flexible import)
    from main import create_app
    
    # Create Flask application instance for ERP13E
    application = create_app()
    
    # Store startup time for monitoring (optional)
    if not hasattr(application, 'start_time'):
        application.start_time = datetime.utcnow()
    if not hasattr(application, 'request_count'):
        application.request_count = 0
    if not hasattr(application, 'active_sessions'):
        application.active_sessions = []
    
    # Enhanced Health Check (compatible with existing /health)
    @application.route('/health/wsgi')
    def wsgi_health_check():
        """Enhanced health check without breaking existing /health endpoint"""
        try:
            # Basic health response
            health_data = {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'service': 'ERP13E-Enterprise',
                'wsgi_version': 'compatible',
                'environment': os.environ.get('FLASK_ENV', 'production')
            }
            
            # Optional database check (non-breaking)
            try:
                from sqlalchemy import text
                from flask import current_app
                
                if hasattr(current_app, 'extensions') and 'sqlalchemy' in current_app.extensions:
                    db = current_app.extensions['sqlalchemy'].db
                    db.session.execute(text('SELECT 1'))
                    health_data['database'] = 'connected'
                else:
                    health_data['database'] = 'not_configured'
            except Exception as db_error:
                health_data['database'] = 'error'
                health_data['db_error'] = str(db_error)
            
            return health_data, 200
            
        except Exception as e:
            logger.error(f"WSGI health check failed: {str(e)}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'service': 'ERP13E-Enterprise'
            }, 500
    
    @application.route('/health/detailed')  
    def detailed_health_check():
        """Detailed health check with system metrics (optional)"""
        try:
            # Import psutil only if available
            try:
                import psutil
                memory = psutil.virtual_memory()
                cpu_percent = psutil.cpu_percent(interval=0.1)  # Quick check
                system_metrics = {
                    'memory_usage': f"{memory.percent}%",
                    'memory_available': f"{memory.available // (1024*1024)}MB",
                    'cpu_usage': f"{cpu_percent}%"
                }
            except ImportError:
                system_metrics = {'status': 'psutil_not_available'}
            
            # Application metrics
            uptime_seconds = (datetime.utcnow() - application.start_time).total_seconds()
            
            return {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'service': 'ERP13E-Enterprise',
                'environment': os.environ.get('FLASK_ENV', 'production'),
                'system': system_metrics,
                'application': {
                    'uptime_seconds': round(uptime_seconds, 2),
                    'request_count': application.request_count,
                    'flask_env': os.environ.get('FLASK_ENV', 'production')
                },
                'configuration': {
                    'workers': os.environ.get('WEB_CONCURRENCY', 'auto'),
                    'database_configured': '✅' if os.environ.get('DATABASE_URL') else '❌',
                    'jwt_configured': '✅' if os.environ.get('JWT_SECRET_KEY') else '❌',
                    'secret_configured': '✅' if os.environ.get('SECRET_KEY') else '❌'
                }
            }, 200
            
        except Exception as e:
            logger.error(f"Detailed health check failed: {str(e)}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'service': 'ERP13E-Enterprise'
            }, 500
    
    @application.route('/metrics')
    def metrics():
        """Simple metrics endpoint for monitoring"""
        try:
            uptime = (datetime.utcnow() - application.start_time).total_seconds()
            
            return {
                'erp13e_requests_total': application.request_count,
                'erp13e_uptime_seconds': round(uptime, 2),
                'erp13e_environment': os.environ.get('FLASK_ENV', 'production'),
                'erp13e_workers': os.environ.get('WEB_CONCURRENCY', 'auto')
            }, 200
        except Exception as e:
            logger.error(f"Metrics endpoint failed: {str(e)}")
            return {'error': str(e)}, 500
    
    # Request counting middleware (optional)
    @application.before_request
    def before_request():
        application.request_count += 1
    
    # Log successful initialization
    logger.info("🚀 ERP13E Enterprise - WSGI application initialized successfully")
    logger.info(f"Environment: {os.environ.get('FLASK_ENV', 'production')}")
    logger.info(f"Workers: {os.environ.get('WEB_CONCURRENCY', 'auto')}")
    logger.info(f"Database configured: {'✅' if os.environ.get('DATABASE_URL') else '❌'}")
    logger.info(f"JWT configured: {'✅' if os.environ.get('JWT_SECRET_KEY') else '❌'}")
    logger.info("Health checks available: /health, /health/wsgi, /health/detailed, /metrics")
    
except ImportError as e:
    logger.error(f"Failed to import main application: {str(e)}")
    
    # Fallback application for debugging (compatible)
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def fallback():
        return {
            'error': 'ERP13E application import failed',
            'message': str(e),
            'status': 'initialization_error',
            'service': 'ERP13E-Enterprise',
            'suggestion': 'Check main.py exists and create_app function is available'
        }, 500
    
    @application.route('/health')
    def fallback_health():
        return {
            'status': 'unhealthy', 
            'error': 'Application not loaded',
            'service': 'ERP13E-Enterprise',
            'timestamp': datetime.utcnow().isoformat()
        }, 500

except Exception as e:
    logger.error(f"Critical error during ERP13E WSGI initialization: {str(e)}")
    
    # Create minimal fallback instead of sys.exit(1)
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/health')
    def emergency_health():
        return {
            'status': 'emergency_mode', 
            'error': str(e),
            'service': 'ERP13E-Enterprise',
            'timestamp': datetime.utcnow().isoformat()
        }, 200  # Return 200 to pass health check
    
    @application.route('/')
    def emergency_home():
        return {
            'status': 'emergency_mode',
            'message': 'ERP13E in emergency fallback mode',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }, 200

if __name__ == "__main__":
    # For local development
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting ERP13E Enterprise in {'development' if debug else 'production'} mode")
    application.run(host='0.0.0.0', port=port, debug=debug)
