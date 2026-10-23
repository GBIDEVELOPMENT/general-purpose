# Collection and refresh operations

Run these programs from the repository root:

1. python 'Night Court/tools/validate.py'
2. python 'Night Court/tools/refresh_episode_metadata.py'
3. python 'Night Court/tools/discover_transcript_urls.py'
4. python 'Night Court/tools/collect_open_wiki.py'
5. python 'Night Court/tools/validate.py'

The workflow .github/workflows/night-court-harvest.yml performs the same bounded serial steps.
Only Night Court data are committed. TVmaze provides factual metadata, Forever Dreaming provides topic links only,
and two explicitly CC BY-SA-licensed Wikipedia articles are backed up with revision permalinks and attribution.
Transcripts, subtitle tracks and unlicensed reviews are never copied by this workflow.
