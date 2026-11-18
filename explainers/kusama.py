"""Kusama: a deterministic painting medium for an RL environment for art.

Everything shown is real: the six layers are the per-leaf masks from
`render --trace-masks` on examples/v1/tear-ransom.json, the hashes are from two separate
renders of that program, and the point cloud is a 3-D PCA of a 1,527-work stride sample of the
repo's CLIP ViT-B/32 corpus embeddings, with the novelty numbers computed exactly as
artist/reward.ts does (1 - cosine to the nearest of 19,791 embedded works).
Media lives in explainers/media/kusama/.
"""
import json

from style import *

M = os.path.join(HERE, "media", "kusama")
LAYERS = [("ground", "canvas ground #ddd8c8"), ("0000-slab", "slab · torn fragment"),
          ("0001-bird-a", "bird-a · fragment"), ("0002-bird-b", "bird-b · fragment"),
          ("0003-strip", "strip · hatched shard"), ("0004-clean", "clean · untorn shard"),
          ("0005-caption", "caption · text")]
HASH = "98367c32b9c8379d6d3cde9bfb3fcfb3ac81ebb1276cd4a4b1ab77c4ccb9d611"
NOVELTY = [("tear-ransom", 0.6907), ("spray-wall", 0.5889), ("clip-cut-paper", 0.7451), ("hill-feast", 0.7548)]


def img(name, h):
    m = ImageMobject(os.path.join(M, name))
    m.height = h
    return m


