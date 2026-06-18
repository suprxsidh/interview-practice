import json
import re
import google.generativeai as genai

from core.prompts import (
    build_first_question_prompt,
    build_evaluate_prompt,
    build_report_prompt,
    build_warmup_prompt,
)
from core.session import InterviewSession
from core.analysis import count_filler_words

_TRANSIENT_ERRORS = (ConnectionError, TimeoutError, OSError)


def _call_gemini(api_key: str, prompt: str, retries: int = 3) -> dict:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    last_err = None
    for attempt in range(retries):
        try:
            response = model.generate_content(prompt)
            text = response.text.strip()
            text = re.sub(r"^```json\s*", "", text, flags=re.MULTILINE)
            text = re.sub(r"```\s*$", "", text, flags=re.MULTILINE).strip()
            return json.loads(text)
        except json.JSONDecodeError as e:
            last_err = e
            if attempt < retries - 1:
                prompt += "\n\nCRITICAL: Return ONLY valid JSON. No markdown, no code fences, no extra text before or after."
        except _TRANSIENT_ERRORS as e:
            last_err = e
        except Exception as e:
            err_str = str(e).lower()
            if any(t in err_str for t in ("503", "502", "unavailable", "timeout", "connection")):
                last_err = e
            else:
                raise RuntimeError(f"Gemini API error: {e}") from e
    raise RuntimeError(f"Gemini call failed after {retries} attempts: {last_err}")


def generate_warmup_question(session: InterviewSession, api_key: str) -> str:
    prompt = build_warmup_prompt(session)
    result = _call_gemini(api_key, prompt)
    question = result.get("question", "What's something you're proud of from this past year?")
    session.questions_asked.append(question)
    session.question_types.append("opener")
    session.warmup_questions_asked += 1
    return question


def generate_first_question(session: InterviewSession, api_key: str) -> str:
    if session.warmup_mode and not session.warmup_complete:
        return generate_warmup_question(session, api_key)
    prompt = build_first_question_prompt(session)
    result = _call_gemini(api_key, prompt)
    question = result.get("question", "Tell me about yourself.")
    q_type = result.get("question_type", "opener")
    session.questions_asked.append(question)
    session.question_types.append(q_type)
    session.current_question_index += 1
    return question


def evaluate_and_continue(
    session: InterviewSession,
    transcript: str,
    api_key: str,
    duration_secs: float = 0.0,
) -> tuple[dict, str | None]:
    # Analyse the answer
    filler_data = count_filler_words(transcript)
    session.filler_counts.append(filler_data)
    session.answer_durations.append(duration_secs)
    session.answers_given.append(transcript)

    # Handle warmup flow
    if session.is_in_warmup:
        warmup_feedback = {
            "score": 3,
            "structure_note": "Warmup — just getting comfortable.",
            "content_note": "Nice! You're finding your voice.",
            "confidence_tip": "Remember: you're also evaluating whether this is the right fit for you.",
            "filler_note": "",
            "duration_note": "",
            "trick_question_guide": "",
            "encouragement": "You're doing great — this is just to warm up. The real session starts next.",
            "summary": "Good warmup answer. Take a breath and get ready for the main interview.",
        }
        session.feedback_per_answer.append(warmup_feedback)
        session.warmup_questions_asked += 1
        if session.warmup_questions_asked >= session.WARMUP_COUNT:
            session.warmup_complete = True
            # Generate first real question
            real_prompt = build_first_question_prompt(session)
            try:
                result = _call_gemini(api_key, real_prompt)
                next_q = result.get("question", "Tell me about yourself.")
                next_type = result.get("question_type", "opener")
            except Exception:
                next_q = "Tell me about yourself."
                next_type = "opener"
            session.questions_asked.append(next_q)
            session.question_types.append(next_type)
            session.current_question_index += 1
            return warmup_feedback, next_q
        else:
            # Another warmup question
            next_q = generate_warmup_question(session, api_key)
            return warmup_feedback, next_q

    # Regular interview flow
    prompt = build_evaluate_prompt(session, transcript, filler_data, duration_secs)
    result = _call_gemini(api_key, prompt)

    feedback = result.get("feedback", {
        "score": 3,
        "structure_note": "Answer received.",
        "content_note": "Keep developing your response with specific examples.",
        "confidence_tip": "Speak at a steady pace and trust your preparation.",
        "filler_note": "",
        "duration_note": "",
        "trick_question_guide": "",
        "encouragement": "",
        "summary": "Good effort. Keep going.",
    })
    session.feedback_per_answer.append(feedback)

    next_question = result.get("next_question")
    next_type = result.get("next_question_type", "behavioral")

    if next_question and session.current_question_index < session.total_questions:
        session.questions_asked.append(next_question)
        session.question_types.append(next_type)
        session.current_question_index += 1
    else:
        session.is_complete = True
        next_question = None

    return feedback, next_question


def generate_report(session: InterviewSession, api_key: str) -> dict:
    prompt = build_report_prompt(session, session.all_filler_totals(), session.answer_durations)
    result = _call_gemini(api_key, prompt)
    return result
