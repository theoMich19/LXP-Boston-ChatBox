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
        .css-79elbk, .css-qbe2hs, [data-testid="collapsedControl"], 
        .css-vk3wp9, .css-18ni7ap, .css-vk3wp9 > button,
        button[kind="header"], .css-vk3wp9 .css-18ni7ap {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            pointer-events: none !important;
        }
        
        .css-1d391kg, .css-6qob1r {
            min-width: 280px !important;
            max-width: 280px !important;
            width: 280px !important;
            position: fixed !important;
            left: 0 !important;
            top: 0 !important;
            height: 100vh !important;
            z-index: 1000 !important;
        }
        
        .css-6qob1r.css-1d391kg {
            width: 280px !important;
            transform: none !important;
        }
        
        .css-1cypcdb .css-1vbkxwb {
            display: none !important;
        }
        
        .css-1cypcdb {
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
        }
        </style>
    """, unsafe_allow_html=True)

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
        
        .curtain-top {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 45px;
            background: linear-gradient(to bottom, 
                var(--burgundy) 0%, 
                var(--wine-red) 20%, 
                var(--bordeaux-light) 50%, 
                var(--wine-red) 80%, 
                var(--burgundy) 100%);
            background-image: 
                repeating-linear-gradient(90deg, 
                    transparent, transparent 12px, 
                    rgba(0,0,0,0.15) 12px, rgba(0,0,0,0.15) 14px);
            box-shadow: 
                0 8px 25px rgba(128, 0, 32, 0.6),
                0 0 20px rgba(212, 175, 55, 0.3);
            z-index: 999;
            border-bottom: 4px solid var(--gold);
        }
        
        .curtain-left, .curtain-right {
            position: fixed;
            top: 45px;
            bottom: 0;
            width: 55px;
            background: linear-gradient(to right, 
                var(--burgundy) 0%, 
                var(--bordeaux-light) 40%, 
                var(--wine-red) 60%, 
                var(--bordeaux-dark) 100%);
            background-image: 
                repeating-linear-gradient(0deg, 
                    transparent, transparent 18px, 
                    rgba(0,0,0,0.12) 18px, rgba(0,0,0,0.12) 20px);
            box-shadow: inset -8px 0 20px rgba(0, 0, 0, 0.4);
            z-index: 998;
        }
        
        .main .block-container {
            padding-top: 70px;
            padding-left: 300px;
            padding-right: 75px;
            max-width: none;
            margin-left: 280px;
            width: calc(100vw - 280px);
        }
        
        .stApp > div:first-child {
            margin-left: 280px !important;
            width: calc(100% - 280px) !important;
        }
        
        .main {
            margin-left: 280px !important;
        }
        
        .css-1d391kg, .css-6qob1r, .css-1cypcdb {
            background: linear-gradient(180deg, 
                var(--bordeaux-medium) 0%, 
                var(--bordeaux-dark) 40%, 
                #2d1417 70%, 
                var(--bordeaux-dark) 100%) !important;
            border-right: 4px solid var(--gold);
            box-shadow: 8px 0 30px rgba(114, 47, 55, 0.4);
            min-width: 280px !important;
            max-width: 280px !important;
            width: 280px !important;
            position: fixed !important;
            left: 0 !important;
            top: 0 !important;
            height: 100vh !important;
            z-index: 1000 !important;
            transform: translateX(0) !important;
        }
        
        .css-1cypcdb {
            overflow-y: auto !important;
            padding: 1rem !important;
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
            width: 100% !important;
        }
        
        .css-1d391kg[data-testid="stSidebar"] {
            transform: none !important;
            transition: none !important;
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
            background-size: 400% 400%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            text-shadow: 
                0 0 15px rgba(212, 175, 55, 0.6),
                0 0 30px rgba(156, 26, 28, 0.4),
                0 0 45px rgba(212, 175, 55, 0.3);
            margin-bottom: 1.5rem;
            font-family: 'Georgia', 'Times New Roman', serif;
            animation: elegantShimmer 4s ease-in-out infinite;
            letter-spacing: 2px;
        }
        
        @keyframes elegantShimmer {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .subtitle {
            text-align: center;
            color: var(--champagne);
            font-size: 1.5rem;
            margin-bottom: 2.5rem;
            font-style: italic;
            font-family: 'Georgia', serif;
            text-shadow: 0 0 12px rgba(247, 231, 206, 0.4);
            letter-spacing: 1px;
        }
        
        .info-card {
            background: linear-gradient(145deg, 
                rgba(114, 47, 55, 0.35) 0%, 
                rgba(156, 26, 28, 0.25) 30%, 
                rgba(138, 75, 92, 0.3) 70%, 
                rgba(74, 14, 14, 0.4) 100%);
            backdrop-filter: blur(12px);
            padding: 2.5rem;
            border-radius: 25px;
            border: 3px solid var(--gold);
            box-shadow: 
                0 15px 40px rgba(156, 26, 28, 0.5),
                inset 0 2px 0 rgba(212, 175, 55, 0.3),
                0 0 30px rgba(212, 175, 55, 0.2);
            margin: 1.5rem 0;
            color: var(--champagne);
            position: relative;
            overflow: hidden;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            min-height: 280px;
            height: 280px;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
        }
        
        .info-card h3 {
            margin-bottom: 1rem;
            flex-shrink: 0;
        }
        
        .info-card p {
            flex-grow: 1;
            display: flex;
            align-items: center;
            text-align: justify;
            line-height: 1.6;
        }
        
        .info-card:hover {
            transform: translateY(-5px);
            box-shadow: 
                0 20px 50px rgba(156, 26, 28, 0.7),
                inset 0 2px 0 rgba(212, 175, 55, 0.4),
                0 0 40px rgba(212, 175, 55, 0.3);
        }
        
        .info-card::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(
                45deg,
                transparent,
                rgba(212, 175, 55, 0.08),
                transparent
            );
            animation: elegantShine 6s infinite;
        }
        
        @keyframes elegantShine {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .feature-icon {
            font-size: 2.8rem;
            margin-right: 15px;
            animation: sophisticatedPulse 4s infinite;
            filter: drop-shadow(0 0 15px rgba(212, 175, 55, 0.6));
        }
        
        @keyframes sophisticatedPulse {
            0% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.85; transform: scale(1.08); }
            100% { opacity: 1; transform: scale(1); }
        }
        
        .stChatMessage {
            background: rgba(74, 14, 14, 0.85) !important;
            border: 2px solid var(--gold);
            border-radius: 20px;
            margin: 0.8rem 0;
            box-shadow: 
                0 8px 25px rgba(156, 26, 28, 0.3),
                0 0 15px rgba(212, 175, 55, 0.2);
            backdrop-filter: blur(8px);
        }
        
        .stButton > button {
            background: linear-gradient(45deg, 
                var(--wine-red) 0%, 
                var(--gold) 50%, 
                var(--wine-red) 100%);
            background-size: 300% 300%;
            color: var(--champagne);
            font-weight: bold;
            border: 3px solid var(--gold);
            border-radius: 35px;
            padding: 0.8rem 3rem;
            box-shadow: 
                0 8px 25px rgba(156, 26, 28, 0.5),
                0 0 25px rgba(212, 175, 55, 0.3);
            transition: all 0.5s ease;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            font-family: 'Georgia', serif;
            font-size: 0.95rem;
        }
        
        .stButton > button:hover {
            transform: translateY(-4px) scale(1.03);
            background-position: 100% 100%;
            box-shadow: 
                0 12px 35px rgba(156, 26, 28, 0.7),
                0 0 35px rgba(212, 175, 55, 0.5);
            color: white;
        }
        
        .streamlit-expanderHeader {
            background: linear-gradient(90deg, 
                var(--burgundy), var(--wine-red), var(--burgundy)) !important;
            color: var(--gold) !important;
            border: 2px solid var(--gold);
            border-radius: 15px;
            box-shadow: 0 6px 15px rgba(128, 0, 32, 0.6);
            font-family: 'Georgia', serif;
            font-weight: bold;
        }
        
        .stTextInput > div > div > input, 
        .stChatInputContainer > div > div > div > input,
        .stChatInputContainer input {
            background: linear-gradient(145deg, 
                rgba(74, 14, 14, 0.9), 
                rgba(45, 20, 23, 0.95)) !important;
            color: var(--champagne) !important;
            border: 3px solid var(--gold) !important;
            border-radius: 20px !important;
            padding: 1.2rem !important;
            box-shadow: 
                inset 0 3px 8px rgba(0, 0, 0, 0.6),
                0 0 20px rgba(156, 26, 28, 0.3) !important;
            font-family: 'Georgia', serif !important;
            font-size: 1rem !important;
        }
        
        .stTextInput > div > div > input::placeholder, 
        .stChatInputContainer input::placeholder {
            color: rgba(247, 231, 206, 0.8) !important;
            font-style: italic;
        }
        
        .stTextInput > div > div > input:focus,
        .stChatInputContainer input:focus {
            border-color: var(--champagne) !important;
            box-shadow: 
                inset 0 3px 8px rgba(0, 0, 0, 0.6),
                0 0 25px rgba(212, 175, 55, 0.5) !important;
        }
        
        .sidebar-header {
            color: var(--gold);
            font-size: 1.7rem;
            font-weight: bold;
            margin: 1.5rem 0;
            text-align: center;
            text-shadow: 0 0 20px rgba(212, 175, 55, 0.6);
            font-family: 'Georgia', serif;
            letter-spacing: 1px;
        }
        
        .ambient-light {
            position: fixed;
            top: 50%;
            left: 50%;
            width: 150px;
            height: 150px;
            background: radial-gradient(circle, 
                rgba(212, 175, 55, 0.08) 0%, 
                rgba(156, 26, 28, 0.04) 40%, 
                transparent 70%);
            border-radius: 50%;
            transform: translate(-50%, -50%);
            animation: sophisticatedGlow 8s ease-in-out infinite;
            pointer-events: none;
            z-index: -1;
        }
        
        @keyframes sophisticatedGlow {
            0%, 100% { 
                transform: translate(-50%, -50%) scale(1); 
                opacity: 0.4; 
            }
            50% { 
                transform: translate(-50%, -50%) scale(1.8); 
                opacity: 0.15; 
            }
        }
        
        .dust-particles {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 1;
        }
        
        .dust-particle {
            position: absolute;
            width: 3px;
            height: 3px;
            background: rgba(212, 175, 55, 0.4);
            border-radius: 50%;
            animation: elegantFloat 12s infinite linear;
            box-shadow: 0 0 6px rgba(212, 175, 55, 0.6);
        }
        
        @keyframes elegantFloat {
            0% { 
                transform: translateY(100vh) rotate(0deg); 
                opacity: 0; 
            }
            10% { opacity: 1; }
            90% { opacity: 1; }
            100% { 
                transform: translateY(-10vh) rotate(360deg); 
                opacity: 0; 
            }
        }
        
        .stMarkdown, .stText {
            color: var(--champagne);
        }
        
        .css-1d391kg .stMarkdown li {
            color: var(--champagne);
            margin-bottom: 0.5rem;
        }
        
        .info-card {
            animation: slideInUp 0.6s ease-out;
        }
        
        @keyframes slideInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        </style>
        
        <div class="curtain-top"></div>
        <div class="curtain-left"></div>
        <div class="curtain-right"></div>
        <div class="ambient-light"></div>
        
        <div class="dust-particles">
            <div class="dust-particle" style="left: 15%; animation-delay: 0s;"></div>
            <div class="dust-particle" style="left: 25%; animation-delay: 2s;"></div>
            <div class="dust-particle" style="left: 35%; animation-delay: 4s;"></div>
            <div class="dust-particle" style="left: 45%; animation-delay: 6s;"></div>
            <div class="dust-particle" style="left: 55%; animation-delay: 8s;"></div>
            <div class="dust-particle" style="left: 65%; animation-delay: 10s;"></div>
            <div class="dust-particle" style="left: 75%; animation-delay: 1s;"></div>
            <div class="dust-particle" style="left: 85%; animation-delay: 3s;"></div>
        </div>
    """, unsafe_allow_html=True)

