"""
Deepgram STT Service — Production-grade Speech-to-Text for Urdulish.

Uses Deepgram Nova-3 model which supports:
  - English with strong Urdu/Urdulish accent handling
  - Real-time streaming transcription
  - Smart formatting for natural text output

Usage:
  stt = DeepgramSTT()
  text = await stt.transcribe_audio_bytes(audio_bytes)   # one-shot
  # or use WebSocket streaming via Deepgram's live connection
"""
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class DeepgramSTT:
    """
    Wrapper around Deepgram SDK for production speech-to-text.
    Supports both one-shot transcription and live streaming.
    """

    def __init__(self):
        self.api_key = os.environ.get("DEEPGRAM_API_KEY", "")
        self._client = None

        if not self.api_key:
            logger.warning("DEEPGRAM_API_KEY not set — STT will be unavailable on backend")

    def _get_client(self):
        """Lazy-load Deepgram client."""
        if self._client is None:
            from deepgram import DeepgramClient
            self._client = DeepgramClient(self.api_key)
        return self._client

    async def transcribe_audio_bytes(
        self,
        audio_bytes: bytes,
        language: str = "en",
        model: str = "nova-3",
    ) -> Optional[str]:
        """
        Transcribes a complete audio buffer (WAV/WebM/OGG) using Deepgram.
        
        For Urdulish: use model="nova-3" with language="en" — it handles
        English with heavy Urdu code-switching natively.
        
        Returns the transcript text, or None if transcription fails.
        """
        if not self.api_key:
            logger.warning("Deepgram unavailable — no API key")
            return None

        try:
            from deepgram import PrerecordedOptions, FileSource

            client = self._get_client()
            options = PrerecordedOptions(
                model=model,
                language=language,
                smart_format=True,       # Capitalizes, adds punctuation
                punctuate=True,
                utterances=False,
                filler_words=False,      # Remove ums/uhs
            )
            payload: FileSource = {"buffer": audio_bytes}
            response = await client.listen.asyncprerecorded.v("1").transcribe_file(payload, options)
            transcript = response.results.channels[0].alternatives[0].transcript
            logger.info(f"Deepgram transcript: {transcript!r}")
            return transcript if transcript.strip() else None

        except Exception as e:
            logger.error(f"Deepgram transcription failed: {e}")
            return None

    def get_websocket_url(self, language: str = "en", model: str = "nova-3") -> str:
        """
        Returns the Deepgram WebSocket URL for live streaming.
        Used by the frontend to connect directly to Deepgram for real-time STT.
        """
        params = (
            f"model={model}"
            f"&language={language}"
            f"&encoding=linear16"
            f"&sample_rate=16000"
            f"&channels=1"
            f"&interim_results=true"
            f"&smart_format=true"
            f"&utterance_end_ms=1000"
            f"&vad_events=true"
        )
        return f"wss://api.deepgram.com/v1/listen?{params}"


# Singleton instance
deepgram_stt = DeepgramSTT()
