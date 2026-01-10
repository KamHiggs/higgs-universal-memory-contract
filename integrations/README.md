# UMC Integrations

This directory contains integrations with external tools and services.

## n8n-MCP Integration

The n8n-MCP server enables Claude to build and manage n8n workflows while leveraging UMC memory for context-aware automation.

### Setup

To use the n8n-MCP integration, clone the repository:

```bash
cd integrations
git clone --depth 1 https://github.com/czlonkowski/n8n-mcp.git
cd n8n-mcp
npm install
npm run build
npm run rebuild
```

### Quick Start

```bash
# Option 1: Use npx (no local installation needed)
npx n8n-mcp

# Option 2: Use Docker
docker pull ghcr.io/czlonkowski/n8n-mcp:latest

# Option 3: Use local installation
cd integrations/n8n-mcp
npm start
```

### Documentation

- [n8n-MCP Integration Guide](../docs/n8n-mcp-integration.md) - Complete setup and usage guide
- [Example Workflows](../examples/n8n-workflows/) - Sample n8n workflows with UMC integration
- [n8n-MCP GitHub](https://github.com/czlonkowski/n8n-mcp) - Official repository

### Why It's Not Committed

The n8n-mcp repository is:
- 280MB+ with all dependencies
- Actively developed with frequent updates
- Better maintained as a separate installation

By cloning it separately, you can:
- Pull the latest updates easily
- Choose your deployment method (npm, Docker, local)
- Keep your UMC repository lightweight

## Other Integrations

Future integrations may include:
- LangChain memory adapters
- Zapier webhook handlers
- Custom MCP servers
- And more!

---

**Contributions welcome!** Have an integration idea? Open an issue or PR.
