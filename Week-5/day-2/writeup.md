# Week 5 Day 2 — LangChain Agent Write-up

**Author:** Shayaan  
**Date:** Week 5, Day 2  
**Stack:** LangChain 1.3.14 · langchain-anthropic 1.4.8 · Pydantic 2.13.4 · Claude claude-3-5-haiku  

---

## 1. What LangChain Automates vs Day 1

| Concern | Raw Python (Day 1) | LangChain (Day 2) |
|---|---|---|
| Tool schema | Manual JSON dict per tool | Auto-generated from `@tool` docstring |
| ReAct loop | `while` + manual history append | `AgentExecutor` handles it |
| Memory | `conversation_history` list | `RunnableWithMessageHistory` |
| Structured output | Manual JSON parsing | `.with_structured_output(PydanticModel)` |
| Error handling | `try/except` in each runner | `handle_parsing_errors=True` |
| Debug visibility | Full (your own colored logs) | `verbose=True` (framework-controlled) |

---

## 2. LCEL Pipe Syntax

The `|` operator composes `Runnable` objects into a sequential pipeline.
Each component (`PromptTemplate`, `ChatAnthropic`, `StrOutputParser`) implements a
`Runnable` interface with `invoke(input) -> output`. `A | B` creates a new `Runnable`
that calls `B.invoke(A.invoke(input))` — passing A's output as B's input.
This enables lazy evaluation, automatic streaming, and async/batch support without
any extra code from the developer.

```python
# Under the hood, this pipe:
chain = prompt | llm | StrOutputParser()
chain.invoke({"question": "..."})

# is equivalent to this raw Python:
formatted = prompt.invoke({"question": "..."})
response  = llm.invoke(formatted)
result    = StrOutputParser().invoke(response)
```

---

## 3. Tool Schemas Used

Five tools were implemented with `@tool` decorator:

| Tool | Data source | Key capability |
|---|---|---|
| `calculator` | In-memory safe eval | Safe math expression evaluation |
| `get_weather` | In-memory stub dict | City weather lookup |
| `lookup_product` | `products.json` (real file) | Product price/rating search with filtering |
| `read_product_csv` | `products.csv` (real file) | Category listing from CSV |
| `get_exchange_rate` | In-memory + simulated failure | Currency rates; fails on first call |

**Docstrings as prompts:** The `@tool` decorator extracts the function's docstring
and sets it as the `description` field in the API's tool schema. The model selects
tools *exclusively* from this description — identical to Day 1's manual JSON schemas,
but auto-generated. Poor docstrings = wrong tool selection.

---

## 4. Annotated Reasoning Trace

Below is the annotated `verbose=True` output for the 3-turn product comparison:

```
> Entering new AgentExecutor chain...

# ─── TURN 1 ────────────────────────────────────────────────────────────────

[REASON]  "The user wants the Sony WH-1000XM5 price. I'll call lookup_product."
[ACT]     Invoking: `lookup_product` with {'query': 'Sony WH-1000XM5'}
[OBSERVE] "- Sony WH-1000XM5 | $349 | Rating: 4.8/5 | Brand: Sony | Stock: 60"
[REASON]  "I have the price. Provide the answer."
ANSWER:   "The Sony WH-1000XM5 costs $349 and has a 4.8/5 rating."

# ─── TURN 2 (agent remembers Turn 1 via RunnableWithMessageHistory) ────────

[REASON]  "User wants to compare with AirPods Pro 2. I'll look that up."
[ACT]     Invoking: `lookup_product` with {'query': 'Apple AirPods Pro 2'}
[OBSERVE] "- Apple AirPods Pro 2 | $249 | Rating: 4.6/5 | Brand: Apple"
[REASON]  "Sony: 4.8, AirPods: 4.6. Sony wins on rating."
ANSWER:   "Sony WH-1000XM5 (4.8/5) has a better rating than AirPods Pro 2 (4.6/5)."

# ─── TURN 3 (uses full context: price from T1, rating from T2) ─────────────

[REASON]  "Budget-conscious client + good quality. AirPods $249 vs Sony $349.
           AirPods has 4.6 rating and saves $100. Recommend AirPods."
ANSWER:   "For a budget-conscious client wanting quality, I recommend the
           Apple AirPods Pro 2 ($249, 4.6/5) — it saves $100 vs Sony while
           still delivering excellent sound quality."
```

**vs Day 1:** The loop structure is identical. What's hidden: the `messages.create()`
API call, the `tool_use` block extraction, the `tool_result` append, and the
`stop_reason` check. LangChain does all of this inside `AgentExecutor.__call__`.

---

## 5. Structured Output

Using `llm.with_structured_output(ProductRecommendation)` the agent returns a
validated Pydantic model instead of raw text:

```python
recommendation.product_name  # "MacBook Air M3"
recommendation.price_usd     # 1299.0
recommendation.verdict       # "Recommended"
recommendation.pros          # ["Best-in-class performance", ...]
```

Under the hood LangChain injects the Pydantic JSON schema into the prompt and
parses the model's JSON output — the same thing you'd do manually with `json.loads()`
and `Model.model_validate()`, just abstracted away.

---

## 6. Error Handling

The `get_exchange_rate` tool raises `ConnectionError` on its first call (simulated
transient failure). With `handle_parsing_errors=True`, `AgentExecutor`:
1. Catches the exception
2. Converts it to a tool observation string: `"ConnectionError: API timeout..."`
3. Adds it to the agent's context so the model can decide to retry
4. The model retries the same tool call — succeeds on the second attempt

Without `handle_parsing_errors=True`, the exception propagates and the whole
`agent_executor.invoke()` call crashes.

---

## 7. Abstraction Leakiness Observed

- **Silent key mismatches:** `RunnableWithMessageHistory` requires `input_messages_key`,
  `history_messages_key`, and `output_messages_key` to match prompt variable names exactly.
  Wrong names cause confusing `KeyError` at runtime, not at definition time.
- **LCEL type errors:** The `|` pipe looks elegant but type mismatches between components
  only surface at `invoke()` time — no static type checking at chain construction.
- **`handle_parsing_errors` swallows silently:** Tool exceptions become observations,
  which is good for recovery but makes debugging harder — you must check verbose output
  to see what failed.
- **Version fragility:** LangChain's API has changed significantly across minor versions;
  patterns from tutorials 6 months ago may not work with `1.3.x`.

**Conclusion:** LangChain dramatically reduces boilerplate for standard patterns.
Knowing the raw Day 1 loop makes you a far more effective LangChain developer —
you know exactly what `AgentExecutor` is doing inside the black box when something
goes wrong.
