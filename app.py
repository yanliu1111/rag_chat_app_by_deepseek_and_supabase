import streamlit as st
import requests
import json
from dotenv import load_dotenv
import os
from supabase import create_client, Client
from document_processor import upload_document, retrieve_relevant_chunks, generate_answer  # Import the functions
from sentence_transformers import SentenceTransformer
import numpy as np

# Load environment variables from .env file
load_dotenv()

# Load API keys and URLs
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_URL = "https://api.deepseek.com/chat/completions"
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

# Initialize Sentence Transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Streamlit UI
st.set_page_config(page_title="RAG 2.0", page_icon="🤖", layout="wide")

# Sidebar for project management
st.sidebar.title("Projects")
if "projects" not in st.session_state:
    st.session_state["projects"] = []

# Dropdown to select or add a project
projects = st.sidebar.selectbox("Select a Project", ["Add New Project"] + st.session_state["projects"])

# Store the current project in session state
st.session_state["current_project"] = projects if projects != "Add New Project" else None

# Add or delete projects
if projects == "Add New Project":
    new_project_name = st.sidebar.text_input("Enter new project name:")
    if st.sidebar.button("Add Project"):
        if new_project_name:
            st.session_state["projects"].append(new_project_name)
            st.session_state[new_project_name] = []  # Initialize chat history
            st.session_state["current_project"] = new_project_name  # Set as current project
            st.rerun()
else:
    if st.sidebar.button("Delete Project"):
        if delete_project(projects):
            st.session_state["projects"].remove(projects)
            del st.session_state[projects]
            st.rerun()

# Call the upload_document function to handle document uploads
upload_document()

# Function to load chat history from Supabase
def load_chat_history(project_name):
    try:
        response = supabase.table("messages") \
            .select("*") \
            .eq("project", project_name) \
            .order("timestamp") \
            .execute()

        # Debugging: Check the raw response
        print(f"Load Chat History Response: {response}")  # Add this line to see the raw response
        
        messages = response.data
        if not messages:
            print(f"No messages found for project: {project_name}")  # Debugging
            return []  # Return empty list if no messages are found
        
        return [{"role": msg["role"], "content": msg["content"]} for msg in messages]
    except Exception as e:
        st.error(f"An error occurred while loading chat history: {e}")
        return []

# Function to save chat history to Supabase
def save_chat_history(role, content):
    try:
        if not st.session_state["current_project"]:
            st.error("No project selected.")
            return False

        response = supabase.table("messages").insert([{
            "project": st.session_state["current_project"],
            "role": role,
            "content": content
        }]).execute()

        print(f"Save Chat Response: {response}")  # Debugging

        if response.data:
            return True
        return False
    except Exception as e:
        st.error(f"Error saving chat message: {e}")
        return False

# Function to delete a project from Supabase
def delete_project(project_name):
    try:
        supabase.table("messages") \
            .delete() \
            .eq("project", project_name) \
            .execute()
        return True
    except Exception as e:
        st.error(f"Error deleting project: {e}")
        return False

# Main content
if st.session_state["current_project"]:
    st.title(f"Project: {st.session_state['current_project']}")
    
    # Load chat history from Supabase if not already loaded
    if st.session_state["current_project"] not in st.session_state:
        st.session_state[st.session_state["current_project"]] = load_chat_history(st.session_state["current_project"])

    # User input for chat
    user_input = st.text_input("Enter your prompt:")
    
    if user_input:
        project_context = st.session_state.get(st.session_state["current_project"], [])
        if not project_context:
            project_context = [{"role": "system", "content": "You are a helpful assistant."}]
        
        # Retrieve relevant chunks from Supabase
        relevant_chunks = retrieve_relevant_chunks(user_input, st.session_state["current_project"])
        
        # Generate answer using DeepSeek API
        response_text = generate_answer(user_input, relevant_chunks)
        
        # Save to Supabase
        save_chat_history("user", user_input)
        save_chat_history("assistant", response_text)

        # Update session state
        st.session_state[st.session_state["current_project"]].append({"role": "user", "content": user_input})
        st.session_state[st.session_state["current_project"]].append({"role": "assistant", "content": response_text})

        st.subheader("Response from DeepSeek AI:")
        st.write(response_text)

    # Display chat history
    st.subheader("Chat History")
    for message in st.session_state[st.session_state["current_project"]]:
        st.write(f"{message['role'].capitalize()}: {message['content']}")
else:
    st.title("Welcome to RAG 2.0!")
    st.write("This app connects to DeepSeek AI.")