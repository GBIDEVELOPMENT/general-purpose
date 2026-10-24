# Reviewed FTP folder batches

The FTP folder mover is a separate, restrictive pipeline to execute exact
owner-reviewed media paths once the live `/downloads` catalogue and an offline
rename/organization plan have been inspected.

Its workflow is `.github/workflows/ftp-media-reviewed-apply.yml`. A PR that
adds `media-organizer/approved-batch.json` runs only offline tests and plan
validation. After a successful merge to trusted `main`, that exact file's
addition/change triggers the privileged FTP job. No FTP secret is available
to the PR event.

Example **schema only**, NOT a real approved path or executable batch:

```json
{
  "root": "/downloads",
  "batch_id": "media_0001",
  "description": "Exact series paths manually checked against the latest inventory",
  "moves": [
    {
      "from": "/downloads/Example.Show.S1E2.mkv",
      "to": "/downloads/Example Show/Season 01/Example Show - S01E02.mkv",
      "size": 12345678,
      "modify": null,
      "reason": "Confirmed show identity, episode number and destination"
    }
  ]
}
```

No sample manifest is committed as `approved-batch.json`. The mover refuses
missing sizes, more than 80 moves, path traversal, differing extensions,
duplicate sources/destinations, loss of a recognized episode token, sources
that changed size or MLSD modification timestamp, case-colliding targets,
and occupied destinations. It creates only required new target directories
and moves files using FTP rename, without downloading their content. Source
preflight occurs before *any* changes, plus a fresh source/destination check
before every individual rename. Interrupted batches can partially complete;
the artifact's `completed.json` is the authoritative journal. There is no
automatic rollback or deletion.

An unprotected GitHub environment does not supply a reviewer gate by itself.
For additional assurance, protect the `ftp-media-changes` environment in
GitHub Settings with required reviewers. If that environment is not protected,
the merge of a valid batch to `main` is the authorization event.

Only use this for high-confidence owner media with verified identity and
nonconflicting paths. Human-readable evidence and the source inventory should
be cited in the PR body. Avoid running multiple batches simultaneously.
