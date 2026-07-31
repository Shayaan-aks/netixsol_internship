# Monitoring and Maintenance Plan

## 1. Daily Monitoring Checklist
- [ ] Review `assistant.log` for ERROR or CRITICAL entries.
- [ ] Monitor API latency via structured JSON logs. Alert if 95th percentile latency exceeds 3.5 seconds.
- [ ] Review Abuse handler logs: Track the number of users hitting the "Blocked" state due to prompt injections or off-topic spam.

## 2. Weekly Data Updates
The AFL is a highly dynamic sport. Data must be refreshed weekly.
- **Structured Data**: Run the ETL pipeline every Monday at 02:00 AEST to pull the weekend's match results and player statistics.
- **Semantic Data**: Ingest daily AFL news articles into the vector database.

## 3. Model Retraining / Prompt Tuning
- **Monthly Evaluation**: Run the `evaluation/tests.py` suite.
- **Failure Analysis**: Identify queries that the router misclassified. Update the `ROUTER_PROMPT` in `graph/router.py` with few-shot examples of the failed queries to improve classification accuracy.
- **Prediction Models**: Retrain the mock ML prediction models every month using updated historical data to prevent concept drift.
