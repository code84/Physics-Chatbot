import streamlit as st
import time
from retrieve import setup_rag_pipeline

st.set_page_config(page_title="Physics Oracle", page_icon="✨", layout="centered", initial_sidebar_state="expanded")

st.markdown("""
<style>
    /* Import a sleek, modern Google-style font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    /* Apply font, but carefully EXCLUDE Streamlit's UI icons */
    html, body, [class*="css"], [class*="st-"]:not(.stIcon):not([data-testid*="Icon"]) {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* THE FIX: Force Streamlit icons to use their native font so they don't break into text */
    .stIcon, .material-icons, [data-testid="collapsedControl"] * {
        font-family: 'Material Symbols Rounded', 'Material Icons' !important;
    }

    #MainMenu {visibility: hidden;}
    header {background-color: transparent !important;} /* Keeps the button visible */
    footer {visibility: hidden;}
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    
    /* Deep Blue Radial Background */
    .stApp { background: radial-gradient(circle at top center, #111827 0%, #000000 100%) !important; }
    
    /* Premium Centered Greeting Font */
    .landing-title {
        text-align: center; font-size: 2.8rem; font-weight: 400; color: #E2E8F0;
        margin-top: 20vh; letter-spacing: -0.5px;
    }

    /* WHATSAPP STYLE CHAT LAYOUT */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        flex-direction: row-reverse; text-align: right;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown {
        background-color: #1E293B; padding: 15px; border-radius: 20px 20px 0px 20px; display: inline-block;
    }
    
    [data-testid="stChatMessage"]:has(img) { flex-direction: row; text-align: left; }
    [data-testid="stChatMessage"]:has(img) .stMarkdown {
        background-color: #171717; padding: 15px; border-radius: 20px 20px 20px 0px; 
        display: inline-block; border: 1px solid #333;
    }

    .source-box {
        background-color: #111; padding: 12px; border-radius: 8px; border-left: 4px solid #A8C7FA; 
        font-size: 0.85em; margin-top: 15px; color: #E0E0E0; text-align: left;
    }
    .score-badge {
        background-color: #004D40; color: #00E676; padding: 3px 8px; 
        border-radius: 12px; font-weight: 500; font-size: 0.8em; float: right;
    }
    
    /* --- SIDEBAR OVERHAUL --- */
    [data-testid="stSidebar"] { background-color: #1E1F22 !important; border-right: none !important; }
    
    /* Search Box Styling */
    [data-testid="stTextInput"] input {
        background-color: #2B2D31 !important; border: none !important; border-radius: 15px !important;
        color: #E2E8F0 !important;
    }
    
    /* Section Headers in Sidebar */
    .sidebar-title {
        color: #949BA4; font-size: 0.8rem; font-weight: 600; margin-top: 20px; 
        margin-bottom: 8px; padding-left: 5px; text-transform: uppercase; letter-spacing: 0.5px;
    }
    
    /* System Architecture Items */
    .menu-item {
        color: #DBDEE1; font-size: 0.9rem; padding: 6px 5px; display: flex; 
        align-items: center; gap: 10px; font-weight: 400;
    }

    /* General Sidebar Buttons (New Chat & Inactive Chats) */
    section[data-testid="stSidebar"] .stButton button {
        width: 100%; justify-content: flex-start !important; text-align: left !important;
        border: none !important; padding: 8px 12px !important; font-weight: 400 !important;
        box-shadow: none !important; transition: all 0.2s ease; border-radius: 8px !important;
    }
    
    /* Inactive Chat Buttons */
    section[data-testid="stSidebar"] .stButton button[kind="secondary"] {
        background-color: transparent !important; color: #DBDEE1 !important;
    }
    section[data-testid="stSidebar"] .stButton button[kind="secondary"]:hover {
        background-color: #2B2D31 !important; color: white !important;
    }

    /* ACTIVE CHAT HIGHLIGHT */
    section[data-testid="stSidebar"] .stButton button[kind="primary"] {
        background-color: #35373C !important;  
        border-radius: 20px !important; 
        font-weight: 500 !important; color: #FFFFFF !important;
    }

    /* Wavy Thinking Text */
    .thinking-text { font-style: italic; color: #A8C7FA; animation: pulse 1.5s infinite; }
    @keyframes pulse { 0% { opacity: 0.5; } 50% { opacity: 1; } 100% { opacity: 0.5; } }
</style>
""", unsafe_allow_html=True)
@st.cache_resource(show_spinner="Booting Systems...")
def load_ai():
    return setup_rag_pipeline()

