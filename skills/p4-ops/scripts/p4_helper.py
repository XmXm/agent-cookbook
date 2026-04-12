#!/usr/bin/env python3
"""
p4_helper.py - Helper script for common P4 operations in MLBB project
Usage: python p4_helper.py <command> [args...]

Works on Windows, macOS, and Linux.
"""

import subprocess
import sys
import os
import json
import re
import shutil
import locale
from datetime import datetime

# MLBB depot list
DEPOTS = ["MLBB", "MLBBArtBridge", "MLBBClientCode", "MLBBPlugin", "MLBBRelease"]
CODE_DEPOTS = ["MLBBClientCode", "MLBBPlugin"]


# ============================================================
# SimpleProj Configuration - Using MLBBSimple depot
# ============================================================
SIMPLEPROJ_DEPOT = "MLBBSimple"
SIMPLEPROJ_PREFIX = "AndroidSimpleProj"


def _detect_p4_encoding() -> str:
    """检测 P4 输出编码。优先使用 P4CHARSET 环境变量，否则使用系统编码。"""
    charset = os.environ.get("P4CHARSET", "")
    if charset and charset.lower() not in ("none", "auto", ""):
        mapping = {"utf8": "utf-8", "utf8-bom": "utf-8-sig", "utf16": "utf-16"}
        return mapping.get(charset.lower(), charset)
    if sys.platform == "win32":
        return locale.getpreferredencoding(False)
    return "utf-8"


_P4_ENCODING = _detect_p4_encoding()
_info_cache: dict[str, str] = {}

# 强制 stdout/stderr 使用 UTF-8 输出（Claude Code bash 终端使用 UTF-8）
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def _decode_p4_output(data: bytes) -> str:
    """解码 P4 输出。优先 UTF-8（本项目 P4 内容实际为 UTF-8），备选系统编码。"""
    if not data:
        return ""
    for enc in ["utf-8", _P4_ENCODING]:
        try:
            return data.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return data.decode("utf-8", errors="replace")


def _get_p4_info() -> dict[str, str]:
    """获取并缓存 p4 info 结果，避免重复调用。"""
    if not _info_cache:
        info = p4_output(["info"])
        for line in info.splitlines():
            if ":" in line:
                key, val = line.split(":", 1)
                _info_cache[key.strip()] = val.strip()
    return _info_cache


def run_p4(args: list[str], silent=False) -> tuple[int, str, str]:
    """Run a p4 command and return (returncode, stdout, stderr)."""
    cmd = ["p4"] + args
    try:
        result = subprocess.run(cmd, capture_output=True)
        stdout = _decode_p4_output(result.stdout)
        stderr = _decode_p4_output(result.stderr)
        return result.returncode, stdout, stderr
    except FileNotFoundError:
        if not silent:
            print("ERROR: 'p4' command not found. Please install the Perforce command-line client and ensure it's in your PATH.")
        sys.exit(1)


def p4_output(args: list[str], silent=False) -> str:
    """Run a p4 command and return stdout. Print stderr if any."""
    rc, stdout, stderr = run_p4(args, silent)
    if stderr and not silent:
        print(stderr.strip(), file=sys.stderr)
    return stdout.strip()


def p4_info_field(field: str) -> str:
    """Extract a specific field from p4 info output (cached)."""
    return _get_p4_info().get(field, "")


def get_current_user() -> str:
    return p4_info_field("User name")


def get_current_client() -> str:
    return p4_info_field("Client name")


def get_current_stream() -> str:
    stream = _get_p4_info().get("Client stream", "")
    if stream:
        return stream
    client_spec = p4_output(["client", "-o"])
    for line in client_spec.splitlines():
        if line.startswith("Stream:"):
            return line.split(None, 1)[1].strip()
    return ""


def get_opened_count() -> int:
    stdout = p4_output(["opened"], silent=True)
    if not stdout or "not opened" in stdout.lower() or "file(s) not opened" in stdout.lower():
        return 0
    return len([l for l in stdout.splitlines() if l.strip()])


# ============================================================
# Commands
# ============================================================

def cmd_info():
    """Show P4 connection and workspace info."""
    print("=== P4 Connection Info ===")
    info = p4_output(["info"])
    for line in info.splitlines():
        if any(line.startswith(f"{k}:") for k in [
            "User name", "Client name", "Client root", "Current directory",
            "Server address", "Server version", "Client stream"
        ]):
            print(f"  {line}")

    print(f"\n=== Current Stream ===")
    stream = get_current_stream()
    print(f"  {stream}" if stream else "  (not set)")

    print(f"\n=== Pending Changes ===")
    opened = get_opened_count()
    print(f"  {opened} file(s) currently opened")
    if opened > 0:
        print(p4_output(["opened"]))


