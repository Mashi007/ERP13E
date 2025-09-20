# Procfile para Railway - ERP13 Enterprise v3.0
# Configuración optimizada de Gunicorn con health checks y logging

web: gunicorn --bind 0.0.0.0:$PORT --workers 2 --worker-class sync --timeout 120 --keep-alive 5 --max-requests 1000 --max-requests-jitter 50 --preload --worker-tmp-dir /dev/shm --log-level info --access-logfile - --error-logfile - --capture-output --enable-stdio-inheritance --pythonpath . wsgi:application
