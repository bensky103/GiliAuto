# 🚀 GiliAuto - Customer Setup Guide

This guide walks you through setting up the WhatsApp Lead Automation system for production use. Follow each step carefully.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Part 1: Meta Business Account Setup](#part-1-meta-business-account-setup)
3. [Part 2: WhatsApp Business Setup](#part-2-whatsapp-business-setup)
4. [Part 3: Create Developer App](#part-3-create-developer-app)
5. [Part 4: Configure WhatsApp API](#part-4-configure-whatsapp-api)
6. [Part 5: Create Message Templates](#part-5-create-message-templates)
7. [Part 6: Configure Webhook](#part-6-configure-webhook)
8. [Part 7: Billing Setup](#part-7-billing-setup)
9. [Part 8: Monday.com Configuration](#part-8-mondaycom-configuration)
10. [Part 9: Provide Credentials to Developer](#part-9-provide-credentials-to-developer)
11. [Part 10: Testing](#part-10-testing)
12. [Appendix: Troubleshooting](#appendix-troubleshooting)

---

## Prerequisites

Before starting, you need:

- [ ] A Facebook personal account (for admin access)
- [ ] A business phone number (NOT currently registered on WhatsApp)
- [ ] A credit card for billing
- [ ] Access to your Monday.com board
- [ ] About 30-60 minutes to complete setup

---

## Part 1: Meta Business Account Setup

### Step 1.1: Create Meta Business Account

1. Go to **[business.facebook.com](https://business.facebook.com/)**
2. Click **"Create Account"** (or log in if you have one)
3. Enter your business details:
   - **Business name**: Your company name
   - **Your name**: Your full name
   - **Business email**: Your business email
4. Click **"Submit"**
5. **Verify your email** by clicking the link sent to you

### Step 1.2: Complete Business Information

1. In Meta Business Suite, go to **Settings** (gear icon)
2. Click **"Business Info"**
3. Fill in:
   - Business address
   - Business phone number
   - Business website (optional)
4. Click **"Save"**

---

## Part 2: WhatsApp Business Setup

### Step 2.1: Add WhatsApp to Your Business

1. In Meta Business Suite, click **"All Tools"** (grid icon)
2. Find and click **"WhatsApp Manager"**
3. Click **"Add WhatsApp Account"** or **"Get Started"**
4. Follow the prompts to create a WhatsApp Business Account

### Step 2.2: Add Your Business Phone Number

1. In WhatsApp Manager, go to **"Phone Numbers"**
2. Click **"Add Phone Number"**
3. Enter your business phone number (with country code)
4. Choose verification method: **SMS** or **Voice Call**
5. Enter the verification code received
6. ✅ Your phone number is now connected!

> ⚠️ **Important**: This phone number will be used to send WhatsApp messages to your leads. It cannot be used for personal WhatsApp.

---

## Part 3: Create Developer App

### Step 3.1: Access Meta for Developers

1. Go to **[developers.facebook.com](https://developers.facebook.com/)**
2. Click **"Get Started"** or **"My Apps"** (top right)
3. If prompted, accept the Developer Terms

### Step 3.2: Create New App

1. Click **"Create App"**
2. Select **"Other"** → Click **"Next"**
3. Select **"Business"** → Click **"Next"**
4. Fill in:
   - **App name**: `Lead Automation` (or your preferred name)
   - **Contact email**: Your email
   - **Business Account**: Select the account you created
5. Click **"Create App"**
6. Enter your Facebook password to confirm

### Step 3.3: Add WhatsApp Product

1. On your app dashboard, scroll to **"Add products to your app"**
2. Find **"WhatsApp"** and click **"Set up"**
3. Select your WhatsApp Business Account → Click **"Continue"**

---

## Part 4: Configure WhatsApp API

### Step 4.1: Get Your API Credentials

1. In your app, go to **"WhatsApp"** → **"API Setup"** (left sidebar)
2. You'll see important information:

| Credential | Where to Find | What It Looks Like |
|------------|---------------|-------------------|
| **Phone Number ID** | Under "From" dropdown | `123456789012345` |
| **WhatsApp Business Account ID** | Top of page | `987654321098765` |
| **Temporary Access Token** | "Temporary access token" section | Long string starting with `EAA...` |

3. **Copy and save these values** - you'll need them later!

### Step 4.2: Generate Permanent Access Token

The temporary token expires in 24 hours. For production, create a permanent token:

1. Go to **"Business Settings"** → **"System Users"**
2. Click **"Add"** to create a new system user:
   - **Name**: `Lead Automation Bot`
   - **Role**: Admin
3. Click **"Create System User"**
4. Click on the user → **"Add Assets"**
5. Select **"Apps"** → Select your app → Toggle **"Full Control"**
6. Click **"Save Changes"**
7. Click **"Generate New Token"**
8. Select your app
9. Select these permissions:
   - ✅ `whatsapp_business_messaging`
   - ✅ `whatsapp_business_management`
10. Set expiration to **"Never"** (or 60 days if required)
11. Click **"Generate Token"**
12. **Copy and save this token securely!** (You won't see it again)

---

## Part 5: Create Message Templates

WhatsApp requires pre-approved templates for outbound messages.

### Step 5.1: Access Message Templates

1. Go to **"WhatsApp Manager"** or **"WhatsApp"** → **"Message Templates"**
2. Click **"Create Template"**

### Step 5.2: Create Welcome Template

| Field | Value |
|-------|-------|
| **Template name** | `lead_welcome` |
| **Category** | `Marketing` |
| **Language** | `Hebrew` (or your language) |

**Body text**:
```
שלום {{1}}! 👋
תודה שפנית אלינו.
נציג יחזור אליך בהקדם.
```

- `{{1}}` is a placeholder for the lead's name
- Click **"Submit"**

### Step 5.3: Create Follow-up Template

| Field | Value |
|-------|-------|
| **Template name** | `lead_followup` |
| **Category** | `Marketing` |
| **Language** | `Hebrew` (or your language) |

**Body text**:
```
שלום {{1}},
שמנו לב שלא הספקת לחזור אלינו.
האם תרצה שנתקשר אליך?
```

- Click **"Submit"**

### Step 5.4: Wait for Approval

- Templates are usually approved within **minutes to a few hours**
- You'll see the status change from "Pending" to "Approved" ✅
- **Do not proceed until templates are approved!**

---

## Part 6: Configure Webhook

The webhook allows the app to receive messages from WhatsApp.

### Step 6.1: Navigate to Webhook Configuration

1. In your Meta Developer App, go to **"WhatsApp"** → **"Configuration"**
2. Find the **"Webhook"** section
3. Click **"Edit"**

### Step 6.2: Enter Webhook Details

| Field | Value |
|-------|-------|
| **Callback URL** | `https://your-app-url.up.railway.app/webhook/meta` |
| **Verify Token** | Use the same value as your `ADMIN_SECRET` |

> 📝 **Note**: The callback URL will be provided by your developer based on your deployment. The verify token must exactly match the `ADMIN_SECRET` environment variable.

### Step 6.3: Verify Webhook

1. Click **"Verify and Save"**
2. If successful, you'll see a green checkmark ✅
3. If failed, contact your developer

### Step 6.4: Subscribe to Messages

1. After verification, find **"Webhook fields"**
2. Click **"Manage"**
3. Find **"messages"** and toggle it **ON** ✅
4. Click **"Done"**

---

## Part 7: Billing Setup

You need to set up billing to send messages to customers.

### Step 7.1: WhatsApp Pricing Overview

| Message Type | Cost (approximate) |
|--------------|-------------------|
| **Business-initiated** (templates) | ~$0.05-0.15 per message |
| **User-initiated** (replies) | Free (within 24h window) |

> Prices vary by country. See [Meta WhatsApp Pricing](https://developers.facebook.com/docs/whatsapp/pricing)

### Step 7.2: Add Payment Method

1. Go to **"WhatsApp Manager"** → **"Payment Settings"**
   - Or: **"Business Settings"** → **"Payments"**
2. Click **"Add Payment Method"**
3. Enter your credit card details:
   - Card number
   - Expiration date
   - CVV
   - Billing address
4. Click **"Save"**

### Step 7.3: Set Spending Limits (Optional)

1. In Payment Settings, find **"Spending Limits"**
2. Set a monthly limit to control costs
3. You'll be notified when approaching the limit

---

## Part 8: Monday.com Configuration

### Step 8.1: Get Monday.com API Key

1. Log in to **[monday.com](https://monday.com)**
2. Click your **profile picture** (bottom-left)
3. Go to **"Developers"** → **"My Access Tokens"**
4. Click **"Show"** or generate a new token
5. **Copy the API key**

### Step 8.2: Get Board ID

1. Open the board you want to use for leads
2. Look at the URL: `https://monday.com/boards/1234567890`
3. The number after `/boards/` is your **Board ID**

### Step 8.3: Identify Column IDs

Your board needs these columns:

| Column Purpose | Example Title | How to Find ID |
|---------------|---------------|----------------|
| **Phone number** | "טלפון" | Click column → Settings → Copy ID |
| **Status** | "סטטוס" | Click column → Settings → Copy ID |

> 💡 **Tip**: Column IDs look like `phone_abc123` or just `status`

### Step 8.4: Set Up Webhook Automation

1. Open your Monday.com board
2. Click **"Integrate"** button (top right)
3. Search for **"Webhooks"**
4. Select **"When item is created, send a webhook"**
5. Configure:
   - **URL**: `https://your-app-url.up.railway.app/webhook/monday` (get exact URL from developer)
   - **Board**: Your leads board
   - **Group**: Select the specific group (optional)
6. Click **"Add to board"**

---

## Part 9: Provide Credentials to Developer

Send the following information **securely** to your developer:

### Required Credentials

```
# Monday.com
MONDAY_API_KEY=<your Monday API key>
MONDAY_BOARD_ID=<your board ID>
MONDAY_PHONE_COLUMN_ID=<phone column ID>
MONDAY_STATUS_COLUMN_ID=<status column ID>

# Meta WhatsApp
META_API_TOKEN=<your permanent access token>
META_PHONE_ID=<your phone number ID>

# Security (REQUIRED - used for webhook verification)
ADMIN_SECRET=<a strong random string, e.g., generate with: openssl rand -hex 32>

# Templates
WHATSAPP_WELCOME_TEMPLATE=lead_welcome
WHATSAPP_FOLLOWUP_TEMPLATE=lead_followup
WHATSAPP_TEMPLATE_LANGUAGE=he
```

> ⚠️ **Security**: Send these via secure channel (encrypted email, password manager sharing, etc.). Never share in plain email or chat!

---

## Part 10: Testing

### Step 10.1: Add Test Phone Number

1. In Meta Developer App → **"WhatsApp"** → **"API Setup"**
2. Find **"To"** section
3. Click **"Add phone number"**
4. Add your personal phone for testing
5. Verify with SMS code

### Step 10.2: Test the Flow

1. **Create a test lead** in Monday.com:
   - Add a new item in your leads group
   - Enter your test phone number
   - Set status to "לייד חדש" (or your initial status)

2. **Check for WhatsApp message**:
   - You should receive the welcome template message
   - Monday status should update to "נשלחה הודעה"

3. **Reply to the message**:
   - Send any reply to the WhatsApp message
   - Monday status should update to "נקבעה שיחת מכירה"

### Step 10.3: Verify Everything Works

| Step | Expected Result |
|------|-----------------|
| Create lead | Webhook fires, message sent |
| Receive message | Welcome template on WhatsApp |
| Monday updates | Status = "נשלחה הודעה" |
| Reply to message | Status = "נקבעה שיחת מכירה" |

---

## Appendix: Troubleshooting

### Common Issues

#### ❌ "Business Account locked"
**Cause**: Billing issue or policy violation
**Fix**: Check Meta Business Settings → Payments, or contact Meta support

#### ❌ "Template not approved"
**Cause**: Template contains prohibited content or formatting
**Fix**: Review template guidelines, edit and resubmit

#### ❌ "Webhook verification failed"
**Cause**: App not running or token mismatch
**Fix**: Confirm app is deployed, check verify token matches

#### ❌ "No phone number found"
**Cause**: Wrong column ID or empty phone field
**Fix**: Verify column ID matches your board

#### ❌ "Rate limit exceeded"
**Cause**: Too many messages sent too quickly
**Fix**: Wait and reduce sending rate

### Getting Help

- **Meta Support**: [Meta Business Help Center](https://www.facebook.com/business/help)
- **Monday.com Support**: [Monday Help Center](https://support.monday.com/)
- **Developer Contact**: [Your developer's contact info]

---

## ✅ Setup Checklist

Use this checklist to track your progress:

- [ ] Meta Business Account created
- [ ] Business info completed
- [ ] WhatsApp Business Account created
- [ ] Phone number added and verified
- [ ] Developer App created
- [ ] WhatsApp product added
- [ ] Permanent access token generated
- [ ] Welcome template created and approved
- [ ] Follow-up template created and approved
- [ ] Webhook configured and verified
- [ ] Messages webhook subscribed
- [ ] Payment method added
- [ ] Monday.com API key obtained
- [ ] Board ID identified
- [ ] Column IDs identified
- [ ] Monday webhook automation created
- [ ] Credentials sent to developer
- [ ] Test message sent and received
- [ ] Reply test completed

---

**Congratulations!** 🎉 Once all items are checked, your WhatsApp Lead Automation is ready for production!
