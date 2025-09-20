#!/usr/bin/env python3
"""
ERP13E Enterprise - WSGI Application Entry Point
Optimized for Railway deployment with PostgreSQL integration
Compatible with existing JWT and SECRET_KEY configuration
"""

import os
import sys
import logging
from datetime import datetime
import psutil
import signal
import atexit

# Configure logging for ERP13E production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# ERP13E Environment validation
required_env_vars = [
    'DATABASE_URL',
    'SECRET_KEY', 
    'JWT_SECRET_KEY',
    'FLASK_ENV',
    'RAILWAY_ENVIRONMENT'
]

def validate_environment():
    """Validate required environment variables for ERP13E"""
    missing_vars = []
    for var in required_env_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        return False
    
    logger.info("✅ All required environment variables present")
    return True

def setup_signal_handlers():
    """Setup graceful shutdown handlers for ERP13E"""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}. Shutting down gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

try:
    # Validate environment before proceeding
    if not validate_environment():
        logger.error("Environment validation failed. Exiting...")
        sys.exit(1)
    
    # Setup signal handlers
    setup_signal_handlers()
    
    # Import main application
    from main import create_app
    
    # Create Flask application instance for ERP13E
    application = create_app()
    
    # Store startup time for monitoring
    application.start_time = datetime.utcnow()
    application.request_count = 0
    application.active_sessions = []
    
    # ERP13E Enhanced Health Check Endpoints
    @application.route('/health')
    def health_check():
        """Basic health check compatible with Railway configuration"""
        try:
            # Quick database connection test
            from sqlalchemy import text
            from flask import current_app
            
            if hasattr(current_app, 'extensions') and 'sqlalchemy' in current_app.extensions:
                db = current_app.extensions['sqlalchemy'].db
                db.session.execute(text('SELECT 1'))
                db_status = 'connected'
            else:
                db_status = 'not_configured'
            
            return {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'service': 'ERP13E-Enterprise',
                'environment': os.environ.get('RAILWAY_ENVIRONMENT', 'unknown'),
                'database': db_status
            }, 200
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                'status': 'unhealthy',
                'error': 'Database connection failed',
                'timestamp': datetime.utcnow().isoformat()
            }, 500
    
    @application.route('/health/detailed')
    def detailed_health_check():
        """Detailed health check with system and database metrics"""
        try:
            # System metrics
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Database connection test with metrics
            db_metrics = {'status': 'not_configured'}
            try:
                from sqlalchemy import text
                from flask import current_app
                import time
                
                if hasattr(current_app, 'extensions') and 'sqlalchemy' in current_app.extensions:
                    db = current_app.extensions['sqlalchemy'].db
                    start_time = time.time()
                    result = db.session.execute(text('SELECT COUNT(*) as connection_test'))
                    query_time = (time.time() - start_time) * 1000
                    
                    db_metrics = {
                        'status': 'connected',
                        'query_time_ms': round(query_time, 2),
                        'connection_pool': 'active'
                    }
            except Exception as db_error:
                db_metrics = {
                    'status': 'error',
                    'error': str(db_error)
                }
            
            # Application metrics
            uptime_seconds = (datetime.utcnow() - application.start_time).total_seconds()
            
            return {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'service': 'ERP13E-Enterprise',
                'environment': os.environ.get('RAILWAY_ENVIRONMENT', 'production'),
                'system': {
                    'memory_usage': f"{memory.percent}%",
                    'memory_available': f"{memory.available // (1024*1024)}MB",
                    'cpu_usage': f"{cpu_percent}%",
                    'workers': os.environ.get('WEB_CONCURRENCY', '3'),
                    'worker_class': os.environ.get('WORKER_CLASS', 'gthread')
                },
                'application': {
                    'uptime_seconds': round(uptime_seconds, 2),
                    'request_count': application.request_count,
                    'active_sessions': len(application.active_sessions),
                    'flask_env': os.environ.get('FLASK_ENV', 'production')
                },
                'database': db_metrics
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
        """Prometheus-style metrics for ERP13E monitoring"""
        try:
            uptime = (datetime.utcnow() - application.start_time).total_seconds()
            
            return {
                'erp13e_requests_total': application.request_count,
                'erp13e_active_users': len(application.active_sessions),
                'erp13e_uptime_seconds': round(uptime, 2),
                'erp13e_memory_usage_percent': psutil.virtual_memory().percent,
                'erp13e_cpu_usage_percent': psutil.cpu_percent(),
                'erp13e_workers_count': int(os.environ.get('WEB_CONCURRENCY', '3')),
                'erp13e_environment': os.environ.get('RAILWAY_ENVIRONMENT', 'production')
            }, 200
        except Exception as e:
            logger.error(f"Metrics endpoint failed: {str(e)}")
            return {'error': str(e)}, 500
    
    @application.route('/status')
    def status():
        """Simple status endpoint for load balancer"""
        return {'status': 'ok', 'service': 'ERP13E'}, 200
    
    # Request counting middleware
    @application.before_request
    def before_request():
        application.request_count += 1
    
    # Log successful initialization
    logger.info("🚀 ERP13E Enterprise - WSGI application initialized successfully")
    logger.info(f"Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'production')}")
    logger.info(f"Flask Environment: {os.environ.get('FLASK_ENV', 'production')}")
    logger.info(f"Workers: {os.environ.get('WEB_CONCURRENCY', '3')}")
    logger.info(f"Worker Class: {os.environ.get('WORKER_CLASS', 'gthread')}")
    logger.info(f"Database URL configured: {'✅' if os.environ.get('DATABASE_URL') else '❌'}")
    logger.info(f"JWT Secret configured: {'✅' if os.environ.get('JWT_SECRET_KEY') else '❌'}")
    
except ImportError as e:
    logger.error(f"Failed to import main application: {str(e)}")
    
    # Fallback application for debugging
    from flask import Flask
    application = Flask(__name__)
    
    @application.route('/')
    def fallback():
        return {
            'error': 'ERP13E application import failed',
            'message': str(e),
            'status': 'initialization_error',
            'service': 'ERP13E-Enterprise'
        }, 500
    
    @application.route('/health')
    def fallback_health():
        return {
            'status': 'unhealthy', 
            'error': 'Application not loaded',
            'service': 'ERP13E-Enterprise'
        }, 500

except Exception as e:
    logger.error(f"Critical error during ERP13E WSGI initialization: {str(e)}")
    sys.exit(1)

# Cleanup function
def cleanup():
    logger.info("ERP13E Enterprise - Cleaning up resources...")

atexit.register(cleanup)

if __name__ == "__main__":
    # For local development
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting ERP13E Enterprise in {'development' if debug else 'production'} mode")
    application.run(host='0.0.0.0', port=port, debug=debug)
