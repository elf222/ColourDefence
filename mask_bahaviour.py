# mask_bahaviour.py

def masked_player_hitbox(reg, state):
    p = state.get("player_eid")
    ppos = reg["component"]["position"][p]
    prad = reg["component"]["collider"][p]
    if p is None or p not in reg["component"]["position"] or p not in reg["component"]["collider"]:
        return ppos, prad

    ppos = reg["component"]["position"][p]
    prad = reg["component"]["collider"][p]
    
    return ppos, prad