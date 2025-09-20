#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📁 Ruta: /app/health.py
📄 Nombre: HealthController.py
🏗️ Propósito: Sistema de health checks integral para Railway
⚡ Performance: Validación rápida de servicios críticos
🔒 Seguridad: Información controlada sin exponer datos sensibles

ERP13 Enterprise - Health Check Controller
Optimizado para Railway deployment con monitoring avanzado
"""

import os
import time
import redis
import psycopg2
from flask import Blueprint, jsonify, current_app
from datetime import datetime, timezone
import logging

# 🏥 BLUEPRINT DE HEALTH CHECKS
health_bp = Blueprint('health', __name__)

# 📊 CONFIGURACIÓN DE LOGGING
logger = logging.getLogger(__name__)

class HealthChecker:
    """
    🏥 Clase para realizar verificaciones de salud del sistema
    Verifica conectividad de servicios críticos con timeouts optimizados
    """
    
    @staticmethod
    def check_database():
        """
        🗄️ Verificar conectividad PostgreSQL
        Returns: tuple (status: bool, message: str, response_time: float)
        """
        start_time = time.time()
        try:
            # Obtener configuración de base de datos
            database_url = os.environ.get('DATABASE_URL')
            if not database_url:
                return False, "DATABASE_URL no configurada", 0
            
            # Conexión con timeout de 3 segundos
            conn = psycopg2.connect(database_url, connect_timeout=3)
            cursor = conn.cursor()
            
            # Query simple para verificar conectividad
            cursor.execute("SELECT 1;")
            result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            response_time = round((time.time() - start_time) * 1000, 2)
            
            if result and result[0] == 1:
                return True, "PostgreSQL conectado", response_time
            else:
                return False, "Query falló", response_time
                
        except psycopg2.OperationalError as e:
            response_time = round((time.time() - start_time) * 1000, 2)
            logger.warning(f"Database connection failed: {str(e)}")
            return False, f"Error de conexión: {str(e)[:50]}", response_time
        except Exception as e:
            response_time = round((time.time() - start_time) * 1000, 2)
            logger.error(f"Database health check error: {str(e)}")
            return False, f"Error inesperado: {str(e)[:50]}", response_time
    
    @staticmethod
    def check_redis():
        """
        🔴 Verificar conectividad Redis
        Returns: tuple (status: bool, message: str, response_time: float)
        """
        start_time = time.time()
        try:
            # Obtener configuración de Redis
            redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
            
            # Conexión con timeout de 2 segundos
            r = redis.from_url(redis_url, socket_timeout=2, socket_connect_timeout=2)
            
            # Ping para verificar conectividad
            result = r.ping()
            
            response_time = round((time.time() - start_time) * 1000, 2)
            
            if result:
                return True, "Redis conectado", response_time
            else:
                return False, "Ping falló", response_time
                
        except redis.ConnectionError as e:
            response_time = round((time.time() - start_time) * 1000, 2)
            logger.warning(f"Redis connection failed: {str(e)}")
            return False, f"Error de conexión: {str(e)[:50]}", response_time
        except redis.TimeoutError as e:
            response_time = round((time.time() - start_time) * 1000, 2)
            logger.warning(f"Redis timeout: {str(e)}")
            return False, "Timeout de conexión", response_time
        except Exception as e:
            response_time = round((time.time() - start_time) * 1000, 2)
            logger.error(f"Redis health check error: {str(e)}")
            return False, f"Error inesperado: {str(e)[:50]}", response_time
    
    @staticmethod
    def check_disk_space():
        """
        💾 Verificar espacio en disco
        Returns: tuple (status: bool, message: str, usage_percent: float)
        """
        try:
            import shutil
            total, used, free = shutil.disk_usage('/')
            
            # Calcular porcentaje de uso
            usage_percent = round((used / total) * 100, 2)
            
            # Consideramos crítico si el uso supera 90%
            if usage_percent > 90:
                return False, f"Espacio crítico: {usage_percent}%", usage_percent
            elif usage_percent > 80:
                return True, f"Espacio bajo: {usage_percent}%", usage_percent
            else:
                return True, f"Espacio disponible: {usage_percent}%", usage_percent
                
        except Exception as e:
            logger.error(f"Disk space check error: {str(e)}")
            return False, f"Error verificando disco: {str(e)[:50]}", 0
    
    @staticmethod
    def check_memory():
        """
        🧠 Verificar uso de memoria
        Returns: tuple (status: bool, message: str, usage_percent: float)
        """
        try:
            import psutil
            memory = psutil.virtual_memory()
            usage_percent = round(memory.percent, 2)
            
            # Consideramos crítico si el uso supera 90%
            if usage_percent > 90:
                return False, f"Memoria crítica: {usage_percent}%", usage_percent
            elif usage_percent > 80:
                return True, f"Memoria alta: {usage_percent}%", usage_percent
            else:
                return True, f"Memoria normal: {usage_percent}%", usage_percent
                
        except ImportError:
            # psutil no disponible, usar alternativa básica
            try:
                with open('/proc/meminfo', 'r') as f:
                    lines = f.readlines()
                    
                total = None
                available = None
                
                for line in lines:
                    if line.startswith('MemTotal:'):
                        total = int(line.split()[1]) * 1024  # Convert to bytes
                    elif line.startswith('MemAvailable:'):
                        available = int(line.split()[1]) * 1024  # Convert to bytes
                
                if total and available:
                    used = total - available
                    usage_percent = round((used / total) * 100, 2)
                    
                    if usage_percent > 90:
                        return False, f"Memoria crítica: {usage_percent}%", usage_percent
                    else:
                        return True, f"Memoria: {usage_percent}%", usage_percent
                else:
                    return True, "Memoria no verificable", 0
                    
            except Exception as e:
                logger.error(f"Memory check error: {str(e)}")
                return True, "Memoria no verificable", 0
        except Exception as e:
            logger.error(f"Memory check error: {str(e)}")
            return True, f"Error verificando memoria: {str(e)[:50]}", 0

# 🚀 ENDPOINTS DE HEALTH CHECK

@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    🏥 Endpoint principal de health check para Railway
    Verifica estado básico de la aplicación
    """
    try:
        return jsonify({
            'status': 'healthy',
            'service': 'ERP13 Enterprise',
            'version': '1.0.0',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'environment': os.environ.get('RAILWAY_ENVIRONMENT', 'unknown'),
            'uptime': 'active'
        }), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'service': 'ERP13 Enterprise',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500

