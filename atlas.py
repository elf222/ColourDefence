# atlas_min.py
import pygame as pg

def load_game_atlas(name, cfg, folder):
    """
    Load folder + name + ".png" and cut into tiles of size (cfg["W"], cfg["H"]).

    Returns:
        {"frames": [Surface, ...], "length": int}
    """
    atlas = pg.image.load(folder + name + ".png").convert_alpha()  # display must be set first

    fw, fh = cfg["W"], cfg["H"]
    aw, ah = atlas.get_size()

    frames = []
    for y in range(0, ah, fh):
        for x in range(0, aw, fw):
            frame = pg.Surface((fw, fh), pg.SRCALPHA)
            frame.blit(atlas, (0, 0), pg.Rect(x, y, fw, fh))
            frames.append(frame)

    return {"frames": frames, "length": len(frames)}

def get_frame(frames, idx):
    idx %= len(frames)
    return frames[idx]

def get_frame_with_alpha(frames, idx, alpha=255) -> pg.Surface:
    """
    Get frames[idx] (wrapped), copy it, apply uniform alpha, return it.
    """
    s = get_frame(frames, idx).copy()
    s.set_alpha(alpha)
    return s
