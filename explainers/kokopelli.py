"""Kokopelli: an agent living inside a world model.

Two Manim scenes, cut together with the repo's own footage by kokopelli_build.sh:
  KokoCity  (3D) the SimWorld city, with a slow orbit
  KokoStudy (2D, on a light ground) the loop, the felt body cue, the 5-arm study, the first run's result

Facts: kokopelli/loop/README.md (60 ticks of 30 sim-seconds), kokopelli/body/README.md (cue / label / none,
the agent never sees a number), experiments/homeostatic/README.md (the comparison arms), docs/exp1_report.md
(first 25-day run: 99 decisions, 25 trained nights, D2/D3 shares, MMLU 75.0 vs 75.0).
"""
import random

from style import *


def fonts(scene):
    scene._f1 = register_font(os.path.join(HERE, "fonts", "EBGaramond.ttf")); scene._f1.__enter__()
    scene._f2 = register_font(os.path.join(HERE, "fonts", "EBGaramond-Italic.ttf")); scene._f2.__enter__()


class KokoCity(ThreeDScene):
    def setup(self):
        fonts(self)
        self.camera.background_color = BG
        self.problems = []

    def play(self, *a, **k):
        super().play(*a, **k)
        for p in layout_problems(self.mobjects):
            if p not in self.problems:
                self.problems.append(p)

    def tear_down(self):
        if self.problems:
            print("LAYOUT PROBLEMS:\n  " + "\n  ".join(self.problems))
        super().tear_down()

    def construct(self):
        random.seed(4)
        self.set_camera_orientation(phi=62 * DEGREES, theta=-60 * DEGREES, zoom=0.55, frame_center=[0, 0, 2.2])
        ground = Square(side_length=12, fill_color=interpolate_color(ManimColor(BG), ManimColor(INK), 0.08),
                        fill_opacity=1, stroke_width=0)
        streets = VGroup(*[Line([-6, y, 0.01], [6, y, 0.01], color=MUTED, stroke_width=2, stroke_opacity=0.35) for y in (-3, 0, 3)],
                         *[Line([x, -6, 0.01], [x, 6, 0.01], color=MUTED, stroke_width=2, stroke_opacity=0.35) for x in (-3, 0, 3)])
        blocks = VGroup()
        for bx in (-4.5, -1.5, 1.5, 4.5):
            for by in (-4.5, -1.5, 1.5, 4.5):
                if (bx, by) == (1.5, -1.5):
                    continue  # the park
                for dx in (-0.6, 0.6):
                    for dy in (-0.6, 0.6):
                        h = random.choice([0.4, 0.6, 0.9, 1.3, 1.8])
                        col = random.choice([DRIFT, INK, SEA, DRIFT])
                        b = Prism(dimensions=[0.9, 0.9, h], fill_color=col, fill_opacity=1, stroke_width=0.6,
                                  stroke_color=BG).move_to([bx + dx, by + dy, h / 2])
                        b.set_shade_in_3d(True)
                        blocks.add(b)
        park = VGroup(*[Sphere(radius=0.28, resolution=(8, 8)).set_color(SEA).move_to([1.5 + x, -1.5 + y, 0.3])
                        for x, y in [(-0.7, -0.6), (0.5, -0.8), (0.0, 0.3), (-0.6, 0.8), (0.8, 0.6)]])
        walker = Dot3D([-6, 0, 0.12], radius=0.12, color=GOLD)
        title = T("Kokopelli", 84).to_edge(UP, buff=0.6)
        sub = I("an agent living inside a world model", 38, GOLD).next_to(title, DOWN, buff=0.2)
        self.add_fixed_in_frame_mobjects(title, sub)
        self.remove(title, sub)
        self.play(Create(streets), run_time=1.0)
        self.play(LaggedStart(*[GrowFromPoint(b, b.get_center() * [1, 1, 0]) for b in blocks], lag_ratio=0.01),
                  FadeIn(park), FadeIn(title), FadeIn(sub), run_time=2.4)
        self.begin_ambient_camera_rotation(rate=0.07)
        self.wait(1.5)
        self.play(FadeOut(title), FadeOut(sub), run_time=0.8)

        cap = T("A city built in Unreal Engine (SimWorld) holds the physical truth.", 40).to_edge(UP, buff=0.55)
        self.add_fixed_in_frame_mobjects(cap); self.remove(cap)
        self.play(FadeIn(cap), FadeIn(walker), run_time=0.7)
        self.play(walker.animate.move_to([0, 0, 0.12]), run_time=2.4, rate_func=linear)
        self.play(walker.animate.move_to([0, -3, 0.12]), run_time=1.6, rate_func=linear)
        cap2 = T("It knows where everything is. It just doesn't look real.", 40).to_edge(UP, buff=0.55)
        self.add_fixed_in_frame_mobjects(cap2); self.remove(cap2)
        self.play(FadeOut(cap), FadeIn(cap2), walker.animate.move_to([3, -3, 0.12]), run_time=1.6, rate_func=linear)
        self.move_camera(phi=72 * DEGREES, zoom=1.1, frame_center=[2, -2.5, 0.4], run_time=2.6)
        self.stop_ambient_camera_rotation()
        self.play(FadeOut(cap2), run_time=0.6)


