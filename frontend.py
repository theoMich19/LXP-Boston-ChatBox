import streamlit as st
import os
from dotenv import load_dotenv

from langchain.memory import ConversationBufferMemory
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

from backend import get_backend_instance

load_dotenv('config.env')

INITIAL_MESSAGE = "🎬 Good evening and welcome to your private screening room! I'm your personal film critic, ready to explore the fascinating world of cinema with you. What would you like to discover tonight?"
CHAT_INPUT_PLACEHOLDER = "🎭 Good evening! Which cinematic masterpiece would you like to discuss tonight?"

def setup_page():
    st.set_page_config(
        page_title="🎬 CinéBot - Your AI Film Critic",
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.markdown("""
        <style>
        :root {
            --bordeaux-dark: #4A0E0E;
            --bordeaux-medium: #722F37;
            --bordeaux-light: #8B4B5C;
            --wine-red: #9C1A1C;
            --burgundy: #800020;
            --cream: #F5F5DC;
            --gold: #D4AF37;
            --champagne: #F7E7CE;
        }
        
        .stApp * {
            color: white !important;
        }
        
        .stApp {
            background: 
                radial-gradient(ellipse at top, rgba(138, 75, 92, 0.08) 0%, transparent 60%),
                linear-gradient(135deg, 
                    var(--bordeaux-dark) 0%, 
                    #2d1417 25%, 
                    var(--bordeaux-medium) 50%, 
                    #1a0d0f 75%, 
                    var(--bordeaux-dark) 100%);
            background-attachment: fixed;
        }
        
        .main-title {
            font-size: 4.2rem;
            font-weight: 900;
            background: linear-gradient(45deg, 
                var(--gold) 0%, 
                var(--champagne) 25%, 
                var(--wine-red) 50%, 
                var(--gold) 75%, 
                var(--champagne) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 1.5rem;
            font-family: 'Georgia', 'Times New Roman', serif;
        }
        
        .subtitle {
            text-align: center;
            color: var(--champagne);
            font-size: 1.5rem;
            margin-bottom: 2.5rem;
            font-style: italic;
            font-family: 'Georgia', serif;
        }
        
        .info-card {
            background: linear-gradient(145deg, 
                rgba(114, 47, 55, 0.35) 0%, 
                rgba(156, 26, 28, 0.25) 30%, 
                rgba(138, 75, 92, 0.3) 70%, 
                rgba(74, 14, 14, 0.4) 100%);
            padding: 2.5rem;
            border-radius: 25px;
            border: 3px solid var(--gold);
            margin: 1.5rem 0;
            color: var(--champagne);
            min-height: 280px;
            height: 280px;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
        }
        
        .sidebar-header {
            color: var(--gold);
            font-size: 1.7rem;
            font-weight: bold;
            margin: 1.5rem 0;
            text-align: center;
            font-family: 'Georgia', serif;
        }
        </style>
    """, unsafe_allow_html=True)

def setup_main_page():
    st.markdown('<h1 class="main-title">🎭 CinéBot 🎬</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">✨ Your Private Critic in this Exclusive Cinema Lounge ✨</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        st.markdown("""
        <div class="info-card">
            <h3><span class="feature-icon">🎭</span>Cinematic Expertise</h3>
            <p>In-depth analysis by a seasoned critic, in the intimate setting of your private lounge.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="info-card">
            <h3><span class="feature-icon">🎬</span>Exclusive Archives</h3>
            <p>Privileged access to the treasures of the seventh art: timeless classics and contemporary masterpieces.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="info-card">
            <h3><span class="feature-icon">🍿</span>Tailor-Made Programming</h3>
            <p>Personalized advice for your movie nights, like a dedicated cultural concierge.</p>
        </div>
        """, unsafe_allow_html=True)

def setup_sidebar():
    with st.sidebar:
        st.markdown('<h2 class="sidebar-header">🎪 Private Lounge</h2>', unsafe_allow_html=True)

        with st.expander("🎯 Your Cultural Menu", expanded=True):
            st.markdown("""
            🎭 **Welcome to your exceptional lounge!**
            
            🍷 Your cultural sommelier offers:
            
            • **🎬 Archive Exploration** - Journey through cinema history
            • **🎭 Art Criticism** - In-depth aesthetic and narrative analysis  
            • **👑 Legend Portraits** - Biographies of cinema masters
            • **💎 Industry Secrets** - Behind-the-scenes and exclusive anecdotes
            """)

        with st.expander("🎬 Cultural Suggestions", expanded=False):
            st.markdown("""
            **🍷 Lounge conversations:**
            
            • *"Analyze Stanley Kubrick's visionary work"*
            • *"Recommend a film in the spirit of Casablanca"*
            • *"Tell me about the influence of the French New Wave"*
            • *"What are Hitchcock's narrative secrets?"*
            """)

        with st.expander("🎭 Our Exclusive Collection"):
            genres = [
                "🎭 Auteur Drama", "😂 Sophisticated Comedy", "🔫 Classic Film Noir",
                "👻 Poetic Fantasy", "🚀 Intellectual Science Fiction", "💕 Timeless Romance"
            ]

            for genre in genres:
                if st.button(genre, key=f"genre_{genre}"):
                    genre_clean = genre.split(' ', 1)[1] if ' ' in genre else genre
                    st.session_state.suggested_input = f"Select the most beautiful {genre_clean} for an exceptional evening"

        st.markdown("---")

        add_reset_button()

        st.markdown("""
        ---
        <div style="text-align: center; color: var(--gold); font-family: Georgia, serif;">
            <small>🎭 Your Personal Critic • AI Excellence</small><br>
            <small>🍷 The Art of Cinema at Your Service 🎬</small>
        </div>
        """, unsafe_allow_html=True)

def add_reset_button():
    if st.button("🎬 New Screening", help="Start a new cinematographic session"):
        if "messages" in st.session_state:
            st.session_state.messages = []

        if "memory" in st.session_state:
            st.session_state.memory.clear()

        if "steps" in st.session_state:
            st.session_state.steps = {}

        st.rerun()

def initialize_backend():
    if "backend" not in st.session_state:
        try:
            st.session_state.backend = get_backend_instance()
            st.success("✅ Cinema backend initialized successfully!")
        except Exception as e:
            st.error(f"❌ Backend initialization error: {e}")
            st.stop()

    if "memory" not in st.session_state:
        st.session_state.memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history",
            output_key="output"
        )

def main():
    setup_page()

    initialize_backend()

    setup_sidebar()

    setup_main_page()

    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({
            "role": "assistant",
            "content": INITIAL_MESSAGE
        })

    st.markdown("---")

    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🎭" if message["role"] == "assistant" else "👤"):
            st.markdown(message["content"])

    user_input = st.chat_input(CHAT_INPUT_PLACEHOLDER)

    if 'suggested_input' in st.session_state:
        user_input = st.session_state.suggested_input
        del st.session_state.suggested_input

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

        with st.chat_message("assistant", avatar="🎭"):
            with st.spinner("🍷 Consulting my cinematographic archives..."):
                try:
                    executor = st.session_state.backend.create_agent_executor(st.session_state.memory)
                    st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
                    response = st.session_state.backend.process_message(user_input, executor, st_cb)

                    response_content = response["output"]

                    if "intermediate_steps" in response:
                        if "steps" not in st.session_state:
                            st.session_state.steps = {}
                        st.session_state.steps[str(len(st.session_state.messages))] = response["intermediate_steps"]

                except Exception as e:
                    response_content = f"🎬 I'm experiencing a technical difficulty with my archives. Error: {str(e)}"

                st.markdown(response_content)

                st.session_state.messages.append({"role": "assistant", "content": response_content})

if __name__ == "__main__":
    main()