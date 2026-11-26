# PLAN.md - Implementation Tasks

Owner roles: Planner, Builder, Reviewer.
Rules: One task at a time. Builder touches ONLY the files listed for that task. Next task starts only after previous test passes.

---

## Phase 0: Skeleton & Setup (C3, C4, R7) - COMPLETED

### T0.1: Git & Initial Configuration Skeleton
- **Goal**: Initialize git repository, setup `.gitignore`, `.env.example`, and default `config.yaml`.
- **Files**: `.gitignore`, `.env.example`, `config.yaml`
- **Requirements**: C4, R7.2
- **Owner**: Builder
- **Status**: done
- **How to test**: Verify `.gitignore`, `.env.example`, and `config.yaml` parse properly.

### T0.2: Minimal FastAPI Backend & UI Shell
- **Goal**: Setup `requirements.txt` with base dependencies. Create `main.py` serving clean dark-theme HTML single page at `http://127.0.0.1:8000`.
- **Files**: `requirements.txt`, `main.py`, `static/index.html`, `static/style.css`
- **Requirements**: C1, C3, R7
- **Owner**: Builder
- **Status**: done
- **How to test**: Run server, open web UI, verify status API.

### T0.3: Windows Launcher `start.bat` & Setup Guide
- **Goal**: Create `start.bat` to automate venv creation, requirements installation, FFmpeg verification, server launch, and browser opening. Create `README.md`.
- **Files**: `start.bat`, `README.md`
- **Requirements**: C3, R7.1
- **Owner**: Builder
- **Status**: done
- **How to test**: Execute `start.bat` in Windows terminal; verify environment setups and browser opens to app.

---

## Phase 1: Script Editor & Project Management (R1, R6) - COMPLETED

### T1.1: Project Storage Backend (`project.json` CRUD)
- **Goal**: Implement project management logic in `main.py`. Endpoints for list, create, load, duplicate, delete projects inside `projects/<id>/project.json`.
- **Files**: `main.py`
- **Requirements**: R6.1, R6.2
- **Owner**: Builder
- **Status**: done
- **How to test**: Send API requests (GET/POST/DELETE `/api/projects`) to create, read, duplicate, and delete projects.

### T1.2: Script Editor UI, Word Counter, Autosave & Cheatsheet
- **Goal**: Build script editor UI in `static/index.html` and `static/app.js`: big text area, project sidebar, live word counter & estimated duration (~150 WPM), random target length button (60-180s), pacing cheat sheet, and debounced autosave.
- **Files**: `static/index.html`, `static/app.js`, `static/style.css`
- **Requirements**: R1.1, R1.2, R1.3, R1.4, R1.5, R6.1
- **Owner**: Builder
- **Status**: done
- **How to test**: Type in editor, check stats live update, test random target length and autosave.

---

## Phase 2: TTS & Pacing Markup System (R2, tests) - COMPLETED

### T2.1: Pacing Markup Parser & Segment Splitter
- **Goal**: Implement `pacing.py` to parse script markup: `[pause X]`, `[slow]...[/slow]`, `[fast]...[/fast]`, `*emphasis*`, `[whisper]...[/whisper]`. Support presets ("Mystery", "Hype", "Calm").
- **Files**: `pacing.py`, `tests/test_pacing.py`
- **Requirements**: R2.1, R2.2, R2.3, R2.4, R2.5, R2.7, R2.10
- **Owner**: Builder
- **Status**: done
- **How to test**: Run `python -m unittest tests/test_pacing.py`.

### T2.2: TTS Engine with `edge-tts` & Voice Locking
- **Goal**: Create `tts.py` with `TTSProvider` and `EdgeTTSProvider`. Fetch English male voices, lock in `config.yaml`, synthesize segments, insert silence, concatenate via FFmpeg, and normalize loudness (`loudnorm`).
- **Files**: `tts.py`, `config.yaml`, `requirements.txt`
- **Requirements**: C2, Tech stack, R2.6
- **Owner**: Builder
- **Status**: done
- **How to test**: Run test synthesis on marked-up script; inspect audio for pauses and loudness normalization.

### T2.3: TTS Integration & Preview Audio UI Button
- **Goal**: Add API endpoint `/api/tts/preview` and UI button "Preview Audio" to synthesize and play selected paragraph in browser. Add voice selection modal.
- **Files**: `main.py`, `static/index.html`, `static/app.js`
- **Requirements**: R2.6, R2.7, R2.9
- **Owner**: Builder
- **Status**: done
- **How to test**: Highlight text, click "Preview Audio", verify in-browser playback.

