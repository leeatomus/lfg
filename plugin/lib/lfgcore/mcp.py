"""`lfg mcp <name>`: the MCP servers the plugin declares in plugin/.mcp.json.

They exist only while the plugin is on (so only in repos where LFG is on). Each starts the real server when its pack
is set up, and otherwise a tiny stub that offers no tools and says how to add the pack, so a missing optional pack
never shows up as a failing server in /mcp."""
import json
import os
import shutil
import sys

from . import common as C

EXTRA_PATH = [os.path.join(C.HOME, ".local", "bin"), "/opt/homebrew/bin", "/usr/local/bin"]
SERVERS = ("code-review-graph", "dev-graph", "second-brain", "headroom")


def _which(name):
    return shutil.which(name, path=os.environ.get("PATH", "") + os.pathsep + os.pathsep.join(EXTRA_PATH))


def _exec(argv):
    env = dict(os.environ)
    env["PATH"] = env.get("PATH", "") + os.pathsep + os.pathsep.join(EXTRA_PATH)
    os.execvpe(argv[0], argv, env)


def why_not(name):
    """None when the real server can start, else a one-line reason with the fix."""
    if name == "code-review-graph":
        return None if _which("code-review-graph") else \
            "code-review-graph isn't installed: run `lfg setup` (Core) or `uv tool install code-review-graph`."
    if name in ("dev-graph", "second-brain"):
        from . import omnigraph as OG
        if not _which("npx"):
            return "%s needs node (npx): run `lfg add knowledge`." % name
        if not OG.ready(name):
            return "%s isn't running: run `lfg add knowledge` (or `lfg omnigraph restart %s`)." % (name, name)
        return None
    if name == "headroom":
        from . import setup as SU
        if not SU.pack_on("headroom"):
            return "Headroom is off: turn it on in `lfg ui` → Settings → Claude Code, or `lfg add headroom`."
        return None if _which("headroom") else "headroom isn't installed: run `lfg add headroom`."
    return "unknown LFG MCP server %r" % name


def serve(name):
    if name not in SERVERS:
        C.die("unknown MCP server %r (expected one of %s)" % (name, ", ".join(SERVERS)), 2)
    reason = why_not(name)
    if reason:
        return stub(name, reason)
    if name == "code-review-graph":
        _exec([_which("code-review-graph"), "serve"])
    elif name == "headroom":
        _exec([_which("headroom"), "mcp", "serve"])
    else:
        from . import omnigraph as OG
        OG.mcp(name)
    return 0


def stub(name, reason, stdin=None, stdout=None):
    """A minimal MCP stdio server with no tools (JSON-RPC, one message per line)."""
    stdin, stdout = stdin or sys.stdin, stdout or sys.stdout
    while True:
        line = stdin.readline()
        if not line:
            return 0
        try:
            msg = json.loads(line)
        except ValueError:
            continue
        if not isinstance(msg, dict) or msg.get("id") is None:
            continue  # notifications need no answer
        method, out = msg.get("method"), {"jsonrpc": "2.0", "id": msg["id"]}
        if method == "initialize":
            out["result"] = {"protocolVersion": (msg.get("params") or {}).get("protocolVersion") or "2025-06-18",
                             "capabilities": {"tools": {}},
                             "serverInfo": {"name": "lfg-%s (not set up)" % name, "version": C.VERSION},
                             "instructions": reason}
        elif method == "tools/list":
            out["result"] = {"tools": []}
        elif method == "ping":
            out["result"] = {}
        else:
            out["error"] = {"code": -32601, "message": reason}
        stdout.write(json.dumps(out) + "\n")
        stdout.flush()
