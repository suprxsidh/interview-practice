import gradio as gr


def build_interview_page():
    with gr.Column(visible=False) as interview_col:

        # Progress + question
        with gr.Row():
            progress_md = gr.Markdown("### Question 0 of 0")
            question_type_md = gr.Markdown("", elem_id="q-type-badge")

        question_md = gr.Markdown(
            "**Your question will appear here...**",
            elem_id="question-display",
        )
        question_audio = gr.Audio(
            label="",
            autoplay=True,
            interactive=False,
            visible=True,
            show_download_button=False,
        )

        gr.Markdown("---")

        # Recording controls
        gr.Markdown(
            "**Your Answer** — click the microphone to record, speak your answer, "
            "then click Stop. Review your transcript, then Submit."
        )
        answer_audio = gr.Audio(
            sources=["microphone"],
            type="numpy",
            label="Record your answer",
        )

        with gr.Row():
            submit_btn = gr.Button("Submit Answer", variant="primary", size="lg")
            retry_btn = gr.Button("Try Again", variant="secondary", size="sm")

        transcript_md = gr.Markdown("", visible=False)
        status_md = gr.Markdown("", visible=False)

        # Feedback
        with gr.Accordion("Feedback on this answer", open=False) as feedback_accordion:
            feedback_md = gr.Markdown("No feedback yet.")

        # Trick question education (shown when applicable)
        with gr.Accordion("How to ace this question type", open=False, visible=False) as trick_guide_accordion:
            trick_guide_md = gr.Markdown("")

    return (
        interview_col,
        progress_md,
        question_type_md,
        question_md,
        question_audio,
        answer_audio,
        submit_btn,
        retry_btn,
        status_md,
        feedback_accordion,
        feedback_md,
        trick_guide_accordion,
        trick_guide_md,
        transcript_md,
    )


def format_question_type_badge(qtype: str) -> str:
    labels = {
        "opener": "Opener",
        "behavioral": "Behavioural",
        "failure": "Failure / Learning",
        "self_awareness": "Self-Awareness",
        "trick": "Trick Question",
        "stress": "Stress Question",
        "curveball": "Curveball",
        "vision": "Career Vision",
        "values": "Values / Ethics",
        "follow_up": "Follow-Up Probe",
        "closer": "Closing",
    }
    label = labels.get(qtype, qtype.replace("_", " ").title())
    # Highlight trick/stress questions differently
    if qtype in ("trick", "stress", "curveball", "self_awareness"):
        return f"**Type: {label}** _(this is a deliberate pressure question — see the guide below)_"
    return f"Type: {label}"
