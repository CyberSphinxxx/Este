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
from services.tts import TTSService
from services.viseme_mapper import VisemeMapper
from setup_assets import setup_piper_models

app = FastAPI()

# Auto-setup assets on startup
try:
    print("Checking Piper Assets...")
    setup_piper_models()
except Exception as e:
    print(f"Asset Setup Failed: {e}")

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
tts_service = TTSService() # Assumes piper is in PATH
viseme_mapper = VisemeMapper()
print("All Services Initialized.")

@app.get("/")
async def root():
    return {"message": "Este Server Running"}

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected to WS")
    try:
        while True:
            # 1. Receive Audio
            audio_bytes = await websocket.receive_bytes()
            start_time = time.time()
            print(f"\n[TIMING] Audio received: {len(audio_bytes)} bytes")
            
            # 2. STT: Transcribe
            t0 = time.time()
            transcript = stt_service.transcribe(audio_bytes)
            t1 = time.time()
            print(f"[TIMING] STT (Transcribe): {t1 - t0:.2f}s")
            print(f"User: {transcript}")
            
            if not transcript or len(transcript.strip()) < 2:
                continue

            # 3. RAG: Retrieve Context
            t2 = time.time()
            context = rag_service.query(transcript)
            t3 = time.time()
            print(f"[TIMING] RAG (Retrieval): {t3 - t2:.2f}s")

            # 4. LLM: Generate Response
            system_prompt = f"""You are Este, the friendly AI student companion for USTP (University of Science and Technology of Southern Philippines). 
            Your goal is to help students and visitors navigate the campus and find information.
            
            GUIDELINES:
            1. Speak naturally and casually, like a helpful student. Avoid robotic phrasing.
            2. CRITICAL: Keep answers VERY SHORT (max 1-2 sentences). You are speaking out loud.
            3. Use the Context below to answer. If the answer isn't there, politely say you don't know and suggest visiting the Admin Building.
            
            Context: {context}"""
            
            t4 = time.time()
            response_text = llm_service.generate(transcript, system_prompt=system_prompt)
            t5 = time.time()
            print(f"[TIMING] LLM (Generation): {t5 - t4:.2f}s")
            print(f"Este: {response_text}")

            # 5. STREAMING TTS Response
            print(f"[TIMING] Starting Streaming Response...")
            
            # Send "start" signal (contains full text for UI)
            await websocket.send_json({
                "type": "audio_start",
                "text": response_text,
                "sampleRate": tts_service.sample_rate
            })
            
            t_stream_start = time.time()
            chunk_count = 0
            
            # Stream Audio Chunks
            audio_generator = tts_service.synthesize_stream_raw(response_text)
            
            # Pre-calculate visemes (approximation for now, since we stream audio)
            # Ideal: Stream visemes synced with audio, but for now we send all visemes 
            # and let frontend play them? OR we send visemes frame by frame?
            # Simpler: Send all visemes in "audio_start" so frontend can animate?
            # We'll send them in 'audio_start'
            visemes = viseme_mapper.map_text_to_visemes(response_text)
            await websocket.send_json({
                "type": "viseme_data",
                "visemes": visemes
            })
            
            if audio_generator:
                for chunk in audio_generator:
                    chunk_count += 1
                    # Send raw audio chunk (base64)
                    await websocket.send_json({
                        "type": "audio_chunk",
                        "audio": base64.b64encode(chunk).decode('utf-8')
                    })
                    # Yield control to event loop to minimize blocking
                    if chunk_count % 5 == 0:
                        await asyncio.sleep(0) 

                t_stream_end = time.time()
                print(f"[TIMING] Stream Finished: {t_stream_end - t_stream_start:.2f}s (Chunks: {chunk_count})")
            
            # Send "end" signal
            await websocket.send_json({"type": "audio_end"})

    except Exception as e:
        print(f"Connection closed/Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
