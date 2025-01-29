# Build RAG Chat App by Supabase and Deepseek V3

## Overview

Build RAG (Retrieval-Augmented Generation) Chat App" by integrating Deepseek V3 and Supabase, built base on a simple Streamlit application that provides an interactive user interface with a sidebar for navigation and content display. Separate projects with unique chats.

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
streamlit run src/app.py
```

## Usage

Once the application is running, you can interact with the sidebar to navigate through different sections of the app. The main content area will update based on your selections.

## Contributing

Feel free to submit issues or pull requests if you have suggestions or improvements for the application.

## License

This project is licensed under the MIT License.
