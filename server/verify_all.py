import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

print("🔍 Verifying Services...")

try:
    print("\n[1/2] Testing TTS Service...")
    from services.tts import TTSService
    tts = TTSService()
    if tts.voice:
        print("   ✅ TTS Model Loaded")
        audio = tts.synthesize("Testing one two three.")
        if audio and len(audio) > 100:
            print(f"   ✅ TTS Synthesis Success ({len(audio)} bytes generated)")
            # Verify WAV header
            if audio.startswith(b'RIFF') and b'WAVEfmt ' in audio:
                 print("   ✅ WAV Header detected")
            else:
                 print("   ❌ WAV Header MISSING")
        else:
            print("   ❌ TTS Synthesis Failed")
    else:
        print("   ❌ TTS Model Failed to Load")

except Exception as e:
    print(f"   ❌ TTS Check Error: {e}")
    import traceback
    traceback.print_exc()

try:
    print("\n[2/2] Testing STT Service...")
    from services.stt import STTService
    stt = STTService(model_size="tiny", device="cpu", compute_type="int8")
    if stt.model:
        print("   ✅ STT Model Loaded (CPU Mode)")
    else:
        print("   ❌ STT Model Failed to Load")

except Exception as e:
    print(f"   ❌ STT Check Error: {e}")

print("\nDONE.")
