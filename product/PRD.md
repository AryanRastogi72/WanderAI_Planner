# PRD: WanderAI v1, Day-by-Day Budget Itinerary

| | |
|---|---|
| **Owner** | Aryan Rastogi |
| **Status** | Draft |
| **Last updated** | 2026-10-25 |
| **Related** | [problem_statement.md](problem_statement.md) · [personas.md](personas.md) · [competitive_analysis.md](competitive_analysis.md) |

## 1. Summary

WanderAI currently returns **options**: tables of flights, hotels, restaurants and activities, from three personas the user switches between by hand. v1 turns those options into **a plan**: a single day-by-day itinerary built from live data, with a total cost checked against the user's budget, editable through chat and exportable as a PDF.

## 2. Background: current state

| Area | Today |
|---|---|
| Interface | Streamlit chat; persona dropdown (Flight & Hotel / Restaurant / Tour) |
| Intelligence | One LangGraph ReAct agent per persona, `gpt-4o-mini`, temperature 0 |
| Data | SearchApi: Google Flights, Google Hotels, Google Local (top 5 results each) |
| Memory | SQLite checkpointer shared across personas; past threads in the sidebar |
| Output | Markdown comparison tables with booking links; PDF export |
| Measurement | **None.** No analytics, no feedback. |
| Known bugs | PDF exports the previous answer; saved trips show as `Trip a1b2c3...` |

## 3. Problem

Users planning short budget trips spend most of their effort assembling options into days and checking the total against their budget (see [problem_statement.md](problem_statement.md)). WanderAI finds the options but leaves that assembly to the user. Without measurement, we also can't tell whether it helps.

## 4. Goals

1. **Generate a usable plan.** One request produces a day-by-day itinerary with travel, stay, activities and meals.
2. **Make the budget trustworthy.** Show an itemised total from live prices, and clearly flag when the plan goes over budget.
3. **Make it measurable.** Log every step of the funnel and collect feedback on each itinerary, so product decisions rest on data.

## 5. Non-goals (v1)

- Booking or payment inside the app
- Group collaboration or shared editing
- Native mobile app
- Trains and buses (see Open questions)
- Accounts and login (sessions are anonymous)
- Supporting trips longer than 7 days

## 6. Target users

**Primary:** Riya, the budget-first student. **Secondary:** Arjun, the time-poor professional. Meera (interest-first) shapes the A/B test. See [personas.md](personas.md).

## 7. User stories

| ID | As a… | I want to… | So that… |
|---|---|---|---|
| US1 | student | enter destination, dates, budget and interests in one message | I don't fill in forms or switch personas |
| US2 | student | get a day-by-day plan (morning / afternoon / evening) | I can follow it without rebuilding it myself |
| US3 | student | see an itemised cost breakdown and total vs. my budget | I know the group can afford it |
| US4 | student | be warned clearly if the plan goes over budget, with cheaper swaps | I can fix it before booking |
| US5 | professional | ask for a change ("make Saturday more relaxed") in chat | I don't start over |
| US6 | professional | click booking links for flights and hotels in the plan | I can book the same evening |
| US7 | any user | export the **current** plan as a PDF | I can share it on WhatsApp |
| US8 | any user | give thumbs up or down plus a comment on a plan | the product gets better |
| US9 | returning user | see past trips by destination name | I can find my Goa plan again |
| US10 | product owner | see a funnel and satisfaction dashboard | I can decide what to build next |

## 8. Requirements (MoSCoW)

### Must have

| ID | Requirement | Story |
|---|---|---|
| M1 | **Itinerary mode**: one agent that uses all four tools and outputs a day-by-day plan in a fixed format | US1, US2 |
| M2 | Extract budget, dates, origin, destination and travelers from the request; ask one follow-up question if something is missing | US1 |
| M3 | Itemised cost table (travel, stay, food estimate, activities) with total and per-person total, using live prices where available and marking estimates clearly | US3 |
| M4 | Over-budget warning plus at least one cheaper alternative | US4 |
| M5 | Fix PDF export so it exports the itinerary shown on screen | US7 |
| M6 | Analytics events in SQLite: `itinerary_requested`, `itinerary_generated`, `itinerary_edited`, `itinerary_saved`, `feedback_given`, each with timestamp, session id and latency | US10 |
| M7 | Thumbs up/down plus optional comment shown after each itinerary | US8 |

