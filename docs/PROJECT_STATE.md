# Project State: Lead Automation Agent

## 1. Executive Summary
A headless automation service connecting Monday.com and WhatsApp (Meta API). The system listens for new leads, sends an immediate welcome message, and schedules a conditional follow-up 24 hours later if the lead has not replied.

## 2. Master Checklist

### Phase 1: Foundation & Infrastructure
- [x] Initialize Git repository
- [x] Configure Environment Variables (Pydantic Settings)
- [x] Setup Logging (Structlog/Standard)
- [x] Setup SQLite Database with SQLAlchemy/Alembic

### Phase 2: Core Logic (The "Happy Path")
- [x] Implement Webhook Endpoint (`POST /webhook/monday`)
- [x] Implement Meta API Client (Send Message)
- [x] Implement Monday API Client (Fetch Data / Update Status)
- [x] Connect: Webhook -> Fetch -> Send -> Update Status to "נשלחה הודעה"

### Phase 3: The Scheduler (24h Logic)
- [x] Create `Lead` Database Model
- [x] Implement APScheduler (Background Polling)
- [x] Logic: Check DB -> **Safety Check (Monday Status)** -> Send Follow-up
- [x] Logic: Update Status to "אין מענה 1"
- [x] Time Window Logic (08:00 - 21:00 execution only)

### Phase 4: Feedback Loop
- [x] Implement Webhook Endpoint (`POST /webhook/meta`) for Incoming Messages
- [x] Logic: Update Monday Status to "נקבעה שיחת מכירה" (or manual intervention needed) on reply.
*Note: The exact status for a general reply isn't specified, but implies human takeover.*

## 3. Change Log
- **2026-01-31**: Phase 4 (Feedback Loop) complete - Meta webhook endpoint for incoming messages, lead reply handling.
- **2026-01-31**: Phase 3 (Scheduler) complete - APScheduler with 10-minute polling, Safety Check, time window logic (08:00-21:00 Israel Time).
- **2026-01-31**: Phase 2 (Core Logic) complete - Monday webhook, Meta API client, Monday API client, lead processing service.
- **2026-01-31**: Phase 1 (Foundation) complete - project structure, config, logging, database models, session manager, FastAPI app, Alembic migrations.
- **2026-01-31**: Initial PRD Analysis and Stack Selection complete. Architecture validated.