def setup_main_page():
    st.markdown('<h1 class="main-title">🎭 CinéBot 🎬</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">✨ Your Private Critic in this Exclusive Cinema Lounge ✨</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        st.markdown("""
        <div class="info-card">
            <h3><span class="feature-icon">🎭</span>Cinematic Expertise</h3>
            <p>In-depth analysis by a seasoned critic, in the intimate setting of your private lounge. Discover narrative, visual and technical subtleties of each work with an expert eye.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="info-card">
            <h3><span class="feature-icon">🎬</span>Exclusive Archives</h3>
            <p>Privileged access to the treasures of the seventh art: timeless classics, contemporary masterpieces and hidden gems from world cinema. A carefully curated collection for all tastes.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="info-card">
            <h3><span class="feature-icon">🍿</span>Tailor-Made Programming</h3>
            <p>Personalized advice for your movie nights, like a cultural concierge dedicated to your refined tastes and momentary desires. Let yourself be guided to your next discovery.</p>
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
            • **🏆 Prestige Awards** - Award-winning films and critical recognition
            • **🎯 Personal Curation** - Selection adapted to your refined tastes
            """)

        with st.expander("🎬 Cultural Suggestions", expanded=False):
            st.markdown("""
            **🍷 Lounge conversations:**
            
            • *"Analyze Stanley Kubrick's visionary work"*
            • *"Recommend a film in the spirit of Casablanca"*
            • *"Tell me about the influence of the French New Wave"*
            • *"What are Hitchcock's narrative secrets?"*
            • *"Explore Bergman's filmography for me"*
            • *"Explain the revolutionary impact of Citizen Kane"*
            • *"Which films defined Hollywood's golden age?"*
            """)

        with st.expander("🎭 Our Exclusive Collection"):
            genres = [
                "🎭 Auteur Drama", "😂 Sophisticated Comedy", "🔫 Classic Film Noir",
                "👻 Poetic Fantasy", "🚀 Intellectual Science Fiction", "💕 Timeless Romance",
                "🕵️ Psychological Thriller", "🤠 Epic Western", "🎨 Art Animation"
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
            <small>🍷 The Art of Cinema at Your Service 🎬</small><br>
            <small style="color: var(--champagne);">🎪 Premium Lounge Experience</small>
        </div>
        """, unsafe_allow_html=True)

