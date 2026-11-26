import asyncio
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from infrastructure.whisper_adapter import (
    WordTiming,
    build_srt_content,
    chunk_words_for_srt,
    format_srt_time,
    transcribe_to_srt,
)
from services.tts_service import synthesize_narration

class TestCaptionsSRT(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path(__file__).resolve().parent / "tmp_captions_srt_test"
        self.test_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_format_srt_time(self):
        self.assertEqual(format_srt_time(0.0), "00:00:00,000")
        self.assertEqual(format_srt_time(1.5), "00:00:01,500")
        self.assertEqual(format_srt_time(65.25), "00:01:05,250")
        self.assertEqual(format_srt_time(3661.123), "01:01:01,123")

    def test_chunk_words_for_srt_5_to_8_words(self):
        # 14 words
        words = [
            WordTiming(word=f"word{i}", start=i * 0.3, end=(i + 1) * 0.3)
            for i in range(14)
        ]
        chunks = chunk_words_for_srt(words, min_words=5, max_words=8)
        self.assertEqual(len(chunks), 2)
        # First chunk should have 8 words, second chunk 6 words (both in 5-8 range)
        self.assertEqual(len(chunks[0].words), 8)
        self.assertEqual(len(chunks[1].words), 6)
        self.assertAlmostEqual(chunks[0].start, 0.0)
        self.assertAlmostEqual(chunks[0].end, 2.4)

    def test_build_srt_content(self):
        words = [
            WordTiming(word="Greenland", start=0.0, end=0.4),
            WordTiming(word="sharks", start=0.4, end=0.8),
            WordTiming(word="live", start=0.8, end=1.1),
            WordTiming(word="longer", start=1.1, end=1.5),
            WordTiming(word="than", start=1.5, end=1.8),
            WordTiming(word="trees.", start=1.8, end=2.2),
        ]
        chunks = chunk_words_for_srt(words, min_words=5, max_words=8)
        srt_text = build_srt_content(chunks)

        self.assertIn("1\n00:00:00,000 --> 00:00:02,200\nGreenland sharks live longer than trees.", srt_text)

    def test_transcribe_to_srt(self):
        # 1. Synthesize audio
        audio_file = self.test_dir / "sample_speech.mp3"
        asyncio.run(synthesize_narration(
            script="Greenland sharks live longer than most trees in the world.",
            output_path=audio_file,
            preset_name="hype"
        ))
        self.assertTrue(audio_file.exists())

        # 2. Transcribe to .srt
        srt_file = self.test_dir / "subtitles.srt"
        out_path = transcribe_to_srt(audio_file, srt_file, model_size="tiny.en")

        self.assertTrue(out_path.exists())
        content = out_path.read_text(encoding="utf-8")
        self.assertIn("1\n00:00:", content)
        self.assertIn("-->", content)
        print("SRT transcription test passed. Generated SRT content:\n" + content[:200])

if __name__ == "__main__":
    unittest.main()
