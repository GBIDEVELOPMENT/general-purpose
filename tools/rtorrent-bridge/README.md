# HP rTorrent Bridge

A standalone Windows rTorrent controller and private ChatGPT MCP server. Lives in `GBIDEVELOPMENT/general-purpose/tools/rtorrent-bridge`; it does **not** depend on Chunks.

## One-click HP installation

1. In this repo, open **Actions → rTorrent Bridge Windows → latest successful run → rtorrent-bridge-windows** and download its ZIP.
2. Extract the ZIP and double-click **Run-RTorrent-Bridge.cmd**. You do not need Python or Git on the PC.
3. On first launch, enter the username/password for the primary Seedhost server. Enter optional passwords for second and third separately. Enable write tools when prompted if desired. Passwords are Windows-DPAPI-encrypted under `%LOCALAPPDATA%\RTorrentBridge\profiles.json`, tied to your Windows login. Credentials are never included in the release artifact.
4. The console runs the MCP server until closed. The local MCP endpoint is `http://127.0.0.1:8765/mcp`. Use **Check-RTorrent-Bridge.cmd** for a read-only connectivity check. Use **Configure-RTorrent-Bridge.cmd** to re-enter/replace credentials and permission choices.

Configuration currently supplies exact (not auto-guessed) Seedhost HTTPS HTTP-RPC endpoints for `/rutorrent/`, `/rutorrent2/` and `/rutorrent3/` separately. Secondary instances require their own passwords. No automatic credential cross-use or fallback. User-editable endpoint support can follow after these known targets are verified.

## Connect to ChatGPT (private, no inbound router port)

The MCP server binds **only** to loopback. Install OpenAI's `tunnel-client` via the official [Secure MCP Tunnel instructions](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels), create a tunnel in the OpenAI Platform, and configure its local HTTP server target as `http://127.0.0.1:8765/mcp`. Launch `tunnel-client run` in a separate process, then in ChatGPT Plugins add a custom MCP server, choose **Tunnel**, select the tunnel ID, review tool descriptions/permissions and save. This requires available tunnel and custom-MCP permissions in the relevant account/workspace. The Windows bridge itself does not create OpenAI resources or obtain Platform API keys. The `tunnel-client` is not bundled: download only from the official OpenAI release.

A stdio transport is also provided via `RTorrentBridge.exe stdio` for compatible local MCP clients. The TCP server and stdio mode share identical server-side tools.

## Tools

`servers`, `server_status`, `list_torrents`, `torrent_details`, `torrent_files`, `start_torrent`, `stop_torrent`, `remove_torrent` and `add_stopped_magnet`.

- The tool caller selects an exact configured server ID. Names and tracker data are not treated as commands.
- Start/stop/remove operate by a validated 40-character infohash. Remove requires the exact current torrent name and calls `d.erase`; **it does not delete downloaded files**. File deletion is intentionally out of scope.
- Magnet Add works with v1 `btih` magnets, defaults to stopped and confirms existence by readback. If a request times out or fails after dispatch, do **not** blindly retry. Inspect the torrent's exact hash first.
- Mutations are disabled unless enabled at local setup. No raw XML-RPC, arbitrary shell commands, automatic bulk deletion, remote credential import, tracker/announce URL reading or filesystem write tools.
- Actions are locally logged by server, infohash and result in `%LOCALAPPDATA%\RTorrentBridge\actions.jsonl` (no passwords, magnet or tracker URLs).

## Source development and tests

Use Python 3.12+ on Windows. `python -m pip install -r requirements.txt`, then `python -m unittest discover -s tests -v`. Run `python rtorrent_bridge.py setup`, `check` or `serve`. GitHub Actions tests offline and produces a Windows x64 self-contained ZIP using PyInstaller. The workflow does **not** consume GitHub secrets or contact seedboxes. For the first actual HP run, the owner supplies credentials locally; repository Actions secrets are not accessible to downloaded executables and must never be embedded in artifacts.

### Validation boundaries

Offline tests cover validation, identity checks, readback and error paths. A successful workflow proves Windows packaging, not live seedbox connectivity, Windows SmartScreen trust, tunnel readiness or an installed ChatGPT plugin. The user can verify the real endpoint via the read-only **Check** launcher. Any future live integration workflow must be manual-only, approved for the exact target and keep credentials outside PR jobs and artifacts. The compiled executable is not code-signed and Windows may show a publisher warning.
