# PLAN.md - Implementation Tasks

Owner roles: Planner, Builder, Reviewer.
Rules: One task at a time. Builder touches ONLY the files listed for that task. Next task starts only after previous test passes.

---

## Phase 0: Skeleton & Setup (C3, C5, R7)

### T0.1: Git & Initial Configuration Skeleton
- **Goal**: Initialize git repository, setup `.gitignore` (ignoring venv, .env, __pycache__, projects/, assets/), `.env.example`, and default `config.yaml`.
- **Files**: `.gitignore`, `.env.example`, `config.yaml`
- **Requirements**: C5, R7.2
- **Owner**: Builder
- **Status**: doing
- **Where I stopped**:
  - *What is done*: Planner role finished project planning; initialized PLAN.md (all 8 phases T0.1 to T7.3) and DECISIONS.md (D1 to D7). Git repository initialized for session tracking.
  - *What is left*: Create `.gitignore`, `.env.example`, and `config.yaml`.
  - *Exact next step*: Builder creates `.gitignore`, `.env.example`, and `config.yaml`, tests their syntax/format, and marks T0.1 as done.
- **How to test**: Verify `.gitignore`, `.env.example` contains `GEMINI_API_KEY=`, and `config.yaml` parses correctly with YAML parser.

### T0.2: Minimal FastAPI Backend & UI Shell
- **Goal**: Setup `requirements.txt` with base dependencies (fastapi, uvicorn, pyyaml, python-dotenv). Create `main.py` serving a clean dark-theme HTML single page at `http://127.0.0.1:8000` with Vietnamese labels.
- **Files**: `requirements.txt`, `main.py`, `static/index.html`, `static/style.css`
- **Requirements**: C1, C3, R7
- **Owner**: Builder
- **Status**: todo
- **How to test**: Run `uvicorn main:app --reload`, open `http://127.0.0.1:8000` in browser, verify page loads with dark theme and Vietnamese headers.

### T0.3: Windows Launcher `start.bat` & Vietnamese Setup Guide
- **Goal**: Create `start.bat` to automate venv creation, requirements installation, FFmpeg verification (with winget install guidance), server launch, and browser opening. Create initial `README.md` in Vietnamese.
- **Files**: `start.bat`, `README.md`
- **Requirements**: C3, R7.1
- **Owner**: Builder
- **Status**: todo
- **How to test**: Execute `start.bat` in Windows terminal; verify environment setups and browser opens to app.

---

## Phase 1: Script Editor & Project Management (R1, R6)

### T1.1: Project Storage Backend (`project.json` CRUD)
- **Goal**: Implement project management logic in `main.py` (or `projects.py`). Endpoints for list, create, load, duplicate, delete projects inside `projects/<id>/project.json`.
- **Files**: `main.py`
- **Requirements**: R6.1, R6.2
- **Owner**: Builder
- **Status**: todo
- **How to test**: Send API requests (GET/POST/DELETE `/api/projects`) to create, read, duplicate, and delete projects. Verify folder and `project.json` creation on disk.

### T1.2: Script Editor UI, Word Counter, Autosave & Cheatsheet
- **Goal**: Build the script editor UI in `static/index.html` and `static/app.js`: big text area, project sidebar, live word counter & estimated duration (~150 WPM), random target length button (60-180s), pacing cheat sheet popup/accordion, and periodic autosave to active project.
- **Files**: `static/index.html`, `static/app.js`, `static/style.css`
- **Requirements**: R1.1, R1.2, R1.3, R1.4, R1.5, R6.1
- **Owner**: Builder
- **Status**: todo
- **How to test**: Type in the editor, verify word count and duration update live; click random target length; check autosave status and verify `project.json` receives the script.

---

## Phase 2: TTS & Pacing Markup System (R2, tests)

### T2.1: Pacing Markup Parser & Segment Splitter
- **Goal**: Implement `pacing.py` to parse script markup: `[pause X]`, `[slow]...[/slow]`, `[fast]...[/fast]`, `*emphasis*`, `[whisper]...[/whisper]`. Support global presets ("Mystery" default, "Hype", "Calm"). Write automated unit tests.
- **Files**: `pacing.py`, `tests/test_pacing.py`
- **Requirements**: R2.1, R2.2, R2.3, R2.4, R2.5, R2.7, R2.10
- **Owner**: Builder
- **Status**: todo
- **How to test**: Run `pytest tests/test_pacing.py` (or `python -m unittest tests/test_pacing.py`) and ensure all tags and preset parameters pass.

### T2.2: TTS Engine with `edge-tts` & Voice Locking
- **Goal**: Create `tts.py` with `TTSProvider` abstract class and `EdgeTTSProvider`. Fetch available English male voices on first run, let user pick once and save to `config.yaml`. Synthesize individual segments, insert silence, concatenate via FFmpeg, and normalize loudness.
- **Files**: `tts.py`, `config.yaml`, `requirements.txt`
- **Requirements**: C2, Tech stack, R2.6
- **Owner**: Builder
- **Status**: todo
- **How to test**: Run test synthesis on a marked-up text snippet; inspect output audio file for correct pacing pauses and loudness normalization.

