---
name: pc-wsl-docker
description: Manage Docker containers and Compose stacks on the user's remote Windows PC that runs Docker inside WSL Debian, exposed to the LAN through Windows portproxy via `sync-ports.bat`. Use this whenever the user asks to start/stop/inspect a container, change a docker-compose stack, expose a service to the LAN, or do anything container-related on "PC", "我的电脑", "那台电脑", "the WSL box", "the home server", or any remote docker host reached via `ssh mt-pc` or direct WSL SSH `ssh mt-wsl`. Trigger even when the user does not explicitly mention WSL or portproxy — if the task is container CRUD or compose management and the target is not the local machine, default to this skill.
---

# pc-wsl-docker

Operate Docker on the remote Windows PC where:

- Docker daemon lives **inside WSL Debian** (not Docker Desktop).
- Compose stacks live in `~/docker/<stack-name>/compose.yaml` inside WSL.
- Containers publish ports only to `127.0.0.1:<port>` inside WSL.
- A Windows-side script `sync-ports.bat` mirrors every published port to `0.0.0.0:<port>` on the Windows host via `netsh portproxy`, making it reachable from the LAN.

Use **`ssh mt-pc`** for Windows-side administration and portproxy sync. Use **`ssh mt-wsl`** for a direct shell inside WSL Debian after portproxy is healthy.

## Why the workflow exists

Docker in WSL only exposes ports on the WSL VM's loopback. The LAN cannot reach WSL directly. `sync-ports.bat`:

1. Reads `docker ps --format '{{.Ports}}'` from WSL.
2. Diffs against the previously managed set stored in `~/.config/caddy/ports/.portproxy-managed.txt`.
3. Adds/removes `netsh interface portproxy` rules from `0.0.0.0:port → 127.0.0.1:port`.
4. Skips Caddy-owned ports (`80`, `443`, `2019`, `8090`) and keeps pinned ports (`9000`).

This means: **every time published ports change, `sync-ports.bat` must run** — otherwise the LAN sees stale state.

## Connection cheatsheet

| What you want | Command |
| --- | --- |
| Shell on PC (lands in MINGW64 / git-bash, already Admin) | `ssh mt-pc` |
| One-shot Windows-side command | `ssh mt-pc '<bash-cmd>'` |
| Direct WSL Debian shell | `ssh mt-wsl` |
| One-shot Docker command in WSL | `ssh mt-wsl 'docker <args>'` or `ssh mt-pc 'wsl -d Debian -- docker <args>'` |
| Multi-line bash inside WSL (login shell, paths resolved) | `ssh mt-wsl 'bash -lic "<cmd>"'` or `ssh mt-pc 'wsl -d Debian -- bash -lic "<cmd>"'` |
| Re-sync portproxy after any port change | `ssh mt-pc 'sync-ports.bat'` |
| Preview what sync would do | `ssh mt-pc 'sync-ports.bat -WhatIf'` |

Notes:

- The default SSH shell is MINGW64. Use `cat` / `ls` / forward slashes; Windows paths work as `/c/...`.
- `ssh mt-wsl` connects to WSL Debian as user `zyx` through Windows portproxy on public port `2222`; WSL `sshd` listens on `2222` and uses public-key auth only.
- `sync-ports.bat` is on `PATH` (`C:\bin\sync-ports.bat`) — call it bare.
- The script auto-elevates via UAC, but the `ssh mt-pc` session already runs as Administrator, so it just works headless.

## Standard workflow

For **every** container-related request that targets the PC, follow this loop. Do not skip steps even if the user only asked for the docker part — the LAN-facing exposure is the whole point of this setup.

### 1. Inspect current state first

Always start by listing what exists so you don't clobber anything:

```bash
ssh mt-wsl 'docker ps -a'
ssh mt-wsl 'bash -lic "ls ~/docker/"'
```

### 2. Make the change

**For ad-hoc containers** (`docker run`, `stop`, `rm`, `exec`, `logs`, …):

```bash
ssh mt-wsl 'docker run -d --name foo -p 127.0.0.1:18080:80 nginx:alpine'
ssh mt-wsl 'docker logs -n 50 foo'
```

**For compose stacks**, work inside `~/docker/<stack>/`:

