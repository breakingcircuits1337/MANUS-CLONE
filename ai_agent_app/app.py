"""
Streamlit GUI for AI Agent Application
Provides a graphical user interface for the AI agent
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import json
import base64
from io import BytesIO
import time
from PIL import Image

# Import application controller
from modules.application_controller import ApplicationController

# Initialize application controller
@st.cache_resource
def get_app_controller():
    return ApplicationController()

def main():
    # Set page configuration
    st.set_page_config(
        page_title="AI Agent Application",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize application controller
    app = get_app_controller()
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #4B8BF5;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #5F6368;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        white-space: pre-wrap;
        font-size: 1rem;
    }
    .memory-warning {
        color: #EA4335;
        font-weight: bold;
    }
    .success-message {
        color: #34A853;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">AI Agent Application</h1>', unsafe_allow_html=True)
    st.markdown("A comprehensive, multi-functional AI assistant for various tasks")
    
    # Sidebar for settings and configuration
    with st.sidebar:
        st.markdown('<h2 class="section-header">Settings</h2>', unsafe_allow_html=True)
        
        # LLM Provider selection
        st.subheader("LLM Provider")
        provider_options = ["Gemini", "Mistral", "Groq", "Ollama"]
        default_provider = app.api_integration.get_default_provider().capitalize()
        selected_provider = st.selectbox(
            "Select LLM Provider",
            provider_options,
            index=provider_options.index(default_provider) if default_provider in provider_options else 0
        )
        
        # Set as default if changed
        if selected_provider.lower() != app.api_integration.get_default_provider():
            if app.api_integration.set_default_provider(selected_provider.lower()):
                st.success(f"Set {selected_provider} as default provider")
        
        # API Keys
        st.subheader("API Keys")
        
        # Gemini API Key
        gemini_key = app.api_integration.get_api_key('gemini') or ""
        gemini_key_input = st.text_input("Gemini API Key", value=gemini_key, type="password")
        if gemini_key_input != gemini_key:
            app.set_api_key('gemini', gemini_key_input)
            st.success("Gemini API key updated")
        
        # Mistral API Key
        mistral_key = app.api_integration.get_api_key('mistral') or ""
        mistral_key_input = st.text_input("Mistral API Key", value=mistral_key, type="password")
        if mistral_key_input != mistral_key:
            app.set_api_key('mistral', mistral_key_input)
            st.success("Mistral API key updated")
        
        # Groq API Key
        groq_key = app.api_integration.get_api_key('groq') or ""
        groq_key_input = st.text_input("Groq API Key", value=groq_key, type="password")
        if groq_key_input != groq_key:
            app.set_api_key('groq', groq_key_input)
            st.success("Groq API key updated")
        
        # Google Search API Key
        google_key = app.api_integration.get_api_key('google_search') or ""
        google_key_input = st.text_input("Google Search API Key", value=google_key, type="password")
        if google_key_input != google_key:
            app.set_api_key('google_search', google_key_input)
            st.success("Google Search API key updated")
        
        # Google Search Engine ID
        google_cx = app.api_integration.config.get('google_search_engine_id', "")
        google_cx_input = st.text_input("Google Search Engine ID", value=google_cx)
        if google_cx_input != google_cx:
            app.api_integration.config['google_search_engine_id'] = google_cx_input
            st.success("Google Search Engine ID updated")
        
        # Memory Management
        st.subheader("Memory Management")
        
        memory_col1, memory_col2 = st.columns(2)
        
        with memory_col1:
            if st.button("Clear All Memory", use_container_width=True):
                if app.clear_memory('all'):
                    st.markdown('<p class="success-message">All memory cleared</p>', unsafe_allow_html=True)
                else:
                    st.markdown('<p class="memory-warning">Failed to clear memory</p>', unsafe_allow_html=True)
        
        with memory_col2:
            memory_type = st.selectbox(
                "Clear Specific Memory",
                ["Select type...", "Conversations", "Web Scraping", "Data Analysis"]
            )
            
            if memory_type != "Select type..." and st.button(f"Clear {memory_type}", use_container_width=True):
                memory_map = {
                    "Conversations": "conversations",
                    "Web Scraping": "scraping",
                    "Data Analysis": "analysis"
                }
                
                if app.clear_memory(memory_map[memory_type]):
                    st.markdown(f'<p class="success-message">{memory_type} memory cleared</p>', unsafe_allow_html=True)
                else:
                    st.markdown('<p class="memory-warning">Failed to clear memory</p>', unsafe_allow_html=True)
        
        # Data Import/Export
        st.subheader("Data Import/Export")
        
        export_col1, export_col2 = st.columns(2)
        
        with export_col1:
            if st.button("Export All Data", use_container_width=True):
                export_path = os.path.join(app.data_dir, f"export_{int(time.time())}.json")
                if app.export_data(export_path):
                    with open(export_path, 'r') as f:
                        st.download_button(
                            label="Download Exported Data",
                            data=f,
                            file_name="ai_agent_data_export.json",
                            mime="application/json",
                            use_container_width=True
                        )
                else:
                    st.markdown('<p class="memory-warning">Failed to export data</p>', unsafe_allow_html=True)
        
        with export_col2:
            uploaded_file = st.file_uploader("Import Data", type="json")
            if uploaded_file is not None:
                import_path = os.path.join(app.data_dir, "import_temp.json")
                with open(import_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                
                replace_existing = st.checkbox("Replace existing data")
                
                if st.button("Import Data", use_container_width=True):
                    if app.import_data(import_path, replace_existing):
                        st.markdown('<p class="success-message">Data imported successfully</p>', unsafe_allow_html=True)
                    else:
                        st.markdown('<p class="memory-warning">Failed to import data</p>', unsafe_allow_html=True)
    
    # Main content area with tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Chat", "Web Scraping", "Data Analysis", "History"])
    
    # Tab 1: Chat Interface
    with tab1:
        st.markdown('<h2 class="section-header">Chat with AI</h2>', unsafe_allow_html=True)
        
        # Initialize chat history
        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = []
        
        # Display chat messages
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask me anything..."):
            # Add user message to chat
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)
            
            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = app.process_nlp_request(prompt, selected_provider.lower())
                    st.write(response)
            
            # Add AI response to chat
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
    
    # Tab 2: Web Scraping
    with tab2:
        st.markdown('<h2 class="section-header">Web Scraping</h2>', unsafe_allow_html=True)
        
        url_input = st.text_input("Enter URL to scrape", placeholder="https://example.com")
        
        if st.button("Scrape Website", use_container_width=False):
            if url_input:
                with st.spinner("Scraping website..."):
                    result = app.process_web_scraping_request(url_input)
                    
                    if 'error' in result:
                        st.error(result['error'])
                    else:
                        # Display results in expandable sections
                        with st.expander("Extracted Text", expanded=True):
                            st.text_area("Content", result['text'], height=300)
                        
                        with st.expander("Links", expanded=False):
                            if result['links']:
                                links_df = pd.DataFrame(result['links'])
                                st.dataframe(links_df, use_container_width=True)
                            else:
                                st.info("No links found")
                        
                        with st.expander("Tables", expanded=False):
                            if result['tables']:
                                for i, table in enumerate(result['tables']):
                                    st.subheader(f"Table {i+1}")
                                    table_df = pd.DataFrame(table)
                                    st.dataframe(table_df, use_container_width=True)
                            else:
                                st.info("No tables found")
            else:
                st.warning("Please enter a URL")
        
        # Web Search
        st.markdown('<h3 class="section-header">Web Search</h3>', unsafe_allow_html=True)
        
        search_query = st.text_input("Search query", placeholder="Enter search terms")
        num_results = st.slider("Number of results", min_value=1, max_value=10, value=5)
        
        if st.button("Search", use_container_width=False):
            if search_query:
                with st.spinner("Searching..."):
                    result = app.search_web(search_query, num_results)
                    
                    if 'error' in result:
                        st.error(result['error'])
                    elif 'items' in result:
                        for item in result['items']:
                            with st.expander(item['title'], expanded=False):
                                st.markdown(f"**Link:** [{item['link']}]({item['link']})")
                                st.markdown(f"**Snippet:** {item['snippet']}")
                    else:
                        st.info("No results found")
            else:
                st.warning("Please enter a search query")
    
    # Tab 3: Data Analysis
    with tab3:
        st.markdown('<h2 class="section-header">Data Analysis</h2>', unsafe_allow_html=True)
        
        # Data upload
        uploaded_file = st.file_uploader("Upload data file", type=["csv", "xlsx", "json"])
        
        if uploaded_file is not None:
            # Save uploaded file
            file_path = os.path.join(app.data_dir, uploaded_file.name)
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            # Load data
            with st.spinner("Loading data..."):
                success = app.data_analysis_module.load_data(file_path)
                
                if success and app.data_analysis_module.current_data is not None:
                    # Display data preview
                    st.subheader("Data Preview")
                    st.dataframe(app.data_analysis_module.current_data.head(), use_container_width=True)
                    
                    # Data summary
                    if st.button("Generate Data Summary"):
                        with st.spinner("Generating summary..."):
                            summary = app.data_analysis_module.get_data_summary()
                            
                            if 'error' in summary:
                                st.error(summary['error'])
                            else:
                                st.subheader("Data Summary")
                                
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.write(f"**Rows:** {summary['shape'][0]}")
                                    st.write(f"**Columns:** {summary['shape'][1]}")
                                
                                with col2:
                                    st.write("**Column Types:**")
                                    for col, dtype in summary['dtypes'].items():
                                        st.write(f"- {col}: {dtype}")
                                
                                st.subheader("Missing Values")
                                missing_df = pd.DataFrame.from_dict(summary['missing_values'], orient='index', columns=['Count'])
                                missing_df = missing_df.reset_index().rename(columns={'index': 'Column'})
                                st.dataframe(missing_df, use_container_width=True)
                                
                                if summary['numeric_summary']:
                                    st.subheader("Numeric Columns Summary")
                                    for col, stats in summary['numeric_summary'].items():
                                        st.write(f"**{col}:**")
                                        stats_df = pd.DataFrame.from_dict(stats, orient='index', columns=['Value'])
                                        stats_df = stats_df.reset_index().rename(columns={'index': 'Statistic'})
                                        st.dataframe(stats_df, use_container_width=True)
                    
                    # Data visualization
                    st.subheader("Data Visualization")
                    
                    # Get column names for selection
                    columns = list(app.data_analysis_module.current_data.columns)
                    numeric_columns = list(app.data_analysis_module.current_data.select_dtypes(include=[np.number]).columns)
                    
                    # Plot type selection
                    plot_type = st.selectbox(
                        "Select Plot Type",
                        ["Bar Chart", "Line Chart", "Scatter Plot", "Histogram", "Pie Chart"]
                    )
                    
                    # Column selection based on plot type
                    if plot_type in ["Scatter Plot"]:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            x_column = st.selectbox("X-axis Column", numeric_columns)
                        
                        with col2:
                            y_column = st.selectbox("Y-axis Column", numeric_columns)
                    else:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            x_column = st.selectbox("Primary Column", columns)
                        
                        with col2:
                            y_column = st.selectbox("Secondary Column (optional)", ["None"] + columns)
                            if y_column == "None":
                                y_column = None
                    
                    # Plot title
                    plot_title = st.text_input("Plot Title", f"{plot_type} of {x_column}")
                    
                    # Generate plot
                    if st.button("Generate Plot"):
                        with st.spinner("Generating plot..."):
                            plot_type_map = {
                                "Bar Chart": "bar",
                                "Line Chart": "line",
                                "Scatter Plot": "scatter",
                                "Histogram": "histogram",
                                "Pie Chart": "pie"
                            }
                            
                            save_path = os.path.join(app.data_dir, f"plot_{int(time.time())}.png")
                            
                            result = app.process_data_analysis_request(
                                app.data_analysis_module.current_data,
                                'plot',
                                {
                                    'plot_type': plot_type_map[plot_type],
                                    'x_column': x_column,
                                    'y_column': y_column,
                                    'title': plot_title,
                                    'save_path': save_path
                                }
                            )
                            
                            if 'error' in result:
                                st.error(result['error'])
                            elif 'image' in result:
                                st.image(f"data:image/png;base64,{result['image']}")
                                
                                with open(save_path, "rb") as file:
                                    btn = st.download_button(
                                        label="Download Plot",
                                        data=file,
                                        file_name=f"{plot_type.lower().replace(' ', '_')}.png",
                                        mime="image/png"
                                    )
                    
                    # Correlation analysis
                    if len(numeric_columns) > 1:
                        st.subheader("Correlation Analysis")
                        
                        if st.button("Generate Correlation Matrix"):
                            with st.spinner("Calculating correlations..."):
                                result = app.process_data_analysis_request(
                                    app.data_analysis_module.current_data,
                                    'correlation'
                                )
                                
                                if 'error' in result:
                                    st.error(result['error'])
                                else:
                                    # Convert to DataFrame for display
                                    corr_df = pd.DataFrame.from_dict(result)
                                    
                                    # Display as heatmap
                                    fig, ax = plt.subplots(figsize=(10, 8))
                                    cax = ax.matshow(corr_df, cmap='coolwarm')
                                    fig.colorbar(cax)
                                    
                                    # Set ticks and labels
                                    ax.set_xticks(range(len(corr_df.columns)))
                                    ax.set_yticks(range(len(corr_df.columns)))
                                    ax.set_xticklabels(corr_df.columns, rotation=90)
                                    ax.set_yticklabels(corr_df.columns)
                                    
                                    # Add correlation values
                                    for i in range(len(corr_df.columns)):
                                        for j in range(len(corr_df.columns)):
                                            ax.text(i, j, f"{corr_df.iloc[j, i]:.2f}", ha="center", va="center", color="black")
                                    
                                    plt.tight_layout()
                                    
                                    # Save and display
                                    save_path = os.path.join(app.data_dir, f"correlation_{int(time.time())}.png")
                                    plt.savefig(save_path)
                                    st.pyplot(fig)
                                    
                                    with open(save_path, "rb") as file:
                                        btn = st.download_button(
                                            label="Download Correlation Matrix",
                                            data=file,
                                            file_name="correlation_matrix.png",
                                            mime="image/png"
                                        )
                else:
                    st.error("Failed to load data")
    
    # Tab 4: History
    with tab4:
        st.markdown('<h2 class="section-header">History</h2>', unsafe_allow_html=True)
        
        history_type = st.radio(
            "Select History Type",
            ["Conversations", "Web Scraping", "Data Analysis"],
            horizontal=True
        )
        
        if history_type == "Conversations":
            conversations = app.get_conversation_history()
            
            if conversations:
                for conv in conversations:
                    with st.expander(f"Conversation {conv['id']} - {conv['timestamp']}", expanded=False):
                        for msg in conv['data']:
                            st.markdown(f"**{msg['role'].capitalize()}:** {msg['content']}")
            else:
                st.info("No conversation history found")
        
        elif history_type == "Web Scraping":
            scraping_results = app.get_scraping_history()
            
            if scraping_results:
                for result in scraping_results:
                    with st.expander(f"Scraping {result['id']} - {result['timestamp']} - {result['url']}", expanded=False):
                        st.markdown(f"**URL:** {result['url']}")
                        
                        with st.expander("Content Preview", expanded=False):
                            content = result['data'].get('text', '')
                            if content:
                                st.text_area("Content", content[:1000] + ("..." if len(content) > 1000 else ""), height=200)
                            else:
                                st.info("No content available")
                        
                        with st.expander("Links", expanded=False):
                            links = result['data'].get('links', [])
                            if links:
                                links_df = pd.DataFrame(links)
                                st.dataframe(links_df, use_container_width=True)
                            else:
                                st.info("No links found")
            else:
                st.info("No web scraping history found")
        
        elif history_type == "Data Analysis":
            analysis_results = app.get_analysis_history()
            
            if analysis_results:
                for result in analysis_results:
                    with st.expander(f"Analysis {result['id']} - {result['timestamp']} - {result['description']}", expanded=False):
                        st.markdown(f"**Description:** {result['description']}")
                        
                        # Display based on result type
                        if 'image' in result['data']:
                            st.image(f"data:image/png;base64,{result['data']['image']}")
                        elif 'error' in result['data']:
                            st.error(result['data']['error'])
                        else:
                            st.json(result['data'])
            else:
                st.info("No data analysis history found")

if __name__ == "__main__":
    main()
