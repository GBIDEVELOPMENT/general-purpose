# Rubik's Cube Loader

Dependency-free **SVG + vanilla JavaScript** isometric Rubik's Cube loading indicator, inspired by 32-bit-era pixel art. No raster frames or GPU-heavy 3D engine.

## Files
- `index.html`: interactive demo with **15-second deterministic solve** and **perpetual shuffle** modes.
- `small-cube.html`: separate one-third-world-size rendition with matching solve and shuffle modes.
- `PALETTES.md`: preserved original vivid palette and adopted muted palette based on the 6 November reference.
- `README.md`: integration and design notes.

Open `index.html` or `small-cube.html` directly in a browser. **Endless scramble-and-solve** is now the default mode; the original timed solve and legacy shuffle remain selectable.

## API

```js
rubiksLoader.start({ mode: 'cycle', seed: 12345, turnMs: 840, scrambleLength: 24 });
// The earlier timed one-shot solve is still supported:
rubiksLoader.start({ mode: 'solve', durationMs: 15000 });
// or feed a chosen legal scramble, to be reversed as a known solve:
rubiksLoader.start({ mode: 'solve', durationMs: 15000, moves: [
  [0,1,1], [2,1,-1], [1,-1,1], [0,-1,-1]
] });
rubiksLoader.complete();
rubiksLoader.pause();
rubiksLoader.resume();
rubiksLoader.destroy();
```

Each move is `[axis,layer,direction]` where axis is 0=x,1=y,2=z, layer is -1/0/1, and direction is ±1 quarter turn. At startup, the given scramble is applied instantly to the solved mathematical cube, then a mathematically equivalent solve sequence is animated. In endless cycle mode, a commuting-layer bridge avoids immediately reversing the previous turn. The final arrangement is **guaranteed to solve**.

To show an almost-solved cube around 13–14 seconds, the default 18-move routine allocates about **0.83 seconds per turn** over 15 seconds. Only the final couple of moves remain after 13 seconds, subject to time spent paused or hidden. At the end of the planned animation, the cube **holds one legal turn short of solved** until the host calls `complete()`. The remaining moves are animated, never snapped. The component freezes elapsed progress when offscreen, the tab is hidden, or the user pauses; elapsed time is therefore **visible active-animation time**, not wall-clock time.

**Important for real asynchronous operations:** 15 seconds is a prediction, not a progress measurement. The cube holds one turn short of solved until the application calls `complete()` when the real task finishes. If that happens earlier, all remaining legal turns run faster over roughly 900 ms; if later, the cube patiently holds. For reduced-motion users, `complete()` immediately shows the mathematically solved cube. Never represent the animated percentage as verified task completion.

The original prototype used 30 FPS SVG redraws and screen-space normalized tile highlights. This version preserves both: no path-dependent highlight resets when a rotating move is committed.

## Accessibility and performance
- 30 FPS maximum, with no timer-based forced renders.
- Stops scheduling frames offscreen, in background tabs, or when paused.
- Honors `prefers-reduced-motion` (static cube until a user intentionally resumes after changing that preference).
- `role="status"` text labels and keyboard-operable demo controls.
- Standalone demo; production use should extract the SVG and script into a reusable component with unique DOM IDs.

## Artwork provenance
The user-supplied reference is a glossy red/blue/yellow isometric Rubik's Cube illustration with beveled pixel-art tiles, black seams and a floor shadow. The renderer recreates that visual language procedurally. The original PNG is held in the ChatGPT conversation and is **not** embedded in this HTML or repository asset.

## Current limitations
- The default solve is the **inverse of its known scramble**, not a general-purpose solver for arbitrary facelet patterns.
- A deadline is a visual estimate; the final turn is deliberately gated on `complete()`. This is not a measured task-progress percentage.
- The demo depends on one particular SVG/DOM structure; refactor to a factory for multiple simultaneous instances.

## Integration example

```js
rubiksLoader.start({mode:'solve',durationMs:15000});
try {
  await runTheRealTask();
  rubiksLoader.complete();
} catch (error) {
  rubiksLoader.pause(); // replace loader with your error UI
  throw error;
}
```

The built-in demo's **Complete** button simulates the host completion signal. Without it, the timed demonstration intentionally stops near solved.

## Continuous scramble-and-solve mode (default)

`mode:'cycle'` starts from a legal scramble and animates a legal, equivalent solution without immediately reversing the last scramble move. As soon as the last quarter-turn completes, it generates a new seeded scramble and **animates that scramble move by move**, then solves it with a genuine non-backtracking path. It repeats indefinitely. No sticker colours or cubie coordinates are reset at cycle boundaries, and there is no idle gap or raster interpolation.

- `seed`: unsigned 32-bit PRNG seed. Same seed and move count produce a reproducible sequence of scrambles.
- `scrambleLength`: compatibility parameter; the current algebraic cycle uses 24 quarter-turns for each scramble.
- `turnMs`: 100 ms or greater (default 840). Duration of each quarter-turn, constant through solve and scramble phases.
- `palette`: `muted` (default) or `original`.

In cycle mode, `complete()` pauses the endless animation, rather than claiming a background job is completed. For task-driven progress, use the existing `mode:'solve'` and call `complete()` when your task actually succeeds. When motion reduction is enabled, all modes begin paused.

Current implementation uses a continuous, reproducible **sequence of legal quarter-turns**, not smooth deformation of cubies into non-cubic shapes. That is intentional to preserve Rubik's Cube mechanics and avoid a visible teleport at the transition.

### Example

```js
rubiksLoader.start({ mode: 'cycle', seed: 20261106, scrambleLength: 24, turnMs: 760 });
// Infinite solve → new legal scramble → solve → next scramble…
```

## No redundant commuting turns (November 2026 correction)

The original solve retraced the scramble backwards. A later workaround inserted turns on an unrelated layer to hide the reversal, but those turns were themselves redundant. That workaround has been removed.

The endless-cycle planner now uses an actual closed walk through cube states. For two intersecting outer face turns A and B, the commutator X = A B A⁻¹ B⁻¹ has order six, meaning X⁶ is the identity and X³ is its own inverse. The planner chooses two distinct commutators X and Y:

- Scramble: X³ Y³ (24 legal quarter-turns).
- Solution: Y³ X³ (24 legal quarter-turns).

The pair always returns to solved with no synthetic commuting-turn detours. Candidates are rejected if inverse turns occur separated only by moves on disjoint layers, including at cycle boundaries. Selection remains seeded and reproducible.

The default 24-move scramble is inherent in this particular algebraic construction. The legacy scrambleLength option is accepted but does not alter this cycle's 24-turn scramble length. Timed one-shot mode still accepts user-supplied moves.

Read-only diagnostics: rubiksLoader.inspect() returns immediateReversals, commutingCancellations, turns and solved. The shared Pages workflow runs node --test RubiksCubeLoader/cycle.test.cjs on both sizes before deployment.
