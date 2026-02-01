# atlas.py
# fully AI generated

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Tuple
import pygame as pg


# =========================
# Grid / cutting utilities
# =========================

@dataclass(frozen=True)
class AtlasGrid:
    """Grid metadata for a uniform atlas."""
    frame_w: int
    frame_h: int
    cols: int
    rows: int
    count: int  # cols * rows


def atlas_grid_from_tile_size(
    atlas_size: Tuple[int, int],
    tile_size: Tuple[int, int],
    *,
    allow_partial: bool = False,
) -> AtlasGrid:
    """
    Compute how many frames fit in an atlas, given a target tile size.

    atlas_size: (atlas_w, atlas_h) in pixels
    tile_size:  (frame_w, frame_h) in pixels

    allow_partial:
      - False (default): atlas must be an exact multiple of tile size.
      - True: frames are computed by floor division (extra pixels are ignored).

    Returns AtlasGrid with cols/rows and total frame count.

    Raises ValueError for invalid sizes / non-divisible atlas (when allow_partial=False).
    """
    aw, ah = atlas_size
    fw, fh = tile_size

    if aw <= 0 or ah <= 0:
        raise ValueError(f"Invalid atlas size: {atlas_size}")
    if fw <= 0 or fh <= 0:
        raise ValueError(f"Invalid tile size: {tile_size}")

    if allow_partial:
        cols = aw // fw
        rows = ah // fh
        if cols <= 0 or rows <= 0:
            raise ValueError(
                f"Tile {tile_size} does not fit into atlas {atlas_size} even once."
            )
        return AtlasGrid(frame_w=fw, frame_h=fh, cols=cols, rows=rows, count=cols * rows)

    # strict: exact multiple
    if aw % fw != 0 or ah % fh != 0:
        raise ValueError(
            f"Atlas size {atlas_size} is not divisible by tile size {tile_size}. "
            f"(aw%fw={aw%fw}, ah%fh={ah%fh})"
        )

    cols = aw // fw
    rows = ah // fh
    return AtlasGrid(frame_w=fw, frame_h=fh, cols=cols, rows=rows, count=cols * rows)


def atlas_rects(
    atlas_size: Tuple[int, int],
    tile_size: Tuple[int, int],
    *,
    margin: Tuple[int, int] = (0, 0),
    spacing: Tuple[int, int] = (0, 0),
    allow_partial: bool = False,
) -> List[pg.Rect]:
    """
    Produce a list of pg.Rect frame regions for a uniform atlas.

    Supports optional margin and spacing (useful if your atlas has padding/gutters).

    margin:  (mx, my) pixels from top-left before first frame
    spacing: (sx, sy) pixels between frames

    In strict mode (allow_partial=False), this validates that frames fit *exactly*.
    In partial mode, it returns all frames that fit by floor division.
    """
    aw, ah = atlas_size
    fw, fh = tile_size
    mx, my = margin
    sx, sy = spacing

    if fw <= 0 or fh <= 0:
        raise ValueError(f"Invalid tile size: {tile_size}")
    if mx < 0 or my < 0 or sx < 0 or sy < 0:
        raise ValueError("margin/spacing must be non-negative")

    usable_w = aw - mx
    usable_h = ah - my
    if usable_w <= 0 or usable_h <= 0:
        raise ValueError(f"Margin {margin} leaves no usable area in atlas {atlas_size}")

    # cols = floor((usable_w + sx) / (fw + sx))
    denom_x = fw + sx
    denom_y = fh + sy
    cols = (usable_w + sx) // denom_x
    rows = (usable_h + sy) // denom_y

    if cols <= 0 or rows <= 0:
        raise ValueError("No frames fit with given tile_size/margin/spacing")

    if not allow_partial:
        expected_w = mx + cols * fw + (cols - 1) * sx
        expected_h = my + rows * fh + (rows - 1) * sy
        if expected_w != aw or expected_h != ah:
            raise ValueError(
                "Atlas does not match strict grid given tile_size/margin/spacing.\n"
                f"atlas={atlas_size}, tile={tile_size}, margin={margin}, spacing={spacing}\n"
                f"Computed grid cols={cols}, rows={rows} => expected={expected_w, expected_h}"
            )

    rects: List[pg.Rect] = []
    for r in range(rows):
        y = my + r * (fh + sy)
        for c in range(cols):
            x = mx + c * (fw + sx)
            rects.append(pg.Rect(x, y, fw, fh))
    return rects


