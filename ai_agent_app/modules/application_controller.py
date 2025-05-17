"""
Main application controller for AI Agent Application
Coordinates between different modules
"""

import os
import json
from typing import Dict, List, Optional, Any

# Import modules
from modules.nlp_module import NLPModule
from modules.web_scraping_module import WebScrapingModule
from modules.data_analysis_module import DataAnalysisModule
from modules.session_manager import SessionManager
from modules.api_integration import APIIntegrationManager

class ApplicationController:
    """
    Application Controller that coordinates between different modules
    and manages the overall application flow.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Application Controller
        
        Args:
            config_path: Path to configuration file (optional)
        """
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize data directory
        self.data_dir = self.config.get('data_dir', 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize modules
        self.session_manager = SessionManager({'data_dir': self.data_dir})
        self.nlp_module = NLPModule(self.config.get('nlp_config', {}))
        self.web_scraping_module = WebScrapingModule(self.config.get('web_scraping_config', {}))
        self.data_analysis_module = DataAnalysisModule(self.config.get('data_analysis_config', {}))
        self.api_integration = APIIntegrationManager(self.config.get('api_config', {}))
        
        # Load API keys from preferences
        self._load_api_keys()
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """
        Load configuration from file or use defaults
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        default_config = {
            'data_dir': 'data',
            'nlp_config': {
                'max_context_length': 10,
                'default_provider': 'gemini'
            },
            'web_scraping_config': {
                'user_agent': 'AI Agent App/1.0',
                'rate_limit': 1
            },
            'data_analysis_config': {},
            'api_config': {
                'default_provider': 'gemini'
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    for key, value in loaded_config.items():
                        if key in default_config and isinstance(default_config[key], dict) and isinstance(value, dict):
                            default_config[key].update(value)
                        else:
                            default_config[key] = value
            except Exception as e:
                print(f"Error loading configuration: {e}")
        
        return default_config
    
    def _load_api_keys(self) -> None:
        """Load API keys from session preferences"""
        api_keys = self.session_manager.load_preference('api_keys', {})
        
        for provider, key in api_keys.items():
            self.api_integration.set_api_key(provider, key)
    
    def _save_api_keys(self) -> None:
        """Save API keys to session preferences"""
        self.session_manager.save_preference('api_keys', self.api_integration.api_keys)
    
    def set_api_key(self, provider: str, api_key: str) -> None:
        """
        Set API key for a provider
        
        Args:
            provider: Provider name
            api_key: API key
        """
        self.api_integration.set_api_key(provider, api_key)
        self._save_api_keys()
    
    def process_nlp_request(self, user_input: str, provider: Optional[str] = None) -> str:
        """
        Process a natural language request
        
        Args:
            user_input: User input text
            provider: LLM provider to use (optional)
            
        Returns:
            Response text
        """
        # Add to NLP context
        self.nlp_module.add_to_context({'role': 'user', 'content': user_input})
        
        # Use API integration to get response
        provider = provider or self.api_integration.get_default_provider()
        response_data = self.api_integration.generate_text(user_input, provider)
        
        # Extract response text based on provider
        response_text = "Sorry, I couldn't process your request."
        
        if 'error' in response_data:
            response_text = f"Error: {response_data['error']}"
        elif provider == 'gemini':
            if 'candidates' in response_data and response_data['candidates']:
                response_text = response_data['candidates'][0]['content']['parts'][0]['text']
        elif provider == 'mistral':
            if 'choices' in response_data and response_data['choices']:
                response_text = response_data['choices'][0]['message']['content']
        elif provider == 'groq':
            if 'choices' in response_data and response_data['choices']:
                response_text = response_data['choices'][0]['message']['content']
        elif provider == 'ollama':
            if 'response' in response_data:
                response_text = response_data['response']
        
        # Add to NLP context
        self.nlp_module.add_to_context({'role': 'assistant', 'content': response_text})
        
        # Save conversation to session
        self.session_manager.save_conversation(self.nlp_module.get_context())
        
        return response_text
    
    def process_web_scraping_request(self, url: str) -> Dict:
        """
        Process a web scraping request
        
        Args:
            url: URL to scrape
            
        Returns:
            Dictionary with scraped data
        """
        # Fetch page
        html = self.web_scraping_module.fetch_page(url)
        
        if not html:
            return {'error': 'Failed to fetch page'}
        
        # Extract data
        text = self.web_scraping_module.extract_text(html)
        links = self.web_scraping_module.extract_links(html, url)
        tables = self.web_scraping_module.extract_tables(html)
        
        # Prepare result
        result = {
            'url': url,
            'text': text,
            'links': links,
            'tables': tables
        }
        
        # Save to session
        self.session_manager.save_scraping_result(url, result)
        
        return result
    
    def process_data_analysis_request(self, data: Any, analysis_type: str, params: Dict = None) -> Dict:
        """
        Process a data analysis request
        
        Args:
            data: Data to analyze
            analysis_type: Type of analysis
            params: Analysis parameters
            
        Returns:
            Analysis results
        """
        params = params or {}
        
        # Load data
        if isinstance(data, str) and os.path.exists(data):
            success = self.data_analysis_module.load_data(data)
        elif isinstance(data, dict):
            success = self.data_analysis_module.load_data_from_dict(data)
        elif isinstance(data, list):
            success = self.data_analysis_module.load_data_from_list(data)
        else:
            return {'error': 'Invalid data format'}
        
        if not success:
            return {'error': 'Failed to load data'}
        
        # Perform analysis
        result = {}
        
        if analysis_type == 'summary':
            result = self.data_analysis_module.get_data_summary()
        elif analysis_type == 'correlation':
            columns = params.get('columns')
            result = self.data_analysis_module.perform_correlation(columns)
            if result is not None:
                result = result.to_dict()
        elif analysis_type == 'plot':
            plot_type = params.get('plot_type', 'bar')
            x_column = params.get('x_column')
            y_column = params.get('y_column')
            title = params.get('title', '')
            save_path = params.get('save_path')
            
            if not x_column:
                return {'error': 'X column not specified'}
                
            img_str = self.data_analysis_module.generate_plot(
                plot_type, x_column, y_column, title, save_path
            )
            
            if img_str:
                result = {'image': img_str}
            else:
                return {'error': 'Failed to generate plot'}
        else:
            return {'error': f'Unknown analysis type: {analysis_type}'}
        
        # Save to session
        description = f"{analysis_type} analysis"
        self.session_manager.save_analysis_result(description, result)
        
        return result
    
    def search_web(self, query: str, num_results: int = 10) -> Dict:
        """
        Search the web using Google
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            Search results
        """
        return self.api_integration.google_search(query, num_results)
    
    def clear_memory(self, memory_type: str = 'all') -> bool:
        """
        Clear memory/persistence data
        
        Args:
            memory_type: Type of memory to clear ('all', 'conversations', 'scraping', 'analysis')
            
        Returns:
            Success status
        """
        if memory_type == 'all':
            success = self.session_manager.clear_all_data()
            if success:
                self.nlp_module.clear_context()
                self.web_scraping_module.clear_history()
                self.data_analysis_module.clear_history()
                self.api_integration.clear_history()
            return success
        elif memory_type == 'conversations':
            success = self.session_manager.clear_conversation_data()
            if success:
                self.nlp_module.clear_context()
            return success
        elif memory_type == 'scraping':
            success = self.session_manager.clear_scraping_data()
            if success:
                self.web_scraping_module.clear_history()
            return success
        elif memory_type == 'analysis':
            success = self.session_manager.clear_analysis_data()
            if success:
                self.data_analysis_module.clear_history()
            return success
        else:
            return False
    
    def export_data(self, file_path: str) -> bool:
        """
        Export all data to a file
        
        Args:
            file_path: Path to save the exported data
            
        Returns:
            Success status
        """
        return self.session_manager.export_all_data(file_path)
    
    def import_data(self, file_path: str, replace_existing: bool = False) -> bool:
        """
        Import data from a file
        
        Args:
            file_path: Path to the data file
            replace_existing: Whether to replace existing data
            
        Returns:
            Success status
        """
        return self.session_manager.import_data(file_path, replace_existing)
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict]:
        """
        Get conversation history
        
        Args:
            limit: Maximum number of conversations to return
            
        Returns:
            List of conversation entries
        """
        return self.session_manager.load_conversations(limit)
    
    def get_scraping_history(self, limit: int = 10) -> List[Dict]:
        """
        Get web scraping history
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of scraping history entries
        """
        return self.session_manager.load_scraping_results(limit)
    
    def get_analysis_history(self, limit: int = 10) -> List[Dict]:
        """
        Get data analysis history
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of analysis history entries
        """
        return self.session_manager.load_analysis_results(limit)
