try:
    from piper import PiperVoice
    import os
    import wave
    import io

    base_dir = os.path.dirname(__file__)
    model_path = os.path.join(base_dir, "models", "en_US-lessac-medium.onnx")
    
    print(f"Loading {model_path}...")
    voice = PiperVoice.load(model_path, model_path + ".json")
    text = "Hello check."

    # Method 1: synthesize returns bytes?
    try:
        print("\n[1] Testing synthesize() -> bytes...")
        res = voice.synthesize(text, None)
        print(f"Result type: {type(res)}")
    except Exception as e:
        print(f"Error: {e}")

    # Method 2: synthesize_stream_raw?
    try:
        print("\n[2] Testing synthesize_stream_raw()...")
        if hasattr(voice, 'synthesize_stream_raw'):
            data = b""
            for chunk in voice.synthesize_stream_raw(text):
                data += chunk
            print(f"Got {len(data)} bytes")
        else:
            print("Method not found")
    except Exception as e:
        print(f"Error: {e}")

    # Method 3: synthesize writes to file?
    try:
        print("\n[3] Testing synthesize(file)...")
        with io.BytesIO() as wav_buffer:
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(22050)
                voice.synthesize(text, wav_file)
            
            wav_buffer.seek(0)
            print(f"Buffer size: {len(wav_buffer.read())}")
    except Exception as e:
        print(f"Error: {e}")

except Exception as e:
    print(f"Fatal: {e}")
