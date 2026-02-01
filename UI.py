import os
import struct
import sys
from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple

import pygame

# Optional GPU shader path (WebGL2 in browser builds)
try:
    import zengl  # type: ignore
except Exception:
    zengl = None

# Platform detection (pygbag/web builds run under Emscripten)
IS_WEB = (sys.platform == "emscripten")

Color = Tuple[int, int, int]

# ----------------------------
# Helpers
# ----------------------------

def load_image(path: str) -> Optional[pygame.Surface]:
    if not path:
        return None
    if not os.path.exists(path):
        return None
    try:
        return pygame.image.load(path).convert_alpha()
    except pygame.error:
        return None

def clip_to_circle(src: pygame.Surface, diameter: int) -> pygame.Surface:
    """Scale + alpha-clip an image to a circle."""
    img = pygame.transform.smoothscale(src, (diameter, diameter)).convert_alpha()
    mask = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
    mask.fill((0, 0, 0, 0))
    pygame.draw.circle(mask, (255, 255, 255, 255), (diameter // 2, diameter // 2), diameter // 2)
    img.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return img

def two_colorize(src: pygame.Surface, fg: Color, bg: Color, threshold: int = 130) -> pygame.Surface:
    """
    Optional: map any image to a 2-color palette (simple luminance threshold).
    Works best with already-high-contrast mask art.
    """
    surf = src.convert_alpha()
    arr = pygame.surfarray.pixels3d(surf)
    alpha = pygame.surfarray.pixels_alpha(surf)

    # luminance-ish
    lum = (arr[:, :, 0].astype(int) * 30 + arr[:, :, 1].astype(int) * 59 + arr[:, :, 2].astype(int) * 11) // 100
    fg_mask = lum >= threshold

    arr[:, :, 0] = bg[0]
    arr[:, :, 1] = bg[1]
    arr[:, :, 2] = bg[2]

    arr[fg_mask, 0] = fg[0]
    arr[fg_mask, 1] = fg[1]
    arr[fg_mask, 2] = fg[2]

    # keep alpha as-is
    del arr
    del alpha
    return surf

# ----------------------------
# UI Bits
# ----------------------------

@dataclass
class MaskItem:
    id: int
    name: str
    image: Optional[pygame.Surface] = None

@dataclass
class CircleButton:
    item_id: int
    center: pygame.Vector2
    radius: int
    label: str
    image: Optional[pygame.Surface] = None

    def hit_test(self, pos: Tuple[int, int]) -> bool:
        p = pygame.Vector2(pos)
        return p.distance_to(self.center) <= self.radius

class RetroMaskOverlay:
    """
    Cassette retro-futurism HUD overlay:
      - teal frame + black viewport
      - top Hits tab
      - bottom mask selection buttons with images
    """

    def __init__(
        self,
        window_size: Tuple[int, int],
        masks: List[MaskItem],
        hits_getter: Callable[[], int],
        on_mask_changed: Optional[Callable[[int], None]] = None,
        palette_teal: Color = (88, 167, 155),
        palette_ink: Color = (0, 0, 0),
    ):
        self.w, self.h = window_size
        self.masks = masks
        self.hits_getter = hits_getter
        self.on_mask_changed = on_mask_changed

        self.TEAL = palette_teal
        self.INK = palette_ink

        # selection
        self.selected_mask_id: int = masks[0].id if masks else -1

        # layout rects
        self.frame_rect = pygame.Rect(0, 0, self.w, self.h)
        self.viewport_rect = pygame.Rect(0, 0, self.w, self.h)
        self.tab_rect = pygame.Rect(0, 0, 10, 10)

        # surfaces
        self.viewport_surface = pygame.Surface((10, 10), pygame.SRCALPHA)

        # post-process hook (for your future “shader” stage)
        # callable: (surface)->surface (same size)
        self.viewport_postprocess: Optional[Callable[[pygame.Surface], pygame.Surface]] = None

        # buttons
        self.small_buttons: List[CircleButton] = []
        self.big_button: Optional[CircleButton] = None

        # fonts (monospace gives a nice cassette vibe)
        pygame.font.init()
        self.font_small = pygame.font.SysFont("consolas", 18) or pygame.font.Font(None, 18)
        self.font_med = pygame.font.SysFont("consolas", 24) or pygame.font.Font(None, 24)
        self.font_big = pygame.font.SysFont("consolas", 34) or pygame.font.Font(None, 34)

        self.relayout(window_size)

    def relayout(self, window_size: Tuple[int, int]):
        self.w, self.h = window_size

        # outer frame inset (keeps that “border” look)
        margin = int(min(self.w, self.h) * 0.04)
        self.frame_rect = pygame.Rect(margin, margin, self.w - margin * 2, self.h - margin * 2)

        # inner viewport padding (matches your screenshot proportions)
        pad_lr = int(self.frame_rect.w * 0.041)     # ~50px on a ~1223px wide frame
        pad_top = int(self.frame_rect.h * 0.052)    # ~38px on a ~742px tall frame
        pad_bottom = int(self.frame_rect.h * 0.084) # ~62px on ~742px tall frame

        self.viewport_rect = pygame.Rect(
            self.frame_rect.left + pad_lr,
            self.frame_rect.top + pad_top,
            self.frame_rect.w - pad_lr * 2,
            self.frame_rect.h - (pad_top + pad_bottom),
        )

        # rebuild viewport surface to match
        self.viewport_surface = pygame.Surface(self.viewport_rect.size).convert()

        # top tab (height = pad_top + overlap)
        overlap = int(pad_top * 0.76)  # makes tab dip into viewport
        tab_h = pad_top + overlap
        tab_w = int(self.frame_rect.w * 0.16)
        self.tab_rect = pygame.Rect(0, 0, tab_w, tab_h)
        self.tab_rect.centerx = self.frame_rect.centerx
        self.tab_rect.top = self.frame_rect.top

        # button radii based on frame height
        big_r = max(28, int(self.frame_rect.h * 0.071))
        small_r = max(14, int(self.frame_rect.h * 0.031))

        # button y positions (overlap upward into viewport)
        small_y = self.frame_rect.bottom - int(small_r * 1.35)
        big_y = self.frame_rect.bottom - int(big_r * 0.95)

        # x positions from your mock (fractions across the frame)
        left_fracs = [0.265, 0.328, 0.389]
        right_fracs = [0.604, 0.682, 0.756]

        # map masks to 6 small buttons (first 6)
        self.small_buttons.clear()
        for i in range(6):
            if i >= len(self.masks):
                break
            frac = left_fracs[i] if i < 3 else right_fracs[i - 3]
            cx = int(self.frame_rect.left + frac * self.frame_rect.w)
            cy = small_y
            self.small_buttons.append(
                CircleButton(
                    item_id=self.masks[i].id,
                    center=pygame.Vector2(cx, cy),
                    radius=small_r,
                    label="",
                    image=self.masks[i].image,
                )
            )

        # big center button (acts as “current mask” display / click target if you want)
        self.big_button = CircleButton(
            item_id=self.selected_mask_id,
            center=pygame.Vector2(self.frame_rect.centerx, big_y),
            radius=big_r,
            label="",
            image=self._find_mask_image(self.selected_mask_id),
        )


    def _find_mask_image(self, mask_id: int) -> Optional[pygame.Surface]:
        """Return the mask image for a given id (or None)."""
        for m in self.masks:
            if m.id == mask_id:
                return m.image
        return None

    def set_selected_mask(self, mask_id: int):
        if mask_id == self.selected_mask_id:
            return
        self.selected_mask_id = mask_id
        if self.big_button:
            self.big_button.item_id = mask_id
            self.big_button.image = self._find_mask_image(mask_id)
        if self.on_mask_changed:
            self.on_mask_changed(mask_id)

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.VIDEORESIZE:
            self.relayout((event.w, event.h))
        if event.type == pygame.KEYDOWN:
            # Hotkeys: number keys 1..6 (also keypad 1..6) select masks
            key_to_index = {
                pygame.K_1: 1, pygame.K_2: 2, pygame.K_3: 3,
                pygame.K_4: 4, pygame.K_5: 5, pygame.K_6: 6,
                pygame.K_KP1: 1, pygame.K_KP2: 2, pygame.K_KP3: 3,
                pygame.K_KP4: 4, pygame.K_KP5: 5, pygame.K_KP6: 6,
            }
            idx = key_to_index.get(event.key)
            if idx is not None and 1 <= idx <= len(self.masks):
                self.set_selected_mask(self.masks[idx - 1].id)
                return


        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            # small buttons
            for btn in self.small_buttons:
                if btn.hit_test(pos):
                    self.set_selected_mask(btn.item_id)
                    return

            # big button
            if self.big_button and self.big_button.hit_test(pos):
                # you could open a mask menu here later
                return

    def begin_viewport(self, clear: bool = True) -> pygame.Surface:
        """
        Call this each frame to get the surface your existing game should draw onto.
        The overlay will then blit it into the black viewport area.
        """
        if clear:
            self.viewport_surface.fill(self.INK)
        return self.viewport_surface

    def _draw_circle_button(self, screen: pygame.Surface, btn: CircleButton, selected: bool, show_index: Optional[int]):
        # 2-color styling: invert for selected
        fill = self.INK if selected else self.TEAL
        outline = self.TEAL if selected else self.INK
        text_col = self.TEAL if selected else self.INK

        pygame.draw.circle(screen, fill, btn.center, btn.radius)
        pygame.draw.circle(screen, outline, btn.center, btn.radius, width=max(2, btn.radius // 10))

        # image (optional)
        if btn.image is not None:
            # If you want strict 2-color mask art, enable the next line:
            # img = two_colorize(btn.image, fg=text_col, bg=fill)
            img = btn.image
            diameter = int(btn.radius * 1.65)
            clipped = clip_to_circle(img, diameter)
            rect = clipped.get_rect(center=(int(btn.center.x), int(btn.center.y)))
            screen.blit(clipped, rect)
        else:
            # fallback label
            label_surf = self.font_small.render(btn.label, True, text_col)
            screen.blit(label_surf, label_surf.get_rect(center=(int(btn.center.x), int(btn.center.y))))

        # number text near the button (matches your “1 2 3 …” vibe)
        if show_index is not None:
            n_surf = self.font_small.render(str(show_index), True, self.INK)
            # position slightly to the right, slightly above center
            screen.blit(
                n_surf,
                n_surf.get_rect(midleft=(int(btn.center.x + btn.radius + 10), int(btn.center.y - 2))),
            )

    
    def draw_base(self, screen: pygame.Surface, include_viewport_content: bool = True):
        """Draw the frame + viewport area, but optionally exclude the viewport content.

        When using the GPU shader path, call this with include_viewport_content=False,
        then let the shader draw the game into the viewport.
        """
        # frame background
        pygame.draw.rect(screen, self.TEAL, self.frame_rect)

        if include_viewport_content:
            # viewport content (your game) + optional postprocess hook
            view = self.viewport_surface
            if self.viewport_postprocess:
                view = self.viewport_postprocess(self.viewport_surface) or self.viewport_surface
            # blit viewport inside frame (black area)
            screen.blit(view, self.viewport_rect.topleft)
        else:
            # Just fill the viewport with ink (black). The shader will draw game here.
            pygame.draw.rect(screen, self.INK, self.viewport_rect)

        # crisp viewport outline
        pygame.draw.rect(screen, self.INK, self.viewport_rect, width=2)

    def draw_overlay(self, screen: pygame.Surface):
        """Draw UI elements that overlap into the viewport (unshaded)."""
        # top hits tab (rounded pill)
        pygame.draw.rect(
            screen,
            self.TEAL,
            self.tab_rect,
            border_radius=int(self.tab_rect.h * 0.35),
        )
        pygame.draw.rect(
            screen,
            self.INK,
            self.tab_rect,
            width=2,
            border_radius=int(self.tab_rect.h * 0.35),
        )

        hits = self.hits_getter()
        hits_title = self.font_small.render("Hits:", True, self.INK)
        hits_val = self.font_big.render(str(hits), True, self.INK)

        # stack text in the tab
        cx = self.tab_rect.centerx
        screen.blit(hits_title, hits_title.get_rect(center=(cx, self.tab_rect.top + int(self.tab_rect.h * 0.32))))
        screen.blit(hits_val, hits_val.get_rect(center=(cx, self.tab_rect.top + int(self.tab_rect.h * 0.70))))

        # bottom buttons (draw AFTER viewport so they overlap upward like your mock)
        for idx, btn in enumerate(self.small_buttons, start=1):
            self._draw_circle_button(
                screen,
                btn,
                selected=(btn.item_id == self.selected_mask_id),
                show_index=idx,
            )

        if self.big_button:
            # Ensure the big button uses the currently selected mask image (if available)
            self.big_button.image = self._find_mask_image(self.selected_mask_id)

            self._draw_circle_button(
                screen,
                self.big_button,
                selected=True,
                show_index=None,
            )

            # Only show the text label if there is no image for this mask
            if self.big_button.image is None:
                label = self.font_med.render("", True, self.TEAL)
                screen.blit(label, label.get_rect(center=(int(self.big_button.center.x), int(self.big_button.center.y))))

    def draw(self, screen: pygame.Surface):
        # Default: draw everything (viewport content + overlay)
        self.draw_base(screen, include_viewport_content=True)
        self.draw_overlay(screen)



class ZenglViewportShader:
    """GPU post-process applied ONLY to the game viewport, while UI overlaps stay unshaded.

    Strategy (single GPU pass):
      - BaseTex   : full frame WITHOUT viewport content and WITHOUT overlap widgets
      - GameTex   : full frame with ONLY the game viewport drawn into it (rest black)
      - OverlayTex: ONLY the overlapping UI widgets (tab + mask buttons), with alpha

    The fragment shader:
      - outside viewport -> BaseTex
      - inside viewport  -> CRT effect sampling GameTex
      - then alpha-blend OverlayTex on top everywhere
    """

    def __init__(self, window_size: Tuple[int, int], viewport_rect: pygame.Rect, teal: Color, ink: Color):
        if zengl is None:
            raise RuntimeError(
                "zengl is not installed/available. Install it (pip install zengl) and ensure your web build bundles it."
            )

        self.window_size = window_size
        self.viewport_rect = viewport_rect.copy()
        self.teal = teal
        self.ink = ink

        self.ctx = zengl.context()

        # std140 UBO, 32 bytes (8 floats) for alignment:
        # [res_x, res_y, res_z, pad0, time, pad1, pad2, pad3]
        self.common = self.ctx.buffer(size=32, uniform=True)

        self.base_tex = None
        self.game_tex = None
        self.overlay_tex = None
        self.output = None
        self.pipeline = None
        self._build_pipeline()

    def resize(self, window_size: Tuple[int, int], viewport_rect: pygame.Rect):
        self.window_size = window_size
        self.viewport_rect = viewport_rect.copy()
        self._build_pipeline()

    def _glsl_prelude(self) -> str:
        # Desktop dev uses OpenGL (GLSL 330). Web release uses WebGL2 (GLSL ES 300).
        if IS_WEB:
            return "#version 300 es\nprecision highp float;\nprecision highp int;\n"
        return "#version 330 core\n"

    def _build_pipeline(self):
        w, h = self.window_size

        # Textures: all full-frame
        self.base_tex = self.ctx.image((w, h), "rgba8unorm", None, texture=True)
        self.game_tex = self.ctx.image((w, h), "rgba8unorm", None, texture=True)
        self.overlay_tex = self.ctx.image((w, h), "rgba8unorm", None, texture=True)

        # Offscreen color target (framebuffer)
        self.output = self.ctx.image((w, h), "rgba8unorm")

        # Apply effect only INSIDE the viewport content area, not the border.
        inner = self.viewport_rect.inflate(-4, -4)

        # Convert pygame top-left coords to OpenGL bottom-left coords.
        vx = int(inner.x)
        vy = int(h - (inner.y + inner.h))
        vw = int(inner.w)
        vh = int(inner.h)

        prelude = self._glsl_prelude()

        vertex_shader = prelude + r"""
        const vec2 vertices[3] = vec2[3](
            vec2(-1.0, -1.0),
            vec2( 3.0, -1.0),
            vec2(-1.0,  3.0)
        );
        void main() {
            gl_Position = vec4(vertices[gl_VertexID], 0.0, 1.0);
        }
        """

        frag_template = r"""
        layout (std140) uniform Common {
            vec3 iResolution;
            float iTime;
        };

        uniform sampler2D BaseTex;
        uniform sampler2D GameTex;
        uniform sampler2D OverlayTex;

        layout(location = 0) out vec4 frag_color;

        vec3 scanline(vec2 coord, vec3 screen) {
            screen.rgb -= sin((coord.y + (iTime * 29.0))) * 0.02;
            return screen;
        }

        vec2 crt(vec2 coord, float bend) {
            coord = (coord - 0.5) * 2.0;
            coord *= 1.1;
            coord.x *= 1.0 + pow((abs(coord.y) / bend), 2.0);
            coord.y *= 1.0 + pow((abs(coord.x) / bend), 2.0);
            coord  = (coord / 2.0) + 0.5;
            return coord;
        }

        vec3 sampleSplit(sampler2D tex, vec2 coord) {
            vec3 frag;
            float s = sin(iTime);
            frag.r = texture(tex, vec2(coord.x - 0.01 * s, coord.y)).r;
            frag.g = texture(tex, vec2(coord.x             , coord.y)).g;
            frag.b = texture(tex, vec2(coord.x + 0.01 * s, coord.y)).b;
            return frag;
        }

        // Pygame surfaces use top-left origin; flip Y when sampling.
        vec3 sample_base(vec2 uv) {
            uv.y = 1.0 - uv.y;
            return texture(BaseTex, uv).rgb;
        }
        vec3 sample_game(vec2 uv) {
            uv.y = 1.0 - uv.y;
            return texture(GameTex, uv).rgb;
        }
        vec4 sample_overlay(vec2 uv) {
            uv.y = 1.0 - uv.y;
            return texture(OverlayTex, uv);
        }

        void main() {
            vec2 fragCoord = gl_FragCoord.xy;

            // Full-screen UV (0..1)
            vec2 full_uv = fragCoord.xy / iResolution.xy;

            // Default: base frame
            vec3 col = sample_base(full_uv);

            // Restrict CRT effect to viewport inner rect
            bool inside = (fragCoord.x >= %(vx)d.0) && (fragCoord.x < (%(vx2)d.0)) &&
                          (fragCoord.y >= %(vy)d.0) && (fragCoord.y < (%(vy2)d.0));

            if (inside) {
                // Local UV inside viewport (0..1)
                vec2 vuv = (fragCoord - vec2(%(vx)d.0, %(vy)d.0)) / vec2(%(vw)d.0, %(vh)d.0);

                vec2 crtCoords = crt(vuv, 3.2);

                // Outside warped region -> black
                if (crtCoords.x < 0.0 || crtCoords.x > 1.0 || crtCoords.y < 0.0 || crtCoords.y > 1.0) {
                    col = vec3(0.0);
                } else {
                    // Map warped local coords back to full-screen UV for sampling GameTex
                    vec2 sample_px = vec2(%(vx)d.0, %(vy)d.0) + crtCoords * vec2(%(vw)d.0, %(vh)d.0);
                    vec2 sample_uv = sample_px / iResolution.xy;

                    // Split channels (GameTex coord expects bottom-left origin here)
                    col = sampleSplit(GameTex, vec2(sample_uv.x, 1.0 - sample_uv.y));

                    // Scanlines in viewport space
                    vec2 screenSpace = crtCoords * vec2(%(vw)d.0, %(vh)d.0);
                    col = scanline(screenSpace, col);
                }
            }

            // Composite overlap UI on top (unshaded)
            vec4 ov = sample_overlay(full_uv);
            col = mix(col, ov.rgb, ov.a);

            frag_color = vec4(col, 1.0);
        }
        """

        fragment_shader = prelude + (
            frag_template % {
                "vx": vx, "vy": vy, "vw": vw, "vh": vh,
                "vx2": vx + vw, "vy2": vy + vh,
            }
        )

        try:
            self.pipeline = self.ctx.pipeline(
                vertex_shader=vertex_shader,
                fragment_shader=fragment_shader,
                framebuffer=[self.output],
                layout=[
                    {"name": "Common", "binding": 0},
                    {"name": "BaseTex", "binding": 1},
                    {"name": "GameTex", "binding": 2},
                    {"name": "OverlayTex", "binding": 3},
                ],
                resources=[
                    {"type": "uniform_buffer", "binding": 0, "buffer": self.common},
                    {"type": "sampler", "binding": 1, "image": self.base_tex,
                     "wrap_x": "clamp_to_edge", "wrap_y": "clamp_to_edge",
                     "min_filter": "nearest", "mag_filter": "nearest"},
                    {"type": "sampler", "binding": 2, "image": self.game_tex,
                     "wrap_x": "clamp_to_edge", "wrap_y": "clamp_to_edge",
                     "min_filter": "nearest", "mag_filter": "nearest"},
                    {"type": "sampler", "binding": 3, "image": self.overlay_tex,
                     "wrap_x": "clamp_to_edge", "wrap_y": "clamp_to_edge",
                     "min_filter": "nearest", "mag_filter": "nearest"},
                ],
                topology="triangles",
                vertex_count=3,
            )
        except Exception as e:
            print("ZenGL pipeline build failed:", e)
            raise

    def present(self, base_frame: pygame.Surface, game_frame: pygame.Surface, overlay_frame: pygame.Surface, time_sec: float):
        """Upload frame surfaces and draw with shader."""
        w, h = self.window_size
        self.common.write(struct.pack(
            "8f",
            float(w), float(h), 1.0, 0.0,
            float(time_sec), 0.0, 0.0, 0.0,
        ))

        # Upload WITHOUT vertical flip (shader flips UV)
        self.base_tex.write(pygame.image.tostring(base_frame, "RGBA", False))
        self.game_tex.write(pygame.image.tostring(game_frame, "RGBA", False))
        self.overlay_tex.write(pygame.image.tostring(overlay_frame, "RGBA", False))

        self.ctx.new_frame(clear=True)
        try:
            self.output.clear()
        except Exception:
            pass
        self.pipeline.render()
        try:
            self.output.blit()
        except Exception:
            pass
        try:
            self.ctx.end_frame(flush=True)
        except TypeError:
            self.ctx.end_frame()

# ----------------------------
# Game integration entrypoint
# ----------------------------

import asyncio
from pathlib import Path

import pygame as pg

import settings as S
from app_init import init_app, shutdown_app
from commands import process_commands
from game import tick_game
from initalisation import init_game
from render import render


def _state_get(st, key, default=None):
    if isinstance(st, dict):
        return st.get(key, default)
    return getattr(st, key, default)


def _state_set(st, key, value):
    if isinstance(st, dict):
        st[key] = value
    else:
        setattr(st, key, value)


def _ensure_assets_working_dir():
    """Try to set CWD so relative asset paths used by init_game() resolve.

    We look in a few likely roots (current CWD, this file's folder, parents).
    """
    here = Path(__file__).resolve()
    candidates = [
        Path.cwd(),
        here.parent,
        here.parent.parent,
        here.parent.parent.parent,
    ]

    # Prefer a candidate that actually contains the expected assets folder.
    # (Your error mentioned assets/images/mask_shield.png.)
    expected = Path("assets/images/mask_shield.png")

    for c in candidates:
        if (c / expected).exists():
            os.chdir(c)
            return

    for c in candidates:
        if (c / "assets").exists():
            os.chdir(c)
            return


async def main():
    # Ensure asset-relative loads (atlases etc.) behave whether you run from repo root or package dir.
    _ensure_assets_working_dir()

    screen, clock, font = init_app()

    # If you want the *GPU* shader path (WebGL2 in browser builds), the window must be OPENGL.
    if zengl is None:
        raise RuntimeError(
            "GPU shader path requires zengl. Install it (pip install zengl) and ensure your web build bundles it."
        )

    use_shader = True
    flags = pg.OPENGL | pg.DOUBLEBUF | pg.RESIZABLE

    if use_shader:
        size = screen.get_size()

        # Desktop dev: request an OpenGL 3.3 context so GLSL 330 compiles.
        # Web release (pygbag/emscripten) will ignore these and use WebGL2.
        if not IS_WEB:
            try:
                pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
                pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
                pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
                pg.display.gl_set_attribute(pg.GL_CONTEXT_FORWARD_COMPATIBLE_FLAG, 1)
                pg.display.gl_set_attribute(pg.GL_DOUBLEBUFFER, 1)
            except Exception:
                pass

        screen = pg.display.set_mode(size, flags)

        # Three-layer canvases:
        #   base   = frame w/ viewport outline (no game content, no overlap widgets)
        #   game   = only game pixels in the viewport (rest black)
        #   overlay= overlap widgets only (tab + buttons), with alpha
        base_canvas = pg.Surface(size).convert()
        game_canvas = pg.Surface(size).convert()
        overlay_canvas = pg.Surface(size, pg.SRCALPHA).convert_alpha()
    else:
        base_canvas = None
        game_canvas = None
        overlay_canvas = None

    # --- init game state exactly like the original main.py ---
    reg, state = init_game()
    process_commands(reg, state)

    # ----- Overlay setup -----
    # These paths are optional; missing files just show text-only buttons.
    # Keep them relative to an 'assets' folder.
    mask_paths = [
        "assets/mask1.png",
        "assets/mask2.png",
        "assets/mask3.png",
        "assets/mask4.png",
        "assets/mask5.png",
        "assets/mask6.png",
        "assets/images/mask1.png",
        "assets/images/mask2.png",
        "assets/images/mask3.png",
        "assets/images/mask4.png",
        "assets/images/mask5.png",
        "assets/images/mask6.png",
    ]

    # Build 6 MaskItems, trying multiple candidate files per slot.
    masks: List[MaskItem] = []
    for i in range(6):
        img = None
        # try a couple common naming patterns
        candidates = [
            f"assets/mask{i+1}.png",
            f"assets/images/mask{i+1}.png",
            f"assets/images/mask_{i+1}.png",
        ]
        for p in candidates:
            img = load_image(p)
            if img is not None:
                break
        masks.append(MaskItem(i + 1, f"Mask {i + 1}", img))

    def get_hits() -> int:
        return int(_state_get(state, "hits", 0) or 0)

    def on_mask_changed(mask_id: int):
        _state_set(state, "selected_mask_id", mask_id)

    ui = RetroMaskOverlay(
        window_size=screen.get_size(),
        masks=masks,
        hits_getter=get_hits,
        on_mask_changed=on_mask_changed,
    )

    shader = ZenglViewportShader(screen.get_size(), ui.viewport_rect, ui.TEAL, ui.INK) if use_shader else None

    running = True
    while running:
        # Match the original main.py behaviour: increment frame counter
        _state_set(state, "frame", int(_state_get(state, "frame", 0) or 0) + 1)

        # Handle events (we can't use poll_quit() because it would consume events the UI needs)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                break

            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                running = False
                break

            if use_shader and event.type == pg.VIDEORESIZE:
                size = (event.w, event.h)

                # Recreate GL context (desktop: request 3.3 again)
                if not IS_WEB:
                    try:
                        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
                        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
                        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
                        pg.display.gl_set_attribute(pg.GL_CONTEXT_FORWARD_COMPATIBLE_FLAG, 1)
                        pg.display.gl_set_attribute(pg.GL_DOUBLEBUFFER, 1)
                    except Exception:
                        pass

                screen = pg.display.set_mode(size, flags)

                base_canvas = pg.Surface(size).convert()
                game_canvas = pg.Surface(size).convert()
                overlay_canvas = pg.Surface(size, pg.SRCALPHA).convert_alpha()

                ui.relayout(size)
                if shader:
                    shader.resize(size, ui.viewport_rect)
                continue

            ui.handle_event(event)

        if not running:
            break

        dt = clock.tick(S.TARGET_FPS) / 1000.0

        tick_game(reg, state, dt)
        process_commands(reg, state)

        # Render the game into the viewport surface (this is the key merge)
        viewport = ui.begin_viewport(clear=True)
        render(viewport, reg, state, font)

        if use_shader and shader and base_canvas and game_canvas and overlay_canvas:
            # Base: frame + viewport outline, but NO viewport content and NO overlap widgets
            base_canvas.fill((0, 0, 0))
            ui.draw_base(base_canvas, include_viewport_content=False)

            # Game: only the viewport content in a black full-frame
            game_canvas.fill((0, 0, 0))
            game_canvas.blit(ui.viewport_surface, ui.viewport_rect.topleft)

            # Overlay: only overlap widgets (tab + mask buttons), with alpha
            overlay_canvas.fill((0, 0, 0, 0))
            ui.draw_overlay(overlay_canvas)

            shader.present(base_canvas, game_canvas, overlay_canvas, pg.time.get_ticks() / 1000.0)
            pg.display.flip()
        else:
            # Fallback: no shader path, draw directly like normal pygame
            screen.fill((0, 0, 0))
            ui.draw(screen)
            pg.display.flip()

        await asyncio.sleep(0)

    shutdown_app()


if __name__ == "__main__":
    asyncio.run(main())