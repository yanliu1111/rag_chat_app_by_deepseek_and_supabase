# Build RAG Chat App by Deepseek V3 🐋 and Supabase ⚡

## Overview

Build RAG (Retrieval-Augmented Generation) Chat App" by integrating Deepseek V3 and Supabase, built base on a simple Streamlit application that provides an interactive user interface with a sidebar for navigation and content display. Separate projects with unique chats.

## Purpose of the Project

- 🚀 Building & Learning: Hands-on experience with modern AI and database integration
- 🧠 Understand DeepSeek V3: Explore its capabilities and use cases
- 🔍 RAG (Retrieval-Augmented Generation) Integration: Implement RAG in a chat application
- ⚡ Streamlit + DeepSeek V3 + Supabase: Develop and deploy a fully functional AI-powered app
- 🐍 Python Feature Practice: Utilize various Python features with plans for unit testing at the end

## Technologies

- Python 3.10
- Packages `pip install streamlit requests python-dotenv supabase`

## Features

- Sidebar for navigation
- Main content area for displaying information

```bash
Build-RAG-Chat-App/
├── .env
├── app.py                # Main Streamlit app file
├── document_processor.py # langchain.text_splitter
├── requirements.txt      # To list all Python dependencies
├── .gitignore            # To ignore .env and venv directories
└── README.md             # Project documentation

```

## Installation

To run this application, you need to have Python installed on your machine. Follow these steps to set up the project:

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/rag-2.0.git
   cd rag-2.0
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Create Environment Variables (.env):

```
DEEPSEEK_API_KEY=your_deepseek_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_API_KEY=your_supabase_api_key
YOUR_SITE_URL=http://localhost:8501
YOUR_SITE_NAME=your_site_name
```

## Running the Application

To start the Streamlit application, run the following command in your terminal:

```
streamlit run app.py
```
