# YouTube Shorts Narration Tool

**AI-powered narration synthesizer, standard SRT subtitle generator, and factual claim verification workstation for YouTube Shorts.**  
Runs completely **locally** on Windows via a responsive modern web UI with zero recurring costs and zero subscription dependencies.

---

## 1. Overview

This application streamlines the entire creation workflow for YouTube Shorts creators specializing in verified science facts and narrative storytelling:
- **Intelligent Scriptwriting Assistant (Gemini AI)**: Generate structured script outlines from a topic and target duration (60s–180s), draft continuous follow-up paragraphs, or rewrite drafts into punchy, speakable narration with a compelling 5-second hook.
- **Dynamic Storytelling Pacing (Auto-Pace & Manual Markup)**: Embed expressive narration pacing tags (`[fast]`, `[slow]`, `[pause]`, `*emphasis*`, `[whisper]`, `[deep]`, `[shock]`, `[urgent]`, `[solemn]`, `[loud]`) to deliver captivating auditory rhythm and audience retention.
- **Scientific Fact-Checking & Citation Panel**: Parse individual atomic claims from the script and verify them against academic and institutional sources into two clear categories:
  - **PROVEN ("ĐÃ CHỨNG MINH")**: Verified by consensus or peer-reviewed literature, linked to reputable reference URLs (Nature, Science, NOAA, Wikipedia).
  - **UNCLEAR ("CHƯA RÕ")**: Disputed, anecdotal, or lacking documentation, offering a 1-click **Safe Rewrite** button to rephrase with scientific caution.
- **Studio-Quality TTS Engine**:
  - Primary provider: Microsoft Edge Neural TTS with natural English male voices (free, human-like cadence).
  - Built-in **automatic offline fallback to Kokoro TTS**: seamlessly switches to local on-device neural voice generation during network dropouts without interrupting your session.
  - Automatic broadcast loudness normalization adhering to **EBU R128 (-16 LUFS)** standards.
  - Complete audio post-processing FX chain: male vocal EQ, dynamic compression, de-esser, acoustic reflection, and true peak control.
- **Word-Level Captions & SRT Export**: Powered by `faster-whisper`, generating word-level precision timestamps grouped into natural spoken phrases (5–8 words per subtitle line).
- **Export Package**: Directly archives all assets into the project directory:
  1. `narration.mp3`: Normalized narration audio with accurate silence gaps and FX enhancement.
  2. `subtitles.srt`: Subtitle file ready for instant import into CapCut, Adobe Premiere Pro, or DaVinci Resolve.
  3. `sources.txt`: Formatted citation and verification summary ready to paste into your YouTube video description.

---

## 2. System Requirements & Prerequisites

