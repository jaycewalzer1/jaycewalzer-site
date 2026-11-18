"""Rent Roll OCR (OM-Analyzer, 2024): how a scanned rent roll becomes rows in a comps database.

Style: documentary. The real scanned page (the synthetic sample used in the demo) lies on a desk in
3D and the camera drifts over it while a scan line reads it row by row; then a flat close-up of
one OCR line being rebuilt by the parser's actual rules; then the real results screen.

Facts from jaycewalzer1/rr-tool2: tenant_parser/exporter.py, rent_roll_parser.py (300 dpi render,
grayscale + sharpen + 2x contrast, tesseract --psm 6; keep only lines with a $ amount; split on
known tenant names; join "1" "850" into square feet; lease end matched to 3, 5 or 10 years; annual
rent checked against sq ft x PSF). The OCR line and the 7-in, 7-out result are from the local run
on 2026-11-17 (Lakeland_Commons_OM.pdf, a synthetic sample).

Scenes: RentA (3D), RentB (2D), RentC (real screen). Render each, then concatenate.
"""
import os

from style import *

MEDIA = os.path.join(HERE, "media", "rent-roll")
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


# the scan is 3300 x 2550 px; rows start at y=500 px, 110 px apart (see the demo's make_sample.py)
PAGE_W = 9.0
PX = PAGE_W / 3300
PAGE_H = 2550 * PX


def row_y(i):
    return PAGE_H / 2 - (500 + 26 + 110 * i) * PX


ROWS = [
    ("100", "Starbucks", "1,850", "03/01/2019", "02/28/2029", "$38.00", "$70,300"),
    ("110", "Supercuts", "1,200", "06/01/2021", "05/31/2026", "$27.50", "$33,000"),
    ("120", "Verizon", "2,400", "01/01/2020", "12/31/2025", "$29.00", "$69,600"),
    ("130", "Five Guys", "2,650", "09/01/2022", "08/31/2032", "$31.25", "$82,812"),
    ("140", "Massage Envy", "3,300", "04/01/2018", "03/31/2028", "$24.00", "$79,200"),
    ("150", "Sally Beauty", "1,600", "11/01/2020", "10/31/2025", "$26.00", "$41,600"),
    ("200", "TJ Maxx", "24,000", "02/01/2016", "01/31/2026", "$11.50", "$276,000"),
]
COLS = [180, 420, 1050, 1400, 1800, 2200, 2560]
HEADS = ["Unit", "Occupant", "Sq Ft", "Begin", "End", "PSF", "Annual"]
PAPER = "#EFEAE0"
PINK = "#2A2A30"


def paper():
    """The sample's scanned page, redrawn as vectors at the same layout (rows/cols in px)."""
    def at(x_px, y_px):
        return np.array([-PAGE_W / 2 + x_px * PX, PAGE_H / 2 - y_px * PX, 0.01])
    g = VGroup(Rectangle(width=PAGE_W, height=PAGE_H, fill_color=PAPER, fill_opacity=1, stroke_width=0))
    t = T("Lakeland Commons - Tenant Schedule (as of 07/01/2024)", 24, PINK, weight=BOLD).scale(0.62)
    g.add(t.move_to(at(180, 290), aligned_edge=LEFT))
    for x, h in zip(COLS, HEADS):
        g.add(T(h, 24, PINK, weight=BOLD).scale(0.5).move_to(at(x, 405), aligned_edge=LEFT))
    g.add(Line(at(180, 450), at(3050, 450), color=PINK, stroke_width=1.5))
    for i, r in enumerate(ROWS):
        for x, v in zip(COLS, r):
            g.add(T(v, 24, PINK).scale(0.5).move_to(at(x, 526 + 110 * i), aligned_edge=LEFT))
    g.add(T("Unit 160   VACANT   1,400", 24, PINK).scale(0.5).move_to(at(180, 526 + 110 * 7 + 40), aligned_edge=LEFT))
    return g


