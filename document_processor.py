import os
import fitz  # PyMuPDF
from supabase import create_client, Client
import streamlit as st
from sentence_transformers import SentenceTransformer
import numpy as np
import requests
import json

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

# Initialize Sentence Transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Function to process the uploaded document and create chunks
def process_document(file, file_type):
    if file_type == "pdf":
        content = extract_text_from_pdf(file)
    else:
        try:
            content = file.read().decode("utf-8")
        except UnicodeDecodeError:
            try:
                content = file.read().decode("latin1")
            except UnicodeDecodeError as e:
                st.error(f"Error decoding file: {e}")
                return []
    chunks = [content[i:i+500] for i in range(0, len(content), 500)]
    return chunks

# Function to extract text from PDF
def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Function to generate embeddings for chunks
def generate_embeddings(chunks):
    embeddings = model.encode(chunks)
    return embeddings

# Function to save chunks and embeddings to Supabase
def save_chunks_to_supabase(chunks, embeddings, project_name):
    try:
        for chunk, embedding in zip(chunks, embeddings):
            response = supabase.table("messages").insert([{
                "project": project_name,
                "role": "document",
                "content": chunk,
                "embedding": embedding.tolist()
            }]).execute()
        return True
    except Exception as e:
        st.error(f"Error saving document chunks: {e}")
        return False

# File uploader for document upload
def upload_document():
    uploaded_file = st.sidebar.file_uploader("Upload Document", type=["txt", "pdf", "docx"])
    if uploaded_file and st.session_state["current_project"]:
        file_type = uploaded_file.name.split(".")[-1]
        chunks = process_document(uploaded_file, file_type)
        if chunks:
            embeddings = generate_embeddings(chunks)
            if save_chunks_to_supabase(chunks, embeddings, st.session_state["current_project"]):
                st.sidebar.success("Document uploaded and processed successfully.")

# Function to retrieve relevant chunks from Supabase
def retrieve_relevant_chunks(question, project_name):
    try:
        response = supabase.table("messages") \
            .select("content, embedding") \
            .eq("project", project_name) \
            .execute()

        messages = response.data
        if not messages:
            return []

        # Generate embedding for the question
        question_embedding = model.encode([question])[0]

        # Calculate cosine similarity between question embedding and document embeddings
        similarities = []
        for msg in messages:
            embedding = np.array(msg["embedding"])
            #debug Check if embedding is not None
            if embedding is not None: 
                similarity = np.dot(question_embedding, embedding) / (np.linalg.norm(question_embedding) * np.linalg.norm(embedding))
                similarities.append((similarity, msg["content"]))

        # Sort by similarity and return the most relevant chunks
        similarities.sort(reverse=True, key=lambda x: x[0])
        relevant_chunks = [content for _, content in similarities[:5]]
        return relevant_chunks
    except Exception as e:
        st.error(f"An error occurred while retrieving relevant chunks: {e}")
        return []

# Function to generate answer using DeepSeek API
def generate_answer(question, relevant_chunks):
    context = [{"role": "user", "content": question}] + [{"role": "system", "content": chunk} for chunk in relevant_chunks]
    try:
        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            data=json.dumps({
                "messages": context,
                "model": "deepseek-chat",
                "max_tokens": 2048
            })
        )
        
        if response.status_code == 200:
            response_data = response.json()
            choices = response_data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "No response received.")
            else:
                return "No valid choices in response."
        else:
            return f"API Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"An error occurred while calling the API: {e}"