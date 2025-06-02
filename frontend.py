import streamlit as st
import os
from dotenv import load_dotenv

# Imports pour l'intégration backend
from langchain.memory import ConversationBufferMemory
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

# Import de votre backend logique
from backend import get_backend_instance

# Charger les variables d'environnement
load_dotenv('config.env')
load_dotenv('prompts.env')

# Messages par défaut
INITIAL_MESSAGE = "🎬 Bonsoir et bienvenue dans votre loge privée ! Je suis votre critique personnel, prêt à explorer avec vous l'univers fascinant du cinéma. Que souhaitez-vous découvrir ce soir ?"
CHAT_INPUT_PLACEHOLDER = "🎭 Bonsoir ! De quel chef-d'œuvre cinématographique souhaitez-vous discuter ce soir ?"

def setup_page():
    """
    Configure la page Streamlit avec un thème cinéma bordeaux luxueux.
    """
    st.set_page_config(
        page_title="🎬 CinéBot - Votre Critique de Cinéma IA",
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Désactiver complètement la possibilité de cacher la sidebar
    st.markdown("""
        <style>
        /* Cacher tous les boutons de fermeture/réduction de la sidebar */
        .css-79elbk, .css-qbe2hs, [data-testid="collapsedControl"], 
        .css-vk3wp9, .css-18ni7ap, .css-vk3wp9 > button,
        button[kind="header"], .css-vk3wp9 .css-18ni7ap {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            pointer-events: none !important;
        }
        
        /* Forcer la sidebar à rester ouverte avec largeur fixe */
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
        
        /* Empêcher toute interaction avec les contrôles de sidebar */
        .css-6qob1r.css-1d391kg {
            width: 280px !important;
            transform: none !important;
        }
        
        /* Masquer le header de la sidebar qui contient les boutons */
        .css-1cypcdb .css-1vbkxwb {
            display: none !important;
        }
        
        /* Forcer l'affichage permanent du contenu */
        .css-1cypcdb {
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # CSS personnalisé avec palette bordeaux élégante
    st.markdown("""
        <style>
        /* Palette de couleurs bordeaux raffinée */
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
        
        /* Arrière-plan avec texture velours bordeaux */
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
        
        /* Rideau bordeaux luxueux en haut */
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
        
        /* Rideaux latéraux bordeaux */
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
        
        .curtain-left { 
            left: 0; 
            background: linear-gradient(to right, 
                var(--burgundy), var(--bordeaux-light), var(--bordeaux-dark));
        }
        .curtain-right { 
            right: 0; 
            background: linear-gradient(to left, 
                var(--burgundy), var(--bordeaux-light), var(--bordeaux-dark));
            box-shadow: inset 8px 0 20px rgba(0, 0, 0, 0.4);
        }
        
        /* Ajustement du contenu principal - Compensation sidebar fixe */
        .main .block-container {
            padding-top: 70px;
            padding-left: 300px;
            padding-right: 75px;
            max-width: none;
            margin-left: 280px;
            width: calc(100vw - 280px);
        }
        
        /* Ajustement de la zone de contenu principal */
        .stApp > div:first-child {
            margin-left: 280px !important;
            width: calc(100% - 280px) !important;
        }
        
        /* Forcer le layout principal à s'adapter */
        .main {
            margin-left: 280px !important;
        }
        
        /* Sidebar bordeaux élégante - Toujours visible et fixe */
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
        
        /* Contenu de la sidebar fixe et toujours visible */
        .css-1cypcdb {
            overflow-y: auto !important;
            padding: 1rem !important;
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
            width: 100% !important;
        }
        
        /* Empêcher les transformations sur la sidebar */
        .css-1d391kg[data-testid="stSidebar"] {
            transform: none !important;
            transition: none !important;
        }
        
        /* Titre principal avec effet champagne-bordeaux */
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
        
        /* Sous-titre raffiné */
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
        
        /* Cards avec effet velours bordeaux premium - Hauteur égale */
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
            /* Hauteur fixe pour égaliser toutes les cards */
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
        
        /* Icônes avec animation sophistiquée */
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
        
        /* Messages de chat avec style salon privé */
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
        
        /* Boutons avec effet bordeaux-champagne */
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
        
        /* Expandeur avec style bordeaux raffiné */
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
        
        /* Input avec style salon privé */
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
        
        /* Headers de sidebar avec éclairage doré */
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
        
        /* Éclairage ambiant doré sophistiqué */
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
        
        /* Particules dorées dans l'air */
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
        
        /* Amélioration de la lisibilité */
        .stMarkdown, .stText {
            color: var(--champagne);
        }
        
        /* Style pour les listes dans la sidebar */
        .css-1d391kg .stMarkdown li {
            color: var(--champagne);
            margin-bottom: 0.5rem;
        }
        
        /* Animation d'entrée pour les cards */
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
        
        <!-- Éléments décoratifs -->
        <div class="curtain-top"></div>
        <div class="curtain-left"></div>
        <div class="curtain-right"></div>
        <div class="ambient-light"></div>
        
        <!-- Particules dorées améliorées -->
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
    """
    Crée la page principale avec l'ambiance cinéma bordeaux raffinée.
    """
    # Titre principal avec effet champagne-bordeaux
    st.markdown('<h1 class="main-title">🎭 CinéBot 🎬</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">✨ Votre Critique Privé dans cette Loge de Cinéma d\'Exception ✨</p>', unsafe_allow_html=True)

    # Section d'information sur les capacités avec style amélioré
    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        st.markdown("""
        <div class="info-card">
            <h3><span class="feature-icon">🎭</span>Expertise Cinématographique</h3>
            <p>Analyses approfondies par un critique chevronné, dans l'intimité feutrée de votre salon privé. Découvrez les subtilités narratives, visuelles et techniques de chaque œuvre avec un regard d'expert.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="info-card">
            <h3><span class="feature-icon">🎬</span>Archives Exclusives</h3>
            <p>Accès privilégié aux trésors du septième art : classiques intemporels, chef-d'œuvres contemporains et perles méconnues du cinéma mondial. Une collection soigneusement curée pour tous les goûts.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="info-card">
            <h3><span class="feature-icon">🍿</span>Programmation Sur-Mesure</h3>
            <p>Conseils personnalisés pour vos soirées cinéma, comme un concierge culturel dédié à vos goûts raffinés et vos envies du moment. Laissez-vous guider vers votre prochaine découverte.</p>
        </div>
        """, unsafe_allow_html=True)

def setup_sidebar():
    """
    Crée une sidebar raffinée avec le thème bordeaux.
    """
    with st.sidebar:
        st.markdown('<h2 class="sidebar-header">🎪 Loge Privée</h2>', unsafe_allow_html=True)

        # Section menu principal avec style raffiné
        with st.expander("🎯 Votre Menu Culturel", expanded=True):
            st.markdown("""
            🎭 **Bienvenue dans votre loge d'exception !**
            
            🍷 Votre sommelier culturel vous propose :
            
            • **🎬 Exploration des Archives** - Voyage à travers l'histoire du cinéma
            • **🎭 Critiques d'Art** - Analyses esthétiques et narratives approfondies  
            • **👑 Portraits de Légendes** - Biographies des maîtres du cinéma
            • **💎 Secrets de l'Industrie** - Coulisses et anecdotes exclusives
            • **🏆 Palmarès Prestige** - Films couronnés et reconnaissance critique
            • **🎯 Curation Personnelle** - Sélection adaptée à vos goûts raffinés
            """)

        # Section suggestions culturelles
        with st.expander("🎬 Suggestions Culturelles", expanded=False):
            st.markdown("""
            **🍷 Conversations de salon :**
            
            • *"Analyse-moi l'œuvre visionnaire de Stanley Kubrick"*
            • *"Recommande-moi un film dans l'esprit de Casablanca"*
            • *"Parle-moi de l'influence de la Nouvelle Vague"*
            • *"Quels sont les secrets narratifs de Hitchcock ?"*
            • *"Explore pour moi la filmographie de Bergman"*
            • *"Explique-moi l'impact révolutionnaire de Citizen Kane"*
            • *"Quels films ont défini l'âge d'or hollywoodien ?"*
            """)

        # Collection de genres raffinés
        with st.expander("🎭 Notre Collection Exclusive"):
            genres = [
                "🎭 Drame d'Auteur", "😂 Comédie Sophistiquée", "🔫 Film Noir Classique",
                "👻 Fantastique Poétique", "🚀 Science-Fiction Intellectuelle", "💕 Romance Intemporelle",
                "🕵️ Thriller Psychologique", "🤠 Western Épique", "🎨 Animation d'Art"
            ]

            for genre in genres:
                if st.button(genre, key=f"genre_{genre}"):
                    genre_clean = genre.split(' ', 1)[1] if ' ' in genre else genre
                    st.session_state.suggested_input = f"Sélectionne-moi les plus beaux {genre_clean} pour une soirée d'exception"

        st.markdown("---")

        # Bouton nouvelle session intégré dans la fonction add_reset_button
        add_reset_button(msgs)

        # Footer raffiné
        st.markdown("""
        ---
        <div style="text-align: center; color: var(--gold); font-family: Georgia, serif;">
            <small>🎭 Votre Critique Personnel • Excellence IA</small><br>
            <small>🍷 L'Art du Cinéma à Votre Service 🎬</small><br>
            <small style="color: var(--champagne);">🎪 Expérience Loge Premium</small>
        </div>
        """, unsafe_allow_html=True)

def setup_chat_memory():
    """
    Configuration de la mémoire de conversation et de l'historique.
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
    Initialise le chat avec un message de bienvenue si nécessaire.
    """
    if len(msgs.messages) == 0:
        msgs.add_ai_message(INITIAL_MESSAGE)
        st.session_state.steps = {}

def display_chat_messages(msgs):
    """
    Affiche les messages de chat avec avatars thématiques cinéma.
    """
    avatars = {"human": "👤", "ai": "🎭"}

    for idx, msg in enumerate(msgs.messages):
        with st.chat_message(msg.type, avatar=avatars[msg.type]):
            # Afficher l'utilisation des outils pour les messages IA
            if msg.type == "ai":
                display_intermediate_steps(idx)

            # Afficher le contenu du message
            st.markdown(msg.content)

def display_intermediate_steps(message_index):
    """
    Affiche l'utilisation des outils cinéma avec icônes appropriées.
    """
    steps = st.session_state.steps.get(str(message_index), [])

    for step in steps:
        if step[0].tool == "_Exception":
            continue

        # Icônes des outils cinéma
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
            st.write("**Analyse:**", step[0].log)
            st.write("**Résultat:**", step[1])

def handle_user_input(msgs, memory, backend):
    """
    Gère l'entrée utilisateur et génère la réponse IA.
    """
    # Gestion des messages suggérés depuis la sidebar
    user_input = None
    if 'suggested_input' in st.session_state:
        user_input = st.session_state.suggested_input
        del st.session_state.suggested_input

    # Input utilisateur normal
    if not user_input:
        user_input = st.chat_input(placeholder=CHAT_INPUT_PLACEHOLDER)

    if user_input:
        # Afficher le message utilisateur
        st.chat_message("human", avatar="👤").markdown(user_input)

        # Traiter via l'IA
        with st.chat_message("ai", avatar="🎭"):
            with st.spinner("🍷 Consultation de mes archives cinématographiques..."):
                st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
                executor = backend.create_agent_executor(memory)
                response = backend.process_message(user_input, executor, st_cb)

            # Afficher la réponse
            st.markdown(response["output"])

            # Stocker les étapes d'utilisation des outils
            st.session_state.steps[str(len(msgs.messages) - 1)] = response["intermediate_steps"]

def add_reset_button(msgs):
    """
    Ajoute un bouton de reset dans la sidebar.
    """
    # Bouton nouvelle session avec style élégant
    if st.button("🎬 Nouvelle Projection", help="Commencer une nouvelle séance cinématographique"):
        msgs.clear()
        msgs.add_ai_message(INITIAL_MESSAGE)
        st.session_state.steps = {}
        if 'chat_history' in st.session_state:
            st.session_state.chat_history = []
        st.rerun()

def main():
    """
    Fonction principale qui orchestre l'interface complète.
    """
    # Configuration de la page
    setup_page()

    # Configuration de la sidebar
    setup_sidebar()

    # Page principale
    setup_main_page()

    # Initialisation de l'historique des messages
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Séparateur élégant
    st.markdown("---")

    # Affichage de l'historique des conversations
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🎭" if message["role"] == "assistant" else "👤"):
            st.markdown(message["content"])

    # Zone de saisie avec style loge privée
    user_input = st.chat_input(
        "🎭 Bonsoir ! De quel chef-d'œuvre cinématographique souhaitez-vous discuter ce soir ?"
    )

    # Gestion des messages suggérés depuis la sidebar
    if 'suggested_input' in st.session_state:
        user_input = st.session_state.suggested_input
        del st.session_state.suggested_input

    # Traitement des messages utilisateur
    if user_input:
        # Ajouter le message utilisateur à l'historique
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Afficher le message utilisateur
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

        # Générer et afficher la réponse du bot
        with st.chat_message("assistant", avatar="🎭"):
            with st.spinner("🍷 Consultation de mes archives cinématographiques..."):
                # Ici, intégrer votre logique backend
                # response = chat_backend.get_response(user_input)

                # Réponse temporaire pour la démonstration
                response = f"🎬 Magnifique choix ! Permettez-moi d'analyser cette œuvre avec l'attention qu'elle mérite. Votre question sur '{user_input}' mérite une réponse digne de ce salon privé..."

                st.markdown(response)

                # Ajouter la réponse à l'historique
                st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()