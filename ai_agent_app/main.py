"""
Main entry point for AI Agent Application
"""

import os
import sys
from modules.application_controller import ApplicationController

def main():
    """
    Main entry point for the application
    """
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Initialize application controller
    app = ApplicationController('config.json')
    
    # Print startup message
    print("AI Agent Application")
    print("====================")
    print("Starting Streamlit interface...")
    
    # Launch Streamlit interface
    os.system("streamlit run app.py")

if __name__ == "__main__":
    main()
