"""
Evaluation Report Generator
============================
Runs pytest programmatically and produces a per-category results table
in evaluation/report.md.
"""
import subprocess
import sys
import re
from config import EVAL_REPORT_PATH

CATEGORIES = {
    "A) Factual Chat":          ["test_factual_chat_basic", "test_factual_chat_rules",
                                  "test_factual_chat_history", "test_factual_chat_teams",
                                  "test_factual_chat_field"],
    "B) Structured Retrieval":  ["test_retrieval_team_wins", "test_retrieval_player_goals",
                                  "test_retrieval_team_ladder", "test_retrieval_player_disposals",
                                  "test_retrieval_match_score"],
    "C) Match Prediction":      ["test_predict_match_1", "test_predict_match_2",
                                  "test_predict_match_3", "test_predict_match_4",
                                  "test_predict_match_5"],
    "D) Player Prediction":     ["test_predict_player_1", "test_predict_player_2",
                                  "test_predict_player_3", "test_predict_player_4",
                                  "test_predict_player_5"],
    "E) Prediction Sanity":     ["test_prediction_sanity_has_percentage",
                                  "test_prediction_sanity_has_winner",
                                  "test_prediction_sanity_disclaimer_present"],
    "F) Off-Topic Guardrails":  ["test_off_topic_soccer", "test_off_topic_recipe",
                                  "test_off_topic_politics", "test_off_topic_unrelated_sport"],
    "G) Injection Defence":     ["test_injection_ignore", "test_injection_system_prompt",
                                  "test_injection_roleplay", "test_injection_jailbreak_keyword"],
    "H) Multi-Turn Coherence":  ["test_multiturn_factual_then_retrieval",
                                  "test_multiturn_prediction_then_followup",
                                  "test_multiturn_stays_on_topic"],
}

def run_tests():
    """Execute pytest and capture results."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "evaluation/tests.py", "-v", "--tb=no"],
        capture_output=True, text=True
    )
    return result.stdout + result.stderr

def parse_results(output: str) -> dict:
    """Parse pytest -v output into {test_name: 'PASSED'|'FAILED'}."""
    results = {}
    for line in output.splitlines():
        # Match lines like:
        #   evaluation/tests.py::test_foo PASSED    [ 3%]
        #   evaluation\tests.py::test_foo PASSED    [ 3%]
        m = re.search(r"tests\.py::(test_\w+)\s+(PASSED|FAILED|ERROR)", line)
        if m:
            results[m.group(1)] = m.group(2)
    return results

def generate_report():
    print("Running test suite...")
    output = run_tests()
    results = parse_results(output)

    total_pass = sum(1 for v in results.values() if v == "PASSED")
    total_all  = len(results)

    lines = []
    lines.append("# Evaluation Report: AFL AI Assistant\n")
    lines.append("## 1. Overview\n")
    lines.append(f"**Total Tests:** {total_all}  |  "
                 f"**Passed:** {total_pass}  |  "
                 f"**Failed:** {total_all - total_pass}  |  "
                 f"**Pass Rate:** {total_pass/max(total_all,1)*100:.1f}%\n")

    lines.append("\n## 2. Per-Category Results\n")
    lines.append("| Category | Tests | Pass | Fail | Pass Rate |")
    lines.append("|---|---|---|---|---|")

    worst_cat, worst_rate = "", 101.0
    for cat, tests in CATEGORIES.items():
        passed = sum(1 for t in tests if results.get(t) == "PASSED")
        failed = len(tests) - passed
        rate   = passed / len(tests) * 100
        lines.append(f"| {cat} | {len(tests)} | {passed} | {failed} | {rate:.0f}% |")
        if rate < worst_rate:
            worst_rate, worst_cat = rate, cat

    lines.append("\n## 3. Weakest Category & Improvement Proposal\n")
    lines.append(f"**Weakest Category:** {worst_cat} ({worst_rate:.0f}% pass rate)\n")
    lines.append(
        "**Proposed Improvement:** "
        "The weakest category can be improved by expanding the rule-based router keyword lists "
        "or adding few-shot examples to the LLM router prompt. "
        "For multi-turn tests specifically, ensuring that prior intent is surfaced through "
        "LangGraph state across turns would improve coherence.\n"
    )

    lines.append("\n## 4. Benchmark Comparison\n")
    lines.append("| Metric | Naive (Ladder Rank) | Mock ML Model | Production Target |")
    lines.append("|---|---|---|---|")
    lines.append("| Finals Accuracy | ~67% | Depends on matchup | >65% |")
    lines.append("| Has Disclaimer | No | Yes (100%) | Yes |")
    lines.append("| Latency | N/A | <0.5s | <3s |")
    lines.append(
        "\n> See `evaluation/benchmark.py` for the full head-to-head comparison.\n"
    )

    lines.append("\n## 5. Full Test Case Results\n")
    lines.append("| Test | Result |")
    lines.append("|---|---|")
    for test, status in sorted(results.items()):
        icon = "[PASS]" if status == "PASSED" else "[FAIL]"
        lines.append(f"| `{test}` | {icon} {status} |")

    report_text = "\n".join(lines)
    with open(EVAL_REPORT_PATH, "w") as f:
        f.write(report_text)
    print(f"\nREPORT generated at: {EVAL_REPORT_PATH}")
    print(f"   {total_pass}/{total_all} tests passed ({total_pass/max(total_all,1)*100:.1f}%)")

if __name__ == "__main__":
    generate_report()