def cmd_branches(pattern="*"):
    """List branches/streams, optionally filtered by pattern."""
    print("=== Available Branches ===")
    for depot in DEPOTS:
        rc, stdout, stderr = run_p4(["streams", f"//{depot}/{pattern}"], silent=True)
        if rc == 0 and stdout.strip():
            lines = stdout.strip().splitlines()
            count = len(lines)
            print(f"\n--- {depot} ({count} streams) ---")
            for line in lines[:20]:
                print(f"  {line}")
            if count > 20:
                print(f"  ... and {count - 20} more")


def _parse_version(name: str) -> tuple:
    """从分支名提取版本号元组用于排序。"""
    nums = re.findall(r"\d+", name)
    return tuple(int(n) for n in nums) if nums else (0,)


def cmd_latest_branches(count=5):
    """Find the N most recent branches (MLBB depot), sorted by version number."""
    print(f"=== {count} Most Recent Branches (MLBB depot) ===")
    stdout = p4_output(["streams", "//MLBB/Android-*"], silent=True)
    if not stdout:
        print("  No branches found.")
        return

    lines = stdout.strip().splitlines()
    lines.sort(key=lambda l: _parse_version(l), reverse=True)
    for line in lines[:count]:
        print(f"  {line}")


def cmd_switch_branch(target_stream: str, code_only=False):
    """Switch to a branch with safety checks. Default: full sync. --code-only: sync code dirs only."""
    opened = get_opened_count()
    if opened > 0:
        print(f"ERROR: {opened} file(s) currently opened. Cannot switch branches.")
        print(p4_output(["opened"]))
        print()
        print("Please shelve or submit your changes first:")
        print("  p4 shelve -c <CL>")
        print("  p4 revert //...")
        sys.exit(1)

    print(f"Switching to stream: {target_stream}")
    rc, stdout, stderr = run_p4(["client", "-s", "-S", target_stream])
    if rc != 0:
        print(f"ERROR: Failed to switch stream.\n{stderr}")
        sys.exit(1)
    print(stdout)

    _info_cache.clear()

    if code_only:
        print("Stream switched. Syncing code directories only (--code-only)...")
        cmd_sync_code()
    else:
        print("Stream switched. Syncing all files...")
        rc, stdout, stderr = run_p4(["sync"])
        print(stdout)
        if stderr:
            print(stderr, file=sys.stderr)

    print("\n=== Now on stream ===")
    print(f"  {get_current_stream()}")


def cmd_sync_code(changelist=None):
    """Sync only code-related directories (faster for developers)."""
    stream = get_current_stream()
    if not stream:
        print("ERROR: No stream set on current workspace.")
        sys.exit(1)

    # Extract the stream path segment (e.g., "trunk" or "Android-2.1.18.1123.1")
    # Stream looks like //MLBB/trunk or //MLBB/Android-xxx
    stream_base = stream.split("/")[-1]

    suffix = f"@{changelist}" if changelist else ""

    print(f"=== Syncing code directories ===")
    print(f"  Stream: {stream}")

    sync_targets = [
        (f"//MLBBClientCode/{stream_base}/Scripts/...{suffix}", "MLBBClientCode Scripts"),
        (f"//MLBBPlugin/{stream_base}/MobaPlugin/Scripts/...{suffix}", "MLBBPlugin Scripts"),
        (f"//MLBB/{stream_base}/Assets/Document/...{suffix}", "Document"),
        (f"//MLBB/{stream_base}/Assets/lua/...{suffix}", "lua"),
        (f"//MLBB/{stream_base}/Assets/lua_add/...{suffix}", "lua_add"),
        (f"//MLBB/{stream_base}/Assets/lua_hotfix/...{suffix}", "lua_hotfix"),
        (f"//MLBB/{stream_base}/Assets/lua_override/...{suffix}", "lua_override"),
        (f"//MLBB/{stream_base}/Assets/UI/...{suffix}", "UI"),
        (f"//MLBB/{stream_base}/Assets/Plugins/...{suffix}", "Plugins"),
    ]

    for target, label in sync_targets:
        print(f"  Syncing {label}...")
        rc, stdout, stderr = run_p4(["sync", target], silent=True)
        if stdout.strip():
            count = len(stdout.strip().splitlines())
            print(f"    {count} file(s) updated")
        else:
            print(f"    (up to date)")

    print("=== Code sync complete ===")


