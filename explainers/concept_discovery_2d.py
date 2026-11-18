"""Chess Concept Discovery: does feature-diverse search find moves the policy ranks low?

Numbers are from the repo README, run outputs/laptop-main (200 held-out forced mates).
"""
from style import *


class ConceptDiscovery(Explainer):
    title = "Concept Discovery"
    subtitle = "finding the move your own instincts rank low"

    def construct(self):
        self.title_card()

        # 1. The policy's prior over candidate moves
        moves = ["Qd5", "Nf3", "Rxe6", "Bc4", "h4", "Qxh7+"]
        prior = [0.34, 0.24, 0.16, 0.12, 0.09, 0.05]
        bars = VGroup()
        for i, (m, p) in enumerate(zip(moves, prior)):
            bar = Rectangle(width=0.9, height=p * 10, fill_color=SEA, fill_opacity=0.85, stroke_width=0)
            bar.move_to(RIGHT * (i - 2.5) * 1.5, aligned_edge=DOWN).shift(DOWN * 0.9)
            lab = T(m, 28, MUTED).next_to(bar, DOWN, buff=0.2)
            bars.add(VGroup(bar, lab))
        head = I("the network's first guess", 34, MUTED).to_edge(UP, buff=0.7)
        cap = self.say(None, "A small chess network ranks every legal move before it searches.", wait=0.3)
        self.play(FadeIn(head), LaggedStart(*[GrowFromEdge(b[0], DOWN) for b in bars], lag_ratio=0.12),
                  LaggedStart(*[FadeIn(b[1]) for b in bars], lag_ratio=0.12), run_time=2)
        self.wait(1.5)

        mate = bars[-1]
        star = T("mate in 3", 28, GOLD).next_to(mate[0], UP, buff=0.25)
        cap = self.say(cap, "Sometimes the move that actually wins is the one it ranked last.")
        self.play(mate[0].animate.set_fill(GOLD), FadeIn(star, shift=DOWN * 0.1))
        self.wait(1.2)

        # 2. Standard search follows the prior
        cap = self.say(cap, "Standard search spends its simulations where the guess was already high.", wait=0.4)
        sims = [0.46, 0.30, 0.14, 0.06, 0.03, 0.01]
        self.play(*[b[0].animate.stretch_to_fit_height(max(s * 8, 0.05)).align_to(b[0], DOWN)
                    for b, s in zip(bars, sims)],
                  head.animate.become(I("where standard search looks", 34, MUTED).to_edge(UP, buff=0.7)),
                  run_time=1.6)
        self.wait(1.6)

        # 3. Feature-diverse search: group moves by what they do, give each group a turn
        cap = self.say(cap, "Feature-diverse search groups moves by what they do, and gives each group a turn.", wait=0.4)
        groups = [(0, 2, "quiet"), (2, 4, "captures"), (4, 6, "checks & threats")]
        braces = VGroup()
        for a, b, name in groups:
            grp = VGroup(*[bars[i][1] for i in range(a, b)])
            br = Brace(grp, DOWN, color=DRIFT)
            braces.add(VGroup(br, T(name, 26, DRIFT).next_to(br, DOWN, buff=0.12)))
        self.play(FadeOut(cap), LaggedStart(*[FadeIn(x) for x in braces], lag_ratio=0.2), run_time=1.4)
        diverse = [0.20, 0.13, 0.17, 0.16, 0.12, 0.22]
        self.play(*[b[0].animate.stretch_to_fit_height(s * 8).align_to(b[0], DOWN) for b, s in zip(bars, diverse)],
                  head.animate.become(I("where feature-diverse search looks", 34, MUTED).to_edge(UP, buff=0.7)),
                  run_time=1.6)
        cap = self.say(None, "Now the last-ranked check gets enough look to be found.", GOLD, wait=1.8)

        self.play(*[FadeOut(m) for m in [bars, braces, star, head, cap]], run_time=0.8)

        # 4. Results across three search budgets
        ax = Axes(x_range=[0, 3, 1], y_range=[15, 45, 10], x_length=8, y_length=3.6,
                  axis_config={"color": MUTED, "stroke_width": 2, "include_ticks": False},
                  y_axis_config={"include_numbers": True, "font_size": 26, "include_ticks": True,
                                 "decimal_number_config": {"color": MUTED, "num_decimal_places": 0}}).shift(UP * 0.55 + RIGHT * 0.3)
        budgets = ["256", "1024", "3072"]
        std = [23.5, 29.0, 35.0]
        div = [26.5, 32.5, 41.5]
        xlab = VGroup(*[T(b, 26, MUTED).next_to(ax.c2p(i + 0.5, 15), DOWN, buff=0.2) for i, b in enumerate(budgets)])
        unit = I("simulations per move", 26, MUTED).next_to(xlab, DOWN, buff=0.15)
        ylab = I("% of 200 mates solved", 26, MUTED).next_to(ax, UP, buff=0.25).align_to(ax, LEFT)
        l1 = ax.plot_line_graph([0.5, 1.5, 2.5], std, line_color=SEA, vertex_dot_style={"color": SEA}, stroke_width=4)
        l2 = ax.plot_line_graph([0.5, 1.5, 2.5], div, line_color=GOLD, vertex_dot_style={"color": GOLD}, stroke_width=4)
        k1 = T("standard", 28, SEA).next_to(ax.c2p(2.5, 35), RIGHT, buff=0.25).shift(DOWN * 0.35)
        k2 = T("feature-diverse", 28, GOLD).next_to(ax.c2p(2.5, 41.5), RIGHT, buff=0.25).shift(LEFT * 1.2 + UP * 0.35)
        cap = self.caption("Same network, same budget. 200 held-out positions, checked by an exact mate verifier.")
        self.play(Create(ax), FadeIn(xlab), FadeIn(unit), FadeIn(ylab), FadeIn(cap), run_time=1.5)
        self.play(Create(l1), FadeIn(k1), run_time=1.4)
        self.play(Create(l2), FadeIn(k2), run_time=1.4)
        self.wait(2)
        gap = T("+6.5 pts", 30, GOLD).next_to(ax.c2p(2.5, 38.25), RIGHT, buff=0.3)
        bracket = Line(ax.c2p(2.5, 35), ax.c2p(2.5, 41.5), color=GOLD, stroke_width=2)
        self.play(Create(bracket), FadeIn(gap), k2.animate.shift(LEFT * 0.2))
        cap = self.say(cap, "The gap grows with more search. At the main budget it is +3.5 points.", wait=2)
        cap = self.say(cap, "But the 95% interval, -1.5 to +8.8, still includes zero.", CORAL, wait=2.2)
        cap = self.say(cap, "So the pre-registered verdict is honest: promising, not yet proven.", wait=2.4)

        self.closing("Concept Discovery", "github.com/jaycewalzer1/ChessConceptDiscovery")
