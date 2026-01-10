# N8N-MCP Integration with Universal Memory Contract

This document explains how to integrate the n8n-MCP server with the Higgs Universal Memory Contract (UMC) to create a powerful AI-driven workflow automation system with persistent memory.

## Overview

The integration combines:
- **n8n-MCP**: Model Context Protocol server providing Claude with access to 1,084+ n8n nodes and workflows
- **UMC Middleware**: Memory server for storing context, state, and interaction history
- **Claude**: AI assistant that orchestrates both systems

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Claude AI                             │
│  (Orchestrates workflow creation with memory context)        │
└────────────┬──────────────────────────────────┬─────────────┘
             │                                   │
             │                                   │
    ┌────────▼──────────┐              ┌────────▼──────────┐
    │   n8n-MCP Server  │              │  UMC Middleware   │
    │  (Workflow Tools) │              │  (Memory System)  │
    └────────┬──────────┘              └────────┬──────────┘
             │                                   │
             │                                   │
    ┌────────▼──────────┐              ┌────────▼──────────┐
    │  n8n Instance     │              │  SQLite Database  │
    │  (Workflows)      │              │  (Memory Events)  │
    └───────────────────┘              └───────────────────┘
```

## Setup Guide

### Step 1: Start UMC Memory Server

```bash
# Navigate to middleware directory
cd /home/user/higgs-universal-memory-contract/middleware

# Install dependencies (if not already done)
pip install -r requirements.txt

# Start the UMC memory server
python umc_memory_server.py
```

The server will start on `http://localhost:8000`

### Step 2: Configure n8n-MCP Server

Choose one of these deployment methods:

#### Option A: NPX (Recommended for Quick Start)

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "n8n-mcp": {
      "command": "npx",
      "args": ["n8n-mcp"],
      "env": {
        "MCP_MODE": "stdio",
        "LOG_LEVEL": "error",
        "DISABLE_CONSOLE_OUTPUT": "true"
      }
    }
  }
}
```

#### Option B: Docker

```json
{
  "mcpServers": {
    "n8n-mcp": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--init",
        "-e", "MCP_MODE=stdio",
        "-e", "LOG_LEVEL=error",
        "-e", "DISABLE_CONSOLE_OUTPUT=true",
        "ghcr.io/czlonkowski/n8n-mcp:latest"
      ]
    }
  }
}
```

#### Option C: Local Installation (For Development)

```bash
# Navigate to n8n-mcp directory
cd /home/user/higgs-universal-memory-contract/integrations/n8n-mcp

# Install dependencies
npm install

# Build the project
npm run build

# Initialize database
npm run rebuild

