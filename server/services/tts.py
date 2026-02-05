"""
TTS Service using piper-tts Python library.
Uses 'libritts_r' model for realistic voice.
Correctly extracts bytes from AudioChunk using audio_int16_bytes.
"""
import os
import io
import wave

try:
    from piper import PiperVoice
    PIPER_AVAILABLE = True
except ImportError:
    PIPER_AVAILABLE = False
    print("⚠️ piper-tts not installed. Run: pip install piper-tts")

class TTSService:
    def __init__(self):
        self.voice = None
        
        if not PIPER_AVAILABLE:
            print("❌ TTS unavailable - piper-tts not installed")
            return
            
        base_dir = os.path.dirname(os.path.dirname(__file__))  # server/
        
        # Use new realistic model if available, else fallback
        new_model = os.path.join(base_dir, "models", "en_US-libritts_r-medium.onnx")
        old_model = os.path.join(base_dir, "models", "en_US-lessac-medium.onnx")
        
        if os.path.exists(new_model):
            model_path = new_model
            print(f"🔊 Using Realistic Voice: Libritts-R")
        elif os.path.exists(old_model):
            model_path = old_model
            print(f"🔊 Using Standard Voice: Lessac")
        else:
            print(f"❌ No Piper models found in {base_dir}/models")
            return
            
        config_path = model_path + ".json"
        
        try:
            print(f"🔊 Loading Piper voice model...")
            self.voice = PiperVoice.load(model_path, config_path)
            self.sample_rate = getattr(self.voice.config, 'sample_rate', 22050)
            print(f"✅ TTS ready! (Sample rate: {self.sample_rate}Hz)")
        except Exception as e:
            print(f"❌ Failed to load Piper voice: {e}")
            self.voice = None

    def synthesize(self, text):
        if not self.voice or not text:
            return None
            
        try:
            audio_stream = self.voice.synthesize(text)
            
            raw_data = b""
            
            for chunk in audio_stream:
                # Based on debugging, the attribute is audio_int16_bytes
                if hasattr(chunk, 'audio_int16_bytes'):
                    raw_data += chunk.audio_int16_bytes
                elif hasattr(chunk, 'bytes'):
                    raw_data += chunk.bytes
                else:
                    # Generic fallback
                    try:
                        raw_data += bytes(chunk)
                    except:
                        pass
            
            if not raw_data:
                print("❌ TTS yielded no data (Attributes found: {})".format(dir(chunk) if 'chunk' in locals() else 'None'))
                return None

            audio_buffer = io.BytesIO()
            with wave.open(audio_buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)                # Mono
                wav_file.setsampwidth(2)                # 16-bit
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(raw_data)
            
            audio_buffer.seek(0)
            audio_bytes = audio_buffer.read()
            
            print(f"🔊 TTS generated {len(audio_bytes)} bytes")
            return audio_bytes
            
        except Exception as e:
            print(f"❌ TTS Error: {e}")
            import traceback
            traceback.print_exc()
            return None

    def synthesize_stream_raw(self, text):
        """
        Yields raw audio chunks (bytes) for streaming.
        """
        if not self.voice or not text:
            return
            
        try:
            audio_stream = self.voice.synthesize(text)
            for chunk in audio_stream:
                if hasattr(chunk, 'audio_int16_bytes'):
                    yield chunk.audio_int16_bytes
                elif hasattr(chunk, 'bytes'):
                    yield chunk.bytes
                else:
                    try:
                        yield bytes(chunk)
                    except:
                        pass
        except Exception as e:
            print(f"❌ TTS Streaming Error: {e}")

