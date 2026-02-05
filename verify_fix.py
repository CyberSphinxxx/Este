import os
import shutil
import sys

print("🔍 Running Final System Check...")

# 1. Clean Chroma DB
db_path = os.path.join("server", "chroma_db")
if os.path.exists(db_path):
    print(f"🧹 Finding old RAG database at {db_path}...")
    try:
        shutil.rmtree(db_path)
        print("   ✅ Database deleted (Force Cleanup)")
    except Exception as e:
        print(f"   ❌ Failed to delete DB: {e}")
else:
    print("   ✅ Database already clean")

# 2. Check Main.py for 'import time'
main_path = os.path.join("server", "main.py")
try:
    with open(main_path, 'r') as f:
        content = f.read()
    if "import time" in content:
        print("   ✅ main.py has 'import time'")
    else:
        print("   ❌ main.py MISSING 'import time'")
except Exception as e:
    print(f"   ❌ Could not read main.py: {e}")

# 3. Check STT Warmup
stt_path = os.path.join("server", "services", "stt.py")
try:
    with open(stt_path, 'r') as f:
        content = f.read()
    if "WARMUP" in content or "Warmup" in content:
        print("   ✅ stt.py has Warmup/Fallback logic")
    else:
        print("   ❌ stt.py MISSING Warmup logic")
except Exception as e:
    print(f"   ❌ Could not read stt.py: {e}")

# 4. Check Model File
model_path = os.path.join("server", "models", "en_US-libritts_r-medium.onnx")
if os.path.exists(model_path):
    print("   ✅ Realistic Voice Model found")
else:
    print("   ⚠️ Realistic Voice Model NOT found (Will fallback to standard)")

print("\n🏁 Check Complete.")
