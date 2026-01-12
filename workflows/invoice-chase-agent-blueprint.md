# Invoice Chase Agent - n8n Workflow Blueprint

## Overview
This workflow runs on a schedule (daily) to detect overdue invoices, evaluate each one through the escalation ladder, and send appropriate reminders with full validation and audit logging.

---

## Workflow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    INVOICE CHASE AGENT                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  TRIGGER: Schedule (daily at 9am)                               │
│     ↓                                                           │
│  GET: List Overdue Invoices (QuickBooks/Xero/Stripe)           │
│     ↓                                                           │
│  LOOP: For Each Invoice                                        │
│     ├→ GET: Customer Context (CRM)                             │
│     ├→ VALIDATE: Consent Flags                                 │
│     ├→ VALIDATE: Not Sent Recently                             │
│     ├→ VALIDATE: Still Overdue                                 │
│     ├→ DETERMINE: Escalation Stage                             │
│     ├→ IF: Stage 1-3 → Generate Message                        │
│     │    ├→ VALIDATE: Tone & Content                           │
│     │    ├→ IF Amount > Threshold → Human Task                 │
│     │    ├→ ELSE → Send Message                                │
│     │    └→ LOG: Audit Trail                                   │
│     └→ IF: Stage 4-5 → Create Human Task                       │
│                                                                 │
│  END: Update Metrics Dashboard                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Node-by-Node Implementation

### 1. TRIGGER: Schedule
**Node Type:** `Schedule Trigger`
**Configuration:**
```json
{
  "rule": {
    "interval": [{"field": "cronExpression", "expression": "0 9 * * *"}]
  },
  "timezone": "America/Los_Angeles"
}
```
**Purpose:** Runs daily at 9am to process overdue invoices

---

### 2. GET OVERDUE INVOICES
**Node Type:** `HTTP Request` or accounting system node (QuickBooks, Xero, etc.)

**For QuickBooks:**
```json
{
  "authentication": "oAuth2",
  "method": "GET",
  "url": "={{$env.ACCOUNTING_API_URL}}/invoices",
  "qs": {
    "status": "overdue",
    "orderBy": "dueDate"
  }
}
```

**Output Schema:**
```json
[
  {
    "invoice_id": "INV-001",
    "invoice_number": "2024-001",
    "customer_id": "CUST-123",
    "customer_name": "Acme Corp",
    "customer_email": "billing@acme.com",
    "amount": 1500.00,
    "due_date": "2024-01-01",
    "days_overdue": 10,
    "status": "overdue",
    "currency": "USD"
  }
]
```

---

### 3. LOOP: Split In Batches
**Node Type:** `SplitInBatches`
**Configuration:**
```json
{
  "batchSize": 1,
  "options": {}
}
```
**Purpose:** Process each invoice individually for proper error handling

---

### 4. GET CUSTOMER CONTEXT
**Node Type:** `HTTP Request` or CRM node (HubSpot, Salesforce, etc.)

**For HubSpot:**
```json
{
  "authentication": "oAuth2",
  "method": "GET",
  "url": "={{$env.CRM_API_URL}}/contacts/{{$json.customer_id}}",
  "qs": {
    "properties": ["payment_history", "communication_preferences", "consent_flags"]
  }
}
```

**Output Schema:**
```json
{
  "customer_id": "CUST-123",
  "payment_history": {
    "total_invoices": 24,
    "on_time_payments": 20,
    "late_payments": 4,
    "average_days_late": 5
  },
  "communication_preferences": {
    "preferred_channel": "email",
    "language": "en"
  },
  "consent_flags": {
    "can_email": true,
    "can_sms": true,
    "can_call": false
  },
  "relationship_status": "good",
  "last_reminder_sent_at": "2024-01-05T10:00:00Z"
}
```

---

### 5. MERGE DATA
**Node Type:** `Merge`
**Configuration:**
```json
{
  "mode": "combine",
  "mergeByFields": {
    "values": [
      {
        "field1": "customer_id",
        "field2": "customer_id"
      }
    ]
  }
}
```
**Purpose:** Combine invoice data with customer context

---

