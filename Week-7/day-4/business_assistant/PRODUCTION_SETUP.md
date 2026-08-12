# Production Setup Guide: Business Automation

To transform the local development codebase into a fully functioning, production-ready system, you need to configure external services (Database, Calendar, Email, and n8n). Follow this step-by-step guide.

---

## 1. CRM Database Configuration (PostgreSQL)
By default, the code uses SQLite (`sqlite:///./crm.db`) for easy testing. For production, you **must** use PostgreSQL for concurrency and data integrity.

**Steps:**
1. Provision a PostgreSQL database (e.g., AWS RDS, Supabase, Railway).
2. Get the connection string.
3. Update your `.env` file in the project root:
   ```env
   DATABASE_URL=postgresql://user:password@host:port/dbname
   ```
   *The SQLAlchemy engine in `src/crm/repository.py` will automatically read this and create the tables (`Customer`, `Appointment`, `CallLog`) on boot.*

---

## 2. Google Calendar API (Service Account)
To prevent the application from requiring a human to log in every time, we use a **Service Account** to manage the calendar.

**Steps:**
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new Project and enable the **Google Calendar API**.
3. Go to **IAM & Admin > Service Accounts** and create a new Service Account.
4. Under "Keys", click **Add Key > Create New Key > JSON**. This will download a `.json` file to your computer.
5. **CRITICAL:** Go to your actual Google Calendar (calendar.google.com), click Settings > "Share with specific people or groups", and add the email address of the Service Account (it looks like `name@project-id.iam.gserviceaccount.com`) giving it **"Make changes to events"** permissions.
6. Rename the downloaded JSON file to `credentials.json` and place it in your `Week-7/day-4/business_assistant/` directory.

---

## 3. Async HTML Email Sender (SMTP)
To send the professional HTML notifications automatically to your employees without paying for expensive APIs, use Gmail's App Passwords.

**Steps:**
1. Go to your company's Google Account settings.
2. Enable **2-Step Verification**.
3. Search for **App Passwords** in the account settings.
4. Create an App Password for "Mail". Google will give you a 16-character password (e.g., `abcd efgh ijkl mnop`).
5. Update your `.env` file:
   ```env
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your.company.email@gmail.com
   SMTP_PASSWORD=abcdefghijklmnop
   ```
   *The `EmailSender` in `src/email/sender.py` will securely use these credentials via TLS.*

---

## 4. n8n Workflow Automation
n8n acts as the background orchestrator for complex fallback logic (like retrying CRM updates if the DB goes down).

**Steps:**
1. Install n8n. If you use Docker, run: `docker run -it --rm --name n8n -p 5678:5678 -v ~/.n8n:/home/node/.n8n n8nio/n8n`
2. Open `http://localhost:5678` in your browser.
3. Go to **Workflows**, click the dropdown menu in the top right, and select **Import from File**.
4. Select the `Week-7/day-4/business_assistant/n8n/real_estate_workflow.json` file.
5. Double-click the **Webhook** node inside n8n to copy its "Test URL" or "Production URL".
6. Update your `.env` file with that URL:
   ```env
   N8N_WEBHOOK_URL=http://localhost:5678/webhook/real-estate
   ```
7. Finally, flip the switch in n8n from "Inactive" to "Active" so it runs in the background continuously.

---

## Final Checklist
Before starting `uvicorn`, your `.env` should look like this:

```env
ENVIRONMENT=production
DATABASE_URL=postgresql://user:pass@host/db
GOOGLE_APPLICATION_CREDENTIALS=credentials.json
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=admin@yourcompany.com
SMTP_PASSWORD=your_16_char_app_password
N8N_WEBHOOK_URL=http://your-n8n-server.com/webhook/real-estate
```
