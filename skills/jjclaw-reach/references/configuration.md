# Configuration Reference

## Config File

**Path**: `~/.config/jjclaw-reach/config.yaml`

**Overrides**:
- CLI flag: `--config <path>`
- Environment variable: `JJCLAW_REACH_CONFIG`

Supports `${VAR}` / `${VAR:-default}` environment variable expansion in config values.

## Environment Variables

| Variable | Purpose |
|----------|---------|
| FIRECRAWL_API_KEY | Enable firecrawl fetch & search |
| TAVILY_API_KEY | Enable tavily search & extract |
| EXA_API_KEY | Enable exa, code search |
| BRAVE_API_KEY | Enable brave search |
| XAI_API_KEY | Enable grok (X/Twitter + web) search |
| XAI_BASE_URL | Override xAI API base URL |
| XAI_MODEL | Override xAI model (default: grok-4-1-fast-non-reasoning) |
| _(feishu uses lark-cli, auth via `lark-cli auth login`)_ | |
| CONTEXT7_API_KEY | Optional, for docs search |
| GITHUB_TOKEN | Optional, raises GitHub API rate limit |

## Presets

Save fetch output to preconfigured directories. Configured in `config.yaml`.

```bash
jjclaw-reach fetch <url> --name ob    # save to Obsidian vault
```

## MCP Server Setup

Start as MCP server for AI agent integration:

```bash
jjclaw-reach mcp
```

Exposes 4 tools: `fetch`, `search`, `run`, `doctor`.

### claude_desktop_config.json

```json
{
  "mcpServers": {
    "jjclaw-reach": {
      "command": "jjclaw-reach",
      "args": ["mcp"],
      "env": { "BRAVE_API_KEY": "...", "TAVILY_API_KEY": "...", "XAI_API_KEY": "..." }
    }
  }
}
```
