from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import uuid
import sqlite3
from langchain_core.messages import HumanMessage, AIMessage
from graph import get_agent_executor
from pdf_generator import generate_itinerary_pdf

# Must be the first Streamlit command
st.set_page_config(
    page_title="WanderAI Planner",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a beautiful, modern UI
st.markdown("""
<style>
    /* Header styling */
    .hero {
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        padding: 40px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .hero h1 {
        color: white;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        margin-bottom: 10px;
    }
    .hero p {
        font-size: 1.2rem;
        opacity: 0.9;
        color: white;
    }
    
    /* Input box styling */
    .stChatInput {
        border-radius: 20px !important;
    }
    
    .st-emotion-cache-16idsys p {
        font-size: 1.05rem;
    }
</style>
""", unsafe_allow_html=True)

# Application Header
st.markdown("""
<div class="hero">
    <h1>🌍 WanderAI Planner</h1>
    <p>Your intelligent, conversational travel assistant powered by live data.</p>
</div>
""", unsafe_allow_html=True)

# Fetch all past threads from SQLite
def get_past_threads():
    try:
        conn = sqlite3.connect("travel_planner_chat.db")
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT thread_id FROM checkpoints")
        threads = [row[0] for row in cursor.fetchall()]
        conn.close()
        return threads
    except Exception:
        return []

past_threads = get_past_threads()

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2060/2060284.png", width=100)
    st.markdown("### Welcome to WanderAI")
    
    st.markdown("---")
    
    # AGENT SELECTION DROPDOWN
    st.markdown("### 🤖 Agent Persona")
    agent_mode = st.selectbox(
        "Choose your expert:",
        ["Flight & Hotel Planner", "Restaurant Guide", "Tour & Activity Guide"],
        help="Switching personas mid-conversation will change the agent's capabilities while keeping your chat history intact!"
    )
    
    st.markdown("---")
    
    # Conversation History
    st.markdown("### 🗂️ Saved Trips")
    
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())
        
    if st.button("➕ Start New Trip"):
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()
        
    if past_threads:
        options = past_threads
        if st.session_state.thread_id not in options:
            options = [st.session_state.thread_id] + options
            
        selected_thread = st.selectbox(
            "Switch Conversation:",
            options=options,
            index=options.index(st.session_state.thread_id),
            format_func=lambda x: f"Trip {x[:6]}..."
        )
        
        if selected_thread != st.session_state.thread_id:
            st.session_state.thread_id = selected_thread
            st.rerun()

    st.markdown("---")
    st.caption("Powered by **OpenAI**, **SearchApi**, and **LangGraph**")

# Get the compiled graph based on the user's selected Agent Mode
agent_executor = get_agent_executor(agent_mode)
config = {"configurable": {"thread_id": st.session_state.thread_id}}

# Fetch conversation history from the checkpointer
try:
    state = agent_executor.get_state(config)
    messages = state.values.get("messages", [])
except Exception as e:
    messages = []

# Display conversation history
for msg in messages:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user", avatar="👤"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage):
        if msg.content:
            with st.chat_message("assistant", avatar="✈️"):
                st.markdown(msg.content)

# Handle new user input
if prompt := st.chat_input(f"Chat with the {agent_mode}..."):
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    
    with st.chat_message("assistant", avatar="✈️"):
        with st.spinner(f"The {agent_mode} is searching..."):
            try:
                events = agent_executor.stream(
                    {"messages": [("user", prompt)]}, 
                    config=config, 
                    stream_mode="values"
                )
                
                final_response = ""
                for event in events:
                    if "messages" in event:
                        last_message = event["messages"][-1]
                        if isinstance(last_message, AIMessage) and last_message.content:
                            final_response = last_message.content
                
                st.markdown(final_response)
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Export to PDF button (only show if there is an AI response in history)
if messages:
    last_ai_message = next((m.content for m in reversed(messages) if isinstance(m, AIMessage) and m.content), None)
    if last_ai_message:
        st.markdown("---")
        col1, col2 = st.columns([1, 4])
        with col1:
            pdf_bytes = generate_itinerary_pdf(last_ai_message)
            st.download_button(
                label="📄 Export to PDF",
                data=pdf_bytes,
                file_name="WanderAI_Itinerary.pdf",
                mime="application/pdf"
            )
