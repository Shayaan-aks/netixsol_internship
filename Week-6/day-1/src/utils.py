"""
utils.py — Helper utilities, logging setup, directory creation, and I/O handlers
Week 6 Day 1: AFL Data Foundations Project
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd

from .config import (
    DATA_RAW_DIR, DATA_PROCESSED_DIR, DATA_FEATURES_DIR, DATA_METADATA_DIR,
    OUTPUTS_FIGURES_DIR, OUTPUTS_REPORTS_DIR, NOTEBOOKS_DIR
)


def setup_logger(name: str = "afl_logger", level: int = logging.INFO) -> logging.Logger:
    """Configures and returns a standardized logger."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger


def ensure_directories() -> None:
    """Ensures all required project directories exist."""
    dirs = [
        DATA_RAW_DIR, DATA_PROCESSED_DIR, DATA_FEATURES_DIR, DATA_METADATA_DIR,
        OUTPUTS_FIGURES_DIR, OUTPUTS_REPORTS_DIR, NOTEBOOKS_DIR
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def save_dataframe(df: pd.DataFrame, filepath: Path, index: bool = False) -> None:
    """Saves a DataFrame to Parquet or CSV based on file extension."""
    filepath = Path(filepath)
    os.makedirs(filepath.parent, exist_ok=True)
    
    if filepath.suffix == '.parquet':
        df.to_parquet(filepath, index=index)
    elif filepath.suffix == '.csv':
        df.to_csv(filepath, index=index)
    else:
        raise ValueError(f"Unsupported file format: {filepath.suffix}")


def load_dataframe(filepath: Path) -> pd.DataFrame:
    """Loads a DataFrame from Parquet or CSV based on file extension."""
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
        
    if filepath.suffix == '.parquet':
        return pd.read_parquet(filepath)
    elif filepath.suffix == '.csv':
        return pd.read_csv(filepath)
    else:
        raise ValueError(f"Unsupported file format: {filepath.suffix}")


class ExecutionTimer:
    """Context manager to log block execution duration."""
    def __init__(self, description: str, logger: Optional[logging.Logger] = None):
        self.description = description
        self.logger = logger or setup_logger()

    def __enter__(self):
        self.start_time = time.time()
        self.logger.info(f"Starting: {self.description}...")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self.start_time
        self.logger.info(f"Finished: {self.description} in {elapsed:.2f} seconds.")
