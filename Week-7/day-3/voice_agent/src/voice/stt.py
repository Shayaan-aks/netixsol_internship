import asyncio
from typing import AsyncGenerator
from deepgram import DeepgramClient, LiveOptions, LiveTranscriptionEvents
from src.config.settings import settings
from src.logging.logger import logger

class STTClient:
    """
    Streaming STT using Deepgram SDK (LiveClient).
    """
    def __init__(self, api_key: str = settings.DEEPGRAM_API_KEY):
        self.api_key = api_key
        # Initialize Deepgram
        self.dg_client = DeepgramClient(self.api_key)

    async def start_listening(self, audio_stream: AsyncGenerator[bytes, None]) -> AsyncGenerator[str, None]:
        """
        Connects to Deepgram WebSocket. Pipes audio in, yields final transcripts out.
        """
        # A queue to bridge the callback-based Deepgram client with this generator
        transcript_queue = asyncio.Queue()

        # Connect to Deepgram Live
        dg_connection = self.dg_client.listen.asyncwebsocket.v("1")

        async def on_message(self, result, **kwargs):
            sentence = result.channel.alternatives[0].transcript
            if len(sentence) == 0:
                return
            if result.is_final:
                await transcript_queue.put(sentence)

        async def on_error(self, error, **kwargs):
            logger.error(f"Deepgram Error: {error}")

        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        dg_connection.on(LiveTranscriptionEvents.Error, on_error)

        options = LiveOptions(
            model="nova-2", 
            language="ur", # Supports Urdu and English mixed (UrduLish)
            smart_format=True,
            endpointing=300 # 300ms of silence triggers endpointing
        )
        
        await dg_connection.start(options)

        # Task to feed audio into Deepgram
        async def feed_audio():
            try:
                async for chunk in audio_stream:
                    await dg_connection.send(chunk)
            except Exception as e:
                logger.error(f"Error feeding audio to Deepgram: {e}")
            finally:
                await dg_connection.finish()

        feed_task = asyncio.create_task(feed_audio())

        # Yield transcripts from the queue
        try:
            while not feed_task.done() or not transcript_queue.empty():
                try:
                    # Wait for a short time to allow checking if feed_task is done
                    transcript = await asyncio.wait_for(transcript_queue.get(), timeout=0.1)
                    yield transcript
                except asyncio.TimeoutError:
                    continue
        except Exception as e:
            logger.error(f"STT Yield Error: {e}")
        finally:
            feed_task.cancel()
