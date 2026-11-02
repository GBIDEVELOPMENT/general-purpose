# Star Trek duplicate pruning, updated owner policy (2026-11-02)

**Legacy Trek may retain as many alternate copies of an episode as desired.** Preserve existing originals and alternate editions of The Original Series, The Animated Series, The Next Generation, Deep Space Nine, Voyager and Enterprise. Do not delete legacy Trek duplicates merely because episode identifiers match.

**NuTrek should have exactly one version per episode**, including Discovery, Picard, Lower Decks, Prodigy, Strange New Worlds and Starfleet Academy, plus any future modern-era Trek series. For same-episode duplicates, keep the *smallest file of the highest actual video resolution*. This replaces the old HDR/Dolby Vision priority ordering. HDR and Dolby Vision metadata remain useful for compatibility notes but are not stronger than resolution and size under this instruction.

**All non-Trek TV shows** also have exactly one copy per episode, except **Studio 60 on the Sunset Strip**, where the multiple video editions are explicitly preserved. The small-file/highest-resolution rule applies to those shows too. Distinguish video duplicates from alternative episode formats, DVD discs, extras, commentaries and multi-episode or cross-season files. Filename quality claims are candidates for checks, not proof; where resolution is ambiguous, retain copies for review.

The one-off 2026-11-02 deletion review `media-organizer/review/ftp-tv-dedupe-2026-11-02.json` lists 80 owner-approved clear-cut duplicate episodes, 119,912,139,016 bytes in unwanted files, and exact retained counterparts. Its deletion executor must verify each retained copy before deleting its loser, and must never delete unrelated files. The review does not itself authorize arbitrary future deletion manifests.

---

## Previous implementation notes (superseded where policy differs)

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
