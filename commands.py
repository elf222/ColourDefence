# commands.py

import random

import pygame as pg

import settings as S
import texture_settings
from ecs import create_entity, destroy_entity
from helpers import aim_at, entity_exists, random_edge_position


def make_command_buffer():
    return []

def enqueue_cmd_with_information(cmd_buf, cmd):
    cmd_buf.append(cmd)

def enqueue_cmd_generic(cmd_buf, factory, n=1): # so far used for spawning in game-independent state
    cmd_buf.extend(factory() for _ in range(n))

# --- command constructors (plain dicts) ---

def cmd_spawn_player():
    return {
        "type": "spawn_player",
    }

def cmd_spawn_bullet():
    return {
        "type": "spawn_bullet",
    }

def cmd_spawn_masks():
    return {
        "type"     : "spawn_mask",
    }


def player_spawning(reg, state):
    e = create_entity(reg)
    reg["player"].add(e)
    reg["transform"][e] = pg.Vector2((S.SCREEN_W * 0.5, S.SCREEN_H * 0.5))
    reg["velocity"][e]  = pg.Vector2(0, 0)
    reg["collider"][e]  = float(S.PLAYER_RADIUS)
    reg["colour"][e]    = random.randint(0, state["pallete_size"]-1)
    reg["shape"][e]     = S.SHAPE_PLAYER

    state["player_eid"] = e

def bullet_spawning(reg, state):
    position = random_edge_position(S.BULLET_RADIUS)
    velocity = aim_at(position, reg["transform"][state["player_eid"]])*random.uniform(S.BULLET_SPEED_MIN, S.BULLET_SPEED_MAX)

    e = create_entity(reg)
    reg["bullet"].add(e)
    reg["transform"][e] = position
    reg["velocity"][e]  = velocity
    reg["collider"][e]  = float(S.BULLET_RADIUS)
    reg["colour"][e]    = random.randint(0, state["pallete_size"]-1)
    reg["shape"][e]     = S.SHAPE_BULLET

"""
def trail_spawning(reg, state, parent_e):
    e = create_entity(reg)
    reg["bullet"].add(e)
    reg["transform"][e] = position
    reg["velocity"][e]  = velocity
    reg["collider"][e]  = float(S.BULLET_RADIUS)
    reg["colour"][e]    = random.randint(0, state["pallete_size"]-1)
    reg["shape"][e]     = S.SHAPE_BULLET
"""

def mask_spawning(reg, state, mask_type):
    e = create_entity(reg)
    reg["mask"].add(e)
    reg["transform"][e] = reg["transform"][state["player_eid"]]
    reg["mask_type"][e] = mask_type
    reg["phase"][e] = "active"
    reg["phase_end"][e] = state["frame"] + int(S.MASKS[mask_type]["active_phase_duration"]*S.TARGET_FPS)
    reg["texture_name"][e] = "mask_" + S.MASKS[mask_type]["name"]
    reg["current_texture"][e] = 0
    reg["offset"][e] =  pg.math.Vector2(
                            texture_settings.game[reg["texture_name"][e]]["offsetX"],
                            texture_settings.game[reg["texture_name"][e]]["offsetY"]) \
                        + pg.math.Vector2(
                            texture_settings.game[reg["texture_name"][e]]["W"],
                            texture_settings.game[reg["texture_name"][e]]["H"]) / 2
def masks_spawning(reg, state):
    for mask in state["mask_engagement"]:
        if state["mask_engagement"][mask] and not entity_exists(reg, state, "mask_type", mask):
            mask_spawning(reg, state, mask)


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
            player_spawning(reg, state)

        elif t == "spawn_bullet":
            bullet_spawning(reg, state)

        elif t == "spawn_mask":
            masks_spawning(reg, state)

        elif t == "destroy":
            destroy_entity(reg, c["e"])

        else:
            # unknown command: ignore (or raise if you prefer)
            pass

    cmd_buf.clear()