@health_bp.route('/health/detailed', methods=['GET'])
def detailed_health_check():
    """
    🔍 Health check detallado con verificación de servicios
    Para monitoreo interno y troubleshooting
    """
    start_time = time.time()
    
    try:
        # Inicializar resultados
        results = {
            'status': 'healthy',
            'service': 'ERP13 Enterprise',
            'version': '1.0.0',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'environment': os.environ.get('RAILWAY_ENVIRONMENT', 'unknown'),
            'checks': {},
            'performance': {}
        }
        
        overall_healthy = True
        
        # 🗄️ Verificar Base de Datos
        db_healthy, db_message, db_time = HealthChecker.check_database()
        results['checks']['database'] = {
            'status': 'healthy' if db_healthy else 'unhealthy',
            'message': db_message,
            'response_time_ms': db_time
        }
        if not db_healthy:
            overall_healthy = False
        
        # 🔴 Verificar Redis
        redis_healthy, redis_message, redis_time = HealthChecker.check_redis()
        results['checks']['redis'] = {
            'status': 'healthy' if redis_healthy else 'unhealthy',
            'message': redis_message,
            'response_time_ms': redis_time
        }
        if not redis_healthy:
            overall_healthy = False
        
        # 💾 Verificar Disco
        disk_healthy, disk_message, disk_usage = HealthChecker.check_disk_space()
        results['checks']['disk'] = {
            'status': 'healthy' if disk_healthy else 'unhealthy',
            'message': disk_message,
            'usage_percent': disk_usage
        }
        if not disk_healthy:
            overall_healthy = False
        
        # 🧠 Verificar Memoria
        memory_healthy, memory_message, memory_usage = HealthChecker.check_memory()
        results['checks']['memory'] = {
            'status': 'healthy' if memory_healthy else 'warning',
            'message': memory_message,
            'usage_percent': memory_usage
        }
        # Memoria en warning no marca como unhealthy el sistema completo
        
        # 📊 Performance metrics
        total_time = round((time.time() - start_time) * 1000, 2)
        results['performance'] = {
            'total_check_time_ms': total_time,
            'database_response_ms': db_time,
            'redis_response_ms': redis_time
        }
        
        # 🎯 Estado general
        results['status'] = 'healthy' if overall_healthy else 'unhealthy'
        
        status_code = 200 if overall_healthy else 503
        return jsonify(results), status_code
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'service': 'ERP13 Enterprise',
            'error': f"Health check error: {str(e)}",
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'checks': {
                'system': {
                    'status': 'unhealthy',
                    'message': 'Health check system failed'
                }
            }
        }), 500

@health_bp.route('/health/ready', methods=['GET'])
def readiness_check():
    """
    ✅ Readiness probe para Kubernetes/Railway
    Verifica si la aplicación está lista para recibir tráfico
    """
    try:
        # Verificar servicios críticos rápidamente
        db_healthy, _, _ = HealthChecker.check_database()
        
        if db_healthy:
            return jsonify({
                'status': 'ready',
                'service': 'ERP13 Enterprise',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 200
        else:
            return jsonify({
                'status': 'not_ready',
                'service': 'ERP13 Enterprise',
                'message': 'Database not available',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }), 503
            
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return jsonify({
            'status': 'not_ready',
            'service': 'ERP13 Enterprise',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 503

@health_bp.route('/health/live', methods=['GET'])
def liveness_check():
    """
    💓 Liveness probe básico
    Verifica si la aplicación está viva (sin verificar dependencias)
    """
    return jsonify({
        'status': 'alive',
        'service': 'ERP13 Enterprise',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'uptime': 'active'
    }), 200

# 📊 ENDPOINT DE MÉTRICAS BÁSICAS
@health_bp.route('/metrics', methods=['GET'])
def basic_metrics():
    """
    📈 Métricas básicas del sistema para monitoreo
    """
    try:
        # Obtener métricas básicas
        disk_healthy, disk_message, disk_usage = HealthChecker.check_disk_space()
        memory_healthy, memory_message, memory_usage = HealthChecker.check_memory()
        
        return jsonify({
            'service': 'ERP13 Enterprise',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'metrics': {
                'disk_usage_percent': disk_usage,
                'memory_usage_percent': memory_usage,
                'environment': os.environ.get('RAILWAY_ENVIRONMENT', 'unknown'),
                'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}"
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Metrics endpoint failed: {str(e)}")
        return jsonify({
            'error': 'Metrics unavailable',
            'message': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500
