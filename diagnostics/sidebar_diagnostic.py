#!/usr/bin/env python3
"""
📁 Ruta: /app/diagnostics/sidebar_diagnostic.py
📄 Nombre: sidebar_diagnostic.py
🏗️ Propósito: Verificación integral del sidebar ERP13 Enterprise v3.1
⚡ Performance: Diagnóstico rápido de componentes de navegación
🔒 Seguridad: Verificación de rutas autorizadas
"""

import requests
import json
from datetime import datetime

class ERP13SidebarDiagnostic:
    def __init__(self, base_url="https://erp13e-production-f4b6.up.railway.app"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def login_and_get_session(self):
        """Autenticación para obtener sesión válida"""
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }
        
        response = self.session.post(f"{self.base_url}/do_login", data=login_data)
        return response.status_code == 302  # Redirección exitosa
    
    def check_dashboard_sidebar(self):
        """Verificar que el dashboard contiene elementos del sidebar"""
        response = self.session.get(f"{self.base_url}/dashboard")
        
        if response.status_code != 200:
            return False, f"Dashboard no accesible: {response.status_code}"
        
        content = response.text
        
        # Verificar elementos críticos del sidebar
        sidebar_elements = [
            'class="sidebar"',
            'class="nav-item"',
            'class="nav-link"',
            'fas fa-chart-pie',  # Dashboard icon
            'fas fa-users',      # Clientes icon
            'fas fa-file-invoice', # Facturas icon
            'nav-text'
        ]
        
        missing_elements = []
        for element in sidebar_elements:
            if element not in content:
                missing_elements.append(element)
        
        return len(missing_elements) == 0, missing_elements
    
    def verify_sidebar_routes(self):
        """Verificar que las rutas del sidebar están disponibles"""
        routes_to_check = [
            '/dashboard',
            '/clientes',
            '/facturas',
            '/productos',
            '/reportes',
            '/configuracion'
        ]
        
        route_status = {}
        
        for route in routes_to_check:
            try:
                response = self.session.get(f"{self.base_url}{route}")
                route_status[route] = response.status_code
            except Exception as e:
                route_status[route] = f"Error: {str(e)}"
        
        return route_status
    
    def run_full_diagnostic(self):
        """Ejecutar diagnóstico completo del sidebar"""
        print("🔍 DIAGNÓSTICO SIDEBAR ERP13 ENTERPRISE v3.1")
        print("=" * 50)
        
        # 1. Login
        print("1. Verificando autenticación...")
        login_success = self.login_and_get_session()
        print(f"   ✅ Login: {'EXITOSO' if login_success else '❌ FALLIDO'}")
        
        if not login_success:
            print("❌ No se puede continuar sin autenticación válida")
            return
        
        # 2. Verificar contenido del sidebar
        print("\n2. Verificando elementos del sidebar...")
        sidebar_ok, missing = self.check_dashboard_sidebar()
        
        if sidebar_ok:
            print("   ✅ Sidebar: DESPLEGADO CORRECTAMENTE")
        else:
            print("   ❌ Sidebar: ELEMENTOS FALTANTES")
            for element in missing:
                print(f"      - {element}")
        
        # 3. Verificar rutas de navegación
        print("\n3. Verificando rutas de navegación...")
        routes = self.verify_sidebar_routes()
        
        for route, status in routes.items():
            status_icon = "✅" if status == 200 else "❌"
            print(f"   {status_icon} {route}: {status}")
        
        # 4. Diagnóstico final
        print(f"\n📊 RESULTADO FINAL:")
        print(f"   Login: {'✅' if login_success else '❌'}")
        print(f"   Sidebar: {'✅' if sidebar_ok else '❌'}")
        print(f"   Rutas operativas: {sum(1 for s in routes.values() if s == 200)}/{len(routes)}")
        
        return {
            'login_success': login_success,
            'sidebar_deployed': sidebar_ok,
            'missing_elements': missing if not sidebar_ok else [],
            'route_status': routes,
            'timestamp': datetime.now().isoformat()
        }

if __name__ == "__main__":
    diagnostic = ERP13SidebarDiagnostic()
    result = diagnostic.run_full_diagnostic()
    
    # Guardar resultado en JSON para análisis
    with open('sidebar_diagnostic_result.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n💾 Resultado guardado en: sidebar_diagnostic_result.json")
