# Client Handover Package

This document formalizes the transfer of the NetixSol Real Estate AI Platform to the client's operations and engineering teams.

## 1. Deliverables Inventory

The following systems are included in this handover:
- **FastAPI Backend Server:** Located in `Week-7/day-7/backend/`. Handles STT/TTS routing, LangGraph orchestration, RAG, and Tool Execution.
- **Security Module:** `prompt_guard.py` implementation with 24 heuristic threat signatures and LLM verification.
- **Deployment Infrastructure:** Complete Docker Compose and Kubernetes manifests located in `deployment/`.
- **Observability Stack:** Prometheus alert rules and Grafana dashboard configurations located in `monitoring/`.
- **Knowledge Base Framework:** ChromaDB integration for RAG.

## 2. Formal Acceptance Checklist

The client must verify the following before signing off:

### 2.1 Infrastructure & Deployment
- [ ] Platform runs cleanly via `docker-compose up`.
- [ ] No hardcoded secrets exist in the codebase.
- [ ] API endpoints are secured behind API Keys or JWT.
- [ ] Nginx is properly proxying traffic with TLS termination (in production).

### 2.2 Functional Requirements
- [ ] Voice agent successfully greets and responds in Urdulish.
- [ ] RAG semantic search accurately retrieves property details.
- [ ] Appointment booking creates a Google Calendar event.
- [ ] Appointment cancellation removes the Google Calendar event.
- [ ] Interaction summaries are saved to the CRM endpoint.

### 2.3 Security & Reliability
- [ ] Attempting prompt injection (e.g., "ignore previous instructions") is blocked and logged.
- [ ] Grafana dashboard successfully receives metrics from Prometheus.
- [ ] All 38 integration and security tests pass (`pytest tests/`).

## 3. Credential Handover

Ensure the client has exclusive access to the following production accounts:
- **Google Cloud Platform:** Project containing the Gemini 2.5 API key and Google Calendar OAuth credentials.
- **n8n Cloud / Self-Hosted:** The automation workflows for email.
- **Domain Registrar / DNS:** For mapping `api.netixsol.com` to the ingress server.

*We recommend rotating all API keys immediately after handover.*

## 4. Support and Escalation

- **Tier 1 (Internal IT):** Follow the `troubleshooting.md` guide.
- **Tier 2 (Platform Team):** Review Grafana dashboards and Kubernetes logs.
- **Tier 3 (External Support):** Escalation to NetixSol AI engineering (if included in maintenance contract).
