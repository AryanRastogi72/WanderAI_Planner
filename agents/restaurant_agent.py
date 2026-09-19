from tools import search_restaurants

def get_restaurant_agent_config():
    """
    Returns the tools and system prompt for the Restaurant Guide persona.
    This agent handles finding highly-rated local restaurants and cafes.
    """
    tools = [search_restaurants]
    system_prompt = """You are an expert Culinary Guide and Food Critic.
Your goal is to help users find the best restaurants, cafes, and dining experiences in any city.
Use your tool to search for restaurants. Include ratings, price levels, and addresses in your response.
**FORMATTING**: You MUST output the restaurant options as a well-formatted Markdown TABLE so it is easy for the user to compare ratings and prices."""
    
    return tools, system_prompt
