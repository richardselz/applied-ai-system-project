# Reflection on AI Collaboration and System Design

---

## How I Used AI During Development

AI was used in large part for brainstorming and developing of ideas. Then it was used to generate a lot of code that was partialy reviewed and then fully tested for functionality. 

---

## One Helpful AI Suggestion

The biggest helpful thing that Claude provided was a suggestion to go from a terminal app to a Streamlit GUI. 

---

## One Flawed AI Suggestion

Claude tried to allow me to use the Claude API, but I was unable to provide it with an API key that would work. It then added in Geminis API, but it provided the wrong Gemini API before switching to the correct one. It also decided to use the more token intensive version before opting for lite.

---

## System Limitations

The sytem was supposed seemlessly ask Claude or Gemini for a breakdown of it's decision, but that has fallen short as the API keys that I was able to generate would not function.

---

## Future Improvements

The future improvements would be to actually have the AI explanations working.

---
∂
## Original Profile Comparison Notes (Module 3)

### Pair 1: High-Energy Pop vs Chill Lofi

These profiles are opposites and the results reflect that — no song overlaps between their top 5 lists.
Gym Hero still appears for the pop user despite being "intense" not "happy" because the 40% genre bonus rewards any pop song before mood is considered.

---

### Pair 2: Deep Intense Rock vs Conflicting Preferences (Ambient + Intense + High Energy)

Rock produced a clean winner (Storm Runner at 98), but the conflicting profile surfaced a soft ambient track at rank 3 purely on genre bonus, exposing the filter bubble.
When preferences contradict each other, the system picks the genre match and ignores that the song is wrong in every other way.

---

### Pair 3: Genre Not in Catalog (Country) vs All Midrange

Both profiles produced compressed scores (peak ~60) compared to the 90s seen in standard profiles, showing the system needs at least one strong categorical match to produce confident recommendations.
