"""Local-only CLI for the already-running rTorrent MCP bridge.
No external packages, API keys, or public listeners. Output is JSON.
"""
import argparse
import json
import sys
import urllib.request
import urllib.error

URL = "http://127.0.0.1:8765/mcp"
READ_ONLY = {"servers", "server_status", "list_torrents", "inventory_extremes", "inventory_report", "compare_servers", "query_torrents", "torrent_health", "torrent_details", "torrent_files"}
WRITES = {"start_torrent", "stop_torrent", "remove_torrent", "add_stopped_magnet"}
TOOLS = READ_ONLY | WRITES

class MCPClient:
    def __init__(self):
        self.session = None
        self.sequence = 0

    def request(self, method, params=None, notification=False):
        self.sequence += 1
        payload = {"jsonrpc": "2.0", "method": method}
        if not notification:
            payload["id"] = self.sequence
        if params is not None:
            payload["params"] = params
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "MCP-Protocol-Version": "2025-03-26",
        }
        if self.session:
            headers["Mcp-Session-Id"] = self.session
        req = urllib.request.Request(URL, json.dumps(payload).encode(), headers, method="POST")
        with urllib.request.urlopen(req, timeout=25) as resp:
            sid = resp.headers.get("Mcp-Session-Id")
            if sid:
                self.session = sid
            raw = resp.read().decode("utf-8")
            if notification or not raw.strip():
                return {}
            if "text/event-stream" in resp.headers.get("Content-Type", ""):
                events = []
                for line in raw.splitlines():
                    if line.startswith("data:"):
                        try:
                            events.append(json.loads(line[5:].strip()))
                        except json.JSONDecodeError:
                            pass
                matches = [x for x in events if x.get("id") == payload.get("id")]
                if not matches:
                    raise RuntimeError("No matching MCP response event")
                result = matches[-1]
            else:
                result = json.loads(raw)
            if "error" in result:
                raise RuntimeError(json.dumps(result["error"]))
            return result.get("result", {})

    def initialize(self):
        self.request("initialize", {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "rtorrent-local-cli", "version": "1.0"},
        })
        self.request("notifications/initialized", notification=True)

def main():
    p = argparse.ArgumentParser(description="Safe, local rTorrent MCP command-line client")
    p.add_argument("tool", choices=sorted(TOOLS) + ["tools"])
    p.add_argument("--server", default="primary", help="Exact configured server ID")
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--query", default=None)
    p.add_argument("--target-ratio", type=float, default=None)
    p.add_argument("--sort-by", default=None)
    p.add_argument("--descending", action="store_true")
    p.add_argument("--offset", type=int, default=None)
    p.add_argument("--complete", action=argparse.BooleanOptionalAction, default=None)
    p.add_argument("--active", action=argparse.BooleanOptionalAction, default=None)
    p.add_argument("--min-ratio", type=float, default=None)
    p.add_argument("--infohash", default=None)
    p.add_argument("--expected-name", default=None)
    p.add_argument("--magnet", default=None)
    p.add_argument("--confirm", action="store_true", help="Explicitly authorize a single mutation")
    args = p.parse_args()
    if args.tool in WRITES and not args.confirm:
        p.error("Write operation requires --confirm after explicit user approval")
    client = MCPClient()
    client.initialize()
    listing = client.request("tools/list")
    available = {t["name"]: t for t in listing.get("tools", [])}
    if args.tool == "tools":
        print(json.dumps({"tools": [{"name": t["name"], "inputSchema": t.get("inputSchema", {})} for t in available.values()]}, indent=2))
        return
    if args.tool not in available:
        raise RuntimeError("MCP tool is not exposed: " + args.tool)
    schema = available[args.tool].get("inputSchema", {})
    properties = schema.get("properties", {})
    supplied = {"server": args.server, "limit": args.limit, "query": args.query,
                "target_ratio": args.target_ratio,
                "sort_by": args.sort_by, "descending": args.descending,
                "offset": args.offset, "complete": args.complete,
                "active": args.active, "min_ratio": args.min_ratio,
                "infohash": args.infohash, "confirm_name": args.expected_name,
                "magnet_uri": args.magnet}
    params = {k: v for k, v in supplied.items() if k in properties and v is not None}
    missing = [k for k in schema.get("required", []) if k not in params]
    if missing:
        raise RuntimeError("Missing required parameters: " + ", ".join(missing) + ". Inspect tools for exact schema.")
    result = client.request("tools/call", {"name": args.tool, "arguments": params})
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result.get("isError"):
        sys.exit(2)

if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, urllib.error.URLError, TimeoutError) as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)
