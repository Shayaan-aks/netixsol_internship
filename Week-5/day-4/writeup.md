# Week 5 Day 4 — CrewAI: Multi-Agent Collaboration, Roles & Task Delegation

**Author:** Shayaan  
**Date:** Week 5, Day 4  
**Stack:** Python 3.13 · CrewAI 1.15.5 · CrewAI Tools · Pydantic · LiteLLM  

---

## Task 1: Multi-Agent Design Thinking

### Business Task Selection
**Business Scenario:** *Competitive Intelligence & Strategic Product Positioning Report*  
A tech firm needs to perform competitive research on top AI Coding Assistants (Cursor IDE, GitHub Copilot, Augment Code), analyze feature matrices and quantitative SWOT gap scores, and draft an executive go-to-market briefing for leadership.

### Agent Decomposition (Roles, Goals, and Backstories)

| Agent Role | Goal | Backstory |
|---|---|---|
| **Senior Competitive Intelligence Analyst** (`researcher`) | Gather comprehensive technical specs, pricing models, feature matrices, and recent market movements for target AI coding assistants. | Experienced market intelligence analyst with a background in software architecture. Evaluates competitive landscapes objectively without bias, focusing on technical specs, pricing structures, and developer UX. |
| **Product Strategy & Data Analyst** (`analyst`) | Synthesize raw research notes into structured feature gap matrices, quantitative SWOT analysis, and strategic positioning gaps. | Data-driven product strategist with enterprise software experience. Specializes in transforming messy qualitative research into clear, structured decision matrices and gap scores. |
| **Principal Marketing Strategist & Copywriter** (`copywriter`) | Draft compelling value propositions, positioning hooks, competitive differentiation messaging, and an executive briefing for leadership. | Veteran B2B tech marketing director known for converting technical feature matrices and SWOT scores into sharp executive messaging, category-defining hooks, and actionable go-to-market strategies. |

### Rationale: Specialized Multi-Agent Crew vs. Single Generalist
> **Why Multi-Agent Outperforms:** Specialized agents outperform a single generalist because breaking a complex task into discrete personas prevents context overload, minimizes prompt interference, and enforces domain-specific reasoning (e.g., preventing marketing hype during raw data gathering). Each agent operates with scoped tools and focused system instructions tailored to its core competency.
> 
> **Where Multi-Agent Fails / Isn't True:** For simple, single-turn, or strictly linear Q&A tasks, a multi-agent setup introduces unnecessary execution latency, token inflation, delegation overhead, and inter-agent formatting failure risks compared to a single, well-crafted system prompt.

---

## Task 2: Build Agents & Assign Tools

### Scoped Tool Matrix & Justification

| Agent | Assigned Tool(s) | Tool Description | Tool Access Justification |
|---|---|---|---|
| **`researcher`** | `Search Competitor Market Data` | Custom search tool querying technical capabilities, pricing, and feature specs of target competitors. | Keeps raw search retrieval isolated to the researcher. Prevents downstream agents from spending tokens on raw data fetching. |
| **`analyst`** | `Calculate SWOT Metrics` | Analytical calculator tool processing qualitative notes into structured JSON feature matrices and SWOT scores. | Ensures analytical scoring relies on structured mathematical calculation rather than ungrounded LLM guessing. |
| **`copywriter`** | `Format Executive Report` | Markdown report formatter wrapping marketing recommendations into structured executive templates. | Ensures final output adheres strictly to executive documentation standards without altering underlying data scores. |

> **Principle of Least Privilege:** Tools are restricted to role-appropriate agents. Giving all tools to all agents increases prompt token overhead by up to 40% and leads to tool selection confusion during agent execution.

---

## Task 3: Define Tasks & Sequential Process

### Task Objects & Dependency Pipeline

```python
task_research = Task(
    description="Perform deep-dive competitive research query on AI Coding Assistants...",
    expected_output="Structured research brief with technical specs, pricing, and capabilities.",
    agent=researcher
)

task_analysis = Task(
    description="Analyze the research brief. Compute feature gap matrix & SWOT scores...",
    expected_output="JSON-formatted SWOT evaluation matrix and feature gap analysis.",
    agent=analyst,
    context=[task_research]  # Explicit context dependency
)

task_copywriting = Task(
    description="Review SWOT matrix. Draft executive briefing report...",
    expected_output="Polished Markdown briefing document formatted for executive review.",
    agent=copywriter,
    context=[task_analysis]  # Explicit context dependency
)
```

### Sequential Execution Log & Format Mismatch Case Study

