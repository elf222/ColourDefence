# settings.py
SCREEN_W, SCREEN_H = 900, 520
TARGET_FPS = 120

ANIMATION_FPS = 4

COLOUR_BACKGROUND = (0, 0, 0)

PLAYER_RADIUS = 16
PLAYER_SPEED  = 260.0
COLOUR_CIRCLE_OUTLINE = (0, 0, 0)

BULLET_START_COUNT = 1
BULLET_SPAWN_AT_HIT = 2
BULLET_MAX_COUNT = 50
BULLET_CRITICAL_MASS = 100
BULLET_DEADLY_MASS = 500
BULLET_MAX_MASS = 1000

BULLET_RADIUS = 5
BULLET_SPEED_MIN = 100.0
BULLET_SPEED_MAX = 400.0

MANA_PER_HIT = 10

COLOUR_VARIETY_MIN = 8
COLOUR_VARIETY_MAX = 10

SHAPE_BULLET = "circle"
SHAPE_PLAYER = "circle"

TRAIL_ALPHA_PLAYER = 25
TRAIL_ALPHA_BULLET = 10
FRAMES_PER_DARKENING = 10

BASE_BULLET_SPAWN = 2
SPAWN_DECAY_FACTOR = 0.02
MIN_SPAWN_COUNT = 1
MAX_SPAWN_COUNT = 4

# key : parameters
MASKS = {
    "1" : {
        "name" : "shield",
        "cost" : 10,
        "active_phase_duration": 5
    },
    "2" : {
        "name" : "hat_propeller",
        "cost" : 10,
        "active_phase_duration": 5
    },
    "3" : {
        "name" : "vortex",
        "cost" : 10,
        "active_phase_duration": 5
    },
    "4" : {
        "name" : "medical",
        "cost" : 10,
        "active_phase_duration": 5
    },
    "5" : {
        "name" : "sunglasses",
        "cost" : 10,
        "active_phase_duration": 5
    },
}
