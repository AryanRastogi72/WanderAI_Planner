# Competitive Analysis

> Based on publicly known features as of late 2026. Competitors ship fast, so **re-check each row in the actual product before using it in an interview or on a resume.** Ratings judge fit for our primary persona (budget-first student, short trip), not overall quality.

## The alternatives

| Alternative | What it is | Why we compare against it |
|---|---|---|
| **MakeMyTrip** | Indian online travel agency: flights, trains, buses, hotels, packages | Where Indian students already book |
| **Google Travel + Maps** | Flight and hotel search, price tracking, saved places | Free, trusted, best data |
| **ChatGPT (plain)** | General LLM chat | What users already try for "plan my trip" |
| **Wanderlog** | Dedicated trip-planner app: itinerary builder, map, shared trips | Closest product to what WanderAI wants to become |

## Feature comparison

✅ strong · ⚠️ partial · ❌ missing

| Capability | MakeMyTrip | Google Travel/Maps | ChatGPT | Wanderlog | **WanderAI today** | **WanderAI v1 (PRD)** |
|---|---|---|---|---|---|---|
| Live flight and hotel prices | ✅ | ✅ | ❌ (or unreliable) | ⚠️ | ✅ via SearchApi | ✅ |
| Restaurants and activities | ⚠️ | ✅ | ⚠️ not live | ✅ | ✅ top 5 results | ✅ |
| Day-by-day itinerary | ⚠️ packages only | ❌ | ✅ | ✅ built by hand | ❌ | ✅ **generated** |
| Total cost vs. budget | ❌ | ❌ | ⚠️ made-up numbers | ⚠️ manual expense tracking | ❌ | ✅ **core feature** |
| Plan from a single natural-language request | ❌ | ❌ | ✅ | ⚠️ | ✅ (options only) | ✅ |
| Booking links | ✅ books directly | ✅ | ❌ | ⚠️ | ✅ | ✅ |
| Share or export the plan | ⚠️ | ⚠️ | ⚠️ copy and paste | ✅ | ⚠️ PDF (bug) | ✅ |
| Group collaboration | ❌ | ⚠️ shared lists | ❌ | ✅ | ❌ | ❌ non-goal |
| Trains and buses (India) | ✅ | ⚠️ | ❌ | ❌ | ❌ | ❌ open question |
| Mobile app | ✅ | ✅ | ✅ | ✅ | ⚠️ web, not tuned for phones | ⚠️ |
| Cost to user | Free (commission) | Free | Free / paid tier | Free / paid tier | Free (portfolio) | Free |

## Where WanderAI wins

1. **Live data plus a generated plan in one step.** ChatGPT writes plans but can't ground them in real prices. Google and MakeMyTrip have real prices but don't write plans. Wanderlog has both, but you build the plan by hand.
2. **Budget check.** Adding up the whole trip against "₹X per person" is the clearest gap across all four alternatives.
3. **Conversational edits.** "Make day 2 cheaper" is one message, not a re-search.

## Where WanderAI loses

1. **Trust and scale.** A student project can't compete with MakeMyTrip's booking guarantees or Google's data coverage.
2. **No trains or buses.** That's a big gap for Indian students, who travel mostly by rail and road. Flights alone undersell the budget story.
3. **No booking or payment.** Users still leave the app to book, so we can't measure whether they actually took the trip.
4. **No collaboration.** Wanderlog wins for group planning.
5. **Speed and cost.** Each request makes several LLM and API calls (seconds per answer, plus a per-request API bill). That's slower than browsing Google.

## Positioning

> **For** students and young professionals planning short budget trips **who** waste hours piecing together a plan from booking sites and ChatGPT, **WanderAI is** an AI trip planner **that** turns one request into a day-by-day plan with live prices and a budget check. **Unlike** ChatGPT, its prices are real; **unlike** MakeMyTrip or Google, it writes the plan for you.

## Implications for the roadmap

- Double down on the **budget check**. It's the clearest gap.
- **Trains and buses** are the biggest gap for the primary persona. Add them to the open questions and the roadmap backlog.
- Don't compete on booking or collaboration in v1.
