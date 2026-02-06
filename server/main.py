from fastapi import FastAPI, WebSocket
import time
import asyncio
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import base64
import json
import traceback

# Services
from rag_service import RAGService
from services.stt import STTService
from services.llm import LLMService
from services.viseme_mapper import VisemeMapper
# from services.tts import TTSService # Deprecated Piper
from services.kokoro_tts import KokoroTTS
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Services
print("Initializing Services...")
rag_service = RAGService()
rag_service.initialize()

stt_service = STTService(model_size="tiny") 
llm_service = LLMService(model="qwen2.5:1.5b")
tts_service = KokoroTTS() 
viseme_mapper = VisemeMapper()

print("🔥 Warming up pipelines...")
# Warmup RAG (loads ChromaDB)
rag_service.query("warmup")
# Warmup LLM (loads model to VRAM)
print("   Warming up LLM...")
llm_service.generate("hi") 
# Warmup TTS (already handled in init, but one more check)
print("   Warming up TTS...")
list(tts_service.synthesize_stream_raw("Hello."))

print("✅ All Services Initialized & Warmed Up.")

@app.get("/")
async def root():
    return {"message": "Este Server Running"}

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected to WS")
    
    async def process_text(text: str):
        # 3. RAG: Retrieve Context
        t1 = time.time()
        context = rag_service.query(text)
        print(f"[TIMING] RAG (Retrieval): {time.time() - t1:.2f}s")

        # 4. LLM Streaming & Sentence Processing
        system_prompt = f"""You are Este, the friendly AI student companion for USTP. 
        Speak naturally and casually. Keep answers SHORT (max 1-3 sentences).
        Context: {context}"""
        
        print(f"[TIMING] Starting LLM & TTS Pipeline...")
        
        # Signal start of response
        await websocket.send_json({
            "type": "audio_start",
            "text": "...", # Text will be updated as we get it
            "sampleRate": tts_service.sample_rate
        })

        full_response = ""
        current_sentence = ""
        t_llm_start = time.time()
        
        # Iterate through LLM stream
        for token in llm_service.stream_generate(text, system_prompt=system_prompt):
            full_response += token
            current_sentence += token
            
            # If we hit a sentence boundary, synthesize right away
            if any(punct in token for punct in [".", "!", "?", "\n"]):
                sentence_to_play = current_sentence.strip()
                if len(sentence_to_play) > 3:
                    # Send visemes and audio
                    visemes = viseme_mapper.map_text_to_visemes(sentence_to_play)
                    await websocket.send_json({"type": "viseme_data", "visemes": visemes})
                    for chunk in tts_service.synthesize_stream_raw(sentence_to_play):
                        await websocket.send_json({
                            "type": "audio_chunk",
                            "audio": base64.b64encode(chunk).decode('utf-8')
                        })
                    current_sentence = ""
        
        # Final cleanup
        if current_sentence.strip():
            visemes = viseme_mapper.map_text_to_visemes(current_sentence)
            await websocket.send_json({"type": "viseme_data", "visemes": visemes})
            for chunk in tts_service.synthesize_stream_raw(current_sentence):
                await websocket.send_json({
                    "type": "audio_chunk",
                    "audio": base64.b64encode(chunk).decode('utf-8')
                })
        
        # Update UI & End
        await websocket.send_json({"type": "audio_response", "text": full_response})
        await websocket.send_json({"type": "audio_end"})
        print(f"[TIMING] Total Response Cycle: {time.time() - t_llm_start:.2f}s")

    try:
        while True:
            # Handle both bytes (audio) and text (json)
            message = await websocket.receive()
            
            if "bytes" in message:
                audio_bytes = message["bytes"]
                print(f"\n[TIMING] Audio received: {len(audio_bytes)} bytes")
                
                # 2. STT: Transcribe
                t0 = time.time()
                transcript = stt_service.transcribe(audio_bytes)
                print(f"[TIMING] STT (Transcribe): {time.time() - t0:.2f}s")
                print(f"User (Audio): {transcript}")
                
                if transcript and len(transcript.strip()) >= 2:
                    await process_text(transcript)
                    
            elif "text" in message:
                data = json.loads(message["text"])
                if data.get("type") == "text_query":
                    query = data.get("text")
                    print(f"User (Text): {query}")
                    await process_text(query)

    except Exception as e:
        print(f"Connection closed/Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
