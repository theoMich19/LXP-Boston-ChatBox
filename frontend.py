"""
CinéBot - Advanced AI Cinema Assistant
Enhanced Cinema Theater Theme Interface (English Version)
"""

import streamlit as st
from langchain.memory import ConversationBufferMemory
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

# Import our backend logic
from backend import get_backend_instance

# Constants
INITIAL_MESSAGE = "🎭 Good evening and welcome to your private cinema lounge! I'm your personal film critic, ready to explore the wonders of the seventh art with you. What would you like to discover tonight?"
CHAT_INPUT_PLACEHOLDER = "Ask me anything about cinema: movies, actors, directors, recommendations..."

def inject_custom_css():
    """
    Inject custom CSS for cinema/theater theme
    """
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Crimson+Text:ital,wght@0,400;0,600;1,400&display=swap');
    
    /* CSS Variables for theme */
    :root {
        --cinema-gold: #D4AF37;
        --cinema-red: #8B0000;
        --cinema-burgundy: #722F37;
        --cinema-black: #1C1C1C;
        --cinema-cream: #F5F5DC;
        --velvet-red: #C41E3A;
        --spotlight: #FFD700;
    }
    
    /* Main background with velvet effect */
    .stApp {
        background: linear-gradient(135deg, 
            var(--cinema-black) 0%, 
            var(--cinema-burgundy) 50%, 
            var(--cinema-black) 100%);
        background-attachment: fixed;
    }
    
    /* Header with theater curtain effect */
    .main-header {
        background: linear-gradient(90deg, var(--cinema-red), var(--velvet-red), var(--cinema-red));
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.8);
        border: 3px solid var(--cinema-gold);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 215, 0, 0.2), transparent);
        animation: spotlight 3s infinite;
    }
    
    @keyframes spotlight {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    .cinema-title {
        font-family: 'Playfair Display', serif;
        font-size: 3.5rem;
        font-weight: 700;
        color: var(--cinema-gold);
        text-align: center;
        text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.8);
        margin-bottom: 0.5rem;
        letter-spacing: 2px;
    }
    
    .cinema-subtitle {
        font-family: 'Crimson Text', serif;
        font-size: 1.4rem;
        color: var(--cinema-cream);
        text-align: center;
        font-style: italic;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.6);
    }
    
    /* Cards with cinema ticket effect */
    .cinema-card {
        background: linear-gradient(45deg, var(--cinema-cream), #FFF8DC);
        border: 2px dashed var(--cinema-gold);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        position: relative;
        font-family: 'Crimson Text', serif;
    }
    
    .cinema-card::before,
    .cinema-card::after {
        content: '';
        position: absolute;
        width: 20px;
        height: 20px;
        background: var(--cinema-burgundy);
        border-radius: 50%;
        top: 50%;
        transform: translateY(-50%);
    }
    
    .cinema-card::before {
        left: -10px;
    }
    
    .cinema-card::after {
        right: -10px;
    }
    
    .cinema-card h4 {
        color: var(--cinema-red);
        font-weight: 600;
        margin-bottom: 0.5rem;
        font-size: 1.2rem;
    }
    
    .cinema-card p {
        color: var(--cinema-black);
        line-height: 1.6;
        margin: 0;
    }
    
    /* Sidebar with curtain effect */
    .css-1d391kg {
        background: linear-gradient(180deg, 
            var(--cinema-black) 0%, 
            var(--cinema-burgundy) 50%, 
            var(--cinema-black) 100%);
        border-right: 3px solid var(--cinema-gold);
    }
    
    /* Chat messages with cinema bubbles */
    .stChatMessage {
        background: rgba(0, 0, 0, 0.55) !important;
        border: 1px solid var(--cinema-gold);
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        font-family: 'Crimson Text', serif;
    }
    
    /* Buttons with theatrical effect */
    .stButton > button {
        background: linear-gradient(45deg, var(--cinema-red), var(--velvet-red));
        color: var(--cinema-gold);
        border: 2px solid var(--cinema-gold);
        border-radius: 25px;
        font-family: 'Crimson Text', serif;
        font-weight: 600;
        font-size: 1.1rem;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton > button:hover {
        background: linear-gradient(45deg, var(--velvet-red), var(--cinema-red));
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(196, 30, 58, 0.4);
    }
    
    /* Input with vintage style */
    .stTextInput > div > div > input {
        background: var(--cinema-cream);
        border: 2px solid var(--cinema-gold);
        border-radius: 10px;
        font-family: 'Crimson Text', serif;
        font-size: 1.1rem;
        color: var(--cinema-black);
    }
    
    /* Status boxes for tools */
    .stStatus {
        background: rgba(212, 175, 55, 0.1);
        border: 1px solid var(--cinema-gold);
        border-radius: 8px;
    }
    
    /* Expander with theatrical style */
    .streamlit-expanderHeader {
        background: var(--cinema-burgundy);
        color: var(--cinema-gold);
        font-family: 'Playfair Display', serif;
        font-weight: 600;
    }
    
    /* Decorative separator */
    .decorative-separator {
        text-align: center;
        margin: 2rem 0;
        font-size: 2rem;
        color: var(--cinema-gold);
    }
    
    /* Blinking animation for important elements */
    .spotlight-text {
        animation: gentle-glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes gentle-glow {
        from { text-shadow: 0 0 5px var(--cinema-gold); }
        to { text-shadow: 0 0 15px var(--cinema-gold), 0 0 25px var(--cinema-gold); }
    }
    
    /* Footer with vintage style */
    .cinema-footer {
        background: var(--cinema-black);
        border: 2px solid var(--cinema-gold);
        border-radius: 10px;
        padding: 1rem;
        margin-top: 2rem;
        text-align: center;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .cinema-title {
            font-size: 2.5rem;
        }
        .cinema-subtitle {
            font-size: 1.2rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def setup_page():
    """
    Configure Streamlit page with elegant cinema theme
    """
    st.set_page_config(
        page_title="🎭 CinéBot - AI Cinema Assistant",
        page_icon="🎭",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Inject custom CSS
    inject_custom_css()

    # Main header with theatrical style
    st.markdown("""
    <div class="main-header">
        <h1 class="cinema-title">🎭 CinéBot 🎬</h1>
        <p class="cinema-subtitle">Your Personal Film Critic</p>
    </div>
    """, unsafe_allow_html=True)

    # Information cards with cinema ticket style
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="cinema-card">
            <h4>🎬 Expert Analysis</h4>
            <p>In-depth criticism and artistic analysis of cinematic works</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="cinema-card">
            <h4>🎯 Recommendations</h4>
            <p>Personalized suggestions based on your movie tastes and preferences</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="cinema-card">
            <h4>📚 Cinema Archives</h4>
            <p>Access to vast database and industry insider secrets</p>
        </div>
        """, unsafe_allow_html=True)

def setup_sidebar():
    """
    Create sidebar with cinema theatrical theme
    """
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h2 style="color: #D4AF37; font-family: 'Playfair Display', serif;">
                🎪 Private Lounge
            </h2>
        </div>
        """, unsafe_allow_html=True)

        # Capabilities section with elegant style
        with st.expander("🎭 My Cinema Talents", expanded=True):
            st.markdown("""
            <div style="font-family: 'Crimson Text', serif; line-height: 1.8;">
                🎬 <strong>Tailored Recommendations</strong><br/>
                <em>Movies adapted to your unique tastes</em><br/>
                🎪 <strong>Critical Analysis</strong><br/>
                <em>Artistic and technical breakdown</em><br/>
                🎭 <strong>Artist Profiles</strong><br/>
                <em>Directors, actors, creators</em><br/>
                📜 <strong>Cinema History</strong><br/>
                <em>Anecdotes and cultural heritage</em><br/>
                💰 <strong>Industry Trends</strong><br/>
                <em>Box office and market data</em>
            </div>
            """, unsafe_allow_html=True)

        # Question examples with theatrical style
        with st.expander("✨ Cinema Inspirations"):
            st.markdown("""
            <div style="font-family: 'Crimson Text', serif; color: white;">
                <p><strong>🎬 "Recommend a movie like Blade Runner"</strong></p>
                <p><strong>🎪 "Tell me about Christopher Nolan's style"</strong></p>
                <p><strong>🏆 "What are the best films of 2023?"</strong></p>
                <p><strong>🎨 "Analyze the cinematography of Citizen Kane"</strong></p>
                <p><strong>🏅 "Who won the Oscar for Best Picture in 1994?"</strong></p>
            </div>
            """, unsafe_allow_html=True)
def setup_chat_memory():
    """
    Configure conversation memory
    """
    msgs = StreamlitChatMessageHistory()
    memory = ConversationBufferMemory(
        chat_memory=msgs,
        return_messages=True,
        memory_key="chat_history",
        output_key="output"
    )
    return msgs, memory

def initialize_chat_if_needed(msgs):
    """
    Initialize chat with elegant welcome message
    """
    if len(msgs.messages) == 0:
        msgs.add_ai_message(INITIAL_MESSAGE)
        st.session_state.steps = {}

def add_reset_button(msgs):
    """
    Add stylized reset button
    """
    st.sidebar.markdown("---")

    if st.sidebar.button("🎬 New Session",
                         help="Start a new conversation",
                         key="reset_chat"):
        msgs.clear()
        msgs.add_ai_message(INITIAL_MESSAGE)
        st.session_state.steps = {}
        if 'suggested_input' in st.session_state:
            del st.session_state.suggested_input
        st.rerun()

def display_chat_messages(msgs):
    """
    Display messages with cinema avatars
    """
    avatars = {"human": "🎭", "ai": "🎬"}

    for idx, msg in enumerate(msgs.messages):
        with st.chat_message(msg.type, avatar=avatars[msg.type]):
            # Display intermediate steps for AI messages
            if msg.type == "ai":
                display_intermediate_steps(idx)

            # Display message content
            st.markdown(f'<div style="font-family: \'Crimson Text\', serif; font-size: 1.1rem; line-height: 1.6;">{msg.content}</div>',
                        unsafe_allow_html=True)

def display_intermediate_steps(message_index):
    """
    Display tool usage with cinema icons
    """
    steps = st.session_state.steps.get(str(message_index), [])

    for step in steps:
        if step[0].tool == "_Exception":
            continue

        # Specialized icons for cinema tools
        tool_icons = {
            "search_movies": "🔍",
            "get_movie_details": "🎬",
            "get_actor_info": "🎭",
            "get_director_info": "🎪",
            "movie_recommendations": "🎯",
            "cinema_analysis": "📊",
            "box_office_data": "💰",
            "film_criticism": "✍️",
            "awards_info": "🏆",
            "cinema_history": "📜"
        }

        tool_name = step[0].tool
        icon = tool_icons.get(tool_name, "🎨")
        display_name = tool_name.replace('_', ' ').title()

        with st.status(f"{icon} {display_name}: {step[0].tool_input}", state="complete"):
            st.write("**Analysis:**", step[0].log)
            st.write("**Result:**", step[1])

def handle_user_input(msgs, memory, backend):
    """
    Handle user input and generate AI response
    """
    # Check for suggestions from sidebar
    user_input = None
    if 'suggested_input' in st.session_state:
        user_input = st.session_state.suggested_input
        del st.session_state.suggested_input

    # Get input from chat box or suggestions
    if not user_input:
        user_input = st.chat_input(placeholder=CHAT_INPUT_PLACEHOLDER)

    if user_input:
        # Display user message
        with st.chat_message("human", avatar="🎭"):
            st.markdown(f'<div style="font-family: \'Crimson Text\', serif; font-size: 1.1rem;">{user_input}</div>',
                        unsafe_allow_html=True)

        # Process through AI
        with st.chat_message("ai", avatar="🎬"):
            with st.spinner("🍿 Consulting my cinema archives..."):
                try:
                    st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
                    executor = backend.create_agent_executor(memory)
                    response = backend.process_message(user_input, executor, st_cb)

                    # Display response with style
                    st.markdown(f'<div style="font-family: \'Crimson Text\', serif; font-size: 1.1rem; line-height: 1.6;">{response["output"]}</div>',
                                unsafe_allow_html=True)

                    # Store tool usage steps
                    st.session_state.steps[str(len(msgs.messages) - 1)] = response["intermediate_steps"]

                except Exception as e:
                    error_msg = f"🎭 I'm experiencing technical difficulties with my cinema database. Error: {str(e)}"
                    st.error(error_msg)
                    msgs.add_ai_message(error_msg)

def add_cinema_footer():
    """
    Add footer with vintage cinema theme
    """
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div class="cinema-footer">
        <p style="color: #D4AF37; font-family: 'Playfair Display', serif; font-size: 1.1rem; margin-bottom: 0.5rem;">
            <span class="spotlight-text">🎭 Your Personal Critic</span>
        </p>
        <p style="color: #F5F5DC; font-family: 'Crimson Text', serif; margin-bottom: 0.5rem;">
            🍿 Powered by Artificial Intelligence
        </p>
        <p style="color: #C41E3A; font-family: 'Playfair Display', serif; font-weight: bold; font-size: 0.9rem;">
            🎬 Welcome to the Red Carpet Experience
        </p>
    </div>
    """, unsafe_allow_html=True)

def main():
    """
    Main function that runs the CinéBot application
    """
    # Page setup
    setup_page()

    # Sidebar setup
    setup_sidebar()

    # Initialize backend and memory
    try:
        backend = get_backend_instance()
        msgs, memory = setup_chat_memory()

        # Initialize chat
        initialize_chat_if_needed(msgs)

        # Add controls
        add_reset_button(msgs)
        add_cinema_footer()

        # Main decorative separator
        st.markdown('<div class="decorative-separator">🎭 ✨ 🎬 ✨ 🎪</div>', unsafe_allow_html=True)

        # Display conversation
        display_chat_messages(msgs)

        # Handle new inputs
        handle_user_input(msgs, memory, backend)

    except Exception as e:
        st.error(f"❌ Failed to initialize CinéBot backend: {e}")
        st.info("Please check your backend configuration and try again.")

if __name__ == "__main__":
    main()