# =========================
# Atlas loading / frames
# =========================

@dataclass(frozen=True)
class AtlasFrames:
    """
    frames: list of frame Surfaces (either subsurfaces or copies)
    frame_size: (w, h)
    """
    frames: List[pg.Surface]
    frame_size: Tuple[int, int]

    def __len__(self) -> int:
        return len(self.frames)

    def __getitem__(self, i: int) -> pg.Surface:
        return self.frames[i]


def load_atlas_frames(
    path: str,
    tile_size: Tuple[int, int],
    *,
    convert_alpha: bool = True,
    margin: Tuple[int, int] = (0, 0),
    spacing: Tuple[int, int] = (0, 0),
    allow_partial: bool = False,
    as_subsurfaces: bool = False,
) -> AtlasFrames:
    """
    Load a PNG atlas and cut it into equally-sized frames.

    NOTE: convert_alpha=True requires you to have already created a display:
        pg.display.set_mode(...)

    as_subsurfaces:
      - False (default): copy each frame into a new Surface (safe, independent)
      - True: return subsurfaces that reference the original atlas surface (faster)

    Returns AtlasFrames.
    """
    atlas = pg.image.load(path)
    if convert_alpha:
        atlas = atlas.convert_alpha()

    rects = atlas_rects(
        atlas.get_size(),
        tile_size,
        margin=margin,
        spacing=spacing,
        allow_partial=allow_partial,
    )

    frames: List[pg.Surface] = []
    for r in rects:
        if as_subsurfaces:
            frames.append(atlas.subsurface(r))
        else:
            # independent copy
            frame = pg.Surface((r.w, r.h), flags=pg.SRCALPHA)
            frame.blit(atlas, (0, 0), r)
            frames.append(frame)

    return AtlasFrames(frames=frames, frame_size=tile_size)


# =========================
# Convenience helpers
# =========================

def pick_animation(frames: Sequence[pg.Surface], start: int, length: int) -> List[pg.Surface]:
    """Return frames[start:start+length] with validation."""
    if length <= 0:
        raise ValueError("length must be > 0")
    end = start + length
    if start < 0 or end > len(frames):
        raise IndexError(f"Animation slice {start}:{end} out of range 0:{len(frames)}")
    return list(frames[start:end])


def frame_at(frames: Sequence[pg.Surface], index: int, *, loop: bool = True) -> pg.Surface:
    """Get a frame by index, optionally looping."""
    if not frames:
        raise ValueError("frames is empty")
    if loop:
        index %= len(frames)
    return frames[index]

def load_game_atlas(name, cfg, folder):
    atlas = load_atlas_frames(
        folder + name + ".png",
        (cfg["W"], cfg["H"]),
    )
    return {
        "frames": atlas,
        "length": len(atlas),
    }

_alpha_cache: dict[tuple[int, int], pg.Surface] = {}
# key = (frame_index, alpha)


def frame_with_alpha(
    frames: Sequence[pg.Surface],
    idx: int,
    alpha: int,
    *,
    loop: bool = True,
) -> pg.Surface:
    """
    Return a frame with uniform alpha applied.
    Frames are cached so alpha is applied only once per (idx, alpha).

    loop=True  -> idx wraps around len(frames)
    loop=False -> IndexError if idx is out of range
    """
    if not frames:
        raise ValueError("frames is empty")

    if loop:
        idx %= len(frames)
    elif idx < 0 or idx >= len(frames):
        raise IndexError(idx)

    key = (idx, alpha)
    surf = _alpha_cache.get(key)

    if surf is None:
        surf = frames[idx].copy()
        surf.set_alpha(alpha)
        _alpha_cache[key] = surf

    return surf
