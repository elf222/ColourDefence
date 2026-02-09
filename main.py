import sys
print("PYTHON:", sys.executable)
print("VERSION:", sys.version)
print("PATH0:", sys.path[0])
"""
import asyncio

import pygame as pg

import settings as S
from app_init import init_app, poll_quit, shutdown_app
from commands import process_commands
from game import tick_game
from initalisation import init_game
from render import render
from state_handling import state_key_processing
# import FPS_track

async def main():
    screen, clock, font = init_app()
    reg, state = init_game()
    state["game_state"] = "active"

    # process_commands(reg, state)
    # fps = FPS_track.FPSTracker()

    running = True
    while running:
        state["frame"]+= 1
        
        if poll_quit():
            running = False
            continue

        dt = clock.tick(S.TARGET_FPS) / 1000.0 
        # dt = fps.tick(S.TARGET_FPS)

        state_key_processing(reg, state)
        process_commands(reg, state)
        if state["game_state"] != "pause":
            tick_game(reg, state, dt)
        render(screen, reg, state, font)

        # fps.draw(screen)
        
        pg.display.flip()

        await asyncio.sleep(0)

    shutdown_app()


if __name__ == "__main__":
    asyncio.run(main())
"""