def cmd_recent_changes(count=20, user=None):
    """Show recent changes for code directories."""
    print(f"=== Recent Code Changes (last {count}) ===")

    for depot, label in [("MLBBClientCode", "MobaBattle + MobaScripts"), ("MLBBPlugin", "MobaPlugin")]:
        print(f"\n--- {depot} ({label}) ---")
        args = ["changes", "-l", "-m", str(count)]
        if user:
            args.extend(["-u", user])
        args.append(f"//{depot}/...")
        stdout = p4_output(args, silent=True)
        if stdout:
            print(stdout)
        else:
            print("  (no changes)")


def _parse_changes(stdout: str) -> list[dict]:
    """解析 p4 changes -l 输出为 [{header, desc}] 列表。"""
    changes = []
    current = None
    for line in stdout.splitlines():
        if line.startswith("Change "):
            if current:
                changes.append(current)
            current = {"header": line, "desc": ""}
        elif current and line and line[0] in ("\t", " "):
            current["desc"] += line.strip() + " "
    if current:
        changes.append(current)
    return changes


def cmd_find_cl(keyword: str, max_changes=200, user: str = None):
    """在 MLBBClientCode 中搜索提交描述匹配关键词的 CL。

    user: 按提交者过滤（搜索老CL时很有用，大幅缩小扫描范围）
    max_changes: 搜索最近 N 条 CL（默认 200，配合 --user 可用更大值如 500）
    """
    parts = [f"last {max_changes}"]
    if user:
        parts.append(f"user={user}")
    label = ", ".join(parts)
    print(f"=== Searching submitted CLs for '{keyword}' ({label}) ===")

    args = ["changes", "-s", "submitted", "-l", "-m", str(max_changes)]
    if user:
        args.extend(["-u", user])
    args.append("//MLBBClientCode/...")

    stdout = p4_output(args)
    if not stdout:
        print("  No changes found.")
        return

    changes = _parse_changes(stdout)

    # 关键词过滤（大小写不敏感）
    kw = keyword.lower()
    matches = [c for c in changes if kw in c["desc"].lower() or kw in c["header"].lower()]

    if not matches:
        print(f"  No matching CLs found.")
        return

    print(f"  Found {len(matches)} match(es):\n")
    for c in matches[:20]:
        print(c["header"])
        desc = c["desc"].strip()
        if len(desc) > 300:
            desc = desc[:300] + "..."
        print(f"    {desc}\n")


def cmd_describe(cl: str):
    """显示 CL 的描述、影响文件和统一 diff。"""
    stdout = p4_output(["describe", "-du", cl])
    if not stdout:
        print(f"ERROR: CL {cl} not found.")
        return
    print(stdout)


def cmd_status():
    """Show overall workspace status."""
    user = get_current_user()

    print("=== Workspace Status ===")

    print(f"\n--- Current Stream ---")
    print(f"  {get_current_stream()}")

    print(f"\n--- Opened Files ---")
    stdout = p4_output(["opened"], silent=True)
    if stdout and "not opened" not in stdout.lower():
        print(stdout)
    else:
        print("  (none)")

    print(f"\n--- Pending Changelists ---")
    stdout = p4_output(["changes", "-s", "pending", "-u", user], silent=True)
    print(stdout if stdout else "  (none)")

    print(f"\n--- Shelved Changelists ---")
    stdout = p4_output(["changes", "-s", "shelved", "-u", user], silent=True)
    print(stdout if stdout else "  (none)")


def cmd_depot_map(filepath: str):
    """Show which depot a local file maps to."""
    print(f"=== Depot Mapping for: {filepath} ===")

    stdout = p4_output(["where", filepath], silent=True)
    if stdout:
        print(stdout)
    else:
        print("  File not in client view")

    print()
    stdout = p4_output([
        "fstat", "-T",
        "depotFile,clientFile,headRev,haveRev,headChange,headAction,action",
        filepath
    ], silent=True)
    if stdout:
        print(stdout)
    else:
        print("  No fstat info available")


def cmd_safe_shelve():
    """Check pending changes and guide user to shelve manually (read-only, no server writes)."""
    user = get_current_user()
    client = get_current_client()

    print("=== Pending Changes Check ===")

    stdout = p4_output(["changes", "-s", "pending", "-u", user, "-c", client], silent=True)
    if not stdout:
        print("  No pending changelists. Safe to switch branches.")
        return

    changelists = []
    for line in stdout.splitlines():
        match = re.match(r"Change (\d+)", line)
        if match:
            changelists.append(match.group(1))

    if not changelists:
        print("  No pending changelists. Safe to switch branches.")
        return

    print(f"  Found {len(changelists)} pending changelist(s):\n")
    for cl in changelists:
        print(f"    Change {cl}")
        # Show opened files in this CL
        opened = p4_output(["opened", "-c", cl], silent=True)
        if opened:
            for f in opened.splitlines()[:10]:
                print(f"      {f}")
            total = len(opened.splitlines())
            if total > 10:
                print(f"      ... and {total - 10} more")

    print(f"\n  WARNING: Please shelve or submit before switching branches.")
    print(f"  To shelve and revert:")
    for cl in changelists:
        print(f"    p4 shelve -c {cl}")
    print(f"    p4 revert //...")


