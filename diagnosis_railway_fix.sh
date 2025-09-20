# DIAGNÓSTICO Y SOLUCIÓN RAILWAY DEPLOYMENT
# 📁 Ruta: /diagnosis_railway_fix.sh
# 🏗️ Propósito: Resolver problemas sync archivos Railway
# ⚡ Performance: Comandos optimizados para fix rápido

echo "🔍 DIAGNÓSTICO RAILWAY DEPLOYMENT INICIADO..."

# ========== VERIFICACIÓN 1: GIT STATUS ==========
echo ""
echo "1️⃣ VERIFICANDO ESTADO GIT:"
git status

echo ""
echo "2️⃣ VERIFICANDO ARCHIVOS NO TRACKEADOS:"
git ls-files --others --exclude-standard

# ========== VERIFICACIÓN 2: .GITIGNORE ==========
echo ""
echo "3️⃣ VERIFICANDO .GITIGNORE:"
if [ -f .gitignore ]; then
    echo "📄 Contenido .gitignore:"
    cat .gitignore
else
    echo "⚠️ .gitignore NO EXISTE"
fi

# ========== VERIFICACIÓN 3: ESTRUCTURA TEMPLATES ==========
echo ""
echo "4️⃣ VERIFICANDO ESTRUCTURA TEMPLATES:"
find . -name "*.html" -type f | head -20

# ========== SOLUCIÓN: FORZAR ADD TEMPLATES ==========
echo ""
echo "🔧 APLICANDO FIX AUTOMÁTICO..."

# Crear directorio errors si no existe
mkdir -p templates/errors

# Agregar archivos específicos
git add templates/ -f
git add templates/errors/ -f
git add . -f

echo ""
echo "5️⃣ ESTADO POST-FIX:"
git status

echo ""
echo "📝 COMANDOS SUGERIDOS PARA EJECUTAR:"
echo "git commit -m 'fix: Force add critical templates for Railway deployment'"
echo "git push origin main --force"

echo ""
echo "🚀 ALTERNATIVA RAILWAY CLI:"
echo "railway redeploy"
echo "railway logs"
