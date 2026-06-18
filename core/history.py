"""Session history — save and load past interview sessions."""

import json
import time
from pathlib import Path
from core.session import InterviewSession

SESSIONS_DIR = Path(__file__).parent.parent / "sessions"


def save_session(session: InterviewSession, report: dict) -> None:
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y-%m-%d-%H-%M")
    filename = SESSIONS_DIR / f"{timestamp}-{session.interview_type}.json"
    data = {
        "timestamp": timestamp,
        "interview_type": session.interview_type,
        "job_role": session.job_role,
        "total_questions": session.total_questions,
        "overall_score": report.get("overall_score"),
        "confidence_score": report.get("confidence_score"),
        "questions": session.questions_asked,
        "question_types": session.question_types,
        "answers": session.answers_given,
        "per_answer_scores": [f.get("score") for f in session.feedback_per_answer],
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_history(limit: int = 10) -> list:
    """Return list of past sessions, most recent first."""
    if not SESSIONS_DIR.exists():
        return []
    files = sorted(SESSIONS_DIR.glob("*.json"), reverse=True)[:limit]
    history = []
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fh:
                history.append(json.load(fh))
        except Exception:
            pass
    return history


def format_history_summary(history: list) -> str:
    """Return a Markdown string summarising past sessions."""
    if not history:
        return ""
    lines = ["### Your Progress Across Sessions", ""]
    for h in history[:5]:
        score = h.get("overall_score", "?")
        conf = h.get("confidence_score", "?")
        itype = h.get("interview_type", "interview").replace("_", " ").title()
        ts = h.get("timestamp", "")
        lines.append(f"- **{ts}** — {itype} | Overall: {score}/10 | Confidence: {conf}/10")
    if len(history) >= 2:
        scores = [h.get("overall_score") for h in history if isinstance(h.get("overall_score"), int)]
        if len(scores) >= 2:
            trend = scores[0] - scores[-1]
            direction = "up" if trend > 0 else "down" if trend < 0 else "steady"
            lines.append(f"\n**Trend:** Score has moved {direction} {abs(trend)} point{'s' if abs(trend) != 1 else ''} over your last {len(scores)} sessions.")
    return "\n".join(lines)
