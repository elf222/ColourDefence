# texture_settings.py

import settings as S

texture_folder = "assets/images/"

game = {
    "mask_shield": {
        "H"      : 64,
        "W"      : 64,
        "radius" : 25,
        "ofsetX" : 0,
        "ofsetY" : 0,
        "alpha"  : 150,
    },
    "mask_hat_propeller": {
        "H"      : 64,
        "W"      : 64,
        "radius" : 25,
        "ofsetX" : 0,
        "ofsetY" : 15,
        "alpha"  : 255,
    },
    "screen_death": {
        "H"      : S.SCREEN_H,
        "W"      : S.SCREEN_W,
        "radius" : S.SCREEN_W//2,
        "ofsetX" : 0,
        "ofsetY" : 0,
        "alpha"  : 255,
    },
}