def card(text, color, w=3.7, h=1.25, size=30, fill=None):
    r = RoundedRectangle(corner_radius=0.16, width=w, height=h, stroke_color=color, stroke_width=3,
                         fill_color=fill or INK, fill_opacity=1)
    t = T(text, size, BG).move_to(r)
    if t.width > w - 0.35:
        t.scale_to_fit_width(w - 0.35)
    return VGroup(r, t)


class KokoStudy(Scene):
    """Light 'paper' ground for the mechanism and the study, unlike the dark 3D city."""

    def setup(self):
        fonts(self)
        self.camera.background_color = INK
        self.problems = []

    def play(self, *a, **k):
        super().play(*a, **k)
        for p in layout_problems(self.mobjects):
            if p not in self.problems:
                self.problems.append(p)

    def tear_down(self):
        if self.problems:
            print("LAYOUT PROBLEMS:\n  " + "\n  ".join(self.problems))
        super().tear_down()

    def cap(self, old, text, wait=2.2, color=BG):
        new = T(text, 36, color).to_edge(DOWN, buff=0.5)
        if old is None:
            self.play(FadeIn(new, shift=UP * 0.1), run_time=0.6)
        else:
            self.play(FadeOut(old), FadeIn(new, shift=UP * 0.1), run_time=0.6)
        self.wait(wait)
        return new

    def construct(self):
        # 1. The loop
        pos = {"sim": UP * 2.0 + LEFT * 4.2, "paint": UP * 2.0 + RIGHT * 4.2,
               "agent": DOWN * 1.2 + RIGHT * 4.2, "act": DOWN * 1.2 + LEFT * 4.2}
        nodes = {
            "sim": card("SimWorld city", DRIFT, fill="#E6D8C9"),
            "paint": card("Cosmos3-Nano paints it", SEA, fill="#D6E1E7"),
            "agent": card("Qwen3-VL-8B agent", GOLD, fill="#F0E4C4"),
            "act": card("its action", DRIFT, fill="#E6D8C9"),
        }
        for k, n in nodes.items():
            n.move_to(pos[k])
        order = ["sim", "paint", "agent", "act"]
        arrows = VGroup()
        labels = ["control videos", "painted film only", "it decides", "lands in the sim"]
        alab = VGroup()
        for i, k in enumerate(order):
            a, b = nodes[k], nodes[order[(i + 1) % 4]]
            ar = Arrow(a.get_center(), b.get_center(), buff=0, color=BG, stroke_width=4, max_tip_length_to_length_ratio=0.06)
            ar.put_start_and_end_on(*self._edge(a, b))
            arrows.add(ar)
            lab = I(labels[i], 28, BG)
            lab.next_to(ar, UP if i == 0 else (RIGHT if i == 1 else (DOWN if i == 2 else LEFT)), buff=0.15)
            alab.add(lab)
        head = I("one tick: 30 sim-seconds", 32, BG).move_to(UP * 0.4)
        c = self.cap(None, "The loop: the sim holds the truth, the world model only draws it.", wait=0.2)
        for i, k in enumerate(order):
            self.play(FadeIn(nodes[k], shift=UP * 0.1), run_time=0.5)
            self.play(GrowArrow(arrows[i]), FadeIn(alab[i]), run_time=0.6)
        self.play(FadeIn(head))
        dot = Dot(color=CORAL, radius=0.1).move_to(arrows[0].get_start())
        self.add(dot)
        for ar in arrows:
            self.play(MoveAlongPath(dot, ar), run_time=0.55, rate_func=linear)
        c = self.cap(c, "60 ticks make 30 sim-minutes of a life.", wait=1.0)

        # 2. The body, felt not read
        body = card("food 0.2", CORAL, w=2.4, h=0.95, size=30, fill="#EED6CC").move_to(UP * 0.8)
        self.play(FadeOut(head), FadeIn(body), run_time=0.6)
        felt = I("“You feel shaky and empty inside.”", 32, BG).move_to(DOWN * 0.1)
        c = self.cap(c, "Its body has numbers, but the agent never sees one.", wait=0.6)
        cross = Line(body.get_left() + RIGHT * 0.2, body.get_right() + LEFT * 0.2, color=CORAL, stroke_width=5)
        self.play(Create(cross))
        self.play(TransformFromCopy(body[1], felt), run_time=1.0)
        self.play(felt.animate.scale(0.85).next_to(nodes["agent"], DOWN, buff=0.25).align_to(nodes["agent"], RIGHT), run_time=1.0)
        c = self.cap(c, "It gets what a body would notice, then decides.", wait=1.8)
        self.play(*[FadeOut(m) for m in [*nodes.values(), arrows, alab, dot, body, cross, felt, c]], run_time=0.8)

        # 3. The study: five arms
        q1 = T("Does living through it, with the weights updated each night,", 38, BG)
        q2 = T("shift a model differently than being told the same facts?", 38, BG)
        q = VGroup(q1, q2).arrange(DOWN, buff=0.15).to_edge(UP, buff=0.5)
        self.play(FadeIn(q), run_time=1.0)
        arms = [("lives it, LoRA\neach night", GOLD, "#F0E4C4"), ("untrained", MUTED, "#E3E6E6"),
                ("told every effect\nin its prompt", SEA, "#D6E1E7"), ("control:\nmaximize", DRIFT, "#E6D8C9"),
                ("control:\nshuffled", DRIFT, "#E6D8C9")]
        cols = VGroup()
        for name, col, fill in arms:
            r = RoundedRectangle(corner_radius=0.14, width=2.3, height=2.9, stroke_color=col, stroke_width=3,
                                 fill_color=fill, fill_opacity=1)
            lines = VGroup(*[T(s, 28, BG) for s in name.split("\n")]).arrange(DOWN, buff=0.1).move_to(r)
            cols.add(VGroup(r, lines))
        cols.arrange(RIGHT, buff=0.3).shift(DOWN * 0.45)
        self.play(LaggedStart(*[FadeIn(cc, shift=UP * 0.2) for cc in cols], lag_ratio=0.18), run_time=1.8)
        c = self.cap(None, "Five arms, one base model, all scored on the same held-out lives.", wait=1.6)
        self.play(Indicate(cols[0][0], color=GOLD, scale_factor=1.05), Indicate(cols[2][0], color=SEA, scale_factor=1.05), run_time=1.2)
        c = self.cap(c, "The two controls use the same training code with the wrong rewards.", wait=2.0)
        self.play(FadeOut(VGroup(q, cols, c)), run_time=0.8)

        # 4. First lived run
        head = I("first 25-day lived run: free-day picks, trained vs untrained", 32, BG).to_edge(UP, buff=0.55)
        rows = [("D2  back row", 77, 78), ("D3  leave early", 100, 100)]
        bars = VGroup()
        for i, (name, tr, un) in enumerate(rows):
            y = 1.1 - i * 1.7
            lab = T(name, 30, BG).move_to([-4.6, y, 0])
            b1 = Rectangle(width=tr / 100 * 6, height=0.45, fill_color=GOLD, fill_opacity=1, stroke_width=0)
            b2 = Rectangle(width=un / 100 * 6, height=0.45, fill_color=MUTED, fill_opacity=1, stroke_width=0)
            b1.move_to([-2.6, y + 0.27, 0], aligned_edge=LEFT)
            b2.move_to([-2.6, y - 0.27, 0], aligned_edge=LEFT)
            n1 = T(f"{tr}%", 26, BG).next_to(b1, RIGHT, buff=0.15)
            n2 = T(f"{un}%", 26, BG).next_to(b2, RIGHT, buff=0.15)
            bars.add(VGroup(lab, b1, b2, n1, n2))
        key = VGroup(VGroup(Square(0.25, fill_color=GOLD, fill_opacity=1, stroke_width=0), T("trained", 26, BG)).arrange(RIGHT, buff=0.15),
                     VGroup(Square(0.25, fill_color=MUTED, fill_opacity=1, stroke_width=0), T("untrained", 26, BG)).arrange(RIGHT, buff=0.15)
                     ).arrange(RIGHT, buff=0.6).next_to(head, DOWN, buff=0.35)
        mmlu = T("general ability (MMLU, 200 questions): 75.0 before, 75.0 after", 30, BG).move_to([0, -1.85, 0])
        self.play(FadeIn(head), FadeIn(key))
        self.play(*[GrowFromEdge(b[1], LEFT) for b in bars], *[GrowFromEdge(b[2], LEFT) for b in bars],
                  *[FadeIn(b[0]) for b in bars], run_time=1.4)
        self.play(*[FadeIn(b[3]) for b in bars], *[FadeIn(b[4]) for b in bars])
        c = self.cap(None, "99 decisions, 25 trained nights. The picks match the untrained model.", wait=1.6)
        self.play(FadeIn(mmlu))
        c = self.cap(c, "So it mostly measured the prior. That is the honest first result.", wait=2.0, color=CORAL)
        c = self.cap(c, "Next: more exploration, and flipped and shuffled worlds.", wait=2.4)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)
        a = T("Kokopelli", 64, BG)
        b = I("kokopelli-labs.com  ·  github.com/jaycewalzer1/kokopelli", 32, BG).next_to(a, DOWN, buff=0.35)
        self.play(FadeIn(a), run_time=0.9)
        self.play(FadeIn(b), run_time=0.7)
        self.wait(2.4)

    @staticmethod
    def _edge(a, b):
        va = b.get_center() - a.get_center()
        if abs(va[0]) > abs(va[1]):
            s = RIGHT if va[0] > 0 else LEFT
            return a.get_edge_center(s) + s * 0.1, b.get_edge_center(-s) - s * 0.1
        s = UP if va[1] > 0 else DOWN
        return a.get_edge_center(s) + s * 0.1, b.get_edge_center(-s) - s * 0.1
