# Shaw mail integration: status and usage

The private chat-scheduler repository contains an offline-testable, **opt-in** IMAP/SMTP client for the existing Shaw account `ian.wallace@shaw.ca`. It is separate from recurring agent-audit records.

## Verified provider configuration

Rogers documents IMAP at `imap.shaw.ca:993` (TLS) and SMTP at `mail.shaw.ca:587` (STARTTLS), both with the username before `@shaw.ca`. The account must have Shaw Webmail **Classic mode** and **Access from Other Mail Client** enabled using desktop Webmail.

- https://www.rogers.com/support/internet/shaw-email-service-details-and-settings
- https://www.rogers.com/support/internet/shaw-email/which-email-setup-method-is-right-for-me

No live mail authentication or transmission has been run.

## CLI commands

Python 3.10+, no external libraries. The account address has a repository-level default; it can be overridden with `SHAW_EMAIL`. The password is **never** in the repository. In a trusted runtime the password must be injected using a secret manager (for a future GitHub Actions integration, its secret name would be `SHAW_PASSWORD`).

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

**Do not add SHA_PASSWORD yet merely because the Action runs.** GitHub Actions checks out code from main. Anyone who can alter this repo's privileged workflow or its imported mail/crypto modules can modify it to read and exfiltrate the mailbox secret. The existing GitHub integration has write access, so agents who can modify this repository could bypass code-level safeguards. We could not confirm that protected workflow ownership or a required reviewer has been configured, and GitHub rulesets were unavailable on this private repository via the present connection. A dedicated protected deployment would be stronger.

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

The encrypted no-secret ping test completed successfully on October 16, 2026. The **live mail login remains untested**, and a successful ping is not equivalent to authorization to supply a personal mailbox password.