```bash
ssh mt-wsl 'bash -lic "mkdir -p ~/docker/myapp && cat > ~/docker/myapp/compose.yaml << EOF
services:
  app:
    image: ...
    container_name: myapp
    restart: unless-stopped
    ports:
      - \"127.0.0.1:18080:8080\"
EOF
cd ~/docker/myapp && docker compose up -d"'
```

### 3. Always bind published ports to `127.0.0.1`

Never use `0.0.0.0:port:...` or bare `port:...` in compose / `docker run -p`. The whole proxy story depends on the WSL side staying on loopback; `sync-ports.bat` is what turns that into a LAN-reachable port. Binding to `0.0.0.0` inside WSL only exposes the WSL VM, not Windows, and confuses the proxy bookkeeping.

### 4. Run `sync-ports.bat` whenever published ports changed

After any of: `docker run` with `-p`, `docker stop/rm` of a published container, `docker compose up/down`, or editing a compose file's `ports:` block — run:

```bash
ssh mt-pc 'sync-ports.bat'
```

Expected output ends with lines like:

```
Docker host ports: 6379, 9000, 18080
Public portproxy: 6379, 9000, 18080
portproxy: updated=1 unchanged=2 removed=0
  battle.cc.ml.oa.mt:18080 -> 127.0.0.1:18080
```

If you only changed image/env/volumes but not the `ports:` list, you can skip this step; in doubt, run it — it is idempotent and cheap.

### 5. Verify

Confirm both layers actually work:

```bash
# Container is up
ssh mt-wsl 'docker ps --filter name=<container>'

# WSL loopback responds
ssh mt-wsl 'curl -s -o /dev/null -w "wsl=%{http_code}\n" http://127.0.0.1:<port>/'

# Windows public-facing portproxy is in place
ssh mt-pc 'netsh interface portproxy show all'

# Windows side actually serves it
ssh mt-pc 'curl -s -o /dev/null -w "win=%{http_code}\n" http://127.0.0.1:<port>/'
```

Report what you observed, not what you expected.

## Conventions to preserve

- **One stack per directory**: `~/docker/<name>/compose.yaml`. Don't dump multiple stacks in one file.
- **Stable `container_name`**: matches the stack name so `docker ps` is readable.
- **`restart: unless-stopped`**: every long-lived stack.
- **Volumes**: named volumes for data, bind-mounts only when the user needs to edit files from Windows (path: `/mnt/c/...`).
- **Reserved ports**: do not publish on `80`, `443`, `2019`, `8090` — Caddy owns those and `sync-ports.bat` excludes them on purpose.
- **Pinned ports**: `9000` stays in portproxy even when Docker is down; `2222` is reserved for direct `ssh mt-wsl`. Don't repurpose either without telling the user.

## Tearing down

```bash
ssh mt-wsl 'bash -lic "cd ~/docker/<stack> && docker compose down"'
# Add -v only if the user confirmed volumes should be wiped
ssh mt-pc 'sync-ports.bat'
```

For ad-hoc containers:

```bash
ssh mt-wsl 'docker rm -f <name>'
ssh mt-pc 'sync-ports.bat'
```

## Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| LAN can't reach a new port, WSL `curl 127.0.0.1:<port>` works | Forgot `sync-ports.bat`, or port is in `ExcludePorts` | Run `sync-ports.bat`; pick a different port if it's `80/443/2019/8090`. |
| `sync-ports.bat` says "Administrator privileges required" | SSH session not elevated for some reason | Re-run from a fresh `ssh mt-pc` — the session normally runs as Admin. |
| `portproxy show all` lists a stale rule | Container was removed without re-syncing | Run `sync-ports.bat`; it will diff against the managed-state file and remove orphans. |
| `wsl docker` hangs / errors right after Windows boot | WSL not yet started | `ssh mt-pc 'wsl -d Debian -- echo ready'` to warm it, then retry. |
| Need to expose on a port that differs from the backend | Edit `$PinnedPorts` in `~/.config/caddy/sync-ports.ps1` (ask the user before changing). |

## What this skill is NOT for

- Local Docker on the user's Mac → just use `docker` directly.
- Docker Desktop on Windows → this PC explicitly runs Docker inside WSL; don't suggest Docker Desktop commands.
- Editing Caddy reverse-proxy config — Caddy owns `80/443/2019/8090` separately and is out of scope here; surface a note if the user seems to want HTTPS termination.