### 6. VALIDATOR: Consent Check
**Node Type:** `IF` condition
**Condition:**
```javascript
{{$json.consent_flags.can_email === true || $json.consent_flags.can_sms === true}}
```

**FALSE Branch:**
- Log violation
- Create human task
- Skip to next invoice

**TRUE Branch:**
- Continue to next validator

---

### 7. VALIDATOR: Duplicate Prevention
**Node Type:** `IF` condition
**Condition:**
```javascript
{{
  const lastSent = new Date($json.last_reminder_sent_at);
  const now = new Date();
  const hoursSince = (now - lastSent) / (1000 * 60 * 60);
  return hoursSince > 48;  // More than 48 hours since last reminder
}}
```

**FALSE Branch:**
- Log skip (sent too recently)
- Skip to next invoice

**TRUE Branch:**
- Continue processing

---

### 8. VALIDATOR: Still Overdue Check
**Node Type:** `HTTP Request` (re-check invoice status)
**Purpose:** Prevent race condition where invoice was just paid

```json
{
  "method": "GET",
  "url": "={{$env.ACCOUNTING_API_URL}}/invoices/{{$json.invoice_id}}"
}
```

**Then:** `IF` condition
```javascript
{{$json.status === 'overdue' || $json.status === 'unpaid'}}
```

---

### 9. DETERMINE ESCALATION STAGE
**Node Type:** `Function` or `Code` node

```javascript
const daysOverdue = $input.item.json.days_overdue;

let stage, channel, tone, template;

if (daysOverdue >= 1 && daysOverdue <= 7) {
  stage = '1_friendly_reminder';
  channel = 'email';
  tone = 'friendly';
  template = 'gentle_reminder';
} else if (daysOverdue >= 8 && daysOverdue <= 15) {
  stage = '2_second_notice';
  channel = 'email_sms';
  tone = 'professional';
  template = 'second_notice';
} else if (daysOverdue >= 16 && daysOverdue <= 30) {
  stage = '3_final_notice';
  channel = 'email_sms';
  tone = 'firm';
  template = 'final_notice';
} else if (daysOverdue >= 31 && daysOverdue <= 60) {
  stage = '4_human_escalation';
  channel = 'human_task';
} else {
  stage = '5_collections';
  channel = 'human_task';
}

return {
  ...item.json,
  escalation: {
    stage,
    channel,
    tone,
    template
  }
};
```

---

### 10. SWITCH: Route by Stage
**Node Type:** `Switch`

**Routes:**
- **Stage 1-3:** Generate & Send Message
- **Stage 4-5:** Create Human Task

---

### 11A. GENERATE MESSAGE (Stages 1-3)
**Node Type:** `AI Agent` or `HTTP Request` to Claude API

**For AI Agent approach:**
```json
{
  "model": "claude-sonnet-4-5",
  "systemPrompt": "You are a professional invoice recovery specialist. Generate a {{$json.escalation.tone}} reminder message for an overdue invoice. Use the template style: {{$json.escalation.template}}. Keep it professional, brief, and actionable.",
  "userPrompt": "Generate a {{$json.escalation.tone}} reminder for:\n\nCustomer: {{$json.customer_name}}\nInvoice: {{$json.invoice_number}}\nAmount: ${{$json.amount}}\nDays Overdue: {{$json.days_overdue}}\nPayment Link: {{$json.payment_link}}\n\nTemplate style: {{$json.escalation.template}}\nTone: {{$json.escalation.tone}}"
}
```

**Output:**
```json
{
  "subject": "Friendly Reminder: Invoice #2024-001",
  "body": "Hi Acme Corp,\n\nI hope...",
  "tone_score": 0.92
}
```

---

### 11B. VALIDATOR: Tone & Content Check
**Node Type:** `Function` node

```javascript
const message = $input.item.json.generated_message.body.toLowerCase();
const blockedWords = ['legal', 'lawsuit', 'court', 'attorney', 'sue', 'collections agency'];

const hasBlockedWords = blockedWords.some(word => message.includes(word));
const hasAllCaps = /[A-Z]{5,}/.test($input.item.json.generated_message.body);

if (hasBlockedWords || hasAllCaps) {
  return {
    validation: 'FAILED',
    reason: hasBlockedWords ? 'Contains legal/threatening language' : 'Contains excessive caps',
    action: 'block_and_escalate'
  };
}

return {
  validation: 'PASSED',
  ...item.json
};
```

