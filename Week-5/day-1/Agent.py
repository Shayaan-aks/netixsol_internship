"""
Agent.py — Minimal raw-Python ReAct Agent using the Anthropic API
Week 5 Day 1: Agent Foundations

Architecture: LLM-in-a-loop
  send message
      └─> check response
            ├─ tool_use blocks found → execute tool → append result → repeat
            └─ final text block     → print answer → done

No LangChain, no LangGraph. Just anthropic + while-loop.
"""

import os
import json
import time
import textwrap
from typing import Optional

import anthropic
from dotenv import load_dotenv

# Load ANTHROPIC_API_KEY from .env if present
load_dotenv()

from Tools import TOOL_SCHEMAS, execute_tool  # noqa: E402  (local module)


# ─────────────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────────────
MODEL             = "claude-3-5-haiku-20241022"   # fast + cheap for demos
MAX_TOKENS        = 1024
MAX_ITERATIONS    = 10          # safeguard against infinite loops
DEFAULT_SYSTEM    = textwrap.dedent("""\
    You are a helpful assistant with access to tools for calculation,
    weather lookup, file reading, and unit conversion. Think step-by-step.
    When a tool call is needed, call exactly ONE tool at a time and wait
    for the result before deciding what to do next. When you have enough
    information to answer the user, respond with a clear final text answer.
""")


# ─────────────────────────────────────────────────────────────────────────────
# Logging helpers
# ─────────────────────────────────────────────────────────────────────────────
CYAN    = "\033[96m"
YELLOW  = "\033[93m"
GREEN   = "\033[92m"
RED     = "\033[91m"
RESET   = "\033[0m"
BOLD    = "\033[1m"


def log_step(step: int, title: str, body: str = "", color: str = CYAN) -> None:
    """Print a single agent step to stdout (becomes your debugging habit)."""
    bar = "─" * 60
    print(f"\n{color}{BOLD}[Step {step}] {title}{RESET}")
    if body:
        for line in body.splitlines():
            print(f"  {line}")
    print(f"{color}{bar}{RESET}")


def log_tool_call(tool_name: str, tool_input: dict) -> None:
    print(f"\n{YELLOW}  ▶ TOOL CALL: {tool_name}{RESET}")
    print(f"    Input: {json.dumps(tool_input, ensure_ascii=False)}")


def log_observation(tool_name: str, result: str) -> None:
    print(f"\n{GREEN}  ◀ OBSERVATION from {tool_name}:{RESET}")
    print(f"    {result}")


def log_final(answer: str) -> None:
    print(f"\n{GREEN}{BOLD}{'═'*60}")
    print("FINAL ANSWER")
    print('═'*60 + RESET)
    print(answer)
    print(f"{GREEN}{'═'*60}{RESET}\n")


def log_error(msg: str) -> None:
    print(f"\n{RED}{BOLD}[ERROR] {msg}{RESET}\n")


