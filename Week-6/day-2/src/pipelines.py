import logging
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

def build_preprocessor(num_cols, cat_cols):
    """
    Build a scikit-learn ColumnTransformer for preprocessing.
    """
    logger = logging.getLogger("prediction_models")
    logger.info(f"Building preprocessor for {len(num_cols)} numerical and {len(cat_cols)} categorical features.")
    
    # Numerical pipeline: Impute missing values with median, then scale
    num_pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    # Categorical pipeline: one-hot encode
    cat_pipeline = Pipeline([
        ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', num_pipeline, num_cols),
            ('cat', cat_pipeline, cat_cols)
        ],
        remainder='drop'  # Drop any columns not explicitly specified
    )
    
    return preprocessor

def get_model_pipeline(preprocessor, estimator):
    """Combine preprocessor and an estimator into a Pipeline."""
    return Pipeline([
        ('preprocessor', preprocessor),
        ('estimator', estimator)
    ])
