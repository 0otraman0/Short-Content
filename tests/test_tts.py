import asyncio
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tts import (
    EdgeTTSProvider,
    generate_silence,
    get_audio_duration,
    get_locked_voice,
    lock_voice,
    synthesize_narration,
)

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

if __name__ == "__main__":
    unittest.main()