def cmd_find_file(pattern: str):
    """Find files matching a pattern across code depots."""
    print(f"=== Searching for: {pattern} ===")
    stream = get_current_stream()
    stream_base = stream.split("/")[-1] if stream else "trunk"

    search_paths = [
        f"//MLBBClientCode/{stream_base}/Scripts/.../{pattern}",
        f"//MLBBPlugin/{stream_base}/MobaPlugin/Scripts/.../{pattern}",
        f"//MLBB/{stream_base}/Assets/Scripts/.../{pattern}",
        f"//MLBB/{stream_base}/Assets/Document/.../{pattern}",
        f"//MLBB/{stream_base}/Assets/lua/.../{pattern}",
        f"//MLBB/{stream_base}/Assets/UI/.../{pattern}",
    ]

    total = 0
    for path in search_paths:
        stdout = p4_output(["files", path], silent=True)
        if stdout and "no such file" not in stdout.lower():
            for line in stdout.strip().splitlines():
                print(f"  {line}")
                total += 1

    if total == 0:
        print("  No files found.")
    else:
        print(f"\n  Total: {total} file(s)")


def cmd_blame(filepath: str):
    """Show annotate (blame) for a file."""
    print(f"=== Annotate: {filepath} ===")
    stdout = p4_output(["annotate", "-c", filepath])
    print(stdout)


def cmd_diff_branch(branch_stream=None):
    """Show code differences between current stream and trunk (or specified branch)."""
    current = get_current_stream()
    if not current:
        print("ERROR: No stream set.")
        sys.exit(1)

    target = branch_stream or "//MLBB/trunk"
    current_base = current.split("/")[-1]
    target_base = target.split("/")[-1]

    print(f"=== Code diff: {current_base} vs {target_base} ===")

    for depot, path in [("MLBBClientCode", "Scripts"), ("MLBBPlugin", "MobaPlugin/Scripts")]:
        print(f"\n--- {depot}/{path} ---")
        stdout = p4_output([
            "interchanges",
            f"//{depot}/{target_base}/{path}/...",
            f"//{depot}/{current_base}/{path}/..."
        ], silent=True)
        if stdout:
            print(stdout)
        else:
            print("  (no pending integrations)")


