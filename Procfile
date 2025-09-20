# 📁 Ruta: /app/Procfile
# 📄 Nombre: Procfile
# 🏗️ Propósito: Configuración Railway deployment ERP13 Enterprise
# ⚡ Performance: Optimizado para producción con workers
# 🔒 Seguridad: Configuración segura para binding

web: gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 2 --worker-class gthread --timeout 30 --keep-alive 2 --max-requests 1000 --max-requests-jitter 100 --log-level info wsgi:application
