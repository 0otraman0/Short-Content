"""
pacing.py - Script pacing markup parser and segment splitter.

Supported tags:
  [pause 0.5]            - Silence in seconds
  [slow]...[/slow]       - Slower narration rate (-15%)
  [fast]...[/fast]       - Faster narration rate (+12%)
  *word or phrase*       - Emphasis (louder, higher pitch, tiny pause before)
  [whisper]...[/whisper] - Lower pitch (-4Hz), lower volume (-30%), slightly slower (-10%)
  [deep]...[/deep]       - Deep bass voice for mysteries and chilling facts (-6Hz pitch, -8% rate, +10% vol)
  [shock]...[/shock]     - High dramatic revelation and disbelief (+6Hz pitch, +15% rate, +15% vol)
  [urgent]...[/urgent]   - Ticking clock, fast-paced intensity (+22% rate, +10% vol, +1Hz pitch)
  [solemn]...[/solemn]   - Slow reflective ending and ancient history (-20% rate, -3Hz pitch)
  [loud]...[/loud]       - Powerful wake-up attention grabber (+30% vol, +2Hz pitch)
"""

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Dict, List, Optional, Union
import yaml

@dataclass
class SpeechSegment:
    text: str
    rate: str = "+0%"
    pitch: str = "+0Hz"
    volume: str = "+0%"
    is_whisper: bool = False
    is_emphasis: bool = False

@dataclass
class PauseSegment:
    duration: float

Segment = Union[SpeechSegment, PauseSegment]

# Default Presets as specified in SPEC (R2.7)
DEFAULT_PRESETS = {
    "mystery": {
        "name": "Mystery",
        "baseline_rate": -0.05,
        "baseline_pitch": "+0Hz",
        "sentence_pause": 0.6,
        "reveal_pause": 1.0,
    },
    "hype": {
        "name": "Hype",
        "baseline_rate": 0.10,
        "baseline_pitch": "+2Hz",
        "sentence_pause": 0.3,
        "reveal_pause": 0.5,
    },
    "calm": {
        "name": "Calm",
        "baseline_rate": -0.10,
        "baseline_pitch": "-2Hz",
        "sentence_pause": 0.8,
        "reveal_pause": 0.8,
    },
}

def load_presets(config_path: Optional[Path] = None) -> Dict[str, dict]:
    """Load pacing presets from config.yaml or fallback to defaults."""
    if config_path and config_path.exists():
        try:
            cfg = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
            custom_presets = cfg.get("pacing_presets")
            if custom_presets and isinstance(custom_presets, dict):
                return custom_presets
        except Exception:
            pass
    return DEFAULT_PRESETS

def format_rate(rate_val: float) -> str:
    pct = round(rate_val * 100)
    return f"+{pct}%" if pct >= 0 else f"{pct}%"

def parse_pitch_hz(pitch_str: str) -> int:
    match = re.match(r"([+-]?\d+)\s*Hz", pitch_str, re.IGNORECASE)
    return int(match.group(1)) if match else 0

def format_pitch(pitch_hz: int) -> str:
    return f"+{pitch_hz}Hz" if pitch_hz >= 0 else f"{pitch_hz}Hz"

