# Invoice Chase Agent v1.2.0 - Bulletproof Import Guide 🛡️

## 🎯 What You're Getting

**4 Production-Ready n8n Workflows:**
1. **Producer** - Fetches overdue invoices, enqueues for processing (fast, no timeouts)
2. **Worker** - Claims queue items, processes through full decision pipeline, sends reminders
3. **SendGrid Webhook** - Processes bounce/spam/unsubscribe events, updates suppression list
4. **Inbound Replies** - Handles customer responses (STOP, PAID, DISPUTE, etc.)

**Complete Postgres Schema:**
- 10 tables with race-condition-proof unique constraints
- Full audit trail
- Cost tracking
- Human task queue

**Security:**
- Race-condition immunity (unique constraints + dedupe buckets)
- Internal idempotency (because SendGrid is NOT idempotent)
- Fail-closed on all gates
- Full audit logging

---

## 📋 Prerequisites

### Required:
- [ ] n8n instance (cloud or self-hosted)
- [ ] PostgreSQL 14+ database
- [ ] Accounting system API (QuickBooks/Xero/Stripe)
- [ ] CRM API (HubSpot/Salesforce)
- [ ] SendGrid account + API key
- [ ] Twilio account (for SMS, optional)

### Recommended:
- [ ] Slack webhook for human task notifications
- [ ] Replit for database management
- [ ] Monitoring/alerting setup

---

## 🗄️ Step 1: Set Up Database (20 minutes)

### 1.1: Create Database

```bash
# On your Postgres server or Replit
createdb invoice_chase_production
```

### 1.2: Run Migrations

Execute the complete schema from the cogni map (see v1.2.0 Postgres migrations section).

Key tables created:
- `audit_events` - Complete audit trail
- `workflow_errors` - Dead-letter queue
- `suppression_list` - Do-not-contact registry
- `promise_to_pay` - Payment promises
- `reminder_sends` - Dedupe anchor + history
- `outbound_requests` - **Internal idempotency** (critical!)
- `human_tasks` - AR queue
- `cost_tracking` - Per-send accounting
- `invoice_queue` - Producer/worker queue
- `unsubscribe_tokens` - Compliance

### 1.3: Verify Tables

```sql
-- Should return 10 tables
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- Verify critical constraints
SELECT constraint_name, table_name
FROM information_schema.table_constraints
WHERE constraint_type = 'UNIQUE'
AND table_schema = 'public';
```

You should see:
- `uq_reminder_dedupe_bucket` on `reminder_sends`
- `uq_outbound_idempotency` on `outbound_requests`
- `uq_promise_to_pay_invoice` on `promise_to_pay`
- `uq_invoice_queue_item` on `invoice_queue`

**These constraints are your race-condition shields.** Don't skip them!

---

## 📥 Step 2: Import Workflows to n8n (10 minutes)

### 2.1: Import All 4 Workflows

1. Open n8n: `https://higgsai.app.n8n.cloud`
2. For each workflow file:
   - Click **"+"** → **"Import from File"**
   - Upload:
     - `workflows/invoice-chase-producer-v1.2.json`
     - `workflows/invoice-chase-worker-v1.2.json`
     - `workflows/invoice-chase-sendgrid-webhook-v1.2.json`
     - `workflows/invoice-chase-inbound-replies-v1.2.json`
   - Click **"Import"**

### 2.2: Verify Import

You should now see 4 workflows:
- ✅ Invoice Chase - Producer (Fetch + Enqueue)
- ✅ Invoice Chase - Worker (Process + Send)
- ✅ Invoice Chase - SendGrid Event Webhook
- ✅ Invoice Chase - Inbound Reply Handler

---

## 🔑 Step 3: Configure Credentials (15 minutes)

### 3.1: PostgreSQL

1. n8n → **Credentials** → **New Credential** → **Postgres**
2. Name: `PostgreSQL Account`
3. Configure:
   ```
   Host: your-postgres-host.com
   Database: invoice_chase_production
   User: your_user
   Password: your_password
   Port: 5432
   SSL: Enable (for cloud databases)
   ```
