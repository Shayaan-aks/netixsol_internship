# AFL AI System - LangGraph Integration

An industry-grade, LangGraph-orchestrated AI Assistant designed specifically for the Australian Football League (AFL). It demonstrates state-of-the-art routing, retrieval, ML predictions, and validation.

## Architecture

This project is built using **LangGraph** to model the conversation and execution as a state machine.

### Flow
1. **Router Node**: An LLM-based intent classifier evaluates the user query and conversational history, assigning it to one of multiple paths (`structured_retrieval`, `semantic_retrieval`, `match_prediction`, `player_prediction`, `off_topic`, `factual_chat`).
2. **Action Nodes**: Based on the route, specialized tools are invoked.
   - **Predictions**: Wrappers around ML models return probabilities and feature importances with mandatory disclaimers.
   - **Retrieval**: Exact lookups via Pandas prevent statistical hallucinations. Semantic lookups via ChromaDB provide qualitative context.
3. **Validation Node**: Checks if the tool successfully fetched data or generated a prediction. If it fails, the state transitions to a fallback formatter.
4. **Clarification Node**: Handles ambiguous queries (e.g., unresolved pronouns without history).
5. **Formatter Node**: Synthesizes the raw tool output into a professional, grounded response.

## Project Structure
- `graph/`: LangGraph definition (nodes, edges, router, state).
- `prediction/`: ML model wrappers and feature explainers.
- `retrieval/`: Structured and semantic search mechanisms.
- `tools/`: LangChain `@tool` definitions.
- `validation/`: Output validation and ambiguity checks.
- `memory/`: Checkpointer for multi-turn conversations.
- `evaluation/`: Scripts for evaluating routing accuracy and full conversations.
- `app.py`: CLI entry point.

## Installation & Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure environment variables in `.env`:
   ```env
   OPENAI_API_KEY=your_key_here
   ```
3. Run the interactive agent:
   ```bash
   python app.py
   ```

## Evaluation

Run routing accuracy tests:
```bash
python evaluation/routing_tests.py
```

Run end-to-end conversation simulations:
```bash
python evaluation/conversations.py
```
Outputs are logged to `evaluation/report.md`.
