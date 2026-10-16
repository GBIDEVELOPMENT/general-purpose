#!/usr/bin/env python3
"""Minimal Shaw IMAP/SMTP client. Never persist credentials or mailbox content."""
import argparse
import email
from email.header import decode_header, make_header
from email.message import EmailMessage
import imaplib
import json
import os
import smtplib
import ssl
import sys
from pathlib import Path

IMAP_HOST = "imap.shaw.ca"
SMTP_HOST = "mail.shaw.ca"
DEFAULT_LIMIT = 20
MAX_LIMIT = 100


def credentials():
    address = os.environ.get("SHAW_EMAIL", "").strip()
    password = os.environ.get("SHAW_PASSWORD", "")
    if not address.lower().endswith("@shaw.ca") or not password:
        raise ValueError("Set SHAW_EMAIL (full @shaw.ca address) and SHAW_PASSWORD securely")
    return address, address.rsplit("@", 1)[0], password


def decode(value):
    return str(make_header(decode_header(value or "")))


def message_summary(uid, raw, include_body=False):
    msg = email.message_from_bytes(raw)
    item = {
        "uid": uid.decode("ascii"),
        "from": decode(msg.get("From")),
        "to": decode(msg.get("To")),
        "subject": decode(msg.get("Subject")),
        "date": msg.get("Date", ""),
        "message_id": msg.get("Message-ID", ""),
    }
    if include_body:
        parts = msg.walk() if msg.is_multipart() else [msg]
        bodies = []
        for part in parts:
            if part.get_content_maintype() != "text" or part.get_content_disposition() == "attachment":
                continue
            payload = part.get_payload(decode=True) or b""
            charset = part.get_content_charset() or "utf-8"
            bodies.append({"content_type": part.get_content_type(),
                           "text": payload.decode(charset, errors="replace")[:50000]})
        item["body_parts"] = bodies
    return item


def fetch(args):
    _, user, password = credentials()
    with imaplib.IMAP4_SSL(IMAP_HOST, 993, ssl_context=ssl.create_default_context(), timeout=30) as conn:
        conn.login(user, password)
        status, _ = conn.select(args.folder, readonly=True)
        if status != "OK":
            raise RuntimeError("Could not select INBOX")
        if args.command == "read":
            if not args.uid.isascii() or not args.uid.isdecimal() or int(args.uid) <= 0:
                raise ValueError("UID must be a positive integer")
            uids = [args.uid.encode("ascii")]
        else:
            # Search is performed server-side. Never interpolate arbitrary IMAP syntax.
            if args.command == "search":
                if "\r" in args.query or "\n" in args.query:
                    raise ValueError("Invalid search query")
                criterion = ["TEXT", '"' + args.query.replace("\\\\", "\\\\\\\\").replace('"', '\\\\"') + '"']
            else:
                criterion = ["ALL"]
            status, data = conn.uid("SEARCH", None, *criterion)
            if status != "OK":
                raise RuntimeError("Search failed")
            uids = (data[0] or b"").split()[-args.limit:][::-1]
        items = []
        for uid in uids:
            status, data = conn.uid("FETCH", uid, "(BODY.PEEK[])")
            if status != "OK":
                raise RuntimeError("Fetch failed")
            raw = next((part[1] for part in data if isinstance(part, tuple)), None)
            if raw is not None:
                items.append(message_summary(uid, raw, args.command == "read"))
        print(json.dumps(items, indent=2, ensure_ascii=False))


def compose(draft):
    sender, _, _ = credentials()
    to = draft.get("to")
    subject = draft.get("subject")
    body = draft.get("body")
    if not isinstance(to, list) or not to or not all(isinstance(x, str) and "@" in x and "\n" not in x and "\r" not in x for x in to):
        raise ValueError("Draft requires a nonempty list of recipient addresses")
    if not isinstance(subject, str) or not isinstance(body, str):
        raise ValueError("Draft requires string subject and body")
    recipients = set(x.strip().lower() for x in to)
    allowed = set(x.strip().lower() for x in os.environ.get("SHAW_ALLOWED_RECIPIENTS", "").split(",") if x.strip())
    if allowed and not recipients.issubset(allowed):
        raise ValueError("Recipient outside SHAW_ALLOWED_RECIPIENTS")
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = ", ".join(to)
    msg["Subject"] = subject
    msg.set_content(body)
    return msg


def send(args):
    path = Path(args.draft)
    draft = json.loads(path.read_text(encoding="utf-8"))
    msg = compose(draft)
    if not args.confirm:
        print(json.dumps({"mode": "preview_only", "from": msg["From"],
                          "to": msg["To"], "subject": msg["Subject"], "body": draft["body"]}, indent=2))
        return
    if os.environ.get("SHAW_ALLOW_SEND") != "yes":
        raise ValueError("Sending disabled: set SHAW_ALLOW_SEND=yes after approving this exact draft")
    _, user, password = credentials()
    with smtplib.SMTP(SMTP_HOST, 587, timeout=30) as smtp:
        smtp.ehlo()
        smtp.starttls(context=ssl.create_default_context())
        smtp.ehlo()
        smtp.login(user, password)
        smtp.send_message(msg)
    print("Sent to approved recipients")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    inbox = subs.add_parser("inbox", help="List recent messages")
    inbox.add_argument("--folder", default="INBOX")
    inbox.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    search = subs.add_parser("search", help="Search server-side message text")
    search.add_argument("--query", required=True)
    search.add_argument("--folder", default="INBOX")
    search.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    read = subs.add_parser("read", help="Read one message by IMAP UID")
    read.add_argument("--uid", required=True)
    read.add_argument("--folder", default="INBOX")
    submit = subs.add_parser("send", help="Preview a JSON draft, or send after explicit approval")
    submit.add_argument("--draft", required=True)
    submit.add_argument("--confirm", action="store_true")
    args = parser.parse_args()
    if hasattr(args, "limit") and not (1 <= args.limit <= MAX_LIMIT):
        parser.error(f"limit must be between 1 and {MAX_LIMIT}")
    try:
        if args.command == "send":
            send(args)
        else:
            fetch(args)
    except (ValueError, OSError, imaplib.IMAP4.error, smtplib.SMTPException, json.JSONDecodeError) as exc:
        print(f"Mail operation failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
