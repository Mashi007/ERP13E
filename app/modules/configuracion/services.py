"""
📁 Ruta: /app/modules/configuracion/services.py
📄 Nombre: services.py
🏗️ Propósito: Servicios de configuración - Lógica de negocio
⚡ Performance: Operaciones optimizadas de BD y validación
🔒 Seguridad: Validación de datos y configuraciones

ERP13 Enterprise - Servicios de Configuración
Manejo de AI, campos dinámicos y configuraciones del sistema
"""

import json
import sqlite3
from typing import Dict, List, Any, Optional
from dataclasses import asdict
import logging
from datetime import datetime

from app.core.ai_service import get_ai_service, AIConfig

logger = logging.getLogger(__name__)

class ConfigurationService:
    """Servicio principal de configuración del ERP"""
    
    def __init__(self):
        self.db_path = 'erp_database.db'
    
    def get_db_connection(self):
        """Obtener conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    # ==========================================================================
    # GESTIÓN DE CONFIGURACIÓN AI
    # ==========================================================================
    
    def save_ai_configuration(self, config_data: Dict[str, Any]) -> bool:
        """Guardar configuración AI y aplicarla al sistema"""
        try:
            # Crear objeto AIConfig
            ai_config = AIConfig(
                provider=config_data['provider'],
                api_key=config_data.get('api_key', ''),
                model=config_data['model'],
                base_url=config_data.get('base_url'),
                max_tokens=int(config_data.get('max_tokens', 4000)),
                temperature=float(config_data.get('temperature', 0.7)),
                enabled=bool(config_data.get('enabled', True))
            )
            
            # Validar configuración con el servicio AI
            ai_service = get_ai_service()
            if not ai_service.set_config(ai_config):
                logger.error("Configuración AI inválida")
                return False
            
            # Guardar en base de datos
            self._save_ai_config_db(ai_config)
            
            logger.info(f"Configuración AI guardada: {ai_config.provider} - {ai_config.model}")
            return True
            
        except Exception as e:
            logger.error(f"Error guardando configuración AI: {str(e)}")
            return False
    
    def load_ai_configuration(self) -> Optional[Dict[str, Any]]:
        """Cargar configuración AI activa y aplicarla al sistema"""
        try:
            conn = self.get_db_connection()
            config_row = conn.execute(
                'SELECT * FROM ai_config WHERE enabled = 1 ORDER BY updated_at DESC LIMIT 1'
            ).fetchone()
            conn.close()
            
            if not config_row:
                return None
            
            config_data = {
                'id': config_row['id'],
                'provider': config_row['provider'],
                'api_key': config_row['api_key'] or '',
                'model': config_row['model'],
                'base_url': config_row['base_url'],
                'max_tokens': config_row['max_tokens'],
                'temperature': config_row['temperature'],
                'enabled': bool(config_row['enabled'])
            }
            
            # Aplicar configuración al servicio AI
            ai_config = AIConfig(
                provider=config_data['provider'],
                api_key=config_data['api_key'],
                model=config_data['model'],
                base_url=config_data['base_url'],
                max_tokens=config_data['max_tokens'],
                temperature=config_data['temperature'],
                enabled=config_data['enabled']
            )
            
            ai_service = get_ai_service()
            ai_service.set_config(ai_config)
            
            return config_data
            
        except Exception as e:
            logger.error(f"Error cargando configuración AI: {str(e)}")
            return None
    
    def test_ai_connection(self) -> Dict[str, Any]:
        """Probar conexión con el proveedor AI configurado"""
        try:
            ai_service = get_ai_service()
            
            if not ai_service.is_enabled():
                return {
                    'success': False,
                    'error': 'AI no está configurado o habilitado'
                }
            
            # Mensaje de prueba específico
            test_message = """Eres un asistente AI del sistema ERP. 
            Responde brevemente (máximo 50 palabras) confirmando que:
            1. Recibes este mensaje correctamente
            2. Estás listo para ayudar con consultas del ERP
            3. Menciona tu modelo/proveedor"""
            
            response = ai_service.chat([{
                'role': 'user',
                'content': test_message
            }])
            
            if response.success:
                return {
                    'success': True,
                    'message': 'Conexión AI exitosa',
                    'ai_response': response.content,
                    'provider': response.provider,
                    'model': response.model,
                    'tokens_used': response.tokens_used
                }
            else:
                return {
                    'success': False,
                    'error': f'Error en respuesta AI: {response.error}'
                }
                
        except Exception as e:
            logger.error(f"Error probando conexión AI: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _save_ai_config_db(self, ai_config: AIConfig):
        """Guardar configuración AI en base de datos"""
        conn = self.get_db_connection()
        
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
    
    # ==========================================================================
    # GESTIÓN DE CAMPOS DINÁMICOS
    # ==========================================================================
    
    def get_client_dynamic_fields(self) -> List[Dict[str, Any]]:
        """Obtener todos los campos dinámicos activos para clientes"""
        try:
            conn = self.get_db_connection()
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
                    'placeholder': field['placeholder'] or '',
                    'default_value': field['default_value'] or '',
                    'validation_rules': json.loads(field['validation_rules']) if field['validation_rules'] else {},
                    'order': field['field_order']
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error obteniendo campos dinámicos: {str(e)}")
            return []
    
    def create_dynamic_field(self, field_data: Dict[str, Any]) -> Optional[int]:
        """Crear nuevo campo dinámico"""
        try:
            # Validar datos requeridos
            if not self._validate_field_data(field_data):
                return None
            
            conn = self.get_db_connection()
            
            cursor = conn.execute('''
                INSERT INTO client_dynamic_fields 
                (name, label, type, required, options, placeholder, default_value, validation_rules, field_order)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                field_data['name'],
                field_data['label'],
                field_data['type'],
                field_data.get('required', False),
                json.dumps(field_data.get('options', [])) if field_data.get('options') else None,
                field_data.get('placeholder', ''),
                field_data.get('default_value', ''),
                json.dumps(field_data.get('validation_rules', {})) if field_data.get('validation_rules') else None,
                field_data.get('order', 0)
            ))
            
            field_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Campo dinámico creado: {field_data['name']} (ID: {field_id})")
            return field_id
            
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                logger.error(f"Campo con nombre '{field_data['name']}' ya existe")
            return None
        except Exception as e:
            logger.error(f"Error creando campo dinámico: {str(e)}")
            return None
    
    def update_dynamic_field(self, field_id: int, field_data: Dict[str, Any]) -> bool:
        """Actualizar campo dinámico existente"""
        try:
            conn = self.get_db_connection()
            
            # Construir query dinámicamente para actualizar solo campos proporcionados
            update_fields = []
            values = []
            
            allowed_fields = ['label', 'type', 'required', 'options', 'placeholder', 
                            'default_value', 'validation_rules', 'field_order']
            
            for field, value in field_data.items():
                if field in allowed_fields:
                    if field == 'options' and value:
                        update_fields.append(f"{field} = ?")
                        values.append(json.dumps(value))
                    elif field == 'validation_rules' and value:
                        update_fields.append(f"{field} = ?")
                        values.append(json.dumps(value))
                    else:
                        update_fields.append(f"{field} = ?")
                        values.append(value)
            
            if not update_fields:
                return False
            
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            values.append(field_id)
            
            query = f"UPDATE client_dynamic_fields SET {', '.join(update_fields)} WHERE id = ?"
            cursor = conn.execute(query, values)
            
            affected = cursor.rowcount
            conn.commit()
            conn.close()
            
            if affected > 0:
                logger.info(f"Campo dinámico actualizado: ID {field_id}")
                return True
            else:
                logger.warning(f"Campo dinámico no encontrado: ID {field_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error actualizando campo dinámico: {str(e)}")
            return False
    
    def delete_dynamic_field(self, field_id: int) -> bool:
        """Eliminar campo dinámico (soft delete)"""
        try:
            conn = self.get_db_connection()
            
            cursor = conn.execute(
                'UPDATE client_dynamic_fields SET active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                (field_id,)
            )
            
            affected = cursor.rowcount
            conn.commit()
            conn.close()
            
            if affected > 0:
                logger.info(f"Campo dinámico eliminado: ID {field_id}")
                return True
            else:
                logger.warning(f"Campo dinámico no encontrado: ID {field_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error eliminando campo dinámico: {str(e)}")
            return False
    
    def reorder_dynamic_fields(self, field_orders: List[Dict[str, int]]) -> bool:
        """Reordenar campos dinámicos"""
        try:
            conn = self.get_db_connection()
            
            for item in field_orders:
                conn.execute(
                    'UPDATE client_dynamic_fields SET field_order = ? WHERE id = ?',
                    (item['order'], item['id'])
                )
            
            conn.commit()
            conn.close()
            
            logger.info(f"Reordenados {len(field_orders)} campos dinámicos")
            return True
            
        except Exception as e:
            logger.error(f"Error reordenando campos dinámicos: {str(e)}")
            return False
    
    def _validate_field_data(self, field_data: Dict[str, Any]) -> bool:
        """Validar datos de campo dinámico"""
        required_fields = ['name', 'label', 'type']
        
        for field in required_fields:
            if field not in field_data or not field_data[field]:
                logger.error(f"Campo requerido faltante: {field}")
                return False
        
        # Validar tipo de campo
        valid_types = ['text', 'number', 'date', 'email', 'select', 'checkbox', 'textarea']
        if field_data['type'] not in valid_types:
            logger.error(f"Tipo de campo inválido: {field_data['type']}")
            return False
        
        # Validar opciones para campos select
        if field_data['type'] == 'select':
            options = field_data.get('options', [])
            if not options or not isinstance(options, list):
                logger.error("Campo tipo 'select' requiere opciones válidas")
                return False
        
        return True
    
    # ==========================================================================
    # GENERACIÓN DE FORMULARIOS DINÁMICOS
    # ==========================================================================
    
    def generate_client_form_schema(self) -> Dict[str, Any]:
        """Generar esquema de formulario para clientes con campos dinámicos"""
        try:
            # Campos base del cliente
            base_fields = [
                {
                    'name': 'nombre_empresa',
                    'label': 'Nombre de la Empresa',
                    'type': 'text',
                    'required': True,
                    'order': 0
                },
                {
                    'name': 'nombre_emails',
                    'label': 'Nombre para Emails',
                    'type': 'text',
                    'required': False,
                    'order': 1
                },
                {
                    'name': 'nif_cif',
                    'label': 'NIF/CIF',
                    'type': 'text',
                    'required': False,
                    'order': 2
                }
            ]
            
            # Obtener campos dinámicos
            dynamic_fields = self.get_client_dynamic_fields()
            
            # Combinar todos los campos
            all_fields = base_fields + dynamic_fields
            
            # Ordenar por campo order
            all_fields.sort(key=lambda x: x.get('order', 999))
            
            return {
                'fields': all_fields,
                'total_fields': len(all_fields),
                'dynamic_fields_count': len(dynamic_fields),
                'base_fields_count': len(base_fields)
            }
            
        except Exception as e:
            logger.error(f"Error generando esquema de formulario: {str(e)}")
            return {
                'fields': [],
                'total_fields': 0,
                'dynamic_fields_count': 0,
                'base_fields_count': 0
            }
    
    def validate_client_data(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validar datos de cliente contra campos dinámicos"""
        try:
            form_schema = self.generate_client_form_schema()
            errors = []
            validated_data = {}
            
            for field in form_schema['fields']:
                field_name = field['name']
                field_value = client_data.get(field_name, '')
                
                # Validar campos requeridos
                if field.get('required', False) and not field_value:
                    errors.append(f"El campo '{field['label']}' es requerido")
                    continue
                
                # Validar según tipo de campo
                if field_value:
                    validation_result = self._validate_field_value(
                        field_value, field['type'], field.get('validation_rules', {})
                    )
                    
                    if not validation_result['valid']:
                        errors.append(f"El campo '{field['label']}': {validation_result['error']}")
                        continue
                
                validated_data[field_name] = field_value
            
            return {
                'valid': len(errors) == 0,
                'errors': errors,
                'data': validated_data if len(errors) == 0 else {}
            }
            
        except Exception as e:
            logger.error(f"Error validando datos de cliente: {str(e)}")
            return {
                'valid': False,
                'errors': [f"Error en validación: {str(e)}"],
                'data': {}
            }
    
    def _validate_field_value(self, value: Any, field_type: str, validation_rules: Dict[str, Any]) -> Dict[str, Any]:
        """Validar valor individual de campo"""
        try:
            if field_type == 'email':
                import re
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, str(value)):
                    return {'valid': False, 'error': 'Formato de email inválido'}
            
            elif field_type == 'number':
                try:
                    float(value)
                except ValueError:
                    return {'valid': False, 'error': 'Debe ser un número válido'}
            
            elif field_type == 'date':
                try:
                    datetime.strptime(str(value), '%Y-%m-%d')
                except ValueError:
                    return {'valid': False, 'error': 'Formato de fecha inválido (YYYY-MM-DD)'}
            
            # Validar reglas adicionales
            if validation_rules:
                # Longitud mínima
                if 'min_length' in validation_rules:
                    if len(str(value)) < validation_rules['min_length']:
                        return {'valid': False, 'error': f'Mínimo {validation_rules["min_length"]} caracteres'}
                
                # Longitud máxima
                if 'max_length' in validation_rules:
                    if len(str(value)) > validation_rules['max_length']:
                        return {'valid': False, 'error': f'Máximo {validation_rules["max_length"]} caracteres'}
            
            return {'valid': True, 'error': None}
            
        except Exception as e:
            return {'valid': False, 'error': f'Error en validación: {str(e)}'}

# Instancia global del servicio
configuration_service = ConfigurationService()

def get_configuration_service() -> ConfigurationService:
    """Obtener instancia del servicio de configuración"""
    return configuration_service
