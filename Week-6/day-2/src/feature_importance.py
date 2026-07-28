import numpy as np

def extract_feature_importances(pipeline, preprocessor, num_cols, cat_cols):
    """
    Extract feature names and importances from a fitted pipeline.
    """
    estimator = pipeline.named_steps['estimator']
    
    # Get feature names after preprocessing
    # Numerical features are identical
    feature_names = list(num_cols)
    
    # Categorical features need to be extracted from OneHotEncoder
    if len(cat_cols) > 0:
        ohe = preprocessor.transformers_[1][1].named_steps['encoder']
        cat_features = ohe.get_feature_names_out(cat_cols)
        feature_names.extend(cat_features)
        
    # Get importances
    if hasattr(estimator, 'feature_importances_'):
        importances = estimator.feature_importances_
    elif hasattr(estimator, 'coef_'):
        # For logistic regression/ridge
        importances = np.abs(estimator.coef_[0]) if estimator.coef_.ndim > 1 else np.abs(estimator.coef_)
    else:
        importances = np.zeros(len(feature_names))
        
    return importances, feature_names
