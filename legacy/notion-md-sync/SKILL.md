---
name: notion-md-sync
description: Push a local markdown file to Notion as a page — create new or update existing. Use when the user says "sync to notion", "push to notion", "upload md to notion", "update notion page from file", "notion-md-sync", "推送到Notion", "同步到Notion", "更新Notion页面", or wants to turn a local .md file into a Notion page. Also trigger when the user has just finished writing/editing a markdown document and mentions putting it on Notion.
---

# Notion Markdown Sync

Sync a local `.md` file to Notion as a page. Two modes: **create** (new page) and **update** (overwrite existing page content).

## Prerequisites

- The Notion MCP server must be connected (`plugin:Notion:notion` or similar).
- The target markdown file must exist locally.

## Workflow

### Step 1: Determine mode

Ask the user if not obvious from context:
- **Create** — make a new Notion page from the file
- **Update** — overwrite an existing Notion page with the file's content

### Step 2: Read the markdown file

Use the Read tool to get the full file content. Extract the H1 title (first `# ...` line) — this becomes the page title in Notion. The page body is everything after the H1 line.

If the file has no H1, use the filename (without extension) as the title, and the entire content as the body.

### Step 3A: Create mode

Gather from the user (or infer from context):

| Parameter | Required | Description |
|-----------|----------|-------------|
| `parent` | Yes | A `page_id` or `data_source_id` to create the page under. Can be a Notion URL — extract the ID from it. |
| `icon` | No | Emoji icon for the page |
| `类型` | No | Capture type: `"Note"` / `"File"` / `"Web Clip"` |
| `Project` | No | Relation URL(s) as JSON array string, e.g. `'["https://www.notion.so/..."]'` |
| `Area` | No | Relation URL(s) as JSON array string |
| `标签` | No | Multi-select tags as JSON array string, e.g. `'["Work", "AI"]'` |

Then execute:

1. Call `notion-create-pages` with:
   - `parent`: `{"type": "data_source_id", "data_source_id": "<id>"}` or `{"type": "page_id", "page_id": "<id>"}`
   - `pages`: array with one page object containing `properties.Name` (the H1 title) and any other properties the user specified
   - No `content` field in the create call (Notion has content size limits on create)

2. Call `notion-update-page` with `replace_content` to push the full body:
   - `page_id`: the ID returned from step 1
   - `command`: `"replace_content"`
   - `new_str`: the markdown body (everything after H1)
   - `properties`: `{}`
   - `content_updates`: `[]`

3. Return the page URL to the user.

### Step 3B: Update mode

Gather from the user:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `page_id` | Yes | The Notion page ID or URL to update |
| Update title? | No | Whether to also update the page title from the file's H1 (default: yes) |

Then execute:

1. If updating the title, call `notion-update-page` with `update_properties`:
   - `command`: `"update_properties"`
   - `properties`: `{"Name": "<H1 title>"}`  (use `"title"` instead of `"Name"` if the page is not in a database)
   - `content_updates`: `[]`

2. Call `notion-update-page` with `replace_content` to overwrite the body:
   - `page_id`: extracted from the URL or provided directly
   - `command`: `"replace_content"`
   - `new_str`: the markdown body (everything after H1)
   - `properties`: `{}`
   - `content_updates`: `[]`

3. Return the page URL to the user.

## Key points

- **Markdown is passed as-is.** Standard markdown (tables, code blocks, mermaid, checkboxes, blockquotes) renders correctly in Notion. No conversion needed.
- **Split H1 from body.** The first `# Title` line becomes the page's `Name` property. Don't include it in the body content — Notion auto-displays the title at the top.
- **Create is two-step.** Create the page first (with properties only), then `replace_content` to push the body. This avoids content size limits on the create call.
- **Page ID extraction.** Notion URLs like `https://www.notion.so/xxxxx` — the last path segment (strip dashes) is the page ID. Also handle `?v=` view parameters by ignoring them.

## Examples

**Create:**
```
User: "把 docs/AI_DEBUG_PROJECT.md 推到 Notion，放在 AI Debug 项目下"
→ Read file → extract H1 → create page in AI Debug's Capture data source → replace_content with body
```

**Update:**
```
User: "用最新的 AI_DEBUG_PROJECT.md 更新这个 Notion 页面 https://www.notion.so/34b18398c62a81c790f1cbd8e511ac84"
→ Read file → extract H1 → update title → replace_content with body
```
