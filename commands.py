# commands.py
# All entity creation/destruction goes through this command list.
# Systems may enqueue commands; main applies them with process_commands().

import pygame as pg
import settings as S
from ecs import create_entity, destroy_entity

def make_command_buffer():
    return []

def enqueue(cmd_buf, cmd):
    cmd_buf.append(cmd)

# --- command constructors (plain dicts) ---

def cmd_spawn_player(pos, radius=S.PLAYER_RADIUS, store_as="player_eid"):
    return {
        "type": "spawn_player",
        "pos": pg.Vector2(pos),
        "radius": float(radius),
        "store_as": store_as,  # saves entity id into state[store_as]
    }

def cmd_spawn_bullet(pos, vel, radius=S.BULLET_RADIUS):
    return {
        "type": "spawn_bullet",
        "pos": pg.Vector2(pos),
        "vel": pg.Vector2(vel),
        "radius": float(radius),
    }

def cmd_destroy(e):
    return {"type": "destroy", "e": int(e)}

def process_commands(reg, state):
    """Apply and clear pending commands.

    IMPORTANT: This is the only place that creates/destroys entities.
    It should be called AFTER tick_game() so systems can safely enqueue while iterating.
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
            e = create_entity(reg)
            reg["bullet"].add(e)
            reg["transform"][e] = pg.Vector2(c["pos"])
            reg["velocity"][e]  = pg.Vector2(c["vel"])
            reg["collider"][e]  = float(c["radius"])

        elif t == "destroy":
            destroy_entity(reg, c["e"])

        else:
            # unknown command: ignore (or raise if you prefer)
            pass

    cmd_buf.clear()