4. **Test connection** → Save

### 3.2: Accounting System

**For QuickBooks:**
1. **New Credential** → **QuickBooks OAuth2 API**
2. Follow OAuth flow
3. Save as `QuickBooks Account`

**For Xero:**
1. **New Credential** → **Xero OAuth2 API**
2. Follow OAuth flow
3. Save as `Xero Account`

**For Stripe:**
1. **New Credential** → **Stripe API**
2. API Key: `sk_live_...` (from Stripe dashboard)
3. Save as `Stripe Account`

### 3.3: CRM

**For HubSpot:**
1. **New Credential** → **HubSpot OAuth2 API**
2. Follow OAuth flow
3. Save as `HubSpot Account`

**For Salesforce:**
1. **New Credential** → **Salesforce OAuth2 API**
2. Follow OAuth flow
3. Save as `Salesforce Account`

### 3.4: SendGrid

1. **New Credential** → **Header Auth**
2. Name: `SendGrid Auth`
3. Header Name: `Authorization`
4. Header Value: `Bearer YOUR_SENDGRID_API_KEY`
5. Save

### 3.5: Twilio (Optional, for SMS)

1. **New Credential** → **Twilio API**
2. Account SID: `ACxxxx...`
3. Auth Token: `your_auth_token`
4. Save as `Twilio Account`

---

## ⚙️ Step 4: Configure Environment Variables (10 minutes)

### 4.1: Add to n8n Environment

**In n8n Cloud:** Settings → Variables
**In Self-Hosted:** `.env` file

```bash
# Required
TENANT_ID=your_company
CLIENT_LABEL=production
USE_SAMPLE_DATA=false
DRY_RUN_MODE=true  # Start with dry run!
DEFAULT_TIMEZONE=America/Los_Angeles

# Thresholds
AUTO_SEND_MAX_AMOUNT_CENTS=1000000  # $10,000
HUMAN_ESCALATION_DAYS=31
QUIET_HOURS_START=20:00
QUIET_HOURS_END=08:00

# Dedupe windows (hours)
STAGE1_DEDUPE_HOURS=48
STAGE2_DEDUPE_HOURS=72
STAGE3_DEDUPE_HOURS=120

# Cost tracking
EMAIL_COST_USD=0.00085
SMS_COST_USD=0.0079

# API URLs
ACCOUNTING_API_URL=https://api.quickbooks.com/v3
CRM_API_URL=https://api.hubspot.com
COMPANY_EMAIL=billing@yourcompany.com
COMPANY_PHONE=+15551234567

# Optional
ESCALATION_SLACK_WEBHOOK=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### 4.2: Verify Variables Loaded

In n8n, open any workflow → Code node → Test with:
```javascript
return { test: $env.TENANT_ID };
```

Should return your tenant ID.

---

## 🧪 Step 5: Test in Dry Run Mode (30 minutes)

### 5.1: Producer Test

1. Open **"Invoice Chase - Producer"**
2. Ensure `USE_SAMPLE_DATA=true` and `DRY_RUN_MODE=true`
3. Click **"Execute Workflow"**
4. Verify:
   - ✅ 3 sample invoices processed
   - ✅ Rows inserted into `invoice_queue`
   - ✅ Audit events logged

```sql
-- Check queue
SELECT * FROM invoice_queue ORDER BY created_at DESC LIMIT 10;

-- Check audit
SELECT * FROM audit_events WHERE event_type = 'producer_enqueued' ORDER BY ts DESC LIMIT 10;
```

### 5.2: Worker Test

1. Open **"Invoice Chase - Worker"**
2. Click **"Execute Workflow"**
3. Watch the execution:
   - ✅ Claims 1 item from queue
   - ✅ Loads invoice + customer context
   - ✅ Runs through all gates
   - ✅ Generates message
   - ✅ **DRY RUN**: Simulates send (doesn't actually send)
   - ✅ Logs cost + audit
   - ✅ Completes queue item

```sql
-- Check reminder_sends
SELECT * FROM reminder_sends ORDER BY created_at DESC LIMIT 10;

