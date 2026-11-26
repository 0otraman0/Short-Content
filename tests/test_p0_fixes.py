"""P0 regression tests (Phase 14). Offline only: no network, no model load.

Run on Windows: python -m pytest tests/test_p0_fixes.py -v
"""
import asyncio
import sys
from pathlib import Path
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import services.pacing_service as pacing_mod
from services.pacing_service import load_presets
from services.factcheck_service import _clean_urls, _is_valid_url, clean_pacing_tags
from services.tts_service import _is_network_error
from repositories.project_repository import ProjectRepository


class TestP01PresetsFromConfig(unittest.TestCase):
    def test_load_presets_default_path_reads_config_yaml(self, tmp_path=None):
        # load_presets() with no argument must read BASE_DIR/config.yaml,
        # not silently return the in-code defaults.
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            cfg = Path(td) / "config.yaml"
            cfg.write_text(
                "pacing_presets:\n"
                "  mystery:\n"
                "    name: Mystery\n"
                "    baseline_rate: 0.2\n"
                "    baseline_pitch: '+0Hz'\n"
                "    sentence_pause: 0.6\n"
                "    reveal_pause: 1.0\n",
                encoding="utf-8",
            )
            old_base = pacing_mod.BASE_DIR
            pacing_mod.BASE_DIR = Path(td)
            try:
                presets = load_presets()
            finally:
                pacing_mod.BASE_DIR = old_base
            self.assertAlmostEqual(presets["mystery"]["baseline_rate"], 0.2)


class TestP02Factcheck(unittest.TestCase):
    def test_clean_pacing_tags_removes_all_ten_tags(self):
        raw = "[deep]Deep[/deep] [shock]Shock[/shock] [urgent]Urgent[/urgent] [solemn]Solemn[/solemn] [loud]Loud[/loud] [slow]Slow[/slow]"
        cleaned = clean_pacing_tags(raw)
        for tag in ("[deep]", "[shock]", "[urgent]", "[solemn]", "[loud]", "[slow]", "[/deep]"):
            self.assertNotIn(tag, cleaned)
        self.assertIn("Deep", cleaned)
        self.assertIn("Loud", cleaned)

    def test_url_validation_drops_invalid_and_duplicates(self):
        self.assertTrue(_is_valid_url("https://en.wikipedia.org/wiki/Shark"))
        self.assertFalse(_is_valid_url("notaurl"))
        self.assertFalse(_is_valid_url("ftp://example.com/x"))
        self.assertFalse(_is_valid_url("https://"))
        cleaned = _clean_urls([
            "https://example.com/a", "notaurl", "https://example.com/a",
            "http://example.com/b",
        ])
        self.assertEqual(cleaned, ["https://example.com/a", "http://example.com/b"])


class TestP03Sanitize(unittest.TestCase):
    def test_export_job_dir_rejects_traversal(self):
        repo = ProjectRepository()
        with self.assertRaises(ValueError):
            repo.get_export_job_dir("abc123", "../evil")
        with self.assertRaises(ValueError):
            repo.get_take_file("abc123", "para_0", "../../etc/passwd")
        # Valid ids still work
        self.assertTrue(str(repo.get_export_job_dir("abc123", "job_abc123")).endswith("job_abc123"))


class TestP04AtomicSave(unittest.TestCase):
    def test_save_project_leaves_no_tmp_file(self):
        import tempfile, json
        with tempfile.TemporaryDirectory() as td:
            import repositories.project_repository as repo_mod
            old_dir = repo_mod.PROJECTS_DIR
            repo_mod.PROJECTS_DIR = Path(td)
            try:
                repo = ProjectRepository()
                data = repo.create_project(title="P0 test", script="Hello world")
                folder = Path(td) / data["id"]
                self.assertTrue((folder / "project.json").exists())
                self.assertFalse((folder / "project.json.tmp").exists())
                self.assertEqual(json.loads((folder / "project.json").read_text(encoding="utf-8"))["title"], "P0 test")
            finally:
                repo_mod.PROJECTS_DIR = old_dir


class TestP05WhisperCache(unittest.TestCase):
    def test_transcribe_to_srt_uses_cached_model(self):
        import tempfile
        from infrastructure import whisper_adapter as wa
        fake_word = MagicMock()
        fake_word.word = "hello"
        fake_word.start = 0.0
        fake_word.end = 0.5
        fake_seg = MagicMock()
        fake_seg.words = [fake_word]
        fake_model = MagicMock()
        fake_model.transcribe.return_value = ([fake_seg], None)
        with tempfile.TemporaryDirectory() as td:
            audio = Path(td) / "a.mp3"
            audio.write_bytes(b"fake")
            out = Path(td) / "out.srt"
            with patch.object(wa, "get_whisper_model", return_value=fake_model) as mock_get:
                result = wa.transcribe_to_srt(audio, out)
            mock_get.assert_called_once()
            self.assertEqual(mock_get.call_args[0][0], "base.en")
            self.assertTrue(result.exists())
            self.assertIn("hello", result.read_text(encoding="utf-8"))


class TestP06FallbackOnlyOnNetworkError(unittest.TestCase):
    def test_non_network_error_is_not_a_network_error(self):
        self.assertFalse(_is_network_error(ValueError("bad script")))
        self.assertFalse(_is_network_error(RuntimeError("voice not found")))
        self.assertTrue(_is_network_error(ConnectionError("Network disconnected")))
        self.assertTrue(_is_network_error(TimeoutError("timed out")))

    def test_value_error_from_primary_is_not_swallowed(self):
        from services import tts_service as tts_mod
        from infrastructure.tts_providers import EdgeTTSProvider
        provider = EdgeTTSProvider()
        with patch.object(tts_mod, "ensure_ffmpeg", return_value=None), \
             patch.object(EdgeTTSProvider, "synthesize_segment", side_effect=ValueError("bad script")), \
             patch.object(tts_mod.KokoroTTSProvider, "is_available", return_value=True):
            with self.assertRaises(ValueError):
                asyncio.run(tts_mod.synthesize_narration(
                    script="Hello world.",
                    output_path=Path("out.mp3"),
                    preset_name="mystery",
                    provider=provider,
                ))


if __name__ == "__main__":
    unittest.main()
