# Shaw mail integration: status and usage

> **Live status, October 16, 2026:** Encrypted GitHub Actions gateway, Shaw IMAP authentication, discovery of 11 folders, three-message header-only listing, and a literal server-side search returning three matched UIDs are **live verified**. A single full-message `read` request returned a sizeable encrypted response, but its MIME data has not yet been accepted through independent plaintext inspection. SMTP is **not live verified for authentication or sending**: an Azure runner got `554` pre-authentication rejection citing Spamhaus; a no-secret GitHub macOS runner negotiated verified TLS and advertised AUTH, but the first credentialed macOS check disconnected at initial `EHLO` before AUTH. The two separate gateway lanes and source pin are merged/tested. No email has been sent. The user authorized mailbox diagnostics and supplied the secret in GitHub Actions.

The private chat-scheduler repository contains an offline-testable, **opt-in** IMAP/SMTP client for the existing Shaw account `ian.wallace@shaw.ca`. It is separate from recurring agent-audit records.

## Verified provider configuration

Rogers documents IMAP at `imap.shaw.ca:993` (TLS) and SMTP at `mail.shaw.ca:587` (STARTTLS), both with the username before `@shaw.ca`. The account must have Shaw Webmail **Classic mode** and **Access from Other Mail Client** enabled using desktop Webmail.

- https://www.rogers.com/support/internet/shaw-email-service-details-and-settings
- https://www.rogers.com/support/internet/shaw-email/which-email-setup-method-is-right-for-me

Live IMAP authentication and searches succeeded. SMTP message transmission has NOT been run.

## CLI commands

Python 3.10+, no external libraries. The account address has a repository-level default; it can be overridden with `SHAW_EMAIL`. The password is **never** in the repository. The trusted GitHub Actions workflow currently receives the configured `SHAW_PASSWORD` secret, which is never committed as source code.

```sh
python tools/shaw_mail.py folders
python tools/shaw_mail.py inbox --folder INBOX --limit 20
python tools/shaw_mail.py inbox --folder 'Sent Items' --limit 20
python tools/shaw_mail.py search --folder INBOX --query 'meeting'
python tools/shaw_mail.py read --folder INBOX --uid 123
```

`folders` lists discovered IMAP folder names. Folder-specific **UIDs are not globally unique**. Pass the same folder name when reading a UID reported by listing or search. Listing is read-only, uses header-only fetches, and does not mark messages as read. Reading a specific message fetches its body and returns text or HTML parts in JSON. Attachment bytes are not automatically written to disk.

For a plain-text send, write an **untracked local** JSON draft with `to` (array of addresses), `subject`, and `body`; see `examples/shaw-draft.example.json`. Run:

```sh
python tools/shaw_mail.py send --draft /private/path/draft.json
```

That previews without contacting SMTP. Once the user has explicitly authorized that **specific** message, a trusted operator can set `SHAW_ALLOW_SEND=yes` and run:

```sh
python tools/shaw_mail.py send --draft /private/path/draft.json --confirm
```

Those two flags are **not** a genuine security boundary against an agent with direct access to the account password. Do not inject the password into an untrusted agent's environment. The `SHAW_ALLOWED_RECIPIENTS` variable can optionally restrict the recipient list, but does not replace proper operator authorization.

## Experimental GitHub Actions bridge

Issue #6 is the private **encrypted command exchange** and PR #7 adds its Action. A command is initiated by an issue comment containing:

