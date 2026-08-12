from fastapi import FastAPI, WebSocket
from src.config.settings import settings
from src.voice.stt import STTClient
from src.voice.tts import TTSClient
from src.llm.engine import LLMEngine
from src.memory.store import MemoryStore
from src.conversation.orchestrator import ConversationOrchestrator
from src.logging.logger import logger
import traceback

app = FastAPI(title=settings.APP_NAME)

@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.APP_NAME} in {settings.ENVIRONMENT} mode.")

@app.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for bidirectional audio streaming.
    Clients connect and send raw audio bytes. Agent replies with audio bytes.
    """
    await websocket.accept()
    
    stt = STTClient(api_key=settings.DEEPGRAM_API_KEY)
    tts = TTSClient(api_key=settings.FISH_AUDIO_API_KEY)
    llm = LLMEngine(model=settings.LLM_MODEL)
    memory = MemoryStore()
    
    orchestrator = ConversationOrchestrator(stt=stt, tts=tts, llm=llm, memory=memory)
    
    # Create an async generator to yield incoming websocket audio
    async def ws_audio_receiver():
        try:
            while True:
                data = await websocket.receive_bytes()
                yield data
        except Exception:
            pass

    try:
        async for audio_out in orchestrator.handle_incoming_audio(ws_audio_receiver()):
            await websocket.send_bytes(audio_out)
    except Exception as e:
        logger.error(f"WebSocket error: {traceback.format_exc()}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
