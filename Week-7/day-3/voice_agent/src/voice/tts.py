import asyncio
import httpx
from typing import AsyncGenerator
from src.config.settings import settings

class TTSClient:
    """
    Streaming TTS using Fish Audio via HTTPX.
    Takes token stream from LLM, groups into sentences, and fetches audio.
    """
    def __init__(self, api_key: str = settings.FISH_AUDIO_API_KEY):
        self.api_key = api_key
        # Fish Audio standard API endpoint for TTS
        self.api_url = "https://api.fish.audio/v1/tts"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def _fetch_audio_for_text(self, text: str) -> bytes:
        """Helper to call Fish Audio REST API and return audio bytes."""
        payload = {
            "text": text,
            "format": "mp3", 
            "latency": "normal" # Use normal or low for faster response
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.api_url, json=payload, headers=self.headers, timeout=5.0)
                if response.status_code == 200:
                    return response.content
                else:
                    print(f"TTS Error: {response.status_code} - {response.text}")
                    return b""
        except Exception as e:
            print(f"TTS Exception: {e}")
            return b""

    async def generate_audio_stream(self, text_stream: AsyncGenerator[str, None]) -> AsyncGenerator[bytes, None]:
        """
        Consumes LLM text chunks, buffers them into sentences, and requests audio.
        Yields raw audio bytes.
        """
        sentence_buffer = ""
        # Punctuation marks indicating a safe place to speak the buffered phrase
        delimiters = ['.', '!', '?', '۔', ',', '\n']
        
        async for token in text_stream:
            sentence_buffer += token
            # Flush buffer to TTS API if delimiter found
            if any(p in token for p in delimiters) and len(sentence_buffer.strip()) > 2:
                text_to_speak = sentence_buffer.strip()
                sentence_buffer = "" # Reset early
                
                audio_bytes = await self._fetch_audio_for_text(text_to_speak)
                if audio_bytes:
                    yield audio_bytes
                
        # Flush remaining text
        if sentence_buffer.strip():
            audio_bytes = await self._fetch_audio_for_text(sentence_buffer.strip())
            if audio_bytes:
                yield audio_bytes

    async def generate_audio_instant(self, text: str) -> bytes:
        """For instant acknowledgements (e.g., 'Ji sir')"""
        return await self._fetch_audio_for_text(text)
