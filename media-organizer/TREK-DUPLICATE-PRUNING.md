# Star Trek duplicate pruning, owner quality policy
The user wants exactly one copy per episode for **Discovery**, **Strange New Worlds**, and **Lower Decks**, retaining 4K with compatible HDR/HDR10 over other releases, using size as a tie-breaker, and prejudiced against DV-only sources.

This pipeline never auto-selects a winner. A reviewed JSON manifest explicitly identifies an exact retained file plus each duplicate slated for removal, all pinned to `MLSD` byte size and timestamp. Its validator enforces identical show-season-episode identity and disallows Enterprise. The trusted FTP job preflights every file, checks the keeper again before **each** removal, refuses changed files or ambiguous names, and retains a per-deletion journal.

Manifest skeleton:
```json
{
  "root": "/downloads",
  "batch_id": "trek_review_001",
  "description": "Explicit quality and compatibility decision for each episode",
  "groups": [{
    "show": "strange_new_worlds",
    "season": "03",
    "episode": "03",
    "retain": {"from": "/downloads/...", "size": 123, "modify": "20261023000000"},
    "delete": [{"from": "/downloads/...", "size": 120, "modify": "20261023000000"}],
    "reason": "Explain 4K HDR10 versus DV-only and size decision for this episode"
  }]
}
```

Use the **latest complete, error-free FTP inventory** and do not trust a truncated older snapshot. Filename tags are merely claims about HDR and DV compatibility. Before marking HDR10 versus DV-only as *verified*, inspect ffprobe stream metadata (HDR10 transfer/primaries and mastering data, DV configuration and HDR10 fallback). When that evidence cannot be obtained, keep uncertain alternatives pending review instead of making destructive assumptions.

PR tests run without FTP secrets. Merging the implementation alone does nothing remotely; only merging a specific `approved-trek-dedupe.json` manifest triggers deletion.