def cmd_export(depot_path: str, output_dir: str):
    """
    Export files from a depot path to a local directory without workspace mapping.
    Uses 'p4 print' so no sync record is created.

    Automatically detects directory paths and exports the full directory recursively.

    depot_path: e.g. //MLBB/AdjustSvnUtil/Tools/BattleMegeUtils/
                or   //MLBB/AdjustSvnUtil/Tools/BattleMegeUtils/...
                or   //MLBB/AdjustSvnUtil/Tools/somefile.py
                can include @changelist or #rev suffix
    output_dir: local directory to export into
    """

    # Separate the revision/changelist spec from the path if present
    rev_spec = ""
    clean_path = depot_path
    for sep in ["@", "#"]:
        if sep in depot_path:
            idx = depot_path.index(sep)
            clean_path = depot_path[:idx]
            rev_spec = depot_path[idx:]
            break

    # Normalize: strip trailing slashes
    clean_path = clean_path.rstrip("/\\")

    # Determine if this is a directory or single file.
    # If it already ends with /... treat as directory.
    # Otherwise, probe with 'p4 dirs' to check if it's a directory in the depot.
    is_directory = clean_path.endswith("/...") or clean_path.endswith("\\...")

    if is_directory:
        # Remove the /... for base_path calculation
        base_path = clean_path.rstrip(".").rstrip("/\\")
        dir_path = clean_path + rev_spec
    else:
        # Check if it's a depot directory by trying 'p4 dirs'
        rc, stdout, stderr = run_p4(["dirs", clean_path], silent=True)
        if rc == 0 and stdout.strip() and "no such file" not in stdout.lower():
            # It's a directory, export recursively
            is_directory = True
            base_path = clean_path
            dir_path = f"{clean_path}/...{rev_spec}"
        else:
            # Single file export
            filename = clean_path.split("/")[-1]
            local_file = os.path.join(output_dir, filename)
            os.makedirs(output_dir, exist_ok=True)
            print(f"Exporting: {depot_path}")
            print(f"       To: {local_file}")
            rc, stdout, stderr = run_p4(["print", "-q", "-o", local_file, depot_path])
            if rc == 0:
                print(f"  Done.")
            else:
                print(f"  ERROR: {stderr.strip()}")
            return

    # Directory export: list all files then export each one
    print(f"=== Exporting depot directory ===")
    print(f"  From: {base_path}/...")
    if rev_spec:
        print(f"  Rev:  {rev_spec}")
    print(f"    To: {output_dir}")
    print()

    # List files
    print("  Listing files...")
    files_output = p4_output(["files", dir_path], silent=True)
    if not files_output or "no such file" in files_output.lower():
        print("  ERROR: No files found at this depot path.")
        print(f"  Tried: p4 files {dir_path}")
        print("  Hint: check the path with 'p4 dirs <parent_path>' or 'p4 files <path>/...' first.")
        return

    file_lines = [l for l in files_output.strip().splitlines() if l.strip()]
    total = len(file_lines)
    print(f"  Found {total} file(s)")
    print()

    exported = 0
    errors = 0
    for i, line in enumerate(file_lines):
        # Line format: //depot/path/file#rev - action change N (type)
        match = re.match(r"^(//[^#]+)#\d+", line)
        if not match:
            continue

        depot_file = match.group(1)

        # Calculate relative path from base_path
        if depot_file.startswith(base_path + "/"):
            rel_path = depot_file[len(base_path) + 1:]
        else:
            rel_path = depot_file.split("/")[-1]

        # Convert to OS path
        local_path = os.path.join(output_dir, rel_path.replace("/", os.sep))

        # Create parent directories
        parent_dir = os.path.dirname(local_path)
        os.makedirs(parent_dir, exist_ok=True)

        # Export with p4 print -q -o
        source = f"{depot_file}{rev_spec}"
        rc, _, stderr = run_p4(["print", "-q", "-o", local_path, source], silent=True)
        if rc == 0:
            exported += 1
        else:
            errors += 1
            print(f"  ERROR exporting {rel_path}: {stderr.strip()}")

        # Progress
        if (i + 1) % 50 == 0 or (i + 1) == total:
            print(f"  Progress: {i + 1}/{total} ({exported} exported, {errors} errors)")

    print(f"\n=== Export complete ===")
    print(f"  Total files: {total}")
    print(f"  Exported:    {exported}")
    if errors:
        print(f"  Errors:      {errors}")
    print(f"  Output dir:  {os.path.abspath(output_dir)}")


# ============================================================
# P4VC GUI Commands
# ============================================================

def cmd_p4vc(action: str, target: str):
    """Launch P4V GUI windows via 'cmd /c p4v.exe -p4vc'."""
    valid_actions = ["workspacewindow", "history", "diff"]
    if action not in valid_actions:
        print(f"ERROR: unknown p4vc action '{action}'")
        print(f"  Valid actions: {', '.join(valid_actions)}")
        return

    if action == "workspacewindow":
        cmd = ["cmd", "/c", "p4v.exe", "-p4vc", "workspacewindow", "-s", target]
    else:
        cmd = ["cmd", "/c", "p4v.exe", "-p4vc", action, target]

    # Set MSYS_NO_PATHCONV to prevent MSYS/Git Bash from mangling paths like //depot/...
    env = os.environ.copy()
    env["MSYS_NO_PATHCONV"] = "1"

    print(f"Launching: {' '.join(cmd)}")
    try:
        subprocess.Popen(cmd, env=env)
        print("  P4V window opened.")
    except FileNotFoundError:
        print("ERROR: 'p4v.exe' not found. Please ensure P4V is installed and in your PATH.")


# ============================================================
# SimpleProj (瘦身工程) - Using MLBBSimple depot
# ============================================================

def _get_simpleproj_branches(count=10):
    """List recent branches from MLBBSimple depot."""
    stdout = p4_output(["streams", f"//{SIMPLEPROJ_DEPOT}/{SIMPLEPROJ_PREFIX}-*"], silent=True)
    if not stdout:
        return []
    branches = []
    for line in stdout.strip().splitlines():
        match = re.match(rf"Stream (//\S+/{SIMPLEPROJ_PREFIX}-(\S+))", line)
        if match:
            branches.append((match.group(2), match.group(1)))
    branches.sort(key=lambda x: [int(n) for n in re.findall(r"\d+", x[0])] if re.findall(r"\d+", x[0]) else [0], reverse=True)
    return branches[:count]


def _simpleproj_client_name(user: str, branch_name: str) -> str:
    ver = branch_name.replace("Android-", "").replace(".", "_")
    return f"{SIMPLEPROJ_PREFIX}-{user}-{ver}"


