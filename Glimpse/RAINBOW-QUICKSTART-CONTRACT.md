# Rainbow quickstart: primary user acceptance contract

**The user's request:** "I've got rainbow pictures in Google Photos. I want to add them all to Rainbows and shuffle one every five minutes."

**Happy path (six steps, no Rule Studio):**
1. Collections → New collection → "Rainbows".
2. Add photos → Android Photo Picker, with Google Photos/cloud provider on supported devices. Provider may show albums but is not guaranteed to have "Select whole album" or continuous sync.
3. Show summary of selected, successfully imported, duplicates, failed items, progress and storage. Copy verified images to app-private offline storage, with resumable failure handling.
4. Tap "Use as wallpaper" directly in collection.
5. Pick Home / Lock / Both (capability-gated), Shuffle no repeats, Every 5 minutes.
6. Start; show Last changed, Next eligible, Next, Pause, Change timing, Why.

**Truthful behavior:** snapshot import, not syncing an ongoing Google Photos album. No cloud credentials are stored; no proprietary Waltz cloud exists. Five-minute active-use eligibility does not guarantee wallpaper replacement in Doze. Preserve original photos, never delete them, and don't paint black when a swap fails.

## Device, failure and accessibility acceptance tests

- **A001:** import 60 Google Photos cloud images, choose home-only shuffle every five minutes, verify 60 usable offline.
- **A002:** network disconnect mid-import leaves a clear partial count and recoverable retry.
- **A003:** airplane mode with 60 previously imported images rotates normally.
- **A004:** reimport exact duplicate references/bytes doesn't silently duplicate content.
- **A005:** one eligible image is handled without spurious churn.
- **A006:** OS-delayed background execution is reported as deferred; UI never claims an exact countdown.
- **A007:** process killed during import -> staging cleanup and resume with no corrupt rows.
- **A008:** process killed during apply -> reconcile unknown status, don't double-advance.
- **A009:** revoked original URI access after successful copy -> copy remains eligible.
- **A010:** low storage mid-copy -> graceful partial result, no damage to original.
- **A011:** home-only applies only to home on supported API/device.
- **A012:** destination/interval unsupported -> truthful explanation and safe alternative.
- **A013:** add new images during shuffle -> deterministically merge without unreasonable repeats.
- **A014:** TalkBack, keyboard, Switch Access and very large text can complete the entire flow.
- **A015:** Google Photos unavailable after import -> cached private copies remain functional.

**Quality goal:** ≥9 of 10 uncoached first-time usability testers complete A001 without consulting Rules. Second-time target ≤30 seconds to restart a saved collection, subject to measured usability research.