# Test that it works
npm start
```

Add to Claude Desktop config:

```json
{
  "mcpServers": {
    "n8n-mcp": {
      "command": "node",
      "args": ["/home/user/higgs-universal-memory-contract/integrations/n8n-mcp/dist/mcp/index.js"],
      "env": {
        "MCP_MODE": "stdio",
        "LOG_LEVEL": "error",
        "DISABLE_CONSOLE_OUTPUT": "true"
      }
    }
  }
}
```

### Step 3: Connect to n8n Instance (Optional)

If you want Claude to manage actual n8n workflows (not just get documentation), add n8n API credentials:

```json
{
  "mcpServers": {
    "n8n-mcp": {
      "command": "npx",
      "args": ["n8n-mcp"],
      "env": {
        "MCP_MODE": "stdio",
        "LOG_LEVEL": "error",
        "DISABLE_CONSOLE_OUTPUT": "true",
        "N8N_API_URL": "http://localhost:5678",
        "N8N_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

**Restart Claude Desktop** after updating the configuration.

## Usage Patterns

### Pattern 1: Context-Aware Workflow Creation

Ask Claude to retrieve context from UMC before building workflows:

```
User: "I need a workflow to process customer emails. Check my project context first."

Claude will:
1. Call UMC `/request_context` to get relevant project information
2. Use n8n-MCP `search_templates` to find email processing templates
3. Use n8n-MCP `get_template` to retrieve workflow structure
4. Create/customize the workflow based on project context
5. Save the interaction to UMC via `/save_note`
```

### Pattern 2: Iterative Workflow Development with Memory

```
Session 1:
User: "Create a Slack notification workflow"
Claude creates workflow and saves details to UMC

Session 2 (hours/days later):
User: "Update that Slack workflow to include error handling"
Claude:
1. Retrieves previous workflow details from UMC
2. Uses n8n-MCP to update the workflow
3. Saves the update to UMC
```

### Pattern 3: Project State Snapshots

```
User: "I just completed Phase 1 of automation setup"
Claude:
1. Saves state update to UMC `/state_update`
2. Includes: workflow IDs, completion status, next steps
3. Can retrieve this state in future sessions
```

## Example Workflows

### Example 1: Email to Slack with UMC Logging

This n8n workflow integrates with UMC to log all processed emails:

```json
{
  "name": "Email to Slack with UMC Logging",
  "nodes": [
    {
      "type": "n8n-nodes-base.emailReadImap",
      "name": "Read Emails"
    },
    {
      "type": "n8n-nodes-base.httpRequest",
      "name": "Log to UMC",
      "parameters": {
        "url": "http://localhost:8000/save_note",
        "method": "POST",
        "bodyParameters": {
          "session_id": "email-processor",
          "event_type": "email_received",
          "content": "={{ $json.subject }}",
          "metadata": {
            "from": "={{ $json.from }}",
            "timestamp": "={{ $json.date }}"
          }
        }
      }
    },
    {
      "type": "n8n-nodes-base.slack",
      "name": "Send to Slack"
    }
  ]
}
```

### Example 2: Daily Standup Automation

```json
{
  "name": "Daily Standup with UMC Context",
  "nodes": [
    {
      "type": "n8n-nodes-base.scheduleTrigger",
      "name": "Daily at 9 AM"
    },
    {
      "type": "n8n-nodes-base.httpRequest",
      "name": "Get Yesterday's Context",
      "parameters": {
        "url": "http://localhost:8000/request_context",
        "method": "POST",
        "bodyParameters": {
          "session_id": "project-x",
          "semantic_query": "What did we accomplish yesterday?"
        }
      }
    },
    {
      "type": "n8n-nodes-base.slack",
      "name": "Post Standup Summary"
    }
  ]
}
```

## UMC Event Types for n8n Integration

When integrating n8n workflows with UMC, use these standardized event types:

```python
# Workflow lifecycle events
"workflow_created"      # New workflow created
"workflow_updated"      # Workflow modified
"workflow_executed"     # Workflow ran successfully
"workflow_failed"       # Workflow execution failed

# Node-specific events
"node_added"           # Node added to workflow
"node_configured"      # Node configuration changed
"node_validated"       # Node validation completed

# Integration events
"template_used"        # n8n template used as base
"api_call_made"        # External API called from workflow
"data_processed"       # Data transformation completed
```

Example save_note call from n8n:

```bash
curl -X POST http://localhost:8000/save_note \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "automation-project",
    "event_type": "workflow_created",
    "content": "Created customer email processing workflow",
    "metadata": {
      "workflow_id": "wf-123",
      "node_count": 5,
      "template_source": "n8n.io/workflows/2414",
      "author": "Claude AI"
    }
  }'
```

## Best Practices

### 1. Session Management

Use consistent session IDs across UMC and n8n workflows:

```
- Project-based: "project-customer-portal"
- Feature-based: "feature-email-automation"
- Environment-based: "prod-slack-notifications"
```

### 2. Memory Structure

Organize UMC notes hierarchically:

```
automation-project/
├─ workflows/
│  ├─ email-processor (workflow_id: wf-123)
│  └─ slack-notifier (workflow_id: wf-456)
├─ templates/
│  └─ used templates and customizations
└─ learnings/
   └─ what worked, what didn't
```

### 3. Error Handling

Always log failures to UMC for debugging:

```javascript
// In n8n Code node
try {
  // Your logic
} catch (error) {
  await fetch('http://localhost:8000/save_note', {
    method: 'POST',
    body: JSON.stringify({
      session_id: 'automation-project',
      event_type: 'workflow_failed',
      content: error.message,
      metadata: { stack: error.stack }
    })
  });
  throw error;
}
```

### 4. Context Retrieval

Before creating complex workflows, always check UMC for relevant context:

```python
# Ask Claude to retrieve context
"Before building this workflow, check if we have any existing
 patterns or decisions about email processing in our UMC memory."
```

## Advanced Integration: n8n Workflow as UMC Client

You can create an n8n workflow that acts as a UMC client for other systems:

```json
{
  "name": "UMC Context API",
  "nodes": [
    {
      "type": "n8n-nodes-base.webhook",
      "name": "Webhook Trigger",
      "parameters": {
        "path": "get-context"
      }
    },
    {
      "type": "n8n-nodes-base.httpRequest",
      "name": "Request UMC Context",
      "parameters": {
        "url": "http://localhost:8000/request_context",
        "method": "POST",
        "body": "={{ $json }}"
      }
    },
    {
      "type": "n8n-nodes-base.respondToWebhook",
      "name": "Return Context"
    }
  ]
}
```

This creates a RESTful API endpoint that other applications can use to query UMC memory.

## Troubleshooting

### n8n-MCP not appearing in Claude

1. Check configuration file location:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. Verify JSON syntax is valid
3. Restart Claude Desktop completely
4. Check Claude Desktop logs for errors

### UMC connection issues from n8n

1. Verify UMC server is running: `curl http://localhost:8000/session/test/memory`
2. Check firewall settings
3. For Docker n8n, use `http://host.docker.internal:8000`

### Memory not persisting

1. Check SQLite database exists: `middleware/memory.db`
2. Verify file permissions
3. Check UMC server logs for errors

## Performance Considerations

- **UMC Database**: SQLite handles ~100k notes efficiently
- **n8n-MCP**: Average query time ~12ms for node searches
- **Network**: Keep UMC and n8n on same network/localhost for best performance

## Security Notes

- **API Keys**: Never commit n8n API keys to version control
- **UMC Access**: Consider adding authentication to UMC middleware for production
- **Network**: Run UMC and n8n on private network, expose only necessary endpoints

## Next Steps

1. Review [n8n-MCP Documentation](../integrations/n8n-mcp/README.md)
2. Review [UMC Specification](../spec/higgs-memory-contract_v0.9-core.json)
3. Check [Example Workflows](./example-workflows/)
4. Join community discussions on GitHub

## Resources

- n8n-MCP GitHub: https://github.com/czlonkowski/n8n-mcp
- n8n Documentation: https://docs.n8n.io
- UMC Quickstart: [../QUICKSTART.md](../QUICKSTART.md)
- Example Usage: [../examples/usage.md](../examples/usage.md)

---

**Built with ❤️ for the n8n and AI automation community**