-- Check outbound_requests (idempotency ledger)
SELECT * FROM outbound_requests ORDER BY created_at DESC LIMIT 10;

-- Check cost tracking
SELECT SUM(cost_usd) as total_cost FROM cost_tracking;

-- Check audit trail
SELECT event_type, COUNT(*)
FROM audit_events
GROUP BY event_type
ORDER BY COUNT(*) DESC;
```

### 5.3: Test Race Condition Protection

1. Manually reset queue item:
```sql
UPDATE invoice_queue
SET status = 'queued', lease_expires_at = NULL
WHERE invoice_id = 'INV-TEST-001';
```

2. Run Worker twice quickly
3. **Expected:** Second run blocked by dedupe bucket constraint
4. Check logs:
```sql
SELECT * FROM reminder_sends WHERE invoice_id = 'INV-TEST-001';
-- Should see only 1 row with status='sent'
```

✅ **Race condition protection working!**

### 5.4: Test Idempotency

1. Find an outbound_request:
```sql
SELECT idempotency_key FROM outbound_requests LIMIT 1;
```

2. Try to insert duplicate:
```sql
INSERT INTO outbound_requests (tenant_id, provider, idempotency_key, status)
VALUES ('your_company', 'email', 'SAME_KEY_AS_ABOVE', 'pending');
-- Should fail with unique constraint violation
```

✅ **Internal idempotency working!**

---

## 🚀 Step 6: Production Deployment (Phased)

### Phase 0: Dry Run with Real Data (2-3 days)

```bash
# Update env
USE_SAMPLE_DATA=false  # Use real invoices
DRY_RUN_MODE=true      # Still simulate sends
```

1. Run Producer daily
2. Run Worker every 2 minutes
3. Monitor decisions in audit_events:

```sql
-- Check what WOULD be sent
SELECT
  DATE(ts) as date,
  stage,
  channel,
  COUNT(*) as would_send
FROM audit_events
WHERE event_type = 'reminder_sent'
  AND redacted_context_json->>'provider' = 'dry_run'
GROUP BY DATE(ts), stage, channel
ORDER BY date DESC;
```

4. Review human_tasks created:

```sql
SELECT task_type, COUNT(*)
FROM human_tasks
WHERE status = 'open'
GROUP BY task_type;
```

5. **Adjust thresholds** based on results

### Phase 1: Limited Production (1 week)

```bash
# Update env
DRY_RUN_MODE=false  # Actually send!
AUTO_SEND_MAX_AMOUNT_CENTS=100000  # Start with $1,000 cap
```

1. Only processes invoices under $1,000
2. Monitor deliverability:

```sql
-- Bounce rate (should be < 2%)
SELECT
  COUNT(CASE WHEN reason LIKE 'bounce%' THEN 1 END)::FLOAT / COUNT(*) * 100 as bounce_rate_pct
FROM suppression_list
WHERE updated_at >= NOW() - INTERVAL '7 days';

-- Open rate (expect 20-40%)
-- Check SendGrid analytics

-- Response rate
SELECT COUNT(*) FROM human_tasks
WHERE task_type IN ('customer_claims_paid', 'customer_inquiry')
  AND created_at >= NOW() - INTERVAL '7 days';
```

3. Check customer feedback (replies, complaints)
4. **If metrics good**, proceed to Phase 2

### Phase 2: Full Production (Ongoing)

```bash
# Update env
AUTO_SEND_MAX_AMOUNT_CENTS=1000000  # $10,000 threshold
```

1. Enable all stages
2. Scale workers (run 2-3 instances in parallel)
3. Set up monitoring dashboards
4. Configure alerting

---

## 🔔 Step 7: Configure Webhooks (15 minutes)

### 7.1: SendGrid Event Webhook

1. SendGrid → **Settings** → **Mail Settings** → **Event Webhook**
2. HTTP Post URL: `https://your-n8n.com/webhook/sendgrid-events`
3. Select Actions:
   - ☑ Bounce
   - ☑ Dropped
   - ☑ Spam Report
   - ☑ Unsubscribe