### T2.3: TTS Integration & "Nghe thử" UI Button
- **Goal**: Add API endpoint `/api/tts/preview` and UI button "Nghe thử" to synthesize and play the selected paragraph directly in browser. Add voice selection modal if no voice is locked in `config.yaml`.
- **Files**: `main.py`, `static/index.html`, `static/app.js`
- **Requirements**: R2.6, R2.7, R2.9
- **Owner**: Builder
- **Status**: todo
- **How to test**: Highlight a paragraph in the editor, click "Nghe thử", verify audio player renders and plays the generated speech in the browser.

---

## Phase 3: Render Pipeline with Placeholder & Captions (R5.1, R5.2, R5.4, R5.6-R5.8)

### T3.1: Subtitle Generation with `faster-whisper` and .ass Formatting
- **Goal**: Implement `captions.py` using `faster-whisper` to transcribe narration audio into word timestamps. Generate 9:16 vertical `.ass` subtitles: bold font, 2-4 words per line, karaoke-style active word highlighting, safe area centering.
- **Files**: `captions.py`, `requirements.txt`, `tests/test_captions.py`
- **Requirements**: R5.4
- **Owner**: Builder
- **Status**: todo
- **How to test**: Transcribe a test audio file, verify generated `.ass` file content, timestamps, and formatting tags via unit tests.

### T3.2: FFmpeg Video Rendering Engine (GPU Detection & Placeholder Video)
- **Goal**: Implement `render.py` to auto-detect NVIDIA GPU (`h264_nvenc` vs `libx264`). Render 1080x1920 30fps vertical video with dark placeholder background, overlay .ass captions, and mux normalized narration audio.
- **Files**: `render.py`
- **Requirements**: C1, R5.1, R5.2, R5.6, R5.8
- **Owner**: Builder
- **Status**: todo
- **How to test**: Call `render.py` directly with test audio and subtitle files to generate `output.mp4`; verify 1080x1920 vertical format and audio sync.

### T3.3: Background Render Task, Progress Tracking & UI Integration
- **Goal**: Implement background worker thread in `main.py` with progress tracking (TTS synthesis -> Whisper transcription -> FFmpeg render). Connect "Tạo video" button, warning if duration is <60s or >180s, progress bar, and video preview/download in UI.
- **Files**: `main.py`, `static/index.html`, `static/app.js`
- **Requirements**: R5.1, R5.2, R5.6, R5.7, R5.8
- **Owner**: Builder
- **Status**: todo
- **How to test**: Click "Tạo video" on a project; verify progress bar updates through stages and video is displayed upon completion.

---

## Phase 4: Minecraft Footage & Music Integration (R5.3, R5.5)

### T4.1: Minecraft Clip Selection, Looping, Random Offset & 9:16 Crop
- **Goal**: In `render.py`, scan `assets/minecraft/`. If clips exist, pick random clip(s), apply random start offset, loop/concatenate if shorter than narration, crop/scale to 1080x1920 without distortion, and mute game audio. Fallback to dark placeholder if folder is empty.
- **Files**: `render.py`
- **Requirements**: C4, R5.3
- **Owner**: Builder
- **Status**: todo
- **How to test**: Place a test video in `assets/minecraft/`, render project, verify 9:16 crop, muted game audio, and seamless looping. Test again with empty folder to ensure fallback works.

### T4.2: Background Music Ducking
- **Goal**: In `render.py`, scan `assets/music/`. If music files exist, pick a track, loop/cut to match narration duration, and duck volume to -22 dB beneath the voice audio. Skip if folder is empty.
- **Files**: `render.py`
- **Requirements**: R5.5
- **Owner**: Builder
- **Status**: todo
- **How to test**: Place a music track in `assets/music/`, render, and verify background music is audible at -22 dB under clear narration.

---

## Phase 5: Gemini Writing Assistant & Auto-Pace (R3, R2.8)

### T5.1: Gemini Client with `google-genai` SDK
- **Goal**: Create `gemini_client.py` wrapping the official `google-genai` SDK. Load API key from `.env` and model from `config.yaml`. Implement prompts enforcing R3.4 (English, no fake facts, [VERIFY] tags, concise speech-oriented sentences) and retry/error handling.
- **Files**: `gemini_client.py`, `requirements.txt`
- **Requirements**: C2, C5, R3.4, R5.8
- **Owner**: Builder
- **Status**: todo
- **How to test**: Execute standalone script calling Gemini API to verify correct response formatting and error handling when key is missing/invalid.

