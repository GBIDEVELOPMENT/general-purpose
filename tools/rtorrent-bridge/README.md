# HP rTorrent Bridge

A standalone Windows rTorrent controller and private ChatGPT MCP server. Lives in `GBIDEVELOPMENT/general-purpose/tools/rtorrent-bridge`; it does **not** depend on Chunks.

## One-click HP installation

1. In this repo, open **Actions → rTorrent Bridge Windows → latest successful run → rtorrent-bridge-windows** and download its ZIP.
2. Extract the ZIP and double-click **Run-RTorrent-Bridge.cmd**. You do not need Python or Git on the PC.
3. On first launch, enter the username/password for the primary Seedhost server. Enter optional passwords for second and third separately. Enable write tools when prompted if desired. Passwords are Windows-DPAPI-encrypted under `%LOCALAPPDATA%\RTorrentBridge\profiles.json`, tied to your Windows login. Credentials are never included in the release artifact.
4. The console runs the MCP server until closed. The local MCP endpoint is `http://127.0.0.1:8765/mcp`. Use **Check-RTorrent-Bridge.cmd** for a read-only connectivity check. Use **Configure-RTorrent-Bridge.cmd** to re-enter/replace credentials and permission choices.

Configuration currently supplies exact (not auto-guessed) Seedhost HTTPS HTTP-RPC endpoints for `/rutorrent/`, `/rutorrent2/` and `/rutorrent3/` separately. Secondary instances require their own passwords. No automatic credential cross-use or fallback.

## Credential decoding failure in the first Windows build

The first Windows artifact incorrectly attempted to protect an already DPAPI-protected
password again during connection setup, causing a `UnicodeDecodeError` before the
first network call. Fixed on this branch: stored credentials are now explicitly
**decrypted** before UTF-8 decoding. The existing `profiles.json` should remain
valid. Extract a newer successful Windows artifact into a fresh folder and
double-click `Run-RTorrent-Bridge.cmd` again. Do **not** delete or share
`%LOCALAPPDATA%\\RTorrentBridge\\profiles.json`.

If Windows reports that the saved password cannot be read (for example,
after switching Windows accounts or moving the configuration between PCs),
double-click `Configure-RTorrent-Bridge.cmd` to enter the passwords again.
This overwrites the local profile set after prompting. It never reads GitHub
Actions secrets automatically.

## Connect to ChatGPT (one-click HP launcher, no inbound router port)

**Observed acceptance:** The owner has started the Windows MCP server and verified
the primary authenticated `system.client_version` response from rTorrent 0.9.8.
That proves the PC and Seedhost path, but **a ChatGPT tunnel has not yet been
enrolled, tested or installed as a plugin**.

