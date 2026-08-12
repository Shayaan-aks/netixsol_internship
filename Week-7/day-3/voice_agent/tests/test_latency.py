import pytest
import asyncio
import time
from src.voice.stt import STTClient
from src.voice.tts import TTSClient
from src.llm.engine import LLMEngine
from src.memory.store import MemoryStore
from src.conversation.orchestrator import ConversationOrchestrator

@pytest.mark.asyncio
async def test_end_to_end_latency():
    """
    Tests the theoretical latency of the mocked pipeline components.
    Ensures that the time to first byte of audio is under 2 seconds.
    """
    stt = STTClient(api_key="mock")
    tts = TTSClient(api_key="mock")
    llm = LLMEngine(model="mock")
    memory = MemoryStore()
    
    orchestrator = ConversationOrchestrator(stt=stt, tts=tts, llm=llm, memory=memory)
    
    async def mock_audio_stream():
        yield b"hello"
        await asyncio.sleep(0.1) # Simulate stream ending
        
    start_time = time.time()
    
    first_byte_time = None
    async for audio_chunk in orchestrator.handle_incoming_audio(mock_audio_stream()):
        if first_byte_time is None:
            first_byte_time = time.time()
            break
            
    latency_ms = (first_byte_time - start_time) * 1000
    
    # Assert that the total latency from STT input to first TTS byte is under 2000ms
    assert latency_ms < 2000, f"Latency too high: {latency_ms}ms"
    print(f"End-to-End Latency: {latency_ms:.2f}ms")
