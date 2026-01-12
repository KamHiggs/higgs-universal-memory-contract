# Connect Claude Code to Your n8n Instance

## Quick Setup (5 minutes)

### Step 1: Get Your n8n API Credentials

1. Open your n8n instance in browser
2. Go to **Settings → API** (in the left sidebar)
3. Click **Create API Key**
4. Copy the API key (you'll only see it once!)
5. Note your n8n instance URL (e.g., `https://your-n8n.app` or `http://localhost:5678`)

### Step 2: Configure n8n-MCP

Run this command to create your config:

```bash
cd /home/user/higgs-universal-memory-contract/integrations/n8n-mcp
cp .env.example .env
```

Then edit the `.env` file and add:

```bash
# Your n8n instance URL (without /api/v1 suffix)
N8N_API_URL=https://your-n8n-instance.com  # ← CHANGE THIS

# Your n8n API key from Settings → API
N8N_API_KEY=your-api-key-here  # ← CHANGE THIS

# For local n8n instance (development)
# N8N_API_URL=http://localhost:5678
# WEBHOOK_SECURITY_MODE=moderate
```

### Step 3: Test the Connection

```bash
cd /home/user/higgs-universal-memory-contract/integrations/n8n-mcp
npm install
npm run build
npm test
```

If successful, you'll see: ✅ All tests passed!

### Step 4: Add to Claude Code Settings

Add n8n-MCP server to your Claude Code MCP configuration:

**File:** `~/.config/claude-code/settings.json`

```json
{
  "mcpServers": {
    "n8n-mcp": {
      "command": "node",
      "args": ["/home/user/higgs-universal-memory-contract/integrations/n8n-mcp/dist/index.js"],
      "env": {
        "MCP_MODE": "stdio",
        "LOG_LEVEL": "error",
        "NODE_DB_PATH": "/home/user/higgs-universal-memory-contract/integrations/n8n-mcp/data/nodes.db"
      }
    }
  }
}
```

### Step 5: Restart Claude Code

```bash
# Restart your Claude Code session
# The n8n-mcp tools should now be available
```

## Quick Test

Once configured, you can test by asking me:

> "List my n8n workflows"

I should be able to see your workflows and help you build new ones!

---

## Troubleshooting

**Error: "Cannot connect to n8n API"**
- Check N8N_API_URL is correct (no trailing slash)
- Verify API key is valid in n8n Settings
- Ensure n8n instance is accessible

**Error: "n8n-mcp tools not available"**
- Restart Claude Code after adding MCP config
- Check settings.json syntax is valid JSON
- Run `npm run build` in n8n-mcp directory

**Local n8n on Docker?**
```bash
# Use Docker host networking
N8N_API_URL=http://host.docker.internal:5678
WEBHOOK_SECURITY_MODE=moderate
```
