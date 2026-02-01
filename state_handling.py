# state_handling.py

import pygame as pg

import settings as S
import keymap as K

from initalisation import init_game

def state_key_processing(reg, state):
    keys = pg.key.get_pressed()
    
    
    
    if state["game_state"] == "pause":
        if keys[K.RESTART]:
            reg, state = init_game()
            state["game_state"] = "active"
            return
        if keys[K.GO]:
            reg, state = init_game()
            state["game_state"] = "active"
            return
    
    if state["game_state"] == "active":
        if keys[K.RESTART]:
            reg, state = init_game()
            state["game_state"] = "active"
            return
        if keys[K.PAUSE]:
            state["game_state"] = "pause"
        if len(reg["bullet"]) > S.BULLET_DEADLY_MASS:
            state["game_state"] = "death"
        
    if state["game_state"] == "death":
        for key in keys:
            if key: 
                reg, state = init_game()
                state["game_state"] = "active"
                return
        return