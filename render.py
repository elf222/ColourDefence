import pygame as pg


def render(screen, reg, state, font):
    screen.fill((0, 0, 0))

    # bullets
    for e in reg["bullet"]:
        if e in reg["transform"] and e in reg["collider"]:
            pos = reg["transform"][e]
            rad = int(reg["collider"][e])
            pg.draw.circle(screen, state["color_pallete"][reg["colour"][e]], (int(pos.x), int(pos.y)), rad)

    # player
    p = state.get("player_eid")
    if p is not None and p in reg["transform"] and p in reg["collider"]:
        pos = reg["transform"][p]
        rad = int(reg["collider"][p])
        pg.draw.circle(screen, state["color_pallete"][reg["colour"][p]], (int(pos.x), int(pos.y)), rad)

    txt = font.render(f"Hits: {state['hits']}", True, (0, 255, 0))
    screen.blit(txt, (12, 10))
