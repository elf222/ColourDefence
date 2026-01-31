# commands.py

import random

import pygame as pg

import settings as S
from ecs import create_entity, destroy_entity
from helpers import aim_at, random_edge_position


def make_command_buffer():
    return []

def enqueue(cmd_buf, cmd):
    cmd_buf.append(cmd)

def enqueue_n (cmd_buf, factory, n=1):
    cmd_buf.extend(factory() for _ in range(n))

# --- command constructors (plain dicts) ---

def cmd_spawn_player(pos, store_as="player_eid"):
    return {
        "type": "spawn_player",
        "pos": pg.Vector2(pos),
        "radius": float(S.PLAYER_RADIUS),
        "store_as": store_as,
    }

def cmd_spawn_bullet():
    return {
        "type": "spawn_bullet",
    }


def bullet_spawning(reg, state):
    position = random_edge_position(S.BULLET_RADIUS)
    velocity = aim_at(position, reg["transform"][state["player_eid"]])*random.uniform(S.BULLET_SPEED_MIN, S.BULLET_SPEED_MAX)

    e = create_entity(reg)
    reg["bullet"].add(e)
    reg["transform"][e] = position
    reg["velocity"][e]  = velocity
    reg["collider"][e]  = float(S.BULLET_RADIUS)
    reg["colour"][e]    = random.randint(0, state["pallete_size"]-1)


def cmd_destroy(e):
    return {"type": "destroy", "e": int(e)}

def process_commands(reg, state):
    """
    Apply and clear pending commands.
    """
    cmd_buf = state["commands"]
    if not cmd_buf:
        return

    for c in cmd_buf:
        t = c.get("type")

        if t == "spawn_player":
            e = create_entity(reg)
            reg["player"].add(e)
            reg["transform"][e] = pg.Vector2(c["pos"])
            reg["velocity"][e]  = pg.Vector2(0, 0)
            reg["collider"][e]  = float(c["radius"])

            store_as = c.get("store_as")
            if store_as:
                state[store_as] = e

        elif t == "spawn_bullet":
            bullet_spawning(reg, state)

        elif t == "destroy":
            destroy_entity(reg, c["e"])

        else:
            # unknown command: ignore (or raise if you prefer)
            pass

    cmd_buf.clear()
