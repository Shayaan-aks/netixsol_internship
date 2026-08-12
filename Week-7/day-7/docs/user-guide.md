# User Guide — NetixSol AI Agent

Welcome to the NetixSol AI Agent! This platform automates real estate inquiries, qualifies leads, and books property viewings.

## For Real Estate Agents & Business Users

### 1. What the AI Handles
The AI voice agent acts as a frontline receptionist and junior sales agent. It is designed to:
- Greet customers in natural Urdulish.
- Answer questions about property prices, locations, and availability (using the RAG database).
- Qualify leads by asking for budget and preferences.
- Book calendar appointments for physical property viewings.
- Handle angry customers by apologizing and escalating.

### 2. Monitoring Conversations (CRM)
Every conversation is logged in the CRM. You can view:
- **Lead Score:** Increases if the customer states a budget or books a visit.
- **Interaction Summary:** A brief recap of what was discussed.
- **Properties Shown:** Which specific properties the AI recommended.

### 3. Appointments
When the AI books an appointment:
1. It checks your **Google Calendar** for open slots.
2. It books the slot and sends an **email confirmation** to the customer via n8n.
3. It appears on your calendar immediately.

If a customer calls back to reschedule, the AI will automatically find a new slot and update the calendar.

### 4. Handling Escalations
If a customer becomes frustrated or asks complex legal questions, the AI is programmed to say:
*"Main apne senior agent se connect karwati hoon."* 
It will then log the CRM status as `requires_human` and you will receive an alert.
