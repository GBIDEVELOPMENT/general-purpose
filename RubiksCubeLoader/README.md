# Rubik's Cube Loader

Dependency-free **SVG + vanilla JavaScript** isometric Rubik's Cube loading indicator, inspired by 32-bit-era pixel art. No raster frames or GPU-heavy 3D engine.

## Files
- `index.html`: interactive demo with **15-second deterministic solve** and **perpetual shuffle** modes.
- `README.md`: integration and design notes.

Open `index.html` directly in a browser.

## API

```js
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

Each move is `[axis,layer,direction]` where axis is 0=x,1=y,2=z, layer is -1/0/1, and direction is ±1 quarter turn. At startup, the given scramble is applied instantly to the solved mathematical cube, then its exact inverse is animated. The final arrangement is **guaranteed to solve**.

To show an almost-solved cube around 13–14 seconds, the default 18-move routine allocates about **0.83 seconds per turn** over 15 seconds. Only the final couple of moves remain after 13 seconds, subject to time spent paused or hidden. The component freezes elapsed progress when offscreen, the tab is hidden, or the user pauses; elapsed time is therefore **visible active-animation time**, not wall-clock time.

**Important for real asynchronous operations:** 15 seconds is only a prediction. The application should call `complete()` when the actual task finishes. If the operation overruns its prediction, this implementation holds the solved cube rather than claiming work is finished only if the animation itself is explicitly completed; for production, a preferable policy is to slow/hold the last 1–2 moves until the real task completes, then animate the final turns. This is a future enhancement. Never represent animation percentage as verified task completion.

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
- Timed solve currently reaches solved at 15s even when an external operation has not completed. To bind honest completion to a real operation, hold the final turns behind a completion signal.
- The demo depends on one particular SVG/DOM structure; refactor to a factory for multiple simultaneous instances.
