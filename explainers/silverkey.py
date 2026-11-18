"""SilverKey: ranking homes per buyer by blending an embedding score and an LLM score.

Style: a clay 3D neighbourhood with an orbiting camera (who ranks where), then a flat chart of how
the per-user blend is learned, then the real app's preference screen from the local demo run.

Facts from jaycewalzer1/SilverKey-Inc, Server/app/services/search/home_matching/:
embeddings/scorer.py (cosine similarity, raised to the power 0.2 to spread scores),
config/settings.py (all-MiniLM-L6-v2, 384 dimensions), postprocessing/weight_learner.py
(L2 logistic regression, C=1.0, features [embedding_score, llm_score], label = liked;
|coefficients| normalised to blend weights), weight_training_data.py (at least 10 impressions and
1 like), weight_service.py (retrain after 10 new impressions; cohort fallback),
cohort_assigner.py (cohorts by budget, age, zip prefix, home type).
The house scores and the scatter of likes are illustrative, not production data.

Scenes: SkA (3D), SkB (2D), SkC (real screen). Render each, then concatenate.
"""
import os

from style import *

MEDIA = os.path.join(HERE, "media", "silverkey")
GROUND = interpolate_color(ManimColor(BG), ManimColor(INK), 0.07)
ROOF = interpolate_color(ManimColor(DRIFT), ManimColor(BG), 0.35)


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


def house(at, w=1.1, d=1.0, h=0.7):
    """Clay house: a box with a gable roof (a square prism turned 45 degrees, half sunk)."""
    body = clay(Prism(dimensions=[w, d, h]), DRIFT).move_to(at + np.array([0, 0, h / 2]))
    side = (d + 0.1) / np.sqrt(2)
    roof = clay(Prism(dimensions=[w + 0.12, side, side]), ROOF).rotate(PI / 4, axis=RIGHT)
    roof.move_to(at + np.array([0, 0, h]))
    return VGroup(body, roof)


# a 4 x 3 block; illustrative per-home scores (embedding similarity, LLM compatibility), 0-1
GRID = [(x, y) for y in (2.4, 0.0, -2.4) for x in (-4.2, -1.4, 1.4, 4.2)]
EMB = [0.82, 0.55, 0.71, 0.40, 0.90, 0.62, 0.35, 0.77, 0.50, 0.68, 0.85, 0.30]
LLM = [0.45, 0.80, 0.60, 0.88, 0.40, 0.72, 0.65, 0.35, 0.92, 0.58, 0.50, 0.70]


def blend(we):
    return [we * e + (1 - we) * l for e, l in zip(EMB, LLM)]


def bar(at, value, color, dx):
    h = max(value * 2.6, 0.05)
    return clay(Prism(dimensions=[0.22, 0.22, h]), color).move_to(at + np.array([0.85 + dx, 0, h / 2]))