class RentA(Explainer3D):
    def construct(self):
        title = T("Rent Roll OCR", 72)
        sub = I("from a scanned page to a comps database", 34, MUTED).next_to(title, DOWN, buff=0.35)
        rule = Line(LEFT * 0.9, RIGHT * 0.9, color=GOLD, stroke_width=2).next_to(sub, DOWN, buff=0.45)
        self.flat(title, sub, rule)
        self.play(FadeIn(title, shift=UP * 0.15), run_time=1.2)
        self.play(FadeIn(sub), Create(rule), run_time=1)
        self.wait(1.2)
        self.play(FadeOut(VGroup(title, sub, rule)), run_time=0.8)

        # the desk and the page, seen from above at an angle
        self.set_camera_orientation(phi=58 * DEGREES, theta=-100 * DEGREES, zoom=0.75)
        desk = clay(Prism(dimensions=[16, 11, 0.1]), GROUND).move_to([0, 0, -0.08])
        shadow = Rectangle(width=PAGE_W + 0.25, height=PAGE_H + 0.25, fill_color=BLACK,
                           fill_opacity=0.25, stroke_width=0).move_to([0.08, -0.08, -0.02])
        page = paper()
        self.add(desk)
        cap = self.say(None, "A broker's offering memo. Its rent roll is often a scan: a picture, no text.", wait=0.2)
        self.play(FadeIn(shadow), FadeIn(page), run_time=1.5)
        self.move_camera(phi=40 * DEGREES, theta=-92 * DEGREES, zoom=1.0, run_time=3.5)

        # render at 300 dpi, clean up, OCR: a reading line sweeps the rows
        cap = self.say(cap, "Each page is rendered at 300 dpi, sharpened, and read by Tesseract.", wait=0.2)
        bar = Rectangle(width=PAGE_W + 0.3, height=0.07, fill_color=GOLD, fill_opacity=0.9,
                        stroke_width=0).move_to([0, PAGE_H / 2 - 0.2, 0.03])
        glow = Rectangle(width=PAGE_W + 0.3, height=0.45, fill_color=GOLD, fill_opacity=0.12,
                         stroke_width=0).move_to(bar)
        self.play(FadeIn(bar), FadeIn(glow), run_time=0.5)
        marks = VGroup()
        for i in range(7):
            y = row_y(i)
            self.play(bar.animate.move_to([0, y, 0.03]), glow.animate.move_to([0, y, 0.03]),
                      run_time=0.55, rate_func=smooth)
            m = Rectangle(width=PAGE_W - 0.4, height=0.26, stroke_color=SEA, stroke_width=2.5,
                          fill_color=SEA, fill_opacity=0.12).move_to([0.05, y, 0.02])
            marks.add(m)
            self.add(m)
        self.play(FadeOut(bar), FadeOut(glow), run_time=0.4)

        # push in on one row
        cap = self.say(cap, "OCR hands back loose fragments, one line per row.", wait=0.2)
        self.move_camera(phi=20 * DEGREES, theta=-90 * DEGREES, zoom=2.3,
                         frame_center=[-1.3, row_y(0) - 0.5, 0], run_time=3)
        self.play(marks[0].animate.set_stroke(GOLD, width=4).set_fill(GOLD, 0.15), run_time=0.6)
        self.wait(1.4)
        self.play(FadeOut(cap), run_time=0.5)


def chip(text, color=INK, fill=None):
    t = T(text, 34, color)
    box = RoundedRectangle(corner_radius=0.12, width=t.width + 0.4, height=0.72,
                           stroke_color=color, stroke_width=2, fill_color=fill or BG, fill_opacity=1)
    return VGroup(box, t.move_to(box))


