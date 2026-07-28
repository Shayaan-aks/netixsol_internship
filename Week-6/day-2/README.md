# Week 6 Day 2: AFL Prediction Models

This directory contains the production-ready machine learning systems for predicting the AFL Match Winner and Top Player.

## Architecture

The project follows a modular structure built on scikit-learn Pipelines to guarantee no data leakage during preprocessing and prediction.

```text
project/
├── notebooks/
│   └── week6_day2_prediction_models.ipynb  # Professional Data Science Report
├── src/
│   ├── preprocessing.py                    # Feature selection and target generation
│   ├── pipelines.py                        # Scikit-Learn ColumnTransformers
│   ├── model_training.py                   # Model wrappers (RF, XGBoost, LR) with TimeSeriesSplit
│   ├── validation.py                       # Leakage checks
│   ├── metrics.py                          # AUC, NDCG, Calibration metrics
│   ├── evaluation.py                       # Aggregating evaluation reports
│   ├── feature_importance.py               # Tree-based importance extraction
│   ├── visualization.py                    # ROC, Calibration, Confusion Matrix plots
│   └── prediction.py                       # Core inference utilities
├── models/                                 # Serialized joblib pipelines
├── outputs/                                # Generated reports and publication-quality figures
├── predict.py                              # Deployment API for future AI Agents
└── main_pipeline.py & top_player_pipeline.py # Training scripts
```

## Setup & Execution

Install dependencies:
```bash
pip install -r requirements.txt
```

Train the models:
```bash
python main_pipeline.py
python top_player_pipeline.py
```

## Inference API (`predict.py`)

The deployment API provides a clean interface for downstream LangGraph agents to use the trained models.

```python
from predict import predict_match_winner, predict_top_player

# 1. Match Winner
result = predict_match_winner(match_data_dict)
print(result['home_win_probability'])

# 2. Top Player
ranked_players = predict_top_player(list_of_player_dicts)
print(ranked_players[0]['predicted_rank'])
```
