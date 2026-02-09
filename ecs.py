# ecs.py
# Minimal ECS registry: entity ids are ints; components are dicts; tags are sets.

def make_registry():
    return {
        "next_entity": 1,
        
        "component": { # e-> data
            "position":        {},   # e -> pygame.Vector2, position
            "velocity":        {},   # e -> pygame.Vector2
            "collider":        {},   # e -> float radius
            "colour":          {},
            "shape":           {},
            "mask_type":       {},
            "phase":           {},
            "phase_end":       {},
            "texture_name":    {},
            "current_texture": {},
            "offset":          {},
        },
        
        "tag": { # sets of entities
            "player": set(),
            "bullet": set(),
            "trail" : set(),
            "mask"  : set(),
        },
    }

def create_entity(reg):
    e = reg["next_entity"]
    reg["next_entity"] += 1
    return e

def destroy_entity(reg, e):
    reg["component"]["position"].pop(e, None)
    reg["component"]["velocity"].pop(e, None)
    reg["component"]["collider"].pop(e, None)
    reg["component"]["colour"].pop(e, None)
    reg["component"]["shape"].pop(e, None)
    reg["component"]["mask_type"].pop(e, None)
    reg["component"]["phase"].pop(e, None)
    reg["component"]["phase_end"].pop(e, None)
    reg["component"]["texture_name"].pop(e, None)
    reg["component"]["current_texture"].pop(e, None)
    reg["component"]["offset"].pop(e, None)

    reg["tag"]["player"].discard(e)
    reg["tag"]["bullet"].discard(e)
    reg["tag"]["trail"].discard(e)
    reg["tag"]["mask"].discard(e)
