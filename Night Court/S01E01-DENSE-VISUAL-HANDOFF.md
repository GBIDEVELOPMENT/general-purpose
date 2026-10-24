# S01E01 75–90s dense temporal visual review

Status: 4-fps capture implementation with synthetic CI, October 23, 2026. The source FTP collection's exact S01E01 SHA is already verified by real run #40042590948. This new evidence is confined to 75–90 seconds around the observed phone receiver and conversation.

## Intent and source limits

The original visual-pass sampled only once every three seconds. These isolated stills establish pose and props but cannot support reliable physical action or timed entrances. This pipeline adds **60 small frames at nominal 4 Hz over 15 seconds**, with SHA per frame, a compact contact sheet and JSON index. The sampling can still miss gestures between frames; it is not continuous video or independently reviewed motion capture.

File `tools/build_s01e01_dense_visual_review.py` enforces the existing exact AVI hash, uses only the fixed 75–90s interval, refuses output overwrites and never includes video/audio bytes in the artifact. Individual JPEGs are 320px wide. A frame's nominal timestamp is determined by the FFmpeg fps filter index, not an independently decoded original presentation timestamp. Every evidence record is marked **unreviewed** until checked against the images.

The trusted owner-only PR-trigger workflow `.github/workflows/night-court-trusted-dense-s01e01.yml` checks out only the accepted base SHA and reads one immutable AVI from the existing FTP connection; never executes contributor code or copies secrets into the triggering PR. Raw source media remains ephemeral. PR's offline CI tests a synthetic 92-second video and ensures exactly 60 SHA-indexed thumbnails.

## Editorial acceptance questions

Review the frames from first to last, noting: who is **visibly present** at each sampled point, whether the telephone receiver changes position, desk positions, facial movements, cut transitions, and the relationship between visible changes and saved caption cue ranges. Label character identities as uncertain unless established independently; a uniform does not identify a specific speaker. Distinguish observed before/after states from inferred action and from on-screen movement captured between frames. If an action has two consistent sampled states but not the actual transition frame, call it a **change between observed states**, not a fully witnessed gesture.

Combine this visual evidence with the already merged [word/turn candidate review](S01E01-WORD-ALIGNMENT-HANDOFF.md) to produce the first more detailed evidence-linked script, but no speaker certainty, inflection label, or physical stage direction may be silently manufactured. The next explicit review gate is word/voice and real video passage verification, followed by full runtime edition alignment.

This is a **bounded experimental package**, not a 193-episode bulk workflow or complete source recording.