def _detect_simpleproj_client() -> tuple:
    import os
    cwd = os.path.abspath(".").replace("/", "\\")
    user = get_current_user()
    stdout = p4_output(["clients", "-u", user], silent=True)
    if not stdout:
        return None, None, None
    for line in stdout.strip().splitlines():
        match = re.match(rf"Client (\S*{SIMPLEPROJ_PREFIX}\S*)\s+\S+\s+root\s+(\S+)", line)
        if match:
            name, root = match.group(1), match.group(2).replace("/", "\\")
            if cwd.startswith(root) or cwd == root:
                spec = p4_output(["-c", name, "client", "-o"], silent=True)
                stream = next((l.split(None, 1)[1].strip() for l in spec.splitlines() if l.startswith("Stream:")), "")
                return name, stream, root
    return None, None, None


def _create_simpleproj_client(client_name: str, root_dir: str, stream: str) -> bool:
    import os
    abs_root = os.path.abspath(root_dir)
    os.makedirs(abs_root, exist_ok=True)
    rc, spec, stderr = run_p4(["client", "-S", stream, "-o", client_name], silent=True)
    if rc != 0:
        print(f"  ERROR: Failed to generate client spec.\n  {stderr.strip()}")
        return False
    new_lines = []
    for line in spec.splitlines():
        if line.startswith("Root:"):
            new_lines.append(f"Root:\t{abs_root}")
        elif line.startswith("Options:"):
            opts = line.split("\t", 1)[1] if "\t" in line else line.split(None, 1)[1]
            new_lines.append(f"Options:\t{opts.replace('noallwrite', 'allwrite')}")
        else:
            new_lines.append(line)
    input_bytes = ("\n".join(new_lines) + "\n").encode(_P4_ENCODING)
    result = subprocess.run(["p4", "client", "-i"], input=input_bytes, capture_output=True)
    if result.returncode != 0:
        print(f"  ERROR: Failed to create client.\n  {result.stderr.strip()}")
        return False
    print(f"  Root set to: {abs_root}")
    return True


