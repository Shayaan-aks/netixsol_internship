import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from backend.config.settings import settings

logger = logging.getLogger(__name__)

def send_email(to_email: str, subject: str, html_content: str):
    """
    Sends an email using the configured SMTP credentials.
    """
    if not settings.smtp_user or not settings.smtp_password:
        logger.warning("SMTP credentials are not configured. Email will not be sent.")
        logger.info(f"Mock Email to {to_email} | Subject: {subject}")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from_email
    msg["To"] = to_email

    part = MIMEText(html_content, "html")
    msg.attach(part)

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
        logger.info(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False

def send_appointment_emails(customer_name: str, customer_email: str, customer_phone: str, date: str, time: str, property_details: str):
    """
    Sends appointment confirmation emails to both the customer and the escorting agent.
    """
    company_name = "AKS RealEstate"
    
    # Send to Customer
    if customer_email:
        customer_subject = f"{company_name} - Site Visit Confirmation"
        customer_body = f"""
        <html>
            <body>
                <h2>Your Site Visit is Confirmed!</h2>
                <p>Dear {customer_name},</p>
                <p>Thank you for choosing <strong>{company_name}</strong>. Your site visit has been successfully scheduled.</p>
                <h3>Visit Details:</h3>
                <ul>
                    <li><strong>Date:</strong> {date}</li>
                    <li><strong>Time:</strong> {time}</li>
                    <li><strong>Property Details:</strong> {property_details}</li>
                </ul>
                <p>One of our agents will be there to escort you and answer any questions you may have.</p>
                <br/>
                <p>Best regards,<br/>The {company_name} Team</p>
            </body>
        </html>
        """
        send_email(customer_email, customer_subject, customer_body)
    
    # Send to Agent (Employee)
    agent_subject = f"New Site Visit Scheduled - {customer_name}"
    agent_body = f"""
    <html>
        <body>
            <h2>New Site Visit Assignment</h2>
            <p>You have been assigned to escort a new site visit for <strong>{company_name}</strong>.</p>
            <h3>Customer Details:</h3>
            <ul>
                <li><strong>Name:</strong> {customer_name}</li>
                <li><strong>Phone:</strong> {customer_phone}</li>
                <li><strong>Email:</strong> {customer_email or 'Not provided'}</li>
            </ul>
            <h3>Visit Details:</h3>
            <ul>
                <li><strong>Date:</strong> {date}</li>
                <li><strong>Time:</strong> {time}</li>
                <li><strong>Property Details:</strong> {property_details}</li>
            </ul>
            <p>Please ensure you arrive 10 minutes early.</p>
        </body>
    </html>
    """
    send_email(settings.agent_email, agent_subject, agent_body)
