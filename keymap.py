# keymap.py

import pygame as pg
import settings as S

UP = pg.K_w
DOWN = pg.K_s
LEFT = pg.K_a
RIGHT = pg.K_d

RESTART = pg.K_r
PAUSE = pg.K_ESCAPE
GO = pg.K_g

KEY_TO_MASK = {
        pg.K_1: "1",
        pg.K_2: "2",
    }