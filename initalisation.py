import settings as S
from commands import cmd_spawn_bullet, cmd_spawn_player, enqueue, enqueue_n, make_command_buffer
from ecs import make_registry
from helpers import random_vel

def init_game():
    reg = make_registry()
    state = {
        "hits": 0,
        "commands": make_command_buffer(),  # pending commands applied by main
        "player_eid": None,                 # will be set by spawn_player command
    }

    enqueue(state["commands"], cmd_spawn_player((S.SCREEN_W * 0.5, S.SCREEN_H * 0.5)))
    enqueue_n(state["commands"], cmd_spawn_bullet, S.BULLET_START_COUNT)

    return reg, state
