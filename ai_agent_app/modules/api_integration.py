"""
API Integration Manager for AI Agent Application
Handles communication with external LLM services
"""

import requests
import json
import os
from typing import Dict, List, Optional, Any
import time

class APIIntegrationManager:
    """
    API Integration Manager that handles communication with external services
    including Google, Gemini, Mistral, Groq, and Ollama.
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize the API Integration Manager
        
        Args:
            config: Configuration dictionary for the module
        """
        self.config = config or {}
        self.api_keys = self.config.get('api_keys', {})
        self.default_provider = self.config.get('default_provider', 'gemini')
        self.request_history = []
        
    def set_api_key(self, provider: str, api_key: str) -> None:
        """
        Set API key for a provider
        
        Args:
            provider: Provider name
            api_key: API key
        """
        self.api_keys[provider] = api_key
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """
        Get API key for a provider
        
        Args:
            provider: Provider name
            
        Returns:
            API key or None if not set
        """
        return self.api_keys.get(provider)
    
    def set_default_provider(self, provider: str) -> bool:
        """
        Set default LLM provider
        
        Args:
            provider: Provider name
            
        Returns:
            Success status
        """
        valid_providers = ['gemini', 'mistral', 'groq', 'ollama']
        if provider.lower() in valid_providers:
            self.default_provider = provider.lower()
            return True
        return False
    
    def get_default_provider(self) -> str:
        """
        Get default LLM provider
        
        Returns:
            Default provider name
        """
        return self.default_provider
    
    def _add_to_history(self, provider: str, request_type: str, request_data: Dict, response_data: Dict) -> None:
        """
        Add request/response to history
        
        Args:
            provider: Provider name
            request_type: Type of request
            request_data: Request data
            response_data: Response data
        """
        self.request_history.append({
            'timestamp': time.time(),
            'provider': provider,
            'request_type': request_type,
            'request_data': request_data,
            'response_data': response_data
        })
        
        # Trim history if it gets too long
        if len(self.request_history) > 100:
            self.request_history = self.request_history[-100:]
    
    def get_history(self) -> List[Dict]:
        """
        Get request history
        
        Returns:
            List of request history entries
        """
        return self.request_history
    
    def clear_history(self) -> None:
        """Clear request history"""
        self.request_history = []
    
    def gemini_generate_text(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.7) -> Dict:
        """
        Generate text using Gemini API
        
        Args:
            prompt: Text prompt
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Response dictionary
        """
        api_key = self.get_api_key('gemini')
        if not api_key:
            return {'error': 'Gemini API key not set'}
        
        try:
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
            headers = {
                "Content-Type": "application/json"
            }
            
            params = {
                "key": api_key
            }
            
            data = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens,
                    "topP": 0.95,
                    "topK": 40
                }
            }
            
            response = requests.post(url, headers=headers, params=params, json=data)
            response.raise_for_status()
            result = response.json()
            
            # Add to history
            self._add_to_history('gemini', 'text_generation', 
                                {'prompt': prompt, 'max_tokens': max_tokens, 'temperature': temperature}, 
                                result)
            
            return result
        except Exception as e:
            error_response = {'error': str(e)}
            self._add_to_history('gemini', 'text_generation', 
                                {'prompt': prompt, 'max_tokens': max_tokens, 'temperature': temperature}, 
                                error_response)
            return error_response
    
    def mistral_generate_text(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.7) -> Dict:
        """
        Generate text using Mistral API
        
        Args:
            prompt: Text prompt
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Response dictionary
        """
        api_key = self.get_api_key('mistral')
        if not api_key:
            return {'error': 'Mistral API key not set'}
        
        try:
            url = "https://api.mistral.ai/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            data = {
                "model": "mistral-medium",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            # Add to history
            self._add_to_history('mistral', 'text_generation', 
                                {'prompt': prompt, 'max_tokens': max_tokens, 'temperature': temperature}, 
                                result)
            
            return result
        except Exception as e:
            error_response = {'error': str(e)}
            self._add_to_history('mistral', 'text_generation', 
                                {'prompt': prompt, 'max_tokens': max_tokens, 'temperature': temperature}, 
                                error_response)
            return error_response
    
    def groq_generate_text(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.7) -> Dict:
        """
        Generate text using Groq API
        
        Args:
            prompt: Text prompt
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Response dictionary
        """
        api_key = self.get_api_key('groq')
        if not api_key:
            return {'error': 'Groq API key not set'}
        
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            data = {
                "model": "llama3-8b-8192",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            # Add to history
            self._add_to_history('groq', 'text_generation', 
                                {'prompt': prompt, 'max_tokens': max_tokens, 'temperature': temperature}, 
                                result)
            
            return result
        except Exception as e:
            error_response = {'error': str(e)}
            self._add_to_history('groq', 'text_generation', 
                                {'prompt': prompt, 'max_tokens': max_tokens, 'temperature': temperature}, 
                                error_response)
            return error_response
    
    def ollama_generate_text(self, prompt: str, model: str = "llama3", max_tokens: int = 1024, temperature: float = 0.7) -> Dict:
        """
        Generate text using local Ollama instance
        
        Args:
            prompt: Text prompt
            model: Model name
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Response dictionary
        """
        try:
            url = "http://localhost:11434/api/generate"
            headers = {
                "Content-Type": "application/json"
            }
            
            data = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature
                }
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            # Add to history
            self._add_to_history('ollama', 'text_generation', 
                                {'prompt': prompt, 'model': model, 'max_tokens': max_tokens, 'temperature': temperature}, 
                                result)
            
            return result
        except Exception as e:
            error_response = {'error': str(e)}
            self._add_to_history('ollama', 'text_generation', 
                                {'prompt': prompt, 'model': model, 'max_tokens': max_tokens, 'temperature': temperature}, 
                                error_response)
            return error_response
    
    def google_search(self, query: str, num_results: int = 10) -> Dict:
        """
        Perform Google search
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            Response dictionary
        """
        api_key = self.get_api_key('google_search')
        if not api_key:
            return {'error': 'Google Search API key not set'}
        
        search_engine_id = self.config.get('google_search_engine_id')
        if not search_engine_id:
            return {'error': 'Google Search Engine ID not set'}
        
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": api_key,
                "cx": search_engine_id,
                "q": query,
                "num": min(num_results, 10)  # API limit is 10
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            result = response.json()
            
            # Add to history
            self._add_to_history('google', 'search', 
                                {'query': query, 'num_results': num_results}, 
                                result)
            
            return result
        except Exception as e:
            error_response = {'error': str(e)}
            self._add_to_history('google', 'search', 
                                {'query': query, 'num_results': num_results}, 
                                error_response)
            return error_response
    
    def generate_text(self, prompt: str, provider: Optional[str] = None, max_tokens: int = 1024, temperature: float = 0.7) -> Dict:
        """
        Generate text using the specified or default provider
        
        Args:
            prompt: Text prompt
            provider: Provider name (optional, uses default if not specified)
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Response dictionary
        """
        provider = provider or self.default_provider
        
        if provider == 'gemini':
            return self.gemini_generate_text(prompt, max_tokens, temperature)
        elif provider == 'mistral':
            return self.mistral_generate_text(prompt, max_tokens, temperature)
        elif provider == 'groq':
            return self.groq_generate_text(prompt, max_tokens, temperature)
        elif provider == 'ollama':
            return self.ollama_generate_text(prompt, "llama3", max_tokens, temperature)
        else:
            return {'error': f'Unknown provider: {provider}'}
