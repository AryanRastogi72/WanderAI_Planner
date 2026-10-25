<div align="center">
  <img src="https://cdn-icons-png.flaticon.com/512/2060/2060284.png" width="110" alt="WanderAI Logo">
  <h1>🌍 WanderAI Planner</h1>
  <p><strong>One message in, a day-by-day trip plan out, with live prices and a budget you can trust.</strong></p>

  [![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
  [![Streamlit](https://img.shields.io/badge/Streamlit-1.38+-red.svg)](https://streamlit.io/)
  [![LangGraph](https://img.shields.io/badge/LangGraph-Agents-orange.svg)](https://langchain-ai.github.io/langgraph/)

  🚀 **[Try the live app](https://wanderaiplanner-ftdc2cbyvhyqxbsvnbbpbk.streamlit.app/)**
</div>

---

## 🧩 The problem

Planning a short trip on a fixed budget means juggling **5+ tabs**: flights, hotels, food, things to do, and a notes app to add it all up.

| Option | Good at | Falls short because |
|---|---|---|
| **MakeMyTrip / booking sites** | Live prices, booking | Books one item at a time; no day-by-day plan, no whole-trip budget check |
| **Google Travel / Maps** | Great data, saved places | You still put the plan together yourself |
| **ChatGPT** | Writes nice day-by-day plans | No live prices, so its budget totals can't be trusted |

**WanderAI combines the two halves:** live prices from Google Flights, Hotels and Local, plus a generated day-by-day plan whose costs are **added up in code, not guessed by the LLM**.

→ Full write-up: [problem statement](product/problem_statement.md) · [competitive analysis](product/competitive_analysis.md)

## 👥 Who it's for

| Persona | Situation | What they need most |
|---|---|---|
| **Riya, the budget-first student** *(primary)* | 3-day trip with friends, hard budget | A per-person total she can trust, and a plan she can share |
| **Arjun, the time-poor professional** | Weekend getaway, planned in under 30 minutes | A realistic schedule and booking links |
| **Meera, the interest-led explorer** | Solo trip built around food or history | Plans built around her interests, not a tourist checklist |

These are **proto-personas**: assumptions to test, not research findings. → [personas](product/personas.md)

## ✨ What it does

- **🗓️ Day-by-day itinerary mode:** describe the trip in one message. You get a morning / afternoon / evening plan, an itemised cost table and booking links.
- **💰 Budget check computed in Python:** a dedicated `calculate_trip_cost` tool adds up every line, flags over-budget plans and lists unpriced items. The LLM never does the arithmetic.
- **✏️ Conversational edits:** "make day 2 cheaper" updates the plan in place.
- **🤖 Specialist personas:** Flight & Hotel, Restaurant, and Tour & Activity agents that share one conversation memory.
- **📄 PDF export** and **👍/👎 feedback** on every itinerary.

→ Full spec: [PRD](product/PRD.md)

## 📏 How success is measured

The app is instrumented to answer one question: **does it produce plans people actually use?**

| | Metric | Definition |
|---|---|---|
| ⭐ **North Star** | **Useful itineraries per week** | Itineraries rated 👍 **or** exported to PDF |
| Supporting | Completion rate | Itineraries generated ÷ requested |
| Supporting | Generation time | Median and p90 latency from request to plan |
| Supporting | Satisfaction rate | 👍 ÷ all ratings |
| Supporting | Edit rate and edit types | How often and why users change the first draft (budget, stay, food…) |
| Guardrail | Cost per itinerary | OpenAI and SearchApi spend per plan |

**How it's tracked:**
- **5 funnel events:** `itinerary_requested` → `generated` → `edited` → `saved` → `feedback_given`, with timestamps and latency, stored in a hosted SQLite database (Turso).
- **A metrics dashboard** (`dashboard.py`): funnel, completion, generation time, satisfaction, top edit types, A/B results and CSV export.

### 🧪 Experiment: budget-first vs interest-first planning

Should the planner **start from the money or from the traveler**? Each new trip is randomly assigned one of two planning strategies:

| `budget_first` | `interest_first` |
|---|---|
| The budget is a hard limit; cheapest flight and hotel; mostly free activities | Searches for each interest; two interest-matched stops a day; best-rated hotel within 15% over budget |

The [experiment plan](product/experiment_plan.md) sets out, **before any data is collected**:
- the hypothesis
- the primary metric (satisfaction rate)
- the guardrails
- a sample-size analysis: a 10–15 person pilot can only show **directional** results
- a fixed decision rule

**Status:** ⏳ **The user pilot hasn't run yet.** There are no user results here, on purpose. They'll be added after the pilot.

## 🔍 What I learned in pre-launch testing

Before asking anyone to test it, I ran the full flow on the live app myself. It found problems that unit tests would have missed.

| Finding | Why it mattered | Fix |
|---|---|---|
| Plans showed **"Over budget by ₹X"**, a literal placeholder | Broke the core promise of trustworthy totals | Two root causes: hotel prices were read from the wrong API fields, and the cost tool crashed on text like "₹4,500". Fixed both. |
| **Flight fares counted once** for a 3-person group | The trip looked far cheaper than it was | Fares are now labelled per person, and Python multiplies by travelers |
| **Round-trip fares counted twice** (outbound + return) | Totals inflated by a whole fare | One flight line per trip, enforced in the tool output and prompt |
| **Both A/B variants produced the same plan** | The experiment could never have found a difference | Rewrote each strategy as explicit rules, then checked that the same request now gives different plans |
| The first fix made interest-first **118% over budget** | Unfair test: it would measure "blew the budget", not "interest-led" | Capped interest-first at 15% over, with a check-and-revise step |
| **Analytics lost on every restart** (Streamlit Cloud wipes its disk) | Test data would disappear | Moved analytics to hosted SQLite (Turso); confirmed it survives redeploys |
| Feedback took **~20 s** to save, because every database call re-synced with the cloud | Testers would give up | Sync once per app start; a typical page update now takes **~2.5 s** |
| No flights to small airports (e.g. Manali) | Many Indian students travel by train or bus | The prompt now falls back to an estimated train/bus cost (not yet re-tested); real rail data is a **roadmap candidate** |

**What I took away:** with an LLM product, the riskiest bugs are the ones that *look* plausible, like a confident total that's wrong. That's why every number now comes from code, and why the experiment was checked before launch, not after.

## 🛠️ Tech stack

| Layer | Tools |
|---|---|
| Agents | **LangGraph** ReAct agents with tool calling, **OpenAI** `gpt-4o-mini` |
| Live data | **SearchApi**: Google Flights, Google Hotels, Google Local; Frankfurter (currency) |
| App and dashboard | **Streamlit** |
| Data | **SQLite** (chat memory), **Turso / libSQL** (hosted analytics) |
| Other | fpdf2 (PDF export), Streamlit Community Cloud (hosting) |

```text
WanderAI_Planner/
├── app.py                  # Streamlit chat UI, analytics events, feedback form
├── dashboard.py            # Product metrics dashboard (run separately)
├── analytics.py            # Event logging, A/B assignment, metric queries (SQLite / Turso)
├── graph.py                # Builds the LangGraph agent for the selected mode
├── tools.py                # Flight / hotel / restaurant / activity search + cost calculator
├── agents/
│   ├── itinerary_agent.py  # Day-by-day planner + the two A/B strategies
│   ├── travel_agent.py     # Flight & Hotel persona
│   ├── restaurant_agent.py # Restaurant persona
│   └── tour_agent.py       # Tour & Activity persona
├── pdf_generator.py        # Itinerary → PDF
├── api.py                  # API key + currency helpers
└── product/                # PM docs: problem, personas, competition, PRD, experiment plan, test kit
```

## 🚀 Run it locally

```bash
git clone https://github.com/AryanRastogi72/WanderAI_Planner.git
cd WanderAI_Planner
pip install -r requirements.txt
```

Create a `.env` file in the project folder:

```env
OPENAI_API_KEY="your_openai_key"
SEARCHAPI_API_KEY="your_searchapi_key"
# Optional: store analytics in Turso instead of the local analytics.db file
LIBSQL_URL="libsql://your-db.turso.io"
LIBSQL_AUTH_TOKEN="your_turso_token"
```

```bash
streamlit run app.py         # the planner
streamlit run dashboard.py   # the metrics dashboard
```

## 🗺️ What's next

1. **Run the user pilot** (10–15 testers) and publish the results: [test kit](product/user_test_kit.md)
2. A **RICE-prioritized roadmap** based on that feedback
3. Candidates already spotted in testing: train/bus data, schedules that respect flight times, keeping the hotel and activities in the same area