### T5.2: Writing Assistant UI Side Panel
- **Goal**: Add UI panel and endpoints for Gemini assistant: "Gợi ý đoạn tiếp theo" (3 alternatives), "Viết lại bài đang dở" (with before/after diff preview), and "Dựng khung từ đầu" (outline & first draft), each with "ghi chú cho AI" input box.
- **Files**: `gemini_client.py`, `main.py`, `static/index.html`, `static/app.js`
- **Requirements**: R3.1, R3.2, R3.3, R3.4
- **Owner**: Builder
- **Status**: todo
- **How to test**: Test each assistant action in the UI, check before/after diff dialog, and accept suggested text into the editor.

### T5.3: Auto-Pace Feature
- **Goal**: Implement "Tự thêm nhịp (auto-pace)" button and endpoint using Gemini to insert pacing markup (`[fast]`, `[slow]`, `[pause]`, `*emphasis*`, `[whisper]`) based on narrative structure. Provide before/after review dialog before applying.
- **Files**: `gemini_client.py`, `main.py`, `static/index.html`, `static/app.js`
- **Requirements**: R2.8
- **Owner**: Builder
- **Status**: todo
- **How to test**: Send a raw script to auto-pace; inspect inserted markup; verify user can preview and accept/reject in UI.

---

## Phase 6: Fact Check Panel & Source Export (R4)

### T6.1: Fact Extraction & Grounded Verification
- **Goal**: Create `factcheck.py` to extract checkable atomic claims from script. Verify claims using Gemini with Google Search grounding (or fallback prompt if grounding unsupported). Classify each claim into exactly two labels: "ĐÃ CHỨNG MINH" (with source URLs and evidence) or "CHƯA RÕ" (with reason).
- **Files**: `factcheck.py`, `requirements.txt`
- **Requirements**: R4.1, R4.2, R4.3, R4.4
- **Owner**: Builder
- **Status**: todo
- **How to test**: Run factcheck on sample script; verify parsed JSON list of claims, labels, source URLs, and summaries.

### T6.2: Fact Check UI Panel & Claim Rewriting
- **Goal**: Implement Fact Check side panel in UI: green/yellow badges, click claim to highlight sentence in script editor, "Sửa câu này cho an toàn" button next to "CHƯA RÕ" claims (Gemini rewrites sentence safely), manual label override, and source URL editing.
- **Files**: `static/index.html`, `static/app.js`, `main.py`
- **Requirements**: R4.5, R4.6, R4.7
- **Owner**: Builder
- **Status**: todo
- **How to test**: Click "Kiểm chứng" in UI, click claims to verify text highlighting, edit a claim label/URL, and test sentence rewriting.

### T6.3: Pre-Render Safety Check & `sources.txt` Export
- **Goal**: In render pipeline, trigger confirmation dialog if any claims remain "CHƯA RÕ". Save claim metadata in `project.json` and export `sources.txt` formatted for YouTube description alongside `output.mp4`.
- **Files**: `main.py`, `render.py`, `static/app.js`
- **Requirements**: R4.8, R4.9
- **Owner**: Builder
- **Status**: todo
- **How to test**: Attempt to render with an unverified claim, verify warning confirmation prompt appears; verify `sources.txt` is created upon rendering.

---

## Phase 7: Polish, Offline Kokoro Fallback & Error Handling (R7, R5.8)

### T7.1: Offline Kokoro TTS Provider Fallback
- **Goal**: Implement `KokoroTTSProvider` in `tts.py`. Allow automatic fallback or manual toggle if internet is unavailable or `edge-tts` fails.
- **Files**: `tts.py`, `requirements.txt`, `config.yaml`
- **Requirements**: Tech stack (Kokoro fallback), C2
- **Owner**: Builder
- **Status**: todo
- **How to test**: Disconnect network or mock edge-tts failure; verify speech synthesis succeeds using local Kokoro model.

### T7.2: Vietnamese Error Handling & Diagnostics
- **Goal**: Add friendly, actionable Vietnamese error handling throughout the application (FFmpeg missing, Gemini API key missing, empty video clips folder, network errors, rate limit handling with retry count).
- **Files**: `main.py`, `render.py`, `gemini_client.py`, `static/app.js`
- **Requirements**: R5.8
- **Owner**: Builder
- **Status**: todo
- **How to test**: Test error states (empty API key, invalid FFmpeg path) and verify descriptive Vietnamese alerts appear in the UI.

### T7.3: Complete Documentation & Final Verification
- **Goal**: Finalize `README.md` with complete installation instructions (Python, winget FFmpeg, Gemini API key, assets folder setup) and troubleshooting guide. Update `CHANGELOG.md`. Conduct end-to-end user workflow test.
- **Files**: `README.md`, `CHANGELOG.md`
- **Requirements**: R7.1, R7.3, Definition of Done
- **Owner**: Builder
- **Status**: todo
- **How to test**: Follow `README.md` from scratch, produce a sample 60-180s YouTube Short with fact check sources, and verify all acceptance criteria.
