"""
Command-line runner for the Applied AI Music Recommender.

Usage examples:
  # Use small built-in catalog, plain output
  python src/main.py

  # Use Kaggle dataset
  python src/main.py --kaggle

  # Use Kaggle dataset + AI explanations (requires ANTHROPIC_API_KEY)
  python src/main.py --kaggle --ai

  # Use full agentic workflow with visible intermediate steps
  python src/main.py --kaggle --agent

  # Run evaluation harness instead of recommendations
  python src/main.py --kaggle --eval
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from recommender import load_songs, recommend_songs

PROFILES = [
    {"label": "High-Energy Pop",      "genre": "pop",     "mood": "happy",   "energy": 0.9,  "likes_acoustic": False},
    {"label": "Chill Lofi",           "genre": "lofi",    "mood": "chill",   "energy": 0.35, "likes_acoustic": True},
    {"label": "Deep Intense Rock",    "genre": "rock",    "mood": "intense", "energy": 0.95, "likes_acoustic": False},
    {"label": "Adversarial: Country", "genre": "country", "mood": "happy",   "energy": 0.7,  "likes_acoustic": False},
    {"label": "Adversarial: Conflict","genre": "ambient", "mood": "intense", "energy": 0.9,  "likes_acoustic": False},
    {"label": "Adversarial: Midrange","genre": "jazz",    "mood": "focused", "energy": 0.5,  "likes_acoustic": False},
]


def print_recommendations(label: str, recommendations: list) -> None:
    divider = "=" * 56
    print(f"\n{divider}")
    print(f"  PROFILE: {label}")
    print(f"  TOP {len(recommendations)} RECOMMENDATIONS")
    print(divider)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"\n  #{rank}  {song['title']} by {song['artist']}")
        print(f"       Genre: {song['genre']} | Mood: {song['mood']}")
        print(f"       Score: {round(score * 100)}/100")
        print(f"       Why:")
        for reason in explanation.split("; "):
            print(f"         - {reason}")
    print(f"\n{divider}")


def run_plain(songs: list) -> None:
    for profile in PROFILES:
        prefs = {k: v for k, v in profile.items() if k != "label"}
        recs = recommend_songs(prefs, songs, k=5)
        print_recommendations(profile["label"], recs)


def run_with_ai(songs: list) -> None:
    from guardrails import validate_user_prefs
    from ai_explainer import explain_recommendations

    for profile in PROFILES:
        prefs = {k: v for k, v in profile.items() if k != "label"}
        ok, messages = validate_user_prefs(prefs)
        for m in messages:
            print(f"  {m}")
        if not ok:
            print(f"  Skipping {profile['label']} due to validation errors.")
            continue

        recs = recommend_songs(prefs, songs, k=5)
        print_recommendations(profile["label"], recs)

        print("\n  AI Explanation:")
        explanation = explain_recommendations(prefs, recs)
        for line in explanation.splitlines():
            print(f"    {line}")


def run_agent_mode(songs: list) -> None:
    from agent import run_agent

    for profile in PROFILES:
        label = profile["label"]
        prefs = {k: v for k, v in profile.items() if k != "label"}
        divider = "=" * 56
        print(f"\n{divider}")
        print(f"  AGENT RUN: {label}")
        print(divider)

        result = run_agent(prefs, songs, k=5, verbose=True)

        if result["recommendations"]:
            print("\n  Final Recommendations:")
            for rank, (song, score, _) in enumerate(result["recommendations"], 1):
                print(f"    #{rank} {song['title']} by {song['artist']} ({round(score*100)}/100)")

        if result["explanation"]:
            print("\n  AI Explanation:")
            for line in result["explanation"].splitlines():
                print(f"    {line}")

        if result["critique"]:
            print(f"\n  Quality Critique: {result['critique']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Applied AI Music Recommender")
    parser.add_argument("--kaggle", action="store_true", help="Use Kaggle Spotify dataset")
    parser.add_argument("--max-songs", type=int, default=5000, help="Max songs to load from Kaggle")
    parser.add_argument("--ai", action="store_true", help="Add Claude AI explanations")
    parser.add_argument("--agent", action="store_true", help="Use full agentic workflow")
    parser.add_argument("--eval", action="store_true", help="Run evaluation harness")
    args = parser.parse_args()

    # Load songs
    if args.kaggle:
        from data_loader import load_kaggle_songs
        csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "spotify_kaggle.csv")
        songs = load_kaggle_songs(csv_path, max_songs=args.max_songs)
    else:
        csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "songs.csv")
        songs = load_songs(csv_path)

    if args.eval:
        from evaluator import run_evaluation
        run_evaluation(songs)
    elif args.agent:
        run_agent_mode(songs)
    elif args.ai:
        run_with_ai(songs)
    else:
        run_plain(songs)


if __name__ == "__main__":
    main()