---

## Phase 3: SRT Subtitle Generation & Project Export Pipeline (R5)

### T3.1: Subtitle Generation with `faster-whisper` and .srt Formatting
- **Goal**: Update `captions.py` to transcribe narration audio into word timestamps using `faster-whisper` and generate clean standard `.srt` format (full natural phrases of about 5-8 words per line, standard timestamp format `HH:MM:SS,mmm --> HH:MM:SS,mmm`).
- **Files**: `captions.py`, `tests/test_captions.py`
- **Requirements**: R5.3
- **Owner**: Builder
- **Status**: done
- **How to test**: Transcribe test audio with `captions.py`, verify `.srt` output format, timing syntax, and line word-count constraint (5-8 words per block).

### T3.2: Export Pipeline & UI Integration (Audio + SRT + Sources)
- **Goal**: Update `main.py` and UI to replace video rendering with project export: endpoint `POST /api/projects/{id}/export` producing `narration.mp3` (or `.wav`), `subtitles.srt`, and `sources.txt` inside `projects/<id>/`. Update UI: change "Render Video" to "Export Audio & Subtitles", display progress modal, and offer direct download links for the exported files. Remove legacy video render endpoints and `render.py`.
- **Files**: `main.py`, `static/index.html`, `static/app.js`, `static/style.css`, `tests/test_export_pipeline.py`
- **Requirements**: R5.1, R5.2, R5.4, R5.5, R5.6, R5.7
- **Owner**: Builder
- **Status**: done
- **How to test**: Trigger export on a project, check progress modal, verify `narration.mp3`, `subtitles.srt`, and `sources.txt` are created in project folder, and download links work in UI.

---

## Phase 4: Gemini Writing Assistant & Auto-Pace (R3, R2.8)

### T4.1: Gemini Client with `google-genai` SDK
- **Goal**: Create `gemini_client.py` wrapping the official `google-genai` SDK. Load API key from `.env` and model from `config.yaml`. Enforce R3.4 rules (English, no fake stats, [VERIFY] flags, short speakable sentences) and retry/error handling.
- **Files**: `gemini_client.py`, `requirements.txt`
- **Requirements**: C2, C4, R3.4
- **Owner**: Builder
- **Status**: done
- **How to test**: Run standalone test script calling Gemini API to verify response formatting and error handling.

### T4.2: Writing Assistant UI Side Panel
- **Goal**: Add UI panel and endpoints for Gemini assistant: "Suggest Next Paragraphs", "Rewrite Draft" (with before/after diff preview), and "Outline Topic", each with an AI guidance note input box.
- **Files**: `gemini_client.py`, `main.py`, `static/index.html`, `static/app.js`
- **Requirements**: R3.1, R3.2, R3.3, R3.4
- **Owner**: Builder
- **Status**: done
- **How to test**: Test each assistant action in UI, check before/after diff dialog, and accept suggested text into editor.

### T4.3: Auto-Pace Feature
- **Goal**: Implement "Auto-Pace" button and endpoint using Gemini to insert pacing markup (`[fast]`, `[slow]`, `[pause]`, `*emphasis*`, `[whisper]`) based on narrative structure. Provide before/after review dialog.
- **Files**: `gemini_client.py`, `main.py`, `static/index.html`, `static/app.js`
- **Requirements**: R2.8
- **Owner**: Builder
- **Status**: done
- **How to test**: Send raw script to auto-pace; inspect inserted markup; verify user can preview and accept/reject in UI.

---

## Phase 5: Fact Check Panel & Source Export (R4)

### T5.1: Fact Extraction & Grounded Verification
- **Goal**: Create `factcheck.py` to extract checkable atomic claims from script. Verify claims using Gemini with Google Search grounding (or fallback prompt). Classify claims into exactly two labels: "ĐÃ CHỨNG MINH" (PROVEN, with source URLs and evidence) or "CHƯA RÕ" (UNCLEAR, with reason).
- **Files**: `factcheck.py`, `requirements.txt`
- **Requirements**: R4.1, R4.2, R4.3, R4.4
- **Owner**: Builder
- **Status**: done
- **How to test**: Run factcheck on sample script; verify parsed JSON list of claims, labels, source URLs, and summaries.

