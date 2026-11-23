# SPEC.md - Source of truth. Do NOT edit unless the user explicitly asks.

## 1. Goal
Build a LOCAL web tool (runs on the user's Windows PC, opens in the browser) that helps produce YouTube Shorts: a vertical 9:16 video with a narrator reading a script over the user's own Minecraft parkour footage, with burned-in captions.

Channel concept: "proven mind-blowing facts" told as short stories (example: "Greenland sharks live longer than most trees"). Audience: English-speaking viewers abroad. Video length: random between 60 and 180 seconds.

The user is a beginner who builds by "vibe coding". UI labels are in Vietnamese. Script, voice and captions are in English.

## 2. Constraints
- C1. Windows 10/11, 16 GB RAM, NVIDIA GPU (detect it, fall back to CPU if absent).
- C2. Everything FREE. No paid APIs. The only external API allowed is Google Gemini (free tier, the user's own key from Google AI Studio).
- C3. Must work on Windows: use pathlib, no bash-only commands. Provide `start.bat` that creates the venv, installs requirements and launches the app. Explain how to install FFmpeg on Windows (winget) and check it.
- C4. Minecraft parkour clips (mp4) are filmed by the user and placed in `assets/minecraft/`. None exist yet, so the app must show a clear message and still work with a plain dark placeholder background.
- C5. No secrets in code. API key is read from `.env` (provide `.env.example`).

## 3. Tech stack (keep it simple, do not over-engineer)
- Backend: Python 3.11+, FastAPI.
- Frontend: one simple HTML page with vanilla JS (no build step, no React). Clean modern dark theme.
- Video: FFmpeg (h264_nvenc if available, else libx264).
- TTS: `edge-tts` as the main provider behind a provider interface. Also an OFFLINE fallback provider using Kokoro TTS (open-source, free). Use ONE fixed male English voice, locked in `config.yaml`, never changed per video. On first run list available English male voices, let the user choose once, and save it.
- Captions: `faster-whisper` for word-level timestamps from the final narration audio, then styled .ass subtitles.
- Gemini: official `google-genai` Python SDK. Model name lives in `config.yaml` (never hardcoded; the user fills in a currently available free model).
- Storage: each project is a folder `projects/<id>/` with `project.json` (script, claims, settings), audio, subtitles, final mp4. No database.
- Modules: tts.py, pacing.py, render.py, captions.py, gemini_client.py, factcheck.py, main.py. Short comments in simple English, type hints.

## 4. Requirements

### R1. Script editor (main page)
- R1.1 Big text area for the script.
- R1.2 Live counter: word count and ESTIMATED duration (about 150 words per minute at the current pace settings).
- R1.3 "Random target length" button: picks a random duration between 60 and 180 seconds and shows the matching word-count range.
- R1.4 Collapsible cheat sheet explaining the pacing markup.
- R1.5 Autosave the script every few seconds.

### R2. Pacing markup (how narration becomes engaging)
- R2.1 `[pause 0.5]` = silence of that many seconds (any number).
- R2.2 `[slow]...[/slow]` = slower reading (rate about -15%).
- R2.3 `[fast]...[/fast]` = faster reading (rate about +12%).
- R2.4 `*word or phrase*` = emphasis (slightly louder, slightly higher pitch, tiny pause before it).
- R2.5 `[whisper]...[/whisper]` = lower pitch, lower volume, a bit slower, for mysterious moments.
- R2.6 Implementation: split the script into segments, synthesize each with its own rate/pitch/volume, insert real silence between them, concatenate with FFmpeg into one narration file, normalize loudness.
- R2.7 Global presets in the UI: "Mystery" (default: slower baseline, longer pauses after sentences, longer pause before a reveal), "Hype", "Calm". A preset only changes baseline values and default pause lengths.
- R2.8 Button "Tự thêm nhịp (auto-pace)": Gemini inserts the markup into the plain script (fast hook at the start, slow buildup, pause before the key fact, strong ending). Show a before/after preview; the user accepts or rejects.
- R2.9 Button "Nghe thử": synthesizes and plays only the selected paragraph.
- R2.10 The markup parser must have simple automated tests.

### R3. Gemini writing assistant (side panel)
Each button has a free-text "ghi chú cho AI" box.
- R3.1 "Gợi ý đoạn tiếp theo": from the script so far, suggest 3 alternative next paragraphs; click one to append it.
- R3.2 "Viết lại bài đang dở": rewrite and polish the unfinished draft, keeping the user's facts and voice, optimized for spoken narration (short sentences, strong hook in the first 2 sentences, curiosity gaps, satisfying ending). Show before/after; the user accepts.
- R3.3 "Dựng khung từ đầu": the user enters a topic or a single fact; Gemini returns an outline (hook, 3-5 beats, reveal, outro) and optionally a full first draft for a chosen target length.
- R3.4 Rules for ALL Gemini writing calls: write in English; NEVER invent statistics, dates, names or sources; if a number is not certain, write the sentence without it and flag it with `[VERIFY]`; short speakable sentences; no clickbait lies.

### R4. Fact check panel (exactly two labels)
Button "Kiểm chứng":
- R4.1 Gemini splits the script into atomic factual claims (one checkable fact each, with the exact source sentence).
- R4.2 For each claim, use Gemini with Google Search grounding if the free tier supports it. If it does not, tell the user clearly and fall back to asking Gemini for sources, marked as less reliable.
- R4.3 Label "ĐÃ CHỨNG MINH" (Proven): supported by at least one credible source (peer-reviewed paper, university, government or scientific institution, major reference). Must include the source URL(s) and a one-line evidence summary.
- R4.4 Label "CHƯA RÕ" (Unclear): everything else (disputed, only popular-media claims, wide-uncertainty estimates, no good source). Say briefly why.
- R4.5 Show a list with colored badges (green / yellow). Clicking a claim highlights its sentence in the script.
- R4.6 Next to each "CHƯA RÕ" claim, button "Sửa câu này cho an toàn": Gemini rewrites the sentence to be accurate (e.g., "estimated to be", "according to one study").
- R4.7 Never auto-decide for the user: show a warning that labels are AI suggestions and the source links must be opened and checked. The user can manually override any label and add their own source URL.
- R4.8 Before rendering, if any claim is "CHƯA RÕ", show a confirmation dialog; the user may still proceed.
- R4.9 Save claims and sources in project.json and export `sources.txt` (ready to paste into the YouTube description) next to the final video.

### R5. Render pipeline
Button "Tạo video":
- R5.1 Generate narration (with pacing markup) and measure the real duration.
- R5.2 If the duration is outside 60-180 s, warn (do not block).
- R5.3 Pick a random clip from `assets/minecraft/`; if shorter than the narration, chain or loop several clips; random start offset so videos differ; crop/scale to 1080x1920 without stretching; mute the original audio. If no clips exist, use a dark placeholder background.
- R5.4 Transcribe the narration with faster-whisper for word timings and build .ass captions: big bold text, 2-4 words at a time, current word highlighted, centered in the safe area of a vertical video.
- R5.5 Optional background music from `assets/music/`, ducked to about -22 dB under the voice; skip if the folder is empty.
- R5.6 Render `output.mp4` (1080x1920, 30 fps, AAC audio) into the project folder.
- R5.7 Show a progress bar with step names (polling or Server-Sent Events). Rendering runs in a background thread so the UI does not freeze.
- R5.8 Clear, human error messages in Vietnamese (FFmpeg missing, no API key, no clips, no internet, Gemini rate limit with friendly retry).

### R6. Projects
- R6.1 Sidebar listing past projects (title, date, status) with open / duplicate / delete.
- R6.2 Each project stored in its own folder (see Tech stack).

### R7. Setup and docs
- R7.1 README in Vietnamese: install Python, FFmpeg, get the Gemini API key, run `start.bat`, troubleshooting section.
- R7.2 `config.yaml` (voice, Gemini model name, defaults) and `.env.example`.
- R7.3 CHANGELOG.md updated after every task.

## 5. Suggested phases (the Planner turns these into tasks in PLAN.md)
- Phase 0: skeleton, start.bat, config.yaml, .env.example, README. Prove the web page opens. (C3, C5, R7)
- Phase 1: script editor, word/duration estimate, projects save/load. (R1, R6)
- Phase 2: TTS with pacing markup, "Nghe thử", voice selection and locking. (R2, tests)
- Phase 3: render pipeline with placeholder background and captions. (R5.1, R5.2, R5.4, R5.6-R5.8)
- Phase 4: Minecraft clip selection (random clip, random offset, loop) and optional music. (R5.3, R5.5)
- Phase 5: Gemini writing assistant and auto-pace. (R3, R2.8)
- Phase 6: fact check panel, sources.txt, confirmation before render. (R4)
- Phase 7: polish, error messages, offline Kokoro fallback, README troubleshooting. (R7, R5.8)

## 6. Definition of done
Every R item works as described, the user can go from a topic to a finished 9:16 mp4 plus sources.txt using only the web page, and nothing requires a paid service.