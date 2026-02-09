import pygame as pg

import settings as S
from helpers import add_alpha
from atlas import get_frame_with_alpha
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
    animation_phase = (state["frame"] * S.ANIMATION_FPS) // (S.TARGET_FPS)
    for mask in reg["tag"]["mask"]:
        frame = get_frame_with_alpha(state["game_atlases"][reg["component"]["texture_name"][mask]]["frames"],
            animation_phase,
            texture_settings.game[reg["component"]["texture_name"][mask]]["alpha"])
        
        screen.blit(frame, (reg["component"]["position"][state["player_eid"]]) - reg["component"]["offset"][mask])

def render(screen, reg, state, font):
    screen.fill(S.COLOUR_BACKGROUND)
    screen.blit(state["cumulative_static_surface"], (0, 0))
    # bullets
    if state["game_state"] != "pause":
        for e in reg["tag"]["bullet"]:
            if e in reg["component"]["position"] and e in reg["component"]["size"]:
                pos = reg["component"]["position"][e]
                rad = int(reg["component"]["size"][e])
                outlined_circle(screen, state["color_pallete"][reg["component"]["colour"][e]], (int(pos.x), int(pos.y)), rad)
                if state["game_state"] == "active":
                    pg.draw.circle(state["new_tick_static_surface"],
                        add_alpha(state["color_pallete"][reg["component"]["colour"][e]], S.TRAIL_ALPHA_BULLET),
                        (int(pos.x), int(pos.y)),
                        rad)

    # player
    p = state.get("player_eid")
    if p is not None and p in reg["component"]["position"] and p in reg["component"]["size"] and state["game_state"] == "active":
        pos = reg["component"]["position"][p]
        rad = int(reg["component"]["size"][p])
        outlined_circle(screen, state["color_pallete"][reg["component"]["colour"][p]], (int(pos.x), int(pos.y)), rad)
        if reg["component"]["velocity"][p]:
            pg.draw.circle(state["new_tick_static_surface"],
                add_alpha(state["color_pallete"][reg["component"]["colour"][p]], S.TRAIL_ALPHA_PLAYER),
                (int(pos.x), int(pos.y)),
                rad)
    
    render_masks(screen, reg, state)
    

    state["cumulative_static_surface"].blit(state["new_tick_static_surface"], (0, 0))
    if(state["frame"]%S.FRAMES_PER_DARKENING == 0) and state["game_state"] != "pause":
        state["cumulative_static_surface"].blit(overlay, (0, 0))
    state["new_tick_static_surface"].fill((0, 0, 0, 0))
    
    if state["game_state"] == "active":
        txt = font.render(f"Hits: {state['hits']}, Mana: {state['mana']}", True, (0, 255, 0))
        screen.blit(txt, (12, 10))
    
    if state["game_state"] == "death":
        screen.blit(get_frame_with_alpha(state["game_atlases"]["screen_death"]["frames"], 0, 255), (0, 0))