### T5.2: Fact Check UI Panel & Claim Rewriting
- **Goal**: Implement Fact Check side panel in UI: green/yellow badges, click claim to highlight sentence in script editor, "Safe Rewrite" button next to "CHƯA RÕ" claims, manual label override, and source URL editing.
- **Files**: `static/index.html`, `static/app.js`, `main.py`
- **Requirements**: R4.5, R4.6, R4.7
- **Owner**: Builder
- **Status**: done
- **How to test**: Click "Fact Check" in UI, click claims to verify text highlighting, edit claim label/URL, and test sentence rewriting.

### T5.3: Pre-Export Safety Check & `sources.txt` Export
- **Goal**: In export pipeline, trigger confirmation dialog if any claims remain "CHƯA RÕ". Save claim metadata in `project.json` and export `sources.txt` formatted for YouTube description inside the project folder.
- **Files**: `main.py`, `static/app.js`
- **Requirements**: R4.8, R4.9
- **Owner**: Builder
- **Status**: done
- **How to test**: Attempt export with an unverified claim, verify warning confirmation prompt appears; verify `sources.txt` is created upon export.

---

## Phase 6: Polish, Offline Kokoro Fallback & Error Handling (R7, R5.7)

### T6.1: Offline Kokoro TTS Provider Fallback
- **Goal**: Implement `KokoroTTSProvider` in `tts.py`. Allow automatic fallback or manual toggle if internet is unavailable or `edge-tts` fails.
- **Files**: `tts.py`, `requirements.txt`, `config.yaml`
- **Requirements**: Tech stack (Kokoro fallback), C2
- **Owner**: Builder
- **Status**: done
- **How to test**: Disable network/simulate failure; verify narration falls back to Kokoro TTS and produces valid audio.

### T6.2: Actionable Error Handling & Status Diagnostics
- **Goal**: Add friendly, localized error messages for Gemini API failures (rate limits, key invalid, network errors), FFmpeg missing check on `/api/status`, and clear UI alerts.
- **Files**: `gemini_client.py`, `main.py`, `static/app.js`
- **Requirements**: R5.7
- **Owner**: Builder
- **Status**: done
- **How to test**: Trigger 429 / bad API key; verify friendly banner appears in UI with guidance.

### T6.3: Documentation & Full Workflow Verification
- **Goal**: Review `README.md` and verify end-to-end user workflow: idea -> outline -> script -> pacing -> fact check -> audio + SRT + sources export.
- **Files**: `README.md`, `CHANGELOG.md`
- **Requirements**: R7.1, R7.3, Definition of Done
- **Owner**: Builder
- **Status**: done
- **How to test**: Follow `README.md` from scratch, produce a sample package (`narration.mp3`, `subtitles.srt`, `sources.txt`), and verify all acceptance criteria.

---

## Phase 7: Export History & Multi-Job Audio Storage (R5.8, R5.9)

### T7.1: Backend Job-isolated Export Storage & Endpoints
- **Goal**: Save output assets for every export into `projects/<id>/exports/<job_id>/` (`narration.mp3`, `subtitles.srt`, `sources.txt`, `metadata.json`), and record job details in `project.json`. Provide API endpoints to list exports and download files per job independently.
- **Files**: `main.py`, `tests/test_export_pipeline.py`
- **Requirements**: R5.8
- **Owner**: Builder
- **Status**: done
- **How to test**: Run test creating two consecutive export jobs; verify both independent directories exist and API retrieves each job's audio correctly.

### T7.2: Export History UI & Audio Playback per Job
- **Goal**: Add "Export History" modal in web UI allowing users to replay past audio exports, view export timestamp and duration, and download individual files per job.
- **Files**: `static/index.html`, `static/app.js`, `static/style.css`
- **Requirements**: R5.9
- **Owner**: Builder
- **Status**: done
- **How to test**: Open browser, perform two test exports, verify the modal lists both jobs, and verify audio playback for each job independently.

---

## Phase 8: Narration Expressiveness & Audio Enhancement (R2.6, R2.11, R2.12, R3.4)

### T8.1: Coalesced Segment Parsing & Speakability Gemini Prompts
- **Goal**: Upgrade `pacing.py` to synthesize speech at sentence/paragraph level by default, splitting only upon explicit markup tags or pauses. Update `gemini_client.py` with 4 speakability rules (alternating sentence lengths, punctuation rhythm breaks, punchline/fact placed at the end, spelling ambiguous numbers as words).
- **Files**: `pacing.py`, `gemini_client.py`, `tests/test_pacing.py`, `tests/test_gemini.py`
- **Requirements**: R2.6, R3.4
- **Owner**: Builder
- **Status**: done
- **How to test**: Run test verifying plain text sentences remain single cohesive segments; check Gemini prompt contains all 4 speakability guidelines.

