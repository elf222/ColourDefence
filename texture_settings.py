# texture_settings.py

import settings as S

texture_folder = "assets/images/"

# ofset is math coordinate standard Up, Right = +
game = {
    "mask_shield": {
        "H"      : 64,
        "W"      : 64,
        "radius" : 25,
        "ofsetX" : 0,
        "ofsetY" : 0,
        "alpha"  : 130,
    },
    "mask_hat_propeller": {
        "H"      : 64,
        "W"      : 64,
        "radius" : 25,
        "ofsetX" : 0,
        "ofsetY" : 15,
        "alpha"  : 255,
    },
    "mask_vortex": {
        "H"      : 64,
        "W"      : 64,
        "radius" : 25,
        "ofsetX" : 0,
        "ofsetY" : 0,
        "alpha"  : 255,
    },
    "mask_medical": {
        "H"      : 64,
        "W"      : 64,
        "radius" : 25,
        "ofsetX" : 0,
        "ofsetY" : -7,
        "alpha"  : 255,
    },
    "mask_sunglasses": {
        "H"      : 64,
        "W"      : 64,
        "radius" : 25,
        "ofsetX" : 0,
        "ofsetY" : 5,
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