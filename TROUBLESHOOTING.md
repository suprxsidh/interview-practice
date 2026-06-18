# Troubleshooting Guide

A fix for every common issue. Work through the list from top to bottom.

---

## 1. "Python not found" when running Install.bat

**Cause:** Python is not installed, or was installed without being added to PATH.

**Fix:**
1. Go to [python.org/downloads](https://www.python.org/downloads/) and download the latest Python 3.x installer
2. Run the installer
3. On the **first screen**, tick the checkbox **"Add Python to PATH"** — this is critical
4. Complete the installation
5. Close the Install.bat window and run it again

---

## 2. Windows Defender or antivirus blocks Install.bat / Start.bat

**Cause:** Windows SmartScreen flags unknown `.bat` files by default.

**Fix:**
- Right-click the file → **Properties** → tick **"Unblock"** at the bottom → OK
- Or when the SmartScreen popup appears: click **"More info"** → **"Run anyway"**
- This is safe — the files only run pip and Python commands

---

## 3. "pip install failed" during setup

**Cause:** No internet connection, corporate firewall, or proxy.

**Fix A (no internet):** Connect to a normal internet connection and re-run Install.bat.

**Fix B (corporate proxy):** Open a Command Prompt in the Interviewer folder and run:
```
py -m pip install -r requirements.txt --proxy http://your-proxy:port
```

**Fix C (permission error):** Run Install.bat as Administrator — right-click → "Run as administrator"

---

## 4. Model download fails (Whisper or Kokoro)

**Cause:** Slow internet, interrupted download, or firewall blocking GitHub/HuggingFace.

**Fix:**
- Run Install.bat again — partial downloads are resumed automatically
- If it keeps failing: connect to a different network (hotspot) and re-run
- Check that `models/whisper/` and `models/kokoro/` folders exist and contain files after install

---

## 5. Browser doesn't open automatically

**Cause:** Default browser is not set, or inbrowser launch failed.

**Fix:** Manually open Chrome or Edge and go to: **http://localhost:7860**

If port 7860 is taken: try **http://localhost:7861** or **http://localhost:7862**

---

## 6. "Port already in use" error in Start.bat

**Cause:** The app is already running in another window, or another program uses port 7860.

**Fix A:** Close the other Start.bat window and run it again.

**Fix B:** The app will automatically try ports 7861, 7862, 7863 — check the Start.bat window for the actual URL it's running on.

**Fix C (manual):** Open Start.bat in Notepad, find `7860` and change it to `7865`, save, and run again.

---

## 7. Microphone not working in the browser

**Cause:** Browser hasn't been given microphone permission.

**Fix for Chrome/Edge:**
1. Look at the **address bar** — there should be a camera/mic icon on the right
2. Click it → select **"Always allow localhost to access your microphone"** → Done
3. If no icon: go to `chrome://settings/content/microphone` → find localhost → set to Allow

**Fix if mic is listed but silent:**
1. Right-click the speaker icon in Windows taskbar → **Sound settings**
2. Under **Input**, check that your microphone is selected and the volume bar moves when you speak
3. Make sure the mic isn't muted (physical mute button on headset?)

---

## 8. "Your API key is invalid"

**Cause:** Wrong key, incomplete copy, or key has been deleted.

**Fix:**
1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Click **"Get API key"** in the top navigation
3. Find your key or create a new one
4. Copy the **full key** — it starts with `AIza` and is about 39 characters
5. Paste it into the app's setup screen

---

## 9. "Daily limit reached" / Gemini quota error

**Cause:** Free Gemini tier allows 1,500 requests/day. A 10-question session uses ~12 requests.

**Fix:**
- Wait until midnight Pacific time — the quota resets daily
- If you're practicing intensively: create a second Google account for a second free key

---

## 10. The app opens but shows a blank white screen

**Cause:** Browser caching issue, or Gradio failed to load.

**Fix:**
1. Hard-refresh: press **Ctrl + Shift + R** in the browser
2. If still blank: close Start.bat, re-run it, and wait 10 seconds before the browser opens
3. Try a different browser (Chrome or Edge recommended)

---

## 11. Voice (TTS) is not playing / very quiet

**Cause:** Browser audio blocked, or Windows volume mixer muting the browser.

**Fix:**
1. Right-click Windows volume icon → **Open Volume Mixer**
2. Find Chrome/Edge in the list and turn its volume up
3. In the browser: click the audio/speaker icon in the browser tab and make sure it's not muted
4. Check that your default audio output device in Windows settings is correct

---

## 12. Transcription is empty or wrong

**Cause:** Audio too quiet, microphone too far away, or background noise.

**Fix:**
- Speak clearly and at normal volume, 20-40cm from the mic
- Use headphones with a built-in microphone for best results
- Try again — click "Try Again" to re-record without submitting

---

## Still stuck?

Open a Command Prompt in the Interviewer folder and run:
```
py app.py
```
This shows the full error message. Copy it and search for it online, or share it when asking for help.