### T8.2: Audio Post-Processing Chain with On/Off Toggles
- **Goal**: Integrate FFmpeg filter chain in `tts.py` including light compression, male EQ, de-esser, acoustic reflection, and EBU R128 loudness normalization with configurable toggles in `config.yaml`.
- **Files**: `tts.py`, `config.yaml`, `tests/test_tts.py`
- **Requirements**: R2.12
- **Owner**: Builder
- **Status**: done
- **How to test**: Run test exporting audio with various filter toggle combinations; verify output audio integrity and loudness compliance.

### T8.3: Paragraph Regeneration, Multi-Take Selector & UI Toggles
- **Goal**: Add "Regenerate" button for individual script paragraphs, storing up to 4 takes to audition and select the best version. Add audio post-processing toggles modal in UI.
- **Files**: `main.py`, `static/index.html`, `static/app.js`, `static/style.css`
- **Requirements**: R2.11, R2.12
- **Owner**: Builder
- **Status**: done
- **How to test**: Click "Regenerate" on a paragraph, generate 3-4 takes, audition and select active take; toggle audio enhancement settings and test audio export.

---

## Phase 9: Pre-Export Narration Audition & Pacing Review (R2.9, R5.10)

### T9.1: In-Editor Paragraph & Full Script Audio Audition Bar
- **Goal**: Upgrade in-editor audio audition bar to allow listening to either the active paragraph or full script with all active pacing tags (pause, slow, fast, emphasis) and Audio FX. Provide timeline and real duration indicator.
- **Files**: `main.py`, `static/index.html`, `static/app.js`, `static/style.css`
- **Requirements**: R2.9
- **Owner**: Builder
- **Status**: done
- **How to test**: Write script with `[slow]`, `[pause]`, `*emphasis*`, click preview buttons, verify player reproduces correct cadence and exact duration.

### T9.2: Pre-Export Audition & Pacing Validation in Export Flow
- **Goal**: Embed pre-export audition review player into the Export modal, allowing creators to validate complete audio pacing before triggering export.
- **Files**: `static/index.html`, `static/app.js`, `static/style.css`
- **Requirements**: R5.10
- **Owner**: Builder
- **Status**: done
- **How to test**: Open export modal, click "Audition Audio", verify playback of the entire narration before committing to export.

---

## Phase 10: Extended Pacing Tags & Quick Pacing Toolbar (R2.13, R1.4)

### T10.1: Extended Pacing Markup Parser & Gemini Auto-Pace Upgrade
- **Goal**: Expand pacing markup with 5 additional emotional styles: `[deep]` (mysterious bass: -6Hz, -8%), `[shock]` (revelation & surprise: +6Hz, +15%), `[urgent]` (ticking clock urgency: +22%), `[solemn]` (reflective closing: -20%, -3Hz), `[loud]` (alarm & warning: +30% vol). Upgrade `auto_pace` prompt in `gemini_client.py` to coordinate all 10 pacing tags dynamically.
- **Files**: `pacing.py`, `gemini_client.py`, `tests/test_pacing.py`
- **Requirements**: R2.8, R2.13
- **Owner**: Builder
- **Status**: done
- **How to test**: Write unit test in `tests/test_pacing.py` verifying each new tag parses into accurate `SpeechSegment` with corresponding rate, pitch, and volume.

### T10.2: Quick Pacing Toolbar & UI Cheatsheet Upgrade
- **Goal**: Upgrade cheatsheet with all 10 pacing tags and add Quick Pacing Toolbar above the editor: users highlight text and click buttons to instantly wrap markup tags.
- **Files**: `static/index.html`, `static/style.css`, `static/app.js`, `tests/test_ui_layout.py`
- **Requirements**: R1.4, R2.13
- **Owner**: Builder
- **Status**: done
- **How to test**: Highlight text in editor, click toolbar buttons, verify selected text is wrapped accurately with pacing tags.

---

## Phase 11: Project Management Enhancement (Rename Project - R6.1)

### T11.1: Project Renaming on Top Bar and Sidebar List
- **Goal**: Support flexible project renaming: (1) Interactive rename button `✏️` and Enter/blur instant save on Top Navigation Bar; (2) Rename button `✏️` on each sidebar project item.
- **Files**: `static/index.html`, `static/style.css`, `static/app.js`, `tests/test_ui_layout.py`
- **Requirements**: R6.1
- **Owner**: Builder
- **Status**: done
- **How to test**: Rename project from Top Bar or Sidebar `✏️` button; verify updated title persists in `project.json` and synchronizes across UI.

