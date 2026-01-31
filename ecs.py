# ecs.py
# Minimal ECS registry: entity ids are ints; components are dicts; tags are sets.

def make_registry():
    return {
        "next_entity": 1,
        
        # When updating this update destroy_entity()
        # components: e -> data
        "transform": {},   # e -> pygame.Vector2, position
        "velocity":  {},   # e -> pygame.Vector2
        "collider":  {},   # e -> float radius
        "colour":    {},
        "shape":     {},

        # tags: sets of entities
        "player": set(),
        "bullet": set(),
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

    reg["player"].discard(e)
    reg["bullet"].discard(e)