def cmd_simpleproj(action: str, args: list):
    if action == "list":
        branches = _get_simpleproj_branches(int(args[0]) if args else 10)
        if not branches:
            print("  No branches found.")
            return
        print("=== Available SimpleProj Branches ===\n")
        for i, (name, path) in enumerate(branches, 1):
            print(f"  {i}. {name}")
        print(f"\nUsage: python p4_helper.py simpleproj pull <branch_name> [target_dir]")
    
    elif action == "pull":
        if not args:
            print("ERROR: specify a branch name.")
            print("  Usage: simpleproj pull Android-2.1.64.1178.1 [target_dir]")
            return
        branch_name = args[0]
        if not branch_name.startswith("Android-"):
            branch_name = f"Android-{branch_name}"
        target_dir = args[1] if len(args) > 1 else f"AndroidSimpleProj-{branch_name.replace('Android-', '')}"
        stream = f"//{SIMPLEPROJ_DEPOT}/{SIMPLEPROJ_PREFIX}-{branch_name.replace('Android-', '')}"
        user = get_current_user()
        client_name = _simpleproj_client_name(user, branch_name)
        abs_target = os.path.abspath(target_dir)
        
        print(f"=== Pull SimpleProj ===")
        print(f"  Branch:    {branch_name}")
        print(f"  Stream:    {stream}")
        print(f"  Target:    {abs_target}")
        print(f"  Workspace: {client_name}")
        
        # Verify stream exists
        rc, _, stderr = run_p4(["stream", "-o", stream], silent=True)
        if rc != 0 or "no such" in stderr.lower():
            print(f"\nERROR: Stream {stream} not found.")
            return
        
        # Check if client exists
        rc, stdout, _ = run_p4(["clients", "-e", client_name], silent=True)
        if stdout.strip() and client_name in stdout:
            print(f"\n  Workspace '{client_name}' already exists.")
            # Check for pending changes
            opened_out = p4_output(["-c", client_name, "opened"], silent=True)
            if opened_out and "not opened" not in opened_out.lower():
                opened_count = len([l for l in opened_out.splitlines() if l.strip()])
                if opened_count > 0:
                    print(f"\n  ERROR: {opened_count} file(s) opened. Please shelve or submit first.")
                    return
            # Switch stream if different
            run_p4(["-c", client_name, "client", "-s", "-S", stream])
        else:
            print(f"\n  Creating workspace '{client_name}'...")
            if not _create_simpleproj_client(client_name, abs_target, stream):
                return
        
        # Sync all files
        print("\n  Syncing files...")
        rc, stdout, stderr = run_p4(["-c", client_name, "sync"], silent=True)
        if stdout.strip():
            count = len([l for l in stdout.strip().splitlines() if l.strip()])
            print(f"    {count} file(s) updated")
        else:
            print(f"    (up to date)")
        
        print(f"\n  Done! Project is at: {abs_target}")
        print(f"  To submit changes, use: p4 -c {client_name} submit")
    
    elif action == "switch":
        if not args:
            print("ERROR: specify a branch name.")
            print("  Usage: simpleproj switch Android-2.1.64.1178.1")
            return
        branch_name = args[0]
        if not branch_name.startswith("Android-"):
            branch_name = f"Android-{branch_name}"
        stream = f"//{SIMPLEPROJ_DEPOT}/{SIMPLEPROJ_PREFIX}-{branch_name.replace('Android-', '')}"
        
        client_name, current_stream, root = _detect_simpleproj_client()
        if not client_name:
            print("ERROR: No simpleproj workspace found for current directory.")
            return
        
        print(f"=== Switch SimpleProj ===")
        print(f"  Workspace: {client_name}")
        print(f"  Target:    {branch_name}")
        
        # Safety check
        opened_out = p4_output(["-c", client_name, "opened"], silent=True)
        if opened_out and "not opened" not in opened_out.lower():
            opened_count = len([l for l in opened_out.splitlines() if l.strip()])
            if opened_count > 0:
                print(f"\n  ERROR: {opened_count} file(s) opened. Cannot switch.")
                return
        
        print(f"  Switching stream...")
        rc, _, stderr = run_p4(["-c", client_name, "client", "-s", "-S", stream])
        if rc != 0:
            print(f"  ERROR: {stderr.strip()}")
            return
        
        print("  Syncing files...")
        rc, stdout, stderr = run_p4(["-c", client_name, "sync"], silent=True)
        if stdout.strip():
            count = len([l for l in stdout.strip().splitlines() if l.strip()])
            print(f"    {count} file(s) updated")
        else:
            print("    (up to date)")
        print("  Done!")
    
    elif action == "update":
        client_name, stream, root = _detect_simpleproj_client()
        if not client_name:
            print("ERROR: No simpleproj workspace found.")
            return
        
        print(f"=== Update SimpleProj ===")
        print(f"  Workspace: {client_name}")
        print(f"  Stream:    {stream}")
        
        rc, stdout, _ = run_p4(["-c", client_name, "sync"], silent=True)
        if stdout.strip():
            count = len([l for l in stdout.strip().splitlines() if l.strip()])
            print(f"  {count} file(s) updated")
        else:
            print("  (up to date)")
    
    elif action == "clean":
        client_name, stream, root = _detect_simpleproj_client()
        if not client_name and args:
            branch_name = args[0]
            if not branch_name.startswith("Android-"):
                branch_name = f"Android-{branch_name}"
            user = get_current_user()
            client_name = _simpleproj_client_name(user, branch_name)
            rc, stdout, _ = run_p4(["clients", "-e", client_name], silent=True)
            if not stdout.strip() or client_name not in stdout:
                print(f"ERROR: Workspace '{client_name}' not found.")
                return
            spec = p4_output(["-c", client_name, "client", "-o"], silent=True)
            for line in spec.splitlines():
                if line.startswith("Root:"):
                    root = line.split("\t", 1)[1].strip() if "\t" in line else line.split(None, 1)[1].strip()
                    break
        
        if not client_name:
            print("ERROR: No simpleproj workspace found.")
            return
        
        print(f"=== Clean SimpleProj ===")
        print(f"  Workspace: {client_name}")
        print(f"  Root:      {root}")
        
        print("\n  [1/3] Reverting opened files...")
        run_p4(["-c", client_name, "revert", "//..."], silent=True)
        
        print(f"  [2/3] Deleting workspace...")
        run_p4(["client", "-d", client_name], silent=True)
        
        if root and os.path.isdir(root):
            print(f"  [3/3] Removing local directory: {root}")
            shutil.rmtree(root, ignore_errors=True)
        
        print("\n  Clean complete.")
    
    else:
        print(f"Unknown simpleproj action: {action}")
        print("  Available: list, pull, switch, update, clean")


def _dispatch_find_cl(args):
    """解析 find-cl 参数：find-cl <keyword> [max] [--user name]"""
    if not args:
        print("ERROR: specify a keyword to search")
        return
    keyword = args[0]
    max_changes = 200
    user = None
    i = 1
    while i < len(args):
        if args[i] == "--user" and i + 1 < len(args):
            user = args[i + 1]
            i += 2
        elif args[i].isdigit():
            max_changes = int(args[i])
            i += 1
        else:
            i += 1
    cmd_find_cl(keyword, max_changes, user)


