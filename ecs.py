# ecs.py
# Minimal ECS registry: entity ids are ints; components are dicts; tags are sets.

def make_registry():
    return {
        "next_entity": 1,
        
        # When updating this update destroy_entity()
        # components: e -> data
        "transform":       {},   # e -> pygame.Vector2, position
        "velocity":        {},   # e -> pygame.Vector2
        "collider":        {},   # e -> float radius
        "colour":          {},
        "shape":           {},
        "mask_type":       {},
        "phase":           {},
        "phase_end":       {},
        "texture_name":    {},
        "current_texture": {},
        "ofset":           {},

        # tags: sets of entities
        "player": set(),
        "bullet": set(),
        "trail" : set(),
        "mask"  : set(),
    }

def create_entity(reg):
    e = reg["next_entity"]
    reg["next_entity"] += 1
    return e

def destroy_entity(reg, e):
    reg["transform"].pop(e, None)
    reg["velocity"].pop(e, None)
    reg["collider"].pop(e, None)
    reg["colour"].pop(e, None)
    reg["shape"].pop(e, None)
    reg["mask_type"].pop(e, None)
    reg["phase"].pop(e, None)
    reg["phase_end"].pop(e, None)
    reg["texture_name"].pop(e, None)
    reg["current_texture"].pop(e, None)
    reg["ofset"].pop(e, None)

    reg["player"].discard(e)
    reg["bullet"].discard(e)
    reg["trail"].discard(e)
    reg["mask"].discard(e)
