#!/usr/bin/env python3
"""Local-only client for encrypted Shaw gateway comments.

It does not access GitHub, require Shaw credentials, or persist mailbox data.
Use GitHub's existing connector to post the generated envelope and to obtain the
encrypted reply. Keep the state file only in the trusted local runtime.
"""
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shaw_mail_protocol as protocol


def load_json(path):
    if path == "-":
        return json.load(sys.stdin)
    return json.loads(Path(path).read_text(encoding="utf-8"))


def create_state(path, data):
    """Fail closed instead of overwriting an unknown or existing private key."""
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as output:
            json.dump(data, output, separators=(",", ":"))
    except BaseException:
        Path(path).unlink(missing_ok=True)
        raise


def prepare(ready, operation, state_path, send_recipient=None):
    if not isinstance(ready, dict) or ready.get("kind") != "ready":
        raise ValueError("Expected ready handshake")
    if not isinstance(operation, dict) or not operation.get("name"):
        raise ValueError("Expected one operation object")
    if operation["name"] == "send":
        draft = operation.get("draft")
        if not send_recipient or not isinstance(draft, dict):
            raise ValueError("Outbound send requires an explicit recipient authorization")
        if operation.get("confirm") is not True or draft.get("to") != [send_recipient]:
            raise ValueError("Send recipient and confirmed draft do not match authorization")
    else:
        if send_recipient is not None:
            raise ValueError("Recipient authorization is only valid for sending")

    command, secret, request_id = protocol.client_command(ready, operation)
    create_state(state_path, {
        "ready": ready,
        "private": protocol.b64(secret),
        "expected_id": request_id,
    })
    return command


def complete(state_path, response, delete_state=True):
    state = json.loads(Path(state_path).read_text(encoding="utf-8"))
    data = protocol.client_response(
        protocol.unb64(state["private"], 128),
        state["ready"],
        response,
        state["expected_id"],
    )
    if delete_state:
        Path(state_path).unlink()
    return data


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    request = commands.add_parser("prepare", help="Encrypt one request and store a temporary private key")
    request.add_argument("--ready-file", required=True, help="Public ready JSON from the gateway")
    request.add_argument("--operation-file", required=True, help="Private operation JSON file, or '-' for stdin")
    request.add_argument("--state-file", required=True, help="New local-only private state path")
    request.add_argument("--authorize-send-to", help="Exact recipient explicitly approved by the user")
    result = commands.add_parser("complete", help="Decrypt one encrypted result and delete private key")
    result.add_argument("--reply-file", required=True, help="Encrypted result JSON file, or '-' for stdin")
    result.add_argument("--state-file", required=True, help="State file from prepare")
    result.add_argument("--keep-state", action="store_true")
    args = parser.parse_args(argv)

    try:
        if args.action == "prepare":
            cmd = prepare(load_json(args.ready_file), load_json(args.operation_file),
                          args.state_file, send_recipient=args.authorize_send_to)
            print("SHAWMAIL2 " + json.dumps(cmd, separators=(",", ":")))
        else:
            plaintext = complete(args.state_file, load_json(args.reply_file),
                                 delete_state=not args.keep_state)
            print(json.dumps(plaintext, ensure_ascii=False, indent=2))
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as error:
        # Do not include contents of requests, responses, or secret keys.
        print(f"Gateway client failed: {type(error).__name__}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
