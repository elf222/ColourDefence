# settings.py
SCREEN_W, SCREEN_H = 900, 520
TARGET_FPS = 120

COLOUR_BACKGROUND = (0, 0, 0)

PLAYER_RADIUS = 14
PLAYER_SPEED  = 260.0
COLOUR_CIRCLE_OUTLINE = (0, 0, 0)

BULLET_START_COUNT = 1
BULLET_SPAWN_AT_HIT = 2
BULLET_MAX_COUNT = 50

BULLET_RADIUS = 6
BULLET_SPEED_MIN = 100.0
BULLET_SPEED_MAX = 400.0

MANA_PER_HIT = 10

COLOUR_VARIETY_MIN = 2
COLOUR_VARIETY_MAX = 16

SHAPE_BULLET = "circle"
SHAPE_PLAYER = "circle"

TRAIL_ALPHA = 10
BASE_BULLET_SPAWN = 2
SPAWN_DECAY_FACTOR = 0.02
MIN_SPAWN_COUNT = 1
MAX_SPAWN_COUNT = 4

MASKS = {
    "1" : {
        "name" : "shield",
        "cost" : 100,
        "active_phase_duration": 1
    },
    "2" : {
        "name" : "2",
        "cost" : 100,
        "active_phase_duration": 15
    },
    "3" : {
        "name" : "3",
        "cost" : 100,
        "active_phase_duration": 15
    },
    "4" : {
        "name" : "4",
        "cost" : 100,
        "active_phase_duration": 15
    },
}