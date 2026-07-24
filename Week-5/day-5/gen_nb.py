"""
gen_nb.py — Script to generate code.ipynb and notebook.ipynb for Week 5 Day 5 Capstone
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
    "# Week 5 Day 5 Capstone — Production-Ready Agent System, Evaluation & Deployment\n",
    "\n",
    "> **Goal:** Design, implement, evaluate, and package an end-to-end multi-agent client onboarding system\n",
    "> using a Hybrid Architecture (LangGraph + CrewAI + FastAPI).\n",
    "\n",
    "**Stack:** `langgraph` · `crewai` · `fastapi` · `pydantic` · `reportlab` · `python-dotenv`  \n",
    "**Scenario:** Enterprise Client Onboarding & Proposal Generation System  \n"
]))

# ── SETUP & ENV ───────────────────────────────────────────────────────────────
cells.append(md_cell(["## Setup & Environment Configuration\n"]))
cells.append(code_cell([
    "import os, sys, json, time, textwrap, warnings\n",
    "from typing import Dict, List, Any, Optional, TypedDict\n",
    "from dotenv import load_dotenv\n",
    "\n",
    "warnings.filterwarnings('ignore')\n",
    "load_dotenv('project.env')\n",
    "load_dotenv()\n",
    "\n",
    "print(f'Python version : {sys.version.split()[0]}')\n",
    "print(f'API Key present: {bool(os.environ.get(\"OPENAI_API_KEY\") or os.environ.get(\"ANTHROPIC_API_KEY\") or os.environ.get(\"GEMINI_API_KEY\"))}')\n"
]))

# ── TASK 1: SYSTEM DESIGN ─────────────────────────────────────────────────────
cells.append(md_cell([
    "---\n",
    "## Task 1: System Design & Architecture Rationale\n",
    "\n",
    "### Business Scenario\n",
    "**Autonomous Enterprise Client Onboarding & Proposal Generation System**.\n",
    "\n",
    "### Hybrid Framework Architecture\n",
    "- **LangGraph:** Orchestrates global state transitions, quality audit self-correction loops, and Human-in-the-Loop (HITL) approval checkpoints.\n",
    "- **CrewAI:** Embeds a 3-agent sub-crew (`Client Analyst`, `Technical Architect`, `Commercial Estimator`) to formulate scope and pricing without role dilution.\n",
    "- **FastAPI Layer:** Wraps the engine behind production REST endpoints with telemetry metrics.\n"
]))

# ── TASK 2: SYSTEM IMPLEMENTATION ─────────────────────────────────────────────
cells.append(md_cell([
    "---\n",
    "## Task 2: Build the End-to-End System\n"
]))

cells.append(code_cell([
    "# Import core engine runner from agent_engine.py\n",
    "from agent_engine import build_onboarding_graph, run_capstone_evaluation, print_evaluation_summary_table\n",
    "\n",
    "# Instantiate Onboarding Graph\n",
    "graph = build_onboarding_graph()\n",
    "print('Onboarding Graph compiled successfully.')\n"
]))

# ── TASK 3: EVALUATION FRAMEWORK ──────────────────────────────────────────────
cells.append(md_cell([
    "---\n",
    "## Task 3: Evaluation Suite (8 Test Cases Benchmark)\n"
]))

cells.append(code_cell([
    "# Run Capstone Evaluation Benchmark Suite\n",
    "eval_results = run_capstone_evaluation()\n",
    "print_evaluation_summary_table(eval_results)\n"
]))

# ── TASK 4: FASTAPI & MONITORING ──────────────────────────────────────────────
cells.append(md_cell([
    "---\n",
    "## Task 4: FastAPI Endpoint & Production Monitoring\n"
]))

cells.append(code_cell([
    "# Import FastAPI app & telemetry store\n",
    "from app import app, METRICS_STORE\n",
    "\n",
    "print('FastAPI app endpoints registered:')\n",
    "for route in app.routes:\n",
    "    if hasattr(route, 'path'):\n",
    "        print(f'  • {route.path}')\n"
]))

# ── TASK 5: REPORT & PRESENTATION ─────────────────────────────────────────────
cells.append(md_cell([
    "---\n",
    "## Task 5: Executive PDF Report & Presentation Outline\n"
]))

cells.append(code_cell([
    "# Run PDF Report Generator\n",
    "from generate_pdf_report import generate_pdf\n",
    "generate_pdf()\n"
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
