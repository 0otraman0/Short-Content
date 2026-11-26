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

### T0.3: Windows Launcher `start.bat` & Vietnamese Setup Guide
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

### T2.3: TTS Integration & "Nghe thá»­" UI Button
- **Goal**: Add API endpoint `/api/tts/preview` and UI button "Nghe thá»­" to synthesize and play selected paragraph in browser. Add voice selection modal.
- **Files**: `main.py`, `static/index.html`, `static/app.js`
- **Requirements**: R2.6, R2.7, R2.9
- **Owner**: Builder
- **Status**: done
- **How to test**: Highlight text, click "Nghe thá»­", verify in-browser playback.

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
- **Goal**: Update `main.py` and UI to replace video rendering with project export: endpoint `POST /api/projects/{id}/export` producing `narration.mp3` (or `.wav`), `subtitles.srt`, and `sources.txt` inside `projects/<id>/`. Update UI: change "Táº¡o video" to "Xuáº¥t Audio & Phá»¥ Ä‘á»", display progress modal, and offer direct download links for the exported files. Remove legacy video render endpoints and `render.py`.
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
- **Goal**: Add UI panel and endpoints for Gemini assistant: "Gá»£i Ã½ Ä‘oáº¡n tiáº¿p theo", "Viáº¿t láº¡i bÃ i Ä‘ang dá»Ÿ" (with before/after diff preview), and "Dá»±ng khung tá»« Ä‘áº§u", each with "ghi chÃº cho AI" input box.
- **Files**: `gemini_client.py`, `main.py`, `static/index.html`, `static/app.js`
- **Requirements**: R3.1, R3.2, R3.3, R3.4
- **Owner**: Builder
- **Status**: done
- **How to test**: Test each assistant action in UI, check before/after diff dialog, and accept suggested text into editor.

### T4.3: Auto-Pace Feature
- **Goal**: Implement "Tá»± thÃªm nhá»‹p (auto-pace)" button and endpoint using Gemini to insert pacing markup (`[fast]`, `[slow]`, `[pause]`, `*emphasis*`, `[whisper]`) based on narrative structure. Provide before/after review dialog.
- **Files**: `gemini_client.py`, `main.py`, `static/index.html`, `static/app.js`
- **Requirements**: R2.8
- **Owner**: Builder
- **Status**: done
- **How to test**: Send raw script to auto-pace; inspect inserted markup; verify user can preview and accept/reject in UI.

---

## Phase 5: Fact Check Panel & Source Export (R4)

### T5.1: Fact Extraction & Grounded Verification
- **Goal**: Create `factcheck.py` to extract checkable atomic claims from script. Verify claims using Gemini with Google Search grounding (or fallback prompt). Classify claims into exactly two labels: "ÄÃƒ CHá»¨NG MINH" (with source URLs and evidence) or "CHÆ¯A RÃ•" (with reason).
- **Files**: `factcheck.py`, `requirements.txt`
- **Requirements**: R4.1, R4.2, R4.3, R4.4
- **Owner**: Builder
- **Status**: done
- **How to test**: Run factcheck on sample script; verify parsed JSON list of claims, labels, source URLs, and summaries.

### T5.2: Fact Check UI Panel & Claim Rewriting
- **Goal**: Implement Fact Check side panel in UI: green/yellow badges, click claim to highlight sentence in script editor, "Sá»­a cÃ¢u nÃ y cho an toÃ n" button next to "CHÆ¯A RÃ•" claims, manual label override, and source URL editing.
- **Files**: `static/index.html`, `static/app.js`, `main.py`
- **Requirements**: R4.5, R4.6, R4.7
- **Owner**: Builder
- **Status**: done
- **How to test**: Click "Kiá»ƒm chá»©ng" in UI, click claims to verify text highlighting, edit claim label/URL, and test sentence rewriting.

### T5.3: Pre-Export Safety Check & `sources.txt` Export
- **Goal**: In export pipeline, trigger confirmation dialog if any claims remain "CHÆ¯A RÃ•". Save claim metadata in `project.json` and export `sources.txt` formatted for YouTube description inside the project folder.
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
- **How to test**: Disconnect network or mock edge-tts failure; verify speech synthesis succeeds using local Kokoro model.

