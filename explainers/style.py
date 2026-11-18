"""Shared look for every project explainer: 3Blue1Brown pacing in the site's palette.

Scenes do `from style import *` (all of Manim comes with it). Render from this folder:

    ~/Desktop/lecture-viz/.venv/bin/manim -qh --fps 30 <scene>.py <SceneName> --media_dir build

The palette is the site's, made less washed so it reads on video: a deep Pacific
ground, fog for text, and three accents that each keep one job across a video.
"""
import os
import sys

from manim import *

sys.path.insert(0, os.path.expanduser("~/Desktop/lecture-viz"))
from lecviz.style import layout_problems  # noqa: E402  (off-frame, overlap, tiny-text linter)

HERE = os.path.dirname(os.path.abspath(__file__))

BG = "#1F3240"        # deep Pacific
INK = "#F1ECE2"       # fog
MUTED = "#9AA6AB"     # wet stone, for secondary labels
SEA = "#7FA3B6"       # lighter Pacific: the main thing being explained
DRIFT = "#B59A80"     # driftwood: the second thing, or the environment
GOLD = "#D9BE7E"      # dune grass: the result, the number that matters
CORAL = "#C9826A"     # used sparingly for failure or error

SERIF = "EB Garamond"
config.background_color = BG
config.frame_rate = 30


def T(text, size=40, color=INK, **kw):
    """Body text in the site's serif."""
    return Text(text, font=SERIF, font_size=size, color=color, **kw)


def I(text, size=40, color=INK, **kw):
    return Text(text, font=SERIF, font_size=size, color=color, slant=ITALIC, **kw)


class Explainer(Scene):
    """Title card, then the story, then a closing line. Lints layout after every beat."""

    title = ""
    subtitle = ""

    def setup(self):
        self._font_ctx = register_font(os.path.join(HERE, "fonts", "EBGaramond.ttf"))
        self._font_ctx.__enter__()
        self._font_ctx2 = register_font(os.path.join(HERE, "fonts", "EBGaramond-Italic.ttf"))
        self._font_ctx2.__enter__()
        self.camera.background_color = BG
        self.problems = []

    def play(self, *args, **kwargs):
        super().play(*args, **kwargs)
        for p in layout_problems(self.mobjects):
            if p not in self.problems:
                self.problems.append(p)

    def tear_down(self):
        if self.problems:
            print("LAYOUT PROBLEMS:\n  " + "\n  ".join(self.problems))
        super().tear_down()

    def title_card(self):
        t = T(self.title, 72)
        s = I(self.subtitle, 34, MUTED).next_to(t, DOWN, buff=0.35)
        rule = Line(LEFT * 0.9, RIGHT * 0.9, color=GOLD, stroke_width=2).next_to(s, DOWN, buff=0.45)
        self.play(FadeIn(t, shift=UP * 0.15), run_time=1.2)
        self.play(FadeIn(s), Create(rule), run_time=1)
        self.wait(1.4)
        self.play(FadeOut(VGroup(t, s, rule)), run_time=0.8)

    def caption(self, text, color=INK, size=34):
        """A sentence at the bottom of the frame, like a narration subtitle."""
        c = T(text, size, color).to_edge(DOWN, buff=0.55)
        if c.width > config.frame_width - 1.2:
            c.scale_to_fit_width(config.frame_width - 1.2)
        return c

    def say(self, old, text, color=INK, wait=2.2):
        """Swap the caption, then hold long enough to read it."""
        new = self.caption(text, color)
        if old is None:
            self.play(FadeIn(new, shift=UP * 0.1), run_time=0.7)
        else:
            self.play(FadeOut(old, shift=UP * 0.1), FadeIn(new, shift=UP * 0.1), run_time=0.7)
        self.wait(wait)
        return new

    def closing(self, line, link):
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)
        a = T(line, 44)
        b = I(link, 30, GOLD).next_to(a, DOWN, buff=0.4)
        self.play(FadeIn(a), run_time=1)
        self.play(FadeIn(b), run_time=0.8)
        self.wait(2.5)


class Explainer3D(ThreeDScene):
    """The same helpers for 3D scenes; captions and titles stay fixed to the screen while the camera moves."""

    def setup(self):
        super().setup()
        self._fonts = [register_font(os.path.join(HERE, "fonts", f)) for f in ("EBGaramond.ttf", "EBGaramond-Italic.ttf")]
        for ctx in self._fonts:
            ctx.__enter__()
        self.camera.background_color = BG
        self.problems = []

    def play(self, *args, **kwargs):
        super().play(*args, **kwargs)
        flat = [m for m in self.mobjects if m in self.camera.fixed_in_frame_mobjects]
        for p in layout_problems(flat):
            if p not in self.problems:
                self.problems.append(p)

    def tear_down(self):
        if self.problems:
            print("LAYOUT PROBLEMS:\n  " + "\n  ".join(self.problems))
        super().tear_down()
    title = ""
    subtitle = ""

    def flat(self, *mobs):
        self.add_fixed_in_frame_mobjects(*mobs)
        return mobs[0] if len(mobs) == 1 else mobs

    def caption(self, text, color=INK, size=32):
        c = T(text, size, color).to_edge(DOWN, buff=0.5)
        if c.width > config.frame_width - 1.2:
            c.scale_to_fit_width(config.frame_width - 1.2)
        self.add_fixed_in_frame_mobjects(c)
        c.set_opacity(0)
        return c

    def say(self, old, text, color=INK, wait=2.2):
        new = self.caption(text, color)
        anims = [new.animate.set_opacity(1)]
        if old is not None:
            anims.append(old.animate.set_opacity(0))
        self.play(*anims, run_time=0.7)
        self.wait(wait)
        if old is not None:
            self.remove(old)
        return new
