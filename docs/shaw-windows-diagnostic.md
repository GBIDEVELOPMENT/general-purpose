# Shaw email: one-click Windows authentication diagnostics

This is an optional PC-side check for the existing `@shaw.ca` bridge. It is
**diagnostic-only**: no email is sent, no IMAP folder is selected, and no message
is fetched. It runs on the owner's HP Windows PC using the existing client,
which has already demonstrated read-only IMAP access from GitHub Actions.

## Run on the HP PC

1. Update your local checkout of this repo after the pull request is merged
   (e.g. `git pull --ff-only` in the existing checkout).
2. Double-click `tools/run-shaw-diagnostic.cmd`.
3. Enter the Shaw **email-account** password when prompted. The terminal hides it.
4. Copy only the printed `RESULT` JSON into ChatGPT. **Never send the password**.

Requires Python 3.10+ already on the PC. The diagnostic has no third-party
dependencies and does not ask you to change email settings or update GitHub
secrets. The password is held in this Python process's environment only for
the duration of two sequential login checks; it is not put in command-line
arguments, written to files or included in the result. Avoid running other
untrusted processes under your Windows login while testing.

The code performs exactly one IMAP authentication attempt to
`imap.shaw.ca:993`, and exactly one SMTP authentication attempt to
`mail.shaw.ca:587` after verified STARTTLS. It never calls SMTP DATA.
Existing TLS settings require TLS >= 1.2, trusted certificates and ECDHE
ciphers. It does **not** disable certificate validation.

## Interpret

- `imap=authentication_accepted`: Shaw IMAP read path is available from PC.
- `smtp=authentication_accepted`: SMTP login works; this **does not**
  establish that actual mail submission/delivery will work.
- `smtp=network_error`, `smtp=smtp_response_error`, or
  `smtp=smtp_protocol_error`: use the safe phase/code fields to distinguish
  host/network blocking from pre-auth protocol trouble.
- `authentication_rejected`: check whether Shaw Webmail Classic mode has
  third-party-client access enabled, and verify the email-account password.
  Do not hammer the login endpoint with repeated tests.
- `tls_error`: preserve certificate verification; do not downgrade TLS.

The previous GitHub-based SMTP attempt had an ambiguous outcome. **This
program does not retry that message.** A later real-world send test requires
a *new* explicit recipient, subject and message authorization and a new,
unique message identifier. If SMTP AUTH succeeds, plan a separate sender
workflow with an idempotency journal and user-approved one-shot submission.

## Existing protected bridge

The privileged GitHub email workflow is pinned to a reviewed source commit.
This diagnostic does **not** change that workflow, the email password
secret, or encrypted issue #6. Read the trust requirements in
`docs/shaw-mail-bridge.md` and `AGENTS.md` before any credential-bearing
production change. This is the recommended entrypoint before attempting
a local Shaw mail agent; no Cloudflare, open inbound port or new provider.
