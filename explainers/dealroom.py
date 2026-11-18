"""DealRoom: a synthetic deal environment for tool-using agents, scored by a deterministic verifier.

Style: editorial and flat, built around the project's own research console. Screenshots of the
console (captured 2026-11-17 from `npm --prefix web run preview`) are pushed in slowly between
diagrams: a timeline of the flagship case that branches into a failed and a repaired run, the
verifier's eight predicates, and waffle charts of the recorded results.

Facts from jaycewalzer1/DealRoom: README (results, case table, engine and reward rules),
web/public/runs.json (flagship-failure / flagship-repaired steps and predicate diagnostics).
"""
import os

from style import *

STILLS = os.environ.get(
    "EXPLAINER_STILLS",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "stills"),
)


class DealRoom(Explainer):
    title = "DealRoom"
    subtitle = "a deal is only done when the record says so"

    def shot(self, name, label, push=1.18, shift=ORIGIN, secs=5.0):
        """A console screenshot as a card on the dark ground, pushed in slowly, with a small italic label."""
        img = ImageMobject(os.path.join(STILLS, name)).scale_to_fit_width(config.frame_width * 0.8).shift(UP * 0.35)
        edge = SurroundingRectangle(img, buff=0, color=MUTED, stroke_width=2)
        card = Group(img, edge)
        tag = I(label, 30, GOLD).to_edge(DOWN, buff=0.4)
        self.play(FadeIn(card, shift=UP * 0.15), run_time=0.8)
        self.play(FadeIn(tag), card.animate.scale(push).shift(shift), run_time=secs, rate_func=smooth)
        self.play(FadeOut(card), FadeOut(tag), run_time=0.7)

    def construct(self):
        self.title_card()
        self.shot("dr_results.png", "the research console: two local 8B models, same 48 tasks",
                  push=1.12, shift=LEFT * 0.5 + DOWN * 0.2, secs=4.5)
        self.timeline()
        self.shot("dr_step8.png", "the failed run in the console: proceeding is rejected",
                  push=1.12, shift=RIGHT * 0.3 + UP * 0.1, secs=4.0)
        self.verifier()
        self.results()
        self.learning()
        self.closing("DealRoom", "github.com/jaycewalzer1/DealRoom")

    # ------------------------------------------------------------------ the flagship case
    def timeline(self):
        terms = VGroup(T("eligible cost $12,000", 30, INK), T("buyer's limit $5,000", 30, INK),
                       T("seller offers $8,000 credit", 30, INK)).arrange(RIGHT, buff=0.9).to_edge(UP, buff=0.6)
        dots_sep = VGroup(*[Dot(radius=0.04, color=MUTED).move_to((terms[i].get_right() + terms[i + 1].get_left()) / 2)
                            for i in range(2)])
        cap = self.say(None, "Case 01, an inspection response: $12,000 of eligible cost.", wait=0.2)
        self.play(FadeIn(terms[0]), run_time=0.6)
        self.play(FadeIn(dots_sep[0]), FadeIn(terms[1]), run_time=0.6)
        self.play(FadeIn(dots_sep[1]), FadeIn(terms[2]), run_time=0.6)
        self.wait(0.8)

        # shared trunk: steps 1-7 of both runs (runs.json)
        y0 = UP * 0.5
        axis = Line(LEFT * 6.7 + y0, LEFT * 1.4 + y0, color=MUTED, stroke_width=3)
        trunk = [("read", "09:00"), ("ask", "09:05"), ("wait", "10:10"), ("negotiate", "10:15"), ("draft", "10:55")]
        nodes = VGroup()
        for i, (lab, t) in enumerate(trunk):
            p = axis.point_from_proportion(i / (len(trunk) - 1))
            d = Dot(p, radius=0.11, color=SEA)
            nodes.add(VGroup(d, T(lab, 26, INK).next_to(d, UP, buff=0.2), T(t, 24, MUTED).next_to(d, DOWN, buff=0.2)))
        cap = self.say(cap, "The agent reads evidence, negotiates, and drafts the credit.", wait=0.2)
        self.play(Create(axis), LaggedStart(*[FadeIn(n, shift=UP * 0.1) for n in nodes], lag_ratio=0.25), run_time=2.4)
        self.wait(0.6)

        # branch at the draft
        fork = nodes[-1][0].get_center()
        bad = Line(fork, fork + RIGHT * 2.2 + UP * 1.2, color=CORAL, stroke_width=4)
        bad_dot = Dot(bad.get_end(), radius=0.12, color=CORAL)
        bad_lab = T("proceed: rejected", 28, CORAL).next_to(bad_dot, RIGHT, buff=0.25)
        bad_t = T("11:00 · unsigned draft", 24, MUTED).next_to(bad_lab, DOWN, buff=0.12, aligned_edge=LEFT)
        cap = self.say(cap, "The scripted failure proceeds on the unsigned draft.", CORAL, wait=0.2)
        self.play(Create(bad), FadeIn(bad_dot), run_time=0.9)
        self.play(FadeIn(bad_lab), FadeIn(bad_t), run_time=0.6)
        cap = self.say(cap, "Unsigned, the credit counts as $0. Residual cost stays $12,000.", wait=1.6)

        dn = DOWN * 1.6
        good_pts = [fork, fork + RIGHT * 2.0 + dn, fork + RIGHT * 3.6 + dn, fork + RIGHT * 5.2 + dn, fork + RIGHT * 6.8 + dn]
        good = VMobject(color=GOLD, stroke_width=4).set_points_as_corners(good_pts)
        g_nodes = VGroup()
        for p, lab, t in zip(good_pts[1:], ["route", "signature 1", "signature 2", "proceed"],
                             ["11:00", "11:15", "12:00", "12:10"]):
            d = Dot(p, radius=0.11, color=GOLD)
            name = T(lab, 26, INK).next_to(d, DOWN, buff=0.2)
            g_nodes.add(VGroup(d, name, T(t, 24, MUTED).next_to(name, DOWN, buff=0.1)))
        cap = self.say(cap, "The repaired run routes that exact revision for both signatures first.", GOLD, wait=0.2)
        self.play(Create(good), LaggedStart(*[FadeIn(n) for n in g_nodes], lag_ratio=0.3), run_time=2.4)
        cap = self.say(cap, "Executed credit $8,000. Residual $4,000, inside the $5,000 limit.", wait=1.8)
        self.play(FadeOut(VGroup(terms, dots_sep, axis, nodes, bad, bad_dot, bad_lab, bad_t, good, g_nodes)),
                  FadeOut(cap), run_time=0.8)

    # ------------------------------------------------------------------ the verifier
    def verifier(self):
        preds = ["disposition", "authority", "revision_signatures", "effective_terms",
                 "deadline", "buyer_constraint", "supported_final_claims", "completed_attempt"]
        tiles = VGroup()
        for p in preds:
            box = RoundedRectangle(corner_radius=0.12, width=5.2, height=0.78, stroke_color=MUTED, stroke_width=2,
                                   fill_color=BG, fill_opacity=1)
            lab = T(p.replace("_", " "), 30, INK).move_to(box)
            tiles.add(VGroup(box, lab))
        tiles.arrange_in_grid(rows=4, cols=2, buff=(0.5, 0.28)).shift(UP * 0.55)
        head = I("eight checks on the final state, no LLM judge", 30, MUTED).to_edge(UP, buff=0.5)
        cap = self.say(None, "A deterministic Python verifier scores what the engine actually recorded.", wait=0.2)
        self.play(FadeIn(head), LaggedStart(*[FadeIn(t, shift=UP * 0.1) for t in tiles], lag_ratio=0.08), run_time=1.6)
        self.wait(0.6)
        score = T("1 of 8", 40, CORAL).next_to(tiles, DOWN, buff=0.35)
        cap = self.say(cap, "The failed run: only 'completed attempt' passes. Reward 0.", CORAL, wait=0.2)
        self.play(*[t[0].animate.set_fill(CORAL, 0.35).set_stroke(CORAL) for t in tiles[:7]],
                  tiles[7][0].animate.set_fill(SEA, 0.35).set_stroke(SEA), FadeIn(score), run_time=1.2)
        self.wait(1.6)
        score2 = T("8 of 8", 40, GOLD).move_to(score)
        cap = self.say(cap, "The repaired run passes all eight. Reward 1.", GOLD, wait=0.2)
        self.play(*[t[0].animate.set_fill(GOLD, 0.3).set_stroke(GOLD) for t in tiles], ReplacementTransform(score, score2),
                  run_time=1.2)
        self.wait(1.6)
        self.play(FadeOut(VGroup(tiles, head, score2)), FadeOut(cap), run_time=0.7)

    # ------------------------------------------------------------------ model comparison
    def waffle(self, counts, title, sub):
        """48 squares: gold success, coral scored failure, hollow unscored."""
        sq = VGroup()
        kinds = ["s"] * counts[0] + ["f"] * counts[1] + ["u"] * counts[2]
        for k in kinds:
            s = Square(0.36, stroke_width=2)
            if k == "s":
                s.set_fill(GOLD, 1).set_stroke(GOLD)
            elif k == "f":
                s.set_fill(CORAL, 0.75).set_stroke(CORAL, opacity=0)
            else:
                s.set_fill(BG, 0).set_stroke(MUTED)
            sq.add(s)
        sq.arrange_in_grid(rows=6, cols=8, buff=0.1)
        t = T(title, 36, INK).next_to(sq, UP, buff=0.3)
        s2 = T(sub, 30, GOLD).next_to(sq, DOWN, buff=0.3)
        return VGroup(t, sq, s2)

    def results(self):
        llama = self.waffle((1, 45, 2), "Llama 3.1 8B", "1 of 46 scored")
        qwen = self.waffle((13, 19, 16), "Qwen3 8B", "13 of 32 scored")
        pair = VGroup(llama, qwen).arrange(RIGHT, buff=1.8).shift(UP * 0.35)
        key = VGroup(*[VGroup(Square(0.26, stroke_width=2).set_fill(c, o).set_stroke(sc), T(n, 26, MUTED)).arrange(RIGHT, buff=0.15)
                       for c, o, sc, n in [(GOLD, 1, GOLD, "success"), (CORAL, 0.75, CORAL, "scored failure"),
                                           (BG, 0, MUTED, "unscored: budget limit or incomplete")]]).arrange(RIGHT, buff=0.5)
        key.next_to(pair, DOWN, buff=0.35)
        cap = self.say(None, "48 generated tasks, one attempt each, run locally through Ollama.", wait=0.2)
        self.play(FadeIn(llama[0]), FadeIn(qwen[0]), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(s, scale=0.5) for s in llama[1]], lag_ratio=0.015),
                  LaggedStart(*[FadeIn(s, scale=0.5) for s in qwen[1]], lag_ratio=0.015), run_time=2.0)
        self.play(FadeIn(llama[2]), FadeIn(qwen[2]), FadeIn(key), run_time=0.7)
        cap = self.say(cap, "Limits stay unscored, so the two rates cover different subsets.", wait=1.8)
        cap = self.say(cap, "Llama often treated negotiation as execution, or waited past the deadline.", wait=1.8)
        self.play(FadeOut(VGroup(pair, key)), FadeOut(cap), run_time=0.7)

    # ------------------------------------------------------------------ training
    def learning(self):
        rows = [("original workflow", 0, 64, "0 / 64"), ("clearer workflow", 0, 39, "0 / 39 scored"),
                ("+ SFT", 2, 64, "2 / 64"), ("+ SFT + RL", 2, 64, "2 / 64")]
        grp = VGroup()
        for name, k, n, txt in rows:
            lab = T(name, 30, INK)
            track = Rectangle(width=6.4, height=0.42, stroke_color=MUTED, stroke_width=1.5, fill_opacity=0)
            fill = Rectangle(width=max(6.4 * k / 64, 0.04), height=0.42, stroke_width=0, fill_color=GOLD if k else MUTED,
                             fill_opacity=1)
            val = T(txt, 28, GOLD if k else MUTED)
            grp.add(VGroup(lab, track, fill, val))
        for i, g in enumerate(grp):
            g[1].move_to(RIGHT * 0.6 + UP * (1.4 - 0.85 * i))
            g[2].align_to(g[1], LEFT).align_to(g[1], UP)
            g[0].next_to(g[1], LEFT, buff=0.4)
            g[3].next_to(g[1], RIGHT, buff=0.3)
        head = I("Llama 3.1 8B, MLX 4-bit LoRA · 64 sealed held-out tasks", 30, MUTED).to_edge(UP, buff=0.6)
        cap = self.say(None, "Then I trained Llama on the clarified workflow.", wait=0.2)
        self.play(FadeIn(head), LaggedStart(*[FadeIn(VGroup(g[0], g[1])) for g in grp], lag_ratio=0.15), run_time=1.4)
        self.play(*[GrowFromEdge(g[2], LEFT) for g in grp], LaggedStart(*[FadeIn(g[3]) for g in grp], lag_ratio=0.15),
                  run_time=1.4)
        cap = self.say(cap, "SFT and SFT followed by RL passed the same two of 64.", GOLD, wait=1.8)
        cap = self.say(cap, "On this small protocol, RL added no measured gain. The report says so.", wait=2.2)
        self.play(FadeOut(VGroup(grp, head)), FadeOut(cap), run_time=0.7)
