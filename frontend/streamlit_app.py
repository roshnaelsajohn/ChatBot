"""
Streamlit Chatbot Frontend
A modern chat interface with file upload and RAG capabilities.
"""

import streamlit as st
import streamlit as st
import requests
import os

# Configuration
# Use environment variable for Docker compatibility, default to localhost for local run
API_BASE_URL = os.environ.get("API_BASE_URL", "http://127.0.0.1:5000/api")

# Page Configuration
st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Smooch+Sans:wght@100..900&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Smooch Sans', sans-serif;
    }

    /* Main container - Deep Dark Flat Background */
    .stApp {
        background-color: #0F1116;
    }
    
    .main {
        background-color: #0F1116;
    }
    
    /* Headers with Smooch Sans */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Smooch Sans', sans-serif;
        font-weight: 600;
        color: #E6EDF3 !important;
    }
    
    /* Chat message styling - Minimalist */
    .chat-message {
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
        border: 1px solid #30363D;
        background-color: #161B22;
    }
    
    .user-message {
        background-color: #1F2937; /* Slightly lighter for user */
        color: #E6EDF3;
        margin-left: 20%;
        border: 1px solid #374151;
    }
    
    .bot-message {
        background-color: #0F1116; /* Darker for bot */
        color: #C9D1D9;
        margin-right: 20%;
        border: 1px solid #30363D;
    }
    
    .source-tag {
        background-color: #21262D;
        color: #8B949E;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
        margin-top: 8px;
        display: inline-block;
        border: 1px solid #30363D;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #010409; /* Very dark sidebar */
        border-right: 1px solid #30363D;
    }
    
    /* Stats card */
    .stats-card {
        background-color: #161B22;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        color: #E6EDF3;
        border: 1px solid #30363D;
    }
    
    /* Button styling - Minimalist Outline */
    .stButton > button {
        background-color: transparent;
        color: #58A6FF;
        border: 1px solid #30363D;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-family: 'Smooch Sans', sans-serif;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background-color: #1F242C;
        border-color: #58A6FF;
        color: #58A6FF;
        box-shadow: none;
    }
    
    /* Title styling */
    h1 {
        background: none;
        -webkit-text-fill-color: #E6EDF3;
        text-align: center;
        font-weight: 800;
        letter-spacing: 1px;
    }
    
    /* Input field styling */
    .stTextInput > div > div > input {
        background-color: #0D1117;
        color: #E6EDF3;
        border: 1px solid #30363D;
        border-radius: 6px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #58A6FF;
        box-shadow: 0 0 0 1px #58A6FF;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []


def get_collection_stats():
    """Fetch collection statistics from the API."""
    try:
        response = requests.get(f"{API_BASE_URL}/stats", timeout=5)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        pass
    return {"total_chunks": 0}


def publish_document(file):
    """Upload and publish a document to the vector database."""
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        response = requests.post(f"{API_BASE_URL}/publish", files=files, timeout=300)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"success": False, "message": f"Connection error: {str(e)}"}


