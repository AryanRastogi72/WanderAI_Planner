# Experiment Plan: Budget-First vs Interest-First Planning

| | |
|---|---|
| **Owner** | Aryan Rastogi |
| **Status** | Ready to run, written **before** any data was collected |
| **Related** | [PRD.md](PRD.md) (S5) · [personas.md](personas.md) · [user_test_kit.md](user_test_kit.md) |

> The decision rule below is fixed before the test starts. That's what stops us from picking whichever result looks best afterwards.

## 1. Question

When WanderAI builds an itinerary, should it **start from the budget** or **start from the traveler's interests**?

This is a real product decision. It sets how the default planner behaves, and it tests the persona assumption that budget is the main concern for students (Riya) rather than interests (Meera).

## 2. Hypothesis

> **If** the planner starts from the budget (split money first, then fill days), **then** more users will rate the itinerary 👍, **because** our primary users are students for whom staying within budget matters most.

- **Null hypothesis:** satisfaction is the same in both arms.
- **What would prove us wrong:** interest-first gets a clearly higher 👍 rate. That would mean users value a plan that feels personal over a cheaper one, and Riya's persona needs revisiting.

## 3. Variants

| | A: `budget_first` | B: `interest_first` |
|---|---|---|
| Planning order | Split budget, then cheapest acceptable flight and hotel, then fill days with what's left | Pick activities and food for the user's interests, then fit flight and hotel into what's left, then cut low-priority items if over budget |
| Everything else | Identical: same model (`gpt-4o-mini`, temperature 0), tools, output format and cost calculator | Same |

Only one paragraph of the system prompt differs (`STRATEGIES` in [agents/itinerary_agent.py](../agents/itinerary_agent.py)). Testers aren't told which arm they're in.

## 4. Design

| | |
|---|---|
| **Unit of randomization** | A **trip** (one chat thread), not a person. The assignment is logged as an `experiment_assigned` event the first time the trip asks for an itinerary. |
| **Assignment** | 50/50 random (`random.choice`). A trip keeps its arm even if reopened later. |
| **Why trips, not people** | Each tester plans **2 trips**, which doubles the data and means about half the testers see both arms. They can then say directly which plan they preferred (see §6). |
| **Who** | 10–15 friends and classmates, mostly students (primary persona) |
| **Where** | Live Streamlit Cloud link; events stored in Turso so restarts don't lose data |
| **Duration** | Until [X] testers have finished, or 7 days, whichever comes first |

## 5. Metrics

### Primary (decides the winner)

**Satisfaction rate** = 👍 ÷ all ratings, per arm. It comes from the in-app feedback prompt (`feedback_given` events).

### Secondary (help explain the result)

| Metric | Definition | Why |
|---|---|---|
| Save rate | Trips exported to PDF ÷ trips with an itinerary | A behavioral signal: they wanted to keep it |
| Budget edit share | `itinerary_edited` with `edit_type = budget` ÷ all edits | If budget-first works, fewer "make it cheaper" edits |
| Form preference | For testers who saw both arms: which plan they preferred | Paired comparison, stronger with a small sample |
| Form "would use it" score | 1–5 rating from the feedback form | Intent to use |

### Guardrails (must not get clearly worse)

| Guardrail | Threshold |
|---|---|
| Completion rate | Winner's completion can't be more than 15 points below the other arm |
| Average generation time | Winner can't be more than 30% slower |

## 6. Sample size: what's realistic

| | |
|---|---|
| Testers | 10–15 |
| Trips per tester | 2 |
| Itineraries | about 20–30 total, **about 10–15 per arm** (random, so it may be uneven) |

**What that sample can and can't show** (Fisher's exact test, two-sided, α = 0.05):

| Example result (per arm) | p-value | Read as |
|---|---|---|
| 10/12 vs 6/12 👍 (83% vs 50%) | 0.19 | **Not significant**, even with a 33-point gap |
| 11/12 vs 5/12 (92% vs 42%) | 0.03 | Significant |
| 13/15 vs 7/15 (87% vs 47%) | 0.05 | Borderline |

To reliably detect (80% power) a realistic 20-point improvement, from 60% to 80% 👍, we'd need **about 41 rated itineraries per arm**. This test has roughly a quarter of that.

**So this is a directional pilot, not a conclusive A/B test.** It can catch a large difference. It can't prove a small one. We report it honestly, and use the qualitative feedback and paired preferences to make the call.

## 7. Decision rule (fixed in advance)

1. **Clear winner:** satisfaction is significantly higher (Fisher p < 0.05) and no guardrail fails → ship it as the default.
2. **Directional winner:** satisfaction is at least **20 points** higher, **and** testers who saw both arms preferred it more often than not, **and** no guardrail fails → ship it as the default, and say it's directional.
3. **No clear winner:** anything else → keep `budget_first` as the default (it matches the primary persona and gives tighter cost control). Use the comments to decide what to test next.
4. **Minimum data:** if there are fewer than **8 rated itineraries per arm**, don't call a winner. Recruit more or report "inconclusive".

## 8. Risks to validity

| Risk | Effect | Mitigation |
|---|---|---|
| Testers are friends, so too polite | Satisfaction inflated in both arms | We compare arms, not absolute levels; the form asks "what would you change?" |
| Tiny sample | False winner or missed real effect | Decision rule above; label results "directional" |
| Different trip requests in each arm | Noise (Goa ≠ Ladakh) | Scenario cards in the test kit; record the destination for each trip |
| Order effect (second trip feels better or worse) | Bias in paired preference | Random assignment per trip spreads this across arms |
| Testers skip the 👍/👎 prompt | Missing primary metric | The script explicitly asks them to rate each plan |
| Strategy prompt ignored by the model | Arms aren't really different | Before launch, read 2 sample outputs from each arm and check the plans differ |
| API outages or slowness | Fewer completions | Watch the dashboard on day 1 |

## 9. Analysis plan (Phase 4)

1. Export events with the dashboard's **Download all events (CSV)** button, and export the Google Form responses.
2. Join them on trip code (the first 6 characters of `thread_id`).
3. For each arm, report satisfaction, completion, save rate, budget edit share and average latency, each with its n.
4. Run Fisher's exact test on the 👍/👎 counts.
5. Count paired preferences from the form.
6. Apply the decision rule in §7, then write experiment_results.md.

## 10. Pre-launch checklist

- [ ] Turso set up and `LIBSQL_URL` / `LIBSQL_AUTH_TOKEN` added to Streamlit Cloud secrets
- [ ] One test trip on the live link shows up in the local dashboard
- [ ] 2 sample itineraries read per arm, and the strategies visibly differ
- [ ] Google Form created from [user_test_kit.md](user_test_kit.md)
- [ ] Test rows deleted, or their dates noted, so they can be excluded later
