# Lead Automation Service

A headless automation service that connects Monday.com and WhatsApp (Meta Business API) to automate lead management and follow-up messaging.

## Use Case

When a new lead is created in a Monday.com board:

1. **Immediate Action**: A welcome WhatsApp message is sent automatically
2. **Status Update**: The lead status in Monday.com is updated to "נשלחה הודעה" (Message Sent)
3. **Scheduled Follow-up**: 24 hours later, if the lead hasn't replied, a follow-up message is sent (between 08:00-21:00 Israel Time)
4. **Reply Handling**: If the lead replies to any message, the status is updated to "נקבעה שיחת מכירה" (Meeting Set)

## Project Structure

```
src/
├── core/               # Configuration, logging, exceptions
│   ├── config.py      # Pydantic Settings for environment variables
│   ├── logging.py     # Structlog configuration
│   └── exceptions.py  # Custom exception classes
├── db/                # Database layer
│   ├── models.py      # SQLAlchemy models (Lead)
│   └── session.py     # Async session management
├── services/          # Business logic layer
│   ├── monday.py      # Monday.com GraphQL API client
│   ├── meta.py        # Meta WhatsApp Business API client
│   ├── lead.py        # Lead processing orchestration
│   └── scheduler.py   # APScheduler for background jobs
├── routers/           # Webhook endpoints
│   ├── monday.py      # POST /webhook/monday (receives new leads)
│   └── meta.py        # GET/POST /webhook/meta (verification & replies)
├── schemas/           # Pydantic validation models
│   ├── monday.py      # Monday webhook payload schemas
│   └── meta.py        # Meta webhook payload schemas
└── main.py            # FastAPI app entrypoint

tests/                 # Unit and integration tests
scripts/               # Utility scripts
alembic/              # Database migrations
data/                 # SQLite database location
```

## Technology Stack

- **Runtime**: Python 3.11+
- **Framework**: FastAPI (async)
- **Database**: SQLite with SQLAlchemy (async) + Alembic migrations
- **Scheduling**: APScheduler (AsyncIOScheduler)
- **HTTP Client**: Httpx (async)
- **External APIs**: Monday.com (GraphQL), Meta WhatsApp (REST)
- **Logging**: Structlog
- **Configuration**: Pydantic Settings

## Installation

### Prerequisites

- Python 3.11+
- pip or conda
- Monday.com account with API access
- Meta/Facebook Business account with WhatsApp Business API access

### Setup

1. Clone the repository
   ```bash
   git clone <repo-url>
   cd Gilad\ Automation
   ```

2. Create a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file from the example
   ```bash
   cp .env.example .env
   ```

5. Configure environment variables (see below)

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and fill in the required values:

#### Monday.com Configuration

**MONDAY_API_KEY**
- Get it from: Monday.com → Integrations → API & Apps → API Token
- Required: Yes
- Format: String (secret)
- Example: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

**MONDAY_BOARD_ID**
- Get it from: The board URL (e.g., `https://your-account.monday.com/boards/12345...`)
- Look for the numeric ID in the URL after `/boards/`
- Required: Yes
- Format: String (numeric)
- Example: `1234567890`

#### Meta WhatsApp Configuration

**META_API_TOKEN**
- Get it from: Meta Business Suite → Settings → Business Accounts → System User Access Tokens
- Or: Temporarily generate a token at facebook.com/developers
- Required: Yes
- Format: String (secret)
- Permissions needed: `whatsapp_business_messaging`
- Example: `EAABBCcc1234...`

**META_PHONE_ID**
- Get it from: Meta Business Suite → WhatsApp → Phone Numbers → Copy the Phone Number ID
- Required: Yes
- Format: String (numeric)
- Example: `123456789012345`

#### Database Configuration

**DATABASE_URL**
- Default: `sqlite+aiosqlite:///./data/leads.db`
- Format: SQLAlchemy async connection string
- For SQLite (local): `sqlite+aiosqlite:///./data/leads.db`
- For PostgreSQL (production): `postgresql+asyncpg://user:pass@localhost/dbname`

#### Admin Configuration

**ADMIN_SECRET**
- Used for Meta webhook verification
- Generate a strong random string for production
- Default: `change-me-in-production`
- Example: `your-secure-random-string-here`

#### App Settings

**ENVIRONMENT**
- Options: `development`, `production`
- Default: `development`
- Controls API documentation visibility and debug features

**LOG_LEVEL**
- Options: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- Default: `INFO`

## Running the Application

### Development

```bash
uvicorn src.main:app --reload
```

The app will start at `http://localhost:8000`

- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### Production

```bash
# Run migrations
alembic upgrade head

# Start with gunicorn (install: pip install gunicorn)
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## API Endpoints

### Public Endpoints

**GET `/`**
- Root endpoint
- Returns: `{"message": "Lead Automation Service is running"}`

**GET `/health`**
- Health check
- Returns: `{"status": "healthy"}`

### Webhook Endpoints

**POST `/webhook/monday`**
- Receives new lead creation events from Monday.com
- Automatic response: Welcome message sent via WhatsApp
- Status updated to "נשלחה הודעה" in Monday.com

**GET `/webhook/meta`**
- Webhook verification from Meta
- Query parameters: `hub.mode`, `hub.verify_token`, `hub.challenge`

**POST `/webhook/meta`**
- Receives incoming WhatsApp messages and status updates
- Automatically marks leads as replied
- Updates Monday.com status to "נקבעה שיחת מכירה"

## Workflow

### 1. New Lead (Monday.com Webhook)

```
Monday.com Event (Item Created)
        ↓
