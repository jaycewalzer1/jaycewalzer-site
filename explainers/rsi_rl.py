"""RSI-RL: a self-improving factory for RL coding tasks, held near a 25% frontier pass rate.

Style: Fern-like. A clay 3D pipeline with slow camera moves, a real terminal capture of the
gate (live run 2026-11-17) intercut, then a flat diagram for the calibration band.

Facts from the repo (jaycewalzer1/rsi-rl-dev): README (loop, gate stages, band 0.15-0.35,
target 0.25, live1 scan: 13 complaints, 5 paper-backed modes), rsi/gate.py, rsi/calibrate.py,
examples/frist-hackathon/history.jsonl (pass counts and mode_slips).
"""
import os

from style import *

STILLS = os.environ.get(
    "EXPLAINER_STILLS",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "stills"),
)
GROUND = interpolate_color(ManimColor(BG), ManimColor(INK), 0.07)


def clay(mob, color):
    """Matte, palette-coloured solid: no stroke, full fill, soft shading from the scene light."""
    mob.set_fill(color, 1).set_stroke(width=0)
    return mob


def upright(text_mob, at):
    """Stand a label up in the x-z plane so a camera on the -y side reads it."""
    text_mob.rotate(PI / 2, axis=RIGHT).move_to(at)
    return text_mob




def floor(w=40, d=30, cy=8.0):
    """A thin clay slab, so the 3D camera depth-sorts it under the solids (a flat Rectangle hides them)."""
    return clay(Prism(dimensions=[w, d, 0.05]), GROUND).move_to(np.array([0, cy, -0.03]))


NAMES = ["X posts", "papers", "combine", "build", "gate", "calibrate"]
HEIGHTS = [0.9, 0.9, 1.3, 1.3, 1.7, 1.3]
COLORS = [DRIFT, DRIFT, SEA, SEA, SEA, GOLD]
XS = [-7.5 + 3 * i for i in range(6)]


def stations():
    boxes, labels = VGroup(), VGroup()
    for x, n, h, c in zip(XS, NAMES, HEIGHTS, COLORS):
        boxes.add(clay(Prism(dimensions=[1.3, 1.3, h]), c).move_to(np.array([x, 0.9, h / 2])))
        labels.add(upright(T(n, 36, INK), np.array([x, 0.9, h + 0.7])))
    track = Line(np.array([XS[0], -0.9, 0.01]), np.array([XS[-1], -0.9, 0.01]), color=MUTED, stroke_width=3)
    return boxes, labels, track


def hide(scene, labels, positions, focus, lo, hi):
    """Fade out, before a camera move, every visible label whose anchor will fall outside the window."""
    out = [l for l, p in zip(labels, positions) if not lo <= p - focus <= hi and l.get_fill_opacity() > 0]
    if out:
        scene.play(*[l.animate.set_opacity(0) for l in out], run_time=0.35)


def shown(labels, positions, focus, lo, hi):
    """Opacity animations so only labels whose anchor lies in [focus+lo, focus+hi] are visible.
    The 3D labels are invisible to the layout linter, so they are faded out before they can reach a frame edge."""
    return [l.animate.set_opacity(1 if lo <= p - focus <= hi else 0) for l, p in zip(labels, positions)]


class Explainer3D(ThreeDScene):
    """style.Explainer for a ThreeDScene: captions and titles stay fixed in frame; lint checks only those."""

    def setup(self):
        self._f1 = register_font(os.path.join(HERE, "fonts", "EBGaramond.ttf")); self._f1.__enter__()
        self._f2 = register_font(os.path.join(HERE, "fonts", "EBGaramond-Italic.ttf")); self._f2.__enter__()
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

    def flat(self, *mobs):
        self.add_fixed_in_frame_mobjects(*mobs)
        self.remove(*mobs)

    def say(self, old, text, color=INK, wait=2.2):
        new = T(text, 34, color).to_edge(DOWN, buff=0.5)
        if new.width > config.frame_width - 1.2:
            new.scale_to_fit_width(config.frame_width - 1.2)
        bg = BackgroundRectangle(new, color=BG, fill_opacity=0.75, buff=0.18)
        grp = VGroup(bg, new)
        self.flat(grp)
        if old is None:
            self.play(FadeIn(grp, shift=UP * 0.1), run_time=0.7)
        else:
            self.play(FadeOut(old), FadeIn(grp, shift=UP * 0.1), run_time=0.7)
        self.wait(wait)
        return grp