# ─────────────────────────────────────────────────────────────────────────────
# Core Agent
# ─────────────────────────────────────────────────────────────────────────────
class RawPythonAgent:
    """
    A minimal ReAct agent implemented as a raw Python while-loop.

    ReAct loop:
      Reason  → the model produces text (chain-of-thought)
      Act     → the model emits tool_use block(s)
      Observe → we execute the tool and append tool_result
      Repeat  → until model returns final text (no tool_use blocks)

    Memory model:
      • conversation_history (list[dict]) — the Anthropic messages list.
        This IS the agent's memory. Every turn is appended so the model
        always sees the full conversation context.
      • working_state (dict) — a simple scratchpad the *agent code* tracks:
        iterations, tool calls made, errors seen. The model doesn't read
        this directly, but it's logged for the developer.
    """

    def __init__(
        self,
        api_key:       Optional[str] = None,
        model:         str           = MODEL,
        max_tokens:    int           = MAX_TOKENS,
        max_iterations:int           = MAX_ITERATIONS,
        system_prompt: str           = DEFAULT_SYSTEM,
    ):
        key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise ValueError(
                "No API key found. Set ANTHROPIC_API_KEY environment variable "
                "or pass api_key= to RawPythonAgent()."
            )

        self.client         = anthropic.Anthropic(api_key=key)
        self.model          = model
        self.max_tokens     = max_tokens
        self.max_iterations = max_iterations
        self.system_prompt  = system_prompt

        # ── Memory ────────────────────────────────────────────────────────────
        # Conversation memory: full list of messages sent to the API
        self.conversation_history: list[dict] = []

        # Working state: agent-level scratchpad (not sent to LLM)
        self.working_state: dict = {}

    def _reset_working_state(self, user_query: str) -> None:
        """Reset scratchpad for a new task."""
        self.working_state = {
            "user_query":    user_query,
            "iteration":     0,
            "tools_called":  [],
            "errors":        [],
            "start_time":    time.time(),
        }

    def _call_llm(self) -> anthropic.types.Message:
        """Send the current conversation history to the API."""
        return self.client.messages.create(
            model       = self.model,
            max_tokens  = self.max_tokens,
            system      = self.system_prompt,
            tools       = TOOL_SCHEMAS,
            messages    = self.conversation_history,
        )

    def _extract_text(self, response: anthropic.types.Message) -> str:
        """Pull all TextBlock content from a response."""
        return "\n".join(
            block.text
            for block in response.content
            if block.type == "text"
        )

    def _extract_tool_uses(self, response: anthropic.types.Message) -> list[dict]:
        """Return a list of {id, name, input} dicts for each ToolUseBlock."""
        return [
            {"id": block.id, "name": block.name, "input": block.input}
            for block in response.content
            if block.type == "tool_use"
        ]

    def run(self, user_query: str) -> str:
        """
        Run the ReAct loop for a user query.

        Returns the model's final text answer.
        """
        self._reset_working_state(user_query)

        # Append user message to conversation history (persistent memory)
        self.conversation_history.append({
            "role": "user",
            "content": user_query
        })

        log_step(0, f"USER QUERY", user_query, color=BOLD)

        iteration = 0
        while iteration < self.max_iterations:
            iteration += 1
            self.working_state["iteration"] = iteration

            # ── REASON: ask the model ─────────────────────────────────────────
            log_step(iteration, f"Calling {self.model}...", color=CYAN)
            response = self._call_llm()

            # Log stop reason
            stop_reason = response.stop_reason
            reasoning   = self._extract_text(response)
            tool_uses   = self._extract_tool_uses(response)

            if reasoning:
                log_step(iteration, "Model reasoning:", reasoning, color=CYAN)

            # ── Check stop_reason ─────────────────────────────────────────────
            if stop_reason == "end_turn" and not tool_uses:
                # Model gave a final answer — done!
                final_answer = reasoning
                log_final(final_answer)
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response.content
                })
                return final_answer

            if stop_reason not in ("tool_use", "end_turn"):
                log_error(f"Unexpected stop_reason: {stop_reason}. Aborting.")
                return f"[Agent stopped: unexpected stop_reason={stop_reason}]"

            if not tool_uses:
                # end_turn with no text and no tools — shouldn't happen, but handle it
                log_error("No tool_use and no text in response. Aborting.")
                return "[Agent stopped: empty response]"

            # ── ACT: execute each tool ────────────────────────────────────────
            # Append assistant response (with tool_use blocks) to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response.content
            })

            # Build tool_result blocks for every tool called this turn
            tool_result_blocks = []
            for tool_call in tool_uses:
                t_name  = tool_call["name"]
                t_input = tool_call["input"]
                t_id    = tool_call["id"]

                log_tool_call(t_name, t_input)
                self.working_state["tools_called"].append(t_name)

                # ── OBSERVE: run the tool ──────────────────────────────────────
                result = execute_tool(t_name, t_input)
                is_error = result.startswith("ERROR:")
                if is_error:
                    self.working_state["errors"].append(result)

                log_observation(t_name, result)

                tool_result_blocks.append({
                    "type":        "tool_result",
                    "tool_use_id": t_id,
                    "content":     result,
                    "is_error":    is_error,
                })

            # Append tool results as a user message (Anthropic format)
            self.conversation_history.append({
                "role": "user",
                "content": tool_result_blocks
            })

        # ── Max iterations reached ─────────────────────────────────────────────
        msg = (
            f"[Agent safeguard] Stopped after {self.max_iterations} iterations "
            f"without a final answer. "
            f"Tools called: {self.working_state['tools_called']}."
        )
        log_error(msg)
        return msg

    def run_fresh(self, user_query: str) -> str:
        """
        Run a query with a clean conversation history (single-turn task).
        Useful for isolated test cases.
        """
        self.conversation_history = []
        return self.run(user_query)

    def chat(self, user_query: str) -> str:
        """
        Multi-turn conversational mode — history persists between calls.
        """
        return self.run(user_query)

    def clear_history(self) -> None:
        """Clear conversation memory."""
        self.conversation_history = []
        print("Conversation history cleared.")


