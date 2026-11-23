import asyncio
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from captions import (
    WordTiming,
    build_ass_events,
    chunk_words,
    format_ass_time,
    get_ass_header,
    transcribe_and_build_ass,
)
from tts import synthesize_narration

class TestCaptionsModule(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path(__file__).resolve().parent / "tmp_captions_test"
        self.test_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_format_ass_time(self):
        self.assertEqual(format_ass_time(0.0), "0:00:00.00")
        self.assertEqual(format_ass_time(1.5), "0:00:01.50")
        self.assertEqual(format_ass_time(65.25), "0:01:05.25")
        self.assertEqual(format_ass_time(3661.12), "1:01:01.12")

    def test_ass_header_geometry(self):
        header = get_ass_header(1080, 1920)
        self.assertIn("PlayResX: 1080", header)
        self.assertIn("PlayResY: 1920", header)
        self.assertIn("Arial Black", header)
        self.assertIn("[Events]", header)

    def test_chunk_words_grouping(self):
        words = [
            WordTiming(word="Greenland", start=0.0, end=0.4),
            WordTiming(word="sharks", start=0.4, end=0.8),
            WordTiming(word="live", start=0.8, end=1.1),
            WordTiming(word="longer", start=1.1, end=1.5),
            WordTiming(word="than", start=1.5, end=1.7),
            WordTiming(word="trees.", start=1.7, end=2.1),
        ]
        chunks = chunk_words(words, min_words=2, max_words=4)
        # Should split into 2 chunks because max_words=4
        self.assertEqual(len(chunks), 2)
        self.assertEqual(len(chunks[0].words), 4)
        self.assertEqual(len(chunks[1].words), 2)
        self.assertAlmostEqual(chunks[0].start, 0.0)
        self.assertAlmostEqual(chunks[0].end, 1.5)

    def test_ass_event_highlighting(self):
        words = [
            WordTiming(word="Mind", start=0.0, end=0.3),
            WordTiming(word="blowing", start=0.3, end=0.7),
        ]
        chunks = chunk_words(words)
        events = build_ass_events(chunks)

        lines = events.strip().split("\n")
        self.assertEqual(len(lines), 2)
        # First line highlights MIND
        self.assertIn(r"{\c&H0000FFFF&}MIND{\c&H00FFFFFF&} BLOWING", lines[0])
        # Second line highlights BLOWING
        self.assertIn(r"MIND {\c&H0000FFFF&}BLOWING{\c&H00FFFFFF&}", lines[1])

    def test_transcribe_and_build_ass(self):
        # 1. Synthesize a short speech clip
        audio_file = self.test_dir / "sample_speech.mp3"
        asyncio.run(synthesize_narration(
            script="Greenland sharks live for centuries in the deep arctic ocean.",
            output_path=audio_file,
            preset_name="hype"
        ))
        self.assertTrue(audio_file.exists())

        # 2. Transcribe and build ASS subtitles
        ass_file = self.test_dir / "sample.ass"
        out_ass = transcribe_and_build_ass(audio_file, ass_file, model_size="tiny.en")

        self.assertTrue(out_ass.exists())
        content = out_ass.read_text(encoding="utf-8")
        self.assertIn("[Script Info]", content)
        self.assertIn("PlayResX: 1080", content)
        self.assertIn("Dialogue:", content)
        self.assertIn(r"{\c&H0000FFFF&}", content)
        print("Caption transcription test passed: generated .ass subtitles with active highlights.")

if __name__ == "__main__":
    unittest.main()