1. **Operating System**: Windows 10 or Windows 11 (64-bit), minimum 8 GB RAM (16 GB recommended).
2. **Python**: Version **3.11** or newer (Python 3.11–3.13 recommended).
   - Download the official installer at: [python.org/downloads](https://www.python.org/downloads/)
   - *Important*: Ensure you check the box **"Add python.exe to PATH"** during setup.
3. **FFmpeg** (Required for audio concatenation, silence generation, and EBU R128 loudness normalization):
   - Open **PowerShell** or Command Prompt and install via Windows Package Manager:
     ```powershell
     winget install Gyan.FFmpeg
     ```
   - Verify the installation in a new terminal window:
     ```powershell
     ffmpeg -version
     ```
     *(The application includes automatic path scanning for WinGet packages, so manual PATH editing is not required).*
4. **Google Gemini API Key** (100% Free Tier):
   - Visit [Google AI Studio](https://aistudio.google.com/) and click **Get API key**.
   - Create a free API key and copy it.

---

## 3. Environment Configuration

1. **Setup `.env` File**:
   - Copy `.env.example` to `.env` in the project root (or let `start.bat` initialize it automatically):
     ```cmd
     copy .env.example .env
     ```
   - Open `.env` in any editor and enter your Gemini API key:
     ```env
     GEMINI_API_KEY=AIzaSy...your_gemini_api_key_here
     ```
2. **Configuration in `config.yaml`**:
   - `gemini.model`: AI model for scriptwriting (default: `gemini-flash-lite-latest` with automatic fallback to `gemini-3.5-flash-lite`).
   - `tts.voice`: Locked English male voice identifier (default: `en-US-ChristopherNeural`).
   - `tts.fallback_provider`: Offline TTS provider fallback (default: `kokoro`).
   - `pacing_presets`: Baseline speaking rates, pitch, and sentence pause configurations (`mystery`, `hype`, `calm`).
   - `audio_enhancements`: Toggles for vocal post-processing (`compression`, `male_eq`, `deesser`, `reverb`, `loudnorm`).

---

## 4. Quick Start

Simply **double-click `start.bat`** (or execute from PowerShell / Command Prompt):
```cmd
start.bat
```

The launcher will automatically:
1. Initialize a Python virtual environment (`venv`) if not already present.
2. Install all required dependencies from `requirements.txt`.
3. Validate that FFmpeg is accessible.
4. Auto-generate the `.env` configuration file if missing.
5. Launch the FastAPI server and open your default browser at:
   ```
   http://127.0.0.1:8000
   ```

---

## 5. User Workflow Guide

### Step 1: Project Management
- Click **+ New Project** on the left sidebar.
- Set a project title in the top navigation bar. The editor autosaves changes automatically every 1.5 seconds.
- Projects are stored independently in `projects/<project_id>/project.json`.

### Step 2: Script Drafting with Gemini AI
- **Outline Builder**: Input your chosen topic (e.g., *"Greenland sharks live 400 years"*) and target duration (60s–180s) to produce a structured draft with an attention-grabbing hook.
- **Rewrite Draft**: Polish conversational rhythm, tighten word choice, and heighten suspense while safeguarding factual integrity.
- **Suggest Next Paragraphs**: Receive 3 dynamic follow-up paragraph alternatives to extend your narrative smoothly.

### Step 3: Storytelling Pacing & Audition
- Use the **Quick Pacing Toolbar** or click **"⚡ Auto-Pace"** to let AI analyze script semantics and insert expressive pacing markup:
  - `[fast]content[/fast]`: Accelerated rate (+12%) for opening hooks and fast-paced sequences.
  - `[slow]content[/slow]`: Decelerated rate (-15%) for mystery build-up and tension.
  - `[pause 0.5]`: Exact silence duration in seconds before critical reveals.
  - `*word*`: Vocal emphasis with higher pitch and subtle pre-pause.
  - `[whisper]content[/whisper]`: Intimate whispered delivery (-30% volume, -4Hz pitch).
  - `[deep]content[/deep]`, `[shock]content[/shock]`, `[urgent]content[/urgent]`, `[solemn]content[/solemn]`, `[loud]content[/loud]`: Extended emotional styles.
- Click **"🔊 Preview"** on the in-editor audition bar to listen to either the current paragraph or the full script with active audio FX and pacing.

### Step 4: Fact-Checking & Safe Rewriting
- Open the right sidebar and click **"🔍 Verify Claims"**.
- The AI isolates checkable atomic statements and classifies them:
  - **PROVEN (Green Badge)**: Accompanied by evidence summaries and citations.
  - **UNCLEAR (Yellow Badge)**: Unsubstantiated claims. Click **"🛡️ Safe Rewrite"** to rephrase into cautious, scientifically accurate statements.
- Add custom reference URLs or manually toggle claim statuses as needed.

### Step 5: Exporting Narration, Subtitles & Sources
- Click **"📦 Export Audio & Subtitles"**.
- Review the narration via the pre-export audition player.
- The pipeline executes:
  1. Segmented TTS audio synthesis, silence insertion, and EBU R128 normalization.
  2. Subtitle transcription via `faster-whisper` (5–8 words per phrase in `.srt`).
  3. Generation of `sources.txt` containing verified citations.
- Download the generated files individually or click **"📂 Open Project Folder"** to import assets directly into your video editing software.

---

## 6. Offline TTS Fallback (Kokoro ONNX)

To enable zero-network offline narration fallback:
1. Obtain the Kokoro ONNX model weights and voice configuration:
   - Weights: `kokoro-v0_19.onnx` (~300MB)
   - Voice mappings: `voices.json`
2. Place both files in the `assets/kokoro/` directory:
   ```
   assets/
     kokoro/
       kokoro-v0_19.onnx
       voices.json
   ```
3. Whenever network connectivity drops or the primary cloud TTS endpoint is unreachable, narration generation automatically switches to Kokoro TTS without breaking the pipeline.

---

## 7. Troubleshooting

- **Error: 'python' is not recognized as an internal or external command**:
  - Reinstall Python from [python.org](https://www.python.org/downloads/) and ensure you check **"Add python.exe to PATH"**.
- **Status Indicator: "⚠️ Missing FFmpeg"**:
  - Run `winget install Gyan.FFmpeg` in PowerShell and restart `start.bat`.
- **Status Indicator: "⚠️ Missing GEMINI_API_KEY"**:
  - Verify that your `.env` file contains `GEMINI_API_KEY=AIzaSy...` without quotes or trailing spaces.
- **Rate Limit 429 / Quota Exhaustion**:
  - Exponential backoff retries are built-in. If the quota is temporarily depleted, pause for 30–60 seconds to allow the free quota window to replenish.
- **Run Full Automated Test Suite**:
  - Execute all unit and integration tests from PowerShell:
    ```powershell
    .\venv\Scripts\python.exe -m unittest discover tests
    ```
