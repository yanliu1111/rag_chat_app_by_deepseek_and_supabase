import streamlit as st
import requests
import json
from dotenv import load_dotenv
import os
from supabase import create_client, Client

# Load environment variables from .env file
load_dotenv()

# Load API keys and URLs
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_URL = "https://api.deepseek.com/chat/completions"
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

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

# Function to load chat history from Supabase
def load_chat_history(project_name):
    try:
        response = supabase.table("messages") \
            .select("*") \
            .eq("project", project_name) \
            .order("timestamp", ascending=True) \
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

# Add or delete projects
if projects == "Add New Project":
    new_project_name = st.sidebar.text_input("Enter new project name:")
    if st.sidebar.button("Add Project"):
        if new_project_name:
            st.session_state["projects"].append(new_project_name)
            st.session_state[new_project_name] = []
            st.rerun()
else:
    if st.sidebar.button("Delete Project"):
        if delete_project(projects):
            st.session_state["projects"].remove(projects)
            del st.session_state[projects]
            st.rerun()

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
        
        # Debugging: Check the project context
        print(f"Project Context for {st.session_state['current_project']}: {project_context}")  # Debugging

        # Call DeepSeek API
        try:
            response = requests.post(
                API_URL,
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                data=json.dumps({
                    "messages": project_context + [{"content": user_input, "role": "user"}],
                    "model": "deepseek-chat",
                    "max_tokens": 2048
                })
            )
            
            # Debug: Print raw response
            print(f"Response Status Code: {response.status_code}")
            print(f"Response Text: {response.text}")
            
            if response.status_code == 200:
                if response.text.strip():  # Check if the response body is not empty
                    try:
                        response_data = response.json()
                        response_text = response_data.get("choices", [{}])[0].get("message", {}).get("content", "No response received.")
                        
                        # Save to Supabase
                        save_chat_history("user", user_input)
                        save_chat_history("assistant", response_text)

                        # Update session state
                        st.session_state[st.session_state["current_project"]].append({"role": "user", "content": user_input})
                        st.session_state[st.session_state["current_project"]].append({"role": "assistant", "content": response_text})

                        st.subheader("Response from DeepSeek AI:")
                        st.write(response_text)
                    except json.JSONDecodeError as e:
                        st.error(f"Error decoding JSON: {e}. Raw response: {response.text}")
                else:
                    st.error("Empty response body received.")
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")
        
        except json.JSONDecodeError as e:
            st.error(f"Error decoding JSON: {e}. Raw response: {response.text}")
        except Exception as e:
            st.error(f"An error occurred while calling the API: {e}")

    # Display chat history
    st.subheader("Chat History")
    for message in st.session_state[st.session_state["current_project"]]:
        st.write(f"{message['role'].capitalize()}: {message['content']}")
else:
    st.title("Welcome to RAG 2.0!")
    st.write("This app connects to DeepSeek AI.")
