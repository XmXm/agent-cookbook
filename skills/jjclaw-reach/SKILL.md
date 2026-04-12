---
name: jjclaw-reach
description: |
  Use when the user pastes a URL, asks to open/read/summarize a link, wants to research a topic,
  search GitHub/X/docs, clip or save articles, extract tweets, look up library documentation,
  find code examples, grab a WeChat or Feishu article, or do any web fetching or web search.
  Also trigger on: "jjclaw-reach", "search the web for", "what does this page say", "fetch this",
  "find docs for", "look up", "clip this", "save this article".
compatibility: |
  Requires jjclaw-reach CLI installed and network access. Some search/fetch providers require
  API keys (run `jjclaw-reach doctor` to check).
---

# jjclaw-reach

## Quick Reference

```bash
jjclaw-reach fetch <url>              # fetch URL → JSON {content, title, status}
jjclaw-reach search "<query>"         # search → JSON {results: [{title, url, content}]}
jjclaw-reach run <script>             # execute Lua pipeline script
jjclaw-reach doctor                   # check provider availability
```

Short aliases: `f`=fetch, `s`=search, `r`=run.

## When to use what

| User intent | Command |
|-------------|---------|
| Gives a URL or pastes a link | `fetch` |
| Wants web research, discovery, or comparison | `search` |
| Wants a repeatable multi-step workflow (search→fetch→save) | `run` |
| Unclear what providers are available | `doctor` |

## Default operating procedure

1. **Start with auto mode** — omit `-p`. The tool picks the best provider by domain/API key availability.
2. **Parse JSON from stdout** — both `fetch` and `search` emit structured JSON. Read `.content` for page text, `.results[]` for search hits.
3. **Save files when asked** — use `-o <dir>` to write a `.md` file, or `--name <preset>` for preconfigured destinations (e.g. `--name ob` for Obsidian).
4. **Handle failures** — if auto mode fails, retry with `-p <provider>`. Run `jjclaw-reach doctor` to see what's configured.

## Fetch

Use `fetch` when the user provides a URL or asks to read/summarize a page.

```bash
jjclaw-reach fetch https://example.com                # auto-route → JSON
jjclaw-reach fetch -p jina https://example.com        # force provider
jjclaw-reach fetch -p jina,firecrawl https://x.com    # chain fallback
jjclaw-reach fetch https://example.com --name ob      # save to preset
jjclaw-reach fetch https://example.com -o ~/notes     # save as .md with images
```

**Output**: JSON to stdout — `{content, title, status}`. With `-o`/`--name`, writes a `.md` file instead.

### Auto-routing (no `-p`)

| Domain | Provider chain |
|--------|---------------|
| x.com, twitter.com | twitter → jina |
| mp.weixin.qq.com | weixin |
| feishu.cn, larksuite.com | feishu |
| everything else | jina → exa_crawl → defuddle → firecrawl |

First success wins. Override with `-p <provider>` or `-p a,b` for custom fallback chain.

## Search

Use `search` when the user wants to research a topic, find docs, or discover content.

```bash
jjclaw-reach search "python asyncio"                    # auto (best available)
jjclaw-reach search -p brave "python asyncio"           # specific provider
jjclaw-reach search -p docs "react:useEffect"           # library docs
jjclaw-reach search -p github "repo:fetch llm"          # GitHub repos
jjclaw-reach search -p github "issue:memory leak"       # GitHub issues
jjclaw-reach search -p grok "AI 中文讨论"                 # X/Twitter + web
jjclaw-reach search -p code "react hooks"               # code snippets
jjclaw-reach search -p weixin "AI 大模型"                 # WeChat articles
jjclaw-reach search -n 20 "query"                       # more results
jjclaw-reach search -p firecrawl --scrape "query"       # full page content
```

**Output**: `{results: [{title, url, content}], status}`.

**Key query syntaxes**:
- `docs` provider: `"library:query"` format (e.g. `"react:useEffect"`)
- `github` provider: prefix with `repo:` for repos, `issue:` for issues

**Auto mode** (no `-p`): picks best available by API keys, falls back to ddg → exa_free.

## Run (Lua pipelines)

Use `run` for repeatable multi-step workflows that chain search → fetch → save.

```bash
jjclaw-reach run ai-news                      # run named script
jjclaw-reach run clip https://example.com      # pass args to script
jjclaw-reach run ./my-script.lua               # run from file path
jjclaw-reach run --list                        # list available scripts
```

Scripts live in `~/.config/jjclaw-reach/scripts/*.lua`. See `references/lua-api.md` for the full Lua API reference.

## Gotchas

- **`fetch` returns JSON, not raw markdown.** Parse `.content` from the JSON output. Only `-o`/`--name` writes plain `.md` files.
- **`docs` search uses `"library:query"` format.** Write `"react:hooks"`, not just `"react hooks"`.
- **`github` search uses prefixes.** `"repo:keyword"` for repos, `"issue:keyword"` for issues.
- **`--scrape` gives full page content** with firecrawl search — without it you only get snippets.
- **Provider availability depends on env vars.** Run `jjclaw-reach doctor` to see what's configured. Free providers (jina, twitter, weixin, ddg, docs, github) always work.
- **X/WeChat/Feishu work best with domain-specific providers.** Auto-routing handles this, but explicit `-p twitter`/`-p weixin`/`-p feishu` if auto fails.

## Common workflows

### Read a tweet
```bash
jjclaw-reach fetch https://x.com/user/status/123456
```

### Research a topic then read top results
```bash
jjclaw-reach search -p brave "LLM agent architectures" -n 10
jjclaw-reach fetch <url-from-results>
```

### Look up library docs
```bash
jjclaw-reach search -p docs "tokio:spawn"
```

### Save an article to Obsidian
```bash
jjclaw-reach fetch https://some-article.com --name ob
```

## References

- `references/providers.md` — provider details, selection logic, API key setup
- `references/lua-api.md` — full Lua pipeline API (`reach.search`, `reach.fetch`, `reach.save`, etc.)
- `references/configuration.md` — config file format, environment variables, MCP server setup, presets
