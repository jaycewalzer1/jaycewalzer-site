"""Reels Edits: from beats to cuts.

Real data: the onset envelope and waveform of the generated 124 BPM test beat used in the demo,
the grid tools/render.py fitted to it (123.96 BPM, first beat +0.26 s), and the 12 CC0 paintings
in the order the render used them. Media lives in explainers/media/reels-edits/.
Style: a calm horizontal timeline, data first, few words.
"""
import json

from style import *

M = os.path.join(HERE, "media", "reels-edits")
X0, X1 = -6.4, 6.4
SPAN = 11.7  # seconds shown


def tx(t):
    return X0 + (X1 - X0) * t / SPAN


class ReelsEdits(Explainer):
    title = "Reels Edits"
    subtitle = "cutting images on the beat, as a seamless loop"

    def construct(self):
        self.title_card()
        d = json.load(open(os.path.join(M, "beat.json")))
        bpm, ph = d["bpm"], d["phase"]
        beat = 60 / bpm

        # waveform
        w = d["wave"]
        n = len(w)
        dt = 12.5 / n
        pts = [[tx(i * dt), 2.1 + 0.55 * v, 0] for i, v in enumerate(w) if i * dt <= SPAN]
        wave = VMobject(stroke_color=MUTED, stroke_width=1.2).set_points_as_corners(pts)
        wl = I("the track", 26, MUTED).next_to(wave, UP, buff=0.12).align_to(wave, LEFT)
        cap = self.say(None, "Start from the music.", wait=0.2)
        self.play(Create(wave), FadeIn(wl), run_time=2)

        # onset strength
        env = [[tx(t), 0.2 + 1.1 * e, 0] for t, e in zip(d["t"], d["env"]) if t <= SPAN]
        on = VMobject(stroke_color=SEA, stroke_width=2.5).set_points_as_corners(env)
        base = Line([X0, 0.2, 0], [X1, 0.2, 0], color=MUTED, stroke_width=1)
        ol = I("onset strength", 26, SEA).next_to(base, UP, buff=1.25).align_to(base, LEFT)
        cap = self.say(cap, "librosa measures where the sound hits: onset strength.", wait=0.2)
        self.play(Create(base), Create(on), FadeIn(ol), run_time=2.2)
        self.wait(0.8)

        # fitted beat grid
        beats = []
        t = ph
        while t <= SPAN:
            beats.append(t)
            t += beat
        grid = VGroup(*[Line([tx(b), -0.15, 0], [tx(b), 1.45, 0], color=GOLD, stroke_width=1.6, stroke_opacity=0.8) for b in beats])
        gl = T(f"{bpm:.2f} BPM, first beat at +{ph:.2f} s", 30, GOLD).move_to(LEFT * 2.6 + UP * 3.25)
        cap = self.say(cap, "A grid search over tempo and phase lines the beats up with the peaks.", wait=0.2)
        self.play(LaggedStart(*[Create(g) for g in grid], lag_ratio=0.05), FadeIn(gl), run_time=2)
        self.wait(1.2)

        # whole bars
        bar = 4 * beat
        nb = int(12 // bar)
        bars = VGroup(*[Rectangle(width=(X1 - X0) * bar / SPAN, height=0.32, stroke_color=DRIFT, stroke_width=1.5,
                                  fill_color=DRIFT, fill_opacity=0.25 if i % 2 else 0.12)
                        .move_to([tx(ph + bar * (i + 0.5)), -0.45, 0]) for i in range(nb)])
        bl = T(f"{nb} bars = {nb * bar:.2f} s", 30, DRIFT).move_to(RIGHT * 3.6 + UP * 3.25)
        cap = self.say(cap, "The edit is a whole number of bars, 7 to 12 seconds, so the loop keeps the rhythm.", wait=0.2)
        self.play(LaggedStart(*[FadeIn(b) for b in bars], lag_ratio=0.1), FadeIn(bl), run_time=1.6)
        self.wait(1.4)

        # cuts every 8 sixteenths = 2 beats, with the real images
        cuts = [ph + 2 * beat * i for i in range(12)]
        thumbs = Group()
        for i, c in enumerate(cuts):
            im = ImageMobject(os.path.join(M, f"cut{i:02d}.jpg"))
            im.height = 1.0
            if im.width > 0.95:
                im.width = 0.95
            im.move_to([tx(c + beat), -1.6, 0])
            thumbs.add(im)
        ticks = VGroup(*[Line([tx(c), -0.7, 0], [tx(c), -2.2, 0], color=INK, stroke_width=2) for c in cuts])
        cap = self.say(cap, "A hard cut every two beats: twelve kept images, in the order they were kept.", wait=0.2)
        for i in range(12):
            self.play(Create(ticks[i]), FadeIn(thumbs[i], shift=DOWN * 0.15), run_time=0.32)
        self.wait(1)

        # loop seam
        arc = ArcBetweenPoints(thumbs[-1].get_bottom() + DOWN * 0.08, thumbs[0].get_bottom() + DOWN * 0.08,
                               angle=-PI / 8, color=GOLD, stroke_width=2.5)
        cap = self.say(cap, "The last shot is the kept image closest in colour to the first, to hide the seam.", GOLD, wait=0.2)
        self.play(Create(arc), run_time=1.4)
        self.wait(1.4)
        cap = self.say(cap, "Measured afterwards: every cut within 16 ms of the beat.", GOLD, wait=2.2)

        self.closing("Reels Edits", "github.com/jaycewalzer1/reels-edits")
