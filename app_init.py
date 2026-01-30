# app_init.py
import pygame as pg
import settings as S

def init_app():
    pg.init()
    pg.display.set_caption("pygame ECS: minimal main, commands for spawn/destroy")
    screen = pg.display.set_mode((S.SCREEN_W, S.SCREEN_H))
    clock = pg.time.Clock()
    font = pg.font.Font(None, 24)
    return screen, clock, font

def poll_quit():
    # pygame quirk: always pump events each frame
    for event in pg.event.get():
        if event.type == pg.QUIT:
            return True
    return False

def shutdown_app():
    pg.quit()
