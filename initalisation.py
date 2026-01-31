import random

import pygame as pg

import settings as S
from commands import (
    cmd_spawn_bullet,
    cmd_spawn_player,
    enqueue_n,
    make_command_buffer,
)
from ecs import make_registry
from helpers import make_up_colours


def init_game():
    reg = make_registry()
    colour_pallete_size = random.randint(S.COLOUR_VARIETY_MIN, S.COLOUR_VARIETY_MAX)
    state = {
        "frame": 0,
        
        "hits": 0,
        "commands": make_command_buffer(),  # pending commands applied by main
        "player_eid": None,                 # will be set by spawn_player command

        "pallete_size": colour_pallete_size,
        "color_pallete": make_up_colours(colour_pallete_size),
        
        # surfaces to cull static objects to
        "cumulative_static_surface": pg.Surface((S.SCREEN_W, S.SCREEN_W), pg.SRCALPHA).convert_alpha(),
        "new_tick_static_surface": pg.Surface((S.SCREEN_W, S.SCREEN_W), pg.SRCALPHA).convert_alpha(),
    }

    enqueue_n(state["commands"], cmd_spawn_player)
    enqueue_n(state["commands"], cmd_spawn_bullet, S.BULLET_START_COUNT)

    return reg, state
