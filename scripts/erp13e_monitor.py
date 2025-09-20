#!/usr/bin/env python3
"""
ERP13E Enterprise - Railway Advanced Monitoring System
Compatible with PostgreSQL, Serverless, and existing configuration
"""

import re
import json
import time
import os
import psycopg2
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
import asyncio
import aiohttp

@dataclass
class ERP13EMetrics:
    """Métricas específicas para ERP13E Enterprise"""
    timestamp: datetime
    level: str
    message: str
    component: str
    response_time: Optional[float] = None
    status_code: Optional[int] = None
    user_id: Optional[str] = None
    endpoint: Optional[str] = None
    database_query_time: Optional[float] = None
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None

class ERP13EMonitor:
    """Monitor avanzado para ERP13E Enterprise en Railway"""
    
    def __init__(self, window_minutes: int = 5):
        self.window_minutes = window_minutes
        self.metrics_buffer = deque(maxlen=2000)  # Más buffer para ERP
        self.database_url = os.environ.get('DATABASE_URL')
        self.railway_env = os.environ.get('RAILWAY_ENVIRONMENT', 'production')
        
        # Thresholds específicos para ERP13E
        self.alert_thresholds = {
            'error_rate': 0.03,  # 3% error rate para ERP
            'avg_response_time': 3.0,  # 3 seconds para operaciones ERP
            'database_query_time': 2.0,  # 2 seconds para queries DB
            'memory_usage': 80.0,  # 80% memory usage
            'cpu_usage': 75.0,   # 75% CPU usage
            'active_connections': 50,  # Max DB connections
            'concurrent_users': 100   # Max concurrent users
        }
        
        # Patrones específicos de logs ERP13E
        self.log_patterns = {
            'gunicorn_start': re.compile(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \+0000\] \[(\d+)\] \[INFO\] Starting gunicorn (.+)'),
            'gunicorn_worker': re.compile(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \+0000\] \[(\d+)\] \[INFO\] Booting worker with pid: (\d+)'),
            'http_request': re.compile(r'(\d+\.\d+\.\d+\.\d+) - - \[(.+)\] "(\w+) (.+) HTTP/1\.[01]" (\d+) (\d+) "(.+)" "(.+)" (\d+\.\d+)'),
            'application_log': re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),(\d+) - (.+) - (\w+) - (.+)'),
            'database_query': re.compile(r'Database query executed in (\d+\.\d+)ms'),
            'erp_operation': re.compile(r'ERP13E - (\w+) operation completed in (\d+\.\d+)s'),
            'user_login': re.compile(r'User (\w+) logged in from IP (\d+\.\d+\.\d+\.\d+)'),
            'memory_usage': re.compile(r'Memory usage: (\d+\.\d+)%'),
            'cpu_usage': re.compile(r'CPU usage: (\d+\.\d+)%'),
            'serverless_scale': re.compile(r'Serverless: Scaling to (\d+) instances'),
            'jwt_token': re.compile(r'JWT token (generated|validated) for user (\w+)'),
            'postgresql_connection': re.compile(r'PostgreSQL connection (\w+): (\d+) active connections')
        }
    
    def parse_erp13e_log(self, log_line: str) -> Optional[ERP13EMetrics]:
        """Parse individual ERP13E log line with enhanced patterns"""
        log_line = log_line.strip()
        
        # Parse Gunicorn startup (compatible with existing config)
        if match := self.log_patterns['gunicorn_start'].search(log_line):
            timestamp_str, pid, version = match.groups()
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            return ERP13EMetrics(
                timestamp=timestamp,
                level='INFO',
                message=f'ERP13E Gunicorn {version} started with PID {pid}',
                component='gunicorn'
            )
        
        # Parse worker boot (enhanced for 3 workers)
        if match := self.log_patterns['gunicorn_worker'].search(log_line):
            timestamp_str, master_pid, worker_pid = match.groups()
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            return ERP13EMetrics(
                timestamp=timestamp,
                level='INFO',
                message=f'ERP13E Worker {worker_pid} booted by master {master_pid}',
                component='gunicorn-worker'
            )
        
        # Parse HTTP requests (enhanced for ERP endpoints)
        if match := self.log_patterns['http_request'].search(log_line):
            ip, timestamp_str, method, path, status, size, referer, user_agent, response_time = match.groups()
            timestamp = datetime.strptime(timestamp_str.split()[0], '%d/%b/%Y:%H:%M:%S')
            return ERP13EMetrics(
                timestamp=timestamp,
                level='INFO',
                message=f'ERP13E {method} {path}',
                component='http-erp',
                response_time=float(response_time),
                status_code=int(status),
                endpoint=path
            )
        
        # Parse database queries
        if match := self.log_patterns['database_query'].search(log_line):
            query_time = float(match.group(1))
            return ERP13EMetrics(
                timestamp=datetime.utcnow(),
                level='INFO',
                message=f'Database query executed',
                component='postgresql',
                database_query_time=query_time
            )
        
        # Parse ERP operations
        if match := self.log_patterns['erp_operation'].search(log_line):
            operation, duration = match.groups()
            return ERP13EMetrics(
                timestamp=datetime.utcnow(),
                level='INFO',
                message=f'ERP operation: {operation}',
                component='erp-business-logic',
                response_time=float(duration)
            )
        
        # Parse user authentication
        if match := self.log_patterns['user_login'].search(log_line):
            user_id, ip = match.groups()
            return ERP13EMetrics(
                timestamp=datetime.utcnow(),
                level='INFO',
                message=f'User authentication successful',
                component='auth-jwt',
                user_id=user_id
            )
        
        # Parse serverless scaling
        if match := self.log_patterns['serverless_scale'].search(log_line):
            instances = int(match.group(1))
            return ERP13EMetrics(
                timestamp=datetime.utcnow(),
                level='INFO',
                message=f'Serverless scaling to {instances} instances',
                component='railway-serverless'
            )
        
        return None
    
    async def check_database_health(self) -> Dict[str, Any]:
        """Check PostgreSQL database health"""
        if not self.database_url:
            return {'status': 'not_configured', 'error': 'DATABASE_URL not set'}
        
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()
            
            # Test basic connectivity
            start_time = time.time()
            cursor.execute('SELECT 1')
            query_time = (time.time() - start_time) * 1000
            
            # Get connection stats
            cursor.execute('''
                SELECT count(*) as active_connections 
                FROM pg_stat_activity 
                WHERE state = 'active'
            ''')
            active_connections = cursor.fetchone()[0]
            
            # Get database size
            cursor.execute('''
                SELECT pg_size_pretty(pg_database_size(current_database())) as db_size
            ''')
            db_size = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            return {
                'status': 'healthy',
                'query_time_ms': round(query_time, 2),
                'active_connections': active_connections,
                'database_size': db_size,
                'connection_test': 'passed'
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'connection_test': 'failed'
            }
    
    async def check_application_health(self) -> Dict[str, Any]:
        """Check ERP13E application health via HTTP"""
        try:
            # Try to get the Railway service URL
            service_name = os.environ.get('RAILWAY_SERVICE_NAME', 'erp13e')
            internal_url = f"http://{service_name}.railway.internal"
            
            async with aiohttp.ClientSession() as session:
                # Test health endpoint
                start_time = time.time()
                async with session.get(f"{internal_url}/health", timeout=10) as response:
                    health_time = (time.time() - start_time) * 1000
                    health_data = await response.json()
                
                # Test detailed health endpoint
                start_time = time.time()
                async with session.get(f"{internal_url}/health/detailed", timeout=15) as response:
                    detailed_time = (time.time() - start_time) * 1000
                    detailed_data = await response.json()
                
                return {
                    'status': 'healthy',
                    'health_endpoint_time_ms': round(health_time, 2),
                    'detailed_endpoint_time_ms': round(detailed_time, 2),
                    'application_data': detailed_data
                }
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'health_check': 'failed'
            }
    
    def analyze_erp13e_window(self) -> Dict:
        """Analyze ERP13E metrics within time window"""
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=self.window_minutes)
        
        window_metrics = [m for m in self.metrics_buffer if m.timestamp >= window_start]
        
        if not window_metrics:
            return {
                'status': 'no_data', 
                'window_minutes': self.window_minutes,
                'service': 'ERP13E-Enterprise'
            }
        
        # ERP-specific calculations
        total_requests = len([m for m in window_metrics if m.component == 'http-erp'])
        error_requests = len([m for m in window_metrics if m.component == 'http-erp' and m.status_code >= 400])
        
        response_times = [m.response_time for m in window_metrics if m.response_time is not None]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        db_query_times = [m.database_query_time for m in window_metrics if m.database_query_time is not None]
        avg_db_time = sum(db_query_times) / len(db_query_times) if db_query_times else 0
        
        error_rate = error_requests / total_requests if total_requests > 0 else 0
        
        # Component distribution
        components = defaultdict(int)
        for metric in window_metrics:
            components[metric.component] += 1
        
        # User activity
        unique_users = len(set(m.user_id for m in window_metrics if m.user_id))
        
        # ERP operations
        erp_operations = len([m for m in window_metrics if m.component == 'erp-business-logic'])
        
        return {
            'service': 'ERP13E-Enterprise',
            'environment': self.railway_env,
            'window_minutes': self.window_minutes,
            'performance': {
                'total_requests': total_requests,
                'error_requests': error_requests,
                'error_rate': error_rate,
                'avg_response_time': avg_response_time,
                'avg_database_time': avg_db_time
            },
            'business_metrics': {
                'erp_operations': erp_operations,
                'unique_users': unique_users,
                'auth_events': len([m for m in window_metrics if m.component == 'auth-jwt'])
            },
            'infrastructure': {
                'components': dict(components),
                'serverless_events': len([m for m in window_metrics if m.component == 'railway-serverless'])
            },
            'alerts': self._generate_erp13e_alerts(error_rate, avg_response_time, avg_db_time)
        }
    
    def _generate_erp13e_alerts(self, error_rate: float, avg_response_time: float, avg_db_time: float) -> List[Dict]:
        """Generate ERP13E-specific alerts"""
        alerts = []
        
        if error_rate > self.alert_thresholds['error_rate']:
            alerts.append({
                'type': 'ERP13E_ERROR_RATE_HIGH',
                'severity': 'CRITICAL',
                'message': f'ERP13E error rate {error_rate:.2%} exceeds threshold {self.alert_thresholds["error_rate"]:.2%}',
                'timestamp': datetime.utcnow().isoformat(),
                'impact': 'Business operations may be affected'
            })
        
        if avg_response_time > self.alert_thresholds['avg_response_time']:
            alerts.append({
                'type': 'ERP13E_RESPONSE_TIME_HIGH',
                'severity': 'WARNING',
                'message': f'ERP13E response time {avg_response_time:.2f}s exceeds threshold {self.alert_thresholds["avg_response_time"]:.2f}s',
                'timestamp': datetime.utcnow().isoformat(),
                'impact': 'User experience degradation'
            })
        
        if avg_db_time > self.alert_thresholds['database_query_time']:
            alerts.append({
                'type': 'ERP13E_DATABASE_SLOW',
                'severity': 'WARNING',
                'message': f'Database query time {avg_db_time:.2f}ms exceeds threshold {self.alert_thresholds["database_query_time"]:.2f}ms',
                'timestamp': datetime.utcnow().isoformat(),
                'impact': 'Database performance issues detected'
            })
        
        return alerts
    
    async def comprehensive_health_check(self) -> Dict:
        """Comprehensive health check combining all systems"""
        db_health = await self.check_database_health()
        app_health = await self.check_application_health()
        window_analysis = self.analyze_erp13e_window()
        
        overall_status = 'healthy'
        if db_health['status'] != 'healthy' or app_health['status'] != 'healthy':
            overall_status = 'degraded'
        
        if window_analysis.get('alerts', []):
            if any(alert['severity'] == 'CRITICAL' for alert in window_analysis['alerts']):
                overall_status = 'critical'
        
        return {
            'service': 'ERP13E-Enterprise',
            'overall_status': overall_status,
            'timestamp': datetime.utcnow().isoformat(),
            'environment': self.railway_env,
            'components': {
                'database': db_health,
                'application': app_health,
                'monitoring': window_analysis
            }
        }

