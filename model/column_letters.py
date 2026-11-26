"""HANUKKAH in face-column letters (user, after the full-size Magen David test cut: even the block
letters had small cuts and notches that were hard to paint).

Each letter is a few columns, and each column is exactly one tooth face of the painting picture.
A column is either blue for its full height or carries one or two blue bands. Every band edge is ONE
straight line from one side of the face to the other: no corner, notch or curve ever sits inside a
face (user: breaking a line on a face is the hard part). Bands are flat, except N's diagonal and K's arms, whose
edges slope but still run straight across each face and carry on into the next face.

A band is (bottom, top) at the face's left edge and (bottom, top) at its right edge, as fractions of
the cap height (0 = the letter's foot, 1 = its top).
"""

from __future__ import annotations

import config as cfg

Band = tuple[float, float, float, float]  # bottom-left, top-left, bottom-right, top-right
Column = tuple[Band, ...]


def flat(bottom: float, top: float) -> Band:
    return (bottom, top, bottom, top)


def diagonal(columns: int, thickness: float) -> tuple[Column, ...]:
    """A stroke from the top-left to the bottom-right over `columns` faces, `thickness` tall (measured
    vertically). Its edges are two straight parallel lines that never touch the cap's top or bottom
    inside a face, so each face holds one parallelogram with no corner inside it."""
    drop = (1.0 - thickness) / columns  # how far the top edge falls per face
    return tuple(
        ((1.0 - thickness - drop * k, 1.0 - drop * k, 1.0 - thickness - drop * (k + 1), 1.0 - drop * (k + 1)),)
        for k in range(columns)
    )


def k_arms(joint: float) -> tuple[Column, ...]:
    """K's two arms over two faces. Face 1 holds one piece, `joint` tall at the stem, whose top edge
    rises and bottom edge falls straight across the face. On face 2 each arm is its own band carrying
    those edges on to the cap's top and bottom. The arms part exactly on the ridge between the faces
    (a hair's gap, ARM_PART), so the white notch between them starts on the ridge, never inside a face."""
    top_at = lambda x: 0.5 + joint / 2 + (0.5 - joint / 2) * x / 2  # noqa: E731  (x in faces from the stem)
    thickness = top_at(1.0) - 0.5 - ARM_PART  # each arm's height, so the arms just meet at the ridge
    face_one = ((1.0 - top_at(0.0), top_at(0.0), 1.0 - top_at(1.0), top_at(1.0)),)
    upper = (top_at(1.0) - thickness, top_at(1.0), top_at(2.0) - thickness, top_at(2.0))
    lower = (1.0 - top_at(1.0), 1.0 - top_at(1.0) + thickness, 1.0 - top_at(2.0), 1.0 - top_at(2.0) + thickness)
    return face_one, (upper, lower)


ARM_PART = 0.005  # cap fraction (~0.15 mm) between K's arms where they part on the ridge
_BAND = cfg.COLUMN_BAND_RATIO
FULL = (flat(0.0, 1.0),)
TOP = flat(1.0 - _BAND, 1.0)
MIDDLE = flat(0.5 - _BAND / 2, 0.5 + _BAND / 2)
BOTTOM = flat(0.0, _BAND)
A_TOP = flat(0.75, 1.0)  # A: a thinner top and a low crossbar, so its opening is a clear 0.2 of the cap (~6 mm)
A_BAR = flat(0.30, 0.55)
N_DIAGONAL = diagonal(2, cfg.COLUMN_DIAGONAL_RATIO)
K_ARMS = k_arms(cfg.COLUMN_K_JOINT_RATIO)

LETTERS: dict[str, tuple[Column, ...]] = {
    "H": (FULL, (MIDDLE,), FULL),
    "A": (FULL, (A_TOP, A_BAR), FULL),
    "N": (FULL, *N_DIAGONAL, FULL),
    "U": (FULL, (BOTTOM,), FULL),
    "K": (FULL, *K_ARMS),
}


def word_columns(text: str) -> tuple[Column, ...]:
    """The word left to right as columns, COLUMN_LETTER_GAP empty columns between letters."""
    unknown = sorted({c for c in text if c not in LETTERS})
    if unknown:
        raise ValueError(f"Column letters exist only for {sorted(LETTERS)}; missing {unknown} in {text!r}")
    gap: tuple[Column, ...] = ((),) * cfg.COLUMN_LETTER_GAP
    columns: tuple[Column, ...] = ()
    for index, character in enumerate(text):
        columns = columns + (gap if index else ()) + LETTERS[character]
    return columns


def check_bands() -> list[str]:
    """Problems: any band outside the cap height."""
    problems = []
    for name, columns in LETTERS.items():
        for column in columns:
            for bottom_left, top_left, bottom_right, top_right in column:
                if not (0.0 <= bottom_left < top_left <= 1.0 and 0.0 <= bottom_right < top_right <= 1.0):
                    problems.append(f"{name}: band {bottom_left}-{top_left} / {bottom_right}-{top_right} outside the cap height")
    return problems