def send_chat_message(message, chat_mode="document", synthesize_response=True):
    """Send a message to the chat API and get a response."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={
                "message": message, 
                "n_results": 10, 
                "chat_mode": chat_mode,
                "synthesize_response": synthesize_response
            },
            timeout=300
        )
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"success": False, "message": f"Connection error: {str(e)}"}


def clear_collection():
    """Clear all documents from the collection."""
    try:
        response = requests.post(f"{API_BASE_URL}/clear", timeout=10)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"success": False, "message": f"Connection error: {str(e)}"}


def get_file_list():
    """Fetch list of uploaded files from the API."""
    try:
        response = requests.get(f"{API_BASE_URL}/files", timeout=5)
        if response.status_code == 200:
            return response.json().get("files", [])
    except requests.exceptions.RequestException:
        pass
    return []

def main():
    """Main application function."""
    init_session_state()
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 📁 Document Upload")
        st.markdown("---")
        
        # Fetch current files from backend
        current_files = get_file_list()
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["pdf", "txt", "docx"],
            help="Upload PDF, TXT, or DOCX files"
        )
        
        # Publish button
        if uploaded_file is not None:
            st.markdown(f"**Selected:** {uploaded_file.name}")
            
            # Check for duplicates
            if uploaded_file.name in current_files:
                st.warning(f"⚠️ File '{uploaded_file.name}' already exists in the knowledge base!")
            else:
                if st.button("🚀 Publish to Knowledge Base", use_container_width=True):
                    with st.spinner("Processing document..."):
                        result = publish_document(uploaded_file)
                        
                    if result.get("success"):
                        st.success(f"✅ {result.get('message', 'Document published!')}")
                        st.info(f"📊 Chunks added: {result.get('chunks_added', 0)}")
                        st.session_state.uploaded_files.append(uploaded_file.name)
                        st.rerun() # Rerun to update file list
                    else:
                        st.error(f"❌ {result.get('message', 'Failed to publish document')}")
        
        st.markdown("---")
        
        # Collection stats
        st.markdown("## 📊 Knowledge Base Stats")
        stats = get_collection_stats()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Chunks", stats.get("total_chunks", 0))
        with col2:
            st.metric("Documents", len(current_files))
            
        # Display file list
        if current_files:
            with st.expander("📄 Uploaded Documents"):
                for f in current_files:
                    st.text(f"• {f}")
        
        st.markdown("---")
        
        # Clear collection button
        if st.button("🗑️ Clear Knowledge Base", use_container_width=True):
            result = clear_collection()
            if result.get("success"):
                st.success("Knowledge base cleared!")
                st.session_state.uploaded_files = []
                st.session_state.messages = []
                st.rerun()
            else:
                st.error(f"Failed: {result.get('message', 'Unknown error')}")
        
        # Clear chat button
        if st.button("💬 Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
        # Mode selection for chat
        st.markdown("## ⚙️ Chat Mode")
        mode = st.radio(
            "Select capability:",
            ["📚 Ask Documents (RAG)", "🌐 Web Search", "🧠 Ask General Knowledge (LLM)"],
            index=0,
            help="**Ask Documents**: Answers based ONLY on your uploaded files.\n**Web Search**: Search the internet.\n**Ask General Knowledge**: Bypasses documents and uses the AI's own knowledge."
        )
        
        # Map UI selection to API mode
        chat_mode = "document"
        if "Web Search" in mode:
            chat_mode = "web"
        elif "General Knowledge" in mode:
            chat_mode = "llm"

        if chat_mode == "llm":
            synthesize_response = True # Always true for pure LLM
        else:
            synthesize_response = st.toggle(
                "Synthesize Answer with AI",
                value=True,
                help="**ON**: AI reads documents and writes an answer (Uses 1 Credit).\n**OFF**: Shows raw text chunks found in documents (Saves Credits)."
            )
    
    # Main chat area
    st.markdown("# 🤖 RAG Chatbot")
    st.markdown("*Ask questions about your uploaded documents*")
    st.markdown("---")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("sources"):
                st.caption(f"📚 Sources: {', '.join(message['sources'])}")
    
    # Chat input
    if prompt := st.chat_input("Ask a question..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = send_chat_message(prompt, chat_mode, synthesize_response)
            
            if response.get("success"):
                answer = response.get("answer", "I couldn't find relevant information.")
                sources = response.get("sources", [])
                
                # Show source tag in markdown (if backend sends it in answer, we can display, but we also have caption)
                st.markdown(answer)
                if sources:
                    st.caption(f"📚 Sources: {', '.join(sources)}")
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })
            else:
                error_msg = f"⚠️ Error: {response.get('message', 'Unknown error')}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })
    
    # Welcome message if no messages
    if not st.session_state.messages:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; color: #a0aec0;">
            <h3>👋 Welcome to the RAG Chatbot!</h3>
            <p>To get started:</p>
            <ol style="text-align: left; max-width: 400px; margin: 0 auto;">
                <li>Upload a document using the sidebar (PDF, TXT, or DOCX)</li>
                <li>Click "Publish to Knowledge Base" to process it</li>
                <li>Ask questions about your documents in the chat!</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
