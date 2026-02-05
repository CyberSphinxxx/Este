from services.tts import TTSService
from services.viseme_mapper import VisemeMapper
from setup_assets import setup_piper_models
import json
import os

def test_pipeline():
    # Redirect stdout to a file for reliable reading
    import sys
    original_stdout = sys.stdout
    with open("pipeline_test_log.txt", "w", encoding="utf-8") as log_file:
        sys.stdout = log_file
        
        print("--- Starting Pipeline Verification (Logged) ---\n")

        # 1. Setup Assets (Ensure model exists)
        print("[1] Checking Assets...")
        try:
            model_path = setup_piper_models()
            print(f"    Model at: {model_path}")
        except Exception as e:
            print(f"    Asset Check Failed: {e}")

        # 2. Initialize Services
        print("\n[2] Initializing Services...")
        try:
            tts = TTSService() # Auto-resolves path
            mapper = VisemeMapper()
            print("    Services initialized.")
        except Exception as e:
            print(f"    Error initializing servies: {e}")
            sys.stdout = original_stdout
            return

        # 3. Test Text
        text = "Maayong buntag, ako si Este."
        print(f"\n[3] Processing Text: '{text}'")

        # 4. Generate Visemes
        print("\n[4] Generating Visemes...")
        try:
            visemes = mapper.map_text_to_visemes(text)
            
            if visemes and len(visemes) > 0:
                print(f"    ✅ Generated {len(visemes)} viseme events.")
                print("    Inspecting first 5 visemes:")
                print(json.dumps(visemes[:5], indent=2))
                
                # Verify codes
                valid_codes = ["sil", "PP", "FF", "TH", "DD", "kk", "CH", "SS", "nn", "RR", "aa", "E", "ih", "oh", "ou"]
                invalid_count = 0
                for v in visemes:
                    if v['value'] not in valid_codes:
                        print(f"    ❌ Warning: Invalid Viseme Code found: {v['value']}")
                        invalid_count += 1
                
                if invalid_count == 0:
                    print("    ✅ All viseme codes are valid Oculus Standard.")
            else:
                print("    ❌ Error: No visemes generated!")
        except Exception as e:
            print(f"    ❌ Viseme Generation Exception: {e}")

        # 5. Generate Audio
        print("\n[5] Generating Audio...")
        try:
            audio_bytes = tts.synthesize(text)
            
            if audio_bytes and len(audio_bytes) > 0:
                output_file = "test_output_pipeline.wav"
                # Need to write file outside of stdout redirect or handle bytes carefully? 
                # actually it writes to file path
                pass 
                print(f"    ✅ Audio generated ({len(audio_bytes)} bytes)")
            else:
                print("    ❌ Error: TTS failed to generate audio. (Check if 'piper' is in PATH)")
        except Exception as e:
             print(f"    ❌ TTS Exception: {e}")

        print("\n--- Verification Complete ---")
    
    sys.stdout = original_stdout
    print("Test complete. Log written to pipeline_test_log.txt")

if __name__ == "__main__":
    test_pipeline()