During early sequential test runs, an **Output Format Mismatch** occurred:
- **The Issue:** The `researcher` agent produced verbose, conversational narrative text. When passed to the `analyst` agent, the analytical parser failed to extract numerical ratings because the text lacked key-value boundaries, causing the analyst to return zeroed gap scores.
- **The Prompt / `expected_output` Fix:** 
  1. Updated `task_research.expected_output` to explicitly require a bulleted key-value specification for each competitor.
  2. Updated `task_analysis.description` to state: *"Parse the key-value technical specs from the research context. Convert each spec into an explicit 1-10 numerical score in JSON format."*

---

## Task 4: Hierarchical Delegation & Comparative Analysis

### Manager Agent Architecture
In `Process.hierarchical`, a **Chief Strategy Officer & Operations Director** (`manager_agent`) acts as an executive controller that dynamically plans execution, delegates tasks to sub-agents, audits interim deliverables, and requests revisions before finalizing output.

```
                      ┌─────────────────────────┐
                      │      Manager Agent      │
                      │ (Chief Strategy Officer)│
                      └────────────┬────────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         │ Delegate                │ Delegate                │ Delegate
         ▼                         ▼                         ▼
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│ Market Researcher│      │ Product Analyst  │      │ Copywriter Agent │
└──────────────────┘      └──────────────────┘      └──────────────────┘
```

### Process Comparison Table: Sequential vs. Hierarchical

| Dimension | `Process.sequential` | `Process.hierarchical` |
|---|---|---|
| **Pros** | Fast execution, predictable token usage, deterministic task flow. | Self-auditing quality control, dynamic task delegation, automatically catches sub-agent errors. |
| **Cons** | Rigid; if early agent output is flawed, downstream errors cascade. | ~50% higher token cost, increased execution latency, potential manager loop stalling. |
| **When to Use** | Fixed linear pipelines (Data Ingestion -> Processing -> Formatting). | Complex, open-ended tasks requiring dynamic strategy, QA reviews, or multi-department oversight. |

---

## Task 5: Evaluation & Cost Awareness

### Token Usage & Cost Log

| Execution Run | Process Type | Prompt Tokens | Completion Tokens | Total Tokens | Estimated Cost (USD)* | Average Score |
|---|---|---|---|---|---|---|
| **Run 1** | `Process.sequential` | 1,520 | 610 | 2,130 | $0.000594 | **8.83 / 10** |
| **Run 2** | `Process.sequential` (Variant) | 1,480 | 607 | 2,087 | $0.000582 | **8.80 / 10** |
| **Run 3** | `Process.hierarchical` | 2,380 | 940 | 3,320 | $0.000921 | **9.50 / 10** |
| **Single-Agent** | LangGraph (Day 3 Ref) | 720 | 260 | 980 | $0.000222 | **8.10 / 10** |

*\*Pricing model based on fast LLM rates ($0.15/1M input tokens, $0.60/1M output tokens).*

### Evaluation Rubric & Manual Scoring (3 Criteria)

1. **Factual Grounding (0–10):** Accuracy and strict adherence to retrieved competitor specs.
2. **Analytical Completeness (0–10):** Depth of SWOT coverage and numerical gap matrix rigor.
3. **Executive Tone & Readability (0–10):** Professional structure, positioning sharpness, and formatting.

| Run ID | Factual Grounding | Analytical Completeness | Executive Tone | Composite Average |
|---|---|---|---|---|
| **Run 1 (Sequential)** | 9.0 / 10 | 8.5 / 10 | 9.0 / 10 | **8.83 / 10** |
| **Run 2 (Sequential)** | 8.8 / 10 | 8.7 / 10 | 8.9 / 10 | **8.80 / 10** |
| **Run 3 (Hierarchical)**| 9.5 / 10 | 9.5 / 10 | 9.5 / 10 | **9.50 / 10** |

---

## Final Evaluation: Was Multi-Agent Worth the Complexity?

For this specific competitive intelligence task, **a multi-agent crew was unequivocally worth the added complexity and modest token cost**. While a single-agent LangGraph setup costs ~60% less ($0.000222 vs. $0.000594), its output lacked deep quantitative SWOT scoring and blended research notes directly into marketing copy. In contrast, the CrewAI multi-agent system enforced strict separation of concerns—enabling the analyst to generate rigorous numerical matrices before the copywriter crafted executive positioning hooks. The hierarchical manager further elevated output quality to **9.5/10** by catching missing monorepo privacy specs, proving that multi-agent delegation is indispensable for high-stakes business intelligence workflows.
