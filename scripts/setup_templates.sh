#!/bin/bash
# 📁 Ruta: /scripts/setup_templates.sh
# 📄 Nombre: setup_templates.sh
# 🏗️ Propósito: Script para crear estructura de templates críticos
# ⚡ Performance: Setup rápido para Railway deployment

echo "🚀 Setting up ERP13 Enterprise Templates Structure..."

# Crear directorios necesarios
mkdir -p templates/errors
mkdir -p templates/clientes
mkdir -p templates/facturacion
mkdir -p templates/auditoria
mkdir -p templates/configuracion
mkdir -p static/css
mkdir -p static/js

echo "📁 Directories created successfully"

# Crear layout.html
cat > templates/layout.html << 'EOF'
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}ERP13 Enterprise{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    {% block extra_css %}{% endblock %}
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container-fluid">
            <a class="navbar-brand" href="/dashboard">
                <i class="fas fa-chart-line me-2"></i>ERP13 Enterprise
            </a>
        </div>
    </nav>
    
    <div class="container-fluid mt-3">
        {% block content %}{% endblock %}
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
EOF

# Crear login.html
cat > templates/login.html << 'EOF'
{% extends "layout.html" %}
{% block title %}Login - ERP13 Enterprise{% endblock %}
{% block content %}
<div class="row justify-content-center mt-5">
    <div class="col-md-4">
        <div class="card shadow">
            <div class="card-body">
                <h3 class="text-center mb-4">ERP13 Enterprise</h3>
                <form action="/login" method="POST">
                    <div class="mb-3">
                        <label class="form-label">Usuario</label>
                        <input type="text" class="form-control" name="username" required>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Contraseña</label>
                        <input type="password" class="form-control" name="password" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Iniciar Sesión</button>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
EOF

# Crear dashboard.html
cat > templates/dashboard.html << 'EOF'
{% extends "layout.html" %}
{% block title %}Dashboard - ERP13 Enterprise{% endblock %}
{% block content %}
<div class="row mb-4">
    <div class="col-12">
        <h2>Dashboard Principal</h2>
        <p class="text-muted">Bienvenido a {{ company_name }}</p>
    </div>
</div>

<div class="row">
    <div class="col-md-3">
        <div class="card bg-primary text-white">
            <div class="card-body">
                <h5 class="card-title">Ventas Totales</h5>
                <h3>{{ total_sales }}</h3>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card bg-success text-white">
            <div class="card-body">
                <h5 class="card-title">Clientes Activos</h5>
                <h3>{{ active_clients }}</h3>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card bg-warning text-white">
            <div class="card-body">
                <h5 class="card-title">Pedidos Pendientes</h5>
                <h3>{{ pending_orders }}</h3>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card bg-info text-white">
            <div class="card-body">
                <h5 class="card-title">Ingresos del Mes</h5>
                <h3>{{ monthly_revenue }}</h3>
            </div>
        </div>
    </div>
</div>
{% endblock %}
EOF

# Crear 404.html
cat > templates/errors/404.html << 'EOF'
{% extends "layout.html" %}
{% block title %}404 - Página no encontrada{% endblock %}
{% block content %}
<div class="text-center mt-5">
    <h1 class="display-1">404</h1>
    <h2>Página no encontrada</h2>
    <p>La página que buscas no existe.</p>
    <a href="/dashboard" class="btn btn-primary">Volver al Dashboard</a>
</div>
{% endblock %}
EOF

# Crear 500.html
cat > templates/errors/500.html << 'EOF'
{% extends "layout.html" %}
{% block title %}500 - Error del servidor{% endblock %}
{% block content %}
<div class="text-center mt-5">
    <h1 class="display-1">500</h1>
    <h2>Error del servidor</h2>
    <p>Ha ocurrido un error interno. Por favor, intenta más tarde.</p>
    <a href="/dashboard" class="btn btn-primary">Volver al Dashboard</a>
</div>
{% endblock %}
EOF

echo "✅ Templates created successfully!"
echo ""
echo "📋 Created files:"
echo "   - templates/layout.html"
echo "   - templates/login.html"
echo "   - templates/dashboard.html"
echo "   - templates/errors/404.html"
echo "   - templates/errors/500.html"
echo ""
echo "🚀 Ready for Railway deployment!"
