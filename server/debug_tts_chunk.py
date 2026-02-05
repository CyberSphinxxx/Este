try:
    from piper import PiperVoice
    import os

    base_dir = os.path.dirname(__file__)
    model_path = os.path.join(base_dir, "models", "en_US-libritts_r-medium.onnx")
    
    if not os.path.exists(model_path):
        print("Using old model for debug")
        model_path = os.path.join(base_dir, "models", "en_US-lessac-medium.onnx")

    voice = PiperVoice.load(model_path, model_path + ".json")
    stream = voice.synthesize("test")
    
    for chunk in stream:
        print(f"Chunk Type: {type(chunk)}")
        print(f"Dir: {dir(chunk)}")
        
        # Test attributes safely
        try:
            val = getattr(chunk, 'bytes')
            print(f"chunk.bytes exists. Type: {type(val)}")
        except Exception as e:
            print(f"chunk.bytes access failed: {e}")
            
        try:
            val = getattr(chunk, 'audio')
            print(f"chunk.audio exists. Type: {type(val)}")
        except Exception as e:
            print(f"chunk.audio access failed: {e}")

        # Try to find THE data
        if hasattr(chunk, 'audio') and chunk.audio:
            print(f"Audio content preview: {chunk.audio[:10]}")
            
        break # Only 1 chunk needed

except Exception as e:
    print(f"ERROR: {e}")
