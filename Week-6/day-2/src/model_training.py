import logging
from sklearn.model_selection import TimeSeriesSplit, RandomizedSearchCV
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from xgboost import XGBClassifier, XGBRegressor

def get_match_winner_models():
    """Return a dictionary of models and their hyperparameter grids for Match Winner (Classification)."""
    models = {
        'LogisticRegression': {
            'estimator': LogisticRegression(max_iter=1000, random_state=42),
            'param_grid': {
                'estimator__C': [0.01, 0.1, 1.0, 10.0],
                'estimator__penalty': ['l2']
            }
        },
        'RandomForestClassifier': {
            'estimator': RandomForestClassifier(random_state=42, n_jobs=-1),
            'param_grid': {
                'estimator__n_estimators': [100, 200],
                'estimator__max_depth': [5, 10, None],
                'estimator__min_samples_split': [2, 5, 10]
            }
        },
        'XGBClassifier': {
            'estimator': XGBClassifier(random_state=42, n_jobs=-1, eval_metric='logloss'),
            'param_grid': {
                'estimator__n_estimators': [100, 200],
                'estimator__max_depth': [3, 5, 7],
                'estimator__learning_rate': [0.01, 0.1, 0.2]
            }
        }
    }
    return models

def get_top_player_models():
    """Return a dictionary of models and grids for Top Player (Regression)."""
    models = {
        'Ridge': {
            'estimator': Ridge(random_state=42),
            'param_grid': {
                'estimator__alpha': [0.1, 1.0, 10.0, 100.0]
            }
        },
        'RandomForestRegressor': {
            'estimator': RandomForestRegressor(random_state=42, n_jobs=-1),
            'param_grid': {
                'estimator__n_estimators': [100, 200],
                'estimator__max_depth': [5, 10, None],
                'estimator__min_samples_split': [5, 10]
            }
        },
        'XGBRegressor': {
            'estimator': XGBRegressor(random_state=42, n_jobs=-1),
            'param_grid': {
                'estimator__n_estimators': [100, 200],
                'estimator__max_depth': [3, 5, 7],
                'estimator__learning_rate': [0.01, 0.1, 0.2]
            }
        }
    }
    return models

def train_with_cv(pipeline, param_grid, X_train, y_train, n_splits=5, scoring='neg_log_loss', n_iter=10):
    """
    Train a pipeline using TimeSeriesSplit and RandomizedSearchCV.
    """
    logger = logging.getLogger("prediction_models")
    
    tscv = TimeSeriesSplit(n_splits=n_splits)
    
    # We use RandomizedSearchCV to speed things up vs GridSearchCV
    search = RandomizedSearchCV(
        pipeline, 
        param_distributions=param_grid, 
        n_iter=n_iter,
        cv=tscv, 
        scoring=scoring, 
        n_jobs=-1,
        random_state=42,
        verbose=1
    )
    
    logger.info(f"Starting RandomizedSearchCV with {n_iter} iterations.")
    search.fit(X_train, y_train)
    
    logger.info(f"Best params: {search.best_params_}")
    logger.info(f"Best CV score: {search.best_score_:.4f}")
    
    return search.best_estimator_
