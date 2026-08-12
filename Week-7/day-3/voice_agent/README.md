# Production Real Estate Voice Agent (Week 7 Day 3)

This repository contains a production-grade, low-latency streaming AI voice agent tailored for the Pakistani real estate market. 

## Architecture
- **Voice In**: Streaming STT via Deepgram with VAD.
- **Brain**: Async OpenAI (gpt-4o-mini) token streaming.
- **Voice Out**: Streaming TTS via Fish Audio.
- **Memory**: Context persistence (short/long term).

## Setup
1. `pip install -r requirements.txt`
2. Set environment variables (`OPENAI_API_KEY`, `DEEPGRAM_API_KEY`, `FISH_AUDIO_API_KEY`).
3. Run the server: `uvicorn src.main:app --reload`

## Docker Deployment
```bash
docker-compose up --build
```
