"""Versioned encrypted envelopes for a GitHub comment mail gateway.

Only the public enrollment bundle and opaque ciphertext should leave the local
agent/privileged runner. Authentication of GitHub actors remains the runner's job.
Requires cryptography >= 43.
"""
import base64
import hashlib
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

VERSION = 1
MAX_ENVELOPE = 48000
CONTEXT = b"chat-scheduler-shaw-mail-v1"
REQUEST_TTL = 900  # stale send requests must never execute


def b64(data):
    return base64.b64encode(data).decode("ascii")


def unb64(value, limit=MAX_ENVELOPE):
    if not isinstance(value, str) or len(value) > limit:
        raise ValueError("Invalid encoded field")
    return base64.b64decode(value, validate=True)


def private_bytes(key):
    return key.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())


def public_bytes(key):
    return key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)


def encryption_key(private, peer_public, direction):
    peer = X25519PublicKey.from_public_bytes(unb64(peer_public, 128))
    secret = private.exchange(peer)
    return HKDF(
        algorithm=hashes.SHA256(), length=32, salt=None,
        info=CONTEXT + b":" + direction.encode("ascii"),
    ).derive(secret)


def encrypt(private, peer_public, direction, payload):
    raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    if len(raw) > 32000:
        raise ValueError("Payload too large")
    nonce = os.urandom(12)
    cipher = ChaCha20Poly1305(encryption_key(private, peer_public, direction))
    return b64(nonce + cipher.encrypt(nonce, raw, CONTEXT + direction.encode("ascii")))


def decrypt(private, peer_public, direction, ciphertext):
    data = unb64(ciphertext)
    if len(data) < 29:
        raise ValueError("Ciphertext truncated")
    cipher = ChaCha20Poly1305(encryption_key(private, peer_public, direction))
    plain = cipher.decrypt(data[:12], data[12:], CONTEXT + direction.encode("ascii"))
    if len(plain) > 32000:
        raise ValueError("Decrypted payload too large")
    return json.loads(plain)


def derive_wrapping_key(password, salt):
    if not isinstance(password, str) or not password:
        raise ValueError("Missing mail password")
    return hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14,
                          r=8, p=1, dklen=32, maxmem=64 * 1024 * 1024)


def enroll(password):
    """Executed only on a trusted Actions runner. Return *public* enrollment."""
    server = X25519PrivateKey.generate()
    salt, nonce = os.urandom(16), os.urandom(12)
    key = derive_wrapping_key(password, salt)
    sealed = ChaCha20Poly1305(key).encrypt(nonce, private_bytes(server), CONTEXT)
    return {
        "version": VERSION,
        "server_public": b64(public_bytes(server)),
        "salt": b64(salt),
        "wrapped_private": b64(nonce + sealed),
    }


def recover_server(password, enrollment):
    if enrollment.get("version") != VERSION:
        raise ValueError("Unsupported enrollment")
    raw = unb64(enrollment["wrapped_private"], 512)
    salt = unb64(enrollment["salt"], 48)
    if len(salt) != 16 or len(raw) != 60:
        raise ValueError("Invalid enrollment data")
    secret = ChaCha20Poly1305(derive_wrapping_key(password, salt)).decrypt(
        raw[:12], raw[12:], CONTEXT
    )
    private = X25519PrivateKey.from_private_bytes(secret)
    if b64(public_bytes(private)) != enrollment["server_public"]:
        raise ValueError("Enrollment public key mismatch")
    return private


def client_request(enrollment, operation, request_id=None, timestamp=None):
    """Run in ChatGPT's isolated execution environment; keep key bytes private."""
    client = X25519PrivateKey.generate()
    payload = {
        "id": request_id or uuid.uuid4().hex,
        "timestamp": int(time.time()) if timestamp is None else int(timestamp),
        "operation": operation,
    }
    envelope = {
        "version": VERSION,
        "kind": "execute",
        "enrollment": enrollment,
        "client_public": b64(public_bytes(client)),
        "ciphertext": encrypt(client, enrollment["server_public"], "request", payload),
    }
    return envelope, private_bytes(client)


def server_request(password, envelope):
    if envelope.get("version") != VERSION or envelope.get("kind") != "execute":
        raise ValueError("Unsupported request envelope")
    server = recover_server(password, envelope["enrollment"])
    request = decrypt(server, envelope["client_public"], "request", envelope["ciphertext"])
    if not isinstance(request, dict) or not isinstance(request.get("operation"), dict):
        raise ValueError("Malformed command")
    request_id = request.get("id")
    ts = request.get("timestamp")
    if not isinstance(request_id, str) or len(request_id) != 32 or not all(c in "0123456789abcdef" for c in request_id):
        raise ValueError("Invalid request identifier")
    if type(ts) is not int or abs(int(time.time()) - ts) > REQUEST_TTL:
        raise ValueError("Stale or future request")
    return server, request


def server_response(server, client_public, request_id, result):
    return {
        "version": VERSION, "kind": "result", "id": request_id,
        "ciphertext": encrypt(server, client_public, "response", result),
    }


def client_response(private_raw, enrollment, reply, expected_id):
    if reply.get("version") != VERSION or reply.get("kind") != "result" or reply.get("id") != expected_id:
        raise ValueError("Unexpected response")
    client = X25519PrivateKey.from_private_bytes(private_raw)
    return decrypt(client, enrollment["server_public"], "response", reply["ciphertext"])
