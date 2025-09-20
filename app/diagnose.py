#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📁 Ruta: /app/diagnose.py
📄 Nombre: diagnose.py
🏗️ Propósito: Script de diagnóstico para problemas de Railway deployment
⚡ Performance: Verificación rápida de estructura y configuración
🔒 Seguridad: Solo lectura, no modifica archivos

ERP13 Enterprise - Diagnostic Script
Identifica problemas de estructura de archivos y configuración
"""

import os
import sys
import json
from pathlib import Path

def diagnose_railway_deployment():
    """
    🔍 Diagnóstico completo del deployment en Railway
    """
    print("=" * 60)
    print("🔍 ERP13 ENTERPRISE - RAILWAY DIAGNOSTIC REPORT")
    print("=" * 60)
    
    # 1. VERIFICAR DIRECTORIO DE TRABAJO
    print(f"\n📁 WORKING DIRECTORY:")
    print(f"   Current: {os.getcwd()}")
    print(f"   Script location: {os.path.dirname(os.path.abspath(__file__))}")
    
    # 2. VERIFICAR ARCHIVOS CRÍTICOS
    print(f"\n📋 CRITICAL FILES CHECK:")
    critical_files = [
        'main.py',
        'wsgi.py', 
        'app.py',
        'requirements.txt',
        'health.py',
        'railway.toml'
    ]
    
    missing_files = []
    for file in critical_files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"   ✅ {file} ({size} bytes)")
        else:
            print(f"   ❌ {file} (MISSING)")
            missing_files.append(file)
    
    # 3. VERIFICAR ESTRUCTURA DE DIRECTORIOS
    print(f"\n📂 DIRECTORY STRUCTURE:")
    important_dirs = ['templates', 'static', 'migrations']
    for dir_name in important_dirs:
        if os.path.exists(dir_name):
            files_count = len(os.listdir(dir_name))
            print(f"   ✅ {dir_name}/ ({files_count} items)")
        else:
            print(f"   ⚠️ {dir_name}/ (not found)")
    
    # 4. VERIFICAR CONTENIDO DE ARCHIVOS CRÍTICOS
    print(f"\n📄 FILE CONTENT ANALYSIS:")
    
    # Verificar wsgi.py
    if os.path.exists('wsgi.py'):
        with open('wsgi.py', 'r') as f:
            wsgi_content = f.read()
            has_application = 'application' in wsgi_content
            has_import = 'from main import' in wsgi_content or 'from app import' in wsgi_content
            print(f"   📄 wsgi.py:")
            print(f"      - Has 'application' variable: {'✅' if has_application else '❌'}")
            print(f"      - Has import statement: {'✅' if has_import else '❌'}")
    
    # Verificar main.py
    if os.path.exists('main.py'):
        with open('main.py', 'r') as f:
            main_content = f.read()
            has_app = 'app = ' in main_content
            has_flask = 'from flask import' in main_content
            print(f"   📄 main.py:")
            print(f"      - Has 'app = ' definition: {'✅' if has_app else '❌'}")
            print(f"      - Imports Flask: {'✅' if has_flask else '❌'}")
    
    # 5. VERIFICAR VARIABLES DE ENTORNO
    print(f"\n🌐 ENVIRONMENT VARIABLES:")
    env_vars = ['PORT', 'RAILWAY_ENVIRONMENT', 'DATABASE_URL', 'REDIS_URL', 'SECRET_KEY']
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            # Ocultar valores sensibles
            if var in ['SECRET_KEY', 'DATABASE_URL', 'REDIS_URL']:
                display_value = f"{value[:10]}..." if len(value) > 10 else "***"
            else:
                display_value = value
            print(f"   ✅ {var}: {display_value}")
        else:
            print(f"   ⚠️ {var}: Not set")
    
    # 6. VERIFICAR PYTHON Y MÓDULOS
    print(f"\n🐍 PYTHON ENVIRONMENT:")
    print(f"   Python version: {sys.version}")
    print(f"   Python path: {sys.executable}")
    
    # Verificar módulos críticos
    critical_modules = ['flask', 'gunicorn', 'psycopg2', 'redis']
    print(f"\n📦 CRITICAL MODULES:")
    for module in critical_modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError:
            print(f"   ❌ {module} (not installed)")
    
    # 7. INTENTAR IMPORTAR LA APLICACIÓN
    print(f"\n🚀 APPLICATION IMPORT TEST:")
    app_imported = False
    
    # Test main.py
    try:
        sys.path.insert(0, os.getcwd())
        from main import app
        print(f"   ✅ Successfully imported from main.py")
        print(f"   📊 App type: {type(app)}")
        app_imported = True
    except Exception as e:
        print(f"   ❌ Failed to import from main.py: {e}")
    
    # Test app.py si main.py falla
    if not app_imported:
        try:
            from app import app
            print(f"   ✅ Successfully imported from app.py")
            app_imported = True
        except Exception as e:
            print(f"   ❌ Failed to import from app.py: {e}")
    
    # 8. GENERAR RECOMENDACIONES
    print(f"\n💡 RECOMMENDATIONS:")
    
    if missing_files:
        print(f"   📋 Missing files to create: {', '.join(missing_files)}")
    
    if not app_imported:
        print(f"   🚨 CRITICAL: Cannot import Flask application")
        print(f"      - Verify main.py exists and has 'app = Flask(__name__)'")
        print(f"      - Check for syntax errors in main.py")
        print(f"      - Ensure all imports are available")
    
    if 'wsgi.py' in missing_files or not os.path.exists('wsgi.py'):
        print(f"   🚨 CRITICAL: wsgi.py missing - required for Gunicorn")
    
    # 9. ESTADO GENERAL
    print(f"\n📊 OVERALL STATUS:")
    critical_score = len(critical_files) - len(missing_files)
    max_score = len(critical_files)
    
    if critical_score == max_score and app_imported:
        status = "🟢 GOOD - Ready for deployment"
    elif critical_score >= max_score * 0.8:
        status = "🟡 WARNING - Minor issues detected"
    else:
        status = "🔴 CRITICAL - Major issues require fixing"
    
    print(f"   Status: {status}")
    print(f"   Score: {critical_score}/{max_score} critical files present")
    
    print("=" * 60)
    print("🏁 DIAGNOSTIC COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    diagnose_railway_deployment()
