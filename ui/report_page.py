import gradio as gr
from core.analysis import score_progression_trend


def build_report_page():
    with gr.Column(visible=False) as report_col:
        gr.Markdown("## Your Session Report")
        report_md = gr.Markdown("Generating your report...")
        with gr.Row():
            restart_btn = gr.Button("Start a New Session", variant="primary", size="lg")
            export_btn = gr.Button("Copy Report Text", variant="secondary", size="sm")
        history_md = gr.Markdown("", visible=False)
    return report_col, report_md, restart_btn, export_btn, history_md


def format_report(report: dict, session=None) -> str:
    overall = report.get("overall_score", "?")
    confidence = report.get("confidence_score", "?")
    strengths = report.get("strengths", [])
    areas = report.get("areas_to_improve", [])
    samples = report.get("sample_answers", [])
    trick_breakdown = report.get("trick_question_breakdown", [])
    filler_summary = report.get("filler_word_summary", "")
    star_coaching = report.get("star_coaching", "")
    top_priority = report.get("top_priority", "")
    encouragement = report.get("closing_encouragement", "")
    progression = report.get("score_progression", [])

    overall_bar = "█" * int(overall) + "░" * (10 - int(overall)) if isinstance(overall, int) else "?"
    conf_bar = "█" * int(confidence) + "░" * (10 - int(confidence)) if isinstance(confidence, int) else "?"

    lines = [
        f"### Overall Score: **{overall}/10**  `{overall_bar}`",
        f"### Confidence Score: **{confidence}/10**  `{conf_bar}`",
        "",
    ]

    # Score progression
    if progression and len(progression) >= 2:
        trend = score_progression_trend(progression)
        bar = " ".join(f"`{s}`" for s in progression)
        lines += [f"**Score per question:** {bar}", f"*{trend}*", ""]

    # Strengths
    if strengths:
        lines += ["### What You Did Well", *[f"- {s}" for s in strengths], ""]

    # Areas
    if areas:
        lines += ["### Areas to Improve", *[f"- {a}" for a in areas], ""]

    # Top priority
    if top_priority:
        lines += ["### Before Your Next Interview", f"> **{top_priority}**", ""]

    # Trick question breakdown
    if trick_breakdown:
        lines += ["---", "### Trick & Stress Question Breakdown"]
        lines += ["*(These are the questions designed to test composure, self-awareness, and authenticity)*", ""]
        for t in trick_breakdown:
            qtype = t.get("question_type", "").replace("_", " ").title()
            lines += [
                f"**Q [{qtype}]: {t.get('question', '')}**",
                f"*What it tested:* {t.get('what_it_tested', '')}",
                f"*How you did:* {t.get('how_they_did', '')}",
                f"*How to ace it next time:* {t.get('model_approach', '')}",
                "",
            ]

    # STAR coaching
    if star_coaching:
        lines += ["---", "### Answer Structure (STAR/CARL Coaching)", f"{star_coaching}", ""]

    # Filler words
    if filler_summary:
        lines += ["### Filler Word Analysis", f"{filler_summary}", ""]

    # Sample better answers
    if samples:
        lines += ["---", "### Sample Stronger Answers *(for your lowest-scoring questions)*", ""]
        for s in samples:
            lines += [
                f"**Q: {s.get('question', '')}**",
                f"*You said:* {s.get('candidate_answer_summary', '')}",
                f"*Stronger approach:* {s.get('better_answer', '')}",
                "",
            ]

    # Encouragement
    if encouragement:
        lines += ["---", f"*{encouragement}*"]

    return "\n".join(lines)


def format_feedback(feedback: dict, q_num: int, total: int, q_type: str = "") -> str:
    score = feedback.get("score", "?")
    score_stars = "★" * score + "☆" * (5 - score) if isinstance(score, int) else "?"

    type_label = q_type.replace("_", " ").title() if q_type else ""
    header = f"**Score: {score}/5** {score_stars}"
    if type_label:
        header += f"  ·  *{type_label}*"

    parts = [header, ""]

    structure = feedback.get("structure_note", "")
    content = feedback.get("content_note", "")
    confidence_tip = feedback.get("confidence_tip", "")
    filler = feedback.get("filler_note", "")
    duration = feedback.get("duration_note", "")
    encouragement = feedback.get("encouragement", "")
    summary = feedback.get("summary", "")

    if structure:
        parts.append(f"**Structure:** {structure}")
    if content:
        parts.append(f"**Content:** {content}")
    if confidence_tip:
        parts.append(f"**Confidence tip:** {confidence_tip}")
    if filler:
        parts.append(f"**Filler words:** {filler}")
    if duration:
        parts.append(f"**Length:** {duration}")
    if encouragement:
        parts.append(f"")
        parts.append(f"*{encouragement}*")
    if summary:
        parts.append(f"")
        parts.append(f"*{summary}*")

    return "\n".join(parts)


def format_trick_guide(feedback: dict) -> tuple[str, bool]:
    """Return (guide_text, should_show)."""
    guide = feedback.get("trick_question_guide", "")
    if not guide or len(guide.strip()) < 10:
        return "", False
    return guide, True
