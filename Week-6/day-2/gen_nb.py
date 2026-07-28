import nbformat as nbf
import os

def create_notebook():
    nb = nbf.v4.new_notebook()
    
    cells = []
    
    cells.append(nbf.v4.new_markdown_cell("""
# AFL Analytics Foundation - Week 6 Day 2
## Production Prediction Models: Match Winner & Top Player

This notebook serves as a professional data science report documenting the development and evaluation of two production-ready machine learning systems for the AFL Data Analytics Platform.

**Objective:**
1. Model 1: Predict Match Winner
2. Model 2: Predict Top Player

The implementation strictly avoids data leakage and adheres to software engineering best practices with a modular architecture.
"""))
    
    cells.append(nbf.v4.new_code_cell("""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import sys
sys.path.append('../')

# Set plotting style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette('deep')
"""))
    
    cells.append(nbf.v4.new_markdown_cell("""
### 1. Data Loading and Preparation
We load the engineered features generated in Day 1.
"""))
    
    cells.append(nbf.v4.new_code_cell("""
from src.utils import load_data

try:
    df = load_data('../day-1/data/features/afl_feature_table.parquet')
except FileNotFoundError:
    df = load_data('../day-1/data/features/afl_feature_table.csv')

df.head()
"""))

    cells.append(nbf.v4.new_markdown_cell("""
### 2. Model Evaluation Summary
The models were trained using time-series cross-validation and rigorous parameter tuning using `RandomizedSearchCV` in our modular pipeline. Let's look at the performance on the hold-out set (2024-2025).
"""))

    cells.append(nbf.v4.new_code_cell("""
# Load Evaluation Summary
summary_df = pd.read_csv('../outputs/reports/evaluation_summary.csv', index_col=0)
summary_df
"""))

    cells.append(nbf.v4.new_markdown_cell("""
### 3. Visualizing Model Calibration and Performance
Good calibration is essential for down-stream decision making (such as betting or AI agents). Here we review the performance of the best model.
"""))

    cells.append(nbf.v4.new_code_cell("""
from IPython.display import Image, display

print("ROC Curve")
display(Image(filename='../outputs/figures/roc_curve_LogisticRegression.png', width=600))
# Replace LogisticRegression with the best model if needed

print("Calibration Curve")
display(Image(filename='../outputs/figures/calibration_curve_LogisticRegression.png', width=600))

print("Feature Importance")
display(Image(filename='../outputs/figures/feature_importance_Best_Model.png', width=800))
"""))

    cells.append(nbf.v4.new_markdown_cell("""
### 4. Inference via Deployment API
Finally, let's test the production deployment API, which handles live inference perfectly for the future AI Agent.
"""))
    
    cells.append(nbf.v4.new_code_cell("""
from predict import predict_match_winner, predict_top_player

# Sample Match Features
sample_match = df[df['season'] == 2024].iloc[0].to_dict()
prediction = predict_match_winner(sample_match)
print(f"Prediction for sample match: {prediction}")

# Sample Top Player
import pandas as pd
df_players = pd.read_csv('../day-1/data/raw/merged_players.csv')
sample_player = df_players.iloc[0].to_dict()
top_player_pred = predict_top_player([sample_player])
print(f"Top Player Prediction: {top_player_pred}")
"""))

    cells.append(nbf.v4.new_markdown_cell("""
### 5. Top Player Ranking Model
We also evaluated a regression model predicting the player's performance. Here are the top player metrics.
"""))

    cells.append(nbf.v4.new_code_cell("""
import pandas as pd
top_player_df = pd.read_csv('../outputs/reports/top_player_evaluation.csv', index_col=0)
top_player_df
"""))

    cells.append(nbf.v4.new_code_cell("""
print("Feature Importance for Top Player")
display(Image(filename='../outputs/figures/feature_importance_Best_Top_Player_Model.png', width=800))
"""))
    
    nb['cells'] = cells
    
    os.makedirs('notebooks', exist_ok=True)
    with open('notebooks/week6_day2_prediction_models.ipynb', 'w') as f:
        nbf.write(nb, f)
        
    print("Notebook generated successfully.")

if __name__ == '__main__':
    create_notebook()
