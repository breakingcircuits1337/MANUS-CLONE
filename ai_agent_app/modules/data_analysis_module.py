"""
Data Analysis Module for AI Agent Application
Handles data processing and analysis capabilities
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import os
from typing import Dict, List, Optional, Any, Tuple, Union
import io
import base64

class DataAnalysisModule:
    """
    Data Analysis module that handles data import/export,
    statistical analysis, and visualization generation.
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize the Data Analysis module
        
        Args:
            config: Configuration dictionary for the module
        """
        self.config = config or {}
        self.current_data = None
        self.analysis_history = []
        
    def load_data(self, file_path: str) -> bool:
        """
        Load data from a file
        
        Args:
            file_path: Path to the data file
            
        Returns:
            Success status
        """
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.csv':
                self.current_data = pd.read_csv(file_path)
            elif file_ext == '.xlsx' or file_ext == '.xls':
                self.current_data = pd.read_excel(file_path)
            elif file_ext == '.json':
                self.current_data = pd.read_json(file_path)
            elif file_ext == '.txt':
                self.current_data = pd.read_csv(file_path, sep='\t')
            else:
                print(f"Unsupported file format: {file_ext}")
                return False
                
            self._add_to_history(f"Loaded data from {file_path}")
            return True
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def load_data_from_dict(self, data: Dict) -> bool:
        """
        Load data from a dictionary
        
        Args:
            data: Dictionary containing data
            
        Returns:
            Success status
        """
        try:
            self.current_data = pd.DataFrame(data)
            self._add_to_history("Loaded data from dictionary")
            return True
        except Exception as e:
            print(f"Error loading data from dictionary: {e}")
            return False
    
    def load_data_from_list(self, data: List) -> bool:
        """
        Load data from a list
        
        Args:
            data: List containing data
            
        Returns:
            Success status
        """
        try:
            self.current_data = pd.DataFrame(data)
            self._add_to_history("Loaded data from list")
            return True
        except Exception as e:
            print(f"Error loading data from list: {e}")
            return False
    
    def save_data(self, file_path: str) -> bool:
        """
        Save current data to a file
        
        Args:
            file_path: Path to save the data
            
        Returns:
            Success status
        """
        if self.current_data is None:
            print("No data to save")
            return False
            
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.csv':
                self.current_data.to_csv(file_path, index=False)
            elif file_ext == '.xlsx':
                self.current_data.to_excel(file_path, index=False)
            elif file_ext == '.json':
                self.current_data.to_json(file_path, orient='records')
            else:
                print(f"Unsupported file format: {file_ext}")
                return False
                
            self._add_to_history(f"Saved data to {file_path}")
            return True
            
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    def get_data_summary(self) -> Dict:
        """
        Get a summary of the current data
        
        Returns:
            Dictionary with data summary
        """
        if self.current_data is None:
            return {"error": "No data loaded"}
            
        try:
            summary = {
                "shape": self.current_data.shape,
                "columns": list(self.current_data.columns),
                "dtypes": {col: str(dtype) for col, dtype in self.current_data.dtypes.items()},
                "missing_values": self.current_data.isnull().sum().to_dict(),
                "numeric_summary": {}
            }
            
            # Add numeric summary for numeric columns
            for col in self.current_data.select_dtypes(include=[np.number]).columns:
                summary["numeric_summary"][col] = {
                    "min": float(self.current_data[col].min()),
                    "max": float(self.current_data[col].max()),
                    "mean": float(self.current_data[col].mean()),
                    "median": float(self.current_data[col].median()),
                    "std": float(self.current_data[col].std())
                }
                
            self._add_to_history("Generated data summary")
            return summary
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return {"error": str(e)}
    
    def filter_data(self, condition: str) -> bool:
        """
        Filter data based on a condition
        
        Args:
            condition: Filtering condition as string (e.g., "column > value")
            
        Returns:
            Success status
        """
        if self.current_data is None:
            print("No data loaded")
            return False
            
        try:
            self.current_data = self.current_data.query(condition)
            self._add_to_history(f"Filtered data with condition: {condition}")
            return True
        except Exception as e:
            print(f"Error filtering data: {e}")
            return False
    
    def sort_data(self, column: str, ascending: bool = True) -> bool:
        """
        Sort data by a column
        
        Args:
            column: Column to sort by
            ascending: Sort order
            
        Returns:
            Success status
        """
        if self.current_data is None:
            print("No data loaded")
            return False
            
        if column not in self.current_data.columns:
            print(f"Column {column} not found")
            return False
            
        try:
            self.current_data = self.current_data.sort_values(by=column, ascending=ascending)
            self._add_to_history(f"Sorted data by {column} ({'ascending' if ascending else 'descending'})")
            return True
        except Exception as e:
            print(f"Error sorting data: {e}")
            return False
    
    def generate_plot(self, plot_type: str, x_column: str, y_column: Optional[str] = None, 
                     title: str = "", save_path: Optional[str] = None) -> Optional[str]:
        """
        Generate a plot from the current data
        
        Args:
            plot_type: Type of plot ('bar', 'line', 'scatter', 'histogram', 'pie')
            x_column: Column for x-axis
            y_column: Column for y-axis (optional for some plot types)
            title: Plot title
            save_path: Path to save the plot image
            
        Returns:
            Base64 encoded image or None if failed
        """
        if self.current_data is None:
            print("No data loaded")
            return None
            
        if x_column not in self.current_data.columns:
            print(f"Column {x_column} not found")
            return None
            
        if y_column and y_column not in self.current_data.columns:
            print(f"Column {y_column} not found")
            return None
            
        try:
            plt.figure(figsize=(10, 6))
            
            if plot_type == 'bar':
                if y_column:
                    self.current_data.plot(kind='bar', x=x_column, y=y_column)
                else:
                    self.current_data[x_column].value_counts().plot(kind='bar')
                    
            elif plot_type == 'line':
                if y_column:
                    self.current_data.plot(kind='line', x=x_column, y=y_column)
                else:
                    self.current_data[x_column].plot(kind='line')
                    
            elif plot_type == 'scatter':
                if not y_column:
                    print("Y column required for scatter plot")
                    return None
                self.current_data.plot(kind='scatter', x=x_column, y=y_column)
                
            elif plot_type == 'histogram':
                self.current_data[x_column].plot(kind='hist')
                
            elif plot_type == 'pie':
                self.current_data[x_column].value_counts().plot(kind='pie')
                
            else:
                print(f"Unsupported plot type: {plot_type}")
                return None
                
            plt.title(title)
            plt.tight_layout()
            
            # Save to file if path provided
            if save_path:
                plt.savefig(save_path)
                self._add_to_history(f"Saved {plot_type} plot to {save_path}")
                
            # Convert plot to base64 for display
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            img_str = base64.b64encode(buf.read()).decode('utf-8')
            plt.close()
            
            self._add_to_history(f"Generated {plot_type} plot")
            return img_str
            
        except Exception as e:
            print(f"Error generating plot: {e}")
            plt.close()
            return None
    
    def perform_correlation(self, columns: Optional[List[str]] = None) -> Optional[pd.DataFrame]:
        """
        Calculate correlation matrix for numeric columns
        
        Args:
            columns: List of columns to include (optional)
            
        Returns:
            Correlation matrix as DataFrame or None if failed
        """
        if self.current_data is None:
            print("No data loaded")
            return None
            
        try:
            if columns:
                # Check if all columns exist
                missing_cols = [col for col in columns if col not in self.current_data.columns]
                if missing_cols:
                    print(f"Columns not found: {missing_cols}")
                    return None
                    
                # Check if columns are numeric
                non_numeric = [col for col in columns if col not in self.current_data.select_dtypes(include=[np.number]).columns]
                if non_numeric:
                    print(f"Non-numeric columns: {non_numeric}")
                    return None
                    
                corr_matrix = self.current_data[columns].corr()
            else:
                corr_matrix = self.current_data.select_dtypes(include=[np.number]).corr()
                
            self._add_to_history("Calculated correlation matrix")
            return corr_matrix
            
        except Exception as e:
            print(f"Error calculating correlation: {e}")
            return None
    
    def _add_to_history(self, action: str) -> None:
        """
        Add an action to the analysis history
        
        Args:
            action: Description of the action
        """
        self.analysis_history.append({
            "timestamp": pd.Timestamp.now().isoformat(),
            "action": action
        })
    
    def get_history(self) -> List[Dict]:
        """
        Get analysis history
        
        Returns:
            List of analysis history entries
        """
        return self.analysis_history
    
    def clear_history(self) -> None:
        """Clear analysis history"""
        self.analysis_history = []
    
    def clear_data(self) -> None:
        """Clear current data"""
        self.current_data = None
        self._add_to_history("Cleared data")