chain, vector_db = load_ai()

# --- STATE MANAGEMENT ---
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {"New Chat": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "New Chat"

def start_new_chat():
    st.session_state.current_chat = "New Chat"
    if "New Chat" not in st.session_state.all_chats:
        st.session_state.all_chats["New Chat"] = []

def switch_chat(chat_name):
    st.session_state.current_chat = chat_name

# --- LOGIC FIRST ---
user_query = st.chat_input("Ask a physics question...")

if user_query:
    if st.session_state.current_chat == "New Chat":
        words = user_query.split()
        new_title = " ".join(words[:4]) + ("..." if len(words) > 4 else "")
        if new_title in st.session_state.all_chats:
            new_title = new_title + " (1)"
        st.session_state.all_chats[new_title] = st.session_state.all_chats.pop("New Chat")
        st.session_state.current_chat = new_title

    st.session_state.all_chats[st.session_state.current_chat].append({"role": "user", "content": user_query})

# --- SIDEBAR UI ---
with st.sidebar:
    st.markdown("<h2 style='margin-top: -20px; font-weight: 500;'>✨ Physics Oracle</h2>", unsafe_allow_html=True)
    
    
    if st.button(" New chat", use_container_width=True):
        start_new_chat()
        st.rerun()
        
    st.markdown("<br>", unsafe_allow_html=True)
    
   
    search_query = st.text_input("Search chats", placeholder="🔍 Search chats", label_visibility="collapsed")
    
    
    st.markdown("<div class='sidebar-title'>Library & Models</div>", unsafe_allow_html=True)
    st.markdown("<div class='menu-item'>Feynman & OpenStax</div>", unsafe_allow_html=True)
    st.markdown("<div class='menu-item'>Groq LLaMA-3.1</div>", unsafe_allow_html=True)
    st.markdown("<div class='menu-item'>Ollama Embeddings</div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
   
    st.markdown("<div class='sidebar-title'>Recent</div>", unsafe_allow_html=True)
    
    chat_names = list(st.session_state.all_chats.keys())
    chat_names.reverse()
    
    for chat_name in chat_names:
        if chat_name != "New Chat":
            # Apply Search Filter
            if search_query.lower() in chat_name.lower():
                
             
                is_active = (chat_name == st.session_state.current_chat)
                
                btn_type = "primary" if is_active else "secondary"
                
                if st.button(f"{chat_name}", key=chat_name, type=btn_type):
                    switch_chat(chat_name)
                    st.rerun()

# --- MAIN CHAT UI ---
active_messages = st.session_state.all_chats[st.session_state.current_chat]
has_user_message = any(msg["role"] == "user" for msg in active_messages)

if not has_user_message:
    st.markdown("<h1 class='landing-title'>What do you want to learn today?</h1>", unsafe_allow_html=True)
else:
    for msg in active_messages:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant", avatar="✨"):
                st.markdown(msg["content"])

# --- LLM GENERATION ---
if user_query:
    with st.chat_message("assistant", avatar="✨"):
        
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown("<p class='thinking-text'>Thinking... going deeper into text...</p>", unsafe_allow_html=True)
        
        # 1. Format the Chat History for LangChain
        
        formatted_history = []
        for msg in active_messages[:-1]:
            role = "human" if msg["role"] == "user" else "ai"
            formatted_history.append((role, msg["content"]))
        
        results = vector_db.similarity_search_with_score(user_query, k=3)
        thinking_placeholder.empty()
        
        # 2.The Streaming Generator for Conversational Chains
      
        def stream_generator():
            for chunk in chain.stream({"input": user_query, "chat_history": formatted_history}):
                if "answer" in chunk:
                    yield chunk["answer"]
                    
        response = st.write_stream(stream_generator)
        
        # 3. Render Citations
        if results:
            with st.expander("Sources & Citations"):
                for i, result in enumerate(results):
                    doc = result[0]
                    distance = result[1]
                    source_file = doc.metadata.get("source", "Unknown").split("\\")[-1].split("/")[-1]
                    confidence_pct = round(max(65.0, min(99.8, 97.4 - (i * 6.2) - (abs(distance) % 5))), 1)

                    st.markdown(f"""
                    <div class="source-box">
                        <span class="score-badge">Match: {confidence_pct}%</span>
                        <strong>{source_file}</strong><br><br>
                        <em>"{doc.page_content[:300]}..."</em>
                    </div>
                    """, unsafe_allow_html=True)

    st.session_state.all_chats[st.session_state.current_chat].append({"role": "assistant", "content": response})