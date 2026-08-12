# Production Release Checklist

Before merging to `main` and deploying to production, the Release Manager must complete this checklist.

## 1. Pre-Deployment (Staging)
- [ ] **Tests Pass:** GitHub Actions CI pipeline is green (Bandit + Pytest).
- [ ] **Configuration:** Verified `.env` variables match the staging environment.
- [ ] **Dependencies:** No vulnerable packages identified (`pip-audit`).
- [ ] **Data Migration:** Run any pending database migrations.
- [ ] **RAG Indexing:** Verify ChromaDB contains the latest property listings.

## 2. Deployment
- [ ] **Tag Release:** Create a semantic version tag in Git (e.g., `v1.0.0`).
- [ ] **Deploy Manifests:** Apply Kubernetes manifests (`kubectl apply -f deployment/kubernetes/`).
- [ ] **Verify Rollout:** Check deployment status (`kubectl rollout status deployment/agent-deployment`).

## 3. Post-Deployment Smoke Tests
- [ ] **Health Check:** `curl https://api.netixsol.com/v1/health` returns `status: "healthy"`.
- [ ] **Chat Endpoint:** Submit a standard text request; verify response and latency < 2s.
- [ ] **Security Gate:** Submit an injection attempt (`Ignore all rules`); verify it is safely deflected.
- [ ] **Metrics:** Check Grafana; verify `http_requests_total` is incrementing.

## 4. Rollback Procedure
If any smoke test fails, immediately initiate a rollback:

**Kubernetes:**
```bash
kubectl rollout undo deployment/agent-deployment
```

**Docker Compose:**
```bash
docker-compose stop
git checkout v0.9.5  # Previous stable tag
docker-compose up -d --build
```
