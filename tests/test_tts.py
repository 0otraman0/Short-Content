import asyncio
from pathlib import Path
import sys
import unittest
from unittest.mock import AsyncMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from infrastructure.tts_providers import (
    ChatterboxTTSProvider,
    EdgeTTSProvider,
    KokoroTTSProvider,
    get_locked_voice,
    get_tts_provider,
    lock_voice,
)
from infrastructure.ffmpeg_processor import (
    build_audio_filter_chain,
    generate_silence,
    get_audio_duration,
    get_audio_enhancements,
)
from services.tts_service import synthesize_narration

class TestTTSEngine(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path(__file__).resolve().parent / "tmp_tts_test"
        self.test_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_voice_config(self):
        voice = get_locked_voice()
        self.assertIsInstance(voice, str)
        self.assertTrue(len(voice) > 0)

    def test_list_english_male_voices(self):
        provider = EdgeTTSProvider()
        voices = asyncio.run(provider.list_english_male_voices())
        self.assertIsInstance(voices, list)
        self.assertGreater(len(voices), 0)
        # Verify voice structure
        first = voices[0]
        self.assertIn("id", first)
        self.assertIn("name", first)
        self.assertTrue(first["locale"].startswith("en-"))
        self.assertEqual(first["gender"], "Male")

    def test_kokoro_provider_and_voices(self):
        provider = KokoroTTSProvider()
        voices = asyncio.run(provider.list_english_male_voices())
        self.assertIsInstance(voices, list)
        self.assertGreaterEqual(len(voices), 5)
        voice_ids = [v["id"] for v in voices]
        self.assertIn("am_adam", voice_ids)
        self.assertIn("bm_daniel", voice_ids)
        for v in voices:
            self.assertEqual(v["gender"], "Male")
            self.assertTrue(v["locale"].startswith("en-"))

    def test_kokoro_missing_model_handling(self):
        # Point to non-existent model files
        provider = KokoroTTSProvider(
            model_path=Path("non_existent_model.onnx"),
            voices_path=Path("non_existent_voices.json"),
        )
        self.assertFalse(provider.is_available())
        with self.assertRaises(FileNotFoundError):
            asyncio.run(provider.synthesize_segment(
                text="Test text",
                output_file=self.test_dir / "out.mp3",
                voice="am_adam",
            ))

    def test_provider_factory(self):
        p_edge = get_tts_provider("edge-tts")
        self.assertIsInstance(p_edge, EdgeTTSProvider)
        p_kokoro = get_tts_provider("kokoro")
        self.assertIsInstance(p_kokoro, KokoroTTSProvider)
        p_cb = get_tts_provider("chatterbox")
        self.assertIsInstance(p_cb, ChatterboxTTSProvider)

    def test_fallback_to_kokoro_on_network_error(self):
        output_file = self.test_dir / "fallback_narration.mp3"
        script = "Fallback test sentence."

        async def mock_kokoro_synth(text, output_file, voice, rate="+0%", pitch="+0Hz", volume="+0%"):
            import subprocess
            cmd = [
                "ffmpeg", "-y",
                "-f", "lavfi",
                "-i", "sine=frequency=440:duration=1.0",
                "-c:a", "libmp3lame",
                "-b:a", "192k",
                str(output_file),
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            return Path(output_file)

        # Mock EdgeTTS to fail with network error and Kokoro to be available
        with patch.object(EdgeTTSProvider, "synthesize_segment", side_effect=ConnectionError("Network disconnected")):
            with patch.object(KokoroTTSProvider, "is_available", return_value=True):
                with patch.object(KokoroTTSProvider, "synthesize_segment", side_effect=mock_kokoro_synth):
                    out_path, duration = asyncio.run(synthesize_narration(
                        script=script,
                        output_path=output_file,
                        preset_name="mystery",
                        allow_fallback=True,
                    ))
                    self.assertTrue(out_path.exists())
                    self.assertGreater(out_path.stat().st_size, 0)
                    self.assertGreater(duration, 0.5)

    def test_silence_generation_and_duration(self):
        silence_file = self.test_dir / "test_silence.mp3"
        generate_silence(0.5, silence_file)
        self.assertTrue(silence_file.exists())
        self.assertGreater(silence_file.stat().st_size, 0)

        duration = get_audio_duration(silence_file)
        self.assertAlmostEqual(duration, 0.5, delta=0.1)

    def test_full_narration_synthesis(self):
        script = "[fast]Greenland sharks.[/fast] [pause 0.5] *Living for centuries.*"
        output_file = self.test_dir / "narration_test.mp3"

        out_path, duration = asyncio.run(synthesize_narration(
            script=script,
            output_path=output_file,
            preset_name="mystery"
        ))

        self.assertTrue(out_path.exists())
        self.assertGreater(out_path.stat().st_size, 1000)
        self.assertGreater(duration, 1.0)
        print(f"TTS synthesis passed: generated {duration:.2f}s audio at {out_path.name}")

    def test_audio_filter_chain_builder(self):
        # All enabled
        chain_all = build_audio_filter_chain({
            "compression": True,
            "male_eq": True,
            "deesser": True,
            "reverb": True,
            "loudnorm": True,
        })
        self.assertIn("acompressor", chain_all)
        self.assertIn("equalizer", chain_all)
        self.assertIn("highpass", chain_all)
        self.assertIn("deesser", chain_all)
        self.assertIn("aecho", chain_all)
        self.assertIn("loudnorm", chain_all)

        # All disabled
        chain_none = build_audio_filter_chain({
            "compression": False,
            "male_eq": False,
            "deesser": False,
            "reverb": False,
            "loudnorm": False,
        })
        self.assertEqual(chain_none, "anull")

        # Selective toggles
        chain_eq_only = build_audio_filter_chain({
            "compression": False,
            "male_eq": True,
            "deesser": False,
            "reverb": False,
            "loudnorm": False,
        })
        self.assertIn("equalizer", chain_eq_only)
        self.assertNotIn("acompressor", chain_eq_only)
        self.assertNotIn("loudnorm", chain_eq_only)

    def test_get_audio_enhancements(self):
        enh = get_audio_enhancements()
        self.assertIsInstance(enh, dict)
        self.assertIn("compression", enh)
        self.assertIn("male_eq", enh)
        self.assertIn("deesser", enh)
        self.assertIn("reverb", enh)
        self.assertIn("loudnorm", enh)
        self.assertTrue(enh["loudnorm"])

if __name__ == "__main__":
    unittest.main()
