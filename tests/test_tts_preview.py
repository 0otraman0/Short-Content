import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from main import app, CACHE_DIR
import tts

def test_tts_endpoints():
    client = TestClient(app)

    # 1. Test GET /api/tts/voices
    res = client.get("/api/tts/voices")
    assert res.status_code == 200
    data = res.json()
    assert "current_voice" in data
    assert "voices" in data
    assert len(data["voices"]) > 0

    # 2. Test POST /api/tts/preview with valid text and markup
    preview_payload = {
        "text": "[fast]Mind blowing facts.[/fast] [pause 0.5] Sharks are *ancient*.",
        "preset": "mystery"
    }
    res = client.post("/api/tts/preview", json=preview_payload)
    assert res.status_code == 200
    preview_data = res.json()
    assert preview_data["success"] is True
    assert "audio_url" in preview_data
    assert preview_data["duration"] > 0

    # 3. Verify audio file was written and can be accessed
    audio_path = Path("static" + preview_data["audio_url"].replace("/static", ""))
    assert audio_path.exists()
    assert audio_path.stat().st_size > 1000

    # Test downloading the audio file via static endpoint
    res_audio = client.get(preview_data["audio_url"])
    assert res_audio.status_code == 200
    assert len(res_audio.content) > 1000

    # Clean up test preview audio
    if audio_path.exists():
        audio_path.unlink()

    # 4. Test POST /api/tts/preview with empty text
    res = client.post("/api/tts/preview", json={"text": "   "})
    assert res.status_code == 400

    # 5. Test POST /api/tts/lock-voice
    original_voice = data["current_voice"]
    res = client.post("/api/tts/lock-voice", json={"voice": "en-US-GuyNeural"})
    assert res.status_code == 200
    assert res.json()["voice"] == "en-US-GuyNeural"
    assert tts.get_locked_voice() == "en-US-GuyNeural"

    # Restore original voice
    client.post("/api/tts/lock-voice", json={"voice": original_voice})
    assert tts.get_locked_voice() == original_voice

    print("TTS Preview & Voice API tests passed successfully!")

if __name__ == "__main__":
    test_tts_endpoints()
