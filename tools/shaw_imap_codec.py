"""IMAP modified UTF-7 and protocol-quoted argument helpers.

Only use these with authenticated IMAP connections to configured servers.
"""
import base64
import re


def quoted(value: str | bytes) -> bytes:
    """Represent a single IMAP quoted-string argument, safely escaped."""
    if isinstance(value, str):
        value = value.encode("utf-8")
    if not value or any(b in value for b in (0, 10, 13)):
        raise ValueError("Empty or unsafe IMAP argument")
    return b'"' + value.replace(b"\\", b"\\\\").replace(b'"', b'\\"') + b'"'


def encode_mailbox(value: str) -> str:
    """Encode a displayed mailbox name as RFC 3501 modified UTF-7."""
    if not value or any(ord(ch) < 32 or ord(ch) == 127 for ch in value):
        raise ValueError("Invalid IMAP folder name")
    result, run = [], []

    def flush():
        if run:
            encoded = base64.b64encode("".join(run).encode("utf-16-be"))
            result.append("&" + encoded.decode("ascii").rstrip("=").replace("/", ",") + "-")
            run.clear()

    for ch in value:
        if ch == "&":
            flush()
            result.append("&-")
        elif 32 <= ord(ch) < 127:
            flush()
            result.append(ch)
        else:
            run.append(ch)
    flush()
    return "".join(result)


def decode_mailbox(value: str) -> str:
    """Decode RFC 3501 modified UTF-7 mailbox names."""
    def decode(match):
        part = match.group(1)
        if not part:
            return "&"
        data = part.replace(",", "/")
        data += "=" * (-len(data) % 4)
        return base64.b64decode(data).decode("utf-16-be")

    return re.sub(r"&([A-Za-z0-9+,]*)-", decode, value)


def parse_folder_row(row: bytes) -> dict:
    """Return a human-readable folder name from an IMAP LIST result."""
    text = row.decode("ascii", errors="replace")
    match = re.fullmatch(r"\(([^)]*)\)\s+(NIL|\"(?:\\.|[^\"])*\")\s+(.+)", text)
    if not match:
        return {"raw": text}
    flags, separator, mailbox = match.groups()
    if mailbox.startswith('"') and mailbox.endswith('"'):
        mailbox = mailbox[1:-1].replace(r'\"', '"').replace(r"\\", "\\")
    if separator.startswith('"'):
        separator = separator[1:-1]
    return {
        "name": decode_mailbox(mailbox),
        "delimiter": None if separator == "NIL" else separator,
        "flags": flags.split(),
    }


def search_arguments(query: str) -> list:
    """Make a literal IMAP TEXT query, not user-controlled IMAP syntax."""
    if not query or len(query) > 2048:
        raise ValueError("Search query must be 1..2048 characters")
    if query.isascii():
        return ["TEXT", quoted(query)]
    return ["CHARSET", "UTF-8", "TEXT", quoted(query)]