4. **Enable** → **Save**

Test:
```sql
-- Force a bounce (use invalid email in test)
-- Then check:
SELECT * FROM suppression_list WHERE reason LIKE 'bounce%';
SELECT * FROM audit_events WHERE event_type = 'deliverability_event';
```

### 7.2: SendGrid Inbound Parse (Email Replies)

1. SendGrid → **Settings** → **Inbound Parse**
2. **Add Host & URL**:
   - Domain: `inbound.yourdomain.com`
   - URL: `https://your-n8n.com/webhook/inbound-replies`
3. Configure MX records (SendGrid will show you the values)
4. **Save**

Test by sending email to: `invoice+test@inbound.yourdomain.com`

### 7.3: Twilio SMS Webhook (Optional)

1. Twilio → **Phone Numbers** → Your Number
2. Messaging → **A MESSAGE COMES IN**:
   - Webhook: `https://your-n8n.com/webhook/inbound-replies`
   - HTTP POST
3. **Save**

Test by texting "STOP" to your Twilio number.

---

## 📊 Step 8: Monitoring & Alerts (20 minutes)

### 8.1: Create Monitoring Dashboard

```sql
-- Daily metrics query
WITH daily AS (
  SELECT DATE(ts) as date,
    COUNT(*) FILTER (WHERE event_type = 'reminder_sent') as sent,
    COUNT(*) FILTER (WHERE event_type = 'producer_enqueued') as enqueued,
    COUNT(DISTINCT invoice_id) as unique_invoices
  FROM audit_events
  WHERE ts >= CURRENT_DATE - INTERVAL '30 days'
  GROUP BY DATE(ts)
),
costs AS (
  SELECT DATE(ts) as date,
    SUM(cost_usd) as daily_cost
  FROM cost_tracking
  WHERE ts >= CURRENT_DATE - INTERVAL '30 days'
  GROUP BY DATE(ts)
)
SELECT d.date, d.sent, d.enqueued, d.unique_invoices, c.daily_cost
FROM daily d
LEFT JOIN costs c ON d.date = c.date
ORDER BY d.date DESC;
```

### 8.2: Set Up Alerts

**Slack alerts for:**
- High bounce rate (> 5%)
- Many human tasks (> 50 open)
- Workflow errors
- Cost spike

Example alert workflow (add to n8n):
```javascript
// Check bounce rate
const bounceRate = await db.query(`
  SELECT COUNT(*) FILTER (WHERE reason LIKE 'bounce%')::FLOAT / COUNT(*) * 100
  FROM suppression_list
  WHERE updated_at >= NOW() - INTERVAL '24 hours'
`);

if (bounceRate > 5) {
  await slack.post({
    channel: '#alerts',
    text: `🚨 Bounce rate is ${bounceRate}% (threshold: 5%)`
  });
}
```

---

## ✅ Production Checklist

Before going live:

### Database
- [ ] All 10 tables created
- [ ] Unique constraints verified
- [ ] Indexes created
- [ ] Backups configured
- [ ] Connection pooling set up

### Workflows
- [ ] All 4 workflows imported
- [ ] All credentials configured
- [ ] Environment variables set
- [ ] Dry run testing passed
- [ ] Race condition test passed
- [ ] Idempotency test passed

### Webhooks
- [ ] SendGrid event webhook configured
- [ ] SendGrid inbound parse configured (if using email replies)
- [ ] Twilio webhook configured (if using SMS)
- [ ] Webhook URLs are HTTPS
- [ ] Webhook signature validation enabled

### Monitoring
- [ ] Dashboard queries tested
- [ ] Slack alerts configured
- [ ] On-call rotation defined
- [ ] Runbook created

### Compliance
- [ ] Unsubscribe links in all email templates
- [ ] "Reply STOP" in all SMS templates
- [ ] Suppression list processing working
- [ ] Privacy policy updated
- [ ] Terms of service updated

### Business
- [ ] Pricing page live
- [ ] Stripe subscription configured
- [ ] Support documentation created
- [ ] Demo video recorded
- [ ] Customer onboarding flow tested

---

## 🐛 Troubleshooting

### "No items in queue" (Worker exits immediately)

**Cause:** No invoices enqueued
**Fix:** Run Producer first

### "Unique constraint violation on reminder_sends"

**Cause:** Duplicate send attempt (GOOD! This is working as intended)
**Action:** Check audit_events for block_reason='dedupe_conflict'

### "CRM API error 401 Unauthorized"

**Cause:** OAuth token expired
**Fix:** Re-authenticate in n8n Credentials

### "SendGrid returns 429 Too Many Requests"

**Cause:** Rate limit hit
**Action:** Worker will retry with backoff automatically

### "High bounce rate"

**Cause:** Bad email data or spam complaints
**Fix:**
1. Check suppression_list for patterns
2. Verify email addresses in CRM
3. Improve copy (reduce spam triggers)
4. Warm up new sending domain

### "Workflow timeout"

**Cause:** Producer trying to process too many invoices
**Fix:** This shouldn't happen with producer/worker pattern, but if it does:
1. Reduce batch size
2. Add more workers
3. Optimize database queries

---

## 📈 Scaling

### Horizontal Scaling (100-10,000 invoices/day)

1. Run multiple Worker instances:
   - Each polls queue independently
   - `FOR UPDATE SKIP LOCKED` prevents conflicts
   - No coordination needed

2. Optimize database:
   ```sql
   -- Add connection pooling
   -- Increase max_connections
   -- Monitor query performance
   EXPLAIN ANALYZE SELECT ...;
   ```

### Vertical Scaling (10,000+ invoices/day)

1. Queue-based architecture (already implemented!)
2. Dedicated database server
3. Redis for distributed locking (if needed)
4. Load balancer for webhook endpoints

---

## 💰 Cost Tracking

Monitor costs:

```sql
-- Monthly cost by tenant
SELECT
  tenant_id,
  DATE_TRUNC('month', ts) as month,
  SUM(cost_usd) as total_cost,
  COUNT(*) as send_count,
  SUM(cost_usd) / COUNT(*) as avg_cost_per_send
FROM cost_tracking
GROUP BY tenant_id, DATE_TRUNC('month', ts)
ORDER BY month DESC, total_cost DESC;
```

**Expected costs** (at scale):
- SendGrid: $15-20/month (40k emails free, then $0.00085/email)
- Twilio SMS: $0.0079/SMS
- n8n: $50/month (Pro plan)
- Postgres: $25-100/month depending on provider
- **Total:** ~$100-150/month infrastructure for unlimited customers

**Revenue per customer:** $499/month

**Margin:** ~$350-400/month per customer (88%+ margin!)

---

## 🎓 Next Steps

Once production-stable:

1. **Add more agents:**
   - Review Flywheel Agent
   - Lead Qualification Agent
   - Support Triage Agent

2. **Build customer dashboard:**
   - Show recovered amount
   - DSO trend
   - ROI calculation

3. **White-label for agencies:**
   - Multi-tenant architecture (already built!)
   - Custom branding
   - Reseller margins

4. **Scale to 8 figures:**
   - 1000 customers = $499k MRR = $6M ARR
   - Raise funding or bootstrap
   - Build marketplace for custom agents

---

## 📞 Support

**Issues?**
- Check workflow_errors table first
- Review audit_events for context
- Check n8n execution logs

**Questions?**
Just ask Claude - I have the complete system loaded!

---

**🎉 You're ready to print money!**

Start with Phase 0 (dry run), validate everything, then flip to production and watch the cash flow improve.
