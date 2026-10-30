#!/usr/bin/env python3
"""One-shot Windows Shaw connectivity/authentication check; never reads or sends mail.

Run from the repo via run-shaw-diagnostic.cmd. All credentials are entered locally,
used in process memory and never written to disk or transmitted to GitHub.
Output contains only bounded diagnostic statuses, no mailbox contents.
"""
import getpass
import json
import os
import sys

import shaw_mail


def run():
    print("Shaw IMAP/SMTP authentication-only diagnostic")
    print("This checks both logins once. It does NOT list/read mail or send anything.")
    print("Use your Shaw EMAIL password (not necessarily your MyRogers password).")
    password = getpass.getpass("Shaw email password (hidden): ")
    if not password:
        print("No password entered; no network authentication attempted.")
        return 2
    previous = os.environ.get("SHAW_PASSWORD")
    try:
        os.environ["SHAW_PASSWORD"] = password
        # Fixed provider endpoints and ports from the existing audited client.
        result = shaw_mail.auth_diagnostics()
    except Exception as exc:
        # No exception text: server errors can include identifying metadata.
        result = {"diagnostic": "unexpected_failure", "exception_class": type(exc).__name__}
    finally:
        if previous is None:
            os.environ.pop("SHAW_PASSWORD", None)
        else:
            os.environ["SHAW_PASSWORD"] = previous
        del password
    print("\nRESULT (safe to paste into chat; contains no password or email):")
    print(json.dumps(result, indent=2, sort_keys=True))
    if result.get("imap") == "authentication_accepted" and result.get("smtp") == "authentication_accepted":
        print("Both authentication checks succeeded. No email was sent.")
        return 0
    print("At least one protocol needs investigation. No email was sent.")
    return 1


if __name__ == "__main__":
    try:
        sys.exit(run())
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled; no email was sent.")
        sys.exit(130)