### T6.2: Vietnamese Error Handling & Diagnostics
- **Goal**: Add friendly, actionable Vietnamese error handling throughout the application (FFmpeg missing, Gemini API key missing, network errors, rate limit handling with retry count).
- **Files**: `main.py`, `gemini_client.py`, `static/app.js`
- **Requirements**: R5.7
- **Owner**: Builder
- **Status**: done
- **How to test**: Test error states and verify descriptive Vietnamese alerts appear in UI.

### T6.3: Complete Documentation & Final Verification
- **Goal**: Finalize `README.md` with complete installation instructions and troubleshooting guide. Update `CHANGELOG.md`. Conduct end-to-end user workflow test from script to exported audio, .srt, and sources.txt.
- **Files**: `README.md`, `CHANGELOG.md`
- **Requirements**: R7.1, R7.3, Definition of Done
- **Owner**: Builder
- **Status**: done
- **How to test**: Follow `README.md` from scratch, produce a sample package (`narration.mp3`, `subtitles.srt`, `sources.txt`), and verify all acceptance criteria.

---

## Phase 7: Export History & Multi-Job Audio Storage (R5.8, R5.9)

### T7.1: Backend Job-isolated Export Storage & Endpoints
- **Goal**: LÆ°u thÃ nh pháº©m má»—i láº§n xuáº¥t vÃ o `projects/<id>/exports/<job_id>/` (narration.mp3, subtitles.srt, sources.txt, metadata.json), ghi nháº­n vÃ o `project.json`. Bá»• sung API láº¥y danh sÃ¡ch exports vÃ  stream/download theo tá»«ng job_id Ä‘á»™c láº­p.
- **Files**: `main.py`, `tests/test_export_pipeline.py`
- **Requirements**: R5.8
- **Owner**: Builder
- **Status**: done
- **How to test**: Cháº¡y test xuáº¥t 2 job liÃªn tiáº¿p, kiá»ƒm tra 2 thÆ° má»¥c job Ä‘á»™c láº­p tá»“n táº¡i, API tráº£ vá» Ä‘Ãºng audio tá»«ng job.

### T7.2: Export History UI & Audio Playback per Job
- **Goal**: ThÃªm giao diá»‡n danh sÃ¡ch "Lá»‹ch sá»­ xuáº¥t" trong UI, cho phÃ©p nghe láº¡i audio cá»§a tá»«ng job, xem thá»i gian xuáº¥t, Ä‘á»™ dÃ i vÃ  táº£i riÃªng tá»«ng file cá»§a job Ä‘Ã³.
- **Files**: `static/index.html`, `static/app.js`, `static/style.css`
- **Requirements**: R5.9
- **Owner**: Builder
- **Status**: done
- **How to test**: Má»Ÿ trÃ¬nh duyá»‡t, xuáº¥t thá»­ 2 láº§n, kiá»ƒm tra danh sÃ¡ch hiá»ƒn thá»‹ Ä‘á»§ 2 job vÃ  báº¥m nghe láº¡i tá»«ng job Ä‘á»™c láº­p.

---

## Phase 8: Narration Expressiveness & Audio Enhancement (R2.6, R2.11, R2.12, R3.4)