---

### 12. IF: Amount Threshold Check
**Node Type:** `IF` condition
**Condition:**
```javascript
{{$json.amount > 10000}}
```

**TRUE:** Create human task (too risky to auto-send)
**FALSE:** Proceed to send message

---

### 13. SEND MESSAGE
**Node Type:** Depends on channel

**For Email (SendGrid):**
```json
{
  "authentication": "apiKey",
  "to": "{{$json.customer_email}}",
  "from": "{{$env.COMPANY_EMAIL}}",
  "subject": "{{$json.generated_message.subject}}",
  "text": "{{$json.generated_message.body}}",
  "customArgs": {
    "tracking_id": "{{$json.invoice_id}}_{{$json.escalation.stage}}_{{$now}}",
    "invoice_id": "{{$json.invoice_id}}",
    "customer_id": "{{$json.customer_id}}"
  }
}
```

**For SMS (Twilio):**
```json
{
  "authentication": "apiKey",
  "to": "{{$json.customer_phone}}",
  "from": "{{$env.TWILIO_PHONE}}",
  "body": "{{$json.generated_message.body_short}}",
  "statusCallback": "{{$env.WEBHOOK_URL}}/sms-status"
}
```

---

### 14. ADD INVOICE NOTE
**Node Type:** `HTTP Request` to accounting system

```json
{
  "method": "POST",
  "url": "={{$env.ACCOUNTING_API_URL}}/invoices/{{$json.invoice_id}}/notes",
  "body": {
    "note": "Reminder sent: {{$json.escalation.stage}} via {{$json.escalation.channel}}",
    "type": "reminder_sent",
    "metadata": {
      "message_id": "{{$json.message_id}}",
      "sent_at": "{{$now}}",
      "channel": "{{$json.escalation.channel}}"
    }
  }
}
```

---

### 15. AUDIT LOG
**Node Type:** `HTTP Request` to UMC or logging service

```json
{
  "method": "POST",
  "url": "={{$env.UMC_API_URL}}/sessions/{{$env.AGENT_SESSION_ID}}/notes",
  "body": {
    "content": {
      "event_type": "reminder_sent",
      "invoice_id": "{{$json.invoice_id}}",
      "customer_id": "{{$json.customer_id}}",
      "stage": "{{$json.escalation.stage}}",
      "channel": "{{$json.escalation.channel}}",
      "amount": "{{$json.amount}}",
      "days_overdue": "{{$json.days_overdue}}",
      "message_id": "{{$json.message_id}}",
      "validation_results": "{{$json.validation}}",
      "timestamp": "{{$now}}"
    },
    "scope": "project"
  }
}
```

---

### 16. CREATE HUMAN TASK (Stages 4-5 or Escalations)
**Node Type:** `HTTP Request` to Slack or task management

**For Slack:**
```json
{
  "method": "POST",
  "url": "https://slack.com/api/chat.postMessage",
  "headers": {
    "Authorization": "Bearer {{$env.SLACK_TOKEN}}"
  },
  "body": {
    "channel": "{{$env.SLACK_CHANNEL_COLLECTIONS}}",
    "text": "🚨 Invoice Requires Human Attention",
    "blocks": [
      {
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": "*Invoice:* {{$json.invoice_number}}\n*Customer:* {{$json.customer_name}}\n*Amount:* ${{$json.amount}}\n*Days Overdue:* {{$json.days_overdue}}\n*Stage:* {{$json.escalation.stage}}\n*Reason:* {{$json.escalation_reason}}"
        }
      },
      {
        "type": "actions",
        "elements": [
          {
            "type": "button",
            "text": {"type": "plain_text", "text": "View Invoice"},
            "url": "{{$env.ACCOUNTING_URL}}/invoices/{{$json.invoice_id}}"
          },
          {
            "type": "button",
            "text": {"type": "plain_text", "text": "View Customer"},
            "url": "{{$env.CRM_URL}}/contacts/{{$json.customer_id}}"
          }
        ]
      }
    ]
  }
}
```

---

### 17. UPDATE METRICS
**Node Type:** `Function` node (aggregate at end of workflow)

