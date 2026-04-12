# Provider Reference

## Fetch Providers

| Provider | Needs | Best for |
|----------|-------|----------|
| jina | free | General web pages |
| twitter | free | X/Twitter single tweets |
| defuddle | free | General web (fallback) |
| weixin | free | WeChat articles (auto captcha unwrap) |
| feishu | lark-cli | Feishu/Lark documents |
| firecrawl | FIRECRAWL_API_KEY | General web (premium) |
| tavily | TAVILY_API_KEY | LLM-optimized extraction (basic/advanced) |
| exa_crawl | free | General web crawling (Exa free MCP, rate limited) |

## Search Providers

| Provider | Needs | Best for |
|----------|-------|----------|
| brave | BRAVE_API_KEY | General web search |
| tavily | TAVILY_API_KEY | LLM-optimized search (general/news/finance) |
| exa | EXA_API_KEY | Semantic search |
| grok | XAI_API_KEY | X/Twitter + web search |
| firecrawl | FIRECRAWL_API_KEY | Web search, `--scrape` for full content |
| code | EXA_API_KEY | Code snippets (GitHub, docs, Stack Overflow) |
| code_free | free | Exa free MCP code search (rate limited) |
| docs | free (optional CONTEXT7_API_KEY) | Library documentation, format: `"lib:query"` |
| github | free (optional GITHUB_TOKEN) | Code/repo/issue (prefix: `repo:` or `issue:`) |
| weixin | free | Sogou WeChat articles (Chinese) |
| ddg | free | DuckDuckGo, zero config |
| exa_free | free | Exa hosted MCP, rate limited |
| feishu | lark-cli | Feishu/Lark document search |

## Auto-Routing Rules (Fetch)

When no `-p` provider is specified, the tool picks the best provider chain by URL domain:

| Domain | Provider chain |
|--------|---------------|
| x.com, twitter.com | twitter -> jina |
| mp.weixin.qq.com | weixin |
| feishu.cn, larksuite.com | feishu |
| everything else | jina -> exa_crawl -> defuddle -> firecrawl |

## Auto Mode (Search)

When no `-p` is specified for search, the tool picks the best available provider based on configured API keys. Falls back to `ddg -> exa_free` when no keys are set.

## Fallback Strategy

First success wins. If a provider in the chain fails, the next one is tried automatically. This applies to both fetch auto-routing and search auto mode.
