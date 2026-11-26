"""Registry of every printed part: geometry in print orientation + where it sits when assembled."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from build123d import Location, Part

import config as cfg
import fountain
import hanukkiah
import profiles

PETG = "PETG"


@dataclass(frozen=True)
class PartSpec:
    name: str
    build: Callable[[], Part]
    material: str
    orientation: str
    assembly: Callable[[Part], Part]  # moves the print-orientation part into the assembly


def _at(z: Callable[[], float]) -> Callable[[Part], Part]:
    return lambda part: Location((0, 0, z())) * part


def _stacked(name: str) -> Callable[[Part], Part]:
    return _at(lambda: fountain.stack_heights()[name])


def _spine_assembled(_: Part) -> Part:
    shaft = profiles.d_shape(cfg.SPINE_DIAMETER, fountain.spine_length(), cfg.SPINE_FLAT)
    return Location((0, 0, fountain.spine_bottom_z())) * shaft


def _ring_spec(index: int) -> PartSpec:
    drum = cfg.DRUMS[index]
    if index == cfg.CANDLE_DRUM_INDEX:
        build = hanukkiah.r3_part
    elif index == len(cfg.DRUMS) - 1:
        build = fountain.r5_dome_part
    else:
        build = lambda i=index: fountain.plain_drum(i)  # noqa: E731
    return PartSpec(drum.name, build, PETG, "upright, as exported", _stacked(drum.name))


def all_parts() -> list[PartSpec]:
    specs = []
    if cfg.POOL_ENABLED:
        specs.append(PartSpec("pool", fountain.pool_part, PETG, "upright", _at(lambda: 0.0)))
    specs.append(PartSpec("plinth_stem", fountain.plinth_stem_part, PETG, "upright, pockets down", _stacked("plinth_stem")))
    specs += [_ring_spec(i) for i in range(len(cfg.DRUMS))]
    specs.append(PartSpec("spine", fountain.spine_part, PETG, "lying on its D-flat", _spine_assembled))
    return specs
