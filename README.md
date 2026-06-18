# Interview Practice Coach

A local, voice-based AI interview coach for MBA admissions and job interviews. No cloud audio — your voice stays on your machine. Powered by Whisper (speech recognition), Kokoro TTS (AI voice), and Gemini (interview intelligence).

---

## What it does

- **Speaks questions aloud** — Alex, your AI interviewer, asks questions using a local text-to-speech voice
- **Listens to your answers** — speech-to-text runs locally (Whisper), nothing leaves your machine
- **Mirrors real interview patterns** — HBS, Wharton, Kellogg, ISB, and LBS style for MBA; consulting, PM, and finance patterns for job interviews
- **Includes trick and stress questions** — deliberate pressure questions mid-session, with a full explanation of what was being tested and how to answer them
- **Gives targeted feedback after every answer** — structure (STAR/CARL), content, confidence tip, filler word count, answer duration
- **Warmup mode** — 2 low-stakes questions before the real interview starts, for nervous speakers
- **Full report card** — overall score, confidence score, score progression, trick question breakdown, sample stronger answers, and one clear "top priority" for next time
- **Session history** — tracks progress across multiple sessions

---

## Setup (Windows, one time only)

### Step 1 — Install Python
Download from [python.org/downloads](https://www.python.org/downloads/). On the first screen of the installer, **tick "Add Python to PATH"**.

### Step 2 — Get a free Gemini API key
1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Sign in with your Google account
3. Click **Get API key** → **Create API key**
4. Copy the key — you'll paste it into the app

The free tier gives you 1,500 requests/day. A 10-question session uses ~12 requests.

### Step 3 — Run Install.bat
Double-click **`Install.bat`**. It will:
- Install all Python packages
- Download the Whisper speech recognition model (~75MB)
- Download the Kokoro TTS voice model (~90MB)

Takes 3-5 minutes. Keep the window open until it says "Setup complete!"

### Step 4 — Launch the app
Double-click **`Start.bat`** every time you want to practise. Your browser opens automatically.

---

## How to use

1. **Paste your Gemini API key** in the setup screen (saved after first use)
2. **Choose interview type** — MBA, Behavioural, or Job Interview
3. **Pick session length** — 5, 10, or 15 questions
4. **Toggle warmup** — recommended if you're nervous (2 easy questions first)
5. **Click Start** — Alex will speak the first question aloud
6. **Record your answer** — click the microphone, speak, click Stop, then Submit
7. **Read the feedback** — it appears after each answer
8. **Watch out for the question type badge** — trick and stress questions are labelled so you know what's coming
9. **Get your report** — full breakdown at the end, including how to answer each trick question better next time

---

## Interview types

| Type | What it covers | Real-world equivalent |
|------|---------------|----------------------|
| **MBA Interview** | Leadership vision, self-awareness, career trajectory, "Why MBA now?", ethics | HBS, Wharton, Kellogg, ISB, LBS |
| **Behavioural** | STAR method, leadership, conflict, failure, teamwork, initiative | General corporate, consulting, any "tell me about a time" |
| **Job Interview** | Role-specific questions, motivation, "why this company", fit | Consulting, PM, finance, general roles |

---

## Trick & stress questions

The app deliberately injects 1-2 of these mid-session in every interview:

| Question | What it's actually testing |
|----------|--------------------------|
| "What's your greatest weakness?" | Whether you humblebrag (77% of candidates do — it backfires) |
| "What would your worst enemy say about you?" | Third-party self-awareness, emotional maturity |
| "Rate yourself out of 10 as a leader" | Confidence calibration, how you handle follow-up pressure |
| "Why should we pick you over other candidates?" | Composure, specific differentiation, employer-frame thinking |
| "I'm not convinced your background is strong enough — persuade me" | Emotional regulation, evidence-based confidence |

After each trick question, the feedback panel explains exactly what was being tested and gives a model answer structure.

---

## Answer frameworks (coached in feedback)

| Framework | When to use |
|-----------|-------------|
| **STAR** (Situation, Task, Action, Result) | Standard behavioural questions |
| **CARL** (Context, Action, Result, Learning) | Failure and "what would you do differently" questions |
| **WAR** (Weakness, Action, Result) | "What is your greatest weakness?" |
| **PAUSE-PROCESS-RESPOND** | Stress and pushback questions |

---

## Requirements

- Windows 10 or 11
- Python 3.10 or newer
- Internet connection (for Gemini — questions and feedback only)
- Microphone
- Chrome or Edge browser

---

## Troubleshooting

See **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** for fixes to all common issues, including:
- Python not found
- Microphone not working in browser
- "API key invalid"
- Port already in use
- Download failures

---

## Tech stack

| Component | Technology |
|-----------|-----------|
| Speech recognition | [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (tiny model, CPU, offline) |
| Text-to-speech | [kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx) (af_sarah voice, offline) |
| Interview AI | Google Gemini 1.5 Flash (free tier) |
| UI | [Gradio](https://gradio.app) (runs in browser) |
| Audio analysis | Custom filler word detector, answer duration tracker |
