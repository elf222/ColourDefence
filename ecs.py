# ecs.py
# Minimal ECS registry: entity ids are ints; components are dicts; tags are sets.

def make_registry():
    return {
        "next_entity": 1,
        
        "component": { # e-> data
            "position":        {}, # e -> pygame.Vector2,
            "velocity":        {}, # e -> pygame.Vector2
            
            "attached_to":     {}, # e -> id of the object it is attached to
            "offset":          {},
            "attached_are":    {},
            
            "shape":           {},
            "size":            {},
            "colour":          {},
            
            "texture_name":    {},
            "current_texture": {}, # e -> number in atlas; not in use
            
            "mask_type":       {},
            "phase":           {},
            "phase_end":       {},
        },
        
        "tag": { # sets of entities
            "player": set(),
            "bullet": set(),
            "trail":  set(),
            "mask":   set(),
        },
    }

def create_entity(reg):
    e = reg["next_entity"]
    reg["next_entity"] += 1
    return e

# to-do: move of entities to the freed-up space

def destroy_entity(reg, e):
    for component in reg["component"]:
        reg["component"][component].pop(e, None)
        
    for tag in reg["tag"]:
        reg["tag"][tag].discard(e)
