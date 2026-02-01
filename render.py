import pygame as pg

import settings as S
from helpers import add_alpha
from atlas import frame_at, frame_with_alpha
import texture_settings

overlay = pg.Surface((S.SCREEN_W, S.SCREEN_W), pg.SRCALPHA)
overlay.fill(add_alpha(S.COLOUR_BACKGROUND, 1))

def outlined_circle(
    surface,
    color,
    pos,
    radius,
    alpha=255,
    outline_color=S.COLOUR_CIRCLE_OUTLINE,
    outline_width=2,
):
    pg.draw.circle(surface, outline_color, pos, radius + outline_width)

    pg.draw.circle(
        surface,
        (*color[:3], alpha),
        pos,
        radius,
)

def render_masks(screen, reg, state):
    frame = state["frame"] * S.ANIMATION_FPS // (S.TARGET_FPS) 
    for mask in reg["mask"]:
        screen.blit(frame_with_alpha(state["game_atlases"][reg["texture_name"][mask]]["frames"].frames, int(frame), texture_settings.game[reg["texture_name"][mask]]["alpha"]),
            (reg["transform"][state["player_eid"]]) - reg["ofset"][mask]) 

def render(screen, reg, state, font):
    screen.fill(S.COLOUR_BACKGROUND)
    screen.blit(state["cumulative_static_surface"], (0, 0))
    # bullets
    if state["game_state"] != "pause":
        for e in reg["bullet"]:
            if e in reg["transform"] and e in reg["collider"]:
                pos = reg["transform"][e]
                rad = int(reg["collider"][e])
                outlined_circle(screen, state["color_pallete"][reg["colour"][e]], (int(pos.x), int(pos.y)), rad)
                if state["game_state"] == "active":
                    pg.draw.circle(state["new_tick_static_surface"],
                        add_alpha(state["color_pallete"][reg["colour"][e]], S.TRAIL_ALPHA),
                        (int(pos.x), int(pos.y)),
                        rad)

    # player
    p = state.get("player_eid")
    if p is not None and p in reg["transform"] and p in reg["collider"] and state["game_state"] == "active":
        pos = reg["transform"][p]
        rad = int(reg["collider"][p])
        outlined_circle(screen, state["color_pallete"][reg["colour"][p]], (int(pos.x), int(pos.y)), rad)
        if reg["velocity"][p]:
            pg.draw.circle(state["new_tick_static_surface"],
                add_alpha(state["color_pallete"][reg["colour"][p]], S.TRAIL_ALPHA*2),
                (int(pos.x), int(pos.y)),
                rad)
    
    render_masks(screen, reg, state)
    

    state["cumulative_static_surface"].blit(state["new_tick_static_surface"], (0, 0))
    if(state["frame"]%15 == 0) and state["game_state"] != "pause":
        state["cumulative_static_surface"].blit(overlay, (0, 0))
    state["new_tick_static_surface"].fill((0, 0, 0, 0))

    txt = font.render(f"Hits: {state['hits']}, Mana: {state['mana']}", True, (0, 255, 0))
    screen.blit(txt, (12, 10))
    
    if state["game_state"] == "death":
        screen.blit(frame_with_alpha(state["game_atlases"]["screen_death"]["frames"].frames, 0, 255), (0, 0))
