import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, log_loss, brier_score_loss,
    mean_absolute_error, mean_squared_error, ndcg_score
)

def evaluate_classification(y_true, y_pred, y_prob):
    """
    Evaluate match winner classification models.
    """
    return {
        'Accuracy': accuracy_score(y_true, y_pred),
        'Precision': precision_score(y_true, y_pred, zero_division=0),
        'Recall': recall_score(y_true, y_pred, zero_division=0),
        'F1_Score': f1_score(y_true, y_pred, zero_division=0),
        'ROC_AUC': roc_auc_score(y_true, y_prob),
        'PR_AUC': average_precision_score(y_true, y_prob),
        'Log_Loss': log_loss(y_true, y_prob),
        'Brier_Score': brier_score_loss(y_true, y_prob)
    }

def evaluate_ranking(df_true, df_pred, match_col='match_id', target_col='composite_fantasy_score', pred_col='predicted_score'):
    """
    Evaluate Top Player models by framing it as a ranking problem per match.
    """
    df = df_true.copy()
    df[pred_col] = df_pred
    
    maes = []
    rmses = []
    ndcgs = []
    top1_accs = []
    
    # Evaluate per match
    for match_id, group in df.groupby(match_col):
        if len(group) < 2:
            continue
            
        y_t = group[target_col].values
        y_p = group[pred_col].values
        
        # Regression metrics
        maes.append(mean_absolute_error(y_t, y_p))
        rmses.append(np.sqrt(mean_squared_error(y_t, y_p)))
        
        # Ranking metrics (NDCG)
        # NDCG requires 2D arrays: shape (n_samples, n_labels)
        # We treat each match as one sample with len(group) labels.
        # But players vary per match. It's easier to compute per match.
        try:
            # For ndcg, all targets must be positive. Assuming scores are. 
            # We subtract min if negative just in case.
            y_t_norm = y_t - y_t.min()
            ndcg = ndcg_score([y_t_norm], [y_p])
            ndcgs.append(ndcg)
        except ValueError:
            pass
            
        # Top-1 Accuracy: Did the model predict the actual top player?
        actual_top_idx = np.argmax(y_t)
        pred_top_idx = np.argmax(y_p)
        top1_accs.append(1 if actual_top_idx == pred_top_idx else 0)
        
    return {
        'MAE': np.mean(maes),
        'RMSE': np.mean(rmses),
        'NDCG': np.mean(ndcgs) if ndcgs else np.nan,
        'Top1_Accuracy': np.mean(top1_accs)
    }
