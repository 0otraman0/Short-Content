"""
export_service.py - Business Logic for end-to-end Export Pipeline.
Orchestrates: TTS narration → Whisper SRT → sources.txt → project.json update.
"""

import asyncio
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from infrastructure.ffmpeg_processor import ensure_ffmpeg, get_audio_enhancements
from infrastructure.tts_providers import get_locked_voice
from infrastructure.whisper_adapter import transcribe_to_srt
from repositories.project_repository import ProjectRepository
from services.tts_service import synthesize_narration_with_info


class ExportService:
    def __init__(self, repository: Optional[ProjectRepository] = None):
        self.repository = repository or ProjectRepository()

    async def execute_export(
        self,
        project_id: str,
        job_id: str,
        progress_callback: Optional[Callable[[int, str, Optional[float]], None]] = None,
    ) -> Dict[str, Any]:
        """
        Execute complete export for a project:
        1. TTS Narration synthesis (pacing + enhancements)
        2. Whisper SRT subtitle generation
        3. sources.txt from verified claims
        4. Update project.json with export entry
        Returns job metadata dict.
        """
        ensure_ffmpeg()

        folder = self.repository.get_folder(project_id)
        project_data = self.repository.get_project(project_id)
        if not project_data:
            raise ValueError(f"Không tìm thấy dự án {project_id}")

        script = project_data.get("script", "").strip()
        if not script:
            raise ValueError("Kịch bản đang trống. Vui lòng nhập nội dung kịch bản trước khi xuất.")

        preset = project_data.get("pacing_preset", "mystery")
        voice = get_locked_voice()

        job_dir = self.repository.get_export_job_dir(project_id, job_id)
        job_dir.mkdir(parents=True, exist_ok=True)

        # Step 1 (20%): TTS narration synthesis
        if progress_callback:
            progress_callback(20, "Đang tổng hợp giọng đọc (TTS)...", None)

        audio_file = job_dir / "narration.mp3"
        enhancements = project_data.get("audio_enhancements") or get_audio_enhancements()
        # P0-6: record whether the Kokoro fallback ran, so the UI/history
        # can warn that the voice changed and pacing nuance may differ.
        _, duration, fallback_used, used_provider = await synthesize_narration_with_info(
            script=script,
            output_path=audio_file,
            preset_name=preset,
            voice=voice,
            enhancements=enhancements,
        )

        # Step 2 (60%): Whisper SRT subtitle generation
        if progress_callback:
            progress_callback(60, "Đang tạo phụ đề SRT (faster-whisper)...", round(duration, 2))

        srt_file = job_dir / "subtitles.srt"
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, transcribe_to_srt, audio_file, srt_file)

        # Step 3 (90%): Write sources.txt
        if progress_callback:
            progress_callback(90, "Đang tạo sources.txt...", round(duration, 2))

        sources_file = job_dir / "sources.txt"
        claims = project_data.get("claims", [])
        if claims:
            lines = [
                "SOURCES & REFERENCES (YouTube Shorts Description):",
                "==================================================",
            ]
            for i, claim in enumerate(claims, 1):
                label = claim.get("label", "CHƯA RÕ")
                text_c = claim.get("text", "")
                urls = claim.get("urls", [])
                evidence = claim.get("evidence", "")
                status_mark = "Verified / Đã chứng minh" if "ĐÃ" in label else "Unverified / Chưa rõ"
                lines.append(f"\n{i}. {text_c}")
                lines.append(f"   Status: [{label}] ({status_mark})")
                if evidence:
                    lines.append(f"   Summary: {evidence}")
                if urls:
                    lines.append("   References:")
                    for url in urls:
                        lines.append(f"   - {url}")
                else:
                    lines.append("   References: (No source link provided)")
            lines.append("\n==================================================")
            lines.append("Produced with Shorts Narration Tool")
            sources_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        else:
            sources_file.write_text(
                "SOURCES & REFERENCES (YouTube Shorts Description):\n"
                "==================================================\n"
                "(No claims fact-checked yet. Use the Fact Check panel in the tool to verify and list references.)\n"
                "==================================================\n",
                encoding="utf-8",
            )

        # Step 4 (100%): Write job metadata and update project.json
        created_at_iso = datetime.now().isoformat()
        job_meta = {
            "id": job_id,
            "created_at": created_at_iso,
            "duration": round(duration, 2),
            "script": script,
            "script_preview": script[:120] + ("..." if len(script) > 120 else ""),
            "pacing_preset": preset,
            "voice": voice,
            "fallback_used": fallback_used,
            "used_provider": used_provider,
            "audio_file": "narration.mp3",
            "subtitles_file": "subtitles.srt",
            "sources_file": "sources.txt",
        }
        (job_dir / "metadata.json").write_text(json.dumps(job_meta, ensure_ascii=False, indent=2), encoding="utf-8")

        # Copy to root folder for backward compatibility
        shutil.copy2(audio_file, folder / "narration.mp3")
        shutil.copy2(srt_file, folder / "subtitles.srt")
        shutil.copy2(sources_file, folder / "sources.txt")

        # Build export_entry for history
        export_entry = {
            "id": job_id,
            "created_at": created_at_iso,
            "duration": round(duration, 2),
            "script_preview": job_meta["script_preview"],
            "pacing_preset": preset,
            "voice": voice,
            "fallback_used": fallback_used,
            "used_provider": used_provider,
            "audio_url": f"/api/projects/{project_id}/exports/{job_id}/audio",
            "subtitles_url": f"/api/projects/{project_id}/exports/{job_id}/subtitles",
            "sources_url": f"/api/projects/{project_id}/exports/{job_id}/sources",
        }

        # Update project.json
        project_data["status"] = "exported"
        project_data["audio_file"] = "narration.mp3"
        project_data["subtitles_file"] = "subtitles.srt"
        project_data["sources_file"] = "sources.txt"
        project_data["actual_duration"] = round(duration, 2)
        project_data["updated_at"] = created_at_iso
        exports = project_data.get("exports", [])
        exports.insert(0, export_entry)
        project_data["exports"] = exports
        self.repository.save_project(project_data)

        if progress_callback:
            progress_callback(100, "Hoàn tất! Gói xuất đã sẵn sàng.", round(duration, 2))

        job_meta["export_entry"] = export_entry
        return job_meta