### Should have

| ID | Requirement | Story |
|---|---|---|
| S1 | Edits through chat ("make day 2 cheaper") regenerate only what changed; logged as `itinerary_edited` with an edit type | US5 |
| S2 | Booking links inside the itinerary | US6 |
| S3 | Metrics dashboard (Streamlit page): funnel, completion rate, average generation time, satisfaction, top edit types | US10 |
| S4 | Name saved trips by destination and dates | US9 |
| S5 | A/B assignment per session between two generation strategies (budget-first vs. interest-first) | — |

### Could have

| ID | Requirement |
|---|---|
| C1 | Keep the three persona modes as an "explore options" mode next to itinerary mode |
| C2 | Show travel time between stops |
| C3 | Prices in INR by default (the currency helper already exists in `api.py`) |
| C4 | Phone-friendly layout tweaks |

### Won't have (v1)

Booking/payments · accounts · collaboration · trains/buses · native app

## 9. Success metrics

> No baselines exist yet. **Targets stay as placeholders until real data from Phase 2–3 comes in.** Don't fill them with guesses.

### North Star metric

**Useful itineraries per week:** itineraries that get a thumbs-up **or** are exported to PDF.

*Why this one:* it counts plans that delivered value (the user liked it or took it with them), not just plans that were generated. It moves only when quality and usefulness both hold up.

### Supporting metrics

| Metric | Definition | Why it matters | Target |
|---|---|---|---|
| **Completion rate** | `itinerary_generated` ÷ `itinerary_requested` | Catches failures, errors and drop-offs | [X%] |
| **Generation time** | Median (and p90) latency from request to itinerary | Slow means abandoned; ChatGPT is fast | [X s] |
| **Satisfaction rate** | Thumbs up ÷ all `feedback_given` | Direct quality signal; the A/B test metric | [X%] |
| **Edit rate and top edit types** | Sessions with ≥1 `itinerary_edited` ÷ sessions with an itinerary; grouped by type | Many "make cheaper" edits mean the first draft misses the budget | [X%] |

### Guardrail

**Cost per itinerary** (OpenAI + SearchApi calls). It must stay within the free/student budget: [₹X per itinerary].

## 10. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| LLM makes up prices or places that don't exist | Med | High (breaks trust, the core promise) | Only quote prices that come from tool results; label everything else "estimate" |
| Budget totals wrong (arithmetic or missing items) | Med | High | Compute totals in Python, not in the LLM |
| Slow generation (many tool calls in sequence) | High | Med | Log latency; limit tool calls; show progress |
| SearchApi or OpenAI cost or rate limits | Med | Med | Cache identical searches; small test group |
| Sample too small for a meaningful A/B result | High | Med | Treat it as directional; collect qualitative feedback too (see experiment_plan.md in Phase 3) |
| No trains or buses makes Indian student plans unrealistic | High | Med | Say so in the UI; top roadmap candidate |
| Storing user comments raises privacy concerns | Low | Med | No personal data collected; anonymous session ids only |

## 11. Open questions

1. Do students mostly travel by train or bus? If so, is flights-only v1 still useful to them, or is a train data source a must-have?
2. Should itinerary mode replace the three personas or sit beside them?
3. How do we estimate food costs without a reliable price source? (Google Local returns `₹₹` levels, not amounts.)
4. What counts as an "edit": any follow-up message, or only ones that change the plan?
5. Is a PDF the right way to share, or would a WhatsApp-friendly text block work better?
6. What can we spend on API calls during the test period?

## 12. Milestones

| Phase | Deliverable |
|---|---|
| 1 | Discovery docs (this PRD) |
| 2 | Analytics events, feedback prompt, dashboard; itinerary mode (M1–M7) |
| 3 | A/B test setup, experiment_plan.md, user test with [X] testers |
| 4 | experiment_results.md, RICE roadmap, README rewrite |
