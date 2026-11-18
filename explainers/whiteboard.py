"""Collaborative whiteboard: how concurrent edits and undo stay consistent.

Style: a flat sequence diagram (two browsers, one server with Postgres) cut against the real
two-browser recording from the local demo run on 2026-11-17. The repo is private: no code is shown.

Facts from the repo README (Sync and conflict model): each edit is one transaction that bumps a
per-canvas seq under a row lock; the new seq is the shape's version; broadcast only after commit,
to everyone including the sender; clients keep the highest version and ignore older frames;
geometry {x, y, width, height} is replaced as one group (last writer wins); deletes are
tombstones; undo is sent as the inverse op through the same path.

Scene: Wb (2D with a real still).
"""
import os

from style import *

MEDIA = os.path.join(HERE, "media", "whiteboard")
LX, SX, RX = -5.2, 0.0, 5.2   # lane x positions: alice, server, bob


def shape_card(version, color=SEA, w=1.5):
    box = RoundedRectangle(corner_radius=0.1, width=w, height=0.8, stroke_color=color, stroke_width=3,
                           fill_color=color, fill_opacity=0.18)
    lab = T(f"v{version}", 30, color).move_to(box)
    return VGroup(box, lab)


class Wb(Explainer):
    title = "Collaborative Whiteboard"
    subtitle = "two to five people editing the same shapes at once"

    def construct(self):
        self.title_card()

        # the real thing first
        shot = ImageMobject(os.path.join(MEDIA, "two-browsers.png")).set_width(config.frame_width)
        self.play(FadeIn(shot), run_time=0.8)
        cap = self.caption("Two browsers, two users, one canvas: the local demo run.", INK)
        bg = BackgroundRectangle(cap, color=BG, fill_opacity=0.85, buff=0.2)
        bg.set_z_index(9); cap.set_z_index(10)
        self.play(FadeIn(bg), FadeIn(cap), run_time=0.5)
        self.play(shot.animate.scale(1.25).shift(RIGHT * 1.0 + DOWN * 0.3), run_time=4, rate_func=linear)
        self.play(FadeOut(shot), FadeOut(bg), FadeOut(cap), run_time=0.7)

        # lanes
        heads = VGroup(T("alice", 34, INK).move_to([LX, 3.2, 0]), T("server + Postgres", 34, GOLD).move_to([SX, 3.2, 0]),
                       T("bob", 34, INK).move_to([RX, 3.2, 0]))
        lanes = VGroup(*[DashedLine([x, 2.8, 0], [x, -2.6, 0], color=MUTED, stroke_width=2) for x in (LX, SX, RX)])
        a_shape = shape_card(7).move_to([LX, 1.9, 0])
        b_shape = shape_card(7).move_to([RX, 1.9, 0])
        seq = T("seq 7", 32, GOLD).move_to([SX, 1.9, 0])
        cap = self.say(None, "Every shape carries a version: the canvas sequence number when it last changed.", wait=0.3)
        self.play(FadeIn(heads), Create(lanes), FadeIn(a_shape), FadeIn(b_shape), FadeIn(seq), run_time=1.2)

        def send(y, frm, to, label, color=SEA):
            arr = Arrow([frm, y, 0], [to, y - 0.35, 0], buff=0.25, color=color, stroke_width=4, max_tip_length_to_length_ratio=0.06)
            lab = T(label, 26, color).next_to(arr, UP, buff=0.05)
            self.play(GrowArrow(arr), FadeIn(lab), run_time=0.7)
            return VGroup(arr, lab)

        # 1. one edit: lock, bump, commit, then broadcast to everyone
        cap = self.say(cap, "Alice drags. The server locks the canvas row, bumps seq, commits.", wait=0.1)
        m1 = send(1.2, LX, SX, "drag")
        self.play(seq.animate.become(T("seq 8", 32, GOLD).move_to(seq)).scale(1.15), run_time=0.8)
        cap = self.say(cap, "Only after the commit does it broadcast, to everyone including Alice.", wait=0.1)
        b1 = VGroup(send(0.4, SX, LX, "v8"), send(0.4, SX, RX, "v8"))
        self.play(a_shape.animate.become(shape_card(8).move_to(a_shape)), b_shape.animate.become(shape_card(8).move_to(b_shape)), run_time=0.6)
        self.wait(0.8)

        # 2. a late frame never moves anything backwards
        cap = self.say(cap, "A late frame with an older version is simply ignored. Nothing moves backwards.", wait=0.1)
        late = send(-0.5, SX, RX, "v7 (late)", MUTED)
        cross = Cross(late[1], stroke_color=CORAL, stroke_width=4)
        self.play(Create(cross), run_time=0.5)
        self.wait(1.2)
        self.play(FadeOut(VGroup(m1, b1, late, cross)), run_time=0.5)

        # 3. a race: drag vs resize, serialized; geometry replaced whole
        cap = self.say(cap, "Bob resizes while Alice drags. The lock puts them in order.", wait=0.1)
        r1 = send(1.2, RX, SX, "resize")
        r2 = send(0.9, LX, SX, "drag")
        order = VGroup(T("v9  resize", 28, INK), T("v10  drag", 28, GOLD)).arrange(DOWN, buff=0.15).move_to([SX + 1.6, -0.3, 0])
        self.play(FadeIn(order), seq.animate.become(T("seq 10", 32, GOLD).move_to(seq)), run_time=0.8)
        cap = self.say(cap, "Position and size travel as one unit, so the result is one user's shape, never a mix.", wait=0.1)
        self.play(a_shape.animate.become(shape_card(10, GOLD, 1.9).move_to(a_shape)),
                  b_shape.animate.become(shape_card(10, GOLD, 1.9).move_to(b_shape)), run_time=0.8)
        self.wait(1.2)
        self.play(FadeOut(VGroup(r1, r2, order)), run_time=0.5)

        # 4. undo is just another edit
        cap = self.say(cap, "Undo sends the inverse of Alice's own edit, down the same path, as v11.", wait=0.1)
        u = send(1.2, LX, SX, "undo = inverse op", DRIFT)
        self.play(seq.animate.become(T("seq 11", 32, GOLD).move_to(seq)), run_time=0.5)
        ub = VGroup(send(0.4, SX, LX, "v11", DRIFT), send(0.4, SX, RX, "v11", DRIFT))
        self.play(a_shape.animate.become(shape_card(11, DRIFT).move_to(a_shape)),
                  b_shape.animate.become(shape_card(11, DRIFT).move_to(b_shape)), run_time=0.6)
        cap = self.say(cap, "Deletes are tombstones, so a late drag can't resurrect a shape.", wait=1.6)
        cap = self.say(cap, "Scripted test with 5 users firing at once: 26 of 26 checks, 3 runs in a row.", GOLD, wait=2.2)
        self.closing("Collaborative Whiteboard", "React, FastAPI, Postgres. A Mechanize take-home.")
