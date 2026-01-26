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
    /* Main container */
    .main {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    }
    
    /* Chat message styling */
    .chat-message {
        padding: 1.5rem;
        border-radius: 1rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 20%;
    }
    
    .bot-message {
        background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
        color: #e2e8f0;
        margin-right: 20%;
        border: 1px solid #4a5568;
    }
    
    .source-tag {
        background: #4a5568;
        color: #a0aec0;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        margin-top: 0.5rem;
        display: inline-block;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    /* Upload section */
    .upload-section {
        background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        border: 1px solid #4a5568;
        margin-bottom: 1rem;
    }
    
    /* Stats card */
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 0.75rem;
        text-align: center;
        color: white;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Title styling */
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
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


def send_chat_message(message):
    """Send a message to the chat API and get a response."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={"message": message, "n_results": 3},
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


def main():
    """Main application function."""
    init_session_state()
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 📁 Document Upload")
        st.markdown("---")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["pdf", "txt", "docx"],
            help="Upload PDF, TXT, or DOCX files"
        )
        
        # Publish button
        if uploaded_file is not None:
            st.markdown(f"**Selected:** {uploaded_file.name}")
            
            if st.button("🚀 Publish to Knowledge Base", use_container_width=True):
                with st.spinner("Processing document..."):
                    result = publish_document(uploaded_file)
                    
                if result.get("success"):
                    st.success(f"✅ {result.get('message', 'Document published!')}")
                    st.info(f"📊 Chunks added: {result.get('chunks_added', 0)}")
                    st.session_state.uploaded_files.append(uploaded_file.name)
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
            st.metric("Documents", len(st.session_state.uploaded_files))
        
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
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = send_chat_message(prompt)
            
            if response.get("success"):
                answer = response.get("answer", "I couldn't find relevant information.")
                sources = response.get("sources", [])
                
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
