import asyncio
import time
from typing import AsyncGenerator
from src.voice.stt import STTClient
from src.voice.tts import TTSClient
from src.llm.engine import LLMEngine
from src.memory.store import MemoryStore
from src.prompts.templates import SYSTEM_PROMPT
from src.conversation.behaviors import ConversationalBehaviors
from src.logging.logger import logger

class ConversationOrchestrator:
    """
    The core brain of the voice agent.
    Manages STT -> LLM -> TTS pipeline, measures latency, and handles barge-ins.
    """
    def __init__(self, stt: STTClient, tts: TTSClient, llm: LLMEngine, memory: MemoryStore):
        self.stt = stt
        self.tts = tts
        self.llm = llm
        self.memory = memory
        self.is_speaking = False
        self.barge_in_event = asyncio.Event()

    async def handle_incoming_audio(self, audio_stream: AsyncGenerator[bytes, None]) -> AsyncGenerator[bytes, None]:
        """
        Main loop handling the duplex stream.
        """
        async for final_transcript in self.stt.start_listening(audio_stream):
            # If agent was speaking and user interrupted, trigger barge-in
            if self.is_speaking:
                self.barge_in_event.set()
                logger.info("Barge-in detected. Stopping TTS.")
            
            logger.info(f"User: {final_transcript}")
            self.memory.add_interaction("user", final_transcript)
            
            # Start pipeline timer
            start_time = time.time()
            
            # 1. Immediately yield an acknowledgement while thinking (Latency < 200ms)
            ack = ConversationalBehaviors.get_acknowledgement()
            # yield await self.tts.generate_audio_instant(ack)
            
            # 2. Add thinking pause naturally
            await ConversationalBehaviors.simulate_thinking_pause()
            
            # 3. Stream LLM to TTS
            context_str = self.memory.get_full_state_summary()
            prompt = SYSTEM_PROMPT.format(context=context_str)
            
            self.is_speaking = True
            self.barge_in_event.clear()
            
            text_stream = self.llm.generate_response_stream(prompt, self.memory.get_context_window())
            
            full_response = ""
            async for audio_chunk in self.tts.generate_audio_stream(text_stream):
                if self.barge_in_event.is_set():
                    break # Stop playing if interrupted
                
                # First byte out latency
                if full_response == "":
                    latency = (time.time() - start_time) * 1000
                    logger.log_latency("end_to_end", latency)
                
                full_response += " (audio) " # Mock tracking
                yield audio_chunk
                
            self.is_speaking = False
            self.memory.add_interaction("assistant", full_response)
