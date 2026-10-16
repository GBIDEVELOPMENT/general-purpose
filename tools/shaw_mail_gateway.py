#!/usr/bin/env python3
"""One-shot encrypted mail operation, initiated by a trusted GitHub issue comment.

Runs ONLY in Actions. Secrets never appear in comments, logs or workflow
artifacts. An ephemeral private key stays in worker memory for one session.
"""
import contextlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import time
from types import SimpleNamespace
from urllib.parse import urlencode
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shaw_mail as mail
import shaw_mail_protocol as crypto

PREFIX = "SHAWMAIL2 "
OWNER = "gamesbyian"
REPOSITORY = "gamesbyian/chat-scheduler"
ISSUE = 6
MAX_WAIT_SECONDS = 110
MAX_MAIL_LIMIT = 15


def parse_comment(body):
    if not isinstance(body, str) or not body.startswith(PREFIX) or len(body) > 52000:
        return None
    try:
        value = json.loads(body[len(PREFIX):])
    except (json.JSONDecodeError, TypeError, ValueError):
        return None
    return value if isinstance(value, dict) and value.get("version") == 2 else None


def github_api(method, path, token, data=None):
    url = "https://api.github.com" + path
    payload = None if data is None else json.dumps(data).encode("utf-8")
    request = Request(url, data=payload, method=method, headers={
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
        "User-Agent": "chat-scheduler-shaw-gateway",
    })
    with urlopen(request, timeout=20) as response:
        return json.load(response)


def post_comment(token, value):
    body = PREFIX + json.dumps(value, separators=(",", ":"), ensure_ascii=False)
    if len(body) > 60000:
        raise ValueError("Encrypted response is too large")
    return github_api("POST", f"/repos/{REPOSITORY}/issues/{ISSUE}/comments",
                      token, {"body": body})


def comments_since(token, since):
    query = urlencode({"per_page": "100", "since": since})
    return github_api("GET", f"/repos/{REPOSITORY}/issues/{ISSUE}/comments?{query}", token)


def scrub_for_reply(value):
    """Bound sizes before encrypting, since issue comments have length limits."""
    if isinstance(value, str):
        return value[:4000]
    if isinstance(value, list):
        return [scrub_for_reply(v) for v in value[:MAX_MAIL_LIMIT]]
    if isinstance(value, dict):
        return {k: scrub_for_reply(v) for k, v in value.items()}
    return value


def validate_operation(operation):
    name = operation.get("name")
    if name not in ("ping", "diagnose", "folders", "inbox", "search", "read", "send"):
        raise ValueError("Unknown operation")
    if name in ("inbox", "search", "read"):
        folder = operation.get("folder", "INBOX")
        if not isinstance(folder, str) or not 1 <= len(folder) <= 200:
            raise ValueError("Invalid folder")
        if any(ord(ch) < 32 for ch in folder):
            raise ValueError("Invalid folder")
    if name in ("inbox", "search"):
        limit = operation.get("limit", 10)
        if type(limit) is not int or not 1 <= limit <= MAX_MAIL_LIMIT:
            raise ValueError("Invalid list limit")
    if name == "search":
        q = operation.get("query")
        if not isinstance(q, str) or not 1 <= len(q) <= 2000:
            raise ValueError("Invalid search query")
    if name == "read":
        uid = operation.get("uid")
        if not isinstance(uid, str) or not uid.isascii() or not uid.isdecimal() or int(uid) <= 0:
            raise ValueError("Invalid UID")
    if name == "send":
        if operation.get("confirm") is not True:
            raise ValueError("Outbound send requires confirmed user instruction")
        draft = operation.get("draft")
        if not isinstance(draft, dict):
            raise ValueError("Expected message draft")
        if not isinstance(draft.get("to"), list) or len(draft["to"]) > 10:
            raise ValueError("Too many recipients")
        if not isinstance(draft.get("body"), str) or len(draft["body"]) > 16000:
            raise ValueError("Invalid send body")
        if not isinstance(draft.get("subject"), str) or len(draft["subject"]) > 400:
            raise ValueError("Invalid subject")
    return name


