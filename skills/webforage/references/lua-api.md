# Lua Pipeline API Reference

## The `reach` Object

| Function | Returns | Description |
|----------|---------|-------------|
| `reach.search(query, {provider=, num_results=})` | array of `{title, url, content}` | Search providers |
| `reach.fetch(url, {provider=})` | `{content, title, status}` | Fetch URL |
| `reach.save(content, {dir=, title=, url=, tags={}, frontmatter=bool, images="download"\|"keep", images_dir=, dedup=bool})` | filepath or nil | Save .md file (auto dedup, image download, frontmatter) |
| `reach.log(msg)` | — | Print to stderr |
| `reach.env(name, default)` | string | Get environment variable |
| `reach.sleep(seconds)` | — | Rate limiting |
| `reach.json.encode(table)` / `.decode(str)` | string / table | JSON conversion |
| `reach.config.get(key)` | value | Read config |
| `reach.rss(urls, {days=, limit=})` | array of `{title, url, content}` | Fetch RSS/Atom feed entries |
| `reach.parallel(tasks)` | array of results | Run fetch/search tasks concurrently. Tasks: `{{fn="fetch", args={url=}}, {fn="search", args={query=}}}` |

## CLI Args and Flags

Accessible via `reach.args` inside Lua scripts:

| Access | Description |
|--------|-------------|
| `reach.args[1]`, `reach.args[2]`, … | Positional arguments passed after the script name |
| `reach.args.force` | `--force` flag — override dedup |
| `reach.args.dry_run` | `--dry-run` flag |

Usage:

```bash
webforage run clip https://example.com      # reach.args[1] = "https://example.com"
webforage run script --force                # reach.args.force = true
```

Scripts live in `~/.config/webforage/scripts/*.lua`.

## Example Script

```lua
-- ~/.config/webforage/scripts/ai-clip.lua
-- Search and save AI articles to Obsidian
local vault = reach.env("OB_VAULT")
local query = reach.args[1] or "AI 最新进展"

local results = reach.search(query, {provider = "brave", num_results = 5})

for i, r in ipairs(results) do
  local ok, err = pcall(function()
    local page = reach.fetch(r.url)
    reach.save(page.content, {
      dir = vault .. "/capture/web_clip",
      title = page.title or r.title,
      url = r.url,
      tags = {"ai"},
      frontmatter = true,
      images = "download",
      images_dir = vault .. "/_/assets",
    })
  end)
  if not ok then reach.log("FAILED: " .. tostring(err)) end
  if i < #results then reach.sleep(2) end
end
```

## RSS Example

```lua
-- Fetch latest entries from a feed
local entries = reach.rss("https://example.com/feed.xml", {days = 7, limit = 20})
for _, e in ipairs(entries) do
  reach.log(e.title .. " — " .. (e.url or ""))
end
```

## Parallel Example

```lua
-- Search multiple providers concurrently
local tasks = {
  {fn = "search", args = {query = "AI agents", provider = "brave", num_results = 5}},
  {fn = "search", args = {query = "AI agents", provider = "ddg", num_results = 5}},
}
local results = reach.parallel(tasks)
-- results[1] = brave results, results[2] = ddg results
```
