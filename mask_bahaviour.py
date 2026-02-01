# mask_bahaviour.py

def masked_player_hitbox(reg, state):
    p = state.get("player_eid")
    ppos = reg["transform"][p]
    prad = reg["collider"][p]
    if p is None or p not in reg["transform"] or p not in reg["collider"]:
        return ppos, prad

    ppos = reg["transform"][p]
    prad = reg["collider"][p]
    
    return ppos, prad