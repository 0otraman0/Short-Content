"""
infrastructure - Data Access & Infrastructure Layer.

Provides low-level adapters:
- ffmpeg_processor: silence generation, filter chain, concatenation, loudness norm.
- tts_providers: EdgeTTSProvider, KokoroTTSProvider, voice locking.
- whisper_adapter: faster-whisper model loading, PyAV patch, SRT transcription.
"""
