import pandas as pd
import logging
from .metrics import evaluate_classification, evaluate_ranking

def evaluate_models(results_dict, problem_type='classification'):
    """
    Compile evaluation metrics from multiple models into a summary DataFrame.
    results_dict format: { 'ModelName': {'y_true': ..., 'y_pred': ..., 'y_prob': ...} }
    """
    logger = logging.getLogger("prediction_models")
    logger.info(f"Evaluating {len(results_dict)} models for {problem_type}")
    
    summary = []
    
    for model_name, res in results_dict.items():
        if problem_type == 'classification':
            metrics = evaluate_classification(res['y_true'], res['y_pred'], res['y_prob'])
        else: # ranking/regression
            # res needs to contain df_true and df_pred
            metrics = evaluate_ranking(res['df_true'], res['df_pred'])
            
        metrics['Model'] = model_name
        summary.append(metrics)
        
    df_summary = pd.DataFrame(summary).set_index('Model')
    
    # Reorder columns logically
    if problem_type == 'classification':
        cols = ['ROC_AUC', 'Log_Loss', 'Accuracy', 'F1_Score', 'Precision', 'Recall', 'PR_AUC', 'Brier_Score']
        df_summary = df_summary[[c for c in cols if c in df_summary.columns]]
        df_summary = df_summary.sort_values('ROC_AUC', ascending=False)
    else:
        cols = ['NDCG', 'Top1_Accuracy', 'MAE', 'RMSE']
        df_summary = df_summary[[c for c in cols if c in df_summary.columns]]
        df_summary = df_summary.sort_values('NDCG', ascending=False)
        
    return df_summary