class SkA(Explainer3D):
    def construct(self):
        title = T("SilverKey", 72)
        sub = I("ranking homes for one buyer at a time", 34, MUTED).next_to(title, DOWN, buff=0.35)
        rule = Line(LEFT * 0.9, RIGHT * 0.9, color=GOLD, stroke_width=2).next_to(sub, DOWN, buff=0.45)
        self.flat(title, sub, rule)
        self.play(FadeIn(title, shift=UP * 0.15), run_time=1.2)
        self.play(FadeIn(sub), Create(rule), run_time=1)
        self.wait(1.2)
        self.play(FadeOut(VGroup(title, sub, rule)), run_time=0.8)

        self.set_camera_orientation(phi=52 * DEGREES, theta=-100 * DEGREES, zoom=0.58)
        # the ground is one slab per lot: the 3D camera depth-sorts each solid by its centre, so a
        # single big slab would be drawn over the far row of houses
        ground = VGroup(*[clay(Prism(dimensions=[2.8, 2.4, 0.08]), GROUND).move_to([x, y, -0.06]) for x, y in GRID])
        streets = VGroup(*[clay(Prism(dimensions=[13, 0.35, 0.02]), interpolate_color(ManimColor(BG), ManimColor(INK), 0.13))
                           .move_to([0, y, -0.005]) for y in (1.2, -1.2)])
        houses = VGroup(*[house(np.array([x, y, 0])) for x, y in GRID])
        self.add(ground, streets)
        cap = self.say(None, "Every listing a buyer could see gets a score for that buyer.", wait=0.2)
        self.play(LaggedStart(*[GrowFromPoint(h, h.get_bottom()) for h in houses], lag_ratio=0.07), run_time=2.4)
        self.begin_ambient_camera_rotation(rate=0.02)

        # two signals per home
        pts = [np.array([x, y, 0]) for x, y in GRID]
        e_bars = VGroup(*[bar(p, v, SEA, -0.14) for p, v in zip(pts, EMB)])
        l_bars = VGroup(*[bar(p, v, INK, 0.14) for p, v in zip(pts, LLM)])
        key = VGroup(T("embedding similarity", 30, SEA), T("LLM compatibility", 30, INK)).arrange(RIGHT, buff=0.8).to_edge(UP, buff=0.5)
        self.flat(key)
        cap = self.say(cap, "One: how close the buyer's profile and the listing sit in embedding space.", wait=0.1)
        self.play(FadeIn(key[0]), LaggedStart(*[GrowFromEdge(b, IN) for b in e_bars], lag_ratio=0.05), run_time=2)
        self.wait(1.2)
        cap = self.say(cap, "Two: an LLM's read of how well the home fits what the buyer said.", wait=0.1)
        self.play(FadeIn(key[1]), LaggedStart(*[GrowFromEdge(b, IN) for b in l_bars], lag_ratio=0.05), run_time=2)
        self.wait(1.5)

        # blend per user: buyer A leans on the embedding, buyer B on the LLM
        def show_blend(we, label, cap):
            f = blend(we)
            top = sorted(range(12), key=lambda i: -f[i])[:3]
            gold = VGroup(*[bar(p, v, GOLD, 0) for p, v in zip(pts, f)])
            tag = T(label, 32, GOLD).to_edge(UP, buff=0.5)
            self.flat(tag)
            cap = self.say(cap, f"Blended with this buyer's own weights: {we:.0%} embedding, {1 - we:.0%} LLM.", GOLD, wait=0.1)
            self.play(FadeIn(tag), run_time=0.4)
            self.play(LaggedStart(*[GrowFromEdge(b, IN) for b in gold], lag_ratio=0.04), run_time=1.6)
            self.play(*[houses[i].animate.set_fill(GOLD).shift(OUT * 0.35) for i in top], run_time=0.8)
            self.wait(1.8)
            return gold, tag, top, cap

        self.play(FadeOut(key), FadeOut(e_bars), FadeOut(l_bars), run_time=0.6)
        gold, tag, top, cap = show_blend(0.8, "buyer A: top three", cap)
        self.play(FadeOut(gold), FadeOut(tag), *[houses[i][0].animate.set_fill(DRIFT).shift(IN * 0.35) for i in top],
                  *[houses[i][1].animate.set_fill(ROOF).shift(IN * 0.35) for i in top], run_time=0.6)
        gold, tag, top, cap = show_blend(0.3, "buyer B: same homes, different top three", cap)
        self.stop_ambient_camera_rotation()
        cap = self.say(cap, "Same listings, same two scores. The weights are what make it personal.", wait=1.8)
        self.play(FadeOut(cap), FadeOut(tag), run_time=0.6)