def operate(operation, token, ready, request_id):
    name = validate_operation(operation)
    if name == "ping":
        return {"ok": True, "reply": "pong", "features": [
            "folders", "inbox", "search", "read", "send"
        ]}
    if not os.environ.get("SHAW_PASSWORD"):
        return {"ok": False, "error": "mail_secret_not_configured"}
    if name == "diagnose":
        return {"ok": True, "data": mail.auth_diagnostics()}
    if name == "send":
        draft = operation["draft"]
        # This claim precedes SMTP: an ambiguous outcome must not be silently retried.
        post_comment(token, {"version": 2, "kind": "send_claim",
                             "session": ready["session"], "id": request_id})
        with tempfile.TemporaryDirectory(prefix="shaw-mail-") as temp:
            path = Path(temp) / "draft.json"
            path.write_text(json.dumps(draft), encoding="utf-8")
            os.chmod(path, 0o600)
            old = os.environ.get("SHAW_ALLOW_SEND")
            os.environ["SHAW_ALLOW_SEND"] = "yes"
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    submission = mail.send(SimpleNamespace(draft=str(path), confirm=True))
            finally:
                if old is None:
                    os.environ.pop("SHAW_ALLOW_SEND", None)
                else:
                    os.environ["SHAW_ALLOW_SEND"] = old
        return {"ok": True, **submission}

    args = SimpleNamespace(command=name, folder=operation.get("folder", "INBOX"),
                           limit=operation.get("limit", 10),
                           query=operation.get("query"), uid=operation.get("uid"))
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        mail.fetch(args)
    value = scrub_for_reply(json.loads(buffer.getvalue()))
    return {"ok": True, "data": value}


def eligible(event):
    comment, issue = event.get("comment", {}), event.get("issue", {})
    if event.get("action") != "created" or issue.get("number") != ISSUE:
        return False
    if comment.get("user", {}).get("login") != OWNER:
        return False
    return parse_comment(comment.get("body")) in (
        {"version": 2, "kind": "start"},
        {"version": 2, "kind": "start_smtp"},
    )



def validate_lane(start_kind, operation):
    """The Linux read lane cannot send; the macOS lane cannot read mailbox data."""
    name = validate_operation(operation)
    if start_kind == "start":
        if name not in ("ping", "folders", "inbox", "search", "read"):
            raise ValueError("Operation not permitted on read lane")
    elif start_kind == "start_smtp":
        if name not in ("ping", "diagnose", "send"):
            raise ValueError("Operation not permitted on SMTP lane")
    else:
        raise ValueError("Unknown lane")
    return name


def run(event, token):
    if not eligible(event):
        return False
    if event.get("repository", {}).get("full_name") != REPOSITORY:
        return False
    started_comment = event["comment"]
    start_kind = parse_comment(started_comment["body"])["kind"]
    private, ready = crypto.server_session()
    ready["reply_to"] = started_comment["id"]
    post_comment(token, ready)
    since = started_comment["created_at"]
    seen = {started_comment["id"]}
    deadline = time.monotonic() + MAX_WAIT_SECONDS
    while time.monotonic() < deadline:
        for candidate in comments_since(token, since):
            cid = candidate.get("id")
            if cid in seen:
                continue
            seen.add(cid)
            if candidate.get("user", {}).get("login") != OWNER:
                continue
            try:
                command = parse_comment(candidate.get("body"))
            except (ValueError, TypeError, json.JSONDecodeError):
                continue
            if not command or command.get("kind") != "command":
                continue
            if command.get("session") != ready["session"]:
                continue
            request_id = None
            try:
                body = crypto.server_command(private, command, ready["session"])
                request_id = body["id"]
                validate_lane(start_kind, body["operation"])
                result = operate(body["operation"], token, ready, request_id)
            except Exception as exc:
                # Server errors, message contents and credentials are not logged.
                result = {"ok": False, "error": type(exc).__name__}
            if request_id is None:
                # Cannot securely correlate malformed messages; do not post details.
                return True
            reply = crypto.server_response(private, ready, command, request_id, result)
            reply["reply_to"] = cid
            post_comment(token, reply)
            return True
        time.sleep(3)
    post_comment(token, {"version": 2, "kind": "expired",
                         "session": ready["session"], "reply_to": ready["reply_to"]})
    return True


def main():
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    token = os.environ.get("GITHUB_TOKEN")
    if not event_path or not token:
        raise SystemExit("Must run in a GitHub Actions issue_comment environment")
    event = json.loads(Path(event_path).read_text(encoding="utf-8"))
    # Nothing from mail is ever printed to a workflow log.
    if run(event, token):
        print("Encrypted gateway request handled")


if __name__ == "__main__":
    main()