# Main monitoring function for ERP13E
async def monitor_erp13e_system(log_content: str = None) -> Dict:
    """Main monitoring function for ERP13E Enterprise"""
    monitor = ERP13EMonitor()
    
    if log_content:
        log_lines = log_content.strip().split('\n')
        for line in log_lines:
            metric = monitor.parse_erp13e_log(line)
            if metric:
                monitor.metrics_buffer.append(metric)
    
    return await monitor.comprehensive_health_check()

# CLI interface for ERP13E monitoring
if __name__ == "__main__":
    import asyncio
    
    # Sample ERP13E logs for testing
    sample_erp13e_logs = """
2025-09-20T15:03:21.000000000Z [inf] Starting Container
2025-09-20T15:03:22.628040746Z [err] [2025-09-20 15:03:21 +0000] [1] [INFO] Starting gunicorn 21.2.0
2025-09-20T15:03:22.628044712Z [err] [2025-09-20 15:03:21 +0000] [1] [INFO] Listening at: http://0.0.0.0:8080 (1)
2025-09-20T15:03:22.628048630Z [err] [2025-09-20 15:03:21 +0000] [1] [INFO] Using worker: gthread
2025-09-20T15:03:22.628052639Z [err] [2025-09-20 15:03:21 +0000] [4] [INFO] Booting worker with pid: 4
ERP13E - invoice_processing operation completed in 1.2s
User john_doe logged in from IP 192.168.1.100
Database query executed in 150.5ms
JWT token generated for user jane_smith
Serverless: Scaling to 2 instances
    """
    
    async def test_monitor():
        result = await monitor_erp13e_system(sample_erp13e_logs)
        print(json.dumps(result, indent=2, default=str))
    
    asyncio.run(test_monitor())
