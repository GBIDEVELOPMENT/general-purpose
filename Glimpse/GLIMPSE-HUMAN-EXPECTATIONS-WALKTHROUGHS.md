# Glimpse — Human expectations and cognitive walkthroughs

**Date:** 2026-10-22  
**Status:** pre-implementation hypotheses and acceptance protocol; **not a human usability study or a revision of approved paper-reel artwork**.  
**Source:** [ROYGBIV → Glimpse research handoff #29](https://github.com/gamesbyian/general-purpose/issues/29), [merged ROYGBIV PR #446](https://github.com/gamesbyian/wallgen/pull/446), [agent field guide](https://github.com/gamesbyian/wallgen/blob/main/docs/AGENT-HUMAN-EXPECTATIONS-AND-CREATIVE-COMPOSITION.md), [applied IA assessment](https://github.com/gamesbyian/wallgen/blob/main/docs/IA-RESEARCH-APPLIED-ASSESSMENT-2026-10-22.md), and [control atlas](https://github.com/gamesbyian/wallgen/blob/main/docs/HUMAN-CENTRED-NAVIGATION-MAP-2026-10-22.md).

Read with [paper-reel UX contract](GLIMPSE-CONTINUOUS-REEL-DESIGN.md), [motion architecture](GLIMPSE-MOTION-RENDERING-ARCHITECTURE.md), [73 workflow scenarios](70-HUMAN-WORKFLOWS.md), [product specification](PRODUCT-SPECIFICATION.md), and [Rainbow golden path](RAINBOW-QUICKSTART-CONTRACT.md). Keep Glimpse's native Compose/API constraints binding.

## 1. The operating principle

**Design for what a person thinks will happen, then verify what the software actually changes.** UI module boundaries, command names and source-code files are not evidence of human expectation.

Each visible affordance should be described with this tuple:

`{ human_goal, anticipated_result, actual_effect, prerequisites, primary_location, expected_search_terms, adjacent_followup_tasks, feedback, reversibility, failure_mode, frequency_hypothesis, evidence_level }`

The distinction between **preview selection**, **queue placement**, **collection membership**, **current home/lock wallpaper**, and **rotation scheduling** must survive every rename or layout change. These five states may correlate, but they are not interchangeable.

### Evidence classes

1. **Implementation fact:** source code, Android API behavior, explicit state transition, verified rendered screenshot or automated outcome.
2. **Approved design decision:** user's selected paper reel, larger windows, clipping, functional labels and existing product requirements.
3. **Research-supported method:** cognitive walkthroughs, tree testing, information scent, heuristics, accessibility and creativity-support principles, whose results must still be applied and verified in this product.
4. **Agent hypothesis:** expected user's interpretation, suggested navigation, estimated frequency, perceived delight. This is a falsifiable prediction, not an observation.
5. **Human observation:** a real person's action, spoken expectation, confusion, task outcome or aesthetic judgment, recorded with task/device context. **None has been collected in this appendix.**

Do not report synthetic success rates, made-up timings or mock “survey respondents.” For this personal app, short owner sessions and explicit approval have high practical value, without representing population studies.

## 2. Four questions for every consequential step

Following the [NN/g cognitive walkthrough](https://www.nngroup.com/articles/cognitive-walkthroughs/), ask:

1. Will the person try to achieve this effect at this point?
2. Will they notice the available action?
3. Will they associate the action/label with their intended result?
4. After acting, will they see enough honest feedback to know what happened?

Do **not** mark “yes” based only on attractive screenshots or AI assumptions. For each hypothetical failure, annotate its potential severity and test it with an actual running prototype.

## 3. Five high-value Glimpse walkthroughs

### A. “I want to browse another image, not change my current wallpaper.” (W57, W54)

- **Likely expectation:** rotating the paper reel changes the large preview only.
- **Potential ambiguity:** real View-Master-like advancing can suggest advancing the installed wallpaper lineup. “Next” without a qualifier can mean *preview*, *active wallpaper*, or *scheduled successor*.
- **Design:** fixed **Next photo / Previous photo** near browsing reel; a distinct **Set as wallpaper** action; true **12 of 50** count; actual current wallpaper visually distinguished from selection.
- **Feedback:** focus photo and count update; a separate status says the phone wallpaper is unchanged until Apply.
- **Failure/undo:** interrupted gesture settles on a stable real asset ID; use conventional grid and device Back to recover; no silent wallpaper change.
- **Test:** Show screen without explanation and ask “What do you expect to change if you turn this?” Observe, then have person find a picture and return to installed wallpaper. Never teach the terminology before the first attempt.

### B. “My photos are in Google Photos. Put them in Rainbows and change every five minutes.” (W01, W04, W08)

- **Likely expectation:** import selected photos once and they remain available offline; start a named collection rotation directly, not assemble a conditional Rule.
- **Ambiguities:** **Import** versus continuous album **Sync**; “every five minutes” may imply exact wall-clock timing while Android defers background operations; no-repeat shuffle may be perceived as random picks.
- **Design:** Collections → Add photos → Android Photo Picker → verified local import → Use as wallpaper / Start shuffle → choose destination and interval. Display completed/failed/duplicate counts. Show last **applied** and **next eligible**, with limitations readable in-line.
- **Feedback:** imported source count, saved-offline result, active rotation state and schedule details; report when Android delays changes.
- **Test:** Without a walkthrough, ask them to import a selection and configure cadence. Then ask “Will a newly added cloud album photo join automatically?” and “What happens if the phone sleeps?” Record predictions before revealing platform details.

### C. “I just took a screenshot. Save it but don't necessarily make it my wallpaper.” (F071)

- **Likely expectation:** Android screenshot Share → Glimpse quick editor → rotate/crop → choose collection → one of **Use Now**, **Show Next**, **Just Save**. Clipboard Paste is fallback and may be unavailable.
- **Ambiguity:** users may think **Save** replaces their wallpaper; they may think **Use Now** pauses the ongoing automatic rotation indefinitely; edited crop may be confused with source.
- **Design:** Explicit three outcome choices with one-sentence description, last collection remembered and editable, original/edited visual indicator.
- **Feedback:** image safely imported even if WallpaperManager apply fails; separate confirmation for collection membership, queue position and current wallpaper.
- **Test:** Ask them to save a screenshot and keep current wallpaper unchanged; repeat, now make it active until tomorrow. Observe selection and comprehension.

### D. “I want to share this photo with ChatGPT, Lens, email or Drive.” (F072–F073)

- **Likely expectation:** familiar Android Share action on any image, no change to collection/rotation, compatible installed destinations appear, edited versus original choice obvious.
- **Ambiguity:** a full screenshot original may reveal private elements hidden in the cropped wallpaper; “Search with Google Images” may imply a guaranteed upload/API that doesn't exist.
- **Design:** Android Sharesheet and original/crop preview, clear EXIF sanitization choices, capability-aware target labels and graceful fallback. Sharing is never a wallpaper-apply command.
- **Feedback:** local export prepared and handoff invoked; don't pretend the third-party recipient necessarily finished processing.
- **Test:** Ask user to find Share without explaining where it lives, choose the crop, and return with selected image/scroll position intact.

### E. “Rotate a chosen set on weekdays, except when I pin something.” (W12, W18, W60)

- **Likely expectation:** simple preset/Rotation action first; Rules only for exceptions; **Pin until…** temporarily overrides without deleting schedule or corrupting shuffle.
- **Ambiguities:** “Pause” (entire rotation?), “Hold current” (only one destination?), “Next” while held (release hold or preview only?), and battery saver behavior.
- **Design:** Home surface **Pause**, **Change now**, **Why am I seeing this?**; active preset visible; advanced **Automation → Rules** with natural-language summary; future-preview simulation must not actually apply wallpapers.
- **Feedback:** active override and explicit end time; show what resumes afterwards; clear reason if a scheduled event was skipped.
- **Test:** Ask user what will happen tomorrow after pinning, then demonstrate by advancing a simulated clock. Do not infer mental model from final button click alone.

## 4. Specific reel hypotheses to falsify early

| Hypothesis (NOT observed) | Prototype comparison / test | Potential product response |
|---|---|---|
| Five windows communicate five items, not a continuous large collection | Show oversized cropped reel with and without visible “12 of 50”; ask expected size and what happens at edge | Strengthen count, index marker, next window continuity; never fabricate image duplicates |
| Rotation suggests active wallpaper was changed | Unprompted expectation before touching; compare reel vs simple pager | Separate selected preview from real wallpaper status and action labels |
| Reel is delightful but slower for finding item 137 | Timed exploratory tasks on reel and grid with same 50/1000-item fixtures | Keep persistent View all; grid first for search/multiselect |
| Spinning motion communicates one controlled selection | Interrupt settle, reverse direction, skip ahead, slow image decode | Preserve touch-to-angle continuity and stable focus IDs; no ghosts |
| A partially hidden reel communicates “there is more” without hiding controls | Short/tall portrait/landscape device test with 200% text | Clip within a bounded layer, not across bottom nav/Android back region |
| Personalized collection reels aid recognition | Show distinct photo-filled covers without labels, then with labels | Text remains accessible; covers decorative not sole collection identity |
| No-repeat shuffle is understood | Ask “What will happen after all 50 have shown?” | Explain cycle boundaries and no-repeat semantics briefly |

## 5. Navigation comparison to perform, not pre-judge

Compare two *task-complete* shells, while preserving Glimpse's approved visuals:

- **A:** Home / Discover / Collections / Automation, with Reel and Grid inside each collection, quick actions on Home and Image detail.
- **B:** same top-level destinations, but with additional task-led shortcuts for **Add photo**, **Find my wallpaper**, **Change now**, **Edit image**, **Share**, **Set a schedule** surfaced contextually.

This isolates cross-links and information scent before contemplating a disruptive navigation taxonomy rewrite. Do not claim one has a faster human success rate based on a route-graph proxy. Use identical tasks in both and ask first-click expectation, count actual misroutes, identify user corrections and assess feedback clarity.

An optional conceptual distance proxy may count hierarchy edges and top-level destination changes for *specified tasks*. Declare it `STRUCTURAL_ROUTE_PROXY_NOT_HUMAN_TEST` and preserve regressions case by case, as in ROYGBIV's [comparison script](https://github.com/gamesbyian/wallgen/blob/main/scripts/ia-structure-evaluate.mjs).

## 6. Creativity-support considerations for wallpaper curation

Glimpse is not an image-creation tool like ROYGBIV. The transferable art concepts are **looking, selecting, recombining, sequencing, framing, preserving, comparing and sharing**.

- Balance and hierarchy: the selected photograph should dominate the disc, not disappear behind decorative paper. Large window apertures must still show recognizable content at the actual Pixel 6 Pro size.
- Creative rhythm: reel motion expresses ordered succession; “surprise me” requests randomized selection while preserving history. The two should not be conflated.
- Exploration and control: Grid is efficient for targeting; Reel is a tactile, contemplative way to explore. Both manipulate the same persistent selected image, with different affordances.
- Low floor / high ceiling / wide walls: default import-and-shuffle within minutes, expert rules on demand, multiple possible collecting and curating styles.
- Undo/history/source: prevent irrecoverable accidental exclusions, imports and editor variants; let people return to previously delightful images.
- Pleasant motion is not automatically clear motion. Test behavior and consequences, not only perceived charm.

## 7. Lightweight evaluation schedule, scaled for one owner

**Before implementation:** 15-minute paper/prototype walkthrough across tasks A–E, collecting predictions, first-click guesses and unclear labels. Fix semantic confusion before fine-tuning shadows.

**After first working native Reel:** same five tasks on Pixel 6 Pro; record actual transitions, screenshot states and qualitative reactions. At least one interruption, small collection, slow-photo-load and simulated delayed scheduler case.

**Before wider release:** one accessibility pass (TalkBack, 200% text, reduced motion), one physical-device performance pass and deliberate owner aesthetic approval. No broad synthetic test atlas required for every copy edit; detailed screenshot/perf checks when actual interaction or visuals change.

For each task record: screenshot/viewport, scenario ID, anticipated outcome **before** action, first action/location, actual result, confusion, unexpected side effect, severity and disposition. Use video/screen capture only if the owner consents. Separate “tested by agent in emulator,” “tested on physical phone” and “observed human user.”

## 8. Decisions and integration

1. Preserve the approved five-wide-window paper-reel direction and domain vs presentation motion split.
2. Add explicit human-expectation gates to Reel prototype readiness; do not defer them until full app exists.
3. Keep normal controls functional, literal and conventionally placed; poetic text is for context, not errors/actions.
4. Prioritize **preview vs apply**, **collection vs rotation**, **eligible vs actually changed**, and **original vs cropped share** as the four key semantic fault lines.
5. Avoid treating an agent's polished design critique as proof of end-user expectations.
6. Record real observed evidence before changing the approved navigation or claiming success.

Research links:
- [Nielsen Norman Group, cognitive walkthroughs](https://www.nngroup.com/articles/cognitive-walkthroughs/)
- [Nielsen Norman Group, information scent](https://www.nngroup.com/articles/information-scent/)
- [Nielsen Norman Group, tree testing](https://www.nngroup.com/articles/tree-testing/)
- [Nielsen Norman Group, usability heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/)
- [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/)
- [Microsoft Human-AI Experience Toolkit](https://www.microsoft.com/en-us/haxtoolkit/), relevant when AI is actually used for recommendation, not to mislabel Glimpse's deterministic rotation engine
- [Resnick, low floors/high ceilings/wide walls](https://www.media.mit.edu/articles/lifelong-kindergarten-how-to-learn-like-a-kid-by-the-co-creator-of-scratch/)

## New release-acceptance companions (2026-10-22)

Treat [GLIMPSE-SCREEN-CONTRACT.json](GLIMPSE-SCREEN-CONTRACT.json) as a proposed executable semantics inventory and [GLIMPSE-REFERENCE-ACCEPTANCE-PLAN.md](GLIMPSE-REFERENCE-ACCEPTANCE-PLAN.md) as the bounded source-vs-runtime validation procedure. Neither proves the owner has tried the app. First review the [current decisions](GLIMPSE-CURRENT-DECISIONS.md) to avoid applying historical Waltz UI labels to the active Glimpse identity.

## 2026-10-22 two-reel meaning test

Use the [purpose-led reel critique](GLIMPSE-REEL-UX-CRITICAL-AUDIT.md). Before displaying labels or explaining the concept, ask what the smaller reel controls and what the larger one controls; then have the owner change collections, choose a photo, return to applied wallpaper, set Lock only and find a known photo in Grid. Compare the same task with a labeled standard collection picker + one reel and Home/Lock tabs + one reel. Collect actual first-click predictions, wrong state assumptions and intervention needs. **Do not report agent guesses as human success rates**; avoid adding exhaustive synthetic personas.