1. In your browser, open the official [OpenAI Platform Tunnels page](https://platform.openai.com/settings/organization/tunnels). Create a tunnel associated with the **ChatGPT workspace** where you will install the plugin. Save the full `tunnel_id`. The creator needs Tunnels Read + Manage; the runtime account and plugin operator need Tunnels Read + Use.
2. Create a **runtime API key**, not an admin key, at [Platform API keys](https://platform.openai.com/settings/organization/api-keys) with permission to use that tunnel. Do not enter this key in ChatGPT, GitHub, URLs or command-line arguments.
3. Download the newest successful `rtorrent-bridge-windows` artifact from [rTorrent Bridge Windows Actions](https://github.com/GBIDEVELOPMENT/general-purpose/actions/workflows/rtorrent-bridge-windows.yml). Extract `rtorrent-bridge-windows.zip` inside it to one directory. Double-click **`Connect-ChatGPT-RTorrent.cmd`** from the extracted directory. The script preserves existing rTorrent credentials, starts the local bridge if needed, asks once for your tunnel ID and hidden runtime key, and stores the key via current-user Windows DPAPI under `%LOCALAPPDATA%\RTorrentBridge\tunnel-key.dpapi.txt`.
4. The launcher downloads **only the official OpenAI** `tunnel-client` Windows x64 release from `github.com/openai/tunnel-client`, checks the GitHub release's SHA-256 digest, and keeps its executable under `%LOCALAPPDATA%\RTorrentBridge\bin`. It then checks `doctor --explain` and starts outbound tunnel polling. No inbound router port, Cloudflare account, or Python installation is needed. Keep this console open; diagnostic UI: `http://127.0.0.1:8877/ui`.
5. On **ChatGPT web → Plugins → + → Add custom MCP server**, name it **HP rTorrent**, choose **Tunnel**, select or paste the same `tunnel_id`, configure the server authentication according to the UI (the bridge itself has no separate MCP OAuth login), acknowledge the risk warning, and create the plugin. Review its nine discovered tools before enabling writes. The connection only counts as accepted when a live `servers` tool invocation from ChatGPT succeeds.
6. For later launches, double-click **`Connect-ChatGPT-RTorrent.cmd`** again. Existing tunnel enrollment and current-user encrypted runtime key are reused. To change the tunnel ID or runtime key, use **`Configure-ChatGPT-Tunnel.cmd`**. It only clears local tunnel pairing and never deletes your rTorrent passwords or remote Platform tunnel.

**Security boundary:** The local MCP listener uses `127.0.0.1:8765` and has
no built-in per-request authentication. Other software running under the same
Windows host can reach it, so use a trusted PC account. Remote access depends on
the scoped OpenAI tunnel and the ChatGPT plugin's own permissions. The runtime
API key is never committed, put in a GitHub Actions secret, embedded in the EXE,
or passed through command-line arguments. The PowerShell launcher decrypts the
key only for its child process environment; stop the tunnel to revoke the local
active session. For full revocation, revoke the runtime key in Platform and remove
the ChatGPT plugin.

**Troubleshooting:** If the secure tunnel has no access to the ChatGPT workspace,
the plugin creation UI may not list the tunnel. Verify its workspace association
and Tunnels Read + Use permissions. If `doctor` fails, correct the tunnel/permissions
or runtime key and use `Configure-ChatGPT-Tunnel.cmd` to enter them again. A
successful offline GitHub Actions run proves packaging and syntax, **not** your
Platform permissions or ChatGPT installation. Official documentation:
[Secure MCP Tunnel](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels),
[OpenAI tunnel-client](https://github.com/openai/tunnel-client),
[Adding a custom MCP server](https://developers.openai.com/api/docs/guides/custom-mcp-server).

A stdio transport is also provided via `RTorrentBridge.exe stdio` for local
MCP clients. The TCP server and stdio mode share identical tools.

## Adding your other rTorrent servers without resetting primary

When only the primary seedbox is configured, **double-click**
`Add-RTorrent-Servers.cmd` locally on the Windows PC. The interactive `setup --extend`
command skips existing server IDs without asking for their credentials, prompts
only for missing servers, and accepts blank passwords to skip any you are not
ready to add. Passwords are entered directly in the Windows console (never in
ChatGPT or GitHub), encrypted with user-bound DPAPI, then saved by atomic
replacement. Before replacement, it backs up the previous config as
`%LOCALAPPDATA%\RTorrentBridge\profiles.bak`. It preserves the existing
write policy, existing encrypted credential blobs and other configuration keys.
If no new passwords are provided, no files change. Do not use `setup --reset`
merely to enroll a second or third instance, because reset replaces the entire
configuration. The running bridge re-reads the config per request, so it does
not need restarting after successful enrollment. Use `Check-RTorrent-Bridge.cmd`
to verify all configured instances locally.

## Desktop Commander, no Platform API billing

The local-only `rtorrent_cli.py` uses Python's standard library to talk to the already-running
`http://127.0.0.1:8765/mcp`. From an authorized Desktop Commander session, run:

```powershell
python rtorrent_cli.py servers
python rtorrent_cli.py inventory_extremes --server primary
python rtorrent_cli.py inventory_report --server primary --target-ratio 1 --limit 10
python rtorrent_cli.py compare_servers --limit 10
python rtorrent_cli.py query_torrents --server primary --sort-by size --descending --limit 10
python rtorrent_cli.py query_torrents --server primary --no-complete --limit 20
python rtorrent_cli.py torrent_health --server primary --infohash 0123456789ABCDEF0123456789ABCDEF01234567
python rtorrent_cli.py list_torrents --server primary --limit 100
python rtorrent_cli.py list_torrents --server primary --query "Slow Horses"
```

Mutations require explicit user approval plus the CLI `--confirm` flag. The CLI does not
open a public port, persist new credentials or require an OpenAI Platform API key.
The local bridge process must be running. This is an alternate transport, not a
separately installed ChatGPT MCP plugin.

## Historical fields and their meaning

Inventory rows include `first_started_at`, `finished_at`, and `torrent_created_at` as
Unix UTC seconds (null for unknown/zero). `first_started_at` is rTorrent's recorded
start timestamp, **not** proof of when a transfer was added. `torrent_created_at`
refers to torrent metadata, not the date it entered this seedbox. `inventory_extremes`
returns the smallest, largest and earliest recorded start, and counts unknown starts.
These methods were verified against the owner's rTorrent 0.9.8 instance; future
compatibility with other versions must be qualified before deployment.

## Read-only inventory diagnostics

`inventory_report` summarizes completed and incomplete torrents, logical payload size,
instantaneous transfer rates, inactive entries, incomplete entries with zero current
speed, missing-metadata placeholders, and ratios below a caller-supplied target.
It ranks complete transfers at or above that target for **human retention review**
without taking action. These are not automatically safe deletion candidates: the
report does not know tracker-specific obligations, free disk space, file overlap,
or whether the payload still exists on disk. `compare_servers` checks exact matching
infohashes among the **configured** servers, reports unavailable instances, and
never silently represents partial inventory as complete. Both tools are bounded
by `limit` (1–100); counts remain totals even when sample lists are truncated.
All features are read-only and use the same authenticated HTTPS XML-RPC paths.

## Filtering, pagination, and transfer diagnostics

`query_torrents` provides stable, server-side paging and sorting by name, size,
ratio, total downloaded/uploaded, recorded start, finish, or current speeds.
Optional name, completion, activity and minimum-ratio filters are applied
before paging. Unknown date fields sort last in both directions. Matching counts,
next offset and the page size are returned so callers do not silently miss results.
All queries take a fresh live snapshot, so results can shift between requests;
this is not a frozen transactional inventory.

`torrent_health` looks up an exact infohash and returns read-only progress, peers
connected, unresolved peer count, remaining bytes, hashing state, number of
tracker entries and connection mode. It uses a bounded, single batched read for
peer metrics, never returns tracker URLs or peer IPs, and distinguishes
instantaneous observations from a diagnosis. Three tracker entries, for example,
do not establish tracker reachability; zero connected peers at one instant does
not establish that a swarm is permanently dead. No repair action is performed.

## Anticipated natural-language requests

- Find transfers by title, exact hash, size, ratio, completion, start time and activity.
- Explain stalled downloads, missing magnet metadata, zero-byte placeholders and
  unexpectedly high upload ratios without treating guesses as diagnoses.
- Compare inventories across configured environments, detect duplicate infohashes,
  and report capacity or storage pressure without assuming identical mount paths.
- Suggest candidates for stopping or removal using age, ratio and retention policy;
  present a preview and exact identities before any mutation.
- Batch start/stop, per-file priorities, per-torrent speed limits, destination choice,
  file deletion, and transfer migration are **not yet implemented**. Each needs
  explicit scope, preflight, readback, audit and ambiguity-safe retry semantics.
- True date-added, per-tracker rules, free-space metrics, historical rate trends and
  seed-time statistics need separately validated data sources; do not fabricate them.
- Keep credentials DPAPI-local, redact URLs/tokens, restrict RPC to allowlisted
  operations, and never expose an arbitrary RPC or shell tool through the bridge.

## Tools

`servers`, `server_status`, `list_torrents`, `torrent_details`, `torrent_files`, `start_torrent`, `stop_torrent`, `remove_torrent` and `add_stopped_magnet`.

- The tool caller selects an exact configured server ID. Names and tracker data are not treated as commands.
- Start/stop/remove operate by validated 40-character infohash. Remove requires the exact current torrent name and calls `d.erase`; **it does not delete downloaded files**. File deletion is intentionally out of scope.
- Magnet Add works with v1 `btih` magnets, defaults to stopped and confirms existence by readback. If a request times out or fails after dispatch, do **not** blindly retry. Inspect the torrent's exact hash first.
- Mutations are disabled unless enabled at local setup. No raw XML-RPC, arbitrary shell commands, automatic bulk deletion, remote credential import, tracker/announce URL reading or filesystem write tools.
- Actions are locally logged by server, infohash and result in `%LOCALAPPDATA%\RTorrentBridge\actions.jsonl` (no passwords, magnet or tracker URLs).

## Source development and tests

Use Python 3.12+ on Windows. `python -m pip install -r requirements.txt`, then `python -m unittest discover -s tests -v`. Run `python rtorrent_bridge.py setup`, `check` or `serve`. GitHub Actions tests offline and produces a Windows x64 self-contained ZIP using PyInstaller. The workflow does **not** consume GitHub secrets or contact seedboxes. For the first actual HP run, the owner supplies credentials locally; repository Actions secrets are not accessible to downloaded executables and must never be embedded in artifacts.

### Validation boundaries

Offline tests cover validation, identity checks, readback and error paths. A successful workflow proves Windows packaging, not live seedbox connectivity, Windows SmartScreen trust, tunnel readiness or an installed ChatGPT plugin. The user can verify the real endpoint via the read-only **Check** launcher. Any future live integration workflow must be manual-only, approved for the exact target and keep credentials outside PR jobs and artifacts. The compiled executable is not code-signed and Windows may show a publisher warning.
