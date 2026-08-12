import aiosmtplib
from email.message import EmailMessage
from src.config.settings import settings
import os

class EmailSender:
    """Async SMTP email sender with retry logic for production reliability."""
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.username = settings.SMTP_USERNAME
        self.password = settings.SMTP_PASSWORD
        
    async def send_email(self, to_email: str, subject: str, html_content: str, retries: int = 3):
        if not self.username or not self.password:
            print(f"MOCK EMAIL to {to_email}: {subject}")
            return True

        message = EmailMessage()
        message["From"] = self.username
        message["To"] = to_email
        message["Subject"] = subject
        message.add_alternative(html_content, subtype='html')

        for attempt in range(retries):
            try:
                await aiosmtplib.send(
                    message,
                    hostname=self.smtp_server,
                    port=self.smtp_port,
                    start_tls=True,
                    username=self.username,
                    password=self.password
                )
                return True
            except Exception as e:
                print(f"Email failed (Attempt {attempt+1}/{retries}): {e}")
                if attempt == retries - 1:
                    return False
        return False
        
    def render_appointment_template(self, context: dict) -> str:
        """Reads the HTML template and injects context variables."""
        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'appointment.html')
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            for key, value in context.items():
                template = template.replace(f"{{{{{key}}}}}", str(value))
            return template
        except FileNotFoundError:
            return f"<h1>Appointment Confirmed</h1><p>{context}</p>"
