"""
📁 Ruta: /app/core/ai_service.py
📄 Nombre: ai_service.py
🏗️ Propósito: Servicio AI unificado multi-proveedor
⚡ Performance: Adaptadores optimizados por proveedor
🔒 Seguridad: Manejo seguro de tokens.

ERP13 Enterprise - Core AI Service
Soporte para múltiples proveedores AI configurables
"""

import requests
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

@dataclass
class AIConfig:
    """Configuración AI del sistema"""
    provider: str  # openai, deepseek, claude, ollama, etc.
    api_key: str
    model: str
    base_url: Optional[str] = None
    max_tokens: int = 4000
    temperature: float = 0.7
    enabled: bool = True

@dataclass 
class AIResponse:
    """Respuesta estandarizada del AI"""
    content: str
    provider: str
    model: str
    tokens_used: Optional[int] = None
    cost_estimate: Optional[float] = None
    success: bool = True
    error: Optional[str] = None

class AIProviderAdapter(ABC):
    """Adaptador base para proveedores AI"""
    
    @abstractmethod
    def chat_completion(self, messages: List[Dict], config: AIConfig) -> AIResponse:
        """Método base para completar chat"""
        pass
    
    @abstractmethod  
    def validate_config(self, config: AIConfig) -> bool:
        """Validar configuración del proveedor"""
        pass

