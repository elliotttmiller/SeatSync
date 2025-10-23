"""
Universal AI Model Loader for SeatSync
Supports multiple AI providers: OpenAI, Anthropic, Google (Gemini), local models, and more

This module provides a unified interface for loading and using various AI models,
enabling automatic fallback and load balancing across different providers.
"""

import logging
import os
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from datetime import datetime
import asyncio
import httpx

logger = logging.getLogger(__name__)


class AIProvider(Enum):
    """Supported AI providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE_GEMINI = "google_gemini"
    HUGGINGFACE = "huggingface"
    LOCAL = "local"
    OLLAMA = "ollama"


class ModelCapability(Enum):
    """AI model capabilities"""
    TEXT_GENERATION = "text_generation"
    CHAT = "chat"
    EMBEDDINGS = "embeddings"
    CLASSIFICATION = "classification"
    SENTIMENT_ANALYSIS = "sentiment_analysis"


class AIModelConfig:
    """Configuration for an AI model"""
    
    def __init__(
        self,
        provider: AIProvider,
        model_name: str,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        capabilities: List[ModelCapability] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        priority: int = 1
    ):
        self.provider = provider
        self.model_name = model_name
        self.api_key = api_key
        self.endpoint = endpoint
        self.capabilities = capabilities or []
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.priority = priority  # Lower number = higher priority
        self.is_available = False
        self.last_error = None


class UniversalAILoader:
    """
    Universal AI model loader with automatic provider selection and fallback
    """
    
    def __init__(self):
        self.models: Dict[str, AIModelConfig] = {}
        self.default_model: Optional[str] = None
        self._initialize_models()
        
    def _initialize_models(self):
        """Initialize available AI models from environment configuration"""
        
        # OpenAI models
        if os.getenv("OPENAI_API_KEY"):
            self.register_model(AIModelConfig(
                provider=AIProvider.OPENAI,
                model_name="gpt-4",
                api_key=os.getenv("OPENAI_API_KEY"),
                capabilities=[
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.CHAT
                ],
                priority=1
            ))
            self.register_model(AIModelConfig(
                provider=AIProvider.OPENAI,
                model_name="gpt-3.5-turbo",
                api_key=os.getenv("OPENAI_API_KEY"),
                capabilities=[
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.CHAT
                ],
                priority=2
            ))
        
        # Anthropic Claude
        if os.getenv("ANTHROPIC_API_KEY"):
            self.register_model(AIModelConfig(
                provider=AIProvider.ANTHROPIC,
                model_name="claude-3-opus-20240229",
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                capabilities=[
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.CHAT
                ],
                priority=1
            ))
            self.register_model(AIModelConfig(
                provider=AIProvider.ANTHROPIC,
                model_name="claude-3-sonnet-20240229",
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                capabilities=[
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.CHAT
                ],
                priority=2
            ))
        
        # Google Gemini
        if os.getenv("GEMINI_API_KEY"):
            self.register_model(AIModelConfig(
                provider=AIProvider.GOOGLE_GEMINI,
                model_name="gemini-pro",
                api_key=os.getenv("GEMINI_API_KEY"),
                capabilities=[
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.CHAT
                ],
                priority=3
            ))
        
        # Ollama (local models)
        if os.getenv("OLLAMA_ENDPOINT"):
            self.register_model(AIModelConfig(
                provider=AIProvider.OLLAMA,
                model_name=os.getenv("OLLAMA_MODEL", "llama2"),
                endpoint=os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434"),
                capabilities=[
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.CHAT
                ],
                priority=10  # Lower priority for local models
            ))
        
        # HuggingFace models
        if os.getenv("HUGGINGFACE_API_KEY"):
            self.register_model(AIModelConfig(
                provider=AIProvider.HUGGINGFACE,
                model_name=os.getenv("HUGGINGFACE_MODEL", "meta-llama/Llama-2-70b-chat-hf"),
                api_key=os.getenv("HUGGINGFACE_API_KEY"),
                capabilities=[
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.CHAT
                ],
                priority=5
            ))
        
        logger.info(f"Initialized {len(self.models)} AI model configurations")
        
    def register_model(self, config: AIModelConfig):
        """Register a new AI model configuration"""
        model_id = f"{config.provider.value}:{config.model_name}"
        self.models[model_id] = config
        
        # Set as default if it's the first model or has higher priority
        if not self.default_model or config.priority < self.models[self.default_model].priority:
            self.default_model = model_id
            
        logger.info(f"Registered AI model: {model_id}")
    
    async def check_availability(self, model_id: Optional[str] = None) -> bool:
        """Check if a model is available"""
        if model_id is None:
            model_id = self.default_model
            
        if not model_id or model_id not in self.models:
            return False
            
        config = self.models[model_id]
        
        try:
            # Perform a lightweight health check based on provider
            if config.provider == AIProvider.OPENAI:
                return await self._check_openai_availability(config)
            elif config.provider == AIProvider.ANTHROPIC:
                return await self._check_anthropic_availability(config)
            elif config.provider == AIProvider.GOOGLE_GEMINI:
                return await self._check_gemini_availability(config)
            elif config.provider == AIProvider.OLLAMA:
                return await self._check_ollama_availability(config)
            elif config.provider == AIProvider.HUGGINGFACE:
                return await self._check_huggingface_availability(config)
            else:
                return False
                
        except Exception as e:
            logger.error(f"Availability check failed for {model_id}: {e}")
            config.last_error = str(e)
            config.is_available = False
            return False
    
    async def generate_text(
        self,
        prompt: str,
        model_id: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate text using the specified model with automatic fallback
        
        Args:
            prompt: Input prompt
            model_id: Specific model to use (uses default if None)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Dict with 'text', 'model_used', 'provider' keys
        """
        # Try primary model
        if model_id is None:
            model_id = self.default_model
            
        if not model_id:
            raise ValueError("No AI model configured")
        
        # Get sorted list of models by priority
        models_to_try = sorted(
            [m for m in self.models.values()],
            key=lambda x: x.priority
        )
        
        # Try primary model first, then fallbacks
        for config in models_to_try:
            try:
                logger.info(f"Attempting text generation with {config.provider.value}:{config.model_name}")
                
                result = await self._generate_with_provider(
                    config, prompt, max_tokens, temperature, **kwargs
                )
                
                if result:
                    config.is_available = True
                    return result
                    
            except Exception as e:
                logger.warning(f"Failed to generate with {config.provider.value}: {e}")
                config.last_error = str(e)
                config.is_available = False
                continue
        
        raise RuntimeError("All AI models failed to generate text")
    
    async def _generate_with_provider(
        self,
        config: AIModelConfig,
        prompt: str,
        max_tokens: Optional[int],
        temperature: Optional[float],
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Generate text using a specific provider"""
        
        max_tokens = max_tokens or config.max_tokens
        temperature = temperature or config.temperature
        
        if config.provider == AIProvider.OPENAI:
            return await self._generate_openai(config, prompt, max_tokens, temperature, **kwargs)
        elif config.provider == AIProvider.ANTHROPIC:
            return await self._generate_anthropic(config, prompt, max_tokens, temperature, **kwargs)
        elif config.provider == AIProvider.GOOGLE_GEMINI:
            return await self._generate_gemini(config, prompt, max_tokens, temperature, **kwargs)
        elif config.provider == AIProvider.OLLAMA:
            return await self._generate_ollama(config, prompt, max_tokens, temperature, **kwargs)
        elif config.provider == AIProvider.HUGGINGFACE:
            return await self._generate_huggingface(config, prompt, max_tokens, temperature, **kwargs)
        else:
            return None
    
    async def _generate_openai(self, config, prompt, max_tokens, temperature, **kwargs):
        """Generate text using OpenAI API"""
        try:
            import openai
            openai.api_key = config.api_key
            
            response = await openai.ChatCompletion.acreate(
                model=config.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            return {
                "text": response.choices[0].message.content,
                "model_used": config.model_name,
                "provider": config.provider.value,
                "usage": response.usage
            }
        except ImportError:
            logger.error("OpenAI package not installed. Install with: pip install openai")
            return None
        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            raise
    
    async def _generate_anthropic(self, config, prompt, max_tokens, temperature, **kwargs):
        """Generate text using Anthropic Claude API"""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=config.api_key)
            
            message = client.messages.create(
                model=config.model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return {
                "text": message.content[0].text,
                "model_used": config.model_name,
                "provider": config.provider.value,
                "usage": {
                    "input_tokens": message.usage.input_tokens,
                    "output_tokens": message.usage.output_tokens
                }
            }
        except ImportError:
            logger.error("Anthropic package not installed. Install with: pip install anthropic")
            return None
        except Exception as e:
            logger.error(f"Anthropic generation error: {e}")
            raise
    
    async def _generate_gemini(self, config, prompt, max_tokens, temperature, **kwargs):
        """Generate text using Google Gemini API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{config.model_name}:generateContent",
                    headers={"Content-Type": "application/json"},
                    params={"key": config.api_key},
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {
                            "maxOutputTokens": max_tokens,
                            "temperature": temperature
                        }
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    
                    return {
                        "text": text,
                        "model_used": config.model_name,
                        "provider": config.provider.value
                    }
                else:
                    raise RuntimeError(f"Gemini API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            raise
    
    async def _generate_ollama(self, config, prompt, max_tokens, temperature, **kwargs):
        """Generate text using Ollama local models"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{config.endpoint}/api/generate",
                    json={
                        "model": config.model_name,
                        "prompt": prompt,
                        "options": {
                            "num_predict": max_tokens,
                            "temperature": temperature
                        }
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "text": data["response"],
                        "model_used": config.model_name,
                        "provider": config.provider.value
                    }
                else:
                    raise RuntimeError(f"Ollama API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            raise
    
    async def _generate_huggingface(self, config, prompt, max_tokens, temperature, **kwargs):
        """Generate text using HuggingFace Inference API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://api-inference.huggingface.co/models/{config.model_name}",
                    headers={"Authorization": f"Bearer {config.api_key}"},
                    json={
                        "inputs": prompt,
                        "parameters": {
                            "max_new_tokens": max_tokens,
                            "temperature": temperature
                        }
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    text = data[0]["generated_text"] if isinstance(data, list) else data["generated_text"]
                    
                    return {
                        "text": text,
                        "model_used": config.model_name,
                        "provider": config.provider.value
                    }
                else:
                    raise RuntimeError(f"HuggingFace API error: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"HuggingFace generation error: {e}")
            raise
    
    async def _check_openai_availability(self, config) -> bool:
        """Check OpenAI API availability"""
        try:
            import openai
            openai.api_key = config.api_key
            # Simple API check
            await openai.Model.alist()
            config.is_available = True
            return True
        except:
            config.is_available = False
            return False
    
    async def _check_anthropic_availability(self, config) -> bool:
        """Check Anthropic API availability"""
        config.is_available = bool(config.api_key)
        return config.is_available
    
    async def _check_gemini_availability(self, config) -> bool:
        """Check Gemini API availability"""
        config.is_available = bool(config.api_key)
        return config.is_available
    
    async def _check_ollama_availability(self, config) -> bool:
        """Check Ollama endpoint availability"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{config.endpoint}/api/tags", timeout=5.0)
                config.is_available = response.status_code == 200
                return config.is_available
        except:
            config.is_available = False
            return False
    
    async def _check_huggingface_availability(self, config) -> bool:
        """Check HuggingFace API availability"""
        config.is_available = bool(config.api_key)
        return config.is_available
    
    def get_available_models(self) -> List[str]:
        """Get list of available model IDs"""
        return [
            model_id for model_id, config in self.models.items()
            if config.is_available or config.api_key is not None
        ]
    
    def get_model_info(self, model_id: Optional[str] = None) -> Dict[str, Any]:
        """Get information about a specific model"""
        if model_id is None:
            model_id = self.default_model
            
        if not model_id or model_id not in self.models:
            return {}
            
        config = self.models[model_id]
        return {
            "model_id": model_id,
            "provider": config.provider.value,
            "model_name": config.model_name,
            "capabilities": [c.value for c in config.capabilities],
            "is_available": config.is_available,
            "priority": config.priority,
            "last_error": config.last_error
        }


# Global instance
_universal_loader = None

def get_universal_loader() -> UniversalAILoader:
    """Get or create the global universal AI loader instance"""
    global _universal_loader
    if _universal_loader is None:
        _universal_loader = UniversalAILoader()
    return _universal_loader
