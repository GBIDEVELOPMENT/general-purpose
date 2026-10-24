# S01E01 integrated script excerpt v3

The first integrated **01:00–01:30** scene draft is a **source-evidence rendering**, not a reconstructed original production screenplay. This lane concatenates all retained evidence streams without inventing speech, screen action or motivation.

Inputs: original owner SRT `aa9f776...` with nine cues C19–C27 and 11 explicit turn fragments; independently acquired tiny.en 60–90s ASR with 45 exact-token *candidate* timing anchors; five static image observations from ten original frames; six AI-reviewed motion/shot observations supported by 60 ordered frame samples in `scene-review-v2`.

`tools/render_s01e01_integrated_scene_v3.py` verifies that all these evidence sources refer to the same AVI/SRT SHA, emits one ordered, readable script timeline (`scene-review-v3/scene-script-v3.md`), and a fully inspectable machine-readable evidence map (`scene-review-v3/scene-evidence-map.json`). It preserves uncertain speakers as **UNIDENTIFIED VOICE** and flags any subtitle cue starting before or ending after the observed 30-second audiovisual excerpt. Script source lines remain verbatim from immutable captions, including unusual comic vocabulary; acoustic word candidates cannot silently replace them.

QA: deterministic source-count checks, no orphaned visual evidence, zero confidently identified speaker aliases or emotions, exact source hash agreement, no full-episode AV completeness claim. All physical action in v2 is qualified as ordered 4fps sampled-frame observation, not continuous video. This is a **readable research edition** only.

Next: human/audio listener validation of the candidate spoken lines and timing, speaker diarization with anchored characters, a more complete visual-motion interval over an entire scene, verified tonal/inflection phrasing for clear unmixed voices, then independent episode-wide transcript/scene acceptance. Do not scale an unresolved voice or discontinuous motion claim by 193 episodes.
