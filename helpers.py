# helpers.py
import math
import random
from functools import lru_cache
from multiprocessing.spawn import import_main_path
from sys import maxsize

import pygame as pg

import settings as S


def clamp(x, a, b):
    return a if x < a else b if x > b else x


def random_vel_norm():
    return pg.Vector2(1, 0).rotate(random.uniform(0, 360))


def circles_overlap(p1, r1, p2, r2):
    d = p1 - p2
    rr = r1 + r2
    return d.x * d.x + d.y * d.y <= rr * rr


def random_edge_position(radius):
    edge = random.choice(["top", "bottom", "left", "right"])

    if edge == "top":
        return pg.Vector2(random.uniform(radius, S.SCREEN_W - radius), radius)
    elif edge == "bottom":
        return pg.Vector2(
            random.uniform(radius, S.SCREEN_W - radius), S.SCREEN_H - radius
        )
    elif edge == "left":
        return pg.Vector2(radius, random.uniform(radius, S.SCREEN_H - radius))
    else:  # right
        return pg.Vector2(
            S.SCREEN_W - radius, random.uniform(radius, S.SCREEN_H - radius)
        )


def aim_at(origin, target):
    direction = pg.Vector2(target) - pg.Vector2(origin)
    if direction.length_squared() == 0:
        return random_vel_norm()
    return direction.normalize()
    
def add_alpha(color, alpha):
    if len(color) == 4:
        return color[:3] + (alpha,)
    return (*color, alpha)


def rand_colour_vivid():
    r = int(100 + 155 * random.random())
    g = int(100 + 155 * random.random())
    b = int(100 + 155 * random.random())
    return (r, g, b)


def make_up_colours(n=10):
    return tuple(rand_colour_vivid() for _ in range(n))


@lru_cache(maxsize=None)
def calculate_bullet_spawn_count(current_bullet_count) -> int:
    """Calculate dynamic bullet spawn count based on current game state"""
    # More bullets in game = fewer new bullets per hit
    spawn_count = S.BASE_BULLET_SPAWN - (current_bullet_count * S.SPAWN_DECAY_FACTOR)
    return max(S.MIN_SPAWN_COUNT, min(S.MAX_SPAWN_COUNT, round(spawn_count)))

def entity_exists(reg, state, component, property):
    for e in reg[component]:
        if reg[component][e] == property:
            return True
            
    return False
