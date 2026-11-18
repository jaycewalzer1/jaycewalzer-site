"""Injectable PrEP for people experiencing homelessness: what the microsimulation found.

Style: a clay 3D population that the camera circles while infections spread, injections protect
and infections keep arriving from outside; then flat charts of the three findings intercut with
the repo's own regenerated figures (python -m prep_model.writeup, run 2026-11-17).

All numbers are from the README of jaycewalzer1/prep-model, and the dev run reproduced them
(5-year ICERs, break-even table, elimination ladder). The 3D figures are a stand-in for the
5,000-person cohort; who turns which colour in it is illustrative.

Scenes: PrA (3D), PrB (2D + real figures). Render each, then concatenate.
"""
import os

from style import *

MEDIA = os.path.join(HERE, "media", "prep-model")
GROUND = interpolate_color(ManimColor(BG), ManimColor(INK), 0.07)


def clay(mob, color):
    mob.set_fill(color, 1).set_stroke(width=0)
    return mob


class Explainer3D(ThreeDScene):
    """style.Explainer for a ThreeDScene: captions stay fixed in frame; lint checks only those."""

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
        grp = VGroup(BackgroundRectangle(new, color=BG, fill_opacity=0.8, buff=0.18), new)
        self.flat(grp)
        if old is None:
            self.play(FadeIn(grp, shift=UP * 0.1), run_time=0.7)
        else:
            self.play(FadeOut(old), FadeIn(grp, shift=UP * 0.1), run_time=0.7)
        self.wait(wait)
        return grp


def person(at):
    body = clay(Prism(dimensions=[0.26, 0.2, 0.5]), DRIFT).move_to(at + np.array([0, 0, 0.25]))
    head = clay(Cube(side_length=0.2), DRIFT).move_to(at + np.array([0, 0, 0.64]))
    return VGroup(body, head)


def paint(p, color):
    return [p[0].animate.set_fill(color), p[1].animate.set_fill(color)]


class PrA(Explainer3D):
    def construct(self):
        title = T("Injectable PrEP", 72)
        sub = I("a microsimulation of who gets protected, and at what price", 34, MUTED).next_to(title, DOWN, buff=0.35)
        rule = Line(LEFT * 0.9, RIGHT * 0.9, color=GOLD, stroke_width=2).next_to(sub, DOWN, buff=0.45)
        self.flat(title, sub, rule)
        self.play(FadeIn(title, shift=UP * 0.15), run_time=1.2)
        self.play(FadeIn(sub), Create(rule), run_time=1)
        self.wait(1.2)
        self.play(FadeOut(VGroup(title, sub, rule)), run_time=0.8)

        self.set_camera_orientation(phi=64 * DEGREES, theta=-70 * DEGREES, zoom=0.7)
        rng = np.random.default_rng(11)
        cells = [(x, y) for x in np.linspace(-4.6, 4.6, 10) for y in np.linspace(-3.2, 3.2, 7)]
        spots = [np.array([x + rng.uniform(-0.2, 0.2), y + rng.uniform(-0.2, 0.2), 0]) for x, y in cells]
        # one ground tile per person: the 3D camera depth-sorts solids by centre, and one big slab
        # would be drawn over the far rows
        ground = VGroup(*[clay(Prism(dimensions=[1.03, 1.08, 0.08]), GROUND).move_to([x, y, -0.05]) for x, y in cells])
        people = VGroup(*[person(s) for s in spots])
        self.add(ground)
        cap = self.say(None, "Adults experiencing homelessness in one catchment, simulated week by week.", wait=0.2)
        self.play(LaggedStart(*[FadeIn(p, shift=OUT * 0.3) for p in people], lag_ratio=0.01), run_time=2)
        self.begin_ambient_camera_rotation(rate=0.06)
        cap = self.say(cap, "Most inputs are hypothetical: a structure for a decision, not an answer.", MUTED, wait=1.4)

        order = rng.permutation(len(people))
        # usual care: infections spread, some arrive from outside
        cap = self.say(cap, "Under usual care, infections spread through mixing groups.", CORAL, wait=0.1)
        sick = list(order[:9])
        self.play(LaggedStart(*[AnimationGroup(*paint(people[i], CORAL)) for i in sick], lag_ratio=0.25), run_time=3)
        arrivals = VGroup(*[person(np.array([6.4, y, 0])) for y in (-2.0, 0.4, 2.4)])
        for a in arrivals:
            a[0].set_fill(CORAL); a[1].set_fill(CORAL)
        cap = self.say(cap, "And some arrive from outside the population, already infected.", CORAL, wait=0.1)
        self.play(FadeIn(arrivals), run_time=0.6)
        self.play(arrivals.animate.shift(LEFT * 1.0), run_time=1.6)

        # the injection: protection spreads, infection slows
        cap = self.say(cap, "Long-acting injections protect whoever the programme can reach and keep.", SEA, wait=0.1)
        reached = [i for i in order[9:] if rng.uniform() < 0.62]
        self.play(LaggedStart(*[AnimationGroup(*paint(people[i], SEA)) for i in reached], lag_ratio=0.03), run_time=3)
        self.wait(1)
        cap = self.say(cap, "Even with unlimited outreach, coverage stops near 61%.", wait=1.6)
        cap = self.say(cap, "And most of the infections left arrive from outside.", CORAL, wait=1.0)
        self.stop_ambient_camera_rotation()
        self.move_camera(phi=50 * DEGREES, theta=-20 * DEGREES, zoom=0.9, frame_center=[3.5, 0, 0], run_time=3)
        self.wait(1.2)
        self.play(FadeOut(cap), run_time=0.5)


