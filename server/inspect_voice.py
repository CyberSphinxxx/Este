try:
    from piper import PiperVoice
    import os

    # Inspect from server/inspect_voice.py
    # Model is at server/models/
    base_dir = os.path.dirname(__file__) # server/
    model_path = os.path.join(base_dir, "models", "en_US-lessac-medium.onnx")
    config_path = model_path + ".json"
    
    print(f"Checking path: {model_path}")
    if os.path.exists(model_path):
        voice = PiperVoice.load(model_path, config_path)
        print("✅ Voice loaded.")
        print("Attributes/Methods:", dir(voice))
    else:
        print("❌ Model not found at path.")

except Exception as e:
    print(f"Error: {e}")