---

## Phase 12: Refactoring to 3-Layer Architecture

### T12.1: Data Access & Infrastructure Layer
- **Goal**: Build Layer 3 (Data Access & Infrastructure): extract project file I/O into `repositories/project_repository.py`; extract EdgeTTS/Kokoro providers into `infrastructure/tts_providers.py`, FFmpeg filters into `infrastructure/ffmpeg_processor.py`, and faster-whisper engine into `infrastructure/whisper_adapter.py`.
- **Files**: `repositories/__init__.py`, `repositories/project_repository.py`, `infrastructure/__init__.py`, `infrastructure/tts_providers.py`, `infrastructure/ffmpeg_processor.py`, `infrastructure/whisper_adapter.py`
- **Requirements**: R6.1, R6.2, R2.12, R5.3
- **Owner**: Builder
- **Status**: done
- **How to test**: Import infrastructure/repositories; check locked voice, enhancements, project CRUD. All OK.

### T12.2: Business Logic Layer (Services)
- **Goal**: Build Layer 2 (Services): organize independent business logic into `services/` (`project_service.py`, `tts_service.py`, `gemini_service.py`, `factcheck_service.py`, `export_service.py`).
- **Files**: `services/__init__.py`, `services/project_service.py`, `services/tts_service.py`, `services/gemini_service.py`, `services/factcheck_service.py`, `services/export_service.py`
- **Requirements**: R1-R6
- **Owner**: Builder
- **Status**: done
- **How to test**: Import all services; verify enhancement keys and GeminiService methods. All OK.

### T12.3: Presentation Layer & Routers
- **Goal**: Build Layer 1 (Presentation / Routers): extract all endpoints from `main.py` into `routers/` (5 router files), refactoring `main.py` into a lightweight ~120-line bootstrap application loader.
- **Files**: `routers/__init__.py`, `routers/projects_router.py`, `routers/tts_router.py`, `routers/gemini_router.py`, `routers/factcheck_router.py`, `routers/export_router.py`, `main.py`
- **Requirements**: R1-R6
- **Owner**: Builder
- **Status**: done
- **How to test**: Import main app; verify routes list loads correctly. All OK.

### T12.4: Verification & Documentation
- **Goal**: Run complete test suite (55 tests), update CHANGELOG, DECISIONS, PLAN, STATE.
- **Files**: `tests/test_*.py`, `CHANGELOG.md`, `DECISIONS.md`, `PLAN.md`, `STATE.md`
- **Requirements**: R7
- **Owner**: Builder
- **Status**: done
- **How to test**: `python -m unittest discover tests` -> 55/55 OK.

### T12.5: Thin Facades Cleanup for Root Modules
- **Goal**: Convert legacy root modules (`gemini_client.py`, `factcheck.py`, `captions.py`, `tts.py`) into pure thin facades (re-exports only); relocate all business logic into `services/` and `infrastructure/`.
- **Files**: `services/gemini_service.py`, `services/factcheck_service.py`, `infrastructure/whisper_adapter.py`, `gemini_client.py`, `factcheck.py`, `captions.py`, `tts.py`
- **Requirements**: R1-R7
- **Owner**: Builder
- **Status**: done
- **How to test**: `python -m unittest discover tests` -> 55/55 tests passing, zero regression.

### T12.6: Root Directory Cleanup & Test Suite Modernization
- **Goal**: Relocate `pacing.py` to `services/pacing_service.py`, modernize all imports across `tests/` to target `services/` and `infrastructure/` directly, and permanently delete the 5 root Python files (`captions.py`, `factcheck.py`, `gemini_client.py`, `pacing.py`, `tts.py`). The project root contains `main.py` as the sole Python entry point.
- **Files**: `services/pacing_service.py`, `services/tts_service.py`, `services/__init__.py`, `tests/test_captions.py`, `tests/test_factcheck.py`, `tests/test_gemini.py`, `tests/test_pacing.py`, `tests/test_tts.py`, `tests/test_tts_preview.py`
- **Requirements**: R1-R7
- **Owner**: Builder
- **Status**: done
- **How to test**: `python -m unittest discover tests` (55/55 OK) & `python tests/test_tts_preview.py` (OK). Root directory contains ONLY `main.py`.
