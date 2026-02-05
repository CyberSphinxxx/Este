"""
STT Service using faster-whisper.
Optimized for speed - using CPU with int8 quantization.
CPU is reliable and "tiny" model is fast enough (~1 second).
"""
from faster_whisper import WhisperModel
import tempfile
import os

class STTService:
    def __init__(self, model_size="tiny", device="cuda", compute_type="float16"):
        """
        Initialize Whisper model.
        Attempts to use GPU (cuda) first, verifies it with a warmup run.
        Falls back to CPU if unavailable or if warmup fails.
        """
        print(f"🎤 Loading Whisper model: {model_size}...")
        self.model = None

        # 1. Try GPU first
        try:
            print(f"   Attempting to use GPU (device='cuda')...")
            model = WhisperModel(model_size, device="cuda", compute_type="float16")
            
            # WARMUP / VERIFICATION
            # actually run a tiny transcription to check for missing DLLs
            print("   Verifying GPU inference...")
            # Create a dummy silent audio (1 sec of silence)
            # Whisper expects audio path or numpy array. 
            # We can't easily create numpy array without numpy installed, 
            # but we can try transcribing a dummy file or just risk it?
            # Better: catch the runtime error during first usage?
            # Actually, let's just try to access the underlying ctranslate2 model properties or rely on the fact 
            # that 'transcribe' might fail later. 
            # BUT, the robust way is to fallback IF transcribe fails.
            
            # Since we can't easily generate audio without numpy/scipy here (maybe we can?), 
            # let's proceed with GPU but update transcribe() to handle the specific RuntimeError and switch to CPU?
            # No, 'transcribe' is called per request. Switching model takes time.
            # Best to switch NOW.
            
            # Let's try to pass a list of zeros if possible? 
            # faster-whisper accepts list of floats.
            dummy_audio = [0.0] * 16000 # 1 sec silence
            segments, _ = model.transcribe(dummy_audio, beam_size=1)
            list(segments) # Consume generator to trigger execution
            
            self.model = model
            print(f"✅ Whisper ready ({model_size} on GPU/CUDA)")
            return
            
        except Exception as e:
            print(f"⚠️ GPU Init/Warmup Failed: {e}")
            print("   Falling back to CPU...")

        # 2. Fallback to CPU
        try:
            self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
            print(f"✅ Whisper ready ({model_size} on CPU)")
        except Exception as e:
            print(f"❌ Error loading Whisper on CPU: {e}")
            self.model = None

    def transcribe(self, audio_bytes):
        """
        Transcribes audio bytes to text.
        Handles WebM/Opus format from browser.
        """
        if not self.model:
            print("❌ Whisper model not loaded")
            return ""

        if len(audio_bytes) < 1000:
            print(f"⚠️ Audio too short ({len(audio_bytes)} bytes)")
            return ""

        print(f"🎤 Processing audio: {len(audio_bytes)} bytes")

        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as f:
                f.write(audio_bytes)
                temp_path = f.name
            
            # Fast transcription settings
            segments, info = self.model.transcribe(
                temp_path,
                beam_size=1,          # Fastest
                language="en",        # Skip language detection
                vad_filter=True,      # Remove silence
            )
            
            # Collect results
            texts = [segment.text for segment in segments]
            result = " ".join(texts).strip()
            
            print(f"📝 Transcription: '{result}'")
            return result
            
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            import traceback
            traceback.print_exc()
            return ""
        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

if __name__ == "__main__":
    stt = STTService()
    print("STT Service Ready")
