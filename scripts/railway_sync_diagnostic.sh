#!/bin/bash

# =============================================================================
# 📁 Ruta: /scripts/railway_sync_diagnostic.sh
# 📄 Nombre: railway_sync_diagnostic.sh
# 🏗️ Propósito: Diagnóstico y resolución de sincronización GitHub-Railway
# ⚡ Performance: Verificación automática, logs detallados
# 🔒 Seguridad: Validación de repositorio, backup de configuración
# =============================================================================

echo "🔍 DIAGNÓSTICO RAILWAY-GITHUB SYNC - ERP13 ENTERPRISE"
echo "================================================================"

# 1. VERIFICACIÓN DEL REPOSITORIO LOCAL
echo "📁 1. VERIFICANDO ESTADO DEL REPOSITORIO..."
git status
echo ""

# 2. VERIFICACIÓN DEL ARCHIVO WSGI.PY
echo "📄 2. VERIFICANDO CONTENIDO DE WSGI.PY..."
if [ -f "wsgi.py" ]; then
    echo "✅ wsgi.py encontrado"
    echo "📝 Primeras 5 líneas:"
    head -5 wsgi.py
    echo ""
    
    # Verificar si contiene comandos bash (problema detectado)
    if grep -q "cd /c/Users" wsgi.py; then
        echo "🚨 ERROR CRÍTICO: wsgi.py contiene comandos bash"
        echo "❌ Archivo corrupto detectado"
    else
        echo "✅ wsgi.py parece válido (código Python)"
    fi
else
    echo "❌ wsgi.py NO encontrado"
fi
echo ""

# 3. VERIFICACIÓN DE ARCHIVOS CRÍTICOS
echo "📋 3. VERIFICANDO ARCHIVOS CRÍTICOS..."
files=("main.py" "app.py" "requirements.txt" "Procfile" "gunicorn.conf.py")

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file - encontrado"
    else
        echo "❌ $file - FALTANTE"
    fi
done
echo ""

# 4. VERIFICACIÓN DEL ÚLTIMO COMMIT
echo "📊 4. ÚLTIMO COMMIT EN GITHUB..."
git log -1 --oneline
echo ""

# 5. VERIFICACIÓN DE BRANCH
echo "🌿 5. BRANCH ACTIVO..."
current_branch=$(git branch --show-current)
echo "Branch actual: $current_branch"

if [ "$current_branch" != "main" ] && [ "$current_branch" != "master" ]; then
    echo "⚠️ ADVERTENCIA: No estás en main/master"
    echo "Railway podría estar usando una branch diferente"
fi
echo ""

# 6. VERIFICACIÓN DE CAMBIOS NO COMMITADOS
echo "🔄 6. CAMBIOS PENDIENTES..."
if git diff-index --quiet HEAD --; then
    echo "✅ No hay cambios pendientes"
else
    echo "⚠️ HAY CAMBIOS SIN COMMITEAR:"
    git diff --name-only
fi
echo ""

# 7. VERIFICACIÓN DE RAILWAY CONFIG (si existe)
echo "🚂 7. CONFIGURACIÓN RAILWAY..."
if [ -f "railway.toml" ]; then
    echo "✅ railway.toml encontrado"
    cat railway.toml
else
    echo "ℹ️ railway.toml no encontrado (opcional)"
fi
echo ""

# 8. GENERAR REPORTE
echo "📋 RESUMEN DEL DIAGNÓSTICO"
echo "=========================="
echo "📅 Fecha: $(date)"
echo "📁 Directorio: $(pwd)"
echo "🌿 Branch: $current_branch"
echo "📝 Último commit: $(git log -1 --oneline)"
echo ""

# 9. RECOMENDACIONES
echo "💡 ACCIONES RECOMENDADAS:"
echo "1. Verificar Railway Project Settings → Source"
echo "2. Confirmar branch correcta en Railway"
echo "3. Forzar nuevo deployment si archivos están OK"
echo "4. Revisar Railway build logs para errores"
echo ""
echo "🔗 Railway Dashboard: https://railway.app/dashboard"
echo "================================================================"