### T8.1: Coalesced Segment Parsing & Speakability Gemini Prompts
- **Goal**: Cáº£i tiáº¿n `pacing.py` Ä‘á»ƒ tá»•ng há»£p á»Ÿ cáº¥p Ä‘á»™ cÃ¢u/Ä‘oáº¡n tá»± nhiÃªn, chá»‰ tÃ¡ch khi cÃ³ tháº» markup hoáº·c pause tÆ°á»ng minh. Cáº­p nháº­t `gemini_client.py` vá»›i 4 quy táº¯c speakability (xen káº½ Ä‘á»™ dÃ i cÃ¢u, dáº¥u ngáº¯t nhá»‹p, Ä‘áº·t fact á»Ÿ cuá»‘i cÃ¢u, viáº¿t sá»‘ thÃ nh chá»¯).
- **Files**: `pacing.py`, `gemini_client.py`, `tests/test_pacing.py`, `tests/test_gemini.py`
- **Requirements**: R2.6, R3.4
- **Owner**: Builder
- **Status**: done
- **How to test**: Cháº¡y test kiá»ƒm tra Ä‘oáº¡n vÄƒn báº£n khÃ´ng tháº» giá»¯ nguyÃªn 1 segment; kiá»ƒm tra prompt Gemini chá»©a Ä‘áº§y Ä‘á»§ 4 quy táº¯c speakability.

### T8.2: Audio Post-Processing Chain with On/Off Toggles
- **Goal**: TÃ­ch há»£p chuá»—i filter FFmpeg trong `tts.py` gá»“m light compression, male EQ, de-esser, light reverb, loudness normalization vá»›i cÃ¡c cÃ´ng táº¯c báº­t/táº¯t Ä‘á»c tá»« `config.yaml` vÃ  tham sá»‘ hÃ m.
- **Files**: `tts.py`, `config.yaml`, `tests/test_tts.py`
- **Requirements**: R2.12
- **Owner**: Builder
- **Status**: done
- **How to test**: Cháº¡y test xuáº¥t audio vá»›i tá»«ng cáº¥u hÃ¬nh báº­t/táº¯t filter, kiá»ƒm tra Ã¢m thanh Ä‘áº§u ra há»£p lá»‡ vÃ  Ä‘áº¡t chuáº©n loudness.

### T8.3: Paragraph Regeneration, Multi-Take Selector & UI Toggles
- **Goal**: ThÃªm nÃºt "Táº¡o láº¡i" cho tá»«ng Ä‘oáº¡n ká»‹ch báº£n, lÆ°u tá»‘i Ä‘a 4 takes Ä‘á»ƒ nghe thá»­ vÃ  chá»n báº£n Æ°ng Ã½ nháº¥t; thÃªm báº£ng cÃ´ng táº¯c báº­t/táº¯t audio post-processing trÃªn giao diá»‡n.
- **Files**: `main.py`, `static/index.html`, `static/app.js`, `static/style.css`
- **Requirements**: R2.11, R2.12
- **Owner**: Builder
- **Status**: done
- **How to test**: Báº¥m "Táº¡o láº¡i" trÃªn 1 Ä‘oáº¡n ká»‹ch báº£n, táº¡o thá»­ 3-4 takes, nghe láº¡i tá»«ng take vÃ  chá»n; chuyá»ƒn Ä‘á»•i cÃ¡c cÃ´ng táº¯c audio enhancement vÃ  xuáº¥t thá»­.

---

## Phase 9: Pre-Export Narration Audition & Pacing Review (R2.9, R5.10)

### T9.1: In-Editor Paragraph & Full Script Audio Audition Bar
- **Goal**: NÃ¢ng cáº¥p chá»©c nÄƒng Ä‘á»c thá»­ trong trÃ¬nh soáº¡n tháº£o, cho phÃ©p nghe thá»­ Ä‘oáº¡n vÄƒn báº£n hiá»‡n táº¡i hoáº·c toÃ n bá»™ ká»‹ch báº£n vá»›i Ä‘áº§y Ä‘á»§ hiá»‡u á»©ng nhá»‹p Ä‘iá»‡u (pause, slow, fast, emphasis) vÃ  Audio FX; cáº£i tiáº¿n thanh nghe thá»­ cÃ³ timeline vÃ  thá»i lÆ°á»£ng thá»±c.
- **Files**: `main.py`, `static/index.html`, `static/app.js`, `static/style.css`
- **Requirements**: R2.9
- **Owner**: Builder
- **Status**: done
- **How to test**: Viáº¿t ká»‹ch báº£n cÃ³ cÃ¡c tháº» [slow], [pause], *emphasis*, báº¥m "Äá»c thá»­" vÃ  kiá»ƒm tra thanh player phÃ¡t Ä‘Ãºng Ã¢m thanh nháº¥n nhÃ¡ vÃ  thá»i lÆ°á»£ng thá»±c táº¿.

