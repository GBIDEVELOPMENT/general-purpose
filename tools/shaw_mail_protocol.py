"""Short-lived end-to-end encrypted messages over GitHub comments.

A single Actions job holds the X25519 server key in memory until the session
ends; no private encryption key, password derivative or plaintext mail is
written to GitHub. Requires cryptography >= 43.
"""
import base64
import json
import os
import time
import uuid

from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey, X25519PublicKey,
)
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import (
    Encoding, PrivateFormat, PublicFormat, NoEncryption,
)

VERSION = 2
CONTEXT = b"chat-scheduler-shaw-mail-ephemeral-v2"
REQUEST_TTL = 300
MAX_CIPHER = 48000


def b64(data):
    return base64.b64encode(data).decode("ascii")


def unb64(value, max_chars=MAX_CIPHER):
    if not isinstance(value, str) or len(value) > max_chars:
        raise ValueError("Invalid encoded value")
    return base64.b64decode(value, validate=True)


def private_bytes(key):
    return key.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())


def public_bytes(key):
    return key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)


def derive(private, peer_public, direction):
    peer = X25519PublicKey.from_public_bytes(unb64(peer_public, 128))
    shared = private.exchange(peer)
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=None,
                info=CONTEXT + direction.encode("ascii")).derive(shared)


def seal(private, peer_public, direction, value):
    plaintext = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    if len(plaintext) > 30000:
        raise ValueError("Payload too large")
    nonce = os.urandom(12)
    ciphertext = ChaCha20Poly1305(derive(private, peer_public, direction)).encrypt(
        nonce, plaintext, CONTEXT + direction.encode("ascii")
    )
    return b64(nonce + ciphertext)


def open_seal(private, peer_public, direction, value):
    raw = unb64(value)
    if len(raw) < 29:
        raise ValueError("Truncated ciphertext")
    plaintext = ChaCha20Poly1305(derive(private, peer_public, direction)).decrypt(
        raw[:12], raw[12:], CONTEXT + direction.encode("ascii")
    )
    if len(plaintext) > 30000:
        raise ValueError("Oversized plaintext")
    return json.loads(plaintext)


def server_session():
    """Only the GitHub Actions worker receives the private key."""
    key = X25519PrivateKey.generate()
    session = uuid.uuid4().hex
    return key, {"version": VERSION, "kind": "ready", "session": session,
                 "server_public": b64(public_bytes(key))}


def client_command(ready, operation):
    if ready.get("version") != VERSION or ready.get("kind") != "ready":
        raise ValueError("Unexpected handshake")
    client = X25519PrivateKey.generate()
    request_id = uuid.uuid4().hex
    body = {"id": request_id, "timestamp": int(time.time()), "operation": operation}
    message = {"version": VERSION, "kind": "command", "session": ready["session"],
               "client_public": b64(public_bytes(client)),
               "ciphertext": seal(client, ready["server_public"], "request", body)}
    return message, private_bytes(client), request_id


def server_command(private, message, expected_session):
    if message.get("version") != VERSION or message.get("kind") != "command":
        raise ValueError("Unsupported protocol")
    if message.get("session") != expected_session:
        raise ValueError("Wrong session")
    body = open_seal(private, message["client_public"], "request", message["ciphertext"])
    if not isinstance(body, dict) or not isinstance(body.get("operation"), dict):
        raise ValueError("Malformed operation")
    request_id, timestamp = body.get("id"), body.get("timestamp")
    if not isinstance(request_id, str) or len(request_id) != 32:
        raise ValueError("Malformed request ID")
    if type(timestamp) is not int or abs(int(time.time()) - timestamp) > REQUEST_TTL:
        raise ValueError("Stale command")
    return body


def server_response(private, ready, command, request_id, result):
    return {"version": VERSION, "kind": "result", "session": ready["session"],
            "id": request_id, "ciphertext": seal(private, command["client_public"],
                                                   "response", result)}


def client_response(private_raw, ready, result, expected_id):
    if result.get("version") != VERSION or result.get("kind") != "result":
        raise ValueError("Unexpected result")
    if result.get("session") != ready["session"] or result.get("id") != expected_id:
        raise ValueError("Wrong session or request ID")
    client = X25519PrivateKey.from_private_bytes(private_raw)
    return open_seal(client, ready["server_public"], "response", result["ciphertext"])
