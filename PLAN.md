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

### T2.3: TTS Integration & "Nghe thử" UI Button
- **Goal**: Add API endpoint `/api/tts/preview` and UI button "Nghe thử" to synthesize and play selected paragraph in browser. Add voice selection modal.
- **Files**: `main.py`, `static/index.html`, `static/app.js`
- **Requirements**: R2.6, R2.7, R2.9
- **Owner**: Builder
- **Status**: done
- **How to test**: Highlight text, click "Nghe thử", verify in-browser playback.

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
- **Goal**: Update `main.py` and UI to replace video rendering with project export: endpoint `POST /api/projects/{id}/export` producing `narration.mp3` (or `.wav`), `subtitles.srt`, and `sources.txt` inside `projects/<id>/`. Update UI: change "Tạo video" to "Xuất Audio & Phụ đề", display progress modal, and offer direct download links for the exported files. Remove legacy video render endpoints and `render.py`.
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
- **Goal**: Add UI panel and endpoints for Gemini assistant: "Gợi ý đoạn tiếp theo", "Viết lại bài đang dở" (with before/after diff preview), and "Dựng khung từ đầu", each with "ghi chú cho AI" input box.
- **Files**: `gemini_client.py`, `main.py`, `static/index.html`, `static/app.js`
- **Requirements**: R3.1, R3.2, R3.3, R3.4
- **Owner**: Builder
- **Status**: done
- **How to test**: Test each assistant action in UI, check before/after diff dialog, and accept suggested text into editor.

### T4.3: Auto-Pace Feature
- **Goal**: Implement "Tự thêm nhịp (auto-pace)" button and endpoint using Gemini to insert pacing markup (`[fast]`, `[slow]`, `[pause]`, `*emphasis*`, `[whisper]`) based on narrative structure. Provide before/after review dialog.
- **Files**: `gemini_client.py`, `main.py`, `static/index.html`, `static/app.js`
- **Requirements**: R2.8
- **Owner**: Builder
- **Status**: done
- **How to test**: Send raw script to auto-pace; inspect inserted markup; verify user can preview and accept/reject in UI.

---

## Phase 5: Fact Check Panel & Source Export (R4)

### T5.1: Fact Extraction & Grounded Verification
- **Goal**: Create `factcheck.py` to extract checkable atomic claims from script. Verify claims using Gemini with Google Search grounding (or fallback prompt). Classify claims into exactly two labels: "ĐÃ CHỨNG MINH" (with source URLs and evidence) or "CHƯA RÕ" (with reason).
- **Files**: `factcheck.py`, `requirements.txt`
- **Requirements**: R4.1, R4.2, R4.3, R4.4
- **Owner**: Builder
- **Status**: done
- **How to test**: Run factcheck on sample script; verify parsed JSON list of claims, labels, source URLs, and summaries.

### T5.2: Fact Check UI Panel & Claim Rewriting
- **Goal**: Implement Fact Check side panel in UI: green/yellow badges, click claim to highlight sentence in script editor, "Sửa câu này cho an toàn" button next to "CHƯA RÕ" claims, manual label override, and source URL editing.
- **Files**: `static/index.html`, `static/app.js`, `main.py`
- **Requirements**: R4.5, R4.6, R4.7
- **Owner**: Builder
- **Status**: done
- **How to test**: Click "Kiểm chứng" in UI, click claims to verify text highlighting, edit claim label/URL, and test sentence rewriting.

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
- **Goal**: Lưu thành phẩm mỗi lần xuất vào `projects/<id>/exports/<job_id>/` (narration.mp3, subtitles.srt, sources.txt, metadata.json), ghi nhận vào `project.json`. Bổ sung API lấy danh sách exports và stream/download theo từng job_id độc lập.
- **Files**: `main.py`, `tests/test_export_pipeline.py`
- **Requirements**: R5.8
- **Owner**: Builder
- **Status**: done
- **How to test**: Chạy test xuất 2 job liên tiếp, kiểm tra 2 thư mục job độc lập tồn tại, API trả về đúng audio từng job.