# ─────────────────────────────────────────────────────────────────────────────
# Demonstration & Failure Mode Tests
# ─────────────────────────────────────────────────────────────────────────────
def demo_basic_tool_call(agent: RawPythonAgent) -> None:
    """Task 2: single tool call + manual tool_result demonstration."""
    print(f"\n{'='*60}")
    print("DEMO 1 — Single tool call (calculator)")
    print(f"{'='*60}")
    agent.run_fresh("What is the square root of 256 plus 7 to the power of 3?")


def demo_multi_step(agent: RawPythonAgent) -> None:
    """Task 3: multi-step task requiring 2+ tool calls."""
    print(f"\n{'='*60}")
    print("DEMO 2 — Multi-step: weather comparison (2+ tool calls)")
    print(f"{'='*60}")
    agent.run_fresh(
        "Look up the current weather in Karachi and London. "
        "Which city is warmer, and by how many degrees Celsius?"
    )


def demo_calculation_chain(agent: RawPythonAgent) -> None:
    """Task 3: chained calculations."""
    print(f"\n{'='*60}")
    print("DEMO 3 — Chained tools: temperature + unit conversion")
    print(f"{'='*60}")
    agent.run_fresh(
        "What is the weather in Dubai? "
        "Then convert that temperature to Fahrenheit and also to Kelvin."
    )


def demo_multi_city_and_math(agent: RawPythonAgent) -> None:
    """Task 3: weather + math — requires 3 tool calls."""
    print(f"\n{'='*60}")
    print("DEMO 4 — 3 tool calls: 2 weather lookups + average calculation")
    print(f"{'='*60}")
    agent.run_fresh(
        "Find the temperatures in Tokyo and Sydney. "
        "Then calculate their average temperature and tell me which is warmer."
    )


def demo_failure_ambiguous(agent: RawPythonAgent) -> None:
    """Task 5: Failure Mode 1 — ambiguous request."""
    print(f"\n{'='*60}")
    print("FAILURE MODE 1 — Ambiguous request (no city specified)")
    print(f"{'='*60}")
    agent.run_fresh("What's the weather like?")


def demo_failure_tool_error(agent: RawPythonAgent) -> None:
    """Task 5: Failure Mode 2 — tool returns an error."""
    print(f"\n{'='*60}")
    print("FAILURE MODE 2 — Tool returns an error (city not in DB)")
    print(f"{'='*60}")
    agent.run_fresh("What is the weather in Narnia?")


def demo_failure_undefined_tool(agent: RawPythonAgent) -> None:
    """Task 5: Failure Mode 3 — task needs a tool we haven't defined."""
    print(f"\n{'='*60}")
    print("FAILURE MODE 3 — Task needs undefined tool (web search)")
    print(f"{'='*60}")
    agent.run_fresh(
        "Search the web for the latest news about AI regulation in 2025 "
        "and give me a 3-point summary."
    )


def demo_failure_bad_expression(agent: RawPythonAgent) -> None:
    """Task 5: Failure Mode 4 — wrong tool arguments."""
    print(f"\n{'='*60}")
    print("FAILURE MODE 4 — Invalid tool arguments (bad math expression)")
    print(f"{'='*60}")
    agent.run_fresh("Calculate the result of 'import os; os.system(\"dir\")'")


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"\n{BOLD}Week 5 Day 1 — Raw Python ReAct Agent{RESET}")
    print(f"Model: {MODEL}  |  Max iterations: {MAX_ITERATIONS}\n")

    agent = RawPythonAgent()

    # ── Task 2: single tool call ──────────────────────────────────────────────
    demo_basic_tool_call(agent)

    # ── Task 3: multi-step tasks (2+ tool calls each) ─────────────────────────
    demo_multi_step(agent)
    demo_calculation_chain(agent)
    demo_multi_city_and_math(agent)

    # ── Task 5: failure modes ─────────────────────────────────────────────────
    demo_failure_ambiguous(agent)
    demo_failure_tool_error(agent)
    demo_failure_undefined_tool(agent)
    demo_failure_bad_expression(agent)

    # Summary of working_state from last run
    print(f"\n{BOLD}Working state from last run:{RESET}")
    for k, v in agent.working_state.items():
        print(f"  {k}: {v}")
