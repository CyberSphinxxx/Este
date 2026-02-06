
import os
import onnxruntime as ort
import json
import numpy as np
import kokoro_onnx

def debug_load():
    print(f"📦 kokoro-onnx version: {kokoro_onnx.__version__ if hasattr(kokoro_onnx, '__version__') else 'unknown'}")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, "kokoro-v0_19.onnx")
    voices_path = os.path.join(base_dir, "voices.bin") # We have voices.bin from conversion
    json_path = os.path.join(base_dir, "voices.json") # We have voices.json

    print(f"🔍 Checking model: {model_path}")
    if os.path.exists(model_path):
        size = os.path.getsize(model_path)
        print(f"   Size: {size / 1024 / 1024:.2f} MB")
        try:
            sess = ort.InferenceSession(model_path)
            print("   ✅ ONNX Model loaded successfully via onnxruntime!")
        except Exception as e:
            print(f"   ❌ ONNX Load Failed: {e}")
    else:
        print("   ❌ Model file missing")

    print(f"🔍 Checking voices.bin")
    if os.path.exists(voices_path):
        try:
            # Try plain pickle load
            import pickle
            with open(voices_path, 'rb') as f:
                d = pickle.load(f)
            print(f"   ✅ Pickle load success. Keys: {len(d)}")
        except Exception as e:
            print(f"   ❌ Pickle load failed: {e}")
            
        try:
            # Try numpy load
            d = np.load(voices_path, allow_pickle=True)
            print(f"   ✅ Numpy load success.")
        except Exception as e:
            print(f"   ❌ Numpy load failed: {e}")

    # Finally try Kokoro instantiation
    print("🚀 Attempting Kokoro(model, voices.bin)...")
    try:
        k = kokoro_onnx.Kokoro(model_path, voices_path)
        print("   ✅ Kokoro init success!")
    except Exception as e:
        print(f"   ❌ Kokoro init failed: {e}")

    print("🚀 Attempting Kokoro(model, voices.json)...")
    try:
        k = kokoro_onnx.Kokoro(model_path, json_path)
        print("   ✅ Kokoro init success (JSON)!")
    except Exception as e:
        print(f"   ❌ Kokoro init failed (JSON): {e}")

if __name__ == "__main__":
    debug_load()