### T7.2: Export History UI & Audio Playback per Job
- **Goal**: Thêm giao diện danh sách "Lịch sử xuất" trong UI, cho phép nghe lại audio của từng job, xem thời gian xuất, độ dài và tải riêng từng file của job đó.
- **Files**: `static/index.html`, `static/app.js`, `static/style.css`
- **Requirements**: R5.9
- **Owner**: Builder
- **Status**: done
- **How to test**: Mở trình duyệt, xuất thử 2 lần, kiểm tra danh sách hiển thị đủ 2 job và bấm nghe lại từng job độc lập.

---

## Phase 8: Narration Expressiveness & Audio Enhancement (R2.6, R2.11, R2.12, R3.4)

### T8.1: Coalesced Segment Parsing & Speakability Gemini Prompts
- **Goal**: Cải tiến `pacing.py` để tổng hợp ở cấp độ câu/đoạn tự nhiên, chỉ tách khi có thẻ markup hoặc pause tường minh. Cập nhật `gemini_client.py` với 4 quy tắc speakability (xen kẽ độ dài câu, dấu ngắt nhịp, đặt fact ở cuối câu, viết số thành chữ).
- **Files**: `pacing.py`, `gemini_client.py`, `tests/test_pacing.py`, `tests/test_gemini.py`
- **Requirements**: R2.6, R3.4
- **Owner**: Builder
- **Status**: done
- **How to test**: Chạy test kiểm tra đoạn văn bản không thẻ giữ nguyên 1 segment; kiểm tra prompt Gemini chứa đầy đủ 4 quy tắc speakability.

### T8.2: Audio Post-Processing Chain with On/Off Toggles
- **Goal**: Tích hợp chuỗi filter FFmpeg trong `tts.py` gồm light compression, male EQ, de-esser, light reverb, loudness normalization với các công tắc bật/tắt đọc từ `config.yaml` và tham số hàm.
- **Files**: `tts.py`, `config.yaml`, `tests/test_tts.py`
- **Requirements**: R2.12
- **Owner**: Builder
- **Status**: done
- **How to test**: Chạy test xuất audio với từng cấu hình bật/tắt filter, kiểm tra âm thanh đầu ra hợp lệ và đạt chuẩn loudness.

### T8.3: Paragraph Regeneration, Multi-Take Selector & UI Toggles
- **Goal**: Thêm nút "Tạo lại" cho từng đoạn kịch bản, lưu tối đa 4 takes để nghe thử và chọn bản ưng ý nhất; thêm bảng công tắc bật/tắt audio post-processing trên giao diện.
- **Files**: `main.py`, `static/index.html`, `static/app.js`, `static/style.css`
- **Requirements**: R2.11, R2.12
- **Owner**: Builder
- **Status**: done
- **How to test**: Bấm "Tạo lại" trên 1 đoạn kịch bản, tạo thử 3-4 takes, nghe lại từng take và chọn; chuyển đổi các công tắc audio enhancement và xuất thử.

---

## Phase 9: Pre-Export Narration Audition & Pacing Review (R2.9, R5.10)

### T9.1: In-Editor Paragraph & Full Script Audio Audition Bar
- **Goal**: Nâng cấp chức năng đọc thử trong trình soạn thảo, cho phép nghe thử đoạn văn bản hiện tại hoặc toàn bộ kịch bản với đầy đủ hiệu ứng nhịp điệu (pause, slow, fast, emphasis) và Audio FX; cải tiến thanh nghe thử có timeline và thời lượng thực.
- **Files**: `main.py`, `static/index.html`, `static/app.js`, `static/style.css`
- **Requirements**: R2.9
- **Owner**: Builder
- **Status**: done
- **How to test**: Viết kịch bản có các thẻ [slow], [pause], *emphasis*, bấm "Đọc thử" và kiểm tra thanh player phát đúng âm thanh nhấn nhá và thời lượng thực tế.

### T9.2: Pre-Export Audition & Pacing Validation in Export Flow
- **Goal**: Tích hợp nút "Đọc thử trước khi xuất" vào Modal Xuất Audio & Phụ đề, cho phép người dùng nghe duyệt toàn bộ audio trước khi bấm xuất chính thức.
- **Files**: `static/index.html`, `static/app.js`, `static/style.css`
- **Requirements**: R5.10
- **Owner**: Builder
- **Status**: todo
- **How to test**: Mở modal xuất, bấm "Đọc thử trước khi xuất", nghe kiểm tra toàn bài rồi mới bấm "Tiến hành xuất".
