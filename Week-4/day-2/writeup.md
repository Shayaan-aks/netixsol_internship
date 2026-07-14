# Week 4 Day 2 Write-Up

## Preprocessing Choices
For the preprocessing pipeline, we divided the features into numeric and categorical subsets:

1. **Numeric Features**: We utilized a `SimpleImputer` with a `median` strategy followed by a `StandardScaler`. The median was chosen over the mean because it is more robust to outliers, which is particularly important for features like `capital-gain` or `capital-loss` where a few massive values could significantly skew the mean. Standard scaling was essential for Logistic Regression because the solver relies on numerical stability and is sensitive to the scale of the features.
2. **Categorical Features**: We employed a `SimpleImputer` using the `most_frequent` strategy, immediately followed by `OneHotEncoder(handle_unknown='ignore')`. `OneHotEncoder` is suitable for nominal data (where no inherent order exists, like `relationship` or `workclass`). We skipped alternatives like `OrdinalEncoder` to avoid implying false numerical orderings to the model algorithms. Handling unknowns with 'ignore' prevents the pipeline from failing on future datasets containing unseen categories.

## Model Metrics Comparison
We trained two supervised models—Logistic Regression and an unconstrained Decision Tree—on the Adult dataset to predict whether income is >50K or <=50K. 

**Evaluation on Hold-Out Test:**
- **Logistic Regression**: Achieved an accuracy of ~85%, strong ROC AUC, and higher precision/recall balance. The confusion matrix revealed fewer false negatives compared to the decision tree. Its feature coefficients were highly interpretable, cleanly isolating predictors like capital-gains and education.
- **Decision Tree**: Suffered from heavy overfitting. The training accuracy approached 100%, but the test accuracy dropped drastically to ~81%. The unrestricted depth resulted in a complex model capturing noise in the training data, ultimately performing worse on unseen data.

## Model Selection for Day 3
Moving into Day 3, we will continue developing the **Logistic Regression** model as our primary candidate. Its generalization on the hold-out set is significantly better than the unconstrained tree, and its inherent interpretability directly supports analytical business goals. 

Tomorrow, we plan to test hyperparameter tuning for Logistic Regression (e.g., tweaking `C` for regularization) and applying `class_weight='balanced'` to better handle false negatives due to class imbalance. We might also test a Random Forest (an ensemble of constrained decision trees) as a powerful non-linear alternative to our failing single tree model.
