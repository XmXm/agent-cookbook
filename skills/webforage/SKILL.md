---
name: webforage
description: |
  Use when the user pastes a URL, asks to open/read/summarize a link, wants to research a topic,
  search GitHub/X/docs, clip or save articles, extract tweets, look up library documentation,
  find code examples, grab a WeChat or Feishu article, or do any web fetching or web search.
  Also trigger on: "webforage", "search the web for", "what does this page say", "fetch this",
  "find docs for", "look up", "clip this", "save this article".
compatibility: |
  Requires webforage CLI installed and network access. Some search/fetch providers require
  API keys (run `webforage doctor` to check).
---

# webforage

## Quick Reference

```bash
webforage fetch <url>              # fetch URL → JSON {content, title, status}
webforage search "<query>"         # search → JSON {results: [{title, url, content}]}
webforage run <script>             # execute Lua pipeline script
webforage doctor                   # check provider availability
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
4. **Handle failures** — if auto mode fails, retry with `-p <provider>`. Run `webforage doctor` to see what's configured.

## Fetch

Use `fetch` when the user provides a URL or asks to read/summarize a page.

```bash
webforage fetch https://example.com                # auto-route → JSON
webforage fetch -p jina https://example.com        # force provider
webforage fetch -p jina,firecrawl https://x.com    # chain fallback
webforage fetch https://example.com --name ob      # save to preset
webforage fetch https://example.com -o ~/notes     # save as .md with images
```

**Output**: JSON to stdout — `{content, title, status}`. With `-o`/`--name`, writes a `.md` file instead.

### Auto-routing (no `-p`)

| Domain | Provider chain |
|--------|---------------|
| x.com, twitter.com | twitter → jina |
| youtube.com, youtu.be | defuddle → jina |
| zhihu.com | jina → readability |
| mp.weixin.qq.com | weixin |
| feishu.cn, larksuite.com | feishu |
| everything else | jina → exa_crawl → readability → defuddle → firecrawl |

First success wins. Override with `-p <provider>` or `-p a,b` for custom fallback chain.

## Search

Use `search` when the user wants to research a topic, find docs, or discover content.

```bash
webforage search "python asyncio"                    # auto (best available)
webforage search -p brave "python asyncio"           # specific provider
webforage search -p docs "react:useEffect"           # library docs
webforage search -p github "repo:fetch llm"          # GitHub repos
webforage search -p github "issue:memory leak"       # GitHub issues
webforage search -p grok "AI 中文讨论"                 # X/Twitter + web
webforage search -p code "react hooks"               # code snippets
webforage search -p weixin "AI 大模型"                 # WeChat articles
webforage search -n 20 "query"                       # more results
webforage search -p firecrawl --scrape "query"       # full page content
webforage search -p rss "https://example.com/feed.xml days:7"  # RSS feed
```

**Output**: `{results: [{title, url, content}], status}`.

**Key query syntaxes**:
- `docs` provider: `"library:query"` format (e.g. `"react:useEffect"`)
- `github` provider: prefix with `repo:` for repos, `issue:` for issues

**Auto mode** (no `-p`): picks best available by API keys, falls back to ddg → exa_free.

## Run (Lua pipelines)

Use `run` for repeatable multi-step workflows that chain search → fetch → save.

```bash
webforage run ai-news                      # run named script
webforage run clip https://example.com      # pass args to script
webforage run ./my-script.lua               # run from file path
webforage run --list                        # list available scripts
```

Scripts live in `~/.config/webforage/scripts/*.lua`. Bundled scripts (available out of the box): `ai-news`, `rss-digest`, `clip`. See `references/lua-api.md` for the full Lua API reference.

## Gotchas

- **`fetch` returns JSON, not raw markdown.** Parse `.content` from the JSON output. Only `-o`/`--name` writes plain `.md` files.
- **`docs` search uses `"library:query"` format.** Write `"react:hooks"`, not just `"react hooks"`.
- **`github` search uses prefixes.** `"repo:keyword"` for repos, `"issue:keyword"` for issues.
- **`--scrape` gives full page content** with firecrawl search — without it you only get snippets.
- **Provider availability depends on env vars.** Run `webforage doctor` to see what's configured. Free providers (jina, twitter, weixin, ddg, docs, github) always work.
- **X/WeChat/Feishu work best with domain-specific providers.** Auto-routing handles this, but explicit `-p twitter`/`-p weixin`/`-p feishu` if auto fails.

## Common workflows

### Read a tweet
```bash
webforage fetch https://x.com/user/status/123456
```

### Research a topic then read top results
```bash
webforage search -p brave "LLM agent architectures" -n 10
webforage fetch <url-from-results>
```

### Look up library docs
```bash
webforage search -p docs "tokio:spawn"
```

### Aggregate RSS feeds
```bash
webforage run rss-digest https://example.com/feed.xml 7
```

### Save an article to Obsidian
```bash
webforage fetch https://some-article.com --name ob
```

## References

- `references/providers.md` — provider details, selection logic, API key setup
- `references/lua-api.md` — full Lua pipeline API (`reach.search`, `reach.fetch`, `reach.save`, etc.)
- `references/configuration.md` — config file format, environment variables, MCP server setup, presets