def cmd_help():
    """Show help message."""
    print("""MLBB P4 Helper Script (Python)

Usage: python p4_helper.py <command> [args...]

Commands:
  info                        Show P4 connection and workspace info
  branches [pattern]          List available branches/streams
  latest [count]              Show N most recent branches (default: 5)
  switch <stream> [--code-only]  Switch to a branch stream (default: full sync, --code-only: code dirs only)
  sync-code [changelist]      Sync only code-related directories
  recent [count] [user]       Show recent code changes
  find-cl <keyword> [max] [--user name]
                              Search submitted CLs in MLBBClientCode by keyword (--user for old CLs)
  describe <CL>               Show CL description, affected files, and unified diff
  status                      Show workspace status overview
  depot-map <file>            Show depot mapping for a local file
  safe-shelve                 Check pending changes & show shelve commands (read-only)
  find <pattern>              Find files matching pattern in code depots
  blame <file>                Show line-by-line annotation (blame)
  diff-branch [stream]        Show pending integrations vs trunk or another branch
  export <depot_path> <dir>   Export depot files to local dir (no workspace needed)
  p4vc <action> <target>      Open P4V GUI (workspacewindow/history/diff)
  simpleproj <action> [args]  Manage slim project (list/pull/switch/update/clean)

SimpleProj Actions:
  simpleproj list [count]              List available simpleproj branches
  simpleproj pull <branch> [dir]       Pull slim project for a branch
  simpleproj switch <branch>           Switch slim project to another branch
  simpleproj update                    Re-sync current slim project
  simpleproj clean [branch]            Delete workspace & local directory

Examples:
  python p4_helper.py status
  python p4_helper.py latest 10
  python p4_helper.py switch //MLBB/Android-2.1.64.1178.1
  python p4_helper.py sync-code
  python p4_helper.py find-cl "feishu.cn/ml/story/detail/6922547"
  python p4_helper.py describe 1809922
  python p4_helper.py export //MLBB/AdjustSvnUtil/Tools/BattleMegeUtils C:\\temp\\export
  python p4_helper.py p4vc history Assets/Scripts/MobaBattle/SomeFile.cs
  python p4_helper.py p4vc workspacewindow //MLBBClientCode/trunk/Scripts
  python p4_helper.py simpleproj list
  python p4_helper.py simpleproj pull Android-2.1.64.1178.1
  python p4_helper.py simpleproj pull 2.1.64.1178.1
  python p4_helper.py simpleproj switch Android-2.1.64.1178.1
  python p4_helper.py simpleproj update
  python p4_helper.py simpleproj clean Android-2.1.64.1178.1
""")


def main():
    if len(sys.argv) < 2:
        cmd_help()
        return

    command = sys.argv[1].lower().replace("_", "-")
    args = sys.argv[2:]

    commands = {
        "info": lambda: cmd_info(),
        "branches": lambda: cmd_branches(args[0] if args else "*"),
        "latest": lambda: cmd_latest_branches(int(args[0]) if args else 5),
        "switch": lambda: cmd_switch_branch(args[0], code_only="--code-only" in args) if args else print("ERROR: specify a stream, e.g. //MLBB/Android-2.1.18.1123.1"),
        "sync-code": lambda: cmd_sync_code(args[0] if args else None),
        "recent": lambda: cmd_recent_changes(int(args[0]) if args else 20, args[1] if len(args) > 1 else None),
        "find-cl": lambda: _dispatch_find_cl(args),
        "describe": lambda: cmd_describe(args[0]) if args else print("ERROR: specify a CL number"),
        "status": lambda: cmd_status(),
        "depot-map": lambda: cmd_depot_map(args[0]) if args else print("ERROR: specify a file path"),
        "safe-shelve": lambda: cmd_safe_shelve(),
        "find": lambda: cmd_find_file(args[0]) if args else print("ERROR: specify a pattern"),
        "blame": lambda: cmd_blame(args[0]) if args else print("ERROR: specify a file path"),
        "diff-branch": lambda: cmd_diff_branch(args[0] if args else None),
        "export": lambda: cmd_export(args[0], args[1]) if len(args) >= 2 else print("ERROR: usage: export <depot_path> <output_dir>"),
        "p4vc": lambda: cmd_p4vc(args[0], args[1]) if len(args) >= 2 else print("ERROR: usage: p4vc <workspacewindow|history|diff> <target>"),
        "simpleproj": lambda: cmd_simpleproj(args[0], args[1:]) if args else cmd_simpleproj("help", []),
        "help": lambda: cmd_help(),
    }

    if command in commands:
        commands[command]()
    else:
        print(f"Unknown command: {command}")
        cmd_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