def setup_chat_memory():
    msgs = StreamlitChatMessageHistory()
    memory = ConversationBufferMemory(
        chat_memory=msgs,
        return_messages=True,
        memory_key="chat_history",
        output_key="output"
    )
    return msgs, memory

def initialize_chat_if_needed(msgs):
    if len(msgs.messages) == 0:
        msgs.add_ai_message(INITIAL_MESSAGE)
        st.session_state.steps = {}

def display_chat_messages(msgs):
    avatars = {"human": "👤", "ai": "🎭"}

    for idx, msg in enumerate(msgs.messages):
        with st.chat_message(msg.type, avatar=avatars[msg.type]):
            if msg.type == "ai":
                display_intermediate_steps(idx)

            st.markdown(msg.content)

def display_intermediate_steps(message_index):
    steps = st.session_state.steps.get(str(message_index), [])

    for step in steps:
        if step[0].tool == "_Exception":
            continue

        tool_icons = {
            "search_movies": "🔍",
            "get_movie_details": "🎬",
            "get_movie_cast": "🎭",
            "get_movie_reviews": "⭐",
            "get_popular_movies": "🔥",
            "get_trending_movies": "📈",
            "discover_movies_by_genre": "🎪",
            "get_person_details": "👤",
            "get_person_movie_credits": "🎞️"
        }

        tool_name = step[0].tool
        icon = tool_icons.get(tool_name, "🔧")
        display_name = tool_name.replace('_', ' ').title()

        with st.status(f"{icon} {display_name}: {step[0].tool_input}", state="complete"):
            st.write("**Analysis:**", step[0].log)
            st.write("**Result:**", step[1])

