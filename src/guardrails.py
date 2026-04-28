"""
Input validation and output guardrails for the music recommender.
All functions return (is_valid, list_of_messages).
"""

from typing import Dict, List, Tuple

VALID_MOODS = {
    "happy", "chill", "intense", "sad", "focused",
    "melancholic", "relaxed", "angry", "nostalgic",
    "euphoric", "moody", "romantic", "hopeful", "defiant", "confident",
}


def validate_user_prefs(user_prefs: Dict) -> Tuple[bool, List[str]]:
    """
    Validate a user preference dict before running the recommender.
    Returns (ok, messages) where messages are warnings or errors.
    """
    messages = []

    energy = user_prefs.get("energy")
    if energy is None:
        messages.append("ERROR: 'energy' is required.")
    elif not isinstance(energy, (int, float)) or not (0.0 <= float(energy) <= 1.0):
        messages.append(f"ERROR: 'energy' must be a float in [0.0, 1.0], got {energy!r}.")

    mood = user_prefs.get("mood", "")
    if mood and mood not in VALID_MOODS:
        messages.append(
            f"WARNING: mood {mood!r} is not in the known mood list. "
            f"Genre/energy scoring will still apply."
        )

    genre = user_prefs.get("genre", "")
    if not genre:
        messages.append("WARNING: No genre specified; genre scoring will be skipped.")

    has_error = any(m.startswith("ERROR") for m in messages)
    return not has_error, messages


def validate_recommendations(
    recommendations: List, min_results: int = 1
) -> Tuple[bool, List[str]]:
    """
    Validate the output of recommend_songs before showing it to the user.
    """
    messages = []

    if len(recommendations) < min_results:
        messages.append(
            f"ERROR: Expected at least {min_results} recommendation(s), "
            f"got {len(recommendations)}."
        )

    for i, item in enumerate(recommendations):
        song, score, _ = item
        if not (0.0 <= score <= 1.0):
            messages.append(
                f"WARNING: Score for '{song.get('title', '?')}' is {score:.3f}, "
                f"outside expected [0, 1] range."
            )

    has_error = any(m.startswith("ERROR") for m in messages)
    return not has_error, messages