\`SHAWMAIL2 {"version":2,"kind":"start"}\`

The trusted Actions job checks the author, repository and issue. It creates an ephemeral X25519 key **in RAM**, comments its public key and session ID, and polls for one encrypted command. The caller supplies a fresh X25519 public key and ChaCha20-Poly1305 ciphertext containing a bounded command. The worker returns an encrypted response that only that caller's private key can decrypt. Both private encryption keys disappear when the session ends. This can be tested with \`{"name":"ping"}\` without credentials. The protocol code is in \`tools/shaw_mail_protocol.py\`, the one-shot worker in \`tools/shaw_mail_gateway.py\`, and tests in \`tests/test_shaw_mail_gateway.py\`.

Commands supported: \`ping\`, \`folders\`, \`inbox\`, \`search\`, \`read\` and \`send\`. Mailbox reads use IMAP read-only selection and return only encrypted results to the caller. Send requests are encrypted, require \`confirm: true\` and a complete draft, and generate a metadata-only claim comment *before* attempting SMTP. Because SMTP success can be ambiguous if a response is lost, a send must never be automatically retried without a new user instruction.

Private data, credentials, search terms and drafts MUST NOT be included in the unencrypted start comment, logs, PRs, issues, CI artifacts or audit records. A ready/expired event, session identifier, opaque ciphertext, request ID, and send claim metadata are the only items visible to repository readers. The GitHub issue itself is PRIVATE, but this encryption minimizes unnecessary retention.

### IMPORTANT: remaining trust boundary

**The user has now entered SHA_PASSWORD after accepting this risk.** GitHub Actions checks out code from main. Anyone who can alter this repo's privileged workflow or its imported mail/crypto modules can modify it to read and exfiltrate the mailbox secret. The existing GitHub integration has write access, so agents who can modify this repository could bypass code-level safeguards. We could not confirm that protected workflow ownership or a required reviewer has been configured, and GitHub rulesets were unavailable on this private repository via the present connection. A dedicated protected deployment would be stronger.

The bridge is not a native ChatGPT plugin. ChatGPT can drive it using available GitHub issue-comment operations plus an isolated cryptography runtime, but each operation requires an ephemeral handshake and may be limited by Actions startup/timeout. It does not run in the background or give any always-on mail access.

To use this from a future authorized chat session: create a fresh in-memory client key, post the start comment to issue #6, identify the reply by \`reply_to\`, encrypt the user-authorized operation to its \`server_public\`, post the command, identify the result by \`reply_to\` and \`session\`, decrypt locally, discard the client key. Never persist client private keys in the repo or send private mailbox data back through GitHub.

### Operational acceptance gates

1. Offline CI passing and a pinned source review.
2. Live encrypted \`ping\` over issue #6 (no mail password).
3. Independent repository privilege/review protection before adding a real personal mailbox credential, or conscious explicit acceptance of the repo-writer threat.
4. User enters one secret named \`SHAW_PASSWORD\` in GitHub Settings > Secrets and variables > Actions. Never send the password in chat.
5. Test \`folders\`, then harmless \`inbox\`, then \`read\`; do not send a test email without direct user instruction.

For architectural/security follow-through see issue #5.


## GitHub Actions secret-scope risk

GitHub documents that a **repository-level Actions secret is accessible to every workflow in that repository**, not just the workflow referencing it today. This matters because chat-scheduler contains other automations and is writable by other project agents. The mail gateway now pins its runtime checkout to audited source commit `12a8c032a5cd9e00a805c1bfb5f5a6f5f9a38601`, limiting accidental imported-code changes. **That pin cannot prevent a writer from editing the workflow itself or introducing another secret-consuming workflow.**

GitHub's environment secrets can limit access to jobs that reference an environment, but the environment and rulesets APIs were unavailable for this private repository with the current account/integration. Environment-scoped secrets alone also cannot defend against an authorized writer who can change the workflow to request that environment. The strongest boundary is a dedicated protected credential service or repository whose privileged code is inaccessible to other coding agents.

References: https://docs.github.com/en/actions/concepts/security/secrets and https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments

The encrypted no-secret ping succeeded on October 16, 2026. Initial password attempts rejected authentication for both protocols, but after the user updated the secret, **IMAP authentication succeeded**. SMTP AUTH has not been reached successfully due to pre-authentication network rejection or disconnection.


## October 16, 2026: IMAP TLS compatibility diagnosis

An encrypted `folders` request reached the real Shaw server from GitHub Actions
but failed with `SSLError`. A separate credential-free runner probe established
the exact error: `DH_KEY_TOO_SMALL` when using OpenSSL 3 defaults. The server
also successfully negotiated `TLSv1.2 / ECDHE-RSA-AES256-GCM-SHA384`, with
full certificate verification enabled, when restricted to ECDHE cipher suites.

The IMAP client now explicitly sets `minimum_version=TLSv1_2` and
`set_ciphers("ECDHE:!DHE:!aNULL:!eNULL")`. This **does not disable TLS
certificate verification, hostname checking, or lower the OpenSSL security
level**. Avoid workarounds using `CERT_NONE`, `check_hostname=False`, or
`@SECLEVEL=1`.

The privileged mail workflow is pinned to a fixed source commit. Updating the
client alone does not alter the credential-bearing runtime. After merging
the client fix and successful CI, update the trusted checkout SHA in
`.github/workflows/shaw-mail-gateway.yml` and its regression test in a
separate reviewed PR, then retest `folders` over the encrypted bridge.


## Authentication-only diagnostic

An updated gateway supports the encrypted `diagnose` operation. It checks
IMAP `LOGIN` and SMTP `AUTH` independently, while **neither selecting/reading
mailboxes nor sending messages**. Returned status codes are limited to
`authentication_accepted`, `authentication_rejected`, `tls_error`,
`tls_or_protocol_error`, and `network_error`. No server authentication
responses or account passwords are included.

If SMTP accepts authentication but IMAP rejects it, verify that Shaw
Webmail uses Classic mode and that external client access is permitted.
If both reject it, verify the `SHAW_PASSWORD` secret contains the actual
mailbox password (not necessarily a separate provider account password).
Avoid repeated automated login retries or account lockouts. The diagnostic
is opt-in and remains password-free in CI.


## Superseded initial password-recovery instructions (2026-10-16)

1. Confirm `https://webmail.shaw.ca` accepts the **email account password** for `ian.wallace@shaw.ca`. Rogers documents that MyRogers (Shaw) account credentials may be different.
2. From a desktop browser, in Webmail Classic mode, enable **Preferences > Access from Other Mail Client**. Rogers says this cannot be configured from mobile devices.
3. If Webmail authentication fails, reset the **email address password** (not the MyRogers login password) using the MyRogers (Shaw) portal. Enter the corrected mailbox password in GitHub Actions `SHAW_PASSWORD` secret, replacing the previous value. Never paste it into issue comments or chat.
4. Once the user reports those changes, perform one encrypted `diagnose` operation or `folders` request. If successful, do a small `inbox` header-only read, and only send if the user gives an explicit new instruction with recipients and content.