def handle_user_input(msgs, memory, backend):
    user_input = None
    if 'suggested_input' in st.session_state:
        user_input = st.session_state.suggested_input
        del st.session_state.suggested_input

    if not user_input:
        user_input = st.chat_input(placeholder=CHAT_INPUT_PLACEHOLDER)

    if user_input:
        st.chat_message("human", avatar="👤").markdown(user_input)

        with st.chat_message("ai", avatar="🎭"):
            with st.spinner("🍷 Consulting my cinematographic archives..."):
                st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
                executor = backend.create_agent_executor(memory)
                response = backend.process_message(user_input, executor, st_cb)

            st.markdown(response["output"])

            st.session_state.steps[str(len(msgs.messages) - 1)] = response["intermediate_steps"]

def add_reset_button():
    if st.button("🎬 New Screening", help="Start a new cinematographic session"):
        if "messages" in st.session_state:
            st.session_state.messages = []

        if "memory" in st.session_state:
            st.session_state.memory.clear()

        if "steps" in st.session_state:
            st.session_state.steps = {}

        st.rerun()

def main():
    setup_page()

    backend = get_backend_instance()
    msgs, memory = setup_chat_memory()

    initialize_chat_if_needed(msgs)

    setup_sidebar()
    setup_main_page()

    st.markdown("---")

    display_chat_messages(msgs)

    handle_user_input(msgs, memory, backend)

if __name__ == "__main__":
    main()