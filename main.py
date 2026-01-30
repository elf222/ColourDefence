import asyncio

import pygame as pg

import settings as S
from app_init import init_app, poll_quit, shutdown_app
from commands import process_commands
from game import tick_game
from initalisation import init_game
from render import render

async def main():
    screen, clock, font = init_app()
    reg, state = init_game()

    process_commands(reg, state)

    running = True
    while running:
        if poll_quit():
            running = False
            continue

        dt = clock.tick(S.TARGET_FPS) / 1000.0

        tick_game(reg, state, dt)
        process_commands(reg, state)
        render(screen, reg, state, font)

        pg.display.flip()

        await asyncio.sleep(0)

    shutdown_app()


if __name__ == "__main__":
    asyncio.run(main())
