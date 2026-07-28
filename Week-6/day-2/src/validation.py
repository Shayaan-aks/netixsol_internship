import logging

def check_leakage(train_meta, val_meta, test_meta):
    """
    Ensure chronological split has no leakage.
    Returns True if valid.
    """
    logger = logging.getLogger("prediction_models")
    
    max_train = train_meta['season'].max()
    min_val = val_meta['season'].min()
    max_val = val_meta['season'].max()
    min_test = test_meta['season'].min()
    
    if max_train >= min_val:
        logger.error(f"LEAKAGE DETECTED: Train data extends to {max_train}, Val starts at {min_val}")
        return False
        
    if max_val >= min_test:
        logger.error(f"LEAKAGE DETECTED: Val data extends to {max_val}, Test starts at {min_test}")
        return False
        
    logger.info("Leakage check passed: Splits are strictly chronological.")
    return True
