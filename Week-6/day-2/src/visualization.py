import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, roc_curve
from sklearn.calibration import calibration_curve
import os

def plot_roc_curve(y_true, y_prob, model_name, save_dir=None):
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, label=f"{model_name} ROC Curve", linewidth=2)
    plt.plot([0, 1], [0, 1], 'k--', label="Random Guess")
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(f'ROC Curve - {model_name}')
    plt.legend()
    plt.grid(True)
    if save_dir:
        plt.savefig(os.path.join(save_dir, f'roc_curve_{model_name}.png'), bbox_inches='tight')
    plt.close()

def plot_calibration_curve(y_true, y_prob, model_name, n_bins=10, save_dir=None):
    prob_true, prob_pred = calibration_curve(y_true, y_prob, n_bins=n_bins)
    plt.figure(figsize=(8, 6))
    plt.plot(prob_pred, prob_true, marker='o', linewidth=2, label=model_name)
    plt.plot([0, 1], [0, 1], 'k--', label='Perfectly Calibrated')
    plt.xlabel('Mean Predicted Probability')
    plt.ylabel('Fraction of Positives')
    plt.title(f'Calibration Curve - {model_name}')
    plt.legend()
    plt.grid(True)
    if save_dir:
        plt.savefig(os.path.join(save_dir, f'calibration_curve_{model_name}.png'), bbox_inches='tight')
    plt.close()

def plot_confusion_matrix(y_true, y_pred, model_name, save_dir=None):
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False)
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.title(f'Confusion Matrix - {model_name}')
    if save_dir:
        plt.savefig(os.path.join(save_dir, f'confusion_matrix_{model_name}.png'), bbox_inches='tight')
    plt.close()

def plot_feature_importance(importances, feature_names, model_name, top_n=20, save_dir=None):
    plt.figure(figsize=(10, 8))
    # sort
    indices = importances.argsort()[-top_n:]
    plt.barh(range(len(indices)), importances[indices], color='skyblue', align='center')
    plt.yticks(range(len(indices)), [feature_names[i] for i in indices])
    plt.xlabel('Relative Importance')
    plt.title(f'Top {top_n} Feature Importances - {model_name}')
    plt.grid(axis='x')
    if save_dir:
        plt.savefig(os.path.join(save_dir, f'feature_importance_{model_name}.png'), bbox_inches='tight')
    plt.close()
