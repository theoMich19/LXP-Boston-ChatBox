"""
LXP - Advanced AI development Workshop: AI Weatherman frontend
"""

import streamlit as st
from langchain.memory import ConversationBufferMemory
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

# Import our backend logic
from backend import get_backend_instance
from prompts import INITIAL_MESSAGE, CHAT_INPUT_PLACEHOLDER

def setup_page():
    """
    Configure the Streamlit page with weather theme.
    """
    st.set_page_config(
        page_title="AI Weatherman",
        page_icon="🌤️",
        layout="wide"
    )
    
    # Simple header with weather theme
    st.title("🌤️ AI Weatherman")
    st.subheader("Your AI Weather Assistant")
    
    # Add weather info boxes using columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("🌍 **Global Coverage**\nGet weather for any city worldwide")
    
    with col2:
        st.info("⚡ **Real-time Data**\nTemperature, precipitation and wind")
    
    with col3:
        st.info("📈 **Detailed 7-Day Wind Forecasts**\nWind forecast")
    

def setup_sidebar():
    """
    Create a weather-themed sidebar with information and controls.
    """
    st.sidebar.header("🌦️ Weather Station")
    
    # Weather service info
    with st.sidebar.expander("📡 What can I do?"):
        st.write("""
        I can help you get comprehensive weather information for any location.
        I can query the following tools:
        - Current temperature, precipitation and wind for any city
        - Wind forecast for any city
        - Get the latitude and longitude of any city
        """)
    
    # Quick examples
    with st.sidebar.expander("💡 Try These Examples"):
        st.write("""
        **Sample Questions:**
        - "What's the weather in London?"
        - "Will it rain in Tokyo tomorrow?"
        - "Show me the wind forecast for Miami"
        - "What's the temperature in Sydney?"
        """)
    


def setup_chat_memory():
    """
    Set up conversation memory and history.
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
    Initialize the chat with a welcome message if needed.
    """
    if len(msgs.messages) == 0:
        msgs.add_ai_message(INITIAL_MESSAGE)
        st.session_state.steps = {}


def add_reset_button(msgs):
    """
    Add a reset button in the sidebar.
    """
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🔄 Reset Chat", help="Start a new conversation"):
        msgs.clear()
        msgs.add_ai_message(INITIAL_MESSAGE)
        st.session_state.steps = {}
        st.rerun()
    

def display_chat_messages(msgs):
    """
    Display chat messages with weather-themed avatars.
    """
    avatars = {"human": "🙋‍♂️", "ai": "🌤️"}
    
    for idx, msg in enumerate(msgs.messages):
        with st.chat_message(msg.type, avatar=avatars[msg.type]):
            # Show tool usage for AI messages
            if msg.type == "ai":
                display_intermediate_steps(idx)
            
            # Display the message content
            st.write(msg.content)


def display_intermediate_steps(message_index):
    """
    Display weather tool usage with appropriate icons.
    """
    steps = st.session_state.steps.get(str(message_index), [])
    
    for step in steps:
        if step[0].tool == "_Exception":
            continue
        
        # Weather tool icons
        tool_icons = {
            "geocode_city": "📍",
            "get_city_temperature": "🌡️", 
            "get_city_precipitation": "🌧️",
            "get_city_wind": "💨",
            "get_city_wind_forecast": "🌪️"
        }
        
        tool_name = step[0].tool
        icon = tool_icons.get(tool_name, "🔧")
        display_name = tool_name.replace('_', ' ').title()
        
        with st.status(f"{icon} {display_name}: {step[0].tool_input}", state="complete"):
            st.write("**Reasoning:**", step[0].log)
            st.write("**Result:**", step[1])


def handle_user_input(msgs, memory, backend):
    """
    Handle user input and generate AI response.
    """
    if prompt := st.chat_input(placeholder=CHAT_INPUT_PLACEHOLDER):
        # Display user message
        st.chat_message("human", avatar="🙋‍♂️").write(prompt)
        
        # Process through AI
        with st.chat_message("ai", avatar="🌤️"):
            with st.spinner("🌦️ Checking weather data..."):
                st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
                executor = backend.create_agent_executor(memory)
                response = backend.process_message(prompt, executor, st_cb)
            
            # Display response
            st.write(response["output"])
            
            # Store tool usage steps
            st.session_state.steps[str(len(msgs.messages) - 1)] = response["intermediate_steps"]


def main():
    """
    Main function that runs the AI Weatherman app.
    """
    # Setup page
    setup_page()
    
    # Setup sidebar
    setup_sidebar()
    
    # Initialize backend and memory
    backend = get_backend_instance()
    msgs, memory = setup_chat_memory()
    
    # Initialize chat
    initialize_chat_if_needed(msgs)
    
    # Add controls
    add_reset_button(msgs)
    
    # Display conversation
    display_chat_messages(msgs)
    
    # Handle new input
    handle_user_input(msgs, memory, backend)


if __name__ == "__main__":
    main() 