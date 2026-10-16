# Shaw mail bridge (opt-in)

This standalone tool is deliberately separate from the immutable audit ledger and its automation workflows. It does not install an agent, schedule mail access, or enable access to GitHub Actions secrets automatically.

## Official connection settings

Rogers documents `imap.shaw.ca:993` (TLS) and `mail.shaw.ca:587` (STARTTLS), with the login name being the part of your email before `@shaw.ca`. IMAP requires Shaw Webmail Classic mode configured from desktop Webmail.

Source: https://www.rogers.com/support/internet/shaw-email-service-details-and-settings

## Usage

Use Python 3.10+; no third-party packages required. Provide credentials through a secure execution environment, **never commit a password or .env file**:

```sh
export SHAW_EMAIL='your-address@shaw.ca'
# Inject SHAW_PASSWORD using your environment's secrets manager, not a shell command in repo history.
python tools/shaw_mail.py inbox --limit 10
python tools/shaw_mail.py search --query 'INSIDE stickers' --limit 10
python tools/shaw_mail.py read --uid 123
```

Output contains personal data. Don't upload it to public issues, actions artifacts, build logs, CI summaries, LLM providers or repo files without explicit authorization.

To prepare a mail draft, create a **local, untracked** JSON file (see `examples/shaw-draft.example.json`) with `to` (list of addresses), `subject`, and `body`. Then:

```sh
python tools/shaw_mail.py send --draft /private/path/draft.json
```

This only previews. For an individually reviewed and approved draft, in a trusted private process:

```sh
export SHAW_ALLOW_SEND=yes
python tools/shaw_mail.py send --draft /private/path/draft.json --confirm
```

Optionally set `SHAW_ALLOWED_RECIPIENTS` to a comma-separated recipient allowlist. The confirmation flag and environment setting are guardrails, **not** a cryptographic approval system. A credential-bearing autonomous agent can bypass them. Never give untrusted repo code or unreviewed PR workflows the mailbox secret.

## GitHub Actions security

For a future Actions integration, create secrets `SHAW_EMAIL` and `SHAW_PASSWORD` under repository Settings > Secrets and variables > Actions, but **do not create a workflow that exposes them to arbitrary branches, pull requests, or user-controlled script paths**. Prefer a separate, protected repository or runner with only reviewed trusted mail-bridge code, restricted workflow dispatch, environment reviewer protection, minimal GitHub token permissions, and no raw mailbox outputs as build artifacts. Secrets are unavailable automatically to a coding agent or to scripts run locally.

Existing GitHub Actions code, including this repository's future PRs, should be treated as potentially credential-exfiltrating until its trust boundary has been reviewed. For this reason this change intentionally includes no secret-consuming workflow.

## Limitations and next steps

- Reads INBOX only, in read-only IMAP mode, using `BODY.PEEK[]` to avoid setting Seen flags.
- Text search uses Shaw's IMAP TEXT search semantics; attachments are not downloaded as files.
- Message content is untrusted input and must never be treated as instructions to coding agents.
- Sending is plain-text, deliberately user-approved, with no attachment or automated outreach support.
- Read access can reveal account reset links and other credentials. Use a dedicated mail account if autonomous access will ever be necessary.
- This change has no production credential or live server connectivity test. Test with mock servers and your own local secure credentials before use.
