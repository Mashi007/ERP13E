"""
📁 Ruta: /app/modules/configuracion/models.py
📄 Nombre: models.py
🏗️ Propósito: Modelos de datos para configuración
⚡ Performance: Clases optimizadas para manejo de datos
🔒 Seguridad: Validación de datos y tipos seguros

ERP13 Enterprise - Modelos de Configuración
Estructuras de datos para AI, campos dinámicos y configuraciones
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
import json

class FieldType(Enum):
    """Tipos de campos dinámicos disponibles"""
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    EMAIL = "email"
    SELECT = "select"
    CHECKBOX = "checkbox"
    TEXTAREA = "textarea"

class AIProvider(Enum):
    """Proveedores de AI soportados"""
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    CLAUDE = "claude"
    OLLAMA = "ollama"
    GENERIC_OPENAI = "generic_openai"

@dataclass
class DynamicField:
    """Modelo para campos dinámicos de clientes"""
    id: Optional[int] = None
    name: str = ""
    label: str = ""
    type: FieldType = FieldType.TEXT
    required: bool = False
    options: List[str] = field(default_factory=list)
    placeholder: str = ""
    default_value: str = ""
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    order: int = 0
    active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validación post-inicialización"""
        if isinstance(self.type, str):
            self.type = FieldType(self.type)
        
        # Validar que campos select tengan opciones
        if self.type == FieldType.SELECT and not self.options:
            raise ValueError("Campo tipo SELECT requiere opciones")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'name': self.name,
            'label': self.label,
            'type': self.type.value,
            'required': self.required,
            'options': self.options,
            'placeholder': self.placeholder,
            'default_value': self.default_value,
            'validation_rules': self.validation_rules,
            'order': self.order,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DynamicField':
        """Crear desde diccionario"""
        # Convertir fechas
        created_at = None
        updated_at = None
        
        if data.get('created_at'):
            created_at = datetime.fromisoformat(data['created_at'])
        if data.get('updated_at'):
            updated_at = datetime.fromisoformat(data['updated_at'])
        
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            label=data.get('label', ''),
            type=FieldType(data.get('type', 'text')),
            required=bool(data.get('required', False)),
            options=data.get('options', []),
            placeholder=data.get('placeholder', ''),
            default_value=data.get('default_value', ''),
            validation_rules=data.get('validation_rules', {}),
            order=int(data.get('order', 0)),
            active=bool(data.get('active', True)),
            created_at=created_at,
            updated_at=updated_at
        )
    
    def validate_value(self, value: Any) -> Dict[str, Any]:
        """Validar un valor contra este campo"""
        errors = []
        
        # Verificar campo requerido
        if self.required and not value:
            errors.append(f"El campo '{self.label}' es requerido")
        
        if not value and not self.required:
            return {'valid': True, 'errors': []}
        
        # Validación por tipo
        if self.type == FieldType.EMAIL:
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, str(value)):
                errors.append("Formato de email inválido")
        
        elif self.type == FieldType.NUMBER:
            try:
                float(value)
            except (ValueError, TypeError):
                errors.append("Debe ser un número válido")
        
        elif self.type == FieldType.DATE:
            try:
                datetime.strptime(str(value), '%Y-%m-%d')
            except ValueError:
                errors.append("Formato de fecha inválido (YYYY-MM-DD)")
        
        elif self.type == FieldType.SELECT:
            if str(value) not in self.options:
                errors.append(f"Valor debe ser uno de: {', '.join(self.options)}")
        
        elif self.type == FieldType.CHECKBOX:
            if str(value).lower() not in ['true', 'false', '1', '0', 'on', 'off']:
                errors.append("Valor debe ser verdadero o falso")
        
        # Validaciones adicionales
        if self.validation_rules:
            if 'min_length' in self.validation_rules:
                if len(str(value)) < self.validation_rules['min_length']:
                    errors.append(f"Mínimo {self.validation_rules['min_length']} caracteres")
            
            if 'max_length' in self.validation_rules:
                if len(str(value)) > self.validation_rules['max_length']:
                    errors.append(f"Máximo {self.validation_rules['max_length']} caracteres")
            
            if 'pattern' in self.validation_rules:
                import re
                if not re.match(self.validation_rules['pattern'], str(value)):
                    errors.append(f"Formato inválido")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

