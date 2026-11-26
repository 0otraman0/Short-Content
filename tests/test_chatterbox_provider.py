"""Tests for the Chatterbox TTS provider (no network, no torch, no real model).

Run from the repo root, same as the other tests:
    python -m unittest discover -s tests -p "test_chatterbox_provider.py" -v
"""

import asyncio
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from infrastructure.tts_providers import (
    ChatterboxTTSProvider,
    EdgeTTSProvider,
    KokoroTTSProvider,
    get_tts_provider,
)


class FakeModel:
    sr = 24000

    def __init__(self):
        self.calls = []

    def generate(self, text, **kwargs):
        self.calls.append((text, kwargs))
        return np.sin(np.linspace(0, 100, 12000)).astype(np.float32)


class TestChatterboxProvider(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.out_dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_factory_returns_chatterbox(self):
        self.assertIsInstance(get_tts_provider("chatterbox"), ChatterboxTTSProvider)
        self.assertIsInstance(get_tts_provider("edge-tts"), EdgeTTSProvider)
        self.assertIsInstance(get_tts_provider("kokoro"), KokoroTTSProvider)

    def test_config_defaults_and_clamps(self):
        p = ChatterboxTTSProvider()
        self.assertEqual(p.exaggeration, 0.7)
        self.assertEqual(p.cfg_weight, 0.3)
        p = ChatterboxTTSProvider(exaggeration=5.0, cfg_weight=0.01)
        self.assertEqual(p.exaggeration, 2.0)
        self.assertEqual(p.cfg_weight, 0.2)

    def test_list_voices(self):
        voices = asyncio.run(ChatterboxTTSProvider().list_english_male_voices())
        self.assertEqual(len(voices), 1)
        self.assertEqual(voices[0]["id"], "chatterbox-default")

    def test_is_available_false_when_missing(self):
        with patch.dict(sys.modules, {"chatterbox": None}):
            self.assertFalse(ChatterboxTTSProvider().is_available())

    def test_missing_package_error_message(self):
        with patch.dict(sys.modules, {"chatterbox": None, "chatterbox.tts": None}):
            with self.assertRaises(RuntimeError) as ctx:
                ChatterboxTTSProvider()._get_model()
        self.assertIn("pip install", str(ctx.exception))

    def test_synthesize_with_fake_model(self):
        fake = FakeModel()
        provider = ChatterboxTTSProvider()
        cmds = []

        def fake_run(cmd, capture_output=False, text=False):
            cmds.append(cmd)
            Path(cmd[-1]).write_bytes(b"fake mp3 data")

            class Res:
                returncode = 0
                stderr = ""

            return Res()

        out = self.out_dir / "seg.mp3"
        with patch.object(provider, "_get_model", return_value=fake):
            with patch("infrastructure.tts_providers.subprocess.run", side_effect=fake_run):
                result = asyncio.run(provider.synthesize_segment(
                    text="Sharks are older than trees.",
                    output_file=out,
                    voice="en-US-ChristopherNeural",
                    rate="+10%",
                    pitch="+2Hz",
                    volume="+0%",
                ))
        self.assertEqual(result, out)
        self.assertTrue(out.exists())
        self.assertEqual(len(fake.calls), 1)
        text, kwargs = fake.calls[0]
        self.assertEqual(text, "Sharks are older than trees.")
        self.assertEqual(kwargs["exaggeration"], 0.7)
        self.assertEqual(kwargs["cfg_weight"], 0.3)
        self.assertNotIn("audio_prompt_path", kwargs)
        # rate +10% -> ffmpeg atempo 1.100
        self.assertTrue(any("atempo=1.100" in a for a in cmds[0]))

    def test_synthesize_applies_volume_and_ignores_pitch(self):
        fake = FakeModel()
        provider = ChatterboxTTSProvider()
        cmds = []

        def fake_run(cmd, capture_output=False, text=False):
            cmds.append(cmd)
            Path(cmd[-1]).write_bytes(b"fake mp3 data")

            class Res:
                returncode = 0
                stderr = ""

            return Res()

        out = self.out_dir / "seg.mp3"
        with patch.object(provider, "_get_model", return_value=fake):
            with patch("infrastructure.tts_providers.subprocess.run", side_effect=fake_run):
                asyncio.run(provider.synthesize_segment(
                    text="Quiet line.",
                    output_file=out,
                    rate="+0%",
                    pitch="-2Hz",
                    volume="-50%",
                ))
        # volume -50% -> volume filter 0.500; no atempo for +0% rate
        self.assertTrue(any("volume=0.500" in a for a in cmds[0]))
        self.assertFalse(any("atempo" in a for a in cmds[0]))

    def test_missing_audio_prompt_raises(self):
        provider = ChatterboxTTSProvider(audio_prompt_path=Path("nope_missing.wav"))
        with patch.object(provider, "_get_model", return_value=FakeModel()):
            with self.assertRaises(FileNotFoundError):
                asyncio.run(provider.synthesize_segment(
                    text="Hello.",
                    output_file=self.out_dir / "seg.mp3",
                ))


if __name__ == "__main__":
    unittest.main()
