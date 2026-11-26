"""All key frames in film order (frames_a: beats 1-5, frames_b: beats 6-10)."""

from __future__ import annotations

import frames_a

try:
    import frames_b
    _B = frames_b.FRAMES
except ImportError:
    _B = []


def ALL() -> list[dict]:
    return [f() for f in frames_a.FRAMES + _B]
