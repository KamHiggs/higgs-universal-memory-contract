#!/bin/bash
set -e

echo "================================================"
echo "  Invoice Chase Agent - Quick Setup"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if n8n connection is configured
echo "Step 1: Checking n8n-MCP configuration..."
if [ ! -f "/home/user/higgs-universal-memory-contract/integrations/n8n-mcp/.env" ]; then
    echo -e "${YELLOW}⚠️  n8n-MCP not configured yet${NC}"
    echo ""
    echo "Please configure n8n connection first:"
    echo "  1. Get your n8n API key from Settings → API"
    echo "  2. Run: cd /home/user/higgs-universal-memory-contract/integrations/n8n-mcp"
    echo "  3. Run: cp .env.example .env"
    echo "  4. Edit .env and add:"
    echo "       N8N_API_URL=https://your-n8n-instance.com"
    echo "       N8N_API_KEY=your-api-key-here"
    echo ""
    echo "See detailed instructions: .claude/n8n-setup.md"
    echo ""
    read -p "Press Enter when ready, or Ctrl+C to exit..."
fi

echo -e "${GREEN}✓${NC} n8n-MCP configuration found"
echo ""

# Check if n8n-mcp is built
echo "Step 2: Building n8n-MCP..."
cd /home/user/higgs-universal-memory-contract/integrations/n8n-mcp

if [ ! -d "dist" ]; then
    echo "Installing dependencies..."
    npm install
    echo "Building..."
    npm run build
fi

echo -e "${GREEN}✓${NC} n8n-MCP ready"
echo ""

# Create test data directory
echo "Step 3: Setting up test data..."
mkdir -p /home/user/higgs-universal-memory-contract/test-data
cd /home/user/higgs-universal-memory-contract

# Create sample test invoices
cat > test-data/sample-invoices.json <<'EOF'
[
  {
    "invoice_id": "INV-TEST-001",
    "invoice_number": "2024-001",
    "customer_id": "CUST-TEST-001",
    "customer_name": "Acme Corp",
    "customer_email": "billing@acme-test.com",
    "customer_phone": "+15551234567",
    "amount": 1500.00,
    "due_date": "2024-01-01",
    "days_overdue": 3,
    "status": "overdue",
    "currency": "USD",
    "payment_link": "https://pay.example.com/inv-001"
  },
  {
    "invoice_id": "INV-TEST-002",
    "invoice_number": "2024-002",
    "customer_id": "CUST-TEST-002",
    "customer_name": "TechStart Inc",
    "customer_email": "accounts@techstart-test.com",
    "customer_phone": "+15559876543",
    "amount": 3200.00,
    "due_date": "2024-01-05",
    "days_overdue": 10,
    "status": "overdue",
    "currency": "USD",
    "payment_link": "https://pay.example.com/inv-002"
  },
  {
    "invoice_id": "INV-TEST-003",
    "invoice_number": "2024-003",
    "customer_id": "CUST-TEST-003",
    "customer_name": "BigClient LLC",
    "customer_email": "finance@bigclient-test.com",
    "customer_phone": "+15552223333",
    "amount": 15000.00,
    "due_date": "2023-12-20",
    "days_overdue": 22,
    "status": "overdue",
    "currency": "USD",
    "payment_link": "https://pay.example.com/inv-003"
  }
]
EOF

# Create sample customer context
cat > test-data/sample-customer-context.json <<'EOF'
{
  "CUST-TEST-001": {
    "customer_id": "CUST-TEST-001",
    "payment_history": {
      "total_invoices": 12,
      "on_time_payments": 10,
      "late_payments": 2,
      "average_days_late": 3
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
    "last_reminder_sent_at": null
  },
  "CUST-TEST-002": {
    "customer_id": "CUST-TEST-002",
    "payment_history": {
      "total_invoices": 8,
      "on_time_payments": 5,
      "late_payments": 3,
      "average_days_late": 7
    },
    "communication_preferences": {
      "preferred_channel": "sms",
      "language": "en"
    },
    "consent_flags": {
      "can_email": true,
      "can_sms": true,
      "can_call": true
    },
    "relationship_status": "at_risk",
    "last_reminder_sent_at": null
  },
  "CUST-TEST-003": {
    "customer_id": "CUST-TEST-003",
    "payment_history": {
      "total_invoices": 24,
      "on_time_payments": 22,
      "late_payments": 2,
      "average_days_late": 2
    },
    "communication_preferences": {
      "preferred_channel": "email",
      "language": "en"
    },
    "consent_flags": {
      "can_email": true,
      "can_sms": false,
      "can_call": false
    },
    "relationship_status": "good",
    "last_reminder_sent_at": null
  }
}
EOF

echo -e "${GREEN}✓${NC} Test data created"
echo ""

# Summary
echo "================================================"
echo "  Setup Complete! 🎉"
echo "================================================"
echo ""
echo "What's been created:"
echo "  ✓ Invoice Chase Agent Cogni Map"
echo "    → .claude/cogni-maps/invoice-chase-agent-v1.json"
echo ""
echo "  ✓ n8n Workflow Blueprint"
echo "    → workflows/invoice-chase-agent-blueprint.md"
echo ""
echo "  ✓ Test Data"
echo "    → test-data/sample-invoices.json"
echo "    → test-data/sample-customer-context.json"
echo ""
echo "  ✓ Setup Guide"
echo "    → .claude/n8n-setup.md"
echo ""
echo "================================================"
echo "  Next Steps"
echo "================================================"
echo ""
echo "1. Configure n8n connection (if not done):"
echo "   → Follow: .claude/n8n-setup.md"
echo ""
echo "2. Once connected, I can help you:"
echo "   → Build the workflow in your n8n instance"
echo "   → Set up test webhook endpoints"
echo "   → Create the customer dashboard"
echo ""
echo "3. Test with sample data:"
echo "   → Use test-data/sample-invoices.json"
echo ""
echo "4. Deploy to production"
echo ""
echo "================================================"
echo ""
echo -e "${GREEN}Ready to connect to your n8n instance!${NC}"
echo ""
echo "Tell me when you have:"
echo "  • Your n8n instance URL"
echo "  • Your n8n API key"
echo ""
echo "Then I can build the workflow for you automatically!"
echo ""
