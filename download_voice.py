import urllib.request
import os

MODELS = {
    "onnx": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/libritts_r/medium/en_US-libritts_r-medium.onnx",
    "json": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/libritts_r/medium/en_US-libritts_r-medium.onnx.json"
}

dest_dir = "server/models"
os.makedirs(dest_dir, exist_ok=True)

for ext, url in MODELS.items():
    filename = url.split("/")[-1]
    dest = os.path.join(dest_dir, filename)
    print(f"Downloading {filename}...")
    try:
        urllib.request.urlretrieve(url, dest)
        print(f"✅ Saved to {dest}")
    except Exception as e:
        print(f"❌ Failed: {e}")
