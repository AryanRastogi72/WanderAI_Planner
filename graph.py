from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

# Import our modular agent configurations
from agents.travel_agent import get_travel_agent_config
from agents.restaurant_agent import get_restaurant_agent_config
from agents.tour_agent import get_tour_agent_config
from tools import search_flight, search_hotel, search_restaurants, search_activities

# Initialize persistent memory database
# This allows the AI to remember the conversation even if the user refreshes the page
conn = sqlite3.connect("travel_planner_chat.db", check_same_thread=False)
memory = SqliteSaver(conn)

def get_agent_executor(agent_mode: str):
    """
    Dynamically compiles and returns a LangGraph agent based on the selected persona.
    All agents share the same SQLite memory checkpointer so they can read the same chat history.
    """
    # Initialize the LLM (OpenAI's GPT-4o-mini for speed and cost-effectiveness)
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    # Route to the specific agent's configuration based on the user's dropdown selection
    if agent_mode == "Flight & Hotel Planner":
        # Load the travel agent's tools and strict prompt
        tools, system_prompt = get_travel_agent_config()
    elif agent_mode == "Restaurant Guide":
        # Load the restaurant agent's tools and culinary prompt
        tools, system_prompt = get_restaurant_agent_config()
    elif agent_mode == "Tour & Activity Guide":
        # Load the tour guide's tools and excursion prompt
        tools, system_prompt = get_tour_agent_config()
    else:
        # Fallback omni-agent just in case the UI selection fails
        tools = [search_flight, search_hotel, search_restaurants, search_activities]
        system_prompt = "You are a comprehensive AI travel assistant. Format results as Markdown tables."
        
    # Compile the React agent graph
    # This wires up the LLM, the Tools, and the Memory into a single callable agent
    return create_react_agent(
        llm,
        tools,
        prompt=system_prompt,
        checkpointer=memory
    )
