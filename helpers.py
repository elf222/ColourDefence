# helpers.py
import random
import math
import pygame as pg

def clamp(x, a, b):
    return a if x < a else b if x > b else x

def random_vel(min_abs, max_abs):
    # random direction + random speed
    speed = random.uniform(min_abs, max_abs)
    angle = random.uniform(0.0, math.tau)
    return pg.Vector2(math.cos(angle), math.sin(angle)) * speed

def circles_overlap(p1, r1, p2, r2):
    d = p1 - p2
    rr = r1 + r2
    return d.x*d.x + d.y*d.y <= rr*rr
