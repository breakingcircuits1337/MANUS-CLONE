"""
README for AI Agent Application
"""

# AI Agent Application

A comprehensive, multi-functional application that emulates the capabilities of an advanced AI agent. This application serves as a versatile assistant capable of handling a wide range of tasks including natural language processing, web scraping, and data analysis.

## Features

- **Natural Language Processing**: Interact with multiple LLM providers (Gemini, Mistral, Groq, Ollama)
- **Web Scraping**: Extract data from websites with text, link, and table extraction
- **Data Analysis**: Process and visualize data with statistical analysis and plotting
- **Persistence**: Save and retrieve conversations, scraping results, and analysis between sessions
- **Memory Management**: Clear specific or all memory with a "forget" button
- **Streamlit GUI**: User-friendly interface for all functionalities

## Requirements

- Python 3.8+
- Streamlit
- Pandas
- NumPy
- Matplotlib
- BeautifulSoup4
- Requests
- SQLite3

## Installation

1. Clone the repository or extract the provided files
2. Install the required dependencies:

```bash
pip install streamlit requests beautifulsoup4 pandas numpy matplotlib
```

3. Run the application:

```bash
python main.py
```

## Configuration

The application uses a `config.json` file for configuration. You can modify this file to change default settings.

API keys for external services (Gemini, Mistral, Groq, Google) can be set through the application's settings panel.

## Usage

### Chat Interface

Use the chat interface to interact with various LLM providers. Select your preferred provider in the settings panel and ensure you've entered the appropriate API key.

### Web Scraping

Enter a URL to scrape content from websites. The application will extract text, links, and tables from the page.

You can also perform web searches using the Google Search API (requires API key and Search Engine ID).

### Data Analysis

Upload data files (CSV, Excel, JSON) for analysis. The application provides:
- Data summary statistics
- Visualization (bar charts, line charts, scatter plots, histograms, pie charts)
- Correlation analysis

### History

View your past interactions, including:
- Conversation history
- Web scraping results
- Data analysis results

### Memory Management

Clear specific types of memory or all memory using the buttons in the settings panel.

## Project Structure

- `main.py`: Application entry point
- `app.py`: Streamlit GUI implementation
- `config.json`: Application configuration
- `modules/`: Core functionality modules
  - `application_controller.py`: Central coordinator
  - `nlp_module.py`: Natural language processing
  - `web_scraping_module.py`: Web scraping functionality
  - `data_analysis_module.py`: Data analysis and visualization
  - `session_manager.py`: Persistence between sessions
  - `api_integration.py`: External API integration
- `data/`: Directory for persistent storage

## API Integration

The application supports integration with:
- Google (Search)
- Gemini
- Mistral
- Groq
- Ollama (local LLM)

API keys must be provided through the settings panel for these services to work.

## License

This project is provided for educational and personal use.

## Acknowledgements

This application was created as a demonstration of AI agent capabilities, integrating multiple services and functionalities into a cohesive assistant.
