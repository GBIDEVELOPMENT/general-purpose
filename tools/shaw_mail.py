#!/usr/bin/env python3
"""Minimal Shaw IMAP/SMTP client. Never persist credentials or mailbox content."""
import argparse
import email
from email.header import decode_header, make_header
from email.message import EmailMessage
from email.utils import parseaddr
import imaplib
import json
import os
import smtplib
import ssl
import sys
from pathlib import Path
from shaw_imap_codec import encode_mailbox, parse_folder_row, quoted, search_arguments

IMAP_HOST = "imap.shaw.ca"
SMTP_HOST = "mail.shaw.ca"
DEFAULT_LIMIT = 20
MAX_LIMIT = 100
DEFAULT_ACCOUNT = "ian.wallace@shaw.ca"


def imap_tls_context():
    """Shaw offers strong ECDHE, but otherwise selects weak finite-field DHE.

    Retain system certificate verification and hostname validation, require
    TLS >= 1.2, and refuse unsafe finite-field DHE and anonymous ciphers.
    """
    context = ssl.create_default_context()
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.set_ciphers("ECDHE:!DHE:!aNULL:!eNULL")
    return context


def credentials():
    address = os.environ.get("SHAW_EMAIL", DEFAULT_ACCOUNT).strip()
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
                           "text": payload.decode(charset, errors="replace")})
        item["body_parts"] = bodies
        item["attachments"] = [
            {"filename": decode(part.get_filename() or ""),
             "content_type": part.get_content_type(),
             "size_bytes": len(part.get_payload(decode=True) or b"")}
            for part in msg.walk()
            if part.get_content_disposition() == "attachment"
        ]
    return item



def auth_diagnostics():
    """Authenticate to IMAP and SMTP without reading or sending any messages.

    No server exception strings, usernames, or credentials enter the result.
    """
    _, user, password = credentials()
    outcomes = {}
    try:
        with imaplib.IMAP4_SSL(IMAP_HOST, 993, ssl_context=imap_tls_context(), timeout=20) as connection:
            connection.login(user, password)
        outcomes["imap"] = "authentication_accepted"
    except imaplib.IMAP4.error:
        outcomes["imap"] = "authentication_rejected"
    except ssl.SSLError:
        outcomes["imap"] = "tls_error"
    except OSError:
        outcomes["imap"] = "network_error"

    # Do not use "with SMTP" here: its implicit QUIT can fail *after*
    # authentication succeeded and misreport the result.
    smtp = None
    phase = "connect"
    try:
        smtp = smtplib.SMTP(SMTP_HOST, 587, timeout=20)
        phase = "ehlo"
        smtp.ehlo()
        phase = "starttls"
        smtp.starttls(context=imap_tls_context())
        phase = "ehlo_after_tls"
        smtp.ehlo()
        phase = "authenticate"
        smtp.login(user, password)
        outcomes["smtp"] = "authentication_accepted"
    except smtplib.SMTPAuthenticationError as exc:
        outcomes["smtp"] = "authentication_rejected"
        outcomes["smtp_code"] = int(exc.smtp_code)
    except smtplib.SMTPResponseException as exc:
        outcomes["smtp"] = "smtp_response_error"
        outcomes["smtp_code"] = int(exc.smtp_code)
        outcomes["smtp_phase"] = phase
    except smtplib.SMTPException as exc:
        outcomes["smtp"] = "smtp_protocol_error"
        outcomes["smtp_error_type"] = type(exc).__name__
        outcomes["smtp_phase"] = phase
    except ssl.SSLError:
        outcomes["smtp"] = "tls_error"
        outcomes["smtp_phase"] = phase
    except OSError:
        outcomes["smtp"] = "network_error"
        outcomes["smtp_phase"] = phase
    finally:
        if smtp is not None:
            smtp.close()
    return outcomes


def fetch(args):
    _, user, password = credentials()
    with imaplib.IMAP4_SSL(IMAP_HOST, 993, ssl_context=imap_tls_context(), timeout=30) as conn:
        conn.login(user, password)
        if args.command == "folders":
            status, folders = conn.list()
            if status != "OK":
                raise RuntimeError("Could not enumerate folders")
            print(json.dumps([parse_folder_row(x) for x in (folders or []) if x], indent=2, ensure_ascii=False))
            return
        status, _ = conn.select(quoted(encode_mailbox(args.folder)), readonly=True)
        if status != "OK":
            raise RuntimeError("Could not select requested folder")
        if args.command == "read":
            if not args.uid.isascii() or not args.uid.isdecimal() or int(args.uid) <= 0:
                raise ValueError("UID must be a positive integer")
            uids = [args.uid.encode("ascii")]
        else:
            if args.command == "search":
                criterion = search_arguments(args.query)
            else:
                criterion = ["ALL"]
            status, data = conn.uid("SEARCH", None, *criterion)
            if status != "OK":
                raise RuntimeError("Search failed")
            uids = (data[0] or b"").split()[-args.limit:][::-1]
        items = []
        for uid in uids:
            status, data = conn.uid("FETCH", uid, "(BODY.PEEK[])" if args.command == "read" else "(BODY.PEEK[HEADER.FIELDS (FROM TO SUBJECT DATE MESSAGE-ID)])")
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
    if not isinstance(to, list) or not to:
        raise ValueError("Draft requires a nonempty list of recipient addresses")
    for recipient in to:
        if not isinstance(recipient, str) or any(ch in recipient for ch in "\r\n\t,;<>"):
            raise ValueError("Recipients must be individual plain email addresses")
        display, parsed = parseaddr(recipient)
        if display or parsed != recipient or parsed.count("@") != 1:
            raise ValueError("Invalid recipient email address")
    if not isinstance(subject, str) or not isinstance(body, str):
        raise ValueError("Draft requires string subject and body")
    if "\r" in subject or "\n" in subject:
        raise ValueError("Subject cannot contain line breaks")
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
    smtp = None
    try:
        smtp = smtplib.SMTP(SMTP_HOST, 587, timeout=30)
        smtp.ehlo()
        smtp.starttls(context=imap_tls_context())
        smtp.ehlo()
        smtp.login(user, password)
        # Once DATA is accepted, a failed QUIT must not turn a successful
        # submission into an apparent failure that invites duplicate sends.
        refused = smtp.send_message(msg)
    finally:
        if smtp is not None:
            smtp.close()
    result = {
        "submitted": True,
        "attempted_recipients": len(draft["to"]),
        "accepted_recipients": len(draft["to"]) - len(refused),
        "rejected_recipients": len(refused),
    }
    print(json.dumps(result))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    subs.add_parser("folders", help="List IMAP folders")
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
