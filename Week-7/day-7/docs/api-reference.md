# API Reference

The NetixSol Real Estate AI Platform exposes a REST API and WebSocket endpoints for voice integration.

## Authentication
All endpoints (except `/health`, `/live`, `/ready`) require authentication. 

Pass your API key in the headers:
```http
X-API-Key: your_production_api_key
```
Alternatively, pass a Bearer JWT token:
```http
Authorization: Bearer your_jwt_token
```

---

## 1. Voice & Chat

### `POST /v1/voice/chat`
Single-turn text chat that triggers the full LangGraph pipeline.

**Request:**
```json
{
  "message": "I want to buy a 3 bed house in DHA Lahore",
  "session_id": "user-123",
  "language": "ur-PK"
}
```

**Response (200 OK):**
```json
{
  "response": "DHA Lahore mein 3 bedrooms ke houses 2 se 4 Crore ke beech mil jayenge. Main aapko options bhejoon?",
  "session_id": "user-123",
  "intent": "property_search",
  "confidence": 0.95,
  "sentiment": "neutral",
  "tools_called": ["search_property_knowledge"],
  "latency_ms": 1205.4,
  "request_id": "req-xyz-123"
}
```

### `WS /v1/voice/ws/{session_id}`
Real-time WebSocket connection for streaming audio/text.

**Protocol Flow:**
1. Connect to `ws://api.netixsol.com/v1/voice/ws/12345`
2. Client sends auth: `{"type": "text", "api_key": "..."}`
3. Server replies: `{"type": "connected"}`
4. Client sends audio/text: `{"type": "text", "data": "Hello"}`
5. Server streams response: `{"type": "response", "data": "Assalam o Alaikum...", "is_streaming": true}`
6. Server marks completion: `{"type": "done"}`

---

## 2. Properties (RAG)

### `POST /v1/properties/search`
Semantic search against the real estate knowledge base.

**Request:**
```json
{
  "query": "House in Gulberg under 5 crore",
  "budget_max": 50000000,
  "limit": 5
}
```

---

## 3. Appointments

### `POST /v1/appointments/book`
Books an appointment in Google Calendar and updates CRM.

**Request:**
```json
{
  "customer_phone": "03001234567",
  "customer_name": "Ali",
  "date": "2026-08-10",
  "time": "14:00"
}
```

---

## 4. CRM

### `GET /v1/crm/customers/{phone}`
Lookup customer history and lead score.

### `POST /v1/crm/customers/{customer_id}/interactions`
Log a conversation summary to the CRM.

---

## Rate Limits
Limits are enforced per IP or API Key:
- REST API: 60 requests/minute
- WebSockets: 5 connections/minute

Response headers include limit status:
- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`
