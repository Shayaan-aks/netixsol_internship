# AFL Conversational AI Assistant

A production-quality, domain-scoped conversational agent built with LangChain, LangGraph, and OpenAI that strictly answers questions about the Australian Football League (AFL).

## Architecture

This project implements a Retrieval-Augmented Generation (RAG) architecture tailored for factual grounding and domain restriction.
- **Agent Framework:** LangGraph for state management, memory, and tool routing.
- **LLM:** `ChatOpenAI` wrapper.
- **Retrieval Layer:**
  - **Structured Retrieval:** Uses pandas on a CSV dataset for numeric statistics. This prevents hallucination by enforcing exact data lookups.
  - **Semantic Retrieval:** Uses ChromaDB and embeddings for narrative articles and news.
- **Guardrails:** System prompt engineering restricts answers strictly to AFL, incorporating multiple refusal templates for adversarial or out-of-scope prompts.
- **Grounding & Logging:** Every tool call logs the question, the retrieved data, and the status to `logs/retrieval_logs.txt`.

## Project Structure

- `app.py`: The main CLI entry point.
- `config.py`: Configuration and environment variables.
- `prompts/`: System prompt definitions.
- `data/`: Sample dataset and semantic articles.
- `retrieval/`: Logic for structured and semantic retrieval.
- `tools/`: LangChain tools (`@tool`) mapped to retrieval methods.
- `chains/`: LangGraph definition linking LLM, memory, and tools.
- `memory/`: Conversation state definition.
- `utils/`: Helper functions including fuzzy matching and logging.
- `evaluation/`: Test cases and evaluation script.

## Setup & Running

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Configure Environment:**
   Rename `.env.example` to `.env` and insert your OpenAI API Key.
   ```
   OPENAI_API_KEY=your_key_here
   ```
3. **Run the Agent:**
   ```bash
   python app.py
   ```

## Evaluation

An evaluation framework is included with 20 test cases spanning statistics, rules, comparisons, off-topic, and adversarial prompts.
Run the evaluation suite:
```bash
python evaluation/evaluation.py
```
This generates an `evaluation/report.md` detailing the performance.