@dataclass
class AIConfiguration:
    """Modelo para configuración de AI"""
    id: Optional[int] = None
    provider: AIProvider = AIProvider.OPENAI
    api_key: str = ""
    model: str = ""
    base_url: Optional[str] = None
    max_tokens: int = 4000
    temperature: float = 0.7
    enabled: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validación post-inicialización"""
        if isinstance(self.provider, str):
            self.provider = AIProvider(self.provider)
        
        # Validar temperatura
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("Temperature debe estar entre 0.0 y 2.0")
        
        # Validar max_tokens
        if self.max_tokens < 1 or self.max_tokens > 32000:
            raise ValueError("Max tokens debe estar entre 1 y 32000")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'provider': self.provider.value,
            'api_key': self.api_key,
            'model': self.model,
            'base_url': self.base_url,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'enabled': self.enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AIConfiguration':
        """Crear desde diccionario"""
        # Convertir fechas
        created_at = None
        updated_at = None
        
        if data.get('created_at'):
            created_at = datetime.fromisoformat(data['created_at'])
        if data.get('updated_at'):
            updated_at = datetime.fromisoformat(data['updated_at'])
        
        return cls(
            id=data.get('id'),
            provider=AIProvider(data.get('provider', 'openai')),
            api_key=data.get('api_key', ''),
            model=data.get('model', ''),
            base_url=data.get('base_url'),
            max_tokens=int(data.get('max_tokens', 4000)),
            temperature=float(data.get('temperature', 0.7)),
            enabled=bool(data.get('enabled', True)),
            created_at=created_at,
            updated_at=updated_at
        )
    
    def validate(self) -> Dict[str, Any]:
        """Validar configuración AI"""
        errors = []
        
        # Validar campos requeridos
        if not self.model:
            errors.append("Modelo es requerido")
        
        # Validar API key para proveedores que lo requieren
        if self.provider != AIProvider.OLLAMA and not self.api_key:
            errors.append(f"API Key es requerido para {self.provider.value}")
        
        # Validar URL base para proveedores genéricos
        if self.provider == AIProvider.GENERIC_OPENAI and not self.base_url:
            errors.append("URL base es requerida para proveedor genérico")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def get_display_name(self) -> str:
        """Obtener nombre para mostrar"""
        provider_names = {
            AIProvider.OPENAI: "OpenAI",
            AIProvider.DEEPSEEK: "DeepSeek",
            AIProvider.CLAUDE: "Anthropic Claude",
            AIProvider.OLLAMA: "Ollama (Local)",
            AIProvider.GENERIC_OPENAI: "Proveedor Personalizado"
        }
        return provider_names.get(self.provider, self.provider.value)

@dataclass
class FormSchema:
    """Esquema de formulario dinámico"""
    fields: List[DynamicField] = field(default_factory=list)
    base_fields_count: int = 0
    dynamic_fields_count: int = 0
    
    def add_field(self, dynamic_field: DynamicField):
        """Agregar campo al esquema"""
        self.fields.append(dynamic_field)
        self.dynamic_fields_count += 1
    
    def get_field_by_name(self, name: str) -> Optional[DynamicField]:
        """Obtener campo por nombre"""
        for field in self.fields:
            if field.name == name:
                return field
        return None
    
    def validate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validar datos contra el esquema"""
        errors = []
        validated_data = {}
        
        for field in self.fields:
            field_value = data.get(field.name, '')
            
            validation_result = field.validate_value(field_value)
            
            if not validation_result['valid']:
                errors.extend([f"{field.label}: {error}" for error in validation_result['errors']])
            else:
                validated_data[field.name] = field_value
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'data': validated_data if len(errors) == 0 else {}
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir esquema a diccionario"""
        return {
            'fields': [field.to_dict() for field in self.fields],
            'total_fields': len(self.fields),
            'base_fields_count': self.base_fields_count,
            'dynamic_fields_count': self.dynamic_fields_count
        }

@dataclass
class SystemConfiguration:
    """Configuración general del sistema"""
    id: Optional[int] = None
    company_name: str = ""
    company_nif: str = ""
    company_address: str = ""
    company_phone: str = ""
    company_email: str = ""
    timezone: str = "UTC"
    language: str = "es"
    currency: str = "USD"
    date_format: str = "%Y-%m-%d"
    time_format: str = "%H:%M:%S"
    logo_url: Optional[str] = None
    theme: str = "default"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        return {
            'id': self.id,
            'company_name': self.company_name,
            'company_nif': self.company_nif,
            'company_address': self.company_address,
            'company_phone': self.company_phone,
            'company_email': self.company_email,
            'timezone': self.timezone,
            'language': self.language,
            'currency': self.currency,
            'date_format': self.date_format,
            'time_format': self.time_format,
            'logo_url': self.logo_url,
            'theme': self.theme
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SystemConfiguration':
        """Crear desde diccionario"""
        return cls(
            id=data.get('id'),
            company_name=data.get('company_name', ''),
            company_nif=data.get('company_nif', ''),
            company_address=data.get('company_address', ''),
            company_phone=data.get('company_phone', ''),
            company_email=data.get('company_email', ''),
            timezone=data.get('timezone', 'UTC'),
            language=data.get('language', 'es'),
            currency=data.get('currency', 'USD'),
            date_format=data.get('date_format', '%Y-%m-%d'),
            time_format=data.get('time_format', '%H:%M:%S'),
            logo_url=data.get('logo_url'),
            theme=data.get('theme', 'default')
        )

# Funciones de utilidad para trabajar con los modelos

def create_base_client_fields() -> List[DynamicField]:
    """Crear campos base para clientes"""
    return [
        DynamicField(
            name="nombre_empresa",
            label="Nombre de la Empresa",
            type=FieldType.TEXT,
            required=True,
            order=0
        ),
        DynamicField(
            name="nombre_emails",
            label="Nombre para Emails",
            type=FieldType.TEXT,
            required=False,
            order=1
        ),
        DynamicField(
            name="nif_cif",
            label="NIF/CIF",
            type=FieldType.TEXT,
            required=False,
            order=2
        ),
        DynamicField(
            name="emails",
            label="Email",
            type=FieldType.EMAIL,
            required=False,
            order=3
        ),
        DynamicField(
            name="telefonos",
            label="Teléfonos",
            type=FieldType.TEXT,
            required=False,
            order=4
        ),
        DynamicField(
            name="sector",
            label="Sector",
            type=FieldType.SELECT,
            required=False,
            options=["Tecnología", "Servicios", "Manufactura", "Comercio", "Otros"],
            order=5
        ),
        DynamicField(
            name="estado",
            label="Estado",
            type=FieldType.SELECT,
            required=False,
            options=["Activo", "Inactivo", "Prospecto"],
            default_value="Activo",
            order=6
        ),
        DynamicField(
            name="direccion",
            label="Dirección",
            type=FieldType.TEXTAREA,
            required=False,
            order=7
        ),
        DynamicField(
            name="etiquetas",
            label="Etiquetas",
            type=FieldType.TEXT,
            required=False,
            placeholder="Separar con comas",
            order=8
        ),
        DynamicField(
            name="notas",
            label="Notas",
            type=FieldType.TEXTAREA,
            required=False,
            order=9
        )
    ]

def get_default_ai_models() -> Dict[str, List[str]]:
    """Obtener modelos AI por defecto para cada proveedor"""
    return {
        AIProvider.OPENAI.value: [
            "gpt-4", 
            "gpt-4-turbo", 
            "gpt-3.5-turbo", 
            "gpt-3.5-turbo-16k"
        ],
        AIProvider.DEEPSEEK.value: [
            "deepseek-chat", 
            "deepseek-coder"
        ],
        AIProvider.CLAUDE.value: [
            "claude-3-sonnet-20240229", 
            "claude-3-haiku-20240307", 
            "claude-3-opus-20240229"
        ],
        AIProvider.OLLAMA.value: [
            "llama2", 
            "mistral", 
            "codellama", 
            "neural-chat"
        ],
        AIProvider.GENERIC_OPENAI.value: [
            "Configurar manualmente"
        ]
    }