class SkB(Explainer):
    def construct(self):
        ax = Axes(x_range=[0, 1, 0.5], y_range=[0, 1, 0.5], x_length=6, y_length=4.6,
                  axis_config={"color": MUTED, "stroke_width": 2, "include_ticks": False}).shift(LEFT * 2.6 + UP * 0.3)
        xl = T("embedding score", 28, SEA).next_to(ax, DOWN, buff=0.25)
        yl = T("LLM score", 28, INK).rotate(PI / 2).next_to(ax, LEFT, buff=0.25)
        cap = self.say(None, "How the weights are learned: every home a buyer was shown is an example.", wait=0.2)
        self.play(Create(ax), FadeIn(xl), FadeIn(yl), run_time=1.2)

        # illustrative impressions for a buyer who mostly likes what the LLM liked
        rng = np.random.default_rng(3)
        pts = rng.uniform(0.05, 0.95, size=(34, 2))
        liked = (0.35 * pts[:, 0] + 0.65 * pts[:, 1] + rng.normal(0, 0.06, 34)) > 0.58
        dots = VGroup(*[Dot(ax.c2p(x, y), radius=0.08, color=GOLD if l else MUTED) for (x, y), l in zip(pts, liked)])
        legend = VGroup(VGroup(Dot(radius=0.08, color=GOLD), T("liked", 28, GOLD)).arrange(RIGHT, buff=0.15),
                        VGroup(Dot(radius=0.08, color=MUTED), T("passed", 28, MUTED)).arrange(RIGHT, buff=0.15)
                        ).arrange(RIGHT, buff=0.6).move_to(RIGHT * 4.2 + DOWN * 1.7)
        self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in dots], lag_ratio=0.03), FadeIn(legend), run_time=2)
        cap = self.say(cap, "An L2-regularised logistic regression predicts a like from the two scores.", wait=0.2)
        # boundary 0.35x + 0.65y = 0.58
        line = Line(ax.c2p(0.05, (0.58 - 0.35 * 0.05) / 0.65), ax.c2p(0.95, (0.58 - 0.35 * 0.95) / 0.65), color=GOLD, stroke_width=4)
        self.play(Create(line), run_time=1.5)

        # coefficients -> blend weights
        panel = VGroup(
            T("|w_embedding|  :  |w_LLM|", 30, INK),
            T("normalised to sum to 1", 26, MUTED),
            VGroup(T("0.35", 44, SEA), T("+", 36, MUTED), T("0.65", 44, INK)).arrange(RIGHT, buff=0.3),
        ).arrange(DOWN, buff=0.35).move_to(RIGHT * 4.2 + UP * 0.2)
        self.play(FadeIn(panel, shift=LEFT * 0.2), run_time=1.2)
        cap = self.say(cap, "Its two coefficients, made positive and normalised, become this buyer's blend.", wait=3.0)
        rules = VGroup(
            T("needs 10 impressions and 1 like", 28, MUTED),
            T("retrains after 10 new impressions", 28, MUTED),
            T("before that: a cohort's weights", 28, MUTED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to(RIGHT * 4.2 + UP * 2.6)
        cap = self.say(cap, "New buyers borrow weights from a cohort: budget, age, zip and home type.", wait=0.2)
        self.play(LaggedStart(*[FadeIn(r) for r in rules], lag_ratio=0.3), run_time=1.5)
        self.wait(3.5)


class SkC(Explainer):
    def construct(self):
        shot = ImageMobject(os.path.join(MEDIA, "preferences.png")).set_height(config.frame_height * 0.95)
        frame = SurroundingRectangle(shot, color=MUTED, stroke_width=2, buff=0.04)
        self.play(FadeIn(shot), FadeIn(frame), run_time=1.2)
        cap = self.caption("The real web app, run locally: the preferences that build the buyer's side.", INK)
        bg = BackgroundRectangle(cap, color=BG, fill_opacity=0.85, buff=0.2)
        bg.set_z_index(9); cap.set_z_index(10)
        self.play(FadeIn(bg), FadeIn(cap), run_time=0.7)
        self.play(Group(shot, frame).animate.scale(1.35).shift(LEFT * 1.4 + DOWN * 0.6), run_time=6, rate_func=linear)
        self.closing("SilverKey", "github.com/jaycewalzer1/SilverKey-Inc")
