"""
📁 Ruta: /app/modules/configuracion/routes.py
📄 Nombre: routes.py
🏗️ Propósito: Blueprint configuración con AI + campos dinámicos
⚡ Performance: Interfaces optimizadas para administración
🔒 Seguridad: Validación de tokens y permisos

ERP13 Enterprise - Módulo Configuración
Configuración AI, campos dinámicos y settings del sistema
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
import json
from typing import Dict, List, Any
import sqlite3
import logging

# Importar el servicio AI
from app.core.ai_service import get_ai_service, AIConfig

logger = logging.getLogger(__name__)

# Crear el blueprint
blueprint = Blueprint('configuracion', __name__)

# =============================================================================
# RUTAS HTML - PÁGINAS DE CONFIGURACIÓN
# =============================================================================

@blueprint.route('/general')
def general():
    """Configuración general del sistema"""
    try:
        # Obtener configuraciones generales desde DB
        general_config = get_general_config()
        
        return render_template('configuracion/general.html', 
                             config=general_config,
                             page_title="Configuración General")
    except Exception as e:
        logger.error(f"Error en configuración general: {str(e)}")
        flash(f"Error al cargar configuración general: {str(e)}", "error")
        return render_template('configuracion/general.html', 
                             config={},
                             page_title="Configuración General")

@blueprint.route('/usuarios')
def usuarios():
    """Gestión de usuarios y permisos"""
    try:
        # Obtener lista de usuarios
        usuarios = get_users_config()
        
        return render_template('configuracion/usuarios.html',
                             usuarios=usuarios,
                             page_title="Gestión de Usuarios")
    except Exception as e:
        logger.error(f"Error en configuración usuarios: {str(e)}")
        flash(f"Error al cargar usuarios: {str(e)}", "error")
        return render_template('configuracion/usuarios.html',
                             usuarios=[],
                             page_title="Gestión de Usuarios")

@blueprint.route('/plantillas')
def plantillas():
    """Configuración de plantillas de documentos"""
    try:
        # Obtener plantillas disponibles
        plantillas = get_document_templates()
        
        return render_template('configuracion/plantillas.html',
                             plantillas=plantillas,
                             page_title="Plantillas de Documentos")
    except Exception as e:
        logger.error(f"Error en plantillas: {str(e)}")
        flash(f"Error al cargar plantillas: {str(e)}", "error")
        return render_template('configuracion/plantillas.html',
                             plantillas=[],
                             page_title="Plantillas de Documentos")

@blueprint.route('/ia')
def ia():
    """Configuración de Inteligencia Artificial"""
    try:
        ai_service = get_ai_service()
        
        # Obtener configuración AI actual
        current_config = get_ai_config_from_db()
        
        # Obtener proveedores disponibles
        providers = ai_service.get_available_providers()
        
        # Obtener modelos por proveedor
        provider_models = {}
        for provider in providers:
            provider_models[provider] = ai_service.get_provider_models(provider)
        
        return render_template('configuracion/ia.html',
                             current_config=current_config,
                             providers=providers,
                             provider_models=provider_models,
                             page_title="Configuración de IA")
    except Exception as e:
        logger.error(f"Error en configuración IA: {str(e)}")
        flash(f"Error al cargar configuración IA: {str(e)}", "error")
        return render_template('configuracion/ia.html',
                             current_config={},
                             providers=[],
                             provider_models={},
                             page_title="Configuración de IA")

@blueprint.route('/facturacion')
def facturacion():
    """Configuración del sistema de facturación"""
    try:
        # Obtener configuración de facturación
        facturacion_config = get_billing_config()
        
        return render_template('configuracion/facturacion.html',
                             config=facturacion_config,
                             page_title="Configuración de Facturación")
    except Exception as e:
        logger.error(f"Error en configuración facturación: {str(e)}")
        flash(f"Error al cargar configuración de facturación: {str(e)}", "error")
        return render_template('configuracion/facturacion.html',
                             config={},
                             page_title="Configuración de Facturación")

@blueprint.route('/campos-clientes')
def campos_clientes():
    """Configuración de campos dinámicos para clientes"""
    try:
        # Obtener campos dinámicos configurados
        dynamic_fields = get_client_dynamic_fields()
        
        # Tipos de campos disponibles
        field_types = [
            {'value': 'text', 'label': 'Texto simple'},
            {'value': 'number', 'label': 'Número'},
            {'value': 'date', 'label': 'Fecha'},
            {'value': 'email', 'label': 'Email'},
            {'value': 'select', 'label': 'Lista desplegable'},
            {'value': 'checkbox', 'label': 'Checkbox (sí/no)'},
            {'value': 'textarea', 'label': 'Área de texto'}
        ]
        
        return render_template('configuracion/campos_clientes.html',
                             dynamic_fields=dynamic_fields,
                             field_types=field_types,
                             page_title="Campos Dinámicos - Clientes")
    except Exception as e:
        logger.error(f"Error en campos dinámicos: {str(e)}")
        flash(f"Error al cargar campos dinámicos: {str(e)}", "error")
        return render_template('configuracion/campos_clientes.html',
                             dynamic_fields=[],
                             field_types=[],
                             page_title="Campos Dinámicos - Clientes")

# =============================================================================
# APIs JSON - CONFIGURACIÓN AI
# =============================================================================

@blueprint.route('/api/ai-config', methods=['GET'])
def api_get_ai_config():
    """API: Obtener configuración AI actual"""
    try:
        config = get_ai_config_from_db()
        return jsonify({
            'success': True,
            'config': config
        })
    except Exception as e:
        logger.error(f"Error API get AI config: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blueprint.route('/api/ai-config', methods=['POST'])
def api_save_ai_config():
    """API: Guardar configuración AI"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['provider', 'model']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido: {field}'
                }), 400
        
        # Crear configuración AI
        ai_config = AIConfig(
            provider=data['provider'],
            api_key=data.get('api_key', ''),
            model=data['model'],
            base_url=data.get('base_url'),
            max_tokens=int(data.get('max_tokens', 4000)),
            temperature=float(data.get('temperature', 0.7)),
            enabled=bool(data.get('enabled', True))
        )
        
        # Validar configuración con el servicio AI
        ai_service = get_ai_service()
        if not ai_service.set_config(ai_config):
            return jsonify({
                'success': False,
                'error': 'Configuración AI inválida'
            }), 400
        
        # Guardar en base de datos
        save_ai_config_to_db(ai_config)
        
        return jsonify({
            'success': True,
            'message': 'Configuración AI guardada exitosamente'
        })
        
    except Exception as e:
        logger.error(f"Error API save AI config: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blueprint.route('/api/ai-test', methods=['POST'])
def api_test_ai():
    """API: Probar conexión AI"""
    try:
        ai_service = get_ai_service()
        
        if not ai_service.is_enabled():
            return jsonify({
                'success': False,
                'error': 'AI no está configurado'
            })
        
        # Mensaje de prueba
        test_message = "Hola, este es un mensaje de prueba. Responde brevemente que la conexión funciona correctamente."
        
        response = ai_service.chat([{
            'role': 'user',
            'content': test_message
        }])
        
        if response.success:
            return jsonify({
                'success': True,
                'message': 'Conexión AI exitosa',
                'response': response.content,
                'provider': response.provider,
                'model': response.model,
                'tokens_used': response.tokens_used
            })
        else:
            return jsonify({
                'success': False,
                'error': response.error
            })
            
    except Exception as e:
        logger.error(f"Error API test AI: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blueprint.route('/api/ai-models/<provider>')
def api_get_ai_models(provider):
    """API: Obtener modelos disponibles para un proveedor"""
    try:
        ai_service = get_ai_service()
        models = ai_service.get_provider_models(provider)
        
        return jsonify({
            'success': True,
            'models': models
        })
    except Exception as e:
        logger.error(f"Error API get AI models: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# =============================================================================
# APIs JSON - CAMPOS DINÁMICOS
# =============================================================================

@blueprint.route('/api/dynamic-fields', methods=['GET'])
def api_get_dynamic_fields():
    """API: Obtener campos dinámicos"""
    try:
        fields = get_client_dynamic_fields()
        return jsonify({
            'success': True,
            'fields': fields
        })
    except Exception as e:
        logger.error(f"Error API get dynamic fields: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blueprint.route('/api/dynamic-fields', methods=['POST'])
def api_create_dynamic_field():
    """API: Crear nuevo campo dinámico"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['name', 'label', 'type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido: {field}'
                }), 400
        
        # Crear campo dinámico
        field_data = {
            'name': data['name'],
            'label': data['label'],
            'type': data['type'],
            'required': bool(data.get('required', False)),
            'options': data.get('options', []),  # Para select
            'placeholder': data.get('placeholder', ''),
            'default_value': data.get('default_value', ''),
            'validation_rules': data.get('validation_rules', {}),
            'order': int(data.get('order', 0))
        }
        
        # Guardar en base de datos
        field_id = save_dynamic_field(field_data)
        
        return jsonify({
            'success': True,
            'message': 'Campo dinámico creado exitosamente',
            'field_id': field_id
        })
        
    except Exception as e:
        logger.error(f"Error API create dynamic field: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blueprint.route('/api/dynamic-fields/<int:field_id>', methods=['PUT'])
def api_update_dynamic_field(field_id):
    """API: Actualizar campo dinámico"""
    try:
        data = request.get_json()
        
        # Actualizar campo dinámico
        updated = update_dynamic_field(field_id, data)
        
        if updated:
            return jsonify({
                'success': True,
                'message': 'Campo dinámico actualizado exitosamente'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Campo no encontrado'
            }), 404
            
    except Exception as e:
        logger.error(f"Error API update dynamic field: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@blueprint.route('/api/dynamic-fields/<int:field_id>', methods=['DELETE'])
def api_delete_dynamic_field(field_id):
    """API: Eliminar campo dinámico"""
    try:
        deleted = delete_dynamic_field(field_id)
        
        if deleted:
            return jsonify({
                'success': True,
                'message': 'Campo dinámico eliminado exitosamente'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Campo no encontrado'
            }), 404
            
    except Exception as e:
        logger.error(f"Error API delete dynamic field: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# =============================================================================
# FUNCIONES DE BASE DE DATOS
# =============================================================================

def get_db_connection():
    """Obtener conexión a la base de datos"""
    conn = sqlite3.connect('erp_database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_config_tables():
    """Inicializar tablas de configuración"""
    conn = get_db_connection()
    
    # Tabla de configuración AI
    conn.execute('''
        CREATE TABLE IF NOT EXISTS ai_config (
            id INTEGER PRIMARY KEY,
            provider TEXT NOT NULL,
            api_key TEXT,
            model TEXT NOT NULL,
            base_url TEXT,
            max_tokens INTEGER DEFAULT 4000,
            temperature REAL DEFAULT 0.7,
            enabled BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de campos dinámicos
    conn.execute('''
        CREATE TABLE IF NOT EXISTS client_dynamic_fields (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            label TEXT NOT NULL,
            type TEXT NOT NULL,
            required BOOLEAN DEFAULT 0,
            options TEXT, -- JSON array para select
            placeholder TEXT,
            default_value TEXT,
            validation_rules TEXT, -- JSON object
            field_order INTEGER DEFAULT 0,
            active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabla de configuración general
    conn.execute('''
        CREATE TABLE IF NOT EXISTS general_config (
            id INTEGER PRIMARY KEY,
            key TEXT UNIQUE NOT NULL,
            value TEXT,
            description TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def get_ai_config_from_db():
    """Obtener configuración AI desde BD"""
    try:
        conn = get_db_connection()
        config = conn.execute(
            'SELECT * FROM ai_config WHERE enabled = 1 ORDER BY updated_at DESC LIMIT 1'
        ).fetchone()
        conn.close()
        
        if config:
            return {
                'id': config['id'],
                'provider': config['provider'],
                'api_key': config['api_key'] if config['api_key'] else '',
                'model': config['model'],
                'base_url': config['base_url'],
                'max_tokens': config['max_tokens'],
                'temperature': config['temperature'],
                'enabled': bool(config['enabled'])
            }
        else:
            return {}
    except Exception as e:
        logger.error(f"Error getting AI config: {str(e)}")
        return {}

def save_ai_config_to_db(ai_config: AIConfig):
    """Guardar configuración AI en BD"""
    conn = get_db_connection()
    
    # Desactivar configuraciones anteriores
    conn.execute('UPDATE ai_config SET enabled = 0')
    
    # Insertar nueva configuración
    conn.execute('''
        INSERT INTO ai_config 
        (provider, api_key, model, base_url, max_tokens, temperature, enabled)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        ai_config.provider,
        ai_config.api_key,
        ai_config.model,
        ai_config.base_url,
        ai_config.max_tokens,
        ai_config.temperature,
        ai_config.enabled
    ))
    
    conn.commit()
    conn.close()

def get_client_dynamic_fields():
    """Obtener campos dinámicos de clientes"""
    try:
        conn = get_db_connection()
        fields = conn.execute(
            'SELECT * FROM client_dynamic_fields WHERE active = 1 ORDER BY field_order, id'
        ).fetchall()
        conn.close()
        
        result = []
        for field in fields:
            result.append({
                'id': field['id'],
                'name': field['name'],
                'label': field['label'],
                'type': field['type'],
                'required': bool(field['required']),
                'options': json.loads(field['options']) if field['options'] else [],
                'placeholder': field['placeholder'],
                'default_value': field['default_value'],
                'validation_rules': json.loads(field['validation_rules']) if field['validation_rules'] else {},
                'order': field['field_order']
            })
        
        return result
    except Exception as e:
        logger.error(f"Error getting dynamic fields: {str(e)}")
        return []

def save_dynamic_field(field_data):
    """Guardar nuevo campo dinámico"""
    conn = get_db_connection()
    
    cursor = conn.execute('''
        INSERT INTO client_dynamic_fields 
        (name, label, type, required, options, placeholder, default_value, validation_rules, field_order)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        field_data['name'],
        field_data['label'],
        field_data['type'],
        field_data['required'],
        json.dumps(field_data['options']) if field_data['options'] else None,
        field_data['placeholder'],
        field_data['default_value'],
        json.dumps(field_data['validation_rules']) if field_data['validation_rules'] else None,
        field_data['order']
    ))
    
    field_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return field_id

def update_dynamic_field(field_id, field_data):
    """Actualizar campo dinámico"""
    conn = get_db_connection()
    
    cursor = conn.execute('''
        UPDATE client_dynamic_fields 
        SET label = ?, type = ?, required = ?, options = ?, placeholder = ?, 
            default_value = ?, validation_rules = ?, field_order = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (
        field_data.get('label'),
        field_data.get('type'),
        field_data.get('required'),
        json.dumps(field_data.get('options', [])) if field_data.get('options') else None,
        field_data.get('placeholder', ''),
        field_data.get('default_value', ''),
        json.dumps(field_data.get('validation_rules', {})) if field_data.get('validation_rules') else None,
        field_data.get('order', 0),
        field_id
    ))
    
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    
    return affected > 0

def delete_dynamic_field(field_id):
    """Eliminar campo dinámico (soft delete)"""
    conn = get_db_connection()
    
    cursor = conn.execute(
        'UPDATE client_dynamic_fields SET active = 0 WHERE id = ?',
        (field_id,)
    )
    
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    
    return affected > 0

def get_general_config():
    """Obtener configuración general"""
    # Placeholder - implementar según necesidades
    return {
        'company_name': 'Mi Empresa ERP',
        'timezone': 'America/Guayaquil',
        'language': 'es',
        'currency': 'USD'
    }

def get_users_config():
    """Obtener configuración de usuarios"""
    # Placeholder - implementar según necesidades
    return [
        {'id': 1, 'username': 'admin', 'email': 'admin@empresa.com', 'role': 'Administrator'},
        {'id': 2, 'username': 'user', 'email': 'user@empresa.com', 'role': 'User'}
    ]

def get_document_templates():
    """Obtener plantillas de documentos"""
    # Placeholder - implementar según necesidades
    return [
        {'id': 1, 'name': 'Factura Estándar', 'type': 'invoice', 'active': True},
        {'id': 2, 'name': 'Cotización', 'type': 'quote', 'active': True}
    ]

def get_billing_config():
    """Obtener configuración de facturación"""
    # Placeholder - implementar según necesidades
    return {
        'tax_rate': 12.0,
        'invoice_prefix': 'INV-',
        'invoice_sequence': 1001,
        'payment_terms': '30 días'
    }

# Inicializar tablas al importar el módulo
init_config_tables()

# Error handlers específicos del módulo
@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('configuracion/error.html', 
                         error_code=404,
                         error_message="Página de configuración no encontrada"), 404

@blueprint.errorhandler(500)
def internal_error(error):
    logger.error(f"Error interno en configuración: {str(error)}")
    return render_template('configuracion/error.html',
                         error_code=500, 
                         error_message="Error interno del servidor"), 500