Official references:
- https://www.rogers.com/support/internet/shaw-email/changing-your-shaw-email-password
- https://www.rogers.com/support/internet/shaw-email/which-email-setup-method-is-right-for-me

## SMTP discovery, October 16, 2026

A no-secret GitHub-hosted network probe confirmed `mail.shaw.ca:587`
responds to EHLO, advertises STARTTLS and both PLAIN/LOGIN authentication,
and negotiates a certificate-validated TLS 1.2 ECDHE-RSA-AES256-GCM-SHA384
cipher under both default and ECDHE-only settings. Port 465 timed out
from the runner; keep 587.

The earlier `tls_or_protocol_error` result was too broad to distinguish
authentication errors from SMTP protocol errors during or after login.
Python `smtplib.SMTP`'s context manager sends QUIT on exit, which can
raise even when AUTH succeeded. The revised login diagnostic uses `close()`
without QUIT, returning only a safe SMTP response *code*, failure stage
and exception category, never the server response text or password.
This diagnostic does **not send mail**. The production send operation
must remain gated behind a separate user instruction, regardless of
the diagnostic result.

Official Shaw settings: https://www.rogers.com/support/internet/shaw-email-service-details-and-settings


## SMTP runner separation and delivery safeguards, October 16, 2026

The GitHub issue #6 gateway supports two exact, owner-authored start requests:

- `SHAWMAIL2 {"version":2,"kind":"start"}`: Linux Ubuntu, restricted to `ping`, `folders`, `inbox`, `search`, and `read`. It **cannot send**.
- `SHAWMAIL2 {"version":2,"kind":"start_smtp"}`: GitHub macOS cloud, restricted to `ping`, `diagnose`, and `send`. It **cannot read mailbox data**.

These request kinds are unencrypted metadata that reveal only the lane. All operation parameters, credentials and responses remain encrypted, with the same ephemeral X25519 handshake as before. A GitHub macOS runner consumes more Actions minutes than a Linux runner, so it is used only for SMTP-related operations.

A no-password diagnostic from GitHub's macOS cloud connected to
`mail.shaw.ca:587`, received EHLO status 250, successfully completed STARTTLS
with certificate verification and `ECDHE-RSA-AES256-GCM-SHA384`, and saw
SMTP AUTH advertised. **SMTP login and delivery are not yet live-verified.**