class RsiA(Explainer3D):
    """Title, then the loop as a row of clay stations with the camera dollying along it."""

    def construct(self):
        t = T("RSI-RL", 72)
        s = I("a factory for RL tasks that teach", 34, MUTED).next_to(t, DOWN, buff=0.35)
        rule = Line(LEFT * 0.9, RIGHT * 0.9, color=GOLD, stroke_width=2).next_to(s, DOWN, buff=0.45)
        self.play(FadeIn(t, shift=UP * 0.15), run_time=1.2)
        self.play(FadeIn(s), Create(rule), run_time=1)
        self.wait(0.5)
        self.play(FadeOut(VGroup(t, s, rule)), run_time=0.7)

        self.set_camera_orientation(phi=55 * DEGREES, theta=-90 * DEGREES, zoom=1.25,
                                    frame_center=np.array([-6.0, 0, 0.2]))
        boxes, labels, track = stations()
        self.add(floor(), track)
        cap = self.say(None, "It starts where developers complain: posts on X about coding agents.", wait=0.2)
        W = (-4.5, 4.5)
        for l, x in zip(labels, XS):
            l.set_opacity(1 if W[0] <= x + 6.0 <= W[1] else 0)
        self.play(LaggedStart(*[GrowFromPoint(b, b.get_bottom()) for b in boxes], lag_ratio=0.12),
                  LaggedStart(*[FadeIn(l) for l in labels], lag_ratio=0.12), run_time=2.0)

        # 13 complaints leave the X station; 5 survive the papers check (README: live1 scan)
        rng = np.random.default_rng(3)
        posts = [clay(Cube(side_length=0.24), DRIFT).move_to(
            np.array([XS[0] + rng.uniform(-1.0, 1.0), -0.9 + rng.uniform(-0.8, 0.2), 0.12])) for _ in range(13)]
        self.play(LaggedStart(*[FadeIn(c, shift=OUT * 0.4) for c in posts], lag_ratio=0.08), run_time=1.6)
        cap = self.say(cap, "13 concrete complaints. A failure mode survives only if a paper backs it.", wait=0.2)
        keep = [1, 4, 6, 9, 11]
        hide(self, labels, XS, -3.5, *W)
        self.move_camera(frame_center=np.array([-3.5, 0, 0.2]), run_time=2.6,
                         added_anims=[c.animate.move_to(np.array([XS[1] + (i % 7 - 3) * 0.32, -0.9 - (i // 7) * 0.32, 0.12]))
                                      for i, c in enumerate(posts)] + shown(labels, XS, -3.5, *W))
        self.play(*[posts[i].animate.set_fill(GOLD) for i in keep],
                  *[FadeOut(posts[i], shift=IN * 0.3) for i in range(13) if i not in keep], run_time=1.2)
        modes = [posts[i] for i in keep]
        self.wait(0.4)

        cap = self.say(cap, "Three or more independent modes are stacked into one Harbor task.", wait=0.2)
        hide(self, labels, XS, -0.5, *W)
        self.move_camera(frame_center=np.array([-0.5, 0, 0.2]), run_time=2.4,
                         added_anims=[c.animate.move_to(np.array([XS[2] + (i - 1) * 0.3, -0.9, 0.12]))
                                      for i, c in enumerate(modes[:3])] + [FadeOut(m) for m in modes[3:]] + shown(labels, XS, -0.5, *W))
        task = clay(Cube(side_length=0.55), GOLD).move_to(np.array([XS[2], -0.9, 0.28]))
        self.play(ReplacementTransform(VGroup(*modes[:3]), task), run_time=1)
        cap = self.say(cap, "A ticket, a starting repo, hidden tests and a reference fix.", wait=0.2)
        hide(self, labels, XS, 3.0, *W)
        self.move_camera(frame_center=np.array([3.0, 0, 0.2]), run_time=2.8,
                         added_anims=[task.animate.move_to(np.array([XS[4], -0.9, 0.28]))] + shown(labels, XS, 3.0, *W))
        self.wait(0.6)
        self.play(FadeOut(cap), run_time=0.5)


class RsiB(Explainer):
    """Real output: the gate, run live on the repo's smoke task (2026-11-17), pushed in slowly."""

    def construct(self):
        img = ImageMobject(os.path.join(STILLS, "rsi_gate.png")).scale_to_fit_width(config.frame_width)
        tag = I("the gate, run live on the repo's smoke task", 30, GOLD)
        lab = VGroup(BackgroundRectangle(tag, color=BG, fill_opacity=0.92, buff=0.2), tag).to_edge(DOWN, buff=0.45)
        self.play(FadeIn(img), run_time=0.8)
        self.play(FadeIn(lab), img.animate.scale(1.35).shift(RIGHT * 2.6 + DOWN * 1.2), run_time=5.0, rate_func=smooth)
        self.wait(0.3)
        self.play(FadeOut(img), FadeOut(lab), run_time=0.8)


class RsiC(Explainer3D):
    """Seven gates in a corridor angled away from the camera; the camera tracks the task through;
    difficulty fires eight attempts. (Theta stays fixed: changing it with frame_center shifts the
    fixed-in-frame captions in Manim's 3D camera, so the corridor is angled instead.)"""

    def construct(self):
        stages = ["shape", "oracle ×3", "no-op", "mutations", "shortcut", "difficulty", "inspect"]
        ang = 30 * DEGREES
        u = np.array([np.cos(ang), np.sin(ang), 0])

        def at(d, z=0.0, side=0.0):
            return u * d + np.array([-np.sin(ang), np.cos(ang), 0]) * side + np.array([0, 0, z])

        ds = [2.4 * i for i in range(7)]
        self.set_camera_orientation(phi=66 * DEGREES, theta=-90 * DEGREES, zoom=1.2, frame_center=at(ds[0] + 1.0, 1.0))
        frames, labs = VGroup(), VGroup()
        for d, s in zip(ds, stages):
            fr = Square(1.8, color=MUTED, stroke_width=7).rotate(PI / 2, axis=UP).rotate(ang, axis=OUT).move_to(at(d, 0.95))
            frames.add(fr)
            labs.add(upright(T(s, 40, MUTED), at(d, 2.3)))
        self.add(clay(Prism(dimensions=[60, 40, 0.05]), GROUND).move_to(np.array([0, 10, -0.03])))
        cap = self.say(None, "Every task must clear a seven-stage gate before it counts.", wait=0.2)
        LO, HI = -1.5, 1.6
        for l, d in zip(labs, ds):
            l.set_opacity(1 if LO <= d - (ds[0] + 1.0) <= HI else 0)
        self.play(LaggedStart(*[Create(f) for f in frames], lag_ratio=0.08),
                  LaggedStart(*[FadeIn(l) for l in labs], lag_ratio=0.08), run_time=1.6)
        cube = clay(Cube(side_length=0.5), GOLD).rotate(ang, axis=OUT).move_to(at(ds[0] - 1.4, 0.3))
        self.play(FadeIn(cube), run_time=0.4)
        notes = {1: "The reference fix must score 1, three runs in a row.",
                 2: "The untouched repo must score 0.",
                 3: "Every deliberately wrong fix must be caught by a failing test.",
                 4: "A solver told to game the grader must score 0."}
        for i in range(5):
            hide(self, labs, ds, ds[i] + 1.2, LO, HI)
            self.move_camera(frame_center=at(ds[i] + 1.2, 1.0), run_time=1.0,
                             added_anims=[cube.animate.move_to(at(ds[i] + 0.8, 0.3)),
                                          frames[i].animate.set_color(SEA)] + shown(labs, ds, ds[i] + 1.2, LO, HI))
            labs[i].set_color(INK)
            if i in notes:
                cap = self.say(cap, notes[i], wait=0.9)
        cap = self.say(cap, "Then a frontier agent gets K cold attempts at it.", wait=0.2)
        shots = [clay(Cube(side_length=0.2), GOLD).move_to(cube.get_center() + at(0, 0, (k - 3.5) * 0.24)) for k in range(8)]
        self.add(*shots)
        self.remove(cube)
        solved = {2, 5}
        hide(self, labs, ds, ds[5] + 0.6, LO, 2.0)
        self.move_camera(frame_center=at(ds[5] + 0.6, 1.0), zoom=1.35, run_time=1.8,
                         added_anims=[s.animate.move_to(at(ds[5] + 0.8, 0.12, (k - 3.5) * 0.24)).set_fill(GOLD if k in solved else CORAL)
                                      for k, s in enumerate(shots)] + [frames[5].animate.set_color(GOLD)] + shown(labs, ds, ds[5] + 0.6, LO, 2.0))
        labs[5].set_color(INK)
        cap = self.say(cap, "The target: about one in four solves it.", GOLD, wait=1.0)
        cap = self.say(cap, "Last, every failed test must map to a sentence in the ticket.", wait=0.2)
        hide(self, labs, ds, ds[6] + 0.2, LO, HI)
        self.move_camera(frame_center=at(ds[6] + 0.2, 1.0), zoom=1.2, run_time=1.2,
                         added_anims=[frames[6].animate.set_color(SEA)] + shown(labs, ds, ds[6] + 0.2, LO, HI))
        labs[6].set_color(INK)
        self.wait(0.8)
        self.play(FadeOut(cap), run_time=0.5)


class RsiD(Explainer):
    """Flat: why about 25%, the band on real tasks, and which failure modes made solvers slip."""

    def construct(self):
        rows = [(0, "0 of 8 solved", "nothing to learn from"),
                (8, "8 of 8 solved", "nothing left to learn"),
                (2, "2 of 8 solved", "a learning signal")]
        grid = VGroup()
        for k, left, right in rows:
            sq = VGroup(*[Square(0.5, stroke_width=0, fill_opacity=1,
                                 fill_color=(GOLD if k == 2 else SEA) if j < k else CORAL) for j in range(8)]).arrange(RIGHT, buff=0.12)
            grid.add(VGroup(T(left, 30, MUTED), sq, T(right, 30, GOLD if k == 2 else MUTED)))
        for row in grid:
            row[1].move_to(ORIGIN)
            row[0].next_to(row[1], LEFT, buff=0.45)
            row[2].next_to(row[1], RIGHT, buff=0.45)
        grid.arrange(DOWN, buff=0.5).move_to(UP * 0.5)
        cap = self.say(None, "Graded all-or-nothing, eight attempts each.", wait=0.2)
        for row in grid:
            self.play(FadeIn(row[0]), LaggedStart(*[FadeIn(s, scale=0.6) for s in row[1]], lag_ratio=0.06), run_time=1.0)
            self.play(FadeIn(row[2], shift=LEFT * 0.1), run_time=0.5)
            self.wait(0.4)
        cap = self.say(cap, "Only a mix of passes and failures gives the learner something to compare.", wait=1.1)
        self.play(FadeOut(grid), FadeOut(cap), run_time=0.7)

        nl = NumberLine(x_range=[0, 1, 0.25], length=11, color=MUTED, stroke_width=3, tick_size=0.08).shift(DOWN * 0.8)
        ticks = VGroup(*[T(f"{int(v * 100)}%", 26, MUTED).next_to(nl.n2p(v), DOWN, buff=0.25) for v in [0, 0.25, 0.5, 0.75, 1]])
        band = Rectangle(width=nl.n2p(0.35)[0] - nl.n2p(0.15)[0], height=2.5, stroke_width=0, fill_color=GOLD, fill_opacity=0.16)
        band.move_to((nl.n2p(0.15) + nl.n2p(0.35)) / 2 + UP * 1.25)
        blab = T("band 15–35%", 28, GOLD).next_to(band, UP, buff=0.15)
        head = I("cold Opus 5.5 on the six Frist hackathon tasks", 30, MUTED).to_edge(UP, buff=0.6)
        cap = self.say(None, "Calibration holds each task inside a band around 25%.", wait=0.05)
        tasks = [(1, 3, 0), (1, 4, 0), (1, 3, 1), (3, 6, 0), (3, 6, 1), (3, 3, 0)]
        dots = VGroup()
        for k, n, stack in tasks:
            p = k / n
            col = GOLD if 0.15 <= p <= 0.35 else CORAL
            d = Dot(nl.n2p(p) + UP * (0.45 + 0.8 * stack), radius=0.13, color=col)
            lbl = T(f"{k}/{n}", 26, col)
            lbl.next_to(d, LEFT if (k, n) == (1, 4) else RIGHT, buff=0.12)
            dots.add(VGroup(d, lbl))
        self.play(Create(nl), FadeIn(ticks), FadeIn(head), FadeIn(band), FadeIn(blab),
                  LaggedStart(*[FadeIn(d, shift=DOWN * 0.2) for d in dots], lag_ratio=0.12), run_time=2.0)
        self.wait(0.8)
        cap = self.say(cap, "Three landed in band. Too easy: add a criterion from a fresh failure mode.", wait=1.7)
        cap = self.say(cap, "Too hard: drop the case family most attempts miss. Then measure again.", wait=1.7)
        self.play(FadeOut(VGroup(nl, ticks, band, blab, head, dots)), FadeOut(cap), run_time=0.7)

        slips = [("derived-surface-omitted", 6), ("sibling-path-missed", 3), ("seam-assumption", 3),
                 ("timezone-math", 1), ("cross-process-state", 1), ("idempotency-under-failure", 0)]
        bars = VGroup()
        x0 = LEFT * 0.4
        for r, (name, k) in enumerate(slips):
            y = UP * (1.6 - 0.62 * r)
            bar = Rectangle(width=max(0.8 * k, 0.05), height=0.38, stroke_width=0, fill_opacity=1,
                            fill_color=GOLD if k >= 3 else (SEA if k else MUTED))
            bar.move_to(x0 + y, aligned_edge=LEFT)
            lab = T(name, 28, INK if k else MUTED).next_to(bar, LEFT, buff=0.35).align_to(x0 + LEFT * 0.35, RIGHT)
            num = T(str(k), 28, MUTED).next_to(bar, RIGHT, buff=0.2)
            bars.add(VGroup(lab, bar, num))
        head = I("failed attempts per failure mode, Frist history", 30, MUTED).to_edge(UP, buff=0.6)
        cap = self.say(None, "Every calibrated task records which failure modes made solvers slip.", wait=0.2)
        self.play(FadeIn(head), LaggedStart(*[FadeIn(b[0]) for b in bars], lag_ratio=0.08),
                  LaggedStart(*[GrowFromEdge(b[1], LEFT) for b in bars], lag_ratio=0.08),
                  LaggedStart(*[FadeIn(b[2]) for b in bars], lag_ratio=0.08), run_time=1.8)
        self.wait(1.2)
        cap = self.say(cap, "The next design samples modes from that history, leaning on what still works.", wait=1.8)
        self.play(FadeOut(bars), FadeOut(head), FadeOut(cap), run_time=0.7)


class RsiE(Explainer3D):
    """The loop closes in 3D: calibrate feeds combine. Then the closing card."""

    def construct(self):
        self.set_camera_orientation(phi=60 * DEGREES, theta=-90 * DEGREES, zoom=0.8,
                                    frame_center=np.array([0, 0, 0.8]))
        boxes, labels, track = stations()
        fl = floor()
        start = np.array([XS[5], 0.9, HEIGHTS[5] + 0.15])
        end = np.array([XS[2], 0.9, HEIGHTS[2] + 0.15])
        arc = ArcBetweenPoints(start, end, angle=PI / 1.6, color=GOLD, stroke_width=7)
        arc.rotate(PI / 2, axis=RIGHT, about_point=(start + end) / 2)
        self.play(FadeIn(VGroup(fl, track, boxes, labels)), run_time=0.7)
        cap = self.say(None, "That feedback is the self-improving part of the loop.", GOLD, wait=0.05)
        self.move_camera(theta=-80 * DEGREES, phi=57 * DEGREES, run_time=3.2, added_anims=[Create(arc, run_time=2.4)])
        self.wait(0.8)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)
        self.set_camera_orientation(phi=0, theta=-90 * DEGREES, zoom=1, frame_center=ORIGIN)
        a = T("RSI-RL", 44)
        b = I("github.com/jaycewalzer1/rsi-rl-dev", 30, GOLD).next_to(a, DOWN, buff=0.4)
        self.play(FadeIn(a), run_time=1)
        self.play(FadeIn(b), run_time=0.8)
        self.wait(2.5)
