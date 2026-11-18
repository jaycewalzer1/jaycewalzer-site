"""Kusama Studio (Kusama_v2): frozen Qwen3-VL-8B directs frozen FLUX.2-klein-base-4B.

Style: real material from the repo (reference packet images, the actual scale-experiment masks)
pushed in slowly, between plain diagrams of the director/generator loop, lineage and review gate.
No model was run. Numbers are from docs/experiments/{director_verification,scale_experiment,
verification}.md and docs/operations/2026-09-08_overnight_handoff.md. The run images themselves
are in untracked artifacts/, so images in the diagrams are drawn as plain frames, not faked.
Media lives in explainers/media/kusama-studio/.
"""
from style import *

M = os.path.join(HERE, "media", "kusama-studio")


def img(name, h):
    m = ImageMobject(os.path.join(M, name))
    m.height = h
    return m


def frame(w=1.5, h=1.85, color=DRIFT, label=None):
    r = RoundedRectangle(corner_radius=0.06, width=w, height=h, stroke_color=color, stroke_width=2.5,
                         fill_color=color, fill_opacity=0.18)
    if label:
        return VGroup(r, T(label, 24, MUTED).move_to(r))
    return r


class KusamaStudio(Explainer):
    title = "Kusama Studio"
    subtitle = "one frozen model directs, another paints, a person decides"

    def construct(self):
        self.title_card()

        # 1. a question and sourced references (real packet images, slow push-in)
        codex = img("dresden-codex-sequence-01.jpg", 5.6).move_to(LEFT * 3.6 + UP * 0.45)
        whistle = img("maize-god-whistle.jpg", 4.2).move_to(RIGHT * 0.2 + UP * 0.45)
        q = I("“our history feels lost”", 40, GOLD).move_to(RIGHT * 4.6 + UP * 1.4)
        qs = T("the brief in packet-v3", 26, MUTED).next_to(q, DOWN, buff=0.2)
        n = T("12 sourced references", 30).next_to(qs, DOWN, buff=0.6)
        n2 = T("each with rights and a hash", 26, MUTED).next_to(n, DOWN, buff=0.15)
        cap = self.say(None, "A run starts from a question and a packet of sourced references.", wait=0.2)
        self.play(FadeIn(codex), FadeIn(whistle), run_time=1.2)
        self.play(FadeIn(q), FadeIn(qs), codex.animate.scale(1.05), whistle.animate.scale(1.05), run_time=2)
        self.play(FadeIn(n), FadeIn(n2), codex.animate.scale(1.03), run_time=1.6)
        cap = self.say(cap, "Dresden Codex, Library of Congress. Maize god whistle, The Met.", MUTED, wait=1.4)
        self.play(*[FadeOut(m) for m in [codex, whistle, q, qs, n, n2, cap]], run_time=0.8)

        # 2. the director / generator loop
        qbox = RoundedRectangle(corner_radius=0.15, width=3.6, height=1.5, stroke_color=SEA, stroke_width=3).move_to(LEFT * 4.6 + UP * 1.3)
        fbox = RoundedRectangle(corner_radius=0.15, width=4.0, height=1.5, stroke_color=GOLD, stroke_width=3).move_to(RIGHT * 4.6 + UP * 1.3)
        ql = VGroup(T("Qwen3-VL-8B", 32, SEA), I("frozen director", 26, MUTED)).arrange(DOWN, buff=0.1).move_to(qbox)
        fl = VGroup(T("FLUX.2-klein-base-4B", 28, GOLD), I("frozen generator", 26, MUTED)).arrange(DOWN, buff=0.1).move_to(fbox)
        prop = VGroup(RoundedRectangle(corner_radius=0.08, width=3.0, height=1.3, stroke_color=INK, stroke_width=2))
        prop.move_to(UP * 1.3)
        pl = VGroup(T("one concrete change", 26), T("+ its expected effect", 26, MUTED)).arrange(DOWN, buff=0.08).move_to(prop)
        a1 = Arrow(qbox.get_right(), prop.get_left(), buff=0.1, color=SEA, stroke_width=3)
        a2 = Arrow(prop.get_right(), fbox.get_left(), buff=0.1, color=GOLD, stroke_width=3)
        im = frame(label="image").move_to(DOWN * 1.2)
        a3 = CurvedArrow(fbox.get_bottom() + DOWN * 0.05, im[0].get_right() + RIGHT * 0.05, angle=-PI / 3, color=GOLD)
        a4 = CurvedArrow(im[0].get_left() + LEFT * 0.05, qbox.get_bottom() + DOWN * 0.05, angle=-PI / 3, color=SEA)
        cap = self.say(None, "Qwen looks at the references and the current image, and proposes one change.", wait=0.2)
        self.play(Create(qbox), FadeIn(ql), run_time=0.9)
        self.play(GrowArrow(a1), Create(prop), FadeIn(pl), run_time=1)
        self.wait(1)
        cap = self.say(cap, "FLUX makes or edits the image from Qwen's exact instruction.", wait=0.2)
        self.play(GrowArrow(a2), Create(fbox), FadeIn(fl), run_time=1)
        self.play(Create(a3), FadeIn(im), run_time=1)
        cap = self.say(cap, "Qwen inspects every new image before its next decision. No weights are trained.", wait=0.2)
        self.play(Create(a4), run_time=1)
        dot = Dot(color=INK, radius=0.09).move_to(qbox.get_right())
        path = VMobject().set_points_as_corners([qbox.get_right(), prop.get_left(), prop.get_right(), fbox.get_left()])
        self.play(MoveAlongPath(dot, path), run_time=1.2)
        self.play(MoveAlongPath(dot, a3), run_time=0.7)
        self.play(MoveAlongPath(dot, a4), run_time=0.7)
        self.play(FadeOut(dot), run_time=0.3)
        self.wait(0.8)

        # memory: the two models take turns on one 36 GB Mac
        loop = VGroup(qbox, ql, fbox, fl, prop, pl, a1, a2, a3, a4, im)
        self.play(FadeOut(loop), FadeOut(cap), run_time=0.8)
        bar = Rectangle(width=9, height=0.6, stroke_color=MUTED, stroke_width=2).move_to(UP * 0.2)
        unit = 9 / 36
        bl = T("36 GB unified memory", 26, MUTED).next_to(bar, DOWN, buff=0.2)
        qm = Rectangle(width=17.32 * unit, height=0.6, fill_color=SEA, fill_opacity=0.85, stroke_width=0).align_to(bar, LEFT).move_to(bar, coor_mask=[0, 1, 0])
        fm = Rectangle(width=13.12 * unit, height=0.6, fill_color=GOLD, fill_opacity=0.85, stroke_width=0).align_to(bar, LEFT).move_to(bar, coor_mask=[0, 1, 0])
        qml = T("Qwen, 17.32 GiB peak sample", 26, SEA).next_to(bar, UP, buff=0.2).align_to(bar, LEFT)
        fml = T("FLUX edit, 13.12 GiB peak sample", 26, GOLD).next_to(bar, UP, buff=0.2).align_to(bar, LEFT)
        cap = self.say(None, "They load one at a time: Qwen is released before FLUX loads.", wait=0.2)
        self.play(Create(bar), FadeIn(bl), run_time=0.8)
        self.play(GrowFromEdge(qm, LEFT), FadeIn(qml), run_time=1)
        self.wait(0.8)
        self.play(ReplacementTransform(qm, fm), ReplacementTransform(qml, fml), run_time=1.2)
        self.wait(1.4)
        self.play(*[FadeOut(m) for m in [bar, bl, fm, fml, cap]], run_time=0.8)

        # 3. a protected edit: the real masks from the scale experiment
        pm = img("person_mask.png", 4.0).move_to(LEFT * 4.2 + UP * 0.6)
        am = img("allowed_mask.png", 4.0).move_to(LEFT * 0.0 + UP * 0.6)
        pml = I("the hiker", 26, MUTED).next_to(pm, UP, buff=0.15)
        aml = I("the only pixels FLUX may touch", 26, MUTED).next_to(am, UP, buff=0.15)
        stats = VGroup(
            VGroup(T("height ratio", 28, MUTED), T("0.3365", 34, GOLD)).arrange(DOWN, aligned_edge=LEFT, buff=0.05),
            VGroup(T("repair patch", 28, MUTED), T("1.65% of the image", 34, GOLD)).arrange(DOWN, aligned_edge=LEFT, buff=0.05),
            VGroup(T("protected pixels changed", 28, MUTED), T("0 of 1,031,297", 34, GOLD)).arrange(DOWN, aligned_edge=LEFT, buff=0.05),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4).move_to(RIGHT * 4.4 + UP * 0.6)
        cap = self.say(None, "One experiment: Qwen directs shrinking a hiker to a third of its height.", wait=0.2)
        self.play(FadeIn(pm), FadeIn(pml), run_time=1)
        self.play(pm.animate.scale(1.04), run_time=1.2)
        cap = self.say(cap, "FLUX only repairs the background inside a mask, so the rest can be checked exactly.", wait=0.2)
        self.play(FadeIn(am), FadeIn(aml), run_time=1)
        self.play(LaggedStart(*[FadeIn(s, shift=LEFT * 0.2) for s in stats], lag_ratio=0.35), run_time=2)
        self.wait(2)
        self.play(*[FadeOut(m) for m in [pm, am, pml, aml, stats, cap]], run_time=0.8)

        # 4. lineage: every image is saved with its parent
        root = frame(0.9, 1.1, SEA).move_to(LEFT * 5.6 + UP * 0.4)
        lvl = []
        cols = [(-3.0, 6, MUTED), (0.0, 4, SEA), (2.7, 4, DRIFT), (5.3, 2, GOLD)]
        names = ["6 possibilities", "4 local edits", "4 protected edits", "2 finishing edits"]
        for (x, k, c) in cols:
            g = VGroup(*[frame(0.62, 0.76, c) for _ in range(k)]).arrange(DOWN, buff=0.14).move_to(RIGHT * x + UP * 0.4)
            lvl.append(g)
        heads = VGroup(*[T(nm, 26, MUTED).next_to(g, UP, buff=0.2) for nm, g in zip(names, lvl)])
        for h in heads:
            h.set_y(lvl[0].get_top()[1] + 0.35)
        edges = VGroup()
        parents = [root, lvl[0][1], lvl[0][1], lvl[2][0]]

        def link(a, b, c):
            return CubicBezier(a.get_right(), a.get_right() + RIGHT * 0.7, b.get_left() + LEFT * 0.7, b.get_left(),
                               stroke_color=c, stroke_width=2, stroke_opacity=0.8)
        cap = self.say(None, "Every proposal, mask, image and hash is saved with its parent.", wait=0.2)
        self.play(FadeIn(root), run_time=0.6)
        for i, g in enumerate(lvl):
            es = VGroup(*[link(parents[i], f, cols[i][2]) for f in g])
            edges.add(es)
            self.play(Create(es), LaggedStart(*[FadeIn(f) for f in g], lag_ratio=0.1), FadeIn(heads[i]), run_time=1.1)
        cap = self.say(cap, "One overnight episode saved 16 images this way: a lineage tree, nothing overwritten.", wait=1.6)
        note = I("counts from the handoff; branch layout schematic", 26, MUTED).move_to(DOWN * 2.62)
        self.play(FadeIn(note), run_time=0.5)
        self.wait(1)

        # 5. the human review gate
        tree = VGroup(root, *lvl, edges)
        self.play(FadeOut(heads), FadeOut(note), FadeOut(cap), run_time=0.6)
        self.play(tree.animate.scale(0.55).to_edge(LEFT, buff=0.5).shift(UP * 0.5), run_time=1)
        gate = Line(UP * 2.2, DOWN * 1.6, color=CORAL, stroke_width=6).move_to(RIGHT * 1.6 + UP * 0.3)
        gl = T("human review", 30, CORAL).next_to(gate, UP, buff=0.15)
        nxt = frame(1.1, 1.35, GOLD, "next parent").move_to(RIGHT * 4.6 + UP * 0.3)
        ar = Arrow(gate.get_center() + LEFT * 1.4, gate.get_center() + LEFT * 0.1, buff=0, color=MUTED, stroke_width=3)
        ar2 = Arrow(gate.get_center() + RIGHT * 0.1, nxt.get_left(), buff=0.1, color=GOLD, stroke_width=3)
        cap = self.say(None, "Nothing advances on the model's say-so. A person chooses what continues.", wait=0.2)
        self.play(Create(gate), FadeIn(gl), GrowArrow(ar), run_time=1)
        self.play(GrowArrow(ar2), FadeIn(nxt), run_time=1)
        cap = self.say(cap, "Model choices and human judgments are stored separately, bound to image hashes.", wait=2)
        q1 = I("“Does the smaller figure change the feeling of vastness?”", 30, INK).move_to(DOWN * 2.0 + RIGHT * 1.6)
        q2 = T("“yes it does”", 34, GOLD).next_to(q1, DOWN, buff=0.15)
        self.play(FadeOut(cap), FadeIn(q1), run_time=0.8)
        self.play(FadeIn(q2), run_time=0.8)
        self.wait(2.4)

        self.closing("Kusama Studio", "github.com/jaycewalzer1/Kusama_v2")
