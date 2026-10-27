#!/usr/bin/env python3
"""Cheap, bounded original-film transport check BEFORE CPU model installs.

No episode media, secrets, credentials, control-banner contents, host keys or
private file paths are exported. This diagnostic does not authenticate SFTP
and does not imply original media/audio was inspected. A successful FTP
welcome isn't a guaranteed subsequent transfer.
"""
from __future__ import annotations

import argparse
import json
import os
import socket
import time


def probe_banner(host: str, port: int, *, expected: bytes,
                 tries: int = 3, timeout: float = 7.0, delay: float = 2.0,
                 socket_connection=socket.create_connection, sleep=time.sleep):
    if not host or not isinstance(host, str) or len(host) > 250:
        raise ValueError("Missing or invalid media host")
    if port not in (21, 22) or not 1 <= tries <= 4 or not 1 <= timeout <= 20:
        raise ValueError("Unsafe original media probe bounds")
    failures = []
    for n in range(tries):
        try:
            with socket_connection((host, port), timeout=timeout) as conn:
                conn.settimeout(timeout)
                banner = conn.recv(512)
            # Don't publish banners/IPs; reject SSH impersonating FTP and
            # distinguish early EOF from a valid protocol welcome.
            if banner.startswith(expected):
                return {"protocol": "FTP_CONTROL" if port == 21 else "SSH_BANNER",
                        "port": port, "reachable": True,
                        "attempts": n + 1, "failure_classes": failures,
                        "authenticated": False, "file_available": None}
            failures.append("closed_before_greeting" if not banner else "unexpected_protocol_greeting")
        except (EOFError, OSError, TimeoutError) as exc:
            failures.append(
                "timeout" if isinstance(exc, TimeoutError) or
                isinstance(exc, socket.timeout) else
                "connection_refused" if isinstance(exc, ConnectionRefusedError) else
                "network_or_early_close")
        if n != tries - 1:
            sleep(delay)
    return {"protocol": "FTP_CONTROL" if port == 21 else "SSH_BANNER",
            "port": port, "reachable": False, "attempts": tries,
            "failure_classes": failures,
            "authenticated": False, "file_available": None}


def run(host, tries=3, timeout=7, delay=2, ftp_probe=probe_banner):
    # Don't fail an FTP readiness test based on unconfigured SFTP. The latter
    # is diagnosis only: an SSH banner is NOT verified host-key trust.
    ftp = ftp_probe(host, 21, expected=b"220", tries=tries, timeout=timeout, delay=delay)
    ssh = ftp_probe(host, 22, expected=b"SSH-", tries=1, timeout=timeout, delay=0)
    return {"schema": "night-court-media-transport-preflight/1",
            "ftp_control": ftp, "sftp_ssh_banner_only": ssh,
            "ftp_control_ready_for_authenticated_stage": ftp["reachable"],
            "ssh_host_key_pinned": False,
            "original_media_downloaded": False,
            "original_audio_processed": False,
            "independent_speaker_or_turns_verified": 0,
            "advice": ("FTP banner good; authenticate and checksum-pin source before heavy inference"
                       if ftp["reachable"] else
                       "Original-film FTP unavailable. Avoid installing model dependencies. "
                       "Check seedbox FTP/FTPS access; SFTP requires verified SSH host-key pin.")}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--host", default=os.environ.get("FTP_HOST", "wood.seedhost.eu"))
    p.add_argument("--tries", type=int, default=3)
    p.add_argument("--timeout", type=float, default=7)
    p.add_argument("--delay", type=float, default=2)
    p.add_argument("--output", help="Optional safe metadata-only diagnostic JSON file")
    args = p.parse_args()
    result = run(args.host, args.tries, args.timeout, args.delay)
    if args.output:
        from pathlib import Path
        target = Path(args.output)
        if target.exists():
            p.error("Refuse to overwrite a prior source availability report")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", "utf-8")
    print(json.dumps(result, sort_keys=True))
    if not result["ftp_control_ready_for_authenticated_stage"]:
        p.exit(3, "Original-film media transport failed before model setup; no source AV work accepted\n")


if __name__ == "__main__":
    main()
