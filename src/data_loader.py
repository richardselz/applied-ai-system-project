"""
Loads and normalizes the Kaggle Spotify dataset into the schema used by
recommender.py: id, title, artist, genre, mood, energy, tempo_bpm,
valence, danceability, acousticness.

Mood is not present in the Kaggle data, so it is derived from valence
and energy using a simple quadrant rule.
"""

import csv
from typing import List, Dict


def derive_mood(valence: float, energy: float) -> str:
    if valence >= 0.6 and energy >= 0.6:
        return "happy"
    if valence >= 0.6 and energy < 0.6:
        return "chill"
    if valence < 0.4 and energy >= 0.6:
        return "intense"
    if valence < 0.4 and energy < 0.4:
        return "sad"
    return "focused"


def load_kaggle_songs(csv_path: str, max_songs: int = 5000) -> List[Dict]:
    """
    Read the Kaggle Spotify CSV and return a list of song dicts normalised
    to the same schema as songs.csv.  Rows with missing or unparseable
    numeric fields are skipped silently.
    """
    songs = []
    seen_ids = set()

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if len(songs) >= max_songs:
                break
            try:
                track_id = row.get("track_id", "").strip()
                if track_id in seen_ids:
                    continue
                seen_ids.add(track_id)

                energy = float(row["energy"])
                valence = float(row["valence"])

                song = {
                    "id": i,
                    "title": row["track_name"].strip(),
                    "artist": row["artists"].strip(),
                    "genre": row["track_genre"].strip().lower(),
                    "mood": derive_mood(valence, energy),
                    "energy": energy,
                    "tempo_bpm": int(float(row["tempo"])),
                    "valence": valence,
                    "danceability": float(row["danceability"]),
                    "acousticness": float(row["acousticness"]),
                }
                songs.append(song)
            except (ValueError, KeyError):
                continue

    print(f"Loaded {len(songs)} songs from Kaggle dataset.")
    return songs
