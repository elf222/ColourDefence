# FPS_track.py
# tracks fps, fully AI genereted

import pygame as pg

class FPSTracker:
    """Drop-in FPS tracker. Call .tick() once per frame, .draw() after rendering."""
    def __init__(self, font_size=18, pos=(8, 6), sample=20):
        self.clock = pg.time.Clock()
        self.font = pg.font.Font(None, font_size)   # uses default pygame font
        self.pos = pos
        self.sample = max(1, int(sample))
        self._hist = []

    def tick(self, target_fps=0):
        """Call at start/end of frame. Returns dt seconds."""
        dt_ms = self.clock.tick(target_fps)         # 0 => uncapped
        fps = self.clock.get_fps()
        self._hist.append(fps)
        if len(self._hist) > self.sample:
            self._hist.pop(0)
        return dt_ms / 1000.0

    def fps(self):
        return sum(self._hist) / len(self._hist) if self._hist else 0.0

    def draw(self, surf, extra_text=""):
        text = f"{self.fps():5.1f} fps"
        if extra_text:
            text += f" | {extra_text}"
        img = self.font.render(text, True, (255, 255, 255))
        # simple readable background
        pad = 4
        r = img.get_rect(topleft=self.pos).inflate(pad * 2, pad * 2)
        pg.draw.rect(surf, (0, 0, 0), r, border_radius=4)
        surf.blit(img, (r.x + pad, r.y + pad))