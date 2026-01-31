# Technical Specification

## 1. Technology Stack
- **Runtime:** Python 3.11+
- **Framework:** FastAPI (Async)
- **Database:** SQLite (Production: Railway Volume / Local: file)
- **ORM:** SQLAlchemy (Async) + Alembic (Migrations)
- **Scheduling:** APScheduler (AsyncIOScheduler)
- **HTTP Client:** Httpx (Async)
- **Hosting:** Railway

## 2. Architecture Diagram

[Monday.com] --(Webhook: Create Item)--> [FastAPI /webhook/monday]
                                                |
                                                v
                                         [Insert into SQLite]
                                                |
                                                v
                                         [Send WhatsApp Msg 1]
                                                |
                                                v
                                    [Update Monday: "נשלחה הודעה"]

[Scheduler] --(Every 10m)--> [Check SQLite (timestamp < now-24h)]
                                      |
                                      v
                        [Safety Check: Query Monday Status]
                                      |
                      (If status == "נשלחה הודעה")
                                      |
                                      v
                             [Send WhatsApp Msg 2]
                                      |
                                      v
                           [Update Monday: "אין מענה 1"]

## 3. Monday.com Configuration

### 3.1 Trigger
- **Type:** Webhook (Create Item)
- **Board:** Specific Board (ID via Env Var)
- [cite_start]**Group:** "Leads - whatsapp automation" [cite: 9]

### 3.2 Status Mapping (Hebrew)
The system MUST strictly use these strings for status updates:
1.  `"לייד חדש"` (New Lead - Initial State)
2.  `"נשלחה הודעה"` (Message Sent - After 1st Msg)
3.  `"אין מענה 1"` (No Answer 1 - After 24h Follow-up)
4.  `"אין מענה 2"` (No Answer 2 - Final Timeout state)
5.  `"נקבעה שיחת מכירה"` (Meeting Set - Manual/Goal state)

## 4. Data Schema (SQLite)

### Table: `leads`
| Column | Type | Notes |
| :--- | :--- | :--- |
| `id` | Integer (PK) | Auto-inc |
| `monday_item_id` | String | Unique, Indexed (The Monday Item ID) |
| `phone_number` | String | E.164 Format |
| `lead_name` | String | |
| `created_at` | DateTime | UTC |
| `status` | String | Internal tracking (matches Monday status) |
| `followup_due_at` | DateTime | Created_at + 24h |
| `is_done` | Boolean | True if replied or timed out |

## 5. Key Logic Protocols

### 5.1 The "Safety Check"
Before sending the 24h follow-up, the system **MUST** query Monday.com for the current status of the item.
* **IF** status is `"נשלחה הודעה"` -> **PROCEED** (Send Msg 2).
* **IF** status is ANY OTHER VALUE (e.g., `"נקבעה שיחת מכירה"`) -> **ABORT** (Do not send, mark as done in DB).

### 5.2 Time Window
The 2nd message must only be sent between **08:00 and 21:00** (Israel Time).
* *Logic:* If `followup_due_at` is reached but time is outside window -> Wait until 08:00 next day.

## 6. Environment Variables
- `MONDAY_API_KEY`: Secret
- `MONDAY_BOARD_ID`: String
- `META_API_TOKEN`: Secret
- `META_PHONE_ID`: String
- `DATABASE_URL`: `sqlite+aiosqlite:///./data/leads.db`
- `ADMIN_SECRET`: For manual triggers/docs