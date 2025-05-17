"""
Session Manager for AI Agent Application
Handles persistence of data between sessions
"""

import json
import os
import pickle
import sqlite3
from typing import Dict, List, Optional, Any
import time

class SessionManager:
    """
    Session Manager that handles persistence of conversations, 
    user preferences, and application data between sessions.
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize the Session Manager
        
        Args:
            config: Configuration dictionary for the module
        """
        self.config = config or {}
        self.data_dir = self.config.get('data_dir', 'data')
        self.db_path = os.path.join(self.data_dir, 'session.db')
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize database if needed
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize the SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables if they don't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            conversation_data TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS preferences (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS scraping_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            url TEXT,
            data TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            description TEXT,
            data TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_conversation(self, conversation_data: List[Dict]) -> bool:
        """
        Save conversation data to database
        
        Args:
            conversation_data: List of conversation messages
            
        Returns:
            Success status
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            data_json = json.dumps(conversation_data)
            
            cursor.execute(
                'INSERT INTO conversations (timestamp, conversation_data) VALUES (?, ?)',
                (timestamp, data_json)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving conversation: {e}")
            return False
    
    def load_conversations(self, limit: int = 10) -> List[Dict]:
        """
        Load recent conversations from database
        
        Args:
            limit: Maximum number of conversations to load
            
        Returns:
            List of conversation entries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                'SELECT id, timestamp, conversation_data FROM conversations ORDER BY id DESC LIMIT ?',
                (limit,)
            )
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': row[0],
                    'timestamp': row[1],
                    'data': json.loads(row[2])
                })
            
            conn.close()
            return results
        except Exception as e:
            print(f"Error loading conversations: {e}")
            return []
    
    def save_preference(self, key: str, value: Any) -> bool:
        """
        Save a user preference
        
        Args:
            key: Preference key
            value: Preference value
            
        Returns:
            Success status
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            value_json = json.dumps(value)
            
            cursor.execute(
                'INSERT OR REPLACE INTO preferences (key, value) VALUES (?, ?)',
                (key, value_json)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving preference: {e}")
            return False
    
    def load_preference(self, key: str, default: Any = None) -> Any:
        """
        Load a user preference
        
        Args:
            key: Preference key
            default: Default value if preference not found
            
        Returns:
            Preference value
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT value FROM preferences WHERE key = ?', (key,))
            result = cursor.fetchone()
            
            conn.close()
            
            if result:
                return json.loads(result[0])
            return default
        except Exception as e:
            print(f"Error loading preference: {e}")
            return default
    
    def save_scraping_result(self, url: str, data: Any) -> bool:
        """
        Save web scraping result
        
        Args:
            url: Source URL
            data: Scraped data
            
        Returns:
            Success status
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            data_json = json.dumps(data)
            
            cursor.execute(
                'INSERT INTO scraping_results (timestamp, url, data) VALUES (?, ?, ?)',
                (timestamp, url, data_json)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving scraping result: {e}")
            return False
    
    def load_scraping_results(self, limit: int = 10) -> List[Dict]:
        """
        Load recent scraping results
        
        Args:
            limit: Maximum number of results to load
            
        Returns:
            List of scraping result entries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                'SELECT id, timestamp, url, data FROM scraping_results ORDER BY id DESC LIMIT ?',
                (limit,)
            )
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': row[0],
                    'timestamp': row[1],
                    'url': row[2],
                    'data': json.loads(row[3])
                })
            
            conn.close()
            return results
        except Exception as e:
            print(f"Error loading scraping results: {e}")
            return []
    
    def save_analysis_result(self, description: str, data: Any) -> bool:
        """
        Save data analysis result
        
        Args:
            description: Analysis description
            data: Analysis data
            
        Returns:
            Success status
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            data_json = json.dumps(data)
            
            cursor.execute(
                'INSERT INTO analysis_results (timestamp, description, data) VALUES (?, ?, ?)',
                (timestamp, description, data_json)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving analysis result: {e}")
            return False
    
    def load_analysis_results(self, limit: int = 10) -> List[Dict]:
        """
        Load recent analysis results
        
        Args:
            limit: Maximum number of results to load
            
        Returns:
            List of analysis result entries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                'SELECT id, timestamp, description, data FROM analysis_results ORDER BY id DESC LIMIT ?',
                (limit,)
            )
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': row[0],
                    'timestamp': row[1],
                    'description': row[2],
                    'data': json.loads(row[3])
                })
            
            conn.close()
            return results
        except Exception as e:
            print(f"Error loading analysis results: {e}")
            return []
    
    def clear_all_data(self) -> bool:
        """
        Clear all persistent data (implement "forget" functionality)
        
        Returns:
            Success status
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Clear all tables
            cursor.execute('DELETE FROM conversations')
            cursor.execute('DELETE FROM preferences')
            cursor.execute('DELETE FROM scraping_results')
            cursor.execute('DELETE FROM analysis_results')
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error clearing data: {e}")
            return False
    
    def clear_conversation_data(self) -> bool:
        """
        Clear only conversation data
        
        Returns:
            Success status
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM conversations')
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error clearing conversation data: {e}")
            return False
    
    def clear_scraping_data(self) -> bool:
        """
        Clear only web scraping data
        
        Returns:
            Success status
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM scraping_results')
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error clearing scraping data: {e}")
            return False
    
    def clear_analysis_data(self) -> bool:
        """
        Clear only analysis data
        
        Returns:
            Success status
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM analysis_results')
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error clearing analysis data: {e}")
            return False
    
    def export_all_data(self, file_path: str) -> bool:
        """
        Export all data to a JSON file
        
        Args:
            file_path: Path to save the exported data
            
        Returns:
            Success status
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all data
            cursor.execute('SELECT id, timestamp, conversation_data FROM conversations')
            conversations = [{'id': row[0], 'timestamp': row[1], 'data': json.loads(row[2])} for row in cursor.fetchall()]
            
            cursor.execute('SELECT key, value FROM preferences')
            preferences = {row[0]: json.loads(row[1]) for row in cursor.fetchall()}
            
            cursor.execute('SELECT id, timestamp, url, data FROM scraping_results')
            scraping = [{'id': row[0], 'timestamp': row[1], 'url': row[2], 'data': json.loads(row[3])} for row in cursor.fetchall()]
            
            cursor.execute('SELECT id, timestamp, description, data FROM analysis_results')
            analysis = [{'id': row[0], 'timestamp': row[1], 'description': row[2], 'data': json.loads(row[3])} for row in cursor.fetchall()]
            
            conn.close()
            
            # Combine all data
            export_data = {
                'conversations': conversations,
                'preferences': preferences,
                'scraping_results': scraping,
                'analysis_results': analysis,
                'export_timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Save to file
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error exporting data: {e}")
            return False
    
    def import_data(self, file_path: str, replace_existing: bool = False) -> bool:
        """
        Import data from a JSON file
        
        Args:
            file_path: Path to the data file
            replace_existing: Whether to replace existing data
            
        Returns:
            Success status
        """
        try:
            # Load data from file
            with open(file_path, 'r') as f:
                import_data = json.load(f)
                
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Clear existing data if requested
            if replace_existing:
                cursor.execute('DELETE FROM conversations')
                cursor.execute('DELETE FROM preferences')
                cursor.execute('DELETE FROM scraping_results')
                cursor.execute('DELETE FROM analysis_results')
            
            # Import conversations
            for conv in import_data.get('conversations', []):
                data_json = json.dumps(conv['data'])
                cursor.execute(
                    'INSERT INTO conversations (timestamp, conversation_data) VALUES (?, ?)',
                    (conv['timestamp'], data_json)
                )
            
            # Import preferences
            for key, value in import_data.get('preferences', {}).items():
                value_json = json.dumps(value)
                cursor.execute(
                    'INSERT OR REPLACE INTO preferences (key, value) VALUES (?, ?)',
                    (key, value_json)
                )
            
            # Import scraping results
            for result in import_data.get('scraping_results', []):
                data_json = json.dumps(result['data'])
                cursor.execute(
                    'INSERT INTO scraping_results (timestamp, url, data) VALUES (?, ?, ?)',
                    (result['timestamp'], result['url'], data_json)
                )
            
            # Import analysis results
            for result in import_data.get('analysis_results', []):
                data_json = json.dumps(result['data'])
                cursor.execute(
                    'INSERT INTO analysis_results (timestamp, description, data) VALUES (?, ?, ?)',
                    (result['timestamp'], result['description'], data_json)
                )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error importing data: {e}")
            return False
