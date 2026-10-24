#!/usr/bin/env python3
"""Static safety gate: owner-only PR signal uses event-time trusted base revision."""
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
p=ROOT/".github/workflows/night-court-trusted-s01e01-drift.yml"
text=p.read_text("utf-8")
assert "on:" in text and "pull_request_target:" in text
assert "github.event.pull_request.user.login == 'gamesbyian'" in text
assert "github.event.pull_request.head.repo.full_name == 'gamesbyian/general-purpose'" in text
assert "github.event.pull_request.base.ref == 'main'" in text
assert "github.event.pull_request.head.ref == 'research/night-court-s01e01-sparse-sync-trigger'" in text
assert "ref: ${{ github.sha }}" in text, "checkout must be event-time main base sha"
assert "ref: ${{ github.event.pull_request.base.sha }}" not in text, "stale PR creation base prohibited"
assert "ref: ${{ github.event.pull_request.head.sha }}" not in text, "untrusted head forbidden"
assert "persist-credentials: false" in text
source=(ROOT/"Night Court/tools/s01e01_sparse_asr_drift_study.py").read_text("utf-8")
assert "segment_boundary_clipped" in source
assert "ftp_connect_with_one_retry" in source
print("Trusted sparse sync: event-time base SHA only; owner controls and no PR-head code verified")
