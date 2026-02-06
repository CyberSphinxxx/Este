
from services.kokoro_tts import KokoroTTS
import time
import os

def test_kokoro():
    print("🧪 Testing Kokoro TTS...")
    tts = KokoroTTS()
    
    text = "Hello! I am Este, capable of speaking with emotion."
    print(f"🗣️ Synthesizing: '{text}'")
    
    t0 = time.time()
    # We use synthesize_stream_raw which yields WAV bytes
    chunks = list(tts.synthesize_stream_raw(text))
    t1 = time.time()
    
    print(f"✅ Synthesis complete in {t1-t0:.2f}s")
    
    # Save to file to verify
    if chunks:
        wav_data = b"".join(chunks) # It yields one big chunk in my implementation
        with open("test_kokoro.wav", "wb") as f:
            f.write(wav_data)
        print(f"💾 Saved test_kokoro.wav ({len(wav_data)} bytes)")
    else:
        print("❌ No audio generated")

if __name__ == "__main__":
    test_kokoro()
