# Week 5 Day 1 — Agent Foundations Write-up

**Author:** Shayaan  
**Date:** Week 5, Day 1  
**Stack:** Python 3.13 · Anthropic SDK 0.117.0 · No frameworks  

---

## 1. What Is an Agent?

An **agent** is an LLM placed inside a loop with access to tools. At each iteration
it reasons about what to do next, optionally calls a tool, observes the result, and
decides whether to continue or return a final answer. This makes agents fundamentally
different from:

- **Chatbots** — stateless prompt-in / text-out, no tool access
- **Workflows** — deterministic pipelines where the path is fixed at design time
- **Agents** — dynamic: the LLM decides the path at runtime based on observations

An agent is *agentic* when it exhibits four properties: **autonomy** (self-directed
action), **tool use** (external capability invocation), **multi-step planning**
(decomposing goals), and **self-correction** (adjusting based on tool results).

---

## 2. The ReAct Loop

ReAct (Reason → Act → Observe) is the core pattern of every tool-using agent:

```
User Query
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  WHILE stop_reason != 'end_turn' (text only):           │
│                                                         │
│  REASON  →  LLM reads full message history,             │
│             produces chain-of-thought text              │
│             "I need to call get_weather for Karachi..." │
│                                                         │
│  ACT     →  LLM emits tool_use block:                   │
│             {name: "get_weather", input: {city: "..."}} │
│                                                         │
│  OBSERVE →  Python executes the tool,                   │
│             appends tool_result to history,             │
│             loops back to REASON                        │
└─────────────────────────────────────────────────────────┘
    │
    ▼  stop_reason = 'end_turn', no tool_use blocks
Final text answer returned to user
```

**Safeguard:** `MAX_ITERATIONS = 10` prevents infinite loops.

---

## 3. Tool Schemas Used

Four tools were implemented, each with a JSON Schema and a Python runner:

| Tool | Purpose | Key inputs |
|---|---|---|
| `calculator` | Safe `eval()` of math expressions | `expression: str` |
| `get_weather` | Simulated city weather lookup | `city: str`, `unit: celsius\|fahrenheit` |
| `read_text_file` | Reads local .txt/.md/.py/.sql files | `filepath: str`, `max_chars: int` |
| `convert_units` | Temperature / length / weight conversions | `value`, `from_unit`, `to_unit` |

**Why descriptions matter:** Claude selects tools *exclusively* from `name` +
`description` in the schema. A vague description ("does math") causes wrong tool
selection. The `calculator` description explicitly lists supported functions
(`sqrt()`, `log()`, `pi`, etc.) so the model knows exactly when to use it.

---

## 4. Memory Architecture

| Type | Storage | Reader | Purpose |
|---|---|---|---|
| **Conversation memory** | `agent.conversation_history` (messages list) | LLM (full context) | Lets model see every past step |
| **Working memory** | `agent.working_state` (dict scratchpad) | Python agent code | Iteration tracking, error logging, guardrails |

The conversation history is the agent's *persistent* memory — the model never
"forgets" what tools it already called because every tool_result is appended to
`messages`. The working state is the developer's view of what is happening.

---

## 5. Failure Modes Observed

| # | Failure Mode | Observed Behaviour | Mitigation Applied |
|---|---|---|---|
| 1 | **Infinite loop** | Would loop forever without a safeguard | `max_iterations=10` breaks the loop and returns a clear message |
| 2 | **Hallucinated tool call** | Model invents a tool name not in schema | `execute_tool` dispatcher returns `ERROR: tool not defined`; model receives this via `tool_result` and either retries or explains the limitation |
| 3 | **Wrong tool arguments** | Missing required field, wrong type | Each runner validates inputs and returns a structured `ERROR:` string rather than raising an exception |
| 4 | **Silent tool error** | Division by zero, bad file path | All runners wrapped in `try/except`; error surfaced as `ERROR:` string with `is_error=True` in the tool_result block |
| 5 | **Ambiguous request** | "What's the weather?" — no city given | Model asked for clarification (returned `end_turn` without tool_use) — correct graceful degradation |
| 6 | **Missing tool** | Requested web search — no tool defined | Model answered from training data and acknowledged the limitation honestly |

---

## 6. Why Frameworks Exist

After building this 150-line agent by hand, the value of LangChain/LangGraph/CrewAI
becomes concrete. They package the patterns every production team re-discovers:

- **Retries + back-off** when the API rate-limits
- **Streaming** responses for better UX
- **Token counting** and context-window management
- **State persistence** across sessions (databases, Redis)
- **Human-in-the-loop** pauses for approval before sensitive actions
- **Parallel tool calls** for speed
- **Multi-agent routing** (supervisor → worker pattern)
- **Observability** (LangSmith, Phoenix traces)
- **Prompt versioning** and A/B testing

The trade-off is opacity. Knowing how the raw loop works — exactly what we built
today — means you can *debug inside the framework* when it behaves unexpectedly,
rather than treating it as an inscrutable black box. Day 1 is the foundation that
makes every framework day more productive.
