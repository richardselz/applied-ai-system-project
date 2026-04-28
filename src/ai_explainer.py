"""
RAG-based explanation layer using the Claude API.

Given a user profile and a ranked list of recommended songs, this module
builds a context document from the retrieved songs and asks Claude to
generate a natural-language explanation of why those songs were chosen.

Requires ANTHROPIC_API_KEY in the environment.  If the key is absent the
module degrades gracefully and returns a plain-text fallback.
"""

import os
from pathlib import Path
from typing import Dict, List, Tuple

from dotenv import load_dotenv

# Load .env from the project root (one level above src/)
load_dotenv(Path(__file__).parent.parent / ".env")

_MODEL = "claude-haiku-4-5-20251001"


def _build_context(user_prefs: Dict, recommendations: List[Tuple]) -> str:
    profile_lines = [
        f"  Genre preference : {user_prefs.get('genre', 'any')}",
        f"  Mood preference  : {user_prefs.get('mood', 'any')}",
        f"  Target energy    : {user_prefs.get('energy', 0.5):.2f}  (0 = calm, 1 = intense)",
        f"  Likes acoustic   : {user_prefs.get('likes_acoustic', False)}",
    ]

    song_lines = []
    for rank, (song, score, reasons) in enumerate(recommendations, 1):
        song_lines.append(
            f"  #{rank} {song['title']} by {song['artist']}\n"
            f"      Genre: {song['genre']} | Mood: {song['mood']} | "
            f"Energy: {song['energy']:.2f} | Score: {round(score * 100)}/100\n"
            f"      Scoring breakdown: {reasons}"
        )

    return (
        "USER PROFILE\n" + "\n".join(profile_lines) +
        "\n\nTOP RECOMMENDED SONGS\n" + "\n\n".join(song_lines)
    )


def explain_recommendations(
    user_prefs: Dict,
    recommendations: List[Tuple],
    model: str = _MODEL,
) -> str:
    """
    Call Claude with the retrieved song context and return a natural-language
    explanation.  Falls back to a plain summary if no API key is set.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return _fallback_explanation(recommendations)

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        context = _build_context(user_prefs, recommendations)
        prompt = (
            "You are a music recommendation assistant. Using ONLY the information "
            "in the context below, write a concise 3-5 sentence explanation of why "
            "these songs were recommended for this listener. Mention specific song "
            "titles and how they match the user's taste.\n\n"
            f"{context}"
        )

        response = client.messages.create(
            model=model,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()

    except Exception as e:
        return f"[AI explanation unavailable: {e}]\n" + _fallback_explanation(recommendations)


def _fallback_explanation(recommendations: List[Tuple]) -> str:
    lines = ["Top picks based on your profile:"]
    for rank, (song, score, _) in enumerate(recommendations, 1):
        lines.append(f"  #{rank} {song['title']} by {song['artist']} (score: {round(score * 100)}/100)")
    return "\n".join(lines)