### T9.2: Pre-Export Audition & Pacing Validation in Export Flow
- **Goal**: TÃ­ch há»£p nÃºt "Äá»c thá»­ trÆ°á»›c khi xuáº¥t" vÃ o Modal Xuáº¥t Audio & Phá»¥ Ä‘á», cho phÃ©p ngÆ°á»i dÃ¹ng nghe duyá»‡t toÃ n bá»™ audio trÆ°á»›c khi báº¥m xuáº¥t chÃ­nh thá»©c.
- **Files**: `static/index.html`, `static/app.js`, `static/style.css`
- **Requirements**: R5.10
- **Owner**: Builder
- **Status**: done
- **How to test**: Má»Ÿ modal xuáº¥t, báº¥m "Äá»c thá»­ trÆ°á»›c khi xuáº¥t", nghe kiá»ƒm tra toÃ n bÃ i rá»“i má»›i báº¥m "Tiáº¿n hÃ nh xuáº¥t".

---

## Phase 10: Extended Pacing Tags & Quick Pacing Toolbar (R2.13, R1.4)

### T10.1: Extended Pacing Markup Parser & Gemini Auto-Pace Upgrade
- **Goal**: Má»Ÿ rá»™ng há»‡ thá»‘ng nhá»‹p Ä‘iá»‡u thÃªm 5 tháº» má»›i: `[deep]` (giá»ng tráº§m ma má»‹ -6Hz, -8%), `[shock]` (giá»ng giáº­t gÃ¢n, ngáº¡c nhiÃªn +6Hz, +15%), `[urgent]` (dá»“n dáº­p, Ä‘áº¿m ngÆ°á»£c +22%), `[solemn]` (láº¯ng Ä‘á»ng, trang nghiÃªm -20%, -3Hz), `[loud]` (to vang, cáº£nh bÃ¡o +30% vol). NÃ¢ng cáº¥p prompt `auto_pace` trong `gemini_client.py` Ä‘á»ƒ AI tá»± Ä‘á»™ng phá»‘i há»£p Ä‘áº§y Ä‘á»§ 10 tháº» nhá»‹p Ä‘iá»‡u.
- **Files**: `pacing.py`, `gemini_client.py`, `tests/test_pacing.py`
- **Requirements**: R2.8, R2.13
- **Owner**: Builder
- **Status**: done
- **How to test**: Viáº¿t unit test trong `tests/test_pacing.py` xÃ¡c minh tá»«ng tháº» má»›i Ä‘Æ°á»£c parse thÃ nh Ä‘Ãºng `SpeechSegment` vá»›i rate, pitch, volume tÆ°Æ¡ng á»©ng. Test passed.

### T10.2: Quick Pacing Toolbar & UI Cheatsheet Upgrade
- **Goal**: NÃ¢ng cáº¥p Cheatsheet Ä‘áº§y Ä‘á»§ 10 tháº» nhá»‹p Ä‘iá»‡u vÃ  bá»• sung thanh nÃºt báº¥m chÃ¨n nhanh (Quick Pacing Toolbar) trÃªn khung soáº¡n tháº£o: ngÆ°á»i dÃ¹ng bÃ´i Ä‘en cÃ¢u/tá»« vÃ  báº¥m chÃ¨n nhanh tháº» nhá»‹p.
- **Files**: `static/index.html`, `static/style.css`, `static/app.js`, `tests/test_ui_layout.py`
- **Requirements**: R1.4, R2.13
- **Owner**: Builder
- **Status**: done
- **How to test**: BÃ´i Ä‘en má»™t Ä‘oáº¡n text trong editor, báº¥m cÃ¡c nÃºt chÃ¨n nhá»‹p, kiá»ƒm tra tháº» Ä‘Æ°á»£c bá»c chÃ­nh xÃ¡c quanh text Ä‘Ã£ chá»n. Test passed.

