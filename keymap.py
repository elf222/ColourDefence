# keymap.py

import pygame as pg
import settings as S

UP = pg.K_w
DOWN = pg.K_s
LEFT = pg.K_a
RIGHT = pg.K_d

RESTART = pg.K_r
PAUSE = pg.K_ESCAPE
EXIT = pg.K_RETURN
GO = pg.K_g

# nth mask to n key
KEY_TO_MASK = {
    getattr(pg, f"K_{i}"): str(i)
    for i in range(1, len(S.MASKS) + 1)
}