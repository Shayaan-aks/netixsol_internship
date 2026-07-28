import pandas as pd
import numpy as np
import logging
import os
import random

def setup_logger(name="prediction_models", log_file=None):
    """Set up a logger for the prediction modeling pipeline."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Check if handlers already exist to avoid duplicate logging
    if not logger.handlers:
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            fh = logging.FileHandler(log_file)
            fh.setFormatter(formatter)
            logger.addHandler(fh)
            
    return logger

def set_seed(seed=42):
    """Set seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    # If using torch/tf in future, set those here too

def load_data(filepath):
    """Load the engineered feature table."""
    logger = logging.getLogger("prediction_models")
    logger.info(f"Loading data from {filepath}")
    
    if filepath.endswith('.parquet'):
        df = pd.read_parquet(filepath)
    elif filepath.endswith('.csv'):
        df = pd.read_csv(filepath)
    else:
        raise ValueError("Unsupported file format. Use .parquet or .csv")
        
    logger.info(f"Loaded {df.shape[0]} rows and {df.shape[1]} columns.")
    return df

def get_train_val_test_split(df, val_year=2023, test_year=2024):
    """
    Split data chronologically to prevent data leakage.
    Train: < val_year
    Val: val_year
    Test: >= test_year
    """
    logger = logging.getLogger("prediction_models")
    
    train = df[df['season'] < val_year].copy()
    val = df[df['season'] == val_year].copy()
    test = df[df['season'] >= test_year].copy()
    
    logger.info(f"Train matches: {len(train)}")
    logger.info(f"Val matches: {len(val)}")
    logger.info(f"Test matches: {len(test)}")
    
    return train, val, test
