from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import uuid
import time
from langchain_core.messages import HumanMessage, AIMessage
from graph import get_agent_executor
from pdf_generator import generate_itinerary_pdf
from agents.itinerary_agent import ITINERARY_MARKER
from analytics import log_event, thread_has_event, has_feedback, classify_edit, get_variant, assign_variant

ITINERARY_MODE = "Day-by-Day Itinerary"

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

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2060/2060284.png", width=100)
    st.markdown("### Welcome to WanderAI")
    
    st.markdown("---")
    
    # AGENT SELECTION DROPDOWN
    st.markdown("### 🤖 Agent Persona")
    agent_mode = st.selectbox(
        "Choose your expert:",
        [ITINERARY_MODE, "Flight & Hotel Planner", "Restaurant Guide", "Tour & Activity Guide"],
        help="Switching personas mid-conversation will change the agent's capabilities while keeping your chat history intact!"
    )
    
    st.markdown("---")
    
    # Conversation History
    st.markdown("### 🗂️ Saved Trips")
    
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())

    # One id per browser visit, for analytics (a visit can contain several trips/threads)
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    # Only trips started in this browser tab are listed, so users never see each other's chats.
    # ponytail: trips are forgotten when the tab closes; needs user accounts to bring back "resume later"
    if "my_trips" not in st.session_state:
        st.session_state.my_trips = [st.session_state.thread_id]

    if st.button("➕ Start New Trip"):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.my_trips.insert(0, st.session_state.thread_id)  # newest first
        st.rerun()

    if len(st.session_state.my_trips) > 1:
        options = st.session_state.my_trips

        selected_thread = st.selectbox(
            "Switch Conversation:",
            options=options,
            index=options.index(st.session_state.thread_id),
            format_func=lambda x: f"Trip {x[:6]}..."
        )
        
        if selected_thread != st.session_state.thread_id:
            st.session_state.thread_id = selected_thread
            st.rerun()

    # Testers paste this into the feedback form so their answers can be matched to their trip
    st.caption(f"Trip code: `{st.session_state.thread_id[:6]}`")

    st.markdown("---")
    st.caption("Powered by **OpenAI**, **SearchApi**, and **LangGraph**")

# Get the compiled graph based on the user's selected Agent Mode.
# variant is this trip's A/B test arm (None until its first itinerary request, see below)
variant = get_variant(st.session_state.thread_id)
agent_executor = get_agent_executor(agent_mode, variant or "budget_first")
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

# Shortcuts used by the analytics calls below
session_id = st.session_state.session_id
thread_id = st.session_state.thread_id
has_itinerary = any(isinstance(m, AIMessage) and ITINERARY_MARKER in m.content for m in messages)

# Handle new user input
if prompt := st.chat_input(f"Chat with the {agent_mode}..."):
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # The first itinerary-mode message of a trip is the "request"; follow-ups are logged after the reply
    if agent_mode == ITINERARY_MODE and not has_itinerary and not thread_has_event(thread_id, "itinerary_requested"):
        # A/B test: a new trip gets a random planning strategy here and keeps it from now on
        if variant is None:
            variant = assign_variant(session_id, thread_id)
            agent_executor = get_agent_executor(agent_mode, variant)
        log_event("itinerary_requested", session_id, thread_id, prompt=prompt, variant=variant)

    with st.chat_message("assistant", avatar="✈️"):
        with st.spinner(f"The {agent_mode} is searching..."):
            try:
                start = time.time()
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
                latency_ms = int((time.time() - start) * 1000)

                if agent_mode == ITINERARY_MODE:
                    if has_itinerary:
                        # Any message after an itinerary exists counts as an edit request
                        log_event("itinerary_edited", session_id, thread_id, latency_ms,
                                  edit_type=classify_edit(prompt), prompt=prompt)
                    elif ITINERARY_MARKER in final_response:
                        log_event("itinerary_generated", session_id, thread_id, latency_ms)

                # Rerun so the new reply loads from memory like the rest of the chat.
                # This also makes the PDF button and feedback form use the newest itinerary.
                st.rerun()

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

last_ai = next((m for m in reversed(messages) if isinstance(m, AIMessage) and m.content), None)

# Feedback prompt under the latest itinerary (asked once per itinerary)
if last_ai and ITINERARY_MARKER in last_ai.content:
    message_id = last_ai.id or f"{thread_id}-{len(messages)}"
    if not has_feedback(message_id):
        with st.form(f"feedback_{message_id}", clear_on_submit=True):
            st.markdown("**How useful is this itinerary?**")
            rating = st.feedback("thumbs")  # returns 1 for 👍, 0 for 👎, None if not clicked
            comment = st.text_input("Anything we should change? (optional)")
            if st.form_submit_button("Send feedback"):
                if rating is None:
                    st.warning("Please pick 👍 or 👎 first.")
                else:
                    log_event("feedback_given", session_id, thread_id,
                              rating="up" if rating == 1 else "down", comment=comment.strip(), message_id=message_id)
                    st.rerun()
    else:
        st.caption("✅ Thanks for your feedback!")

# Export to PDF button (only show if there is an AI response in history)
if last_ai:
    st.markdown("---")
    col1, col2 = st.columns([1, 4])
    with col1:
        pdf_bytes = generate_itinerary_pdf(last_ai.content)
        st.download_button(
            label="📄 Export to PDF",
            data=pdf_bytes,
            file_name="WanderAI_Itinerary.pdf",
            mime="application/pdf",
            # Exporting an itinerary counts as "saving" it (one of the North Star signals)
            on_click=log_event if ITINERARY_MARKER in last_ai.content else "ignore",
            args=("itinerary_saved", session_id, thread_id),
        )
