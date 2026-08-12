# NetixSol Real Estate AI Platform

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Status](https://img.shields.io/badge/status-production_ready-success.svg)

An enterprise-grade, autonomous Voice AI Platform designed for the Pakistani Real Estate market. Powered by LangGraph, FastAPI, and Gemini, this agent handles natural Urdulish conversations, performs semantic property searches (RAG), books appointments via Google Calendar, and updates CRM records in real-time.

## Features
- **Conversational AI:** Fluent in Pakistani Urdulish with stateful memory.
- **RAG Knowledge Base:** Grounded responses using ChromaDB vector search.
- **Tool Orchestration:** Autonomous Google Calendar, CRM, and Email (n8n) integration.
- **Security:** 2-stage PromptGuard defense against jailbreaks and prompt injection.
- **Observability:** Full Prometheus metrics, Grafana dashboards, and structured JSON logging.
- **Enterprise Deployment:** Kubernetes manifests, Docker Compose, Nginx TLS proxy, and CI/CD pipelines.

---

## Quick Start (Docker Compose)

The easiest way to run the platform locally or on a single VM:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/netixsol/real-estate-ai.git
   cd real-estate-ai/Week-7/day-7
   ```

2. **Configure Environment:**
   ```bash
   cp .env.example .env
   # Open .env and add your GEMINI_API_KEY and passwords
   ```

3. **Start the Stack:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d --build
   ```

4. **Verify Health:**
   ```bash
   curl http://localhost:8000/v1/health
   ```

---

## Documentation Directory

Comprehensive documentation has been prepared for all stakeholders:

### Technical Documentation
- [Architecture Overview](docs/architecture.md)
- [API Reference](docs/api-reference.md)
- [Troubleshooting Guide](docs/troubleshooting.md)
- [Release Checklist](RELEASE_CHECKLIST.md)

### Operations & Business Documentation
- [Administrator Guide](docs/admin-guide.md)
- [Maintenance & SLO Plan](docs/maintenance-plan.md)
- [User Guide (Agents)](docs/user-guide.md)
- [Future Roadmap](docs/roadmap.md)
- [Client Handover Package](docs/handover-package.md)

---

## Architecture Stack
- **Backend:** FastAPI, Python 3.11, Pydantic
- **AI Orchestration:** LangGraph, LangChain, Google Gemini 2.5 Flash
- **Databases:** PostgreSQL (CRM), ChromaDB (Vector Store), Redis (Rate Limiting)
- **Infrastructure:** Docker, Kubernetes, Nginx
- **Observability:** Prometheus, Grafana, AlertManager, structlog

---

## License & Support
Proprietary software developed by NetixSol. For support, please refer to the [Client Handover Package](docs/handover-package.md) escalation matrix.
