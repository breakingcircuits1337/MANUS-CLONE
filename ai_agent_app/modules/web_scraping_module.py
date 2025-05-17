"""
Web Scraping Module for AI Agent Application
Handles web data extraction capabilities
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
import time
import random
import json
import os

class WebScrapingModule:
    """
    Web Scraping module that handles URL validation, content extraction,
    and data cleaning from websites.
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize the Web Scraping module
        
        Args:
            config: Configuration dictionary for the module
        """
        self.config = config or {}
        self.user_agent = self.config.get('user_agent', 'AI Agent App/1.0')
        self.rate_limit = self.config.get('rate_limit', 1)  # seconds between requests
        self.last_request_time = 0
        self.history = []
        
    def _respect_rate_limit(self) -> None:
        """Ensure rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit:
            sleep_time = self.rate_limit - time_since_last
            time.sleep(sleep_time)
            
        self.last_request_time = time.time()
    
    def validate_url(self, url: str) -> bool:
        """
        Validate if a URL is properly formatted
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Basic validation - could be enhanced with regex
        return url.startswith(('http://', 'https://'))
    
    def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch HTML content from a URL
        
        Args:
            url: URL to fetch
            
        Returns:
            HTML content as string or None if failed
        """
        if not self.validate_url(url):
            return None
            
        self._respect_rate_limit()
        
        headers = {'User-Agent': self.user_agent}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Add to history
            self.history.append({
                'url': url,
                'timestamp': time.time(),
                'status_code': response.status_code
            })
            
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def extract_text(self, html: str) -> str:
        """
        Extract readable text from HTML
        
        Args:
            html: HTML content
            
        Returns:
            Extracted text
        """
        if not html:
            return ""
            
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
            
        # Get text
        text = soup.get_text()
        
        # Break into lines and remove leading/trailing space
        lines = (line.strip() for line in text.splitlines())
        
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def extract_links(self, html: str, base_url: str = "") -> List[Dict[str, str]]:
        """
        Extract links from HTML
        
        Args:
            html: HTML content
            base_url: Base URL for resolving relative links
            
        Returns:
            List of dictionaries with 'text' and 'href' keys
        """
        if not html:
            return []
            
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            
            # Handle relative URLs
            if base_url and not href.startswith(('http://', 'https://')):
                if href.startswith('/'):
                    href = base_url.rstrip('/') + href
                else:
                    href = base_url.rstrip('/') + '/' + href
                    
            links.append({
                'text': a.get_text().strip(),
                'href': href
            })
            
        return links
    
    def extract_tables(self, html: str) -> List[List[List[str]]]:
        """
        Extract tables from HTML
        
        Args:
            html: HTML content
            
        Returns:
            List of tables, where each table is a list of rows, and each row is a list of cells
        """
        if not html:
            return []
            
        soup = BeautifulSoup(html, 'html.parser')
        tables = []
        
        for table in soup.find_all('table'):
            current_table = []
            
            for row in table.find_all('tr'):
                current_row = []
                
                # Process both header and data cells
                cells = row.find_all(['th', 'td'])
                for cell in cells:
                    current_row.append(cell.get_text().strip())
                    
                if current_row:
                    current_table.append(current_row)
                    
            if current_table:
                tables.append(current_table)
                
        return tables
    
    def save_results(self, data: Any, file_path: str) -> bool:
        """
        Save scraping results to a file
        
        Args:
            data: Data to save
            file_path: Path to save the data
            
        Returns:
            Success status
        """
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    def load_results(self, file_path: str) -> Optional[Any]:
        """
        Load scraping results from a file
        
        Args:
            file_path: Path to load the data from
            
        Returns:
            Loaded data or None if failed
        """
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"Error loading data: {e}")
            return None
    
    def get_history(self) -> List[Dict]:
        """
        Get scraping history
        
        Returns:
            List of scraping history entries
        """
        return self.history
    
    def clear_history(self) -> None:
        """Clear scraping history"""
        self.history = []
