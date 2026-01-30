import random

import pygame as pg

import settings as S
from commands import cmd_spawn_bullet, cmd_spawn_player, enqueue, make_command_buffer
from ecs import make_registry
from helpers import random_vel


def init_game():
    reg = make_registry()
    state = {
        "hits": 0,
        "commands": make_command_buffer(),  # pending commands applied by main
        "player_eid": None,                 # will be set by spawn_player command
    }

    # Enqueue initial entities (spawn only via commands)
    enqueue(state["commands"], cmd_spawn_player((S.SCREEN_W * 0.5, S.SCREEN_H * 0.5)))

    for _ in range(S.BULLET_COUNT):
        x = random.uniform(S.BULLET_RADIUS, S.SCREEN_W - S.BULLET_RADIUS)
        y = random.uniform(S.BULLET_RADIUS, S.SCREEN_H - S.BULLET_RADIUS)
        vel = random_vel(S.BULLET_SPEED_MIN, S.BULLET_SPEED_MAX)
        enqueue(state["commands"], cmd_spawn_bullet((x, y), vel))

    return reg, state
