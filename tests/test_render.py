import asyncio
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from captions import transcribe_and_build_ass
from render import (
    detect_video_encoder,
    escape_filter_path,
    get_media_duration,
    render_video_with_placeholder,
)
from tts import synthesize_narration

class TestRenderEngine(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path(__file__).resolve().parent / "tmp_render_test"
        self.test_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_encoder_detection(self):
        encoder_name, args = detect_video_encoder()
        self.assertIn(encoder_name, ["h264_nvenc", "libx264"])
        self.assertGreater(len(args), 0)
        print(f"Detected video encoder: {encoder_name} with args {args}")

    def test_escape_filter_path(self):
        p = Path("D:/Content_English/projects/p1/sub.ass")
        escaped = escape_filter_path(p)
        self.assertIn(r"\:", escaped)
        self.assertNotIn("\\", escaped.replace(r"\:", ""))

    def test_render_placeholder_video_with_subtitles(self):
        # 1. Synthesize audio
        audio_file = self.test_dir / "test_audio.mp3"
        asyncio.run(synthesize_narration(
            script="Greenland sharks live longer than most trees.",
            output_path=audio_file,
            preset_name="hype"
        ))
        self.assertTrue(audio_file.exists())

        # 2. Build .ass captions
        ass_file = self.test_dir / "test_subs.ass"
        transcribe_and_build_ass(audio_file, ass_file, model_size="tiny.en")
        self.assertTrue(ass_file.exists())

        # 3. Render MP4
        output_mp4 = self.test_dir / "output.mp4"
        render_video_with_placeholder(
            audio_path=audio_file,
            output_mp4=output_mp4,
            ass_path=ass_file,
            width=1080,
            height=1920,
            fps=30
        )

        self.assertTrue(output_mp4.exists())
        self.assertGreater(output_mp4.stat().st_size, 10000)

        # 4. Check video resolution and duration via ffprobe
        probe_cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height,r_frame_rate",
            "-of", "csv=s=x:p=0",
            str(output_mp4)
        ]
        res = subprocess.run(probe_cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        out_dims = res.stdout.strip()
        self.assertIn("1080x1920", out_dims)

        duration = get_media_duration(output_mp4)
        self.assertGreater(duration, 2.0)
        print(f"Video render passed: {out_dims}, duration: {duration:.2f}s, size: {output_mp4.stat().st_size} bytes")

if __name__ == "__main__":
    unittest.main()
