import sys
from pathlib import Path
import unittest

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.pacing_service import (
    parse_script,
    SpeechSegment,
    PauseSegment,
    format_rate,
    format_pitch
)

class TestPacingParser(unittest.TestCase):

    def test_empty_script(self):
        self.assertEqual(parse_script(""), [])
        self.assertEqual(parse_script("   \n\t  "), [])

    def test_pause_tag(self):
        script = "First sentence. [pause 1.5] Second sentence."
        segments = parse_script(script, auto_sentence_pauses=False)
        self.assertEqual(len(segments), 3)
        self.assertIsInstance(segments[0], SpeechSegment)
        self.assertEqual(segments[0].text, "First sentence.")
        self.assertIsInstance(segments[1], PauseSegment)
        self.assertAlmostEqual(segments[1].duration, 1.5)
        self.assertIsInstance(segments[2], SpeechSegment)
        self.assertEqual(segments[2].text, "Second sentence.")

    def test_slow_tag(self):
        script = "Normal text [slow]creeping slowly in the dark[/slow] back to normal."
        segments = parse_script(script, preset_name="mystery", auto_sentence_pauses=False)
        slow_seg = [s for s in segments if isinstance(s, SpeechSegment) and "creeping" in s.text][0]
        # Baseline mystery is -5%, slow is -15% => -20%
        self.assertEqual(slow_seg.rate, "-20%")
        self.assertEqual(slow_seg.text, "creeping slowly in the dark")

    def test_fast_tag(self):
        script = "Listen up! [fast]Here comes the rapid hook[/fast] and we slow down."
        segments = parse_script(script, preset_name="mystery", auto_sentence_pauses=False)
        fast_seg = [s for s in segments if isinstance(s, SpeechSegment) and "rapid hook" in s.text][0]
        # Baseline mystery is -5%, fast is +12% => +7%
        self.assertEqual(fast_seg.rate, "+7%")
        self.assertEqual(fast_seg.text, "Here comes the rapid hook")

    def test_emphasis_tag(self):
        script = "This is *absolutely mind-blowing* fact."
        segments = parse_script(script, preset_name="mystery", auto_sentence_pauses=False)
        # Check that tiny pause was inserted before emphasis
        emphasis_idx = next(i for i, s in enumerate(segments) if getattr(s, "is_emphasis", False))
        self.assertGreater(emphasis_idx, 0)
        self.assertIsInstance(segments[emphasis_idx - 1], PauseSegment)
        self.assertAlmostEqual(segments[emphasis_idx - 1].duration, 0.15)

        emp_seg = segments[emphasis_idx]
        self.assertEqual(emp_seg.text, "absolutely mind-blowing")
        self.assertEqual(emp_seg.volume, "+15%")
        self.assertTrue(emp_seg.is_emphasis)

    def test_whisper_tag(self):
        script = "Listen closely. [whisper]Nobody was ever supposed to know[/whisper] the truth."
        segments = parse_script(script, preset_name="mystery", auto_sentence_pauses=False)
        whisper_seg = [s for s in segments if getattr(s, "is_whisper", False)][0]
        self.assertEqual(whisper_seg.text, "Nobody was ever supposed to know")
        self.assertEqual(whisper_seg.volume, "-30%")
        self.assertTrue(whisper_seg.is_whisper)
        # Mystery baseline 0Hz - 4Hz = -4Hz
        self.assertEqual(whisper_seg.pitch, "-4Hz")

    def test_presets_difference(self):
        text = "Hello world"
        mystery_segs = parse_script(text, preset_name="mystery", auto_sentence_pauses=False)
        hype_segs = parse_script(text, preset_name="hype", auto_sentence_pauses=False)
        calm_segs = parse_script(text, preset_name="calm", auto_sentence_pauses=False)

        self.assertEqual(mystery_segs[0].rate, "-5%")
        self.assertEqual(hype_segs[0].rate, "+10%")
        self.assertEqual(hype_segs[0].pitch, "+2Hz")
        self.assertEqual(calm_segs[0].rate, "-10%")
        self.assertEqual(calm_segs[0].pitch, "-2Hz")

    def test_compound_script(self):
        script = (
            "[fast]Greenland sharks live longer than most trees.[/fast] "
            "[pause 0.8] "
            "Scientists made a *shocking* discovery. "
            "[whisper]They do not reach maturity until age one hundred and fifty.[/whisper]"
        )
        segments = parse_script(script)
        self.assertGreater(len(segments), 4)

        # Check types
        has_speech = any(isinstance(s, SpeechSegment) for s in segments)
        has_pause = any(isinstance(s, PauseSegment) for s in segments)
        self.assertTrue(has_speech)
        self.assertTrue(has_pause)

    def test_coalesced_sentence_paragraph_default(self):
        # By default (R2.6), sentences without tags remain coalesced into 1 speech segment
        script = "Greenland sharks live in near-freezing waters. They grow less than one centimeter per year."
        segments = parse_script(script)
        self.assertEqual(len(segments), 1)
        self.assertIsInstance(segments[0], SpeechSegment)
        self.assertIn("waters. They grow", segments[0].text)

    def test_split_only_on_tags_or_pause(self):
        script = "Sentence one. [pause 0.5] Sentence two and three. [slow]Sentence four.[/slow]"
        segments = parse_script(script)
        # Expected:
        # 1. "Sentence one."
        # 2. Pause(0.5)
        # 3. "Sentence two and three."
        # 4. "Sentence four." (slow)
        self.assertEqual(len(segments), 4)
        self.assertEqual(segments[0].text, "Sentence one.")
        self.assertIsInstance(segments[1], PauseSegment)
        self.assertEqual(segments[2].text, "Sentence two and three.")
        self.assertEqual(segments[3].text, "Sentence four.")

    def test_deep_tag(self):
        script = "Surface level. [deep]Down in the abyssal midnight zone[/deep] light never penetrates."
        segments = parse_script(script, preset_name="mystery", auto_sentence_pauses=False)
        deep_seg = [s for s in segments if isinstance(s, SpeechSegment) and "abyssal" in s.text][0]
        # Baseline mystery: rate -5%, pitch 0Hz. Deep: rate -8% (-13%), pitch -6Hz (-6Hz), vol +10%
        self.assertEqual(deep_seg.rate, "-13%")
        self.assertEqual(deep_seg.pitch, "-6Hz")
        self.assertEqual(deep_seg.volume, "+10%")
        self.assertEqual(deep_seg.text, "Down in the abyssal midnight zone")

    def test_shock_tag(self):
        script = "They checked the data again. [shock]It was born during the Renaissance![/shock] Absolutely wild."
        segments = parse_script(script, preset_name="mystery", auto_sentence_pauses=False)
        shock_seg = [s for s in segments if isinstance(s, SpeechSegment) and "Renaissance" in s.text][0]
        # Baseline mystery: rate -5%, pitch 0Hz. Shock: rate +15% (+10%), pitch +6Hz (+6Hz), vol +15%
        self.assertEqual(shock_seg.rate, "+10%")
        self.assertEqual(shock_seg.pitch, "+6Hz")
        self.assertEqual(shock_seg.volume, "+15%")
        self.assertEqual(shock_seg.text, "It was born during the Renaissance!")

    def test_urgent_tag(self):
        script = "Stand by. [urgent]The ice is collapsing fast around them[/urgent] and there is no escape."
        segments = parse_script(script, preset_name="mystery", auto_sentence_pauses=False)
        urgent_seg = [s for s in segments if isinstance(s, SpeechSegment) and "collapsing" in s.text][0]
        # Baseline mystery: rate -5%, pitch 0Hz. Urgent: rate +22% (+17%), pitch +1Hz (+1Hz), vol +10%
        self.assertEqual(urgent_seg.rate, "+17%")
        self.assertEqual(urgent_seg.pitch, "+1Hz")
        self.assertEqual(urgent_seg.volume, "+10%")
        self.assertEqual(urgent_seg.text, "The ice is collapsing fast around them")

    def test_solemn_tag(self):
        script = "The story ends here. [solemn]A living relic surviving across human centuries.[/solemn]"
        segments = parse_script(script, preset_name="mystery", auto_sentence_pauses=False)
        solemn_seg = [s for s in segments if isinstance(s, SpeechSegment) and "living relic" in s.text][0]
        # Baseline mystery: rate -5%, pitch 0Hz. Solemn: rate -20% (-25%), pitch -3Hz (-3Hz), vol +0%
        self.assertEqual(solemn_seg.rate, "-25%")
        self.assertEqual(solemn_seg.pitch, "-3Hz")
        self.assertEqual(solemn_seg.volume, "+0%")
        self.assertEqual(solemn_seg.text, "A living relic surviving across human centuries.")

    def test_loud_tag(self):
        script = "Quiet murmur. [loud]Wake up and listen to this number![/loud] Back to quiet."
        segments = parse_script(script, preset_name="mystery", auto_sentence_pauses=False)
        loud_seg = [s for s in segments if isinstance(s, SpeechSegment) and "Wake up" in s.text][0]
        # Baseline mystery: rate -5%, pitch 0Hz. Loud: rate -5%, pitch +2Hz, vol +30%
        self.assertEqual(loud_seg.rate, "-5%")
        self.assertEqual(loud_seg.pitch, "+2Hz")
        self.assertEqual(loud_seg.volume, "+30%")
        self.assertEqual(loud_seg.text, "Wake up and listen to this number!")

    def test_all_ten_tags_parsed_correctly(self):
        script = (
            "[fast]Fast hook[/fast] "
            "[slow]Slow buildup[/slow] "
            "[pause 0.5] "
            "*Key emphasis* "
            "[whisper]Whispered secret[/whisper] "
            "[deep]Deep ocean fact[/deep] "
            "[shock]Astonishing reveal[/shock] "
            "[urgent]Fast ticking clock[/urgent] "
            "[solemn]Ancient ending[/solemn] "
            "[loud]Final warning[/loud]"
        )
        segments = parse_script(script, auto_sentence_pauses=False)
        self.assertGreater(len(segments), 9)
        # Verify text of every tag was captured
        all_texts = " ".join(s.text for s in segments if isinstance(s, SpeechSegment))
        self.assertIn("Fast hook", all_texts)
        self.assertIn("Slow buildup", all_texts)
        self.assertIn("Key emphasis", all_texts)
        self.assertIn("Whispered secret", all_texts)
        self.assertIn("Deep ocean fact", all_texts)
        self.assertIn("Astonishing reveal", all_texts)
        self.assertIn("Fast ticking clock", all_texts)
        self.assertIn("Ancient ending", all_texts)
        self.assertIn("Final warning", all_texts)

if __name__ == "__main__":
    unittest.main()
