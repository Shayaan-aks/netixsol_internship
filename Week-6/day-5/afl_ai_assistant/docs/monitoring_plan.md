# Monitoring & Maintenance Plan — AFL AI Assistant

## 1. Metrics to Track

| Metric | Description | Source |
|---|---|---|
| **Response Latency (p95)** | 95th-percentile API response time | `logs/assistant.log` → `latency_seconds` |
| **Tool Error Rate** | % of requests where tool returns error string | `logs/assistant.log` → `response_preview` contains "error" |
| **Off-Topic Leak Rate** | % of off-topic queries not caught by guardrail | Manual review + `logs/abuse.log` |
| **Intent Distribution** | Breakdown of factual / retrieval / prediction / blocked | `logs/assistant.log` → `intent` |
| **Prediction Accuracy Drift** | How often predicted winner matches actual result | Weekly comparison vs published AFL results |
| **Token Usage** | Estimated tokens per request for cost tracking | `logs/assistant.log` → `token_usage` |
| **Injection Attempt Rate** | Count of blocked injection attempts per day | `logs/abuse.log` → `event_type=injection_attempt` |

---

## 2. Alert Thresholds

| Metric | Warning | Critical | Action |
|---|---|---|---|
| API Latency p95 | > 2.0s | > 5.0s | Check LangGraph node timeouts; scale API |
| Tool Error Rate | > 5% | > 15% | Check CSV path, tool imports, Python env |
| Off-Topic Leak Rate | > 2% | > 10% | Update router keyword lists; add LLM fallback |
| Injection Attempts/Day | > 20 | > 100 | Review `abuse.log`; consider IP-level blocking |
| Test Suite Pass Rate | < 95% | < 85% | Run `evaluation/report.py`; identify regressed category |

---

## 3. Daily Monitoring Checklist

- [ ] Review `logs/assistant.log` — check for any `"intent": "error"` entries
- [ ] Review `logs/abuse.log` — count injection attempts and off-topic abuse events
- [ ] Spot-check 5 random log entries for correct intent classification
- [ ] Verify API health endpoint: `GET /health` returns `{"status": "healthy"}`
- [ ] Confirm p95 latency < 2.0s across last 100 requests

---

## 4. Weekly Data Refresh Loop

The AFL season runs weekly (rounds every Saturday/Sunday). Data must be refreshed:

```
Monday 02:00 AEST (automated):
  1. Pull weekend match results → append to data/afl_dataset.csv
  2. Update player stats (goals, disposals) for completed rounds
  3. Re-run pytest: python -m pytest evaluation/tests.py
  4. Re-run report: python -m evaluation.report
  5. If pass rate < 95%, page on-call engineer
```

**ETL Script location:** `data/etl_refresh.py` (to be built for production)

---

## 5. Monthly Model Retraining Loop

```
1st Monday of each month:
  1. Export structured_dataset → train/validation split (80/20)
  2. Retrain match_predictor on updated season results
     - Baseline: ladder-position naive model
     - Target: >65% accuracy on held-out finals matches
  3. Update prediction/match_predictor.py with new coefficients
  4. Re-run benchmark: python -m evaluation.benchmark
  5. If accuracy < naive baseline, rollback and investigate
```

---

## 6. Guardrail Drift Review (Monthly)

As users probe the system, new injection patterns emerge. Monthly:

1. Pull all `logs/abuse.log` entries from the past month
2. Review any `event_type=off_topic` entries where the query was actually AFL-related
   (false positive analysis)
3. Add new injection patterns to `INJECTION_KEYWORDS` in `graph/router.py`
4. Add new off-topic terms if new sports/topics have been probed
5. Re-run `evaluation/tests.py` to confirm no regressions

---

## 7. Recommended Alert Cadence

| Cadence | Action |
|---|---|
| Real-time | Health check endpoint monitored by uptime service |
| Daily | Automated log analysis script emails summary |
| Weekly | ETL refresh + test suite + report regeneration |
| Monthly | Model retraining + guardrail review + benchmarking |
| Quarterly | Full architecture review; consider replacing mock ML with production model |