`mail.send` and the encrypted response now distinguish complete from partial
recipient acceptance, recording counts of submitted, accepted and rejected
recipients. The code closes the SMTP transport without risking a spurious error
from the implicit QUIT command *after* successful acceptance. Sending still
requires an explicit new user instruction naming recipients and content.
If delivery acknowledgement is lost after the operation starts, **do not
automatically retry**, as an email may already have been accepted.

Linux runner failure (no credentials): Shaw's SMTP server rejected one Azure
runner with status `554` and a Spamhaus IP-blocklisting policy. This is about
the sending network, not the user's Shaw password or message content.
No IP-rotation retry loop is implemented.


## Subsequent live acceptance and outbound blocker (October 16, 2026)

- Both Linux and macOS encrypted gateway lanes are implemented and protected by an exact source SHA. Offline tests passed on the integrated change.
- A Linux encrypted `search` of `INBOX` with a generic ASCII query succeeded and returned three UIDs. Those headers were decrypted only in isolated execution; no message content was copied into GitHub issues or logs.
- A single live `read` operation returned an encrypted result. The response was not fully decrypted/inspected for MIME acceptance in this run; do not overclaim that full-body parsing has been independently verified.
- An authenticated SMTP diagnostic through macOS returned `smtp_protocol_error` with exception category `SMTPServerDisconnected` at phase `ehlo`. SMTP AUTH was not reached; no outbound message was sent. A prior Linux diagnostic returned server status `554` before AUTH, explicitly identifying an Azure runner IP in a Spamhaus policy rejection.
- A no-credential GET of `https://webmail.shaw.ca/` succeeded, while `/service/soap/`, `/service/soap`, and `/zimbra/` returned HTTP 404. There is no evidence of a usable standard Zimbra SOAP send endpoint, so do not build a Webmail fallback by assuming that API exists.
- No automatic runner/IP retry rotation is implemented. Prefer a stable, permitted, authenticated outgoing transport if future user-directed sending is needed. Any real send requires a fresh, explicit instruction for recipients/content and must not be used as a diagnostic without one.
- The credential resides only in GitHub Actions `SHAW_PASSWORD`. Keep source pin and repository-writing risks in view.

Evidence and follow-through: issue #5, PRs #15–#18, and secret-free diagnostic workflows on `diagnostics/shaw-smtp-greeting-554`, `diagnostics/shaw-smtp-macos-egress`, `diagnostics/shaw-webmail-https-discovery`.

## Local encrypted request helper

`tools/shaw_gateway_client.py` makes future mailbox tasks easier without
granting GitHub Actions direct access to the local session private key.
It uses only the existing `shaw_mail_protocol.py` and the already-pinned
cryptography library. It does not have GitHub API credentials and **does not
read the Shaw mailbox by itself**.

An authorized operator using the existing GitHub connector:

1. Posts the exact `SHAWMAIL2` start comment in private issue #6.
2. Saves the matching bot `ready` JSON locally as `ready.json`.
3. Constructs a single intended operation in a private local `operation.json`
   file, for instance `{"name":"inbox","folder":"Sent","limit":5}`.
4. Runs `python tools/shaw_gateway_client.py prepare --ready-file ready.json
   --operation-file operation.json --state-file /tmp/shaw-private-state.json`.
   This prints only encrypted command metadata and stores the ephemeral private
   key with `0600` permissions. Send operations require an additional
   `--authorize-send-to` argument matching the exact one allowed recipient.
5. Posts that encrypted command to issue #6, obtains the bot result, and saves
   the result JSON as `reply.json`. Run
   `python tools/shaw_gateway_client.py complete --reply-file reply.json
   --state-file /tmp/shaw-private-state.json` in the trusted local runtime.
   It decrypts the response locally and removes the private state file after
   successful authentication and decryption.

**Do not commit** any of these local `*.json` operation/response/state files,
pipe decrypted mailbox data to GitHub logs, or reuse private state for a new
session. The read-only `start` lane cannot send. Only `start_smtp` permits
a separately authorized send. Sending can be ambiguous if the SMTP server
closes unexpectedly; consult the destination inbox before even considering
a repeat.

### Live acceptance update

On October 16, 2026, an encrypted `inbox` request against the actual `Sent`
folder successfully decrypted six message headers, demonstrating that folder
selection and header-only reads work beyond the main inbox. No message bodies
were needed for this verification.
