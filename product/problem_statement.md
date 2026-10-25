# Problem Statement

> Status: hypothesis. Nothing here has been validated with users yet. Claims marked **[to validate]** need evidence from interviews or the Phase 3 test before they go on a resume or into a pitch.

## The problem in one sentence

Planning a short trip on a fixed budget means juggling 5+ tabs (flights, hotels, food, things to do, a notes app). No single tool turns "I have ₹X and 3 days" into a plan you can actually follow.

## Who has it

People planning **short (2–5 day), budget-constrained, self-organised trips**, mainly:

- **College students** planning trips with friends. Budget is the hardest constraint, and the plan has to work for the whole group.
- **Early-career professionals** planning weekend getaways. Time is the hardest constraint: they want a good plan in minutes, not an evening of research.

Both groups plan trips themselves rather than through a travel agent or a package tour, and both already use search engines and ChatGPT.

## What the job looks like today

A typical planning session **[to validate]**:

1. Search flights or trains on a booking site and note prices.
2. Search hotels or hostels on a second site.
3. Google "things to do in X" and read 2–3 blog posts.
4. Search restaurants on Google Maps or Zomato.
5. Copy everything into a notes app or WhatsApp and try to fit it into days.
6. Add up costs by hand to check it fits the budget.

Steps 5 and 6 are where the time goes. **No tool does them for you.**

## Why existing options fall short

| Option | What it's good at | Where it falls short for this user |
|---|---|---|
| **MakeMyTrip / booking sites** | Booking flights, trains and hotels; deals | Built for booking one item at a time. No day-by-day plan, nothing for food or activities, and no check that the whole trip fits a budget. |
| **Google Travel / Google Maps** | Flight price tracking, hotel search, saved places | Strong data, but you assemble the plan yourself. Saved places aren't a schedule. |
| **Plain ChatGPT** | Fast, flexible, good at writing day-by-day plans | No live prices or availability, so plans can include closed places or made-up costs. You can't trust the budget total, and there are no booking links. |

**The gap:** a tool that combines **live prices** (what booking sites have) with an **organised, budget-checked day-by-day plan** (what ChatGPT writes, but can't ground in real data).

## What WanderAI does today vs. the gap

| Today | Gap this PRD closes |
|---|---|
| Live flights, hotels, restaurants and activities via SearchApi (Google data) | ✅ Live data is already there |
| One chat, three personas, shared memory | Partly there: the user still has to switch persona by hand |
| Comparison tables with booking links | Tables are options, **not a plan** |
| PDF export | Exports the previous answer (bug) |
| — | **No day-by-day itinerary** |
| — | **No budget total or budget check** |

## How we'll know we solved it

See the success metrics in [PRD.md](PRD.md). In short: users get a day-by-day plan they say they would actually use, within their budget, in one session.

## Riskiest assumptions

1. Users actually feel steps 5–6 (assembling the plan) as the painful part, not just finding options. **[to validate]**
2. Users trust an AI plan enough to use it if prices are live. **[to validate]**
3. A budget check matters more to students than a polished UI. **[to validate]**
