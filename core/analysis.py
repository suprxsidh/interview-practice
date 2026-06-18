"""Lightweight transcript analysis — filler words, duration, STAR ratio heuristics."""

import re

FILLER_WORDS = [
    "um", "uh", "er", "ah", "hmm",
    "like", "you know", "you know what i mean",
    "basically", "literally", "actually", "honestly",
    "so", "right", "okay", "kind of", "sort of",
    "i mean", "i guess", "i think", "i feel like",
    "that's a great question",  # flagged by interviewers as credibility killer
]


def count_filler_words(transcript: str) -> dict:
    """Return a dict of filler_word → count for any word that appears ≥1 time."""
    text = transcript.lower()
    counts = {}
    for filler in FILLER_WORDS:
        pattern = r'\b' + re.escape(filler) + r'\b'
        found = re.findall(pattern, text)
        if found:
            counts[filler] = len(found)
    return counts


def filler_summary(counts: dict) -> str:
    """Human-readable summary of filler word usage."""
    if not counts:
        return ""
    total = sum(counts.values())
    top = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:3]
    detail = ", ".join(f'"{w}" ×{c}' for w, c in top)
    return f"{total} filler word{'s' if total != 1 else ''} ({detail})"


def duration_feedback(seconds: float) -> str:
    """Return coaching note about answer duration."""
    if seconds < 20:
        return "Very brief — aim for 60-90 seconds for strong interview answers."
    if seconds < 40:
        return "A little short — try to develop your answer further with specific details."
    if seconds > 240:
        return "Running long — practice tightening to under 3 minutes."
    if seconds > 180:
        return "Slightly long — aim to wrap up a touch sooner."
    return ""


def detect_humblebrag(transcript: str) -> bool:
    """Detect common humblebrag patterns in weakness answers."""
    lower = transcript.lower()
    humblebrag_patterns = [
        r"i work too hard",
        r"i'?m? too? (passionate|dedicated|committed|perfectionis)",
        r"i care too much",
        r"i'?m? too (detail.oriented|thorough|meticulous)",
        r"i push (myself|my team) too hard",
        r"i set (too high|very high) standards",
        r"i take on too much",
    ]
    return any(re.search(p, lower) for p in humblebrag_patterns)


def score_progression_trend(scores: list) -> str:
    """Return a human-readable trend description."""
    if len(scores) < 2:
        return "Not enough data for trend."
    avg_first_half = sum(scores[:len(scores)//2]) / (len(scores)//2)
    avg_second_half = sum(scores[len(scores)//2:]) / (len(scores) - len(scores)//2)
    diff = avg_second_half - avg_first_half
    if diff > 0.4:
        return f"Improving — your average score rose from {avg_first_half:.1f} to {avg_second_half:.1f} across the session."
    if diff < -0.4:
        return f"You started stronger (avg {avg_first_half:.1f}) than you finished (avg {avg_second_half:.1f}). Fatigue or harder questions? Either way, work on sustaining energy."
    return f"Consistent performance throughout (avg {avg_first_half:.1f} → {avg_second_half:.1f})."
