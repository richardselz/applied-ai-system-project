"""
Multi-step agentic workflow for the music recommender.

Each step is printed so intermediate reasoning is observable in the output.

Steps:
  1. Validate & normalise input (guardrails)
  2. Run the recommender against the song catalog
  3. Self-critique: flag if results look weak (low top score)
  4. Generate an AI explanation via the RAG explainer
"""

from typing import Dict, List, Tuple

from guardrails import validate_user_prefs, validate_recommendations
from recommender import recommend_songs
from ai_explainer import explain_recommendations


def run_agent(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    verbose: bool = True,
) -> Dict:
    """
    Run the full agentic pipeline and return a result dict with keys:
      recommendations, explanation, warnings, critique
    """

    def log(msg: str) -> None:
        if verbose:
            print(msg)

    result = {
        "recommendations": [],
        "explanation": "",
        "warnings": [],
        "critique": "",
    }

    # ── Step 1: Validate input ────────────────────────────────────────────────
    log("\n[Agent Step 1] Validating user preferences...")
    ok, messages = validate_user_prefs(user_prefs)
    for m in messages:
        log(f"  {m}")
        result["warnings"].append(m)
    if not ok:
        log("  Input validation failed. Aborting.")
        return result
    log("  Input looks good.")

    # ── Step 2: Run recommender ───────────────────────────────────────────────
    log(f"\n[Agent Step 2] Scoring {len(songs):,} songs against profile...")
    recommendations = recommend_songs(user_prefs, songs, k=k)
    result["recommendations"] = recommendations
    log(f"  Retrieved {len(recommendations)} candidates.")

    # ── Step 3: Validate output & self-critique ───────────────────────────────
    log("\n[Agent Step 3] Checking output quality...")
    out_ok, out_msgs = validate_recommendations(recommendations)
    for m in out_msgs:
        log(f"  {m}")
        result["warnings"].append(m)

    if recommendations:
        top_score = recommendations[0][1]
        if top_score < 0.5:
            critique = (
                f"Top score is only {round(top_score * 100)}/100. "
                "The catalog may lack a strong genre or mood match for this profile. "
                "Consider broadening preferences or adding more songs."
            )
        else:
            critique = f"Strong top match at {round(top_score * 100)}/100."
        result["critique"] = critique
        log(f"  Critique: {critique}")

    # ── Step 4: Generate AI explanation ──────────────────────────────────────
    log("\n[Agent Step 4] Generating AI explanation...")
    explanation = explain_recommendations(user_prefs, recommendations)
    result["explanation"] = explanation
    log("  Explanation ready.")

    return result
