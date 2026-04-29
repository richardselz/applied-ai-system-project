"""
Streamlit GUI for the Applied AI Music Recommender.

Select by artist first to filter the song list, or search songs directly.
The app uses the selected song's audio features to find similar tracks.

Run from the project root:
  streamlit run src/app.py
"""

import os
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

from data_loader import load_kaggle_songs
from recommender import recommend_songs
from ai_explainer import explain_recommendations

ALL_ARTISTS = "— All Artists —"

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Music Recommender", page_icon="🎵", layout="centered")
st.title("🎵 Music Recommender")
st.caption("Pick a song you love and we'll find similar ones.")

# ── Load catalog ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading catalog…")
def get_songs(max_songs: int = 5000):
    csv_path = Path(__file__).parent.parent / "data" / "spotify_kaggle.csv"
    return load_kaggle_songs(str(csv_path), max_songs=max_songs)


songs = get_songs()

# Pre-build lookup structures
all_artists = sorted({s["artist"] for s in songs})
songs_by_artist = {}
for s in songs:
    songs_by_artist.setdefault(s["artist"], []).append(s)
label_to_song = {f"{s['title']} — {s['artist']}": s for s in songs}

# ── Filter controls ───────────────────────────────────────────────────────────
st.subheader("Step 1 — Filter by artist (optional)")
selected_artist = st.selectbox(
    "Artist",
    options=[ALL_ARTISTS] + all_artists,
    index=0,
    placeholder="Type to search an artist…",
)

# Build song list based on artist selection
if selected_artist == ALL_ARTISTS:
    filtered_songs = songs
else:
    filtered_songs = songs_by_artist.get(selected_artist, [])

song_labels = sorted({f"{s['title']} — {s['artist']}" for s in filtered_songs})

st.subheader("Step 2 — Select a song")
selected_label = st.selectbox(
    "Song",
    options=song_labels,
    index=0,
    placeholder="Type to search a song…",
)

# ── Options ───────────────────────────────────────────────────────────────────
st.subheader("Step 3 — Options")
top_k = st.slider("Number of recommendations", min_value=1, max_value=10, value=5)
use_ai = st.checkbox(
    "Generate AI explanation (requires GEMINI_API_KEY)",
    value=bool(os.environ.get("GEMINI_API_KEY")),
)

search = st.button("Find similar songs", type="primary")

# ── Results ───────────────────────────────────────────────────────────────────
if search and selected_label:
    seed = label_to_song[selected_label]

    st.success(f"Finding songs similar to **{seed['title']}** by {seed['artist']}")

    with st.expander("Seed song audio profile", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Genre", seed["genre"])
        c2.metric("Mood", seed["mood"])
        c3.metric("Energy", f"{seed['energy']:.2f}")
        c4.metric("Acousticness", f"{seed['acousticness']:.2f}")

    user_prefs = {
        "genre": seed["genre"],
        "mood": seed["mood"],
        "energy": seed["energy"],
        "likes_acoustic": seed["acousticness"] > 0.5,
    }

    catalog = [s for s in songs if s["title"] != seed["title"] or s["artist"] != seed["artist"]]
    recs = recommend_songs(user_prefs, catalog, k=top_k)

    st.subheader(f"Top {top_k} similar songs")
    for rank, (song, score, explanation) in enumerate(recs, 1):
        st.markdown(f"**#{rank} — {song['title']}** by {song['artist']}")
        cols = st.columns(4)
        cols[0].metric("Score", f"{round(score * 100)}/100")
        cols[1].metric("Genre", song["genre"])
        cols[2].metric("Mood", song["mood"])
        cols[3].metric("Energy", f"{song['energy']:.2f}")
        with st.expander("Scoring breakdown"):
            for reason in explanation.split("; "):
                st.write(f"• {reason}")
        st.divider()

    if use_ai:
        with st.spinner("Asking Claude for an explanation…"):
            ai_text = explain_recommendations(user_prefs, recs)
        st.subheader("AI Explanation")
        st.info(ai_text)
