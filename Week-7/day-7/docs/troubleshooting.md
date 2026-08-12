# Troubleshooting Guide

Use this decision tree to diagnose and fix common production issues.

## 1. High Latency (Slow Responses)

**Symptom:** AI takes 5+ seconds to reply. Voice feels unnatural.
**Diagnosis:** Check Grafana `E2E P95 Latency` dashboard.
- **If LLM latency is high:** Google's API may be degraded. Switch to a fallback model region.
- **If Tool latency is high:** The CRM database or Google Calendar API is slow. Check DB connection pooling limits (`DB_POOL_SIZE`).
- **If STT/TTS is slow:** Ensure the server is located near the STT provider's datacenter (e.g., AWS me-south-1).

## 2. AI is Hallucinating Properties

**Symptom:** AI recommends properties that don't exist in the database.
**Diagnosis:** 
- Check the RAG prompt in `properties.py`.
- **Fix:** Ensure the system prompt strictly says: *"Do not invent properties. Only use the tools provided."*
- **Fix:** Verify ChromaDB is populated by running a manual semantic search query via REST API.

## 3. Appointments Failing to Book

**Symptom:** Customer agrees to a time, but no email is sent and Calendar is empty.
**Diagnosis:** Check Grafana `agent_calendar_failures_total`.
- **Cause 1:** Google Calendar OAuth token expired. Re-authenticate and update `credentials.json`.
- **Cause 2:** n8n webhook URL changed or is down. Verify `N8N_WEBHOOK_URL` in `.env`.

## 4. "Rate Limit Exceeded" Errors (HTTP 429)

**Symptom:** Valid API keys are getting rejected.
**Diagnosis:**
- **Cause 1:** Nginx limit (`limit_req_zone`) is too strict. Adjust `nginx.conf` `rate=30r/m` to a higher value.
- **Cause 2:** FastAPI internal rate limiter triggered. Increase `RATE_LIMIT_PER_MINUTE` in `.env`.
- **Cause 3:** Nginx is not forwarding the real client IP, causing all traffic to look like it comes from 1 IP. Ensure `X-Forwarded-For` is correctly mapped.

## 5. Security Block False Positives

**Symptom:** Legitimate customer messages are triggering the security warning.
**Diagnosis:** Look at Prometheus `agent_security_violations_total` grouped by `reason`.
- **Fix:** Check `prompt_guard.py` regex patterns. Ensure the regex isn't too broad (e.g., accidentally blocking the word "ignore" in a normal context like "ignore the budget").

## 6. Containers Crash Loop (OOMKilled)

**Symptom:** `docker ps` shows the agent restarting constantly.
**Diagnosis:** Container ran out of memory.
- **Fix:** In `docker-compose.prod.yml`, increase or remove memory limits, or reduce the number of Uvicorn `workers`.
