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
            print("   Verifying GPU inference...")
            try:
                import numpy as np
                dummy_audio = np.zeros(16000, dtype=np.float32) 
                segments, _ = model.transcribe(dummy_audio, beam_size=1)
                list(segments) # Consume generator
                print("   ✅ GPU Warmup successful")
                
                self.model = model
                print(f"✅ Whisper ready ({model_size} on GPU/CUDA)")
                return

            except ImportError:
                print("   ⚠️ Numpy not found, skipping active GPU warmup (assuming success)")
                self.model = model
                print(f"✅ Whisper ready ({model_size} on GPU/CUDA)")
                return

            except Exception as e:
                print(f"⚠️ GPU Init/Warmup Failed: {e}")
                print("   Falling back to CPU...")
                # Fallthrough to CPU block below
        
        except Exception as e:
            print(f"⚠️ GPU Init Failed: {e}")
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

        print(f"🎤 Processing audio: {len(audio_bytes)} bytes")
        
        try:
            import io
            audio_buffer = io.BytesIO(audio_bytes)
            
            # Fast transcription settings
            segments, info = self.model.transcribe(
                audio_buffer,
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

if __name__ == "__main__":
    stt = STTService()
    print("STT Service Ready")
