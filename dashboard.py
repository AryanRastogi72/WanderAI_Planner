# Product metrics dashboard. Run it separately from the app:  streamlit run dashboard.py
# It only reads analytics.db, so it never affects what users see.
import pandas as pd
import streamlit as st
from analytics import compute_metrics, compute_variant_metrics, all_events, EVENT_COLUMNS

st.set_page_config(page_title="WanderAI Metrics", page_icon="📊", layout="wide")
st.title("📊 WanderAI Product Metrics")

m = compute_metrics()

if m["funnel"]["itinerary_requested"] == 0:
    st.info("No data yet. Generate an itinerary in the app (Day-by-Day Itinerary mode) and refresh this page.")
    st.stop()


def pct(value):
    return "—" if value is None else f"{value:.0%}"


# Headline numbers
col1, col2, col3, col4 = st.columns(4)
col1.metric("Completion rate", pct(m["completion_rate"]), help="Itineraries generated ÷ itineraries requested")
col2.metric("Avg generation time", f"{m['avg_generation_s']:.1f} s" if m["avg_generation_s"] else "—")
col3.metric("Satisfaction rate", pct(m["satisfaction_rate"]), help="👍 ÷ all feedback")
col4.metric("Feedback responses", m["feedback_count"])

# Funnel: how many trips reached each step
st.subheader("Funnel (trips reaching each step)")
funnel = pd.DataFrame({
    "Step": ["1. Requested", "2. Generated", "3. Edited", "4. Saved (PDF)", "5. Feedback given"],
    "Trips": list(m["funnel"].values()),
})
st.bar_chart(funnel, x="Step", y="Trips", horizontal=True)

left, right = st.columns(2)
with left:
    st.subheader("Most common edit types")
    if m["edit_types"]:
        edits = pd.DataFrame({"Edit type": list(m["edit_types"]), "Count": list(m["edit_types"].values())})
        st.bar_chart(edits, x="Edit type", y="Count")
    else:
        st.caption("No edits yet.")

with right:
    st.subheader("Latest feedback comments")
    if m["comments"]:
        comments = pd.DataFrame(m["comments"], columns=["Time (UTC)", "Rating", "Comment"])
        st.dataframe(comments, hide_index=True, width="stretch")
    else:
        st.caption("No comments yet.")

# A/B test: budget-first vs interest-first planning (see product/experiment_plan.md)
st.subheader("A/B test: budget-first vs interest-first")
variants = compute_variant_metrics()
if variants:
    def rate(part, whole):
        return f"{part / whole:.0%} ({part}/{whole})" if whole else "—"

    st.dataframe(pd.DataFrame([{
        "Variant": v["variant"],
        "Trips requested": v["requested"],
        "Completion": rate(v["generated"], v["requested"]),
        "Satisfaction (👍)": rate(v["thumbs_up"], v["feedback"]),
        "Saved (PDF)": rate(v["saved"], v["generated"]),
        "Edited": rate(v["edited"], v["generated"]),
        "Avg generation (s)": round(v["avg_generation_s"], 1) if v["avg_generation_s"] else None,
    } for v in variants]), hide_index=True, width="stretch")
    st.caption("Small samples: treat differences as directional. The decision rule is in experiment_plan.md.")
else:
    st.caption("No trips assigned to a variant yet.")

# Raw data for the Phase 4 analysis
events_csv = pd.DataFrame(all_events(), columns=EVENT_COLUMNS).to_csv(index=False)
st.download_button("⬇️ Download all events (CSV)", events_csv, file_name="wanderai_events.csv", mime="text/csv")
