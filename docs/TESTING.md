# 🧪 Testing the Automation

Quick commands to test the lead automation flow.

---

## Prerequisites

- App deployed and running on Railway
- Monday.com board with a lead item
- Your phone number added as Meta test recipient

---

## Step 1: Simulate Monday Webhook (Create Lead)

Replace `ITEM_ID` with your Monday.com item ID (from the item's URL).

```powershell
# PowerShell
$itemId = "2684334467"
Invoke-RestMethod -Uri "https://giliauto-production.up.railway.app/webhook/monday" `
  -Method POST `
  -ContentType "application/json" `
  -Body "{`"event`":{`"pulseId`":$itemId,`"boardId`":5090056144,`"groupId`":`"topics`"}}"
```

```bash
# Bash / cURL
curl -X POST "https://giliauto-production.up.railway.app/webhook/monday" \
  -H "Content-Type: application/json" \
  -d '{"event":{"pulseId":"YOUR_MONDAY_ITEM_ID","boardId":5090056144,"groupId":"topics"}}'
```

**Expected Response:**
```json
{"status": "processed"}
```

---

## Step 2: Trigger Scheduler (Send Messages)

```powershell
# PowerShell
Invoke-RestMethod -Uri "https://giliauto-production.up.railway.app/admin/trigger-scheduler?secret=gilad-token" -Method POST
```

```bash
# Bash / cURL
curl -X POST "https://giliauto-production.up.railway.app/admin/trigger-scheduler?secret=gilad-token"
```

**Expected Response:**
```json
{"status": "triggered", "message": "Scheduler job executed"}
```

---

## Step 3: Check Health

```powershell
# PowerShell
Invoke-RestMethod -Uri "https://giliauto-production.up.railway.app/health"
```

```bash
# Bash / cURL
curl "https://giliauto-production.up.railway.app/health"
```

**Expected Response:**
```json
{"status": "healthy"}
```

---

## Full Test Flow

1. **Create item in Monday.com** with phone number and status "לייד חדש"
2. **Run Step 1** → Creates lead in database
3. **Run Step 2** → Sends WhatsApp message
4. **Check your phone** → Should receive message
5. **Reply to message** → Monday status should update

---

## Troubleshooting

| Issue | Command to Debug |
|-------|------------------|
| Check if app is running | `curl https://giliauto-production.up.railway.app/` |
| Check logs | Railway Dashboard → Logs tab |
| Webhook not working | Verify Monday item has phone number in correct column |
