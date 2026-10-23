# Night Court: FTP access via GitHub Actions

This workflow reproduces the **connection pattern** in the separate [gamesbyian/S60 FTP inventory](https://github.com/gamesbyian/S60/blob/main/.github/workflows/ftp-inventory.yml):

- Server: `wood.seedhost.eu` (FTP port 21)
- Username: `ianseeds`
- Authentication secret: `FTP_PASSWORD`, stored in **gamesbyian/general-purpose** (the private repo containing `Night Court/`)
- Initial exploration root: `/downloads`
- Night Court source location: **discovered, not presumed**. S60 itself is under `/downloads/S60`.

**The secret belongs in the general-purpose repository, not in S60 and never in ChatGPT, issues, PRs, logs or source files.** GitHub Actions secrets are scoped to their own repo (unless an administrator explicitly configures and grants an organization secret to both). A working S60 job does not prove that this repo has its own credential.

## One-time owner action

Open [the private general-purpose repository Actions secrets settings](https://github.com/gamesbyian/general-purpose/settings/secrets/actions). Choose **New repository secret** (under *Repository secrets*) with the precise case-sensitive name:

```text
FTP_PASSWORD
```

Value: your existing Seedhost FTP account password. Do **not** put `FTP_HOST`, `FTP_USER`, episode footage or the password into the secret name. The host/user are non-secret workflow configuration copied from S60. GitHub masks secret values in logs; the workflow never writes the credential to the checkout.

Then, under [Actions](https://github.com/gamesbyian/general-purpose/actions), open **Night Court FTP access (S60-compatible)**, select **Run workflow**.

- Choose `operation=inventory`, `inventory_root=/downloads`, `protocol=ftp` for S60-compatible discovery. The job lists only Night Court-named folders and allowed subtitle/archive filenames/sizes; unrelated listings are not printed or copied. GitHub's workflow logs show the inventory. No staged files are committed.
- If the server accepts explicit TLS, choose `protocol=ftps` instead. **S60 currently uses unencrypted FTP** (`ftplib.FTP`), which transmits the login credential in cleartext. This workflow supports the same existing protocol for compatibility, but stronger transport protection is preferable and no FTPS support has been verified yet.
- For one deliberately selected source, choose `operation=stage`, select a branch matching `research/night-court-ftp-*`, and fill `remote_file` with the complete absolute path to a single file found by inventory, for example `/downloads/Night Court/Subtitles/S03E01.eng.srt`. **This example path is illustrative and not a claim about the server layout.** Stage fetches only the named file, never media videos or recursive folders, and commits it to `Night Court/incoming/` with hash/remote-path provenance.

The staged file can then be inspected and processed by the existing dialogue import workflow if it is the original 1984 series and its episode/release identities have been confirmed. ZIP and individually numbered SRT/VTT/TXT files have importer support; the previous fixed two-RAR importer is specific to the already integrated Season 1/2 archives. A new RAR or ambiguous batch requires inspected mapping before import. Do not blindly use the fixed import of S01/S02 on other seasons.

## Limits and confidentiality

- Workflow is **manual** for actual FTP network operations. Ordinary code pushes only test the mock FTP implementation and never read the password or contact the server.
- Inventory is bounded to at most 180 directories within three levels, with 600 entries per directory, and logs only source filename metadata inside Night Court-matching directories.
- Staging is bounded to **one explicit file per dispatch**, **90 MB maximum**, with accepted types .srt, .vtt, .txt, .rar and .zip. The exact FTP source must be nested within a Night Court-named directory under `/downloads`; 2023/reboot-named files are rejected.
- No `STOR`, `DELE`, `RMD` or `RNFR` commands: it never mutates the FTP account. No passwords or source dialogue are printed to logs.
- The current Season 1 and Season 2 owner-supplied RAR archives and their **35 individually imported SRT tracks** already exist under `research/source-archives/` and `seasons/`. There is no need to fetch those two sources again via FTP.
- For a complete extraction, source editions and private research rights must be independently reviewed; a file located on FTP is not automatically a verified original-series caption or an AV-complete transcript.

## Independent offline test

```sh
python "Night Court/tools/test_ftp_research_intake.py"
```

The test uses a synthetic FTP tree, synthetic bytes and a fake account connection. It validates path boundaries, no unrequested transfers, staging deduplication and the missing-credential failure mode. It does not need an FTP account or touch a real server.

**If you have installed the secret and run an inventory, provide the link to the GitHub Actions run.** Agents can then use the discovered directory and source filenames as grounded inputs for a focused research-branch transfer, without needing to know or expose the password.


## Confirmed video root and metadata-only next step (October 23, 2026)

The authenticated inventory workflow [run #40028731871](https://github.com/gamesbyian/general-purpose/actions/runs/40028731871) completed with `FTP_PASSWORD` available and found **`/downloads/Night Court TVRip S1-S9`**. It reported zero eligible SRT, VTT, TXT, ZIP or RAR files in that video-root scan; the inventory reached its 180-directory exploration bound, so this is **not proof that no subtitles exist anywhere on the account**. The owner confirms the named directory is the original nine-season TVRip collection without separate subtitles.

The existing Season 1 and 2 RARs **have already been imported** from the repository into **35 season-mapped source-preserving SRT witnesses**. In `catalog/dialogue-coverage.json`, 35 episodes have locally held subtitles, 158 do not, and no version has independently verified audiovisual completeness. Do not rerun the two-RAR importer or pretend they are still waiting for extraction.

New dedicated **metadata-only** workflow: [Night Court FTP video metadata](https://github.com/gamesbyian/general-purpose/actions/workflows/night-court-ftp-video-metadata.yml). Dispatch with root `/downloads/Night Court TVRip S1-S9` and `protocol=ftp` (or `ftps` if supported). It prints filenames, sizes, season/episode candidates and unmatched names from a bounded collection of Night Court-only directories. **No video bytes are transferred, the FTP account isn't modified, and no media is committed.** This can establish the available video editions and exact episode filename patterns for a future source-owner-approved offline ASR/synchronization workflow. The video-root identity is owner-supplied; an FTP file's filename alone is still not proof of screen identity.

The separate local `tools/extract_local_media.py` already supports selecting embedded text subtitle streams and optional offline ASR for files legitimately accessible on the researcher's machine. GPU/CPU runtime cost, FTP transfer size and provenance checks need to be considered before attempting full nine-season ASR.
