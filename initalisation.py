import random

import settings as S
from commands import (
    cmd_spawn_bullet,
    cmd_spawn_player,
    enqueue,
    enqueue_n,
    make_command_buffer,
)
from ecs import make_registry
from helpers import make_up_colours


def init_game():
    reg = make_registry()
    colour_pallete_size = random.randint(S.COLOUR_VARIETY_MIN, S.COLOUR_VARIETY_MAX)
    state = {
        "hits": 0,
        "commands": make_command_buffer(),  # pending commands applied by main
        "player_eid": None,                 # will be set by spawn_player command

        "pallete_size": colour_pallete_size,
        "color_pallete": make_up_colours(colour_pallete_size)
    }

    enqueue(state["commands"], cmd_spawn_player((S.SCREEN_W * 0.5, S.SCREEN_H * 0.5)))
    enqueue_n(state["commands"], cmd_spawn_bullet, S.BULLET_START_COUNT)

    return reg, state
