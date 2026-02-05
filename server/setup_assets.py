import os
import requests
from tqdm import tqdm

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_NAME = "en_US-lessac-medium"
ONNX_FILE = f"{MODEL_NAME}.onnx"
JSON_FILE = f"{MODEL_NAME}.onnx.json"

# Official Hugging Face Links
BASE_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium"
ONNX_URL = f"{BASE_URL}/{ONNX_FILE}?download=true"
JSON_URL = f"{BASE_URL}/{JSON_FILE}?download=true"

def download_file(url, filename, folder):
    filepath = os.path.join(folder, filename)
    if os.path.exists(filepath):
        print(f"✅ {filename} already exists.")
        return filepath

    print(f"⬇️ Downloading {filename}...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024
        
        with open(filepath, 'wb') as f, tqdm(
            desc=filename,
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(block_size):
                size = f.write(data)
                bar.update(size)
                
        print(f"✅ {filename} downloaded.")
        return filepath
    except Exception as e:
        print(f"❌ Failed to download {filename}: {e}")
        if os.path.exists(filepath):
            os.remove(filepath)
        return None

def setup_piper_models():
    if not os.path.exists(MODELS_DIR):
        print(f"📂 Creating models directory: {MODELS_DIR}")
        os.makedirs(MODELS_DIR)

    model_path = download_file(ONNX_URL, ONNX_FILE, MODELS_DIR)
    config_path = download_file(JSON_URL, JSON_FILE, MODELS_DIR)
    
    if model_path and config_path:
        return model_path
    else:
        raise RuntimeError("Failed to set up Piper assets.")

if __name__ == "__main__":
    setup_piper_models()
