"""Chess Concept Discovery, told on a 3D board: where does search spend its looks?

Numbers are from the repo README, run outputs/laptop-main (200 held-out forced mates).
"""
from style import *

LIGHT, DARK = "#D8CDB8", "#8C7A66"     # board squares: fog-sand and driftwood
SQ = 0.62                              # square size in scene units


def sq(file, rank):
    """Centre of a square, files a..h -> 0..7, ranks 1..8 -> 0..7."""
    return np.array([(file - 3.5) * SQ, (rank - 3.5) * SQ, 0])


def piece(file, rank, color, tall=0.55):
    base = Cylinder(radius=0.2, height=tall, direction=OUT, resolution=(1, 18), checkerboard_colors=False,
                    fill_color=color, fill_opacity=1, stroke_width=0)
    head = Sphere(radius=0.14, resolution=(10, 10), checkerboard_colors=False).set_color(color).set_opacity(1)
    head.set_stroke(width=0)
    base.move_to(sq(file, rank) + OUT * (0.06 + tall / 2))
    head.move_to(sq(file, rank) + OUT * (0.06 + tall + 0.1))
    return VGroup(base, head)


class ConceptDiscovery(Explainer3D):
    def construct(self):
        self.set_camera_orientation(phi=62 * DEGREES, theta=-62 * DEGREES, zoom=1.35)

        board = VGroup()
        for f in range(8):
            for r in range(8):
                c = DARK if (f + r) % 2 == 0 else LIGHT
                p = Prism(dimensions=[SQ, SQ, 0.12], fill_color=c, fill_opacity=1, stroke_width=0)
                p.move_to(sq(f, r))
                board.add(p)
        pieces = VGroup(
            piece(6, 0, INK, 0.62), piece(5, 1, INK, 0.4), piece(6, 1, INK, 0.4), piece(7, 1, INK, 0.4),
            piece(3, 4, INK, 0.7),
            piece(6, 7, "#33302C", 0.62), piece(5, 6, "#33302C", 0.4), piece(6, 6, "#33302C", 0.4),
            piece(7, 5, "#33302C", 0.4), piece(1, 6, "#33302C", 0.55),
        )

        title = self.flat(T("Concept Discovery", 64).to_edge(UP, buff=0.35))
        sub = self.flat(I("finding the move your own instincts rank low", 30, MUTED).next_to(title, DOWN, buff=0.15))
        self.play(FadeIn(board), run_time=1.5)
        self.play(LaggedStart(*[FadeIn(p, shift=IN * 0.3) for p in pieces], lag_ratio=0.08),
                  FadeIn(title), FadeIn(sub), run_time=2)
        self.begin_ambient_camera_rotation(rate=0.04)
        self.wait(2)
        self.play(FadeOut(title), FadeOut(sub))

        # The network's first guess: a column over each candidate target square
        targets = [(3, 6), (2, 5), (4, 6), (0, 3), (5, 4), (7, 6)]
        prior = [0.34, 0.24, 0.16, 0.12, 0.09, 0.05]
        sims_std = [0.46, 0.30, 0.14, 0.06, 0.03, 0.01]
        sims_div = [0.20, 0.13, 0.17, 0.16, 0.12, 0.22]

        def columns(values, mate_color=SEA):
            g = VGroup()
            for i, ((f, r), v) in enumerate(zip(targets, values)):
                h = max(v * 5, 0.04)
                col = Prism(dimensions=[SQ * 0.62, SQ * 0.62, h], stroke_width=0,
                            fill_color=(mate_color if i == 5 else SEA), fill_opacity=0.82)
                col.move_to(sq(f, r) + OUT * (0.06 + h / 2))
                g.add(col)
            return g

        cols = columns(prior)
        cap = self.say(None, "Before searching, a small network guesses which moves are good.", wait=0.2)
        self.play(LaggedStart(*[GrowFromPoint(c, c.get_center() + IN * c.height / 2) for c in cols], lag_ratio=0.12),
                  run_time=2)
        self.wait(1.4)
        cap = self.say(cap, "The move that actually mates is the one it ranked last.", GOLD, wait=0.2)
        self.play(Transform(cols, columns(prior, GOLD)), run_time=1)
        self.move_camera(phi=55 * DEGREES, zoom=1.7, frame_center=sq(6, 5), run_time=2.5)
        self.wait(0.8)

        cap = self.say(cap, "Standard search spends its looks where the guess was already high.", wait=0.2)
        self.move_camera(phi=62 * DEGREES, zoom=1.35, frame_center=ORIGIN, run_time=1.5)
        self.play(Transform(cols, columns(sims_std, GOLD)), run_time=2)
        self.wait(1.6)

        cap = self.say(cap, "Feature-diverse search sorts moves by what they do: quiet, captures, checks.", wait=0.6)
        cap = self.say(cap, "Each kind gets a turn, so the overlooked check finally gets a real look.", GOLD, wait=0.2)
        self.play(Transform(cols, columns(sims_div, GOLD)), run_time=2.2)
        self.move_camera(phi=48 * DEGREES, theta=-30 * DEGREES, zoom=1.6, frame_center=sq(6, 5), run_time=3)
        self.wait(1)
        self.stop_ambient_camera_rotation()

        # Results as a 3D bar chart where the board was
        self.play(FadeOut(VGroup(board, pieces, cols)), FadeOut(cap), run_time=1)
        self.set_camera_orientation(phi=68 * DEGREES, theta=-78 * DEGREES, zoom=0.85, frame_center=OUT * 1.6)
        budgets = ["256", "1024", "3072"]
        std, div = [23.5, 29.0, 35.0], [26.5, 32.5, 41.5]
        bars = VGroup()
        for i in range(3):
            for j, (vals, colr) in enumerate(((std, SEA), (div, GOLD))):
                h = vals[i] / 10
                b = Prism(dimensions=[0.7, 0.7, h], fill_color=colr, fill_opacity=0.9, stroke_width=0)
                b.move_to(np.array([(i - 1) * 2.4 + (j - 0.5) * 0.85 - 1.2, 0, h / 2]))
                bars.add(b)
        floor = Prism(dimensions=[8, 2.2, 0.06], fill_color="#33505F", fill_opacity=1, stroke_width=0).shift(IN * 0.03 + LEFT * 1.2)
        head = self.flat(I("share of 200 held-out mates solved, by search budget", 30, MUTED).to_edge(UP, buff=0.6))
        key = self.flat(VGroup(T("standard", 30, SEA), T("feature-diverse", 30, GOLD)).arrange(RIGHT, buff=0.8)
                        .next_to(head, DOWN, buff=0.3))
        self.play(FadeIn(floor), FadeIn(head), FadeIn(key))
        self.play(LaggedStart(*[GrowFromPoint(b, b.get_center() + IN * b.height / 2) for b in bars], lag_ratio=0.1),
                  run_time=2.4)
        nums = VGroup(*[T(f"{budgets[i]} sims:  {std[i]:g}%  →  {div[i]:g}%", 30, INK) for i in range(3)])
        nums.arrange(DOWN, buff=0.22, aligned_edge=LEFT).to_edge(RIGHT, buff=0.8).shift(DOWN * 0.2)
        self.add_fixed_in_frame_mobjects(nums)
        nums.set_opacity(0)
        self.begin_ambient_camera_rotation(rate=0.06)
        self.play(nums.animate.set_opacity(1), run_time=1.2)
        cap = self.say(None, "Same network, same budget. The gap widens with search, to +6.5 points at 3072.", wait=1.8)
        cap = self.say(cap, "At the main budget it is +3.5, but the 95% interval (−1.5 to +8.8) includes zero.", CORAL, wait=2.2)
        cap = self.say(cap, "So the pre-registered verdict is honest: promising, not yet proven.", wait=2.2)
        self.stop_ambient_camera_rotation()

        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1)
        a = self.flat(T("Concept Discovery", 46))
        b = self.flat(I("github.com/jaycewalzer1/ChessConceptDiscovery", 30, GOLD).next_to(a, DOWN, buff=0.4))
        self.play(FadeIn(a), FadeIn(b), run_time=1)
        self.wait(2.4)
