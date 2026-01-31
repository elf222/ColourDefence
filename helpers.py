# helpers.py
import random
import math
import pygame as pg
import settings as S

def clamp(x, a, b):
    return a if x < a else b if x > b else x

def random_vel_norm():
    return pg.Vector2(1, 0).rotate(random.uniform(0, 360))

def circles_overlap(p1, r1, p2, r2):
    d = p1 - p2
    rr = r1 + r2
    return d.x*d.x + d.y*d.y <= rr*rr

def random_edge_position(radius):
    edge = random.choice(["top", "bottom", "left", "right"])

    if edge == "top":
        return pg.Vector2(
            random.uniform(radius, S.SCREEN_W - radius),
            radius
        )
    elif edge == "bottom":
        return pg.Vector2(
            random.uniform(radius, S.SCREEN_W - radius),
            S.SCREEN_H - radius
        )
    elif edge == "left":
        return pg.Vector2(
            radius,
            random.uniform(radius, S.SCREEN_H - radius)
        )
    else:  # right
        return pg.Vector2(
            S.SCREEN_W - radius,
            random.uniform(radius, S.SCREEN_H - radius)
        )

def aim_at(origin, target):
    direction = pg.Vector2(target) - pg.Vector2(origin)
    if direction.length_squared() == 0:
        return random_vel_norm()
    return direction.normalize()