```javascript
// Count successes, failures, amounts
const results = $input.all();

const metrics = {
  run_date: new Date().toISOString().split('T')[0],
  total_processed: results.length,
  reminders_sent: results.filter(r => r.json.status === 'sent').length,
  escalations_to_human: results.filter(r => r.json.escalation?.stage?.includes('human')).length,
  total_amount_at_risk: results.reduce((sum, r) => sum + (r.json.amount || 0), 0),
  validation_failures: results.filter(r => r.json.validation === 'FAILED').length,
  by_stage: {
    stage_1: results.filter(r => r.json.escalation?.stage === '1_friendly_reminder').length,
    stage_2: results.filter(r => r.json.escalation?.stage === '2_second_notice').length,
    stage_3: results.filter(r => r.json.escalation?.stage === '3_final_notice').length,
    stage_4: results.filter(r => r.json.escalation?.stage === '4_human_escalation').length,
    stage_5: results.filter(r => r.json.escalation?.stage === '5_collections').length
  }
};

return [{ json: metrics }];
```

---

### 18. SAVE METRICS TO DATABASE
**Node Type:** `HTTP Request` or database node

```json
{
  "method": "POST",
  "url": "={{$env.METRICS_API_URL}}/invoice-chase/daily",
  "body": "{{$json}}"
}
```

---

### 19. ERROR HANDLING
**Node Type:** `Error Trigger` workflow

**Setup:**
- Create separate workflow triggered on errors
- Log error details to UMC
- Send alert to admin Slack
- Retry logic for transient failures

```json
{
  "trigger": "error",
  "retryAttempts": 3,
  "retryDelay": 300,
  "continueOnFail": true
}
```

---

## Environment Variables Required

```bash
# Accounting System
ACCOUNTING_API_URL=https://api.quickbooks.com/v3
ACCOUNTING_API_KEY=qb_xxx

# CRM System
CRM_API_URL=https://api.hubspot.com
CRM_API_KEY=hs_xxx

# Messaging
SENDGRID_API_KEY=SG.xxx
TWILIO_ACCOUNT_SID=ACxxx
TWILIO_AUTH_TOKEN=xxx
TWILIO_PHONE=+15551234567
COMPANY_EMAIL=billing@yourcompany.com

# AI
ANTHROPIC_API_KEY=sk-ant-xxx

# Alerting
SLACK_TOKEN=xoxb-xxx
SLACK_CHANNEL_COLLECTIONS=C12345

# UMC Memory
UMC_API_URL=http://localhost:3000
AGENT_SESSION_ID=invoice-chase-agent-prod

# Metrics
METRICS_API_URL=http://localhost:4000

# URLs for human tasks
ACCOUNTING_URL=https://your-qb-instance.com
CRM_URL=https://your-crm.com

# Risk Thresholds
AUTO_SEND_EMAIL_MAX_AMOUNT=5000
AUTO_SEND_SMS_MAX_AMOUNT=2000
REQUIRES_HUMAN_REVIEW_AT=10000
```

---

## Testing Checklist

- [ ] Test with paid invoice (should skip)
- [ ] Test with no email consent (should block)
- [ ] Test with sent within 48h (should skip)
- [ ] Test each escalation stage (1-5)
- [ ] Test amount threshold trigger
- [ ] Test tone validator with caps/legal words
- [ ] Test message generation quality
- [ ] Test audit logging completeness
- [ ] Test error handling (API down scenarios)
- [ ] Test metrics accuracy
- [ ] Load test with 100+ invoices

---

## Deployment Steps

1. **Import workflow to n8n**
2. **Configure all credentials (OAuth connections)**
3. **Set environment variables**
4. **Test in development mode with test data**
5. **Run acceptance tests (see evaluation harness)**
6. **Deploy to production**
7. **Monitor first 3 runs manually**
8. **Enable kill switch monitoring**
9. **Set up weekly metrics reports**

---

## Next: Customer Dashboard

Once workflow is deployed, build customer dashboard showing:
- Total overdue amount recovered
- DSO trend (before/after)
- Recovery rate by stage
- Human hours saved
- ROI calculation

This proves value and justifies $499/month subscription.