def kb(scene, path, cap_text, scale=1.18, shift=LEFT * 0.4, seconds=5.5):
    """Ken-burns push on one of the repo's regenerated figures."""
    img = ImageMobject(path)
    img.set_width(config.frame_width * 0.86)
    if img.height > config.frame_height * 0.78:
        img.set_height(config.frame_height * 0.78)
    img.move_to(UP * 0.35)
    card = BackgroundRectangle(img, color="#F7F4EE", fill_opacity=1, buff=0.25)
    cap = scene.caption(cap_text, INK)
    scene.play(FadeIn(card), FadeIn(img), FadeIn(cap), run_time=0.8)
    scene.play(Group(card, img).animate.scale(scale).shift(shift), run_time=seconds, rate_func=linear)
    scene.play(FadeOut(card), FadeOut(img), FadeOut(cap), run_time=0.6)


class PrB(Explainer):
    def construct(self):
        # finding 1: cost per QALY at 5 years, pairwise against usual care
        head = I("cost per QALY gained, 5 years", 32, MUTED).to_edge(UP, buff=0.6)
        arms = [("B  clinic lenacapavir", 205342, SEA), ("C  low-barrier lenacapavir", 468567, SEA),
                ("D  low-barrier cabotegravir", 389378, SEA), ("E  outreach, no injection", 84691, GOLD)]
        scale = 6.0 / 500000
        rows = VGroup()
        for k, (name, v, c) in enumerate(arms):
            y = 1.6 - k * 1.05
            lab = T(name, 30, c if c == GOLD else INK).move_to([-4.3, y, 0])
            b = Rectangle(width=v * scale, height=0.5, fill_color=c, fill_opacity=0.9, stroke_width=0)
            b.move_to([-1.9, y, 0], aligned_edge=LEFT)
            val = T(f"${v:,}", 28, c if c == GOLD else MUTED).next_to(b, RIGHT, buff=0.2)
            rows.add(VGroup(lab, b, val))
        wtp = DashedLine([-1.9 + 100000 * scale, 2.3, 0], [-1.9 + 100000 * scale, -1.9, 0], color=CORAL, stroke_width=2)
        wtp_l = T("$100k", 26, CORAL).next_to(wtp, UP, buff=0.12)
        cap = self.say(None, "Finding one: the cheapest win is the outreach itself, with no injection.", wait=0.2)
        self.play(FadeIn(head), LaggedStart(*[FadeIn(r[0]) for r in rows], lag_ratio=0.15), run_time=1.2)
        self.play(LaggedStart(*[GrowFromEdge(r[1], LEFT) for r in rows], lag_ratio=0.15),
                  LaggedStart(*[FadeIn(r[2]) for r in rows], lag_ratio=0.15), Create(wtp), FadeIn(wtp_l), run_time=2)
        cap = self.say(cap, "Showing up, testing and linking to care does much of the work the drug gets credit for.", wait=2.2)
        self.play(FadeOut(VGroup(head, rows, wtp, wtp_l, cap)), run_time=0.7)

        # finding 2: break-even dose price
        line = NumberLine(x_range=[-2000, 22000, 4000], length=12, color=MUTED, include_numbers=False).shift(UP * 0.4)
        ticks = VGroup(*[T(f"${v // 1000}k" if v else "$0", 26, MUTED).next_to(line.n2p(v), DOWN, buff=0.25)
                         for v in range(0, 22000, 4000)])
        span = Line(line.n2p(-443), line.n2p(20478), color=GOLD, stroke_width=10)
        lo = T("-$443", 30, GOLD).next_to(line.n2p(-443), UP, buff=0.35)
        hi = T("$20,478", 30, GOLD).next_to(line.n2p(20478), UP, buff=0.35)
        today = Triangle(color=INK, fill_color=INK, fill_opacity=1).scale(0.14).rotate(PI).next_to(line.n2p(14109), UP, buff=0.05)
        today_l = T("lenacapavir today: $14,109", 28, INK).next_to(today, UP, buff=0.75)
        head = I("break-even price per dose", 32, MUTED).to_edge(UP, buff=0.6)
        cap = self.say(None, "Finding two: the price that breaks even depends on the accounting.", wait=0.2)
        self.play(FadeIn(head), Create(line), FadeIn(ticks), run_time=1.2)
        self.play(Create(span), FadeIn(lo), FadeIn(hi), run_time=1.6)
        self.play(FadeIn(today), FadeIn(today_l), run_time=0.8)
        cap = self.say(cap, "Is a client who moves away a saving, or a cost that left the spreadsheet?", wait=2.0)
        self.play(FadeOut(VGroup(head, line, ticks, span, lo, hi, today, today_l, cap)), run_time=0.7)
        kb(self, os.path.join(MEDIA, "fig6_break_even_price.png"), "The model's own figure, regenerated from today's run.")

        # finding 3: elimination is not purchasable
        ax = Axes(x_range=[0, 4, 1], y_range=[0, 1.5, 0.5], x_length=6.5, y_length=4,
                  axis_config={"color": MUTED, "stroke_width": 2, "include_ticks": False},
                  y_axis_config={"include_numbers": True, "font_size": 26,
                                 "decimal_number_config": {"color": MUTED, "num_decimal_places": 1}}).shift(LEFT * 2.6 + UP * 0.2)
        steps = [("usual\ncare", 1.337), ("reach\nx1", 0.434), ("reach\nx4", 0.214), ("reach\nx16", 0.163)]
        dots = VGroup(*[Dot(ax.c2p(i + 0.5, v), radius=0.1, color=GOLD if i else CORAL) for i, (_, v) in enumerate(steps)])
        labs = VGroup(*[T(n.replace("\n", " "), 26, MUTED).next_to(ax.c2p(i + 0.5, 0), DOWN, buff=0.25)
                        for i, (n, _) in enumerate(steps)])
        path = VMobject(color=GOLD, stroke_width=4).set_points_as_corners([d.get_center() for d in dots])
        ylab = I("infections per 100 person-years", 28, MUTED).next_to(ax, UP, buff=0.3).align_to(ax, LEFT)
        cap = self.say(None, "Finding three: more outreach flattens out well above zero.", wait=0.2)
        self.play(Create(ax), FadeIn(labs), FadeIn(ylab), run_time=1.2)
        self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in dots], lag_ratio=0.25), Create(path), run_time=2)

        # 54 infections left: 34 imported (63%), 20 internal
        left = 54
        ring = VGroup(
            AnnularSector(inner_radius=0.9, outer_radius=1.45, angle=TAU * 34 / left, start_angle=PI / 2, color=CORAL),
            AnnularSector(inner_radius=0.9, outer_radius=1.45, angle=TAU * 20 / left, start_angle=PI / 2 + TAU * 34 / left, color=MUTED),
        ).move_to(RIGHT * 4.3 + UP * 0.5)
        pct = T("63%", 44, CORAL).move_to(ring)
        rl = T("of the 54 left come from outside", 28, CORAL).next_to(ring, DOWN, buff=0.35)
        self.play(FadeIn(ring), FadeIn(pct), FadeIn(rl), run_time=1.2)
        cap = self.say(cap, "No amount of coverage inside the population reaches those. It is not for sale.", wait=2.2)
        self.play(FadeOut(VGroup(ax, labs, ylab, dots, path, ring, pct, rl, cap)), run_time=0.7)
        kb(self, os.path.join(MEDIA, "fig7_elimination.png"), "The elimination ladder, regenerated from today's run.", seconds=5)

        self.closing("Injectable PrEP model", "github.com/jaycewalzer1/prep-model")