class OpenAIAdapter(AIProviderAdapter):
    """Adaptador para OpenAI (GPT-4, GPT-3.5)"""
    
    def chat_completion(self, messages: List[Dict], config: AIConfig) -> AIResponse:
        try:
            headers = {
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": config.model,
                "messages": messages,
                "max_tokens": config.max_tokens,
                "temperature": config.temperature
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return AIResponse(
                    content=data['choices'][0]['message']['content'],
                    provider="openai",
                    model=config.model,
                    tokens_used=data.get('usage', {}).get('total_tokens'),
                    success=True
                )
            else:
                return AIResponse(
                    content="",
                    provider="openai", 
                    model=config.model,
                    success=False,
                    error=f"API Error: {response.status_code}"
                )
                
        except Exception as e:
            logger.error(f"OpenAI API Error: {str(e)}")
            return AIResponse(
                content="",
                provider="openai",
                model=config.model, 
                success=False,
                error=str(e)
            )
    
    def validate_config(self, config: AIConfig) -> bool:
        return bool(config.api_key and config.model)

class DeepSeekAdapter(AIProviderAdapter):
    """Adaptador para DeepSeek"""
    
    def chat_completion(self, messages: List[Dict], config: AIConfig) -> AIResponse:
        try:
            headers = {
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": config.model,
                "messages": messages,
                "max_tokens": config.max_tokens,
                "temperature": config.temperature
            }
            
            base_url = config.base_url or "https://api.deepseek.com/v1/chat/completions"
            
            response = requests.post(
                base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return AIResponse(
                    content=data['choices'][0]['message']['content'],
                    provider="deepseek",
                    model=config.model,
                    tokens_used=data.get('usage', {}).get('total_tokens'),
                    success=True
                )
            else:
                return AIResponse(
                    content="",
                    provider="deepseek",
                    model=config.model,
                    success=False,
                    error=f"API Error: {response.status_code}"
                )
                
        except Exception as e:
            logger.error(f"DeepSeek API Error: {str(e)}")
            return AIResponse(
                content="",
                provider="deepseek",
                model=config.model,
                success=False,
                error=str(e)
            )
    
    def validate_config(self, config: AIConfig) -> bool:
        return bool(config.api_key and config.model)

class ClaudeAdapter(AIProviderAdapter):
    """Adaptador para Anthropic Claude"""
    
    def chat_completion(self, messages: List[Dict], config: AIConfig) -> AIResponse:
        try:
            headers = {
                "x-api-key": config.api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            # Claude usa formato diferente - convertir messages
            system_message = ""
            user_messages = []
            
            for msg in messages:
                if msg['role'] == 'system':
                    system_message = msg['content']
                elif msg['role'] == 'user':
                    user_messages.append({"role": "human", "content": msg['content']})
                elif msg['role'] == 'assistant':
                    user_messages.append({"role": "assistant", "content": msg['content']})
            
            payload = {
                "model": config.model,
                "max_tokens": config.max_tokens,
                "temperature": config.temperature,
                "messages": user_messages
            }
            
            if system_message:
                payload["system"] = system_message
            
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return AIResponse(
                    content=data['content'][0]['text'],
                    provider="claude",
                    model=config.model,
                    tokens_used=data.get('usage', {}).get('input_tokens', 0) + data.get('usage', {}).get('output_tokens', 0),
                    success=True
                )
            else:
                return AIResponse(
                    content="",
                    provider="claude",
                    model=config.model,
                    success=False,
                    error=f"API Error: {response.status_code}"
                )
                
        except Exception as e:
            logger.error(f"Claude API Error: {str(e)}")
            return AIResponse(
                content="",
                provider="claude",
                model=config.model,
                success=False,
                error=str(e)
            )
    
    def validate_config(self, config: AIConfig) -> bool:
        return bool(config.api_key and config.model)

class OllamaAdapter(AIProviderAdapter):
    """Adaptador para Ollama (AI local)"""
    
    def chat_completion(self, messages: List[Dict], config: AIConfig) -> AIResponse:
        try:
            base_url = config.base_url or "http://localhost:11434"
            
            payload = {
                "model": config.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": config.temperature
                }
            }
            
            response = requests.post(
                f"{base_url}/api/chat",
                json=payload,
                timeout=60  # Ollama puede ser más lento
            )
            
            if response.status_code == 200:
                data = response.json()
                return AIResponse(
                    content=data['message']['content'],
                    provider="ollama",
                    model=config.model,
                    success=True
                )
            else:
                return AIResponse(
                    content="",
                    provider="ollama",
                    model=config.model,
                    success=False,
                    error=f"API Error: {response.status_code}"
                )
                
        except Exception as e:
            logger.error(f"Ollama API Error: {str(e)}")
            return AIResponse(
                content="",
                provider="ollama",
                model=config.model,
                success=False,
                error=str(e)
            )
    
    def validate_config(self, config: AIConfig) -> bool:
        return bool(config.model)  # Ollama no necesita API key

class GenericOpenAIAdapter(AIProviderAdapter):
    """Adaptador genérico para APIs compatibles con OpenAI"""
    
    def chat_completion(self, messages: List[Dict], config: AIConfig) -> AIResponse:
        try:
            headers = {
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": config.model,
                "messages": messages,
                "max_tokens": config.max_tokens,
                "temperature": config.temperature
            }
            
            base_url = config.base_url or "https://api.openai.com"
            endpoint = f"{base_url}/v1/chat/completions"
            
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return AIResponse(
                    content=data['choices'][0]['message']['content'],
                    provider="generic_openai",
                    model=config.model,
                    tokens_used=data.get('usage', {}).get('total_tokens'),
                    success=True
                )
            else:
                return AIResponse(
                    content="",
                    provider="generic_openai",
                    model=config.model,
                    success=False,
                    error=f"API Error: {response.status_code}"
                )
                
        except Exception as e:
            logger.error(f"Generic OpenAI API Error: {str(e)}")
            return AIResponse(
                content="",
                provider="generic_openai",
                model=config.model,
                success=False,
                error=str(e)
            )
    
    def validate_config(self, config: AIConfig) -> bool:
        return bool(config.api_key and config.model and config.base_url)

class AIService:
    """Servicio AI unificado del ERP"""
    
    def __init__(self):
        self.adapters = {
            "openai": OpenAIAdapter(),
            "deepseek": DeepSeekAdapter(), 
            "claude": ClaudeAdapter(),
            "ollama": OllamaAdapter(),
            "generic_openai": GenericOpenAIAdapter()
        }
        self.current_config: Optional[AIConfig] = None
    
    def set_config(self, config: AIConfig) -> bool:
        """Establecer configuración AI activa"""
        if not config.enabled:
            self.current_config = None
            return True
            
        adapter = self.adapters.get(config.provider)
        if not adapter:
            logger.error(f"Proveedor AI no soportado: {config.provider}")
            return False
            
        if not adapter.validate_config(config):
            logger.error(f"Configuración AI inválida para {config.provider}")
            return False
            
        self.current_config = config
        logger.info(f"Configuración AI establecida: {config.provider} - {config.model}")
        return True
    
    def is_enabled(self) -> bool:
        """Verificar si AI está habilitado y configurado"""
        return self.current_config is not None and self.current_config.enabled
    
    def chat(self, messages: List[Dict[str, str]]) -> AIResponse:
        """Enviar mensajes al AI configurado"""
        if not self.is_enabled():
            return AIResponse(
                content="",
                provider="none",
                model="none", 
                success=False,
                error="AI no está configurado o habilitado"
            )
        
        adapter = self.adapters.get(self.current_config.provider)
        if not adapter:
            return AIResponse(
                content="",
                provider=self.current_config.provider,
                model=self.current_config.model,
                success=False,
                error="Adaptador AI no encontrado"
            )
        
        return adapter.chat_completion(messages, self.current_config)
    
    def get_available_providers(self) -> List[str]:
        """Obtener lista de proveedores AI disponibles"""
        return list(self.adapters.keys())
    
    def get_provider_models(self, provider: str) -> List[str]:
        """Obtener modelos disponibles por proveedor"""
        models_by_provider = {
            "openai": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"],
            "deepseek": ["deepseek-chat", "deepseek-coder"],
            "claude": ["claude-3-sonnet-20240229", "claude-3-haiku-20240307", "claude-3-opus-20240229"],
            "ollama": ["llama2", "mistral", "codellama", "neural-chat"],
            "generic_openai": ["Configurar manualmente"]
        }
        
        return models_by_provider.get(provider, [])

# Instancia global del servicio AI
ai_service = AIService()

def get_ai_service() -> AIService:
    """Obtener instancia global del servicio AI"""
    return ai_service

# Funciones de utilidad para usar en otras partes del ERP

def ask_ai(question: str, context: str = "") -> AIResponse:
    """Función simple para hacer consultas AI"""
    messages = []
    
    if context:
        messages.append({
            "role": "system",
            "content": f"Eres un asistente AI del ERP. Contexto: {context}"
        })
    
    messages.append({
        "role": "user", 
        "content": question
    })
    
    return ai_service.chat(messages)

def ask_ai_about_client(client_id: str, question: str, client_data: Dict[str, Any]) -> AIResponse:
    """Función específica para consultas sobre clientes"""
    context = f"""
    Datos del cliente ID {client_id}:
    {json.dumps(client_data, indent=2)}
    
    Responde preguntas sobre este cliente basándote en los datos proporcionados.
    Sé específico y menciona datos concretos cuando sea relevante.
    """
    
    return ask_ai(question, context)
