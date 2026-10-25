# User Test Kit

Everything you need to run the experiment in [experiment_plan.md](experiment_plan.md) with 10–15 friends or classmates.

---

## Part 0: Setup (for you, once, ~15 minutes)

### 1. Create the Turso database (free)
1. Sign up at [turso.tech](https://turso.tech) and create a database, e.g. `wanderai-analytics`.
2. Copy its **database URL** (starts with `libsql://`).
3. Create a **database token** for it and copy that too.

### 2. Add the keys to Streamlit Cloud
In your app on share.streamlit.io: **⋮ → Settings → Secrets**, add:

```toml
LIBSQL_URL = "libsql://wanderai-analytics-<your-org>.turso.io"
LIBSQL_AUTH_TOKEN = "<your token>"
```

Streamlit turns these into environment variables, which `analytics.py` reads. The app restarts on save.

### 3. Add the same two lines to your local `.env`
Then `streamlit run dashboard.py` on your laptop reads the live test data from Turso.

### 4. Smoke test
- Plan one trip on the live link and rate it.
- Refresh your local dashboard and check it appears.
- Plan 2–3 more trips until you've seen **both** variants (the A/B table shows which arm each trip got). Check the plans actually differ.
- Note the date and time you finish, so these test rows can be excluded in Phase 4.

---

## Part 1: Recruiting message (WhatsApp / DM)

> Hey! I've built an AI trip planner for my portfolio and I need **10 minutes** of honest feedback 🙏
>
> You'd plan two quick trips (real or dream ones), rate the plans, and fill in a 2-minute form. Brutal honesty is way more useful to me than nice comments.
>
> Can you try it before **[day]**? I'll send the link if you're in!

Send to more people than you need, about 20, to end up with 10–15.

---

## Part 2: Instructions to send testers (with the link)

> Thanks for helping! 🙌 Link: **[your Streamlit link]**
>
> 1. Keep **"Day-by-Day Itinerary"** selected in the left sidebar.
> 2. **Trip 1:** type one message like this (fill in your own):
>    *"Plan a 3-day trip from Delhi to Rishikesh for 3 friends, Dec 20–22, total budget ₹15,000. We like adventure and cafes."*
>    Include **from where, where to, dates, how many people, total budget and what you like**.
> 3. Read the plan. If you'd change something, just ask in the chat (e.g. *"make day 2 cheaper"*).
> 4. **Rate the plan with 👍 or 👎** under it, and add a comment if you can. This is the most important step!
> 5. Note your **Trip code** from the sidebar.
> 6. Click **➕ Start New Trip** and repeat for **Trip 2** (a different destination).
> 7. Fill in the form, using both trip codes: **[Google Form link]**
>
> Please don't put personal details (phone numbers, addresses) in the chat.

**No trip idea? Use a scenario card:**

| Card | Request |
|---|---|
| 🏖️ Beach | Delhi → Goa, 4 days, 4 friends, ₹30,000 total, beaches and nightlife |
| 🏔️ Hills | Delhi → Manali, 3 days, 2 people, ₹12,000 total, nature and cafes |
| 🏛️ Culture | Mumbai → Jaipur, 3 days, solo, ₹10,000, history and street food |
| 💼 Weekend | Bengaluru → Pondicherry, 2 days, 2 people, ₹15,000, relaxed, food |

---

## Part 3: If you test in person (optional, ~10 minutes each)

In-person sessions give you the best quotes for interviews. Stay quiet and take notes.

1. **Before:** "I'm testing the product, not you. Think out loud. There are no wrong answers."
2. **Watch, don't help.** If they get stuck, ask "What would you do now?" before you explain anything.
3. **Note:** where they hesitate, what they scroll past, what they say about prices, and whether they'd open the booking links.
4. **After both trips, ask:**
   - "Which of the two plans was better? Why?"
   - "Would you actually follow this plan? What would stop you?"
   - "How do you usually plan trips like this today?"
   - "If this disappeared tomorrow, would you miss it?"

Write down exact quotes. They're more useful in Phase 4 than summaries.

---

## Part 4: Feedback form (create it in Google Forms)

Keep it to about 2 minutes. Questions:

**About you**
1. You are a… *(Student / Working professional / Other)*
2. How do you usually travel on short trips? *(Train / Bus / Flight / Car / Mix)* ← answers PRD open question 1
3. What do you use to plan trips today? *(checkboxes: MakeMyTrip, Google, ChatGPT, Instagram/YouTube, friends, other)*

**Trip 1**
4. Trip 1 code *(short answer)*
5. How useful was the plan? *(1 = useless … 5 = very useful)*
6. Would you actually use this plan? *(Yes as-is / Yes with changes / No)*
7. Did the costs look realistic? *(1–5)*

**Trip 2**
8. Trip 2 code
9. How useful was the plan? *(1–5)*
10. Would you actually use this plan? *(Yes as-is / Yes with changes / No)*
11. Did the costs look realistic? *(1–5)*

**Overall**
12. Which plan was better? *(Trip 1 / Trip 2 / About the same)*
13. Why? *(short answer)*
14. Most useful thing about WanderAI? *(short answer)*
15. Most frustrating or missing thing? *(short answer)*
16. How likely are you to use WanderAI for your next trip? *(0–10)*

**Tips**
- Make questions 4–7 required and 8–13 optional, in case someone only does one trip.
- When responses come in, **File → Download → CSV** for Phase 4.

---

## Part 5: During the test

| When | Do |
|---|---|
| Day 1 | Check the dashboard: are trips completing? Errors? Both arms getting trips? |
| Every 2 days | Nudge people who said yes but haven't tried it |
| End | Download the events CSV (dashboard) and the form CSV, then start Phase 4 |

**Don't** change prompts or code mid-test. Any change splits the data into "before" and "after".
