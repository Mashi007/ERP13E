# Ruta: /Procfile
# Nombre: Procfile
# Propósito: Configuración de procesos para Railway deployment
# Performance: Gunicorn optimizado, workers dinámicos, health monitoring

web: gunicorn --bind 0.0.0.0:$PORT --workers $WEB_CONCURRENCY --threads 4 --timeout 120 --keepalive 5 --max-requests 1000 --max-requests-jitter 100 --preload --access-logfile - --error-logfile - wsgi:application
