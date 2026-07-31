import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATASET_PATH = os.path.join(DATA_DIR, "afl_dataset.csv")
ARTICLES_DIR = os.path.join(DATA_DIR, "articles")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

STRUCTURED_LOG_PATH = os.path.join(LOGS_DIR, "assistant.log")
EVAL_DIR = os.path.join(BASE_DIR, "evaluation")
EVAL_REPORT_PATH = os.path.join(EVAL_DIR, "report.md")

LLM_MODEL = "gemini-3.5-flash"
TEMPERATURE = 0.0

# Ensure directories exist
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(EVAL_DIR, exist_ok=True)
os.makedirs(ARTICLES_DIR, exist_ok=True)
