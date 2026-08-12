import os
from dotenv import load_dotenv

load_dotenv()

# ── OpenRouter (OpenAI-compatible) ──────────────────────────────────────────
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Keep GOOGLE_API_KEY for backwards-compat (set to None if not present)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATASET_PATH = os.path.join(DATA_DIR, "afl_dataset.csv")
ARTICLES_DIR = os.path.join(DATA_DIR, "articles")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

STRUCTURED_LOG_PATH = os.path.join(LOGS_DIR, "assistant.log")
EVAL_DIR = os.path.join(BASE_DIR, "evaluation")
EVAL_REPORT_PATH = os.path.join(EVAL_DIR, "report.md")

# Model on OpenRouter (using working free model)
LLM_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"
TEMPERATURE = 0.0

# Ensure directories exist
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(EVAL_DIR, exist_ok=True)
os.makedirs(ARTICLES_DIR, exist_ok=True)
