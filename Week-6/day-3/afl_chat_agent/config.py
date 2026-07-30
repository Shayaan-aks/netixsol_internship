import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Data Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATASET_PATH = os.path.join(DATA_DIR, "afl_dataset.csv")
ARTICLES_DIR = os.path.join(DATA_DIR, "articles")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
RETRIEVAL_LOG_PATH = os.path.join(LOGS_DIR, "retrieval_logs.txt")
EVAL_DIR = os.path.join(BASE_DIR, "evaluation")
EVAL_REPORT_PATH = os.path.join(EVAL_DIR, "report.md")

# Model config
LLM_MODEL = "gpt-4o-mini"
TEMPERATURE = 0.0

# Ensure directories exist
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(EVAL_DIR, exist_ok=True)
