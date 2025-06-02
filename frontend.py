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

    # CSS personnalisé avec palette bordeaux élégante (gardez tout votre CSS existant)
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
        
        /* Règle pour le texte blanc */
        .stApp * {
            color: white !important;
        }
        
        /* Votre CSS existant ici - je garde juste les parties essentielles pour l'exemple */
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
            <p>Analyses approfondies par un critique chevronné, dans l'intimité feutrée de votre salon privé.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="info-card">
            <h3><span class="feature-icon">🎬</span>Archives Exclusives</h3>
            <p>Accès privilégié aux trésors du septième art : classiques intemporels et chef-d'œuvres contemporains.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="info-card">
            <h3><span class="feature-icon">🍿</span>Programmation Sur-Mesure</h3>
            <p>Conseils personnalisés pour vos soirées cinéma, comme un concierge culturel dédié.</p>
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
            """)

        # Section suggestions culturelles
        with st.expander("🎬 Suggestions Culturelles", expanded=False):
            st.markdown("""
            **🍷 Conversations de salon :**
            
            • *"Analyse-moi l'œuvre visionnaire de Stanley Kubrick"*
            • *"Recommande-moi un film dans l'esprit de Casablanca"*
            • *"Parle-moi de l'influence de la Nouvelle Vague"*
            • *"Quels sont les secrets narratifs de Hitchcock ?"*
            """)

        # Collection de genres raffinés
        with st.expander("🎭 Notre Collection Exclusive"):
            genres = [
                "🎭 Drame d'Auteur", "😂 Comédie Sophistiquée", "🔫 Film Noir Classique",
                "👻 Fantastique Poétique", "🚀 Science-Fiction Intellectuelle", "💕 Romance Intemporelle"
            ]

            for genre in genres:
                if st.button(genre, key=f"genre_{genre}"):
                    genre_clean = genre.split(' ', 1)[1] if ' ' in genre else genre
                    st.session_state.suggested_input = f"Sélectionne-moi les plus beaux {genre_clean} pour une soirée d'exception"

        st.markdown("---")

        # Bouton nouvelle session
        add_reset_button()

        # Footer raffiné
        st.markdown("""
        ---
        <div style="text-align: center; color: var(--gold); font-family: Georgia, serif;">
            <small>🎭 Votre Critique Personnel • Excellence IA</small><br>
            <small>🍷 L'Art du Cinéma à Votre Service 🎬</small>
        </div>
        """, unsafe_allow_html=True)

def add_reset_button():
    """
    Ajoute un bouton de reset dans la sidebar.
    """
    # Bouton nouvelle session avec style élégant
    if st.button("🎬 Nouvelle Projection", help="Commencer une nouvelle séance cinématographique"):
        # Reset des messages
        if "messages" in st.session_state:
            st.session_state.messages = []

        # Reset de la mémoire si elle existe
        if "memory" in st.session_state:
            st.session_state.memory.clear()

        # Reset des étapes
        if "steps" in st.session_state:
            st.session_state.steps = {}

        st.rerun()

def initialize_backend():
    """
    Initialise le backend si ce n'est pas déjà fait.
    """
    if "backend" not in st.session_state:
        try:
            st.session_state.backend = get_backend_instance()
            st.success("✅ Backend cinéma initialisé avec succès !")
        except Exception as e:
            st.error(f"❌ Erreur d'initialisation du backend : {e}")
            st.stop()

    if "memory" not in st.session_state:
        st.session_state.memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history",
            output_key="output"
        )

def main():
    """
    Fonction principale qui orchestre l'interface complète.
    """
    # Configuration de la page
    setup_page()

    # Initialisation du backend
    initialize_backend()

    # Configuration de la sidebar
    setup_sidebar()

    # Page principale
    setup_main_page()

    # Initialisation de l'historique des messages
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Message de bienvenue initial
        st.session_state.messages.append({
            "role": "assistant",
            "content": INITIAL_MESSAGE
        })

    # Séparateur élégant
    st.markdown("---")

    # Affichage de l'historique des conversations
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🎭" if message["role"] == "assistant" else "👤"):
            st.markdown(message["content"])

    # Zone de saisie avec style loge privée
    user_input = st.chat_input(CHAT_INPUT_PLACEHOLDER)

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
                try:
                    # Utilisation du vrai backend
                    executor = st.session_state.backend.create_agent_executor(st.session_state.memory)
                    st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
                    response = st.session_state.backend.process_message(user_input, executor, st_cb)

                    response_content = response["output"]

                    # Stocker les étapes d'utilisation des outils
                    if "intermediate_steps" in response:
                        if "steps" not in st.session_state:
                            st.session_state.steps = {}
                        st.session_state.steps[str(len(st.session_state.messages))] = response["intermediate_steps"]

                except Exception as e:
                    # Fallback en cas d'erreur
                    response_content = f"🎬 Je rencontre une difficulté technique dans mes archives. Erreur : {str(e)}"

                st.markdown(response_content)

                # Ajouter la réponse à l'historique
                st.session_state.messages.append({"role": "assistant", "content": response_content})

if __name__ == "__main__":
    main()