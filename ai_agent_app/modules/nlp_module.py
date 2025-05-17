"""
NLP Module for AI Agent Application
Handles natural language processing capabilities
"""

import json
import os
from typing import Dict, List, Optional, Any

class NLPModule:
    """
    Natural Language Processing module that handles text processing,
    context management, and integration with various LLM providers.
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize the NLP module
        
        Args:
            config: Configuration dictionary for the module
        """
        self.config = config or {}
        self.context = []
        self.max_context_length = self.config.get('max_context_length', 10)
        self.current_provider = self.config.get('default_provider', 'gemini')
        
    def add_to_context(self, message: Dict[str, str]) -> None:
        """
        Add a message to the conversation context
        
        Args:
            message: Dictionary with 'role' and 'content' keys
        """
        self.context.append(message)
        
        # Trim context if it exceeds max length
        if len(self.context) > self.max_context_length:
            self.context = self.context[-self.max_context_length:]
    
    def clear_context(self) -> None:
        """Clear the conversation context"""
        self.context = []
    
    def process_input(self, user_input: str) -> str:
        """
        Process user input and generate a response
        
        Args:
            user_input: The text input from the user
            
        Returns:
            Generated response text
        """
        # Add user message to context
        self.add_to_context({'role': 'user', 'content': user_input})
        
        # Placeholder for actual LLM integration
        # In a real implementation, this would call the appropriate API
        response = f"This is a placeholder response from the {self.current_provider} provider. In a complete implementation, this would process: '{user_input}'"
        
        # Add assistant response to context
        self.add_to_context({'role': 'assistant', 'content': response})
        
        return response
    
    def set_provider(self, provider_name: str) -> bool:
        """
        Set the current LLM provider
        
        Args:
            provider_name: Name of the provider to use
            
        Returns:
            Success status
        """
        valid_providers = ['gemini', 'mistral', 'groq', 'ollama']
        if provider_name.lower() in valid_providers:
            self.current_provider = provider_name.lower()
            return True
        return False
    
    def get_context(self) -> List[Dict[str, str]]:
        """
        Get the current conversation context
        
        Returns:
            List of context messages
        """
        return self.context
    
    def save_context(self, file_path: str) -> bool:
        """
        Save the current context to a file
        
        Args:
            file_path: Path to save the context
            
        Returns:
            Success status
        """
        try:
            with open(file_path, 'w') as f:
                json.dump(self.context, f)
            return True
        except Exception as e:
            print(f"Error saving context: {e}")
            return False
    
    def load_context(self, file_path: str) -> bool:
        """
        Load context from a file
        
        Args:
            file_path: Path to load the context from
            
        Returns:
            Success status
        """
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    self.context = json.load(f)
                return True
            return False
        except Exception as e:
            print(f"Error loading context: {e}")
            return False