class Kusama(ThreeDScene):
    title = "Kusama"
    subtitle = "a painting medium that returns the same bytes every time"

    # The same helpers as style.Explainer, with every caption pinned to the frame.
    def setup(self):
        Explainer.setup(self)

    def play(self, *args, **kwargs):
        super().play(*args, **kwargs)
        for p in layout_problems(self.mobjects):
            if p not in self.problems:
                self.problems.append(p)

    def tear_down(self):
        if self.problems:
            print("LAYOUT PROBLEMS:\n  " + "\n  ".join(self.problems))
        super().tear_down()

    def flat(self, *mobs):
        self.add_fixed_in_frame_mobjects(*mobs)
        self.remove(*mobs)
        return mobs[0] if len(mobs) == 1 else VGroup(*mobs)

    def say(self, old, text, color=INK, wait=2.2):
        new = Explainer.caption(self, text, color)
        self.flat(new)
        if old is None:
            self.play(FadeIn(new, shift=UP * 0.1), run_time=0.7)
        else:
            self.play(FadeOut(old, shift=UP * 0.1), FadeIn(new, shift=UP * 0.1), run_time=0.7)
        self.wait(wait)
        return new

    def construct(self):
        # ---- title
        t = T(self.title, 72)
        s = I(self.subtitle, 34, MUTED).next_to(t, DOWN, buff=0.35)
        rule = Line(LEFT * 0.9, RIGHT * 0.9, color=GOLD, stroke_width=2).next_to(s, DOWN, buff=0.45)
        self.flat(t, s, rule)
        self.play(FadeIn(t, shift=UP * 0.15), run_time=1.2)
        self.play(FadeIn(s), Create(rule), run_time=1)
        self.wait(1.2)
        self.play(FadeOut(VGroup(t, s, rule)), run_time=0.8)

        # ---- 1. a picture is a tree of nodes: the real per-leaf layers, exploded in 3-D
        self.set_camera_orientation(phi=66 * DEGREES, theta=-62 * DEGREES, zoom=1.1)
        planes = []
        for i, (name, _) in enumerate(LAYERS):
            f = "layer-ground.png" if name == "ground" else f"layer-{name}.png"
            p = img(f, 4.6)
            p.move_to(RIGHT * 1.6 + IN * 0.3)
            planes.append(p)
        labels = VGroup(*[T(lab, 26, MUTED) for _, lab in LAYERS]).arrange(UP, aligned_edge=LEFT, buff=0.22)
        labels.to_corner(UL, buff=0.6).shift(DOWN * 0.3)
        head = I("examples/v1/tear-ransom.json", 28, SEA).next_to(labels, UP, buff=0.3, aligned_edge=LEFT)
        self.flat(labels, head)
        cap = self.say(None, "A picture here is a JSON program: a tree of typed nodes, no free code.", wait=0.2)
        self.play(FadeIn(head), FadeIn(planes[0]), FadeIn(labels[0]), run_time=1)
        for i in range(1, len(planes)):
            planes[i].shift(OUT * 0.65 * i)
            self.play(FadeIn(planes[i], shift=OUT * 0.3), FadeIn(labels[i]), run_time=0.55)
        cap = self.say(cap, "Each drawing node carries its own random key, so its marks never depend on its neighbours.", wait=0.3)
        self.begin_ambient_camera_rotation(rate=0.16)
        self.wait(4.5)
        self.stop_ambient_camera_rotation()
        cap = self.say(cap, "p5 and p5.brush draw it in a pinned headless Chromium, on software WebGL.", wait=0.2)
        self.move_camera(phi=0, theta=-90 * DEGREES, zoom=1,
                         added_anims=[p.animate.move_to(RIGHT * 1.6) for p in planes], run_time=2.6)
        self.wait(1.2)
        self.play(FadeOut(labels), FadeOut(head), FadeOut(cap), *[FadeOut(p) for p in planes[:-1]], run_time=0.8)
        final = planes[-1]

        # ---- 2. the same bytes, twice
        a = img("tear-ransom.png", 4.4).move_to(LEFT * 3.2 + UP * 0.55)
        b = img("tear-ransom.png", 4.4).move_to(RIGHT * 3.2 + UP * 0.55)
        self.add(a)
        self.remove(final)
        ha = T(HASH[:16] + "…", 28, GOLD).next_to(a, DOWN, buff=0.25)
        hb = T(HASH[:16] + "…", 28, GOLD).next_to(b, DOWN, buff=0.25)
        la = I("first render", 26, MUTED).next_to(a, UP, buff=0.2)
        lb = I("fresh browser, again", 26, MUTED).next_to(b, UP, buff=0.2)
        self.play(FadeIn(la), FadeIn(ha), run_time=0.8)
        self.play(FadeIn(b, shift=LEFT * 0.4), FadeIn(lb), run_time=1)
        self.play(FadeIn(hb), run_time=0.8)
        eq = T("=", 72, GOLD).move_to(UP * 0.55)
        self.play(FadeIn(eq, scale=1.3))
        cap = self.say(None, "Rendered twice, canonical.png has the same sha256, byte for byte.", GOLD, wait=2.2)
        self.play(*[FadeOut(m) for m in [a, b, ha, hb, la, lb, eq, cap]], run_time=0.8)

        # how: repeat until two renders agree
        boxes = VGroup(*[RoundedRectangle(corner_radius=0.12, width=2.6, height=1.0, stroke_color=SEA, stroke_width=2.5,
                                          fill_color=BG, fill_opacity=1) for _ in range(3)]).arrange(RIGHT, buff=1.2).shift(UP * 0.7)
        words = ["render", "hash", "same as last?"]
        bl = VGroup(*[T(w, 32).move_to(bx) for w, bx in zip(words, boxes)])
        arrows = VGroup(Arrow(boxes[0].get_right(), boxes[1].get_left(), buff=0.1, color=MUTED, stroke_width=3),
                        Arrow(boxes[1].get_right(), boxes[2].get_left(), buff=0.1, color=MUTED, stroke_width=3))
        back = CurvedArrow(boxes[2].get_bottom() + DOWN * 0.05, boxes[0].get_bottom() + DOWN * 0.05, angle=-PI / 2.4, color=CORAL)
        no = T("no: render again", 28, CORAL).next_to(back, DOWN, buff=0.1)
        yes = Arrow(boxes[2].get_top(), boxes[2].get_top() + UP * 1.1, buff=0.1, color=GOLD, stroke_width=3)
        yl = T("yes: return it", 28, GOLD).next_to(yes, RIGHT, buff=0.2)
        cap = self.say(None, "Three sources of drift had to be removed, so it never trusts a single render.", wait=0.2)
        self.play(LaggedStart(*[AnimationGroup(Create(bx), FadeIn(w)) for bx, w in zip(boxes, bl)], lag_ratio=0.3),
                  Create(arrows), run_time=1.6)
        self.play(Create(back), FadeIn(no), run_time=1)
        self.play(GrowArrow(yes), FadeIn(yl), run_time=0.8)
        cap = self.say(cap, "The browser warms up the same way, until two frames agree.", wait=2)
        self.play(*[FadeOut(m) for m in [boxes, bl, arrows, back, no, yes, yl, cap]], run_time=0.8)

        # ---- 3. why an RL environment needs this
        states = VGroup()
        for i in range(4):
            card = RoundedRectangle(corner_radius=0.1, width=2.0, height=2.5, stroke_color=SEA, stroke_width=2.5)
            states.add(card)
        states.arrange(RIGHT, buff=1.1).shift(UP * 1.0)
        thumbs = Group(*[img(f"step{i}.png", 2.2).move_to(c) for i, c in enumerate(states)])
        sl = VGroup(*[T(f"program {i}", 26, MUTED).next_to(c, UP, buff=0.15) for i, c in enumerate(states)])
        eds = VGroup(*[Arrow(states[i].get_right(), states[i + 1].get_left(), buff=0.08, color=DRIFT, stroke_width=3)
                       for i in range(3)])
        el = VGroup(*[T("edit", 26, DRIFT).next_to(e, UP, buff=0.08) for e in eds])
        log = VGroup(*[RoundedRectangle(corner_radius=0.06, width=2.0, height=0.5, stroke_color=GOLD, stroke_width=2)
                       .next_to(c, DOWN, buff=0.55) for c in states])
        links = VGroup(*[Line(log[i].get_right(), log[i + 1].get_left(), color=GOLD, stroke_width=2) for i in range(3)])
        ll = T("studio.jsonl, each line hashed with the one before", 26, GOLD).next_to(log, DOWN, buff=0.25)
        cap = self.say(None, "An agent paints by sending typed, bounded edits to the program. Nothing else can change it.", wait=0.2)
        self.play(Create(states[0]), FadeIn(thumbs[0]), FadeIn(sl[0]), run_time=0.8)
        for i in range(3):
            self.play(GrowArrow(eds[i]), FadeIn(el[i]), Create(states[i + 1]), FadeIn(thumbs[i + 1]), FadeIn(sl[i + 1]),
                      run_time=0.7)
        self.play(LaggedStart(*[Create(x) for x in log], lag_ratio=0.2), Create(links), FadeIn(ll), run_time=1.4)
        cap = self.say(cap, "Each step is logged, and a finished run replays byte for byte with the model unplugged.", wait=0.4)
        sweep = SurroundingRectangle(states[0], color=GOLD, buff=0.08, stroke_width=4)
        self.play(Create(sweep), run_time=0.5)
        for i in range(1, 4):
            self.play(sweep.animate.move_to(states[i]), run_time=0.5)
        cap = self.say(cap, "So a reward can be recomputed later from the record alone, and checked.", GOLD, wait=2)
        self.play(*[FadeOut(m) for m in [states, thumbs, sl, eds, el, log, links, ll, sweep, cap]], run_time=0.8)

        # ---- 4. novelty against ~20K museum works, in CLIP space
        d = json.load(open(os.path.join(M, "pca3.json")))
        pts = d["corpus"]
        cloud = VGroup()
        for k, (x, y, z) in enumerate(pts[::2]):
            cloud.add(Dot3D(point=[x * 1.35, y * 1.35, z * 1.35], radius=0.04, color=MUTED, resolution=(3, 3)))
        nn_i = d["nn"].index("met-442940")
        nn = Dot3D(point=[c * 1.35 for c in pts[nn_i]], radius=0.11, color=SEA)
        me = Dot3D(point=[c * 1.35 for c in d["renders"]["tear-ransom"]], radius=0.14, color=GOLD)
        self.set_camera_orientation(phi=68 * DEGREES, theta=-40 * DEGREES, zoom=1.0)
        cap = self.say(None, "About 20,000 public-domain works from three museums, embedded with CLIP.", wait=0.2)
        self.play(LaggedStart(*[FadeIn(p) for p in cloud], lag_ratio=0.001), run_time=2)
        self.begin_ambient_camera_rotation(rate=0.2)
        self.wait(1.5)
        cap = self.say(cap, "A finished painting is embedded too, and found its nearest neighbour.", wait=0.2)
        self.play(FadeIn(me, scale=2), run_time=0.8)
        link = Line(me.get_center(), nn.get_center(), color=GOLD, stroke_width=5)
        self.play(FadeIn(nn), Create(link), run_time=1)
        self.wait(2.5)
        self.stop_ambient_camera_rotation()
        self.play(FadeOut(cloud), FadeOut(me), FadeOut(nn), FadeOut(link), FadeOut(cap), run_time=0.8)
        self.set_camera_orientation(phi=0, theta=-90 * DEGREES, zoom=1)

        r = img("tear-ransom.png", 4.2).move_to(LEFT * 3.0 + UP * 0.7)
        n = img("near-tear-ransom.jpg", 4.2).move_to(RIGHT * 3.0 + UP * 0.7)
        rl = I("tear-ransom", 26, MUTED).next_to(r, UP, buff=0.18)
        nl = I("nearest: Textile Fragment, The Met", 26, MUTED).next_to(n, UP, buff=0.18)
        cos = T("cosine 0.69", 34, SEA).move_to(UP * 0.7)
        self.play(FadeIn(r), FadeIn(rl), run_time=0.8)
        self.play(FadeIn(n), FadeIn(nl), FadeIn(cos), run_time=0.8)
        cap = self.say(None, "Novelty is one minus that cosine: 0.31. Above 0.95 counts as a copy.", GOLD, wait=2.2)
        self.play(*[FadeOut(m) for m in [r, n, rl, nl, cos, cap]], run_time=0.7)

        # all four demo renders, one bar each
        bars = Group()
        for i, (name, c) in enumerate(NOVELTY):
            th = img(f"{name}.png", 2.0)
            th.move_to(LEFT * 4.5 + RIGHT * 3.0 * i + UP * 1.75)
            v = 1 - c
            bar = Rectangle(width=1.0, height=v * 5.5, fill_color=GOLD, fill_opacity=0.9, stroke_width=0)
            bar.move_to([th.get_x(), -2.35 + v * 2.75, 0])
            num = T(f"{v:.2f}", 30, GOLD).next_to(bar, RIGHT, buff=0.15)
            bars.add(Group(th, bar, num))
        cap = self.say(None, "The four paintings rendered in the demo, scored against the corpus.", wait=0.2)
        self.play(LaggedStart(*[FadeIn(b[0]) for b in bars], lag_ratio=0.15), run_time=1.2)
        self.play(*[GrowFromEdge(b[1], DOWN) for b in bars], *[FadeIn(b[2]) for b in bars], run_time=1.2)
        self.wait(2.2)

        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)
        a = T("Kusama", 44)
        b2 = I("github.com/jaycewalzer1/kusama", 30, GOLD).next_to(a, DOWN, buff=0.4)
        self.flat(a, b2)
        self.play(FadeIn(a), run_time=1)
        self.play(FadeIn(b2), run_time=0.8)
        self.wait(2.5)