def parse_script(
    script: str,
    preset_name: str = "mystery",
    config_path: Optional[Path] = None,
    auto_sentence_pauses: bool = False
) -> List[Segment]:
    """
    Parse a script containing pacing markup into a list of SpeechSegment and PauseSegment items.
    By default (auto_sentence_pauses=False), text is kept coalesced at sentence/paragraph level
    and only splits where markup explicitly specifies a different rate/pitch or a pause (R2.6).
    """
    if not script or not script.strip():
        return []

    presets = load_presets(config_path)
    preset = presets.get(preset_name.lower(), DEFAULT_PRESETS["mystery"])

    baseline_rate = float(preset.get("baseline_rate", -0.05))
    baseline_pitch_hz = parse_pitch_hz(preset.get("baseline_pitch", "+0Hz"))
    sentence_pause = float(preset.get("sentence_pause", 0.6))

    # Token patterns
    # Matches: [pause X], [slow]...[/slow], [fast]...[/fast], [whisper]...[/whisper],
    #          [deep]...[/deep], [shock]...[/shock], [urgent]...[/urgent],
    #          [solemn]...[/solemn], [loud]...[/loud], *emphasis*
    token_pattern = re.compile(
        r"(\[pause\s+([0-9.]+)\])"
        r"|(\[slow\]([\s\S]*?)\[/slow\])"
        r"|(\[fast\]([\s\S]*?)\[/fast\])"
        r"|(\[whisper\]([\s\S]*?)\[/whisper\])"
        r"|(\[deep\]([\s\S]*?)\[/deep\])"
        r"|(\[shock\]([\s\S]*?)\[/shock\])"
        r"|(\[urgent\]([\s\S]*?)\[/urgent\])"
        r"|(\[solemn\]([\s\S]*?)\[/solemn\])"
        r"|(\[loud\]([\s\S]*?)\[/loud\])"
        r"|(\*([^*\n]+)\*)",
        re.IGNORECASE
    )

    raw_segments: List[Segment] = []
    last_idx = 0

    for match in token_pattern.finditer(script):
        start, end = match.span()

        # Text before the matched tag
        if start > last_idx:
            pre_text = script[last_idx:start]
            _append_plain_text(raw_segments, pre_text, baseline_rate, baseline_pitch_hz, sentence_pause, auto_sentence_pauses)

        # 1. [pause X]
        if match.group(1):
            pause_sec = float(match.group(2))
            raw_segments.append(PauseSegment(duration=max(0.0, pause_sec)))

        # 2. [slow]...[/slow]
        elif match.group(3):
            inner_text = match.group(4).strip()
            if inner_text:
                effective_rate = baseline_rate - 0.15
                raw_segments.append(SpeechSegment(
                    text=inner_text,
                    rate=format_rate(effective_rate),
                    pitch=format_pitch(baseline_pitch_hz),
                    volume="+0%"
                ))

        # 3. [fast]...[/fast]
        elif match.group(5):
            inner_text = match.group(6).strip()
            if inner_text:
                effective_rate = baseline_rate + 0.12
                raw_segments.append(SpeechSegment(
                    text=inner_text,
                    rate=format_rate(effective_rate),
                    pitch=format_pitch(baseline_pitch_hz),
                    volume="+0%"
                ))

        # 4. [whisper]...[/whisper]
        elif match.group(7):
            inner_text = match.group(8).strip()
            if inner_text:
                effective_rate = baseline_rate - 0.10
                effective_pitch = baseline_pitch_hz - 4
                raw_segments.append(SpeechSegment(
                    text=inner_text,
                    rate=format_rate(effective_rate),
                    pitch=format_pitch(effective_pitch),
                    volume="-30%",
                    is_whisper=True
                ))

        # 5. [deep]...[/deep]
        elif match.group(9):
            inner_text = match.group(10).strip()
            if inner_text:
                effective_rate = baseline_rate - 0.08
                effective_pitch = baseline_pitch_hz - 6
                raw_segments.append(SpeechSegment(
                    text=inner_text,
                    rate=format_rate(effective_rate),
                    pitch=format_pitch(effective_pitch),
                    volume="+10%"
                ))

        # 6. [shock]...[/shock]
        elif match.group(11):
            inner_text = match.group(12).strip()
            if inner_text:
                effective_rate = baseline_rate + 0.15
                effective_pitch = baseline_pitch_hz + 6
                raw_segments.append(SpeechSegment(
                    text=inner_text,
                    rate=format_rate(effective_rate),
                    pitch=format_pitch(effective_pitch),
                    volume="+15%"
                ))

        # 7. [urgent]...[/urgent]
        elif match.group(13):
            inner_text = match.group(14).strip()
            if inner_text:
                effective_rate = baseline_rate + 0.22
                effective_pitch = baseline_pitch_hz + 1
                raw_segments.append(SpeechSegment(
                    text=inner_text,
                    rate=format_rate(effective_rate),
                    pitch=format_pitch(effective_pitch),
                    volume="+10%"
                ))

        # 8. [solemn]...[/solemn]
        elif match.group(15):
            inner_text = match.group(16).strip()
            if inner_text:
                effective_rate = baseline_rate - 0.20
                effective_pitch = baseline_pitch_hz - 3
                raw_segments.append(SpeechSegment(
                    text=inner_text,
                    rate=format_rate(effective_rate),
                    pitch=format_pitch(effective_pitch),
                    volume="+0%"
                ))

        # 9. [loud]...[/loud]
        elif match.group(17):
            inner_text = match.group(18).strip()
            if inner_text:
                effective_rate = baseline_rate
                effective_pitch = baseline_pitch_hz + 2
                raw_segments.append(SpeechSegment(
                    text=inner_text,
                    rate=format_rate(effective_rate),
                    pitch=format_pitch(effective_pitch),
                    volume="+30%"
                ))

        # 10. *emphasis*
        elif match.group(19):
            inner_text = match.group(20).strip()
            if inner_text:
                # Insert tiny pause (0.15s) before emphasis if previous segment isn't already a pause
                if not raw_segments or not isinstance(raw_segments[-1], PauseSegment):
                    raw_segments.append(PauseSegment(duration=0.15))

                effective_rate = baseline_rate - 0.05
                effective_pitch = baseline_pitch_hz + 3
                raw_segments.append(SpeechSegment(
                    text=inner_text,
                    rate=format_rate(effective_rate),
                    pitch=format_pitch(effective_pitch),
                    volume="+15%",
                    is_emphasis=True
                ))

        last_idx = end

    # Text after the last tag
    if last_idx < len(script):
        tail_text = script[last_idx:]
        _append_plain_text(raw_segments, tail_text, baseline_rate, baseline_pitch_hz, sentence_pause, auto_sentence_pauses)

    return _clean_and_coalesce_segments(raw_segments)

