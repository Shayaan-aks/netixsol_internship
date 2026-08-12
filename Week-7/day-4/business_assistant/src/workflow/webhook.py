import httpx
from src.config.settings import settings

class WorkflowWebhookClient:
    """Triggers the n8n Workflow automation."""
    def __init__(self):
        self.webhook_url = settings.N8N_WEBHOOK_URL
        
    async def trigger_workflow(self, event_type: str, payload: dict):
        """Send event data to n8n for background processing (CRM sync, Email sending)."""
        data = {
            "event": event_type,
            "data": payload
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.webhook_url, json=data, timeout=5.0)
                return response.status_code == 200
        except Exception as e:
            print(f"Failed to trigger n8n workflow: {e}")
            # Fallback handling would happen here (store in local queue to retry later)
            return False
