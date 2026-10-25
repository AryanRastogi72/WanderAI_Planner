import os
import json
import random
import sqlite3
from datetime import datetime, timezone

# Analytics live in their own database so they never mix with the chat memory
DB_PATH = "analytics.db"

# Streamlit Cloud wipes its disk on every restart, so in the cloud we use Turso (hosted SQLite).
# Set LIBSQL_URL and LIBSQL_AUTH_TOKEN (in .env locally, or in Streamlit Cloud "Secrets") to turn it on.
# Without them, everything is stored in the local analytics.db file as before.
TURSO_URL = os.environ.get("LIBSQL_URL")
TURSO_TOKEN = os.environ.get("LIBSQL_AUTH_TOKEN")


def _connect(db_path):
    if TURSO_URL and db_path == DB_PATH:
        import libsql  # only needed when Turso is configured
        # "Embedded replica": a local copy that syncs with the cloud. Writes go straight to the cloud.
        conn = libsql.connect("analytics_replica.db", sync_url=TURSO_URL, auth_token=TURSO_TOKEN)
        # ponytail: syncs on every call (one network round trip); keep one shared connection if logging feels slow
        conn.sync()
    else:
        conn = sqlite3.connect(db_path)
    # One row per event. "props" holds any extra details as a JSON string
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            session_id TEXT NOT NULL,
            thread_id TEXT NOT NULL,
            event TEXT NOT NULL,
            latency_ms INTEGER,
            props TEXT
        )
    """)
    conn.commit()
    return conn


def log_event(event, session_id, thread_id, latency_ms=None, db_path=DB_PATH, **props):
    """
    Saves one analytics event with a UTC timestamp.
    Example: log_event("itinerary_generated", sid, tid, latency_ms=4200, mode="Day-by-Day Itinerary")
    """
    conn = _connect(db_path)
    conn.execute(
        "INSERT INTO events (ts, session_id, thread_id, event, latency_ms, props) VALUES (?, ?, ?, ?, ?, ?)",
        (datetime.now(timezone.utc).isoformat(), session_id, thread_id, event, latency_ms, json.dumps(props)),
    )
    conn.commit()  # without commit the row is thrown away
    conn.close()


# A/B test arms. Each trip (thread) gets one of these at random and keeps it, even if reopened later.
VARIANTS = ["budget_first", "interest_first"]


def get_variant(thread_id, db_path=DB_PATH):
    """Returns this trip's A/B variant, or None if it hasn't been assigned yet."""
    conn = _connect(db_path)
    row = conn.execute(
        "SELECT json_extract(props, '$.variant') FROM events WHERE event = 'experiment_assigned' AND thread_id = ?",
        (thread_id,),
    ).fetchone()
    conn.close()
    return row[0] if row else None


def assign_variant(session_id, thread_id, db_path=DB_PATH):
    """Randomly picks a variant for a new trip and logs the assignment."""
    variant = random.choice(VARIANTS)
    log_event("experiment_assigned", session_id, thread_id, db_path=db_path, variant=variant)
    return variant


def thread_has_event(thread_id, event, db_path=DB_PATH):
    """True if this trip already logged the event (e.g. so a clarifying question doesn't count as a second request)."""
    conn = _connect(db_path)
    row = conn.execute("SELECT 1 FROM events WHERE thread_id = ? AND event = ?", (thread_id, event)).fetchone()
    conn.close()
    return row is not None


def has_feedback(message_id, db_path=DB_PATH):
    """True if this itinerary message was already rated, so we don't ask twice."""
    conn = _connect(db_path)
    row = conn.execute(
        "SELECT 1 FROM events WHERE event = 'feedback_given' AND json_extract(props, '$.message_id') = ?",
        (message_id,),
    ).fetchone()
    conn.close()
    return row is not None


# Keyword -> edit type. The first matching group wins, so order matters.
EDIT_KEYWORDS = {
    "budget": ["cheap", "budget", "cost", "price", "afford", "expensive", "save money"],
    "stay": ["hotel", "hostel", "stay", "room"],
    "food": ["food", "restaurant", "eat", "cafe", "veg", "dinner", "lunch", "breakfast"],
    "activities": ["activity", "activities", "museum", "tour", "visit", "adventure", "trek"],
    "travel": ["flight", "train", "bus", "airport"],
    # Last, because words like "day" appear in almost every edit request
    "schedule": ["day", "morning", "evening", "relax", "packed", "time", "earlier", "later"],
}


def classify_edit(text):
    """
    Guesses what kind of change the user asked for, e.g. "make day 2 cheaper" -> "budget".
    # ponytail: keyword matching misses phrasings it doesn't know; switch to an LLM classifier if "other" gets large
    """
    text = text.lower()
    for edit_type, words in EDIT_KEYWORDS.items():
        if any(word in text for word in words):
            return edit_type
    return "other"


def compute_metrics(db_path=DB_PATH):
    """Reads all events and returns the numbers the dashboard shows."""
    conn = _connect(db_path)

    def scalar(sql):
        return conn.execute(sql).fetchone()[0]

    # Funnel = how many trips (threads) reached each step at least once
    funnel = {}
    for step in ["itinerary_requested", "itinerary_generated", "itinerary_edited", "itinerary_saved", "feedback_given"]:
        funnel[step] = scalar(f"SELECT COUNT(DISTINCT thread_id) FROM events WHERE event = '{step}'")

    requested = scalar("SELECT COUNT(*) FROM events WHERE event = 'itinerary_requested'")
    generated = scalar("SELECT COUNT(*) FROM events WHERE event = 'itinerary_generated'")
    ratings = conn.execute(
        "SELECT json_extract(props, '$.rating') FROM events WHERE event = 'feedback_given'"
    ).fetchall()
    thumbs_up = sum(1 for (r,) in ratings if r == "up")

    edit_types = dict(conn.execute("""
        SELECT json_extract(props, '$.edit_type'), COUNT(*) FROM events
        WHERE event = 'itinerary_edited' GROUP BY 1 ORDER BY 2 DESC
    """).fetchall())

    comments = conn.execute("""
        SELECT replace(substr(ts, 1, 16), 'T', ' '), json_extract(props, '$.rating'), json_extract(props, '$.comment') FROM events
        WHERE event = 'feedback_given' AND json_extract(props, '$.comment') != '' ORDER BY ts DESC
    """).fetchall()

    metrics = {
        "funnel": funnel,
        "completion_rate": generated / requested if requested else None,
        "avg_generation_s": scalar("SELECT AVG(latency_ms) FROM events WHERE event = 'itinerary_generated'"),
        "satisfaction_rate": thumbs_up / len(ratings) if ratings else None,
        "feedback_count": len(ratings),
        "edit_types": edit_types,
        "comments": comments,
    }
    if metrics["avg_generation_s"] is not None:
        metrics["avg_generation_s"] /= 1000
    conn.close()
    return metrics


def compute_variant_metrics(db_path=DB_PATH):
    """A/B results: one row per variant, counting only trips that were assigned to an experiment arm."""
    conn = _connect(db_path)
    rows = conn.execute("""
        WITH assigned AS (
            SELECT thread_id, json_extract(props, '$.variant') AS variant
            FROM events WHERE event = 'experiment_assigned'
        )
        SELECT a.variant,
            COUNT(DISTINCT CASE WHEN e.event = 'itinerary_requested' THEN e.thread_id END),
            COUNT(DISTINCT CASE WHEN e.event = 'itinerary_generated' THEN e.thread_id END),
            AVG(CASE WHEN e.event = 'itinerary_generated' THEN e.latency_ms END) / 1000.0,
            COUNT(DISTINCT CASE WHEN e.event = 'itinerary_edited' THEN e.thread_id END),
            COUNT(DISTINCT CASE WHEN e.event = 'itinerary_saved' THEN e.thread_id END),
            SUM(e.event = 'feedback_given'),
            SUM(e.event = 'feedback_given' AND json_extract(e.props, '$.rating') = 'up')
        FROM assigned a JOIN events e ON e.thread_id = a.thread_id
        GROUP BY a.variant ORDER BY a.variant
    """).fetchall()
    conn.close()
    keys = ["variant", "requested", "generated", "avg_generation_s", "edited", "saved", "feedback", "thumbs_up"]
    return [dict(zip(keys, row)) for row in rows]


def storage_status(db_path=DB_PATH):
    """One line for the ?debug=1 sidebar: where analytics are stored and how many events exist."""
    conn = _connect(db_path)
    count = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    conn.close()
    return f"{'Turso (cloud)' if TURSO_URL else 'local file'} · {count} events"


EVENT_COLUMNS = ["id", "ts", "session_id", "thread_id", "event", "latency_ms", "props"]


def all_events(db_path=DB_PATH):
    """Every raw event row, for the CSV download used in the Phase 4 analysis."""
    conn = _connect(db_path)
    rows = conn.execute(f"SELECT {', '.join(EVENT_COLUMNS)} FROM events ORDER BY id").fetchall()
    conn.close()
    return rows


if __name__ == "__main__":
    # Self-check with a throwaway database: python analytics.py
    import os, tempfile
    test_db = os.path.join(tempfile.mkdtemp(), "test.db")

    assert classify_edit("Make day 2 cheaper") == "budget"
    assert classify_edit("Swap the hotel for a hostel") == "stay"
    assert classify_edit("hmm") == "other"

    log_event("itinerary_requested", "s1", "t1", db_path=test_db)
    log_event("itinerary_generated", "s1", "t1", latency_ms=4000, db_path=test_db)
    log_event("itinerary_requested", "s2", "t2", db_path=test_db)  # this one never completed
    log_event("itinerary_edited", "s1", "t1", db_path=test_db, edit_type="budget")
    log_event("feedback_given", "s1", "t1", db_path=test_db, rating="up", comment="nice", message_id="m1")

    m = compute_metrics(test_db)
    assert m["funnel"]["itinerary_requested"] == 2 and m["funnel"]["itinerary_generated"] == 1
    assert m["completion_rate"] == 0.5
    assert m["avg_generation_s"] == 4.0
    assert m["satisfaction_rate"] == 1.0
    assert m["edit_types"] == {"budget": 1}
    assert has_feedback("m1", test_db) and not has_feedback("m2", test_db)
    assert thread_has_event("t2", "itinerary_requested", test_db) and not thread_has_event("t2", "itinerary_generated", test_db)

    # A/B: t1 is budget_first (completed, 👍), t2 is interest_first (never completed)
    assert get_variant("t1", test_db) is None
    log_event("experiment_assigned", "s1", "t1", db_path=test_db, variant="budget_first")
    log_event("experiment_assigned", "s2", "t2", db_path=test_db, variant="interest_first")
    assert get_variant("t1", test_db) == "budget_first"
    assert assign_variant("s3", "t3", test_db) in VARIANTS
    rows = {r["variant"]: r for r in compute_variant_metrics(test_db)}
    assert rows["budget_first"]["generated"] == 1 and rows["budget_first"]["thumbs_up"] == 1
    assert rows["budget_first"]["edited"] == 1
    assert rows["interest_first"]["requested"] == 1 and rows["interest_first"]["generated"] == 0
    assert len(all_events(test_db)) == 8
    print("analytics self-check passed")
