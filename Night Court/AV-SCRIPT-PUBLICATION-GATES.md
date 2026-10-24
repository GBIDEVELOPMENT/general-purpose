## Separate fast editing milestone (2026-10-24)

The independent whole-episode AV-certification gates above continue
unchanged. A **working screenplay** can and should be published to
the project's private editorial research tree before these gates
pass. See [caption-first working-screenplay policy](CAPTION-FIRST-WORKING-SCREENPLAY-POLICY.md).
That new tier uses held original captions as presumptive dialogue and
model comparisons as selective review pointers. It can be marked
`COMPLETE_HELD_DIALOGUE_WORKING_DRAFT_VISUAL_AND_SPEAKER_EDIT_PENDING`
when the full *held source witness* is included, without calling it a
verified screenplay or claiming physical-action coverage. A later
`WORKING_SCREENPLAY_EDITORIALLY_READY` requires actual substantial
scene and speaker editing, and is distinct from `INDEPENDENTLY_AV_CERTIFIED`.
Neither of these editorial statuses changes this stricter existing
archive acceptance ledger, which still stands at 0/193.

# Night Court production-script publication gates

The archive holds source-only reading scripts for **193/193 original-series episodes** and has two ongoing bounded audiovisual pilots, S01E01 and S09E19. None of the 193 episodes is independently verified complete against its source video, including source speech, cast speakers, scenes, sound and physical action.

`tools/audit_production_script_publication.py` cross-checks all 193 entries in `catalog/av-script-reconstruction-queue.json` against the per-episode source reading script SHA and the master scaffold coverage ledger. Its output, `catalog/production-script-publication-gates.json`, is an **explicit publication block** until an independent media-matched reviewer acceptance process is established. Model confidence, caption presence, frame extraction, narrator prose or acoustic F0 measurements cannot self-promote a full production script.

Each episode's report preserves the original dialogue source SHA, reading-script path and seven still-open audiovisual gates: source video edition, entire episode audio alignment, speaker identity, real scene settings/boundaries, physical action/reactions, vocal delivery, and independent whole-episode audiovisual review.

**Current acceptance: 193 prepared sources, zero full-episode production scripts verified.** Neither a 30-second multimodal S01E01 sample nor a S09E19 scene excerpt counts toward independent episode completeness. S09E19's sole retained dialogue text is untimed, and no synthetic timestamps may be fabricated.

To graduate an episode in a future version of the policy, introduce a separate signed or otherwise independently reviewed, immutable episode acceptance manifest. It must link every accepted scene/dialogue/performative claim to exact source media/cue/frame/acoustic evidence, identify the source cut, demonstrate all-runtime coverage, and retain reviewer decisions. This script intentionally has **no automatic release acceptance mode**; changes to promotion policy require explicitly reviewed implementation and tests.

The offline pull-request CI validates one-to-one source/cue hash consistency across every episode and commits the compact publication gate ledger only. It does not download episodes, access FTP credentials or perform another audio/video analysis. Other agent-owned media, speaker and drift workflows are not modified.
