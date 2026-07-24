"""
gen_nb.py — Script to generate code.ipynb and notebook.ipynb for Week 5 Day 4: CrewAI Multi-Agent Collaboration
"""
import json
import os

def code_cell(src_lines):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": src_lines
    }

def md_cell(src_lines):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": src_lines
    }

cells = []

# ── HEADER ────────────────────────────────────────────────────────────────────
cells.append(md_cell([
    "# Week 5 Day 4 — CrewAI: Multi-Agent Collaboration, Roles & Task Delegation\n",
    "\n",
    "> **Goal:** Design a specialized crew of autonomous agents with distinct roles, goals, and scoped tools\n",
    "> collaborating on a business intelligence objective using `Process.sequential` and `Process.hierarchical` delegation.\n",
    "\n",
    "**Stack:** `crewai` · `crewai-tools` · `langchain` · `pydantic` · `python-dotenv`  \n",
    "**Scenario:** Competitive Intelligence & Strategic Product Positioning Report  \n"
]))

# ── SETUP & ENV ───────────────────────────────────────────────────────────────
cells.append(md_cell(["## Setup & Environment Configuration\n"]))
cells.append(code_cell([
    "import os, sys, json, time, textwrap, warnings\n",
    "from typing import Dict, List, Any, Optional\n",
    "from dotenv import load_dotenv\n",
    "\n",
    "warnings.filterwarnings('ignore')\n",
    "load_dotenv('project.env')\n",
    "load_dotenv()\n",
    "\n",
    "print(f'Python version : {sys.version.split()[0]}')\n",
    "print(f'API key present: {bool(os.environ.get(\"OPENAI_API_KEY\") or os.environ.get(\"ANTHROPIC_API_KEY\") or os.environ.get(\"GEMINI_API_KEY\"))}')\n"
]))

# ── TASK 1: MULTI-AGENT DESIGN THINKING ───────────────────────────────────────
cells.append(md_cell([
    "---\n",
    "## Task 1: Multi-Agent Design Thinking & Role Decomposition\n",
    "\n",
    "### Business Scenario\n",
    "**Competitive Intelligence & Strategic Product Positioning** for AI Coding Assistants.\n",
    "\n",
    "### Agent Role Decomposition\n",
    "1. **Senior Competitive Intelligence Analyst (`researcher`)**\n",
    "   - **Role:** Market Intelligence Specialist\n",
    "   - **Goal:** Gather technical specs, pricing models, feature matrices, and market movements for competitors.\n",
    "   - **Backstory:** Deep software architecture background; evaluates tech specs objectively without marketing bias.\n",
    "2. **Product Strategy & Data Analyst (`analyst`)**\n",
    "   - **Role:** Data-Driven Product Strategist\n",
    "   - **Goal:** Synthesize raw research notes into quantitative feature gap matrices and SWOT scores.\n",
    "   - **Backstory:** Enterprise product background; transforms qualitative notes into structured decision tables.\n",
    "3. **Principal Marketing Strategist & Copywriter (`copywriter`)**\n",
    "   - **Role:** B2B Tech Marketing Director\n",
    "   - **Goal:** Convert SWOT matrices into executive value propositions, positioning hooks, and go-to-market briefs.\n",
    "   - **Backstory:** Expert in translating technical feature advantages into compelling executive narratives.\n",
    "\n",
    "### Why Multi-Agent Specialized Crews Outperform Generalist Agents\n",
    "Specialized agents outperform single generalists by constraining context windows, enforcing strict role personas, and preventing cognitive overload. A single generalist forced to research, analyze, and format simultaneously often produces shallow analysis or loses tone consistency. However, for simple single-turn tasks, single agents avoid multi-agent delegation latency and overhead cost.\n"
]))

# ── TASK 2 & 3: AGENTS, TOOLS & SEQUENTIAL CREW ──────────────────────────────
cells.append(md_cell([
    "---\n",
    "## Task 2 & 3: Build Agents, Scoped Tools & Sequential Execution\n"
]))

cells.append(code_cell([
    "# Define Custom Scoped Tools\n",
    "def search_competitor_data(query: str) -> str:\
",
    "    db = {\n",
    "        'cursor': 'Cursor IDE: Composer multi-file editing, codebase indexing. Pro $20/mo.',\n",
    "        'github copilot': 'GitHub Copilot: PR summaries, Workspace, enterprise IP indemnification. $19/user/mo.',\n",
    "        'augment': 'Augment Code: Remote vector server, sub-100ms multi-file inline completion. Custom pricing.'\n",
    "    }\n",
    "    return '\\n'.join([v for k, v in db.items() if k in query.lower() or 'all' in query.lower() or not query])\n",
    "\n",
    "def calculate_swot_scores(data_text: str) -> str:\n",
    "    return json.dumps({\n",
    "        'competitors': ['Cursor IDE', 'GitHub Copilot', 'Augment Code'],\n",
    "        'gap_score': 8.4,\n",
    "        'swot': {'strengths': 'Cursor UX lead', 'weaknesses': 'Copilot context limit', 'opportunity': 'Privacy-first monorepo agent'}\n",
    "    }, indent=2)\n",
    "\n",
    "def format_executive_report(title: str, body: str) -> str:\n",
    "    return f'# EXECUTIVE BRIEFING: {title.upper()}\\n\\n{body}\\n\\n*Finalized by Marketing Crew.*'\n",
    "\n",
    "print('Tools registered successfully.')\n"
]))

cells.append(code_cell([
    "# Import main execution runner from code.py\n",
    "from code import run_crewai_simulation_or_live, evaluate_runs, print_comparison_report\n",
    "\n",
    "# Run Task 3: Sequential Process Crew\n",
    "seq_results = run_crewai_simulation_or_live(process_type='sequential')\n"
]))

# ── TASK 4: HIERARCHICAL DELEGATION ──────────────────────────────────────────
cells.append(md_cell([
    "---\n",
    "## Task 4: Hierarchical Process & Manager Delegation\n"
]))

cells.append(code_cell([
    "# Run Task 4: Hierarchical Process Crew with Manager Agent\n",
    "hier_results = run_crewai_simulation_or_live(process_type='hierarchical')\n"
]))

# ── TASK 5: EVALUATION & COST ANALYSIS ───────────────────────────────────────
cells.append(md_cell([
    "---\n",
    "## Task 5: Evaluation, Cost Benchmarking & Single-Agent Comparison\n"
]))

cells.append(code_cell([
    "# Run Evaluation Scoring & Comparative Benchmark\n",
    "eval_results = evaluate_runs(seq_results, hier_results)\n",
    "print_comparison_report(seq_results, hier_results, eval_results)\n"
]))

# Build Notebook Dictionary
notebook_dict = {
    "cells": cells,
    "metadata": {
        "language_info": {"name": "python"},
        "orig_nbformat": 4
    },
    "nbformat": 4,
    "nbformat_minor": 2
}

# Write code.ipynb and notebook.ipynb
with open("code.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook_dict, f, indent=2)

with open("notebook.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook_dict, f, indent=2)

print("Generated code.ipynb and notebook.ipynb successfully.")