---

## Phase 11: Project Management Enhancement (Rename Project - R6.1)

### T11.1: Project Renaming on Top Bar and Sidebar List
- **Goal**: Há»— trá»£ Ä‘á»•i tÃªn dá»± Ã¡n linh hoáº¡t: (1) ThÃªm icon sá»­a tÃªn `âœï¸` vÃ  xá»­ lÃ½ Enter/blur lÆ°u ngay trÃªn thanh Top Bar; (2) ThÃªm nÃºt `âœï¸ (Äá»•i tÃªn)` trÃªn tá»«ng dá»± Ã¡n á»Ÿ Sidebar Ä‘á»ƒ Ä‘á»•i tÃªn nhanh chÃ³ng.
- **Files**: `static/index.html`, `static/style.css`, `static/app.js`, `tests/test_ui_layout.py`
- **Requirements**: R6.1
- **Owner**: Builder
- **Status**: done
- **How to test**: Äá»•i tÃªn dá»± Ã¡n tá»« Ã´ Top Bar hoáº·c nÃºt `âœï¸` á»Ÿ Sidebar, kiá»ƒm tra tÃªn má»›i Ä‘Æ°á»£c lÆ°u vÃ o `project.json` vÃ  hiá»ƒn thá»‹ Ä‘á»“ng bá»™ á»Ÿ cáº£ hai vá»‹ trÃ­. Test passed.


---

## Phase 12: Refactoring to 3-Layer Architecture

### T12.1: Data Access & Infrastructure Layer
- **Goal**: Xây dựng tầng 3 (Data Access & Infrastructure): tách logic file I/O dự án vào epositories/project_repository.py; tách EdgeTTS/Kokoro providers vào infrastructure/tts_providers.py, FFmpeg filters vào infrastructure/ffmpeg_processor.py, whisper engine vào infrastructure/whisper_adapter.py.
- **Files**: epositories/__init__.py, epositories/project_repository.py, infrastructure/__init__.py, infrastructure/tts_providers.py, infrastructure/ffmpeg_processor.py, infrastructure/whisper_adapter.py
- **Requirements**: R6.1, R6.2, R2.12, R5.3
- **Owner**: Builder
- **Status**: done
- **How to test**: Import infrastructure/repositories; check locked voice, enhancements, project CRUD. All OK.

### T12.2: Business Logic Layer (Services)
- **Goal**: Xây dựng tầng 2 (Services): tổ chức các dịch vụ nghiệp vụ độc lập vào services/ (project_service.py, 	ts_service.py, gemini_service.py, actcheck_service.py, export_service.py). Facade pattern giữ root modules tương thích.
- **Files**: services/__init__.py, services/project_service.py, services/tts_service.py, services/gemini_service.py, services/factcheck_service.py, services/export_service.py
- **Requirements**: R1-R6
- **Owner**: Builder
- **Status**: done
- **How to test**: Import tất cả services; verify enhancements keys, GeminiService methods. All OK.

### T12.3: Presentation Layer & Routers
- **Goal**: Xây dựng tầng 1 (Presentation / Routers): phân tách các endpoints từ main.py sang outers/ (5 router file), tinh gọn main.py thành bootstrap loader (~120 dòng).
- **Files**: outers/__init__.py, outers/projects_router.py, outers/tts_router.py, outers/gemini_router.py, outers/factcheck_router.py, outers/export_router.py, main.py
- **Requirements**: R1-R6
- **Owner**: Builder
- **Status**: done
- **How to test**: Import main app; verify routes list loads correctly. All OK.

### T12.4: Verification & Documentation
- **Goal**: Chạy toàn bộ 55 tests, cập nhật CHANGELOG, DECISIONS, PLAN, STATE.
- **Files**: 	ests/test_*.py, CHANGELOG.md, DECISIONS.md, PLAN.md, STATE.md
- **Requirements**: R7
- **Owner**: Builder
- **Status**: done
- **How to test**: python -m unittest discover tests -> 55/55 OK.
