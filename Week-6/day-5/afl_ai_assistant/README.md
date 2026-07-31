# AFL AI Assistant (Capstone Project)

A production-ready conversational AI assistant dedicated to the Australian Football League (AFL). Built with LangGraph, FastAPI, and Streamlit.

## Features
- **Intelligent Routing**: LangGraph router directs queries to factual chat, structured retrieval, or ML prediction.
- **Retrieval-Augmented Generation (RAG)**: Prevents hallucinations by grounding answers in a structured dataset.
- **Robust Guardrails**: Actively detects and blocks prompt injections and off-topic queries.
- **API First**: Exposes a clean REST API via FastAPI.
- **Interactive UI**: Streamlit frontend for seamless chatting.

## Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configuration**
   Copy `.env.example` to `.env` and add your OpenAI API key.
   ```bash
   cp .env.example .env
   ```

3. **Run the Backend (FastAPI)**
   ```bash
   set PYTHONPATH=.
   uvicorn api.main:app --reload
   ```

4. **Run the Frontend (Streamlit)**
   ```bash
   set PYTHONPATH=.
   streamlit run ui/streamlit_app.py
   ```

## Evaluation
Run the test suite to verify routing, retrieval, and guardrails:
```bash
set PYTHONPATH=.
pytest evaluation/tests.py
python evaluation/report.py
```

## Documentation
- `docs/executive_report.md`: High-level project summary.
- `docs/monitoring_plan.md`: Operations and maintenance guidelines.
- `docs/presentation.md`: Slide outline and demo script.
