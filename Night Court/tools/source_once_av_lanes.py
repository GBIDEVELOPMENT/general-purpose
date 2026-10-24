#!/usr/bin/env python3
"""Bounded source-once AV lane scheduler.

Runs independent audio and video research against ONE previously verified,
read-only original AVI. No source acquisition, media persistence, access to
credentials, or editorial decisions occur here. Parallelism is opt-in;
a serial fallback remains the reference control.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
import time
from typing import Callable, Any


@dataclass(frozen=True)
class LaneResult:
    audio: Any
    visual: Any
    mode: str
    elapsed_seconds: float
    audio_lane_seconds: float
    visual_lane_seconds: float
    overlapped_seconds: float


def run_av_lanes(audio_work: Callable[[], Any],
                 visual_work: Callable[[], Any], *,
                 mode: str = "serial", clock=time.monotonic) -> LaneResult:
    """Schedule two *read-only source* work functions, propagate all failures.

    Parallel workers can share an immutable AVI, but must use separate scratch
    paths and must not mutate common model caches. The GIL is not a speedup
    guarantee: FFmpeg/native model runtimes may contend for host CPU or I/O.
    """
    if mode not in ("serial", "parallel"):
        raise ValueError("Invalid execution mode")
    if not callable(audio_work) or not callable(visual_work):
        raise ValueError("Both AV lane jobs must be callable")

    def measured(work):
        t = clock()
        result = work()
        return result, clock() - t

    total_start = clock()
    if mode == "serial":
        audio, audio_s = measured(audio_work)
        visual, visual_s = measured(visual_work)
    else:
        # Both can decode/read the same verified immutable AVI independently,
        # without re-downloading it or sharing mutable scratch output.
        with ThreadPoolExecutor(max_workers=2, thread_name_prefix="night-court-av") as pool:
            audio_future = pool.submit(measured, audio_work)
            visual_future = pool.submit(measured, visual_work)
            try:
                audio, audio_s = audio_future.result()
                visual, visual_s = visual_future.result()
            except BaseException:
                audio_future.cancel()
                visual_future.cancel()
                raise
    elapsed = clock() - total_start
    if not all(isinstance(n, (int, float)) and 0 <= n <= 3600 for n in
               (elapsed, audio_s, visual_s)):
        raise ValueError("Invalid AV worker stage timings")
    # This is *measured overlap* in processor wall time, not CPU-time saved.
    overlap = max(0.0, audio_s + visual_s - elapsed)
    return LaneResult(audio, visual, mode, round(elapsed, 3),
                      round(audio_s, 3), round(visual_s, 3),
                      round(overlap, 3))