def _append_plain_text(
    segments: List[Segment],
    text: str,
    rate: float,
    pitch_hz: int,
    sentence_pause: float,
    auto_sentence_pauses: bool
):
    """Split plain text by sentence boundaries if auto_sentence_pauses is True."""
    clean_text = text.strip()
    if not clean_text:
        return

    if not auto_sentence_pauses:
        segments.append(SpeechSegment(
            text=clean_text,
            rate=format_rate(rate),
            pitch=format_pitch(pitch_hz),
            volume="+0%"
        ))
        return

    # Split by sentence ending punctuation (. ? !)
    sentences = re.split(r"([.?!]+(?:\s+|$))", clean_text)
    current_sentence = ""

    for part in sentences:
        if not part:
            continue
        current_sentence += part
        if re.search(r"[.?!]+(?:\s+|$)", part):
            sent_str = current_sentence.strip()
            if sent_str:
                segments.append(SpeechSegment(
                    text=sent_str,
                    rate=format_rate(rate),
                    pitch=format_pitch(pitch_hz),
                    volume="+0%"
                ))
                # Add natural sentence pause
                segments.append(PauseSegment(duration=sentence_pause))
            current_sentence = ""

    if current_sentence.strip():
        segments.append(SpeechSegment(
            text=current_sentence.strip(),
            rate=format_rate(rate),
            pitch=format_pitch(pitch_hz),
            volume="+0%"
        ))

def _clean_and_coalesce_segments(segments: List[Segment]) -> List[Segment]:
    """Merge adjacent pauses and coalesce adjacent speech segments with identical audio settings (R2.6)."""
    result: List[Segment] = []

    for seg in segments:
        if isinstance(seg, PauseSegment):
            if seg.duration <= 0.01:
                continue
            if result and isinstance(result[-1], PauseSegment):
                # Keep the longer pause rather than stacking indefinitely
                result[-1].duration = max(result[-1].duration, seg.duration)
            else:
                result.append(seg)
        elif isinstance(seg, SpeechSegment):
            clean_text = seg.text.strip()
            if not clean_text:
                continue
            # If segment has no speakable words (only punctuation like '.' or '?')
            if not re.search(r"\w", clean_text):
                if result and isinstance(result[-1], SpeechSegment):
                    result[-1].text = (result[-1].text + clean_text).strip()
                continue

            # Coalesce with preceding SpeechSegment if parameters match exactly (R2.6)
            if (
                result
                and isinstance(result[-1], SpeechSegment)
                and result[-1].rate == seg.rate
                and result[-1].pitch == seg.pitch
                and result[-1].volume == seg.volume
                and result[-1].is_whisper == seg.is_whisper
                and result[-1].is_emphasis == seg.is_emphasis
            ):
                result[-1].text = f"{result[-1].text} {clean_text}".strip()
            else:
                result.append(seg)

    # Trim trailing pause
    if result and isinstance(result[-1], PauseSegment):
        result.pop()

    return result
