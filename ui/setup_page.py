import gradio as gr
from core.config_manager import load_config


GEMINI_INSTRUCTIONS = """
### Get your free Gemini API key (2 minutes)

**Step 1:** Open [Google AI Studio](https://aistudio.google.com) in your browser

**Step 2:** Sign in with your Google account

**Step 3:** Click **"Get API key"** in the top left → **"Create API key"**

**Step 4:** Copy the key and paste it in the box below

> The key is free. Google's free tier gives you 1,500 requests per day — more than enough for daily practice sessions.
"""

CALMING_INTRO = """
### Before we begin

Take a slow breath. You've got this.

A few things to remember as you practise:
- **You are also interviewing them.** Every conversation is mutual — remind yourself of that.
- **Nervousness is energy.** Research shows that saying "I am excited" before speaking \
actually improves performance — try it before you click Start.
- **Specificity beats polish.** A real, specific story always beats a slick, generic one.
- **Silence is okay.** Pausing to think reads as composed, not slow.

The interviewer (Alex) will speak each question aloud. Record your answer, then click Submit. \
Feedback appears after each answer, and you get a full report at the end.
"""


def build_setup_page():
    cfg = load_config()

    with gr.Column(visible=True) as setup_col:
        gr.Markdown("## Interview Practice Coach")
        gr.Markdown(
            "Voice-based mock interviews for MBA admissions and job applications. "
            "Alex, your AI interviewer, will speak each question. You record your answer and get targeted feedback."
        )

        with gr.Tabs():
            with gr.Tab("Setup"):
                # ── Gemini instructions — always visible ─────────────────────
                with gr.Group():
                    gr.Markdown(GEMINI_INSTRUCTIONS)
                    api_key_input = gr.Textbox(
                        label="Paste your Gemini API key here",
                        placeholder="AIza...",
                        type="password",
                        value=cfg.get("api_key", ""),
                    )
                    api_status = gr.Markdown("", visible=False)

                gr.Markdown("---")

                # ── Interview settings ────────────────────────────────────────
                interview_type = gr.Radio(
                    choices=[
                        ("MBA Interview  (HBS / Wharton / Kellogg / ISB / LBS style)", "mba"),
                        ("Behavioural Interview  (STAR method, leadership, teamwork)", "behavioral"),
                        ("Job Interview  (role-specific + behavioural mix)", "job_interview"),
                    ],
                    value=cfg.get("interview_type", "mba"),
                    label="Interview Type",
                )

                job_role_input = gr.Textbox(
                    label="Job Role  (only needed for Job Interview type)",
                    placeholder="e.g. Product Manager, Investment Banking Analyst, Strategy Consultant...",
                    value=cfg.get("job_role", ""),
                    visible=(cfg.get("interview_type") == "job_interview"),
                )

                session_length = gr.Radio(
                    choices=[
                        ("5 questions  (quick, ~15 min)", 5),
                        ("10 questions  (standard, ~30 min)", 10),
                        ("15 questions  (full session, ~45 min)", 15),
                    ],
                    value=cfg.get("session_length", 10),
                    label="Session Length",
                )

                warmup_toggle = gr.Checkbox(
                    label="Start with a 2-question warmup  (recommended for nervous speakers — low-stakes questions to get comfortable before the real interview)",
                    value=cfg.get("warmup_mode", True),
                )

                gr.Markdown("---")
                gr.Markdown(CALMING_INTRO)

                start_btn = gr.Button("Start Interview", variant="primary", size="lg")
                setup_status = gr.Markdown("", visible=False)

            with gr.Tab("Help & Troubleshooting"):
                gr.Markdown("""
### Microphone not working?
- Make sure Chrome or Edge is your browser (Firefox has limited mic support)
- Look for the **microphone icon** in your browser's address bar — click it and select **"Allow"**
- If you don't see it: go to Chrome Settings → Privacy → Site Settings → Microphone → Allow localhost

### The app won't start?
- **Close this window**, then double-click **Install.bat** again to repair the setup
- If Install.bat shows "Python not found": install Python from [python.org](https://www.python.org/downloads/) — tick **"Add Python to PATH"** during setup, then re-run Install.bat

### "Your API key is invalid"?
- Make sure you copied the full key (it starts with "AIza" and is ~39 characters)
- The key is at [aistudio.google.com](https://aistudio.google.com) → Get API key

### Daily limit reached?
- Gemini free tier allows 1,500 requests per day. A 10-question session uses ~12 requests.
- If you hit the limit, wait until midnight (Pacific time) for it to reset

### Port 7860 already in use?
- Another app is using the port. Close the other app and run Start.bat again
- Or: open Start.bat in a text editor, change `7860` to `7861`, save, and re-run

### Voice sounds robotic or cuts out?
- This is the local TTS model working normally — no internet needed for voice
- If there's no sound at all: check your Windows volume and browser audio permissions

### See the TROUBLESHOOTING.md file in the app folder for more detailed fixes.
""")

    def toggle_job_role(itype):
        return gr.update(visible=(itype == "job_interview"))

    interview_type.change(toggle_job_role, inputs=interview_type, outputs=job_role_input)

    return (
        setup_col, api_key_input, interview_type, job_role_input,
        session_length, warmup_toggle, start_btn, setup_status, api_status,
    )
