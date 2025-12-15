"""
LLM Provider Abstraction Layer
Supports multiple LLM providers with easy switching
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import config

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def generate_response(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        """Generate a response from the LLM"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available and configured"""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI GPT Provider"""
    
    def __init__(self):
        try:
            from langchain_openai import ChatOpenAI
            self.llm = ChatOpenAI(
                model=config.Config.OPENAI_MODEL,
                api_key=config.Config.OPENAI_API_KEY,
                temperature=0.7
            )
            self.available = True
        except Exception as e:
            print(f"Error initializing OpenAI: {e}")
            self.available = False
    
    def is_available(self) -> bool:
        return self.available and bool(config.Config.OPENAI_API_KEY)
    
    def generate_response(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        if not self.is_available():
            raise ValueError("OpenAI provider is not available or not configured")
        
        try:
            from langchain_core.messages import HumanMessage, SystemMessage
            
            messages = []
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            messages.append(HumanMessage(content=prompt))
            
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            raise Exception(f"Error generating OpenAI response: {str(e)}")


class GeminiProvider(LLMProvider):
    """Google Gemini Provider"""
    
    def __init__(self):
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            self.llm = ChatGoogleGenerativeAI(
                model=config.Config.GEMINI_MODEL,
                google_api_key=config.Config.GEMINI_API_KEY,
                temperature=0.7
            )
            self.available = True
        except Exception as e:
            print(f"Error initializing Gemini: {e}")
            self.available = False
    
    def is_available(self) -> bool:
        return self.available and bool(config.Config.GEMINI_API_KEY)
    
    def generate_response(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        if not self.is_available():
            raise ValueError("Gemini provider is not available or not configured")
        
        try:
            from langchain_core.messages import HumanMessage, SystemMessage
            
            messages = []
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            messages.append(HumanMessage(content=prompt))
            
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            raise Exception(f"Error generating Gemini response: {str(e)}")


class AnthropicProvider(LLMProvider):
    """Anthropic Claude Provider (Placeholder for future implementation)"""
    
    def __init__(self):
        self.available = False
    
    def is_available(self) -> bool:
        return False  # Not implemented yet
    
    def generate_response(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        raise NotImplementedError("Anthropic provider is not yet implemented")


class LLMProviderFactory:
    """Factory class to create and manage LLM providers"""
    
    _providers = {
        'openai': OpenAIProvider,
        'gemini': GeminiProvider,
        'anthropic': AnthropicProvider
    }
    
    _instance = None
    
    @classmethod
    def get_provider(cls, provider_name: str = None) -> LLMProvider:
        """Get an LLM provider instance"""
        if cls._instance is None:
            provider_name = provider_name or config.Config.LLM_PROVIDER
            
            if provider_name not in cls._providers:
                raise ValueError(f"Unknown provider: {provider_name}. Available: {list(cls._providers.keys())}")
            
            provider_class = cls._providers[provider_name]
            cls._instance = provider_class()
            
            if not cls._instance.is_available():
                raise ValueError(f"Provider {provider_name} is not available. Please check your API keys.")
        
        return cls._instance
    
    @classmethod
    def switch_provider(cls, provider_name: str) -> LLMProvider:
        """Switch to a different provider"""
        cls._instance = None
        return cls.get_provider(provider_name)
    
    @classmethod
    def list_available_providers(cls) -> List[str]:
        """List all available and configured providers"""
        available = []
        for name, provider_class in cls._providers.items():
            try:
                provider = provider_class()
                if provider.is_available():
                    available.append(name)
            except:
                pass
        return available

