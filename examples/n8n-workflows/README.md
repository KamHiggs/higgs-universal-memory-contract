# n8n Workflow Examples for UMC Integration

This directory contains example n8n workflows that demonstrate integration with the Universal Memory Contract (UMC) middleware.

## Prerequisites

1. **UMC Middleware running**: `python middleware/umc_memory_server.py`
2. **n8n instance**: Local or cloud n8n instance running
3. **Network access**: n8n can reach `http://localhost:8000` (or your UMC server URL)

## Workflows

### 01-basic-umc-logging.json

**Purpose**: Demonstrates basic logging to UMC from an n8n workflow

**Features**:
- Manual trigger for testing
- Saves execution events to UMC
- Includes execution metadata (ID, mode, timestamp)

**Setup**:
1. Import into n8n
2. Ensure UMC middleware is running
3. Execute manually to test

**Test**:
```bash
# Start UMC server
cd middleware && python umc_memory_server.py

# In n8n, execute the workflow
# Check UMC memory:
curl http://localhost:8000/session/demo-workflow/memory
```

### 02-context-aware-processing.json

**Purpose**: Advanced workflow that retrieves context from UMC before processing data

**Features**:
- Webhook trigger for external data input
- Retrieves processing rules from UMC memory
- Applies context-aware transformations
- Logs processing results back to UMC
- Returns processed data via webhook response

**Setup**:
1. Import into n8n
2. Add processing rules to UMC:
   ```bash
   curl -X POST http://localhost:8000/save_note \
     -H "Content-Type: application/json" \
     -d '{
       "session_id": "default",
       "event_type": "processing_rule",
       "content": "Transform all email addresses to lowercase"
     }'
   ```
3. Activate the workflow
4. Get the webhook URL from n8n

**Test**:
```bash
curl -X POST http://localhost:5678/webhook/process-data \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "default",
    "data": {
      "email": "User@Example.COM",
      "name": "Test User"
    }
  }'
```

## Common Patterns

### Pattern 1: Event Logging

Save workflow events to UMC for tracking:

```javascript
// HTTP Request node to UMC
{
  "url": "http://localhost:8000/save_note",
  "method": "POST",
  "body": {
    "session_id": "{{ $workflow.name }}",
    "event_type": "workflow_executed",
    "content": "Description of what happened",
    "metadata": {
      "execution_id": "{{ $execution.id }}"
    }
  }
}
```

### Pattern 2: Context Retrieval

Get relevant context before processing:

```javascript
// HTTP Request node to UMC
{
  "url": "http://localhost:8000/request_context",
  "method": "POST",
  "body": {
    "session_id": "{{ $json.project_id }}",
    "semantic_query": "What are the rules for this type of data?"
  }
}
```

### Pattern 3: State Updates

Update project state in UMC:

```javascript
// HTTP Request node to UMC
{
  "url": "http://localhost:8000/state_update",
  "method": "POST",
  "body": {
    "session_id": "{{ $workflow.name }}",
    "state": {
      "last_run": "{{ $now.toISO() }}",
      "items_processed": "{{ $items().length }}",
      "status": "success"
    }
  }
}
```

## Docker n8n Configuration

If running n8n in Docker, use `host.docker.internal` to access UMC:

```bash
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -e N8N_HOST=localhost \
  -e WEBHOOK_URL=http://localhost:5678/ \
  n8nio/n8n
```

In workflows, use: `http://host.docker.internal:8000` for UMC URL

## Customization Tips

### Custom Event Types

Define your own event types for better organization:

```javascript
const EVENT_TYPES = {
  DATA_RECEIVED: 'data_received',
  VALIDATION_PASSED: 'validation_passed',
  TRANSFORMATION_APPLIED: 'transformation_applied',
  NOTIFICATION_SENT: 'notification_sent',
  ERROR_OCCURRED: 'error_occurred'
};
```

### Error Handling

Always log errors to UMC for debugging:

```javascript
// In Code node
try {
  // Your processing logic
} catch (error) {
  await $http.request({
    method: 'POST',
    url: 'http://localhost:8000/save_note',
    body: {
      session_id: $workflow.name,
      event_type: 'error_occurred',
      content: error.message,
      metadata: {
        stack: error.stack,
        node: $node.name
      }
    }
  });
  throw error;
}
```

### Semantic Search

Use semantic queries to find relevant context:

```javascript
// Get previous similar executions
const context = await $http.request({
  method: 'POST',
  url: 'http://localhost:8000/request_context',
  body: {
    session_id: 'my-workflow',
    semantic_query: 'Show me similar data processing tasks from the last week'
  }
});
```

## Troubleshooting

### Connection Refused

```
Error: connect ECONNREFUSED 127.0.0.1:8000
```

**Solution**: Ensure UMC middleware is running:
```bash
cd middleware && python umc_memory_server.py
```

### Docker Network Issues

**Problem**: n8n in Docker can't reach localhost:8000

**Solution**: Use `host.docker.internal:8000` instead of `localhost:8000`

### Invalid JSON Response

**Problem**: UMC returns unexpected response

**Solution**: Check UMC logs and verify request format matches API spec

## Next Steps

1. Read [n8n-MCP Integration Guide](../../docs/n8n-mcp-integration.md)
2. Review [UMC Specification](../../spec/higgs-memory-contract_v0.9-core.json)
3. Explore [UMC Middleware Examples](../../middleware/examples/)
4. Build your own workflows!

## Resources

- n8n Documentation: https://docs.n8n.io
- UMC Quickstart: [../../QUICKSTART.md](../../QUICKSTART.md)
- n8n-MCP Server: [../../integrations/n8n-mcp/](../../integrations/n8n-mcp/)

---

**Happy Automating!** 🚀
