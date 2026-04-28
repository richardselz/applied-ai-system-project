"""
Evaluation harness for the music recommender.

Runs a fixed set of test cases (profiles + expected criteria) and prints
a pass/fail summary.  Exit code is 0 if all pass, 1 otherwise.

Usage:
  cd applied-ai-system-final
  python src/evaluator.py                          # uses Kaggle dataset
  python src/evaluator.py --csv data/songs.csv     # uses small dataset
"""

import sys
import os
import argparse

# Allow running from any directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from recommender import recommend_songs
from guardrails import validate_user_prefs, validate_recommendations

TEST_CASES = [
    {
        "label": "High-Energy Pop",
        "prefs": {"genre": "pop", "mood": "happy", "energy": 0.9, "likes_acoustic": False},
        "expect_min_results": 1,
        "expect_top_score_above": 0.4,
    },
    {
        "label": "Chill Lofi",
        "prefs": {"genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True},
        "expect_min_results": 1,
        "expect_top_score_above": 0.3,
    },
    {
        "label": "Deep Intense Rock",
        "prefs": {"genre": "rock", "mood": "intense", "energy": 0.95, "likes_acoustic": False},
        "expect_min_results": 1,
        "expect_top_score_above": 0.4,
    },
    {
        "label": "Adversarial: Invalid Energy",
        "prefs": {"genre": "pop", "mood": "happy", "energy": 1.5, "likes_acoustic": False},
        "expect_validation_failure": True,
    },
    {
        "label": "Adversarial: Genre Not in Catalog",
        "prefs": {"genre": "polka", "mood": "happy", "energy": 0.7, "likes_acoustic": False},
        "expect_min_results": 1,
        "expect_top_score_above": 0.0,
    },
    {
        "label": "Adversarial: Conflicting Preferences",
        "prefs": {"genre": "ambient", "mood": "intense", "energy": 0.9, "likes_acoustic": False},
        "expect_min_results": 1,
        "expect_top_score_above": 0.0,
    },
]


def run_evaluation(songs, k: int = 5) -> bool:
    divider = "=" * 60
    print(f"\n{divider}")
    print("  EVALUATION HARNESS")
    print(f"  {len(TEST_CASES)} test cases | catalog size: {len(songs):,} songs")
    print(divider)

    passed = 0
    failed = 0

    for tc in TEST_CASES:
        label = tc["label"]
        prefs = tc["prefs"]
        checks = []

        # Guardrail check
        ok, messages = validate_user_prefs(prefs)

        if tc.get("expect_validation_failure"):
            if not ok:
                checks.append(("Validation correctly rejected bad input", True))
            else:
                checks.append(("Expected validation failure but input passed", False))
            _print_result(label, checks)
            passed += sum(1 for _, v in checks if v)
            failed += sum(1 for _, v in checks if not v)
            continue

        if not ok:
            checks.append((f"Unexpected validation failure: {messages}", False))
            _print_result(label, checks)
            failed += 1
            continue

        recs = recommend_songs(prefs, songs, k=k)

        min_r = tc.get("expect_min_results", 1)
        checks.append((
            f"At least {min_r} result(s) returned (got {len(recs)})",
            len(recs) >= min_r,
        ))

        if recs and "expect_top_score_above" in tc:
            top = recs[0][1]
            threshold = tc["expect_top_score_above"]
            checks.append((
                f"Top score {round(top * 100)}/100 > {round(threshold * 100)}/100",
                top > threshold,
            ))

        out_ok, out_msgs = validate_recommendations(recs, min_results=min_r)
        checks.append(("Output guardrails passed", out_ok))

        _print_result(label, checks)
        passed += sum(1 for _, v in checks if v)
        failed += sum(1 for _, v in checks if not v)

    total = passed + failed
    print(f"\n{divider}")
    print(f"  RESULT: {passed}/{total} checks passed", end="")
    if failed == 0:
        print("  ✓ ALL PASS")
    else:
        print(f"  ✗ {failed} FAILED")
    print(divider)

    return failed == 0


def _print_result(label: str, checks: list) -> None:
    all_ok = all(v for _, v in checks)
    status = "PASS" if all_ok else "FAIL"
    print(f"\n  [{status}] {label}")
    for msg, ok in checks:
        icon = "✓" if ok else "✗"
        print(f"        {icon} {msg}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run recommender evaluation harness")
    parser.add_argument("--csv", default="data/spotify_kaggle.csv", help="Path to song CSV")
    parser.add_argument("--max-songs", type=int, default=5000)
    args = parser.parse_args()

    csv_path = args.csv
    if csv_path.endswith("spotify_kaggle.csv"):
        from data_loader import load_kaggle_songs
        songs = load_kaggle_songs(csv_path, max_songs=args.max_songs)
    else:
        from recommender import load_songs
        songs = load_songs(csv_path)

    all_passed = run_evaluation(songs)
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
