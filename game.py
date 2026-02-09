# game.py
# High-level game API: init_game(), tick_game(), render_game()

import pygame as pg

import settings as S
import keymap as K
from commands import (
    cmd_destroy,
    cmd_spawn_bullet,
    cmd_spawn_masks,
    enqueue_cmd_with_information,
    enqueue_cmd_generic,
)
from helpers import calculate_bullet_spawn_count, circles_overlap, clamp
from mask_bahaviour import masked_player_hitbox

# ------------------ tick (input + logic) ------------------


def tick_game(reg, state, dt):
    """Advance game logic by dt seconds.

    This function is allowed to mutate component data (movement, velocity, etc.).
    But it must NOT create/destroy entities directly — it enqueue_cmd_with_informations commands instead.
    """
    _input_player(reg, state)
    _update_movement_and_bounds(reg, dt)
    _update_attached_objects(reg, state, dt)
    _update_collisions(reg, state)
    _input_masks(reg, state)
    _manage_masks(reg, state)


def _input_player(reg, state):
    p = state.get("player_eid")
    if p is None or p not in reg["velocity"]:
        return

    keys = pg.key.get_pressed()
    move = pg.Vector2(0, 0)

    move.x += keys[K.RIGHT] - keys[K.LEFT]
    move.y += keys[K.DOWN] - keys[K.UP]

    if move.length_squared() > 0:
        move = move.normalize()
    if state["game_state"] != "active":
        move = pg.Vector2(0, 0)

    reg["velocity"][p] = move * S.PLAYER_SPEED


def _input_masks(reg, state): # spawn mask only if they do not exist, stacking is allowed
    keys = pg.key.get_pressed()
    nothing_new = True
   
    for key, mask in K.KEY_TO_MASK.items():
        if keys[key] and (not state["mask_engagement"][mask]) and state["mana"] >= S.MASKS[mask]["cost"]:
            state["mask_engagement"][mask] = True
            state["mana"] -= S.MASKS[mask]["cost"]
            nothing_new = False
            
    if nothing_new:
        return

    enqueue_cmd_generic(state["commands"], cmd_spawn_masks)


def _update_movement_and_bounds(reg, dt):
    # integrate entities that have velocity+transform
    for e, vel in list(reg["velocity"].items()):
        if e not in reg["transform"]:
            continue
        pos = reg["transform"][e]
        pos += vel * dt
        reg["transform"][e] = pos

        # player: clamp inside window
        if e in reg["player"] and e in reg["collider"]:
            rad = reg["collider"][e]
            pos.x = clamp(pos.x, rad, S.SCREEN_W - rad)
            pos.y = clamp(pos.y, rad, S.SCREEN_H - rad)
            reg["transform"][e] = pos

        # bullets: bounce off window edges
        if e in reg["bullet"] and e in reg["collider"]:
            rad = reg["collider"][e]

            if pos.x - rad < 0:
                pos.x = rad
                vel.x = -vel.x
            elif pos.x + rad > S.SCREEN_W:
                pos.x = S.SCREEN_W - rad
                vel.x = -vel.x

            if pos.y - rad < 0:
                pos.y = rad
                vel.y = -vel.y
            elif pos.y + rad > S.SCREEN_H:
                pos.y = S.SCREEN_H - rad
                vel.y = -vel.y

            reg["transform"][e] = pos
            reg["velocity"][e] = vel
            

def _update_attached_objects(reg, state, dt):
    for mask in reg["mask"]:
        if state["mask_engagement"][reg["mask_type"][mask]]:
            reg["transform"][mask] = reg["transform"][state["player_eid"]]


def _update_collisions(reg, state):
    p = state.get("player_eid")

    ppos, prad = masked_player_hitbox(reg, state)

    cmd_buf = state["commands"]

    # iterate bullets without mutating sets/dicts; enqueue_cmd_with_information destroy/spawn instead
    if state["game_state"] != "death":
        for b in list(reg["bullet"]):
            if b not in reg["transform"] or b not in reg["collider"]:
                continue
    
            bpos = reg["transform"][b]
            brad = reg["collider"][b]
    
            if circles_overlap(ppos, prad, bpos, brad):
                state["hits"] += 1
    
                reg["colour"][p] = reg["colour"][b]
                # destroy bullet and spawn a new
                enqueue_cmd_with_information(cmd_buf, cmd_destroy(b))
                enqueue_cmd_generic(
                    cmd_buf,
                    cmd_spawn_bullet,
                    calculate_bullet_spawn_count(len(reg["bullet"])),
                )
                state["mana"]+= S.MANA_PER_HIT

def _manage_masks(reg, state):
    cmd_buf = state["commands"]
    
    for mask in reg["mask"]:
        if state["frame"] >= reg["phase_end"][mask]:
            enqueue_cmd_with_information(cmd_buf, cmd_destroy(mask))
            state["mask_engagement"][reg["mask_type"][mask]] = False
            
    
    