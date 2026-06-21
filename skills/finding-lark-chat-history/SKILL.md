---
name: finding-lark-chat-history
description: "Finds Lark/Feishu P2P chat history with a person from a Chinese name, email prefix/account ID like v_ywcai, open_id, or chat_id. Use when asked to look up conversations, recent messages, or chat records with a specific person."
---

# Finding Lark Chat History

Find recent Lark/Feishu direct-message history with a person from a human input such as a Chinese name, an enterprise email prefix/account ID like `v_ywcai`, an `ou_...` open_id, or an `oc_...` chat_id.

## Required related skills

Load these first when available:

- `lark-shared` — authentication, scope handling, update notices, and safety rules.
- `lark-contact` — resolving names/account IDs to `open_id` and `p2p_chat_id`.
- `lark-im` — listing P2P/chat messages.

## Terminology

- `ou_...` is a Lark/Feishu `open_id`; it is the best stable user identifier for follow-up CLI commands.
- `oc_...` is an open chat ID / `chat_id`; for P2P conversations, use it directly to list messages.
- Inputs like `v_ywcai` are usually an enterprise email prefix, employee account, LDAP/login name, or local part of an enterprise email such as `v_ywcai@company.com`. Do not call it `open_id`.
- In some tenants this value may also correspond to Feishu's `user_id` / employee ID, but do not assume that. Prefer calling it an “enterprise email prefix/account ID” unless the API response proves it is `user_id`.

## Default behavior

When the user asks for chat history with a person and does not specify count or time range:

- Fetch the latest 5 messages.
- Sort descending (`--sort desc`).
- Use user identity (`--as user`).
- Return a concise human-readable summary: person resolved, identifiers, and recent messages with timestamp, sender, and content.
- If the command returns `_notice.update`, mention it briefly at the end after satisfying the request.

## Resolution workflow

### 1. Classify the input

Let the user's input be `<person>`.

- If it starts with `oc_`, treat it as `chat_id` and skip to message listing.
- If it starts with `ou_`, treat it as `open_id`; list messages with `--user-id` or resolve P2P if needed.
- Otherwise, treat it as a name, email, email prefix, or enterprise account ID and use contact search.

### 2. Resolve names/account IDs with contact search

Use `contact +search-user` first for Chinese names, email prefixes like `v_ywcai`, or full email addresses:

```bash
lark-cli contact +search-user --as user --query "<person>" --has-chatted --format json
```

If this returns no users, retry without `--has-chatted`:

```bash
lark-cli contact +search-user --as user --query "<person>" --format json
```

Use the result fields:

- `localized_name`
- `open_id`
- `email` / `enterprise_email`
- `department`
- `p2p_chat_id`
- `has_chatted`

Prefer `p2p_chat_id` when present; it avoids another P2P resolution step.

### 3. Handle multiple matches

If search returns multiple plausible people, do not guess. Present a compact numbered list and ask the user to choose:

```text
搜到多个候选：
1. 张三 / zhangsan@example.com / 部门 A / open_id=ou_...
2. 张三 / zhangsan2@example.com / 部门 B / open_id=ou_...
你要查哪一个？
```

If exactly one match is returned, proceed without asking.

### 4. List messages

If you have `p2p_chat_id` or the user supplied `oc_...`, use `--chat-id`:

```bash
lark-cli im +chat-messages-list --as user --chat-id <oc_chat_id> --page-size 5 --sort desc --format json
```

If you only have `open_id`, use `--user-id`:

```bash
lark-cli im +chat-messages-list --as user --user-id <ou_open_id> --page-size 5 --sort desc --format json
```

For custom count or time range, adjust:

```bash
lark-cli im +chat-messages-list --as user --chat-id <oc_chat_id> \
  --page-size <n> \
  --sort desc \
  --start "YYYY-MM-DDT00:00:00+08:00" \
  --end "YYYY-MM-DDT23:59:59+08:00" \
  --format json
```

## Permission handling

If contact search fails with missing `contact:user:search`, tell the user the exact command:

```bash
lark-cli auth login --scope "contact:user:search"
```

Only start the split-flow authorization when the user explicitly asks you to do it. If the user says not to send another URL, do not start a new authorization URL; try the command again using the current authorization state.

If a command fails because the user did not authorize or the device-code polling was interrupted, explain the current state clearly and do not repeat authorization URLs unless requested.

## Output format

Report the resolved person first:

```text
<input> 对应到：
- 姓名：...
- 邮箱：...
- open_id：ou_...
- P2P chat_id：oc_...
- 部门：...
```

Then list messages in the order returned by the command:

```text
最近 5 条（倒序）：
1. 2026-06-11 17:20｜左应(Brian)
   讲道理...
2. 2026-06-11 17:17｜蔡由卫
   可能还是...
```

Mention reactions only when useful, for example “（对方有 OK 反应）”. Avoid dumping raw JSON unless the user asks.

## Common examples

Resolve an enterprise email prefix/account ID and fetch recent messages:

```bash
lark-cli contact +search-user --as user --query "v_ywcai" --has-chatted --format json
lark-cli im +chat-messages-list --as user --chat-id oc_... --page-size 5 --sort desc --format json
```

Fetch by open_id:

```bash
lark-cli im +chat-messages-list --as user --user-id ou_... --page-size 5 --sort desc --format json
```

Fetch by P2P chat_id:

```bash
lark-cli im +chat-messages-list --as user --chat-id oc_... --page-size 5 --sort desc --format json
```
