# Administrator Guide

This guide covers installation, configuration, and monitoring of the NetixSol AI Platform.

## 1. Installation (Docker Compose)

The easiest way to run the production stack on a single VM (e.g., AWS EC2, DigitalOcean Droplet) is via Docker Compose.

```bash
# 1. Clone the repository
git clone https://github.com/netixsol/real-estate-ai.git
cd real-estate-ai/Week-7/day-7

# 2. Setup Environment Variables
cp .env.example .env
nano .env  # Add GEMINI_API_KEY, POSTGRES_PASSWORD, etc.

# 3. Start the Stack
docker-compose -f docker-compose.prod.yml up -d --build
```

## 2. Environment Variables & Secrets

Critical variables that MUST be set in production:

- `GEMINI_API_KEY`: Google AI Studio key (required for LLM).
- `JWT_SECRET`: Random 256-bit string for signing JWT tokens.
- `API_KEYS`: Comma-separated list of valid backend API keys.
- `POSTGRES_PASSWORD`: Secure password for CRM database.
- `REDIS_PASSWORD`: Secure password for Rate limit cache.

## 3. Monitoring & Logs

### Viewing Logs
All containers use the `json-file` logging driver with automatic rotation.

```bash
# View live API logs
docker logs -f real_estate_agent

# View Nginx access logs
docker logs -f nginx
```

### Accessing Dashboards
- **Prometheus:** `http://localhost:9090` (Internal port forwarding required)
- **Grafana:** `http://localhost:3000` 
  - User: `admin`
  - Pass: Defined by `GRAFANA_PASSWORD` in `.env`

## 4. Database Backups

The PostgreSQL database should be backed up daily using `pg_dump`:

```bash
docker exec -t postgres pg_dump -U realestate netixsol_re > backup_$(date +%F).sql
```
Restore:
```bash
cat backup_YYYY-MM-DD.sql | docker exec -i postgres psql -U realestate netixsol_re
```

## 5. Scaling

If `agent_request_latency_seconds` increases, scale the FastAPI workers:
1. **In Docker Compose:** Increase `workers: 4` to `workers: 8` in `Dockerfile.api`.
2. **In Kubernetes:** The HPA (HorizontalPodAutoscaler) will automatically scale pods up to 10 based on CPU usage.
