# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the app

```bash
python app.py          # launches Gradio at localhost:7860 (auto-increments to 7861-7863 if busy)
```

Models must be downloaded first. If `models/whisper/` or `models/kokoro/` are empty, run:
```bash
python -c "from faster_whisper import WhisperModel; WhisperModel('tiny', download_root='models/whisper', device='cpu', compute_type='int8')"
python scripts/download_models.py
```

Install dependencies: `pip install -r requirements.txt`

## Architecture

The app is a single-page Gradio app with three hidden/visible column panels (setup → interview → report) wired together in `app.py`. All state for one interview lives in a `gr.State(InterviewSession)` object scoped per browser session — there is no global mutable state.

### Data flow for one interview turn

```
User speaks → gr.Audio (numpy) → voice/stt.py (Whisper) → transcript
→ core/interview_engine.py → core/prompts.py → Gemini API
→ feedback dict + next_question string
→ voice/tts.py (Kokoro) → gr.Audio (autoplay)
→ ui/ formatters → Gradio component updates
```

### Module responsibilities

- **`core/session.py`** — `InterviewSession` dataclass. Single source of truth for all per-session state: questions, answers, feedback, question types, filler counts, durations, warmup tracking.
- **`core/prompts.py`** — All Gemini prompt templates. `build_first_question_prompt`, `build_evaluate_prompt`, `build_report_prompt`, `build_warmup_prompt`. Contains the interviewer persona (Alex Chen), question type taxonomy, trick question bank, and `TRICK_QUESTION_GUIDANCE` dict used in both prompts and UI.
- **`core/interview_engine.py`** — Orchestrates the interview loop. Calls `_call_gemini` (with JSON-strip retry logic), updates `InterviewSession` state, and handles the warmup → real-interview transition.
- **`core/analysis.py`** — Stateless helpers: filler word counter (`count_filler_words`), duration feedback string, humblebrag detector, score progression trend.
- **`core/config_manager.py`** — Reads/writes `config/config.json` (API key, preferences). `validate_api_key` makes a live Gemini ping before saving.
- **`core/history.py`** — Saves completed sessions as JSON to `sessions/YYYY-MM-DD-HH-MM-{type}.json` and loads them for cross-session trend display.
- **`voice/stt.py`** — Lazy-loads `faster-whisper` tiny model on first call. Takes `(np.ndarray, sample_rate)` from Gradio, writes a temp WAV (closing the file handle before writing — required on Windows), transcribes, cleans up.
- **`voice/tts.py`** — Lazy-loads `kokoro-onnx` from `models/kokoro/`. Returns `(sample_rate, np.ndarray)` tuple consumed directly by `gr.Audio`.
- **`ui/`** — Pure view builders. Each returns a tuple of Gradio components; no logic. Formatting helpers (`format_feedback`, `format_report`, `format_trick_guide`, `format_question_type_badge`) live here alongside the builders.
- **`app.py`** — Wires all components and event handlers. All Gradio `.click()` callbacks are defined here. Output lists must stay in sync with the `outputs=[]` list on each `.click()` call — this is the most fragile part of the codebase.

### Gemini API contract

Every Gemini call expects a JSON response. `_call_gemini` strips markdown code fences with `re.MULTILINE` and retries up to 3 times, appending a "return only JSON" nudge on the first `JSONDecodeError`. Prompts always end with an explicit JSON schema comment so the model knows the exact shape expected.

The evaluate prompt returns:
```json
{
  "feedback": { "score": 1-5, "structure_note": "", "content_note": "", "confidence_tip": "",
                "filler_note": "", "duration_note": "", "trick_question_guide": "",
                "encouragement": "", "summary": "" },
  "next_question": "<string or null>",
  "next_question_type": "<type tag>",
  "is_follow_up": true/false
}
```

### Question type system

Questions are tagged with types from: `opener`, `behavioral`, `failure`, `self_awareness`, `trick`, `stress`, `curveball`, `vision`, `values`, `follow_up`, `closer`. Types are stored in `session.question_types` parallel to `session.questions_asked`. The `TRICK_QUESTION_GUIDANCE` dict in `prompts.py` drives both the feedback UI accordion and the end-of-session report breakdown.

### Warmup mode

When `session.warmup_mode=True`, `generate_first_question` calls `generate_warmup_question` instead. Warmup answers bypass the full evaluate prompt — they get a hardcoded encouraging feedback dict. After `WARMUP_COUNT` (2) warmup answers, `evaluate_and_continue` sets `session.warmup_complete=True` and immediately generates the first real question using `build_first_question_prompt`.

### Gradio output list discipline

`on_submit` returns a list of exactly 14 `gr.update()` values mapped to `outputs=[...]`. `on_start` returns 13. If components are added or removed from a page builder, the output count and the matching `.click(outputs=[...])` list must be updated together — Gradio silently drops or mismatches updates if counts differ.
