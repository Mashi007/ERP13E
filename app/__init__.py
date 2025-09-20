"""
ERP13 Enterprise Factory Pattern  Anti-Rupturas
Diseño: Single factory + blueprints modulares independientes
"""

def create_app(config_name='production'):
    """Factory pattern UNIFICADO - Evita duplicaciones"""
    app = Flask(__name__)
    
    # Core system initialization
    initialize_core_systems(app)
    
    # Register modular blueprints SOLO si existen
    register_module_blueprints(app)
    
    return app

def register_module_blueprints(app):
    """Registro modular - NO falla si módulos no existen"""
    
    modules = [
        'dashboard', 'clientes', 'auditoria', 
        'facturacion', 'configuracion', 'inventory', 
        'sales', 'accounting', 'production'
    ]
    
    for module_name in modules:
        try:
            module = import_module(f'app.modules.{module_name}.routes')
            app.register_blueprint(
                module.blueprint, 
                url_prefix=f'/{module_name}'
            )
        except ImportError:
            # Módulo no existe - continúa sin fallar
            app.logger.warning(f"Module {module_name} not found")
