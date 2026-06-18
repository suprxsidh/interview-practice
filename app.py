import time
import gradio as gr

from core.session import InterviewSession
from core.config_manager import validate_api_key, save_config, load_config
from core.interview_engine import generate_first_question, evaluate_and_continue, generate_report
from core.history import save_session, load_history, format_history_summary
from voice.stt import transcribe, is_model_ready as stt_ready
from voice.tts import synthesize, is_model_ready as tts_ready
from ui.setup_page import build_setup_page
from ui.interview_page import build_interview_page, format_question_type_badge
from ui.report_page import build_report_page, format_report, format_feedback, format_trick_guide


def _tts(text: str):
    try:
        sr, audio = synthesize(text)
        return (sr, audio)
    except Exception:
        return None


def build_app():
    with gr.Blocks(
        theme=gr.themes.Soft(),
        title="Interview Practice Coach",
        css="""
        #question-display { font-size: 1.25em; line-height: 1.7; padding: 1.2em 1em; }
        #q-type-badge { font-size: 0.85em; color: #666; padding-top: 0.4em; }
        .gr-button-primary { font-size: 1.05em; }
        """,
    ) as demo:
        gr.Markdown("# Interview Practice Coach")
        gr.Markdown(
            "*Voice-based mock interviews — MBA admissions & job interview preparation. "
            "Powered by Whisper, Kokoro TTS, and Gemini.*"
        )

        # Model readiness warning
        models_ok = stt_ready() and tts_ready()
        if not models_ok:
            gr.Markdown(
                "> **Setup required:** AI models are not yet downloaded. "
                "Please close this window and run **Install.bat** first, then re-run Start.bat."
            )

        session_state = gr.State(None)
        record_start_state = gr.State(0.0)  # timestamp when recording started

        # ── Build pages ──────────────────────────────────────────────────────
        (
            setup_col, api_key_input, interview_type, job_role_input,
            session_length, warmup_toggle, start_btn, setup_status, api_status,
        ) = build_setup_page()

        (
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
        ) = build_interview_page()

        report_col, report_md, restart_btn, export_btn, history_md = build_report_page()

        # ── Helpers ──────────────────────────────────────────────────────────
        def _interview_outputs_no_change(n=16):
            return [gr.update()] * n

        def _session_to_progress(session: InterviewSession) -> str:
            if session.is_in_warmup:
                wq = session.warmup_questions_asked
                return f"### Warmup Question {wq} of {session.WARMUP_COUNT}"
            q = session.current_question_index
            t = session.total_questions
            return f"### Question {q} of {t}"

        # ── Start interview ──────────────────────────────────────────────────
        def on_start(api_key, itype, job_role, length, warmup):
            valid, msg = validate_api_key(api_key)
            if not valid:
                return (
                    [gr.update(value=f"> **Error:** {msg}", visible=True)]
                    + [gr.update()] * 10
                    + [None, 0.0]
                )

            cfg = load_config()
            cfg.update({
                "api_key": api_key.strip(),
                "interview_type": itype,
                "job_role": job_role or "",
                "session_length": int(length),
                "warmup_mode": warmup,
            })
            save_config(cfg)

            session = InterviewSession(
                interview_type=itype,
                total_questions=int(length),
                job_role=job_role or "",
                warmup_mode=bool(warmup),
            )

            try:
                question = generate_first_question(session, api_key.strip())
            except Exception as e:
                return (
                    [gr.update(value=f"> **Error:** {e}", visible=True)]
                    + [gr.update()] * 10
                    + [None, 0.0]
                )

            q_type = session.current_question_type
            type_badge = format_question_type_badge(q_type)
            progress = _session_to_progress(session)

            return [
                gr.update(visible=False),           # setup_status
                gr.update(visible=False),           # setup_col
                gr.update(visible=True),            # interview_col
                gr.update(visible=False),           # report_col
                gr.update(value=progress),          # progress_md
                gr.update(value=type_badge),        # question_type_md
                gr.update(value=f"**{question}**"), # question_md
                gr.update(value=_tts(question)),    # question_audio
                gr.update(value="", visible=False), # status_md
                gr.update(value="", visible=False), # transcript_md
                gr.update(value="No feedback yet."),# feedback_md
                session,
                time.time(),
            ]

        start_btn.click(
            on_start,
            inputs=[api_key_input, interview_type, job_role_input, session_length, warmup_toggle],
            outputs=[
                setup_status, setup_col, interview_col, report_col,
                progress_md, question_type_md, question_md, question_audio,
                status_md, transcript_md, feedback_md,
                session_state, record_start_state,
            ],
        )

        # ── Retry (clear audio) ───────────────────────────────────────────────
        def on_retry():
            return gr.update(value=None), gr.update(value="", visible=False)

        retry_btn.click(on_retry, outputs=[answer_audio, transcript_md])

        # Track recording start time when audio component updates
        def on_audio_change(audio_data, _):
            if audio_data is not None:
                return time.time()
            return gr.update()

        answer_audio.change(on_audio_change, inputs=[answer_audio, record_start_state], outputs=[record_start_state])

        # ── Submit answer ────────────────────────────────────────────────────
        def on_submit(audio_data, session: InterviewSession, rec_start: float):
            N = 14
            no_change = [gr.update()] * N

            def err(msg):
                out = no_change.copy()
                out[0] = gr.update(value=msg, visible=True)
                out[N - 2] = session
                out[N - 1] = rec_start
                return out

            if session is None:
                return err("> Session not started. Please go back and click Start Interview.")
            if audio_data is None:
                return err("> No audio recorded. Click the microphone, speak, then click Stop.")

            sr, audio_np = audio_data
            duration_secs = max(0.0, time.time() - rec_start) if rec_start > 0 else 0.0

            try:
                transcript = transcribe(audio_np, sr)
            except Exception as e:
                return err(f"> Transcription error: {e}")

            if not transcript.strip():
                return err("> We couldn't hear anything. Please try again — make sure your microphone is allowed.")

            api_key = load_config().get("api_key", "")

            # Snapshot question index BEFORE evaluating (engine increments it)
            q_num_before = session.current_question_index
            q_type_before = session.current_question_type
            total = session.total_questions

            try:
                feedback, next_question = evaluate_and_continue(
                    session, transcript, api_key, duration_secs
                )
            except Exception as e:
                return err(f"> Could not get feedback: {e}")

            feedback_text = format_feedback(feedback, q_num_before, total, q_type_before)
            trick_text, show_trick = format_trick_guide(feedback)
            transcript_text = f"*You said:* {transcript}"

            # ── Session complete ─────────────────────────────────────────────
            if session.is_complete:
                try:
                    report = generate_report(session, api_key)
                    save_session(session, report)
                    history = load_history()
                    history_text = format_history_summary(history)
                    report_text = format_report(report, session)
                except Exception as e:
                    report_text = f"Session complete!\n\n(Full report could not be generated: {e})"
                    history_text = ""

                return [
                    gr.update(visible=False),           # status_md
                    gr.update(value=feedback_text),     # feedback_md
                    gr.update(open=True),               # feedback_accordion
                    gr.update(value=trick_text, visible=show_trick),  # trick_guide_accordion
                    gr.update(value=trick_text),        # trick_guide_md
                    gr.update(visible=False),           # interview_col
                    gr.update(visible=True),            # report_col
                    gr.update(value=report_text),       # report_md
                    gr.update(value=history_text, visible=bool(history_text)),  # history_md
                    gr.update(),                        # question_audio
                    gr.update(),                        # progress_md
                    gr.update(value=transcript_text, visible=True),  # transcript_md
                    session,
                    rec_start,
                ]

            # ── Next question ────────────────────────────────────────────────
            next_audio = _tts(next_question)
            q_type_next = session.current_question_type
            type_badge = format_question_type_badge(q_type_next)
            progress = _session_to_progress(session)

            return [
                gr.update(value="", visible=False),         # status_md
                gr.update(value=feedback_text),             # feedback_md
                gr.update(open=True),                       # feedback_accordion
                gr.update(value=trick_text, visible=show_trick),  # trick_guide_accordion
                gr.update(value=trick_text),                # trick_guide_md
                gr.update(),                                # interview_col
                gr.update(),                                # report_col
                gr.update(),                                # report_md
                gr.update(),                                # history_md
                gr.update(value=next_audio),                # question_audio
                gr.update(value=progress),                  # progress_md
                gr.update(value=transcript_text, visible=True),  # transcript_md
                session,
                time.time(),
            ]

        # Also update question_md + question_type_md after submit
        def update_question_display(session: InterviewSession):
            if session and session.questions_asked:
                q = session.current_question
                badge = format_question_type_badge(session.current_question_type)
                return gr.update(value=f"**{q}**"), gr.update(value=badge)
            return gr.update(), gr.update()

        submit_btn.click(
            on_submit,
            inputs=[answer_audio, session_state, record_start_state],
            outputs=[
                status_md, feedback_md, feedback_accordion,
                trick_guide_accordion, trick_guide_md,
                interview_col, report_col, report_md, history_md,
                question_audio, progress_md, transcript_md,
                session_state, record_start_state,
            ],
        )

        submit_btn.click(
            update_question_display,
            inputs=[session_state],
            outputs=[question_md, question_type_md],
        )

        # ── Restart ──────────────────────────────────────────────────────────
        def on_restart():
            return (
                gr.update(visible=True),   # setup_col
                gr.update(visible=False),  # interview_col
                gr.update(visible=False),  # report_col
                None,
                0.0,
            )

        restart_btn.click(
            on_restart,
            outputs=[setup_col, interview_col, report_col, session_state, record_start_state],
        )

    return demo


if __name__ == "__main__":
    cfg = load_config()
    for port in [7860, 7861, 7862, 7863]:
        try:
            demo = build_app()
            demo.launch(
                server_name="127.0.0.1",
                server_port=port,
                inbrowser=True,
                show_error=True,
            )
            break
        except OSError:
            if port == 7863:
                raise
            continue