class RentB(Explainer):
    def construct(self):
        # the OCR fragments of row 1, as the parser splits them (on commas and spaces)
        frags = ["100", "Starbucks", "1", "850", "03/01/2019", "02/28/2029", "$38.00", "$70", "300"]
        chips = VGroup(*[chip(f, INK) for f in frags]).arrange(RIGHT, buff=0.16)
        chips.scale_to_fit_width(config.frame_width - 1.0).move_to(UP * 2.3)
        head = I("one OCR line, split into tokens", 30, MUTED).next_to(chips, UP, buff=0.4)
        cap = self.say(None, "The parser keeps only lines with a dollar amount, then rebuilds each field.", wait=0.2)
        self.play(FadeIn(head), LaggedStart(*[FadeIn(c, shift=DOWN * 0.2) for c in chips], lag_ratio=0.08), run_time=2)
        self.wait(1)

        # the rebuilt row: five slots
        names = ["tenant", "sq ft", "lease begin", "lease end", "rent / sq ft", "annual rent"]
        pos = [(-4.2, 0.9), (0, 0.9), (4.2, 0.9), (-4.2, -0.9), (0, -0.9), (4.2, -0.9)]
        slots = VGroup()
        for (x, y), n in zip(pos, names):
            lab = T(n, 28, MUTED).move_to([x, y, 0])
            line = Line([x - 1.5, y - 0.4, 0], [x + 1.5, y - 0.4, 0], color=MUTED, stroke_width=2)
            slots.add(VGroup(lab, line))
        self.play(FadeIn(slots), run_time=0.8)

        def land(src_idx, text, slot, color, note):
            srcs = VGroup(*[chips[i] for i in src_idx])
            out = T(text, 36, color).move_to([pos[slot][0], pos[slot][1] - 0.8, 0])
            n = I(note, 30, color).move_to([0, -2.55, 0])
            self.play(*[c[0].animate.set_stroke(color, width=3) for c in srcs], FadeIn(n), run_time=0.5)
            self.play(TransformFromCopy(srcs, out), run_time=1.0)
            self.wait(0.9)
            self.play(FadeOut(n), run_time=0.3)
            return out

        cap = self.say(cap, "Every rule shown here comes from the parser's code.", wait=0.2)
        land([1], "Starbucks", 0, SEA, "matched against a list of known tenant names")
        land([2, 3], "1,850", 1, GOLD, '"1" and "850" were split by the comma: join them back')
        land([4], "03/01/2019", 2, SEA, "earliest date is the lease start")
        land([5], "02/28/2029", 3, SEA, "end date: the one 3, 5 or 10 years after the start")
        land([6], "$38.00", 4, SEA, "a $x.xx token above a floor is rent per square foot")
        land([7, 8], "$70,300", 5, GOLD, '"$70" and "300" join into annual rent')

        check = T("1,850 sq ft  x  $38.00  =  $70,300", 38, GOLD).move_to(DOWN * 2.55)
        cap = self.say(cap, "If OCR leaves several candidates, rent is checked against size x rate.", wait=0.2)
        self.play(Write(check), run_time=1.4)
        self.wait(2.2)


class RentC(Explainer):
    def construct(self):
        scan = ImageMobject(os.path.join(MEDIA, "rentroll_scan.png")).set_width(config.frame_width * 1.15)
        scan.move_to(DOWN * 0.8 + RIGHT * 0.6)
        self.play(FadeIn(scan), run_time=1)
        cap = self.caption("The real input from the demo: a scanned page (a synthetic sample).", INK)
        bg = BackgroundRectangle(cap, color=BG, fill_opacity=0.85, buff=0.2)
        bg.set_z_index(9); cap.set_z_index(10)
        self.play(FadeIn(bg), FadeIn(cap), run_time=0.6)
        self.play(scan.animate.scale(1.35).shift(LEFT * 1.5 + DOWN * 0.6), run_time=5, rate_func=linear)
        self.play(FadeOut(scan), FadeOut(bg), FadeOut(cap), run_time=0.8)
        shot = ImageMobject(os.path.join(MEDIA, "results.png")).set_height(config.frame_height * 0.98)
        shot.move_to(UP * 0.4)
        frame = SurroundingRectangle(shot, color=MUTED, stroke_width=2, buff=0.04)
        self.play(FadeIn(shot), FadeIn(frame), run_time=1.2)
        cap = self.caption("The real app, run locally: seven tenants in, seven complete rows out.", GOLD)
        bg = BackgroundRectangle(cap, color=BG, fill_opacity=0.85, buff=0.2)
        bg.set_z_index(9); cap.set_z_index(10)
        self.play(FadeIn(bg), FadeIn(cap), run_time=0.7)
        self.play(Group(shot, frame).animate.scale(1.3).shift(RIGHT * 1.6 + DOWN * 0.9), run_time=6, rate_func=linear)
        self.wait(0.5)
        self.closing("Rent Roll OCR", "github.com/jaycewalzer1/rr-tool2")
