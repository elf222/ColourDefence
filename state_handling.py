# state_handling.py

import pygame as pg

import settings as S
import keymap as K

from initalisation import init_game

def replace_dict_contents(dst: dict, src: dict):
    dst.clear()
    dst.update(src)

def reload_dict(reg: dict, state: dict):
    reg_new, state_new = init_game()
    replace_dict_contents(reg, reg_new)
    replace_dict_contents(state, state_new)

def state_key_processing(reg, state):
    keys = pg.key.get_pressed()
    
    if state["game_state"] == "pause":
        if keys[K.RESTART]:
            reload_dict(reg, state)
            state["game_state"] = "active"
            return
        if keys[K.GO]:
            state["game_state"] = "active"
            return
    
    if state["game_state"] == "active":
        if keys[K.RESTART]:
            reload_dict(reg, state)
            state["game_state"] = "active"
            return
        if keys[K.PAUSE]:
            state["game_state"] = "pause"
            return
        if len(reg["tag"]["bullet"]) > S.BULLET_DEADLY_MASS:
            state["game_state"] = "death"
            return
        
    if state["game_state"] == "death":
        if keys[K.PAUSE]:
            state["game_state"] = "pause"
            return
        if keys[K.RESTART]:
            reload_dict(reg, state)
            state["game_state"] = "active"
            return