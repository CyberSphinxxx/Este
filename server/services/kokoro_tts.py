
import os
import soundfile as sf
import numpy as np
from kokoro_onnx import Kokoro
from huggingface_hub import hf_hub_download

class KokoroTTS:
    def __init__(self, model_name="kokoro-v0_19.onnx", voices_file="voices.bin"):
        """
        Initialize Kokoro TTS with ONNX model.
        Automatically downloads model and voices.bin if missing.
        """
        self.sample_rate = 24000
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = os.path.join(self.base_dir, model_name)
        self.voices_path = os.path.join(self.base_dir, voices_file)
        
        # Auto-download models if missing
        self._ensure_models()
        
        print("🗣️ Loading Kokoro TTS (ONNX)...")
        try:
            self.kokoro = Kokoro(self.model_path, self.voices_path)
            # Warmup
            print("   Warming up Kokoro...")
            self.kokoro.create("Hello", voice="af_sarah", speed=1.0, lang="en-us")
            print("✅ Kokoro TTS Ready")
        except Exception as e:
            print(f"❌ Failed to load Kokoro: {e}")
            self.kokoro = None

    def _ensure_models(self):
        """Download model files from HuggingFace if they don't exist."""
        if not os.path.exists(self.model_path) or not os.path.exists(self.voices_path):
            print("⬇️ Downloading Kokoro models from HuggingFace...")
            try:
                # Download ONNX model (try hexgrad first, fallback if needed or keep thewh1teagle if tested)
                # We stick with hexgrad for model if possible, or correct filename. 
                # Step 429 said hexgrad has kokoro-v0_19.onnx.
                if not os.path.exists(self.model_path):
                    print("   Downloading kokoro-v0_19.onnx...")
                    try:
                        hf_hub_download(
                            repo_id="hexgrad/Kokoro-82M", 
                            filename="kokoro-v0_19.onnx", 
                            local_dir=self.base_dir
                        )
                    except:
                        # Fallback
                        print("   Fallback download from thewh1teagle...")
                        hf_hub_download(
                            repo_id="thewh1teagle/Kokoro", 
                            filename="kokoro-v0_19.onnx", 
                            local_dir=self.base_dir
                        )
                
                
                # Download voices.bin from official GitHub release
                # The library expects a specific format/pickle.
                if not os.path.exists(self.voices_path):
                    print("   Downloading voices.bin from GitHub...")
                    import urllib.request
                    url = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"
                    urllib.request.urlretrieve(url, self.voices_path)
                    print("✅ Download voices.bin complete.")
                
                print("✅ Download complete.")
            except Exception as e:
                print(f"❌ Error downloading models: {e}")

    def synthesize_stream_raw(self, text, voice="af_sarah", speed=1.0):
        """
        Synthesize text to WAV audio bytes.
        Yields the entire sentence audio as a single WAV file (byte stream).
        """
        if not self.kokoro:
            print("❌ Kokoro not initialized")
            return

        try:
            import io
            # Kokoro.create returns (audio_samples, phonemes)
            audio, _ = self.kokoro.create(text, voice=voice, speed=speed, lang="en-us")
            
            # Write to in-memory WAV file
            buffer = io.BytesIO()
            sf.write(buffer, audio, self.sample_rate, format='WAV')
            wav_bytes = buffer.getvalue()
            
            # Yield the whole WAV file as one chunk (since we stream sentence-by-sentence)
            yield wav_bytes
                
        except Exception as e:
            print(f"❌ TTS Synthesis Error: {e}")
