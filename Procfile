# =============================================================================
# 📁 Ruta: /Procfile
# 📄 Nombre: Procfile
# 🏗️ Propósito: Comando de inicio alternativo para Railway
# ⚡ Performance: Configuración Gunicorn optimizada
# 🔒 Seguridad: Workers sincronos con timeouts apropiados
# =============================================================================

# 🚀 COMANDO PRINCIPAL PARA RAILWAY
web: gunicorn --bind 0.0.0.0:$PORT --workers 2 --worker-class sync --worker-tmp-dir /dev/shm --timeout 60 --keep-alive 5 --max-requests 1000 --max-requests-jitter 100 --log-level info --access-logfile - --error-logfile - wsgi:application

# 🔄 COMANDOS ALTERNATIVOS (comentados por defecto)
# Desarrollo local:
# dev: python wsgi.py

# Con más workers (para alta carga):
# web-scaled: gunicorn --bind 0.0.0.0:$PORT --workers 4 --worker-class sync --worker-tmp-dir /dev/shm --timeout 120 --keep-alive 5 wsgi:application

# Con workers asíncronos (si necesitas WebSockets):
# web-async: gunicorn --bind 0.0.0.0:$PORT --workers 2 --worker-class gevent --worker-connections 1000 wsgi:application

# Para debugging en production (temporal):
# debug: gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 0 --reload --log-level debug wsgi:application
