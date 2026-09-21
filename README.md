<div align="center">
  <img src="https://cdn-icons-png.flaticon.com/512/2060/2060284.png" width="120" alt="WanderAI Logo">
  <h1>🌍 WanderAI Planner</h1>
  <p><strong>Your Intelligent, Multi-Persona Travel Assistant</strong></p>
  
  [![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
  [![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)](https://streamlit.io/)
  [![LangGraph](https://img.shields.io/badge/LangGraph-Stateful_Agents-orange.svg)](https://python.langchain.com/docs/langgraph)
</div>

---

## ✨ Overview

WanderAI is a state-of-the-art conversational travel planner powered by large language models, dynamic tooling, and a robust memory system. 

Instead of a single bot, WanderAI utilizes a **Multi-Persona Agent Architecture**. You can seamlessly switch between specialized expert agents mid-conversation:
- ✈️ **Flight & Hotel Planner:** Books your travel using live Google Flights and Google Hotels data.
- 🍽️ **Restaurant Guide:** A culinary expert that finds the highest-rated local dining spots.
- 🗺️ **Tour & Activity Guide:** A local concierge that recommends excursions and museums.

Because all agents share the same persistent memory checkpointer (SQLite), you can book a flight to Paris with the *Travel Planner*, then instantly switch to the *Restaurant Guide* and ask *"Where can I eat near my hotel?"* without ever repeating yourself!

## 🚀 Features

- **Live Data:** Fetches real-time flights, hotels, restaurants, and activities via SearchApi.
- **Dynamic Personas:** Switch between specialized agents on the fly.
- **Persistent Memory:** Conversations are saved locally. You can close the app and resume your trip planning days later.
- **Trip History:** Dropdown interface to switch between past saved trips.
- **PDF Export:** Download a beautiful, offline PDF of your generated itineraries.
- **Markdown Tables:** Agent results are strictly formatted into comparative tables for easy reading.

---

## 📂 Project Structure

The project has been carefully modularized for easy scaling and readability:

```text
WanderAI/
├── app.py                     # The beautiful Streamlit frontend UI (sidebar, chat, custom CSS)
├── graph.py                   # Compiles the LangGraph agent & handles persistent SQLite memory
├── tools.py                   # Contains the core tools connecting to live external APIs
├── pdf_generator.py           # Uses fpdf2 to convert Markdown itineraries into downloadable PDFs
├── api.py                     # Helper functions for API connections and currency conversion
├── agents/                    # Multi-Agent configurations
│   ├── travel_agent.py        # Prompts & tools for the Flight/Hotel Planner
│   ├── restaurant_agent.py    # Prompts & tools for the Restaurant Guide
│   └── tour_agent.py          # Prompts & tools for the Tour & Activity Guide
└── travel_planner_chat.db     # Local SQLite database storing conversation history
```

## 🛠️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AryanRastogi72/Multi_Agent_AI_Travel_Planner.git
   cd Multi_Agent_AI_Travel_Planner
   ```

2. **Install dependencies:**
   Make sure you have `streamlit`, `langchain-openai`, `langgraph`, `requests`, `python-dotenv`, and `fpdf2` installed.
   ```bash
   pip install streamlit langchain-openai langgraph requests python-dotenv fpdf2
   ```

3. **Set up API Keys:**
   Create a `.env` file in the root directory and add your keys:
   ```env
   OPENAI_API_KEY="your_openai_key"
   SEARCHAPI_API_KEY="your_searchapi_key"
   ```

4. **Run the application:**
   ```bash
   streamlit run app.py
   ```

---

## 🎨 UI Showcase

WanderAI features a meticulously designed custom Streamlit interface:
- **Dark-Mode Compatible:** Custom CSS automatically adapts to your system theme.
- **Sidebar Navigation:** Quickly start new trips or select saved threads.
- **Beautiful Avatars:** Distinguishes between you and the expert AI personas.

<div align="center">
  <p><i>"The future of travel planning is conversational."</i></p>
</div>