/webhook/monday receives event
        ↓
Fetch lead details from Monday API:
  - Phone number
  - Lead name
        ↓
Send WhatsApp welcome message via Meta API
        ↓
Update Monday status → "נשלחה הודעה"
        ↓
Store lead in SQLite database with:
  - followup_due_at = now + 24 hours
  - is_done = false
```

### 2. Follow-up Processing (Scheduler - Every 10 minutes)

```
APScheduler Job (Every 10 minutes)
        ↓
Check if within send window (08:00 - 21:00 Israel Time)
        ↓
Query database for leads with:
  - followup_due_at ≤ now
  - is_done = false
        ↓
For each lead:
  ├─ Safety Check: Query Monday for current status
  │
  ├─ IF status is "נשלחה הודעה":
  │   ├─ Send follow-up WhatsApp message
  │   ├─ Update Monday status → "אין מענה 1"
  │   └─ Mark lead as done
  │
  └─ ELSE (status changed):
      └─ Abort (human intervention detected)
           Mark lead as done
```

### 3. Lead Reply (Meta Webhook)

```
WhatsApp message received
        ↓
/webhook/meta receives message
        ↓
Find lead by phone number in database
        ↓
Mark lead as replied (is_done = true)
        ↓
Update Monday status → "נקבעה שיחת מכירה"
```

## Status Flow (Hebrew)

| Status | Meaning | When | Auto-set by |
|--------|---------|------|-------------|
| `לייד חדש` | New Lead | Initial state | Manual in Monday |
| `נשלחה הודעה` | Message Sent | After 1st WhatsApp | Monday webhook handler |
| `אין מענה 1` | No Answer 1 | After 24h follow-up | Scheduler |
| `אין מענה 2` | No Answer 2 | Final timeout | Manual intervention |
| `נקבעה שיחת מכירה` | Meeting Set | Lead replied | Meta webhook handler |

## Error Handling

Per STANDARDS.md:

- **Webhooks**: Never crash. Log error → Return 200 OK to provider (to stop retries) → Alert via logs
- **External APIs**: Handle `httpx.HTTPError` gracefully with retry logic if needed
- **Database**: Rollback on error, log details

## Database Schema

### Table: `leads`

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | Integer | PK, AutoInc | Primary key |
| `monday_item_id` | String | UNIQUE, INDEX | Monday.com item ID (source of truth) |
| `phone_number` | String | — | E.164 format (e.g., +972501234567) |
| `lead_name` | String | — | Lead name from Monday |
| `created_at` | DateTime | — | UTC timestamp of lead creation |
| `status` | String | — | Current status (Hebrew string) |
| `followup_due_at` | DateTime | INDEX | When 24h follow-up is due |
| `is_done` | Boolean | INDEX | True if replied or timed out |

## Time Window Logic

The 24-hour follow-up is only sent between **08:00 and 21:00 (Israel Time)**.

- If `followup_due_at` is reached outside this window, the scheduler waits until 08:00 the next day
- Timezone: `Asia/Jerusalem` (pytz)
- Configurable via `SEND_WINDOW_START_HOUR` and `SEND_WINDOW_END_HOUR` in config

## Logging

Structured logging with structlog:

- Development: Pretty console output with colors
- Production: JSON output for log aggregation

Log entries include:

- Request/response metadata
- Lead and item IDs for tracing
- Error details with context
- Performance info (API call durations)

Example:
```json
{
  "event": "lead_processed_successfully",
  "lead_id": 42,
  "phone": "+972501234567",
  "timestamp": "2026-01-31T12:34:56.789Z"
}
```

## Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=src

# Watch mode
pytest-watch
```

## Deployment

### Railway (Recommended)

1. Push to GitHub
2. Connect Railway to your repository
3. Set environment variables in Railway dashboard
4. Deploy

Railway will:
- Use SQLite with persistent volume for `data/`
- Auto-scale based on load
- Monitor health via `/health` endpoint

### Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t lead-automation .
docker run -p 8000:8000 --env-file .env lead-automation
```

## Troubleshooting

### Lead not sending

1. Check logs: `LOG_LEVEL=DEBUG`
2. Verify Monday API key has correct permissions
3. Verify phone number is in E.164 format (e.g., +972...)
4. Check Meta API token is active

### Scheduler not running

1. Check `scheduler_started` in logs
2. Verify APScheduler is installed: `pip install apscheduler`
3. Check database permissions

### Webhook not receiving events

1. Verify webhook URLs are correct in Monday.com and Meta settings
2. Check firewall/network access
3. Verify `ADMIN_SECRET` matches Meta webhook verification token

### Phone number format errors

Meta WhatsApp API expects E.164 format:
- ✅ `+972501234567`
- ❌ `0501234567` (missing country code)
- ❌ `972501234567` (missing +)

Use international format with country code.

## Contributing

Follow STANDARDS.md for code style:
- Async/await for all I/O
- 100% type hints
- English codebase (Hebrew only for Monday status strings)
- Minimize dependencies

## License

TBD

## Support

For issues, check the logs and refer to the troubleshooting section above.
