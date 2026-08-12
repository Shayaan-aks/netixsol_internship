# Maintenance Plan & Operational Strategy

To ensure long-term stability and quality of the AI Platform, follow this maintenance strategy.

## 1. Service Level Objectives (SLOs)

The platform is monitored against the following strict latency and availability targets:

| Metric | Target (P95) | Alert Threshold |
|--------|--------------|-----------------|
| Speech-to-Text (STT) | < 600 ms | > 600 ms |
| LLM First Token | < 700 ms | > 700 ms |
| Tool Execution (RAG/API) | < 500 ms | > 500 ms |
| End-to-End Response | < 2,000 ms | > 2,000 ms |
| Platform Availability | 99.9% Uptime | < 99.9% (8.7h downtime/yr) |

*All SLOs are tracked in Grafana and alert via Prometheus AlertManager.*

---

## 2. Weekly Maintenance Schedule

### Tuesday: Prompt & Conversation Review
- **Action:** Review 50 random conversation logs from the CRM.
- **Goal:** Identify areas where the AI misunderstood Urdulish or failed to handle objections properly.
- **Output:** Update the LangGraph System Prompts and deploy.

### Thursday: RAG Knowledge Base Refresh
- **Action:** Sync ChromaDB with the master property inventory.
- **Goal:** Ensure sold properties are removed and new listings are indexed.
- **Process:** Run the `generate_data.py` embedding script. Verify vector count matches DB count.

### Friday: Security & Dependency Scan
- **Action:** Review Prometheus `agent_security_violations_total`.
- **Goal:** Check for new prompt injection patterns. If hackers are trying new phrases, add them to `prompt_guard.py` blacklist.
- **Action:** Run `bandit` and `pip-audit` on the codebase.

---

## 3. Backup & Disaster Recovery

- **Daily (Automated):** PostgreSQL dump saved to AWS S3.
- **Weekly (Automated):** ChromaDB persist directory archived.
- **Disaster Recovery (MTTR < 1h):** If the server fails, provision a new VM, clone the repo, restore PostgreSQL from S3, and run `docker-compose up`. The system is stateless except for the DBs.

---

## 4. Model Lifecycle

When a new Gemini model is released (e.g., Gemini 3.0):
1. Update `.env` `LLM_MODEL` in a staging environment.
2. Run the `test_security.py` and evaluation suites.
3. Validate Hallucination Rate metric.
4. Perform blue/green deployment to production.
