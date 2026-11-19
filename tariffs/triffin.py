"""Triffin's dilemma  (companion to gubbgub.github.io/tariffs.html, Intuition 5)

Render:  manim -pqh triffin.py Triffin

Gold numbers are real (Federal Reserve): about $24.6B in 1949, $17.8B at the end of
1960, $10.5B at the end of July 1971, valued at the official $35 an ounce. Between those
dates the pile is interpolated in a straight line.
The dollars-held-abroad bar is illustrative: only its 1960 crossing point is taken from
the record (Cleveland Fed: by 1960, external dollar liabilities exceeded the gold stock).
The on-screen note says so.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))   # finds site_style.py
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import numpy as np
from manim import *
from site_style import *

CROSS = 1960.99        # end of 1960, when dollars abroad passed the gold stock
GOLD_PTS = [(1949.0, 24.6), (1960.99, 17.8), (1971.58, 10.5)]   # (year, $ billions)
UNIT = 0.1             # scene units per $1 billion
BASE = -2.45
PILE_X, BAR_X = -2.9, 2.9     # symmetric, so the picture sits in the middle of the frame
BRICK_W, BRICK_H, PER_ROW = 0.8, 0.4, 4      # one brick = $1B, so a row of 4 = $4B = 0.4 units = 4 * UNIT


def gold(yr):
    xs, ys = zip(*GOLD_PTS)
    return float(np.interp(yr, xs, ys))


def dollars_abroad(yr):
    """Illustrative curve that crosses the gold stock at the start of 1961 (end of 1960)."""
    cross_yr, cross_v = CROSS, gold(CROSS)
    if yr <= cross_yr:
        return 7 + (cross_v - 7) * ((yr - 1949) / (cross_yr - 1949)) ** 1.25
    return cross_v + 17 * ((yr - cross_yr) / (1971.58 - cross_yr)) ** 1.4


def label(text, size=24, color=INK, font=SANS, weight=NORMAL):
    return Text(text, font=font, font_size=size, color=color, weight=weight)


def fit(mob, max_w):
    if mob.width > max_w:
        mob.scale(max_w / mob.width)
    return mob


class Triffin(Scene):
    def construct(self):
        yr = ValueTracker(1949)
        grow = ValueTracker(0)    # 0 -> 1 while the gold pile stacks up and the dollar bar rises

        # ---------- Title ----------
        tag = label("DEEP DIVE · ECONOMICS", 18, INK_3, LABEL)
        title = label("Triffin's dilemma", 58, INK, SERIF)
        sub = label("The trap inside the world's currency", 26, INK_2)
        VGroup(tag, title, sub).arrange(DOWN, buff=0.3)
        self.play(FadeIn(tag, shift=UP * 0.2), Write(title), run_time=1.5)
        self.play(FadeIn(sub, shift=UP * 0.1))
        self.wait(1.2)
        header = label("Triffin's dilemma", 30, INK, SERIF).to_corner(UL, buff=0.5)
        self.play(FadeOut(tag), FadeOut(sub), ReplacementTransform(title, header))

        # ---------- The promise ----------
        brick_icon = Polygon([-0.6, -0.22, 0], [0.6, -0.22, 0], [0.42, 0.22, 0], [-0.42, 0.22, 0],
                             fill_color=GOLD, fill_opacity=1, stroke_width=0).scale(1.2)
        oz = label("1 ounce of gold", 22, INK_2).next_to(brick_icon, DOWN, buff=0.25)
        eq = label("=", 60, INK)
        note = RoundedRectangle(corner_radius=0.08, width=2.2, height=1.0, fill_color=SURFACE, fill_opacity=1,
                                stroke_color=LINE, stroke_width=2)
        note_txt = label("$35", 44, ACCENT, weight=BOLD).move_to(note)
        note_g = VGroup(note, note_txt)
        promise = VGroup(note_g, eq, VGroup(brick_icon, oz)).arrange(RIGHT, buff=0.7).shift(UP * 0.3)
        cap = label("1944, Bretton Woods: the U.S. promises foreign governments", 24, INK_2)
        cap2 = label("it will trade gold for dollars at $35 an ounce.", 24, INK_2)
        caps = VGroup(cap, cap2).arrange(DOWN, buff=0.15).next_to(promise, DOWN, buff=0.8)
        self.play(FadeIn(note_g, shift=RIGHT * 0.2), FadeIn(eq), FadeIn(VGroup(brick_icon, oz), shift=LEFT * 0.2))
        self.play(FadeIn(caps, shift=UP * 0.1))
        self.wait(2.2)
        line3 = label("So every dollar held abroad is a claim on American gold.", 26, INK, weight=BOLD) \
            .next_to(caps, DOWN, buff=0.35)
        self.play(FadeIn(line3, shift=UP * 0.1))
        self.wait(2.2)
        self.play(FadeOut(VGroup(promise, caps, line3), shift=UP * 0.2))

        # ---------- The race: gold pile vs dollars abroad ----------
        axis = Line([-5.4, BASE, 0], [5.4, BASE, 0], color=INK_3, stroke_width=2)

        def pile():
            g = VGroup()
            for i in range(round(gold(yr.get_value()) * grow.get_value())):    # one whole brick per $1 billion
                row, col = divmod(i, PER_ROW)
                w = BRICK_W
                b = Polygon([-w / 2 + 0.04, 0, 0], [w / 2 - 0.04, 0, 0], [w / 2 - 0.14, BRICK_H - 0.05, 0],
                            [-w / 2 + 0.14, BRICK_H - 0.05, 0], fill_color=GOLD, fill_opacity=1, stroke_width=0)
                x = PILE_X + (col - (PER_ROW - 1) / 2) * BRICK_W
                b.shift([x, BASE + row * BRICK_H, 0])
                g.add(b)
            return g

        def dollar_bar():
            h = max(dollars_abroad(yr.get_value()) * UNIT * grow.get_value(), 0.001)
            return Rectangle(width=PER_ROW * BRICK_W, height=h, stroke_width=0, fill_color=ACCENT,
                             fill_opacity=0.85).move_to([BAR_X, BASE, 0], aligned_edge=DOWN)

        gold_val = always_redraw(lambda: label(f"${gold(yr.get_value()):.1f}B", 28, INK, weight=BOLD)
                                 .move_to([PILE_X, BASE + round(gold(yr.get_value())) / PER_ROW * BRICK_H + 0.4, 0])
                                 .set_opacity(max(0, grow.get_value() * 3 - 2)))
        bar_val = always_redraw(lambda: label("growing", 22, ACCENT, weight=BOLD)
                                .next_to([BAR_X, BASE + dollars_abroad(yr.get_value()) * UNIT, 0], UP, buff=0.15)
                                .set_opacity(max(0, grow.get_value() * 3 - 2)))
        pile_name = label("U.S. gold", 22, INK_2).next_to([PILE_X, BASE, 0], DOWN, buff=0.22)
        bar_name = label("Dollars held abroad", 22, INK_2).next_to([BAR_X, BASE, 0], DOWN, buff=0.22)
        year = always_redraw(lambda: label(f"{int(yr.get_value())}", 54, INK, SERIF).to_corner(UR, buff=0.45)
                             .set_opacity(max(0, grow.get_value() * 3 - 2)))
        foot = label("Gold: Federal Reserve data at $35/oz (1949, 1960, July 1971).  "
                     "Dollar bar: illustrative, except where it crosses gold (1960).", 15, INK_3) \
            .to_corner(DL, buff=0.3)

        # dollars streaming abroad: dots ride an arc from the pile to the bar
        stream_on = ValueTracker(0)   # fades the stream in once the pile is built
        def stream():
            g = VGroup()
            t = yr.get_value()
            start, end = np.array([PILE_X + 1.3, BASE + 0.6, 0]), np.array([BAR_X - 1.3, BASE + 0.6, 0])
            for k in range(10):
                f = ((t - 1949) * 1.6 + k / 10) % 1
                pt = start + (end - start) * f + np.array([0, 1.1 * np.sin(np.pi * f), 0])
                g.add(Dot(pt, radius=0.06, color=ACCENT).set_opacity(np.sin(np.pi * f) * stream_on.get_value()))
            return g

        cap = label("The world needs dollars to trade, so they flow out of the U.S. every year.", 24, INK_2) \
            .next_to(header, DOWN, buff=0.35, aligned_edge=LEFT)
        self.play(Create(axis), FadeIn(pile_name, shift=UP * 0.1), FadeIn(bar_name, shift=UP * 0.1), FadeIn(foot),
                  run_time=1)
        self.add(always_redraw(pile), always_redraw(dollar_bar), gold_val, bar_val, year, always_redraw(stream))
        # LEARN: the bricks are counted from `grow`, so raising it from 0 to 1 stacks them up one at a time.
        self.play(grow.animate.set_value(1), run_time=2.2, rate_func=rate_functions.ease_in_out_sine)
        self.play(FadeIn(cap, shift=UP * 0.1), stream_on.animate.set_value(1), run_time=1)
        self.play(yr.animate.set_value(1958), run_time=4.5, rate_func=linear)
        self.play(yr.animate.set_value(CROSS), run_time=2.5, rate_func=rate_functions.ease_out_sine)

        # ---------- 1960: the crossing ----------
        cross_y = BASE + gold(CROSS) * UNIT
        cross = DashedLine([PILE_X - 1.3, cross_y, 0], [BAR_X + 1.3, cross_y, 0], color=INK_2, dash_length=0.1)
        new = VGroup(label("1960: dollars abroad now outnumber the gold behind them.", 24, INK, weight=BOLD),
                     label("The $35 promise can't be kept for everyone at once.", 24, INK_2)) \
            .arrange(DOWN, aligned_edge=LEFT, buff=0.15).next_to(header, DOWN, buff=0.35, aligned_edge=LEFT)
        self.play(FadeOut(cap, shift=UP * 0.1), run_time=0.4)
        self.play(Create(cross), FadeIn(new, shift=UP * 0.1))
        cap = new
        self.wait(3)

        # ---------- The dilemma ----------
        def card(head, *body):
            t1 = label(head, 24, INK, weight=BOLD)
            lines = [label(b, 22, INK_2) for b in body]
            txt = VGroup(t1, *lines).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
            box = RoundedRectangle(corner_radius=0.18, width=5.4, height=txt.height + 0.55, fill_color=SURFACE,
                                   fill_opacity=1, stroke_color=LINE, stroke_width=2)
            txt.move_to(box)
            return VGroup(box, txt)

        warn = label("Robert Triffin warned Congress: the U.S. faced two bad choices.", 24, INK, weight=BOLD) \
            .next_to(header, DOWN, buff=0.35, aligned_edge=LEFT)
        c1 = card("Stop sending dollars abroad", "and the world runs short", "of money to trade with.")
        c2 = card("Keep sending dollars abroad", "and the gold promise", "looks weaker every year.")
        cards = VGroup(c1, c2).arrange(RIGHT, buff=0.7).next_to(warn, DOWN, buff=0.35).set_x(0)
        or_txt = label("or", 22, INK_3).move_to(VGroup(c1, c2).get_center())
        self.play(FadeOut(cap, shift=UP * 0.1), FadeOut(cross), run_time=0.4)
        self.play(FadeIn(warn, shift=UP * 0.1))
        self.play(FadeIn(c1, shift=UP * 0.15))
        self.play(FadeIn(or_txt), FadeIn(c2, shift=UP * 0.15))
        self.wait(4)
        self.play(FadeOut(VGroup(warn, cards, or_txt), shift=UP * 0.15))

        cap = label("The U.S. kept sending dollars. Foreign governments kept trading them for gold.", 24, INK_2) \
            .next_to(header, DOWN, buff=0.35, aligned_edge=LEFT)
        self.play(FadeIn(cap, shift=UP * 0.1))
        self.play(yr.animate.set_value(1971.58), run_time=5.5, rate_func=linear)

        # ---------- 1971: the gold window closes ----------
        pile_top = BASE + np.ceil(round(gold(yr.get_value())) / PER_ROW) * BRICK_H + 0.25
        frame = Rectangle(width=PER_ROW * BRICK_W + 0.5, height=pile_top - BASE + 0.05, stroke_color=INK_2,
                          stroke_width=3).move_to([PILE_X, BASE, 0], aligned_edge=DOWN)
        shutter = Rectangle(width=frame.width, height=frame.height, fill_color=INK_2, fill_opacity=0.92,
                            stroke_width=0).move_to(frame).stretch(0.001, 1, about_edge=UP)
        new = VGroup(label("August 15, 1971: Nixon closes the \"gold window.\"", 24, INK, weight=BOLD),
                     label("Dollars can no longer be traded for U.S. gold, just as Triffin predicted.", 24, INK_2)) \
            .arrange(DOWN, aligned_edge=LEFT, buff=0.15).next_to(header, DOWN, buff=0.35, aligned_edge=LEFT)
        self.play(FadeOut(cap, shift=UP * 0.1), FadeOut(gold_val), run_time=0.4)
        self.play(Create(frame), FadeIn(new, shift=UP * 0.1))
        self.play(shutter.animate.stretch(1000, 1, about_edge=UP), run_time=1.6, rate_func=rate_functions.ease_in_quad)
        closed = label("CLOSED", 28, SURFACE, LABEL).move_to(frame)
        left = label(f"${gold(yr.get_value()):.1f}B of gold left", 24, INK, weight=BOLD).next_to(frame, UP, buff=0.2)
        self.play(FadeIn(closed), FadeIn(left, shift=UP * 0.1))
        self.wait(3)

        # ---------- Today ----------
        self.play(*[FadeOut(m) for m in self.mobjects if m is not header])
        q = label("Is there a version of this trap today?", 40, INK, SERIF)
        settled = label("The gold trap is gone. It ended in 1971.", 26, INK, weight=BOLD)
        open_q = label("Whether a new one replaced it is still debated:", 23, INK_2)

        def view(head, *body):
            txt = VGroup(label(head, 23, INK, weight=BOLD), *[label(l, 21, INK_2) for l in body]) \
                .arrange(DOWN, aligned_edge=LEFT, buff=0.12)
            box = RoundedRectangle(corner_radius=0.18, width=txt.width + 0.7, height=txt.height + 0.5, fill_color=SURFACE,
                                   fill_opacity=1, stroke_color=LINE, stroke_width=2)
            return VGroup(box, txt.move_to(box))

        v1 = view("One view", "The world's demand for dollars keeps", "the dollar strong and U.S. trade", "deficits large.")
        v2 = view("The other view", "Dollars can leave through investment,", "not just trade, so the deficits come", "from U.S. budget choices.")
        views = VGroup(v1, v2).arrange(RIGHT, buff=0.5)
        decide = VGroup(label("The deciding question: which one explains the deficits better.", 23, INK, weight=BOLD),
                        label("Economists are still measuring that.", 23, INK_2)).arrange(DOWN, buff=0.12)
        g = VGroup(q, settled, open_q, views, decide).arrange(DOWN, buff=0.3).shift(DOWN * 0.1)
        self.play(Write(q), run_time=1.4)
        self.wait(0.4)
        self.play(FadeIn(settled, shift=UP * 0.1))
        self.wait(1.6)
        self.play(FadeIn(open_q, shift=UP * 0.1))
        self.play(FadeIn(v1, shift=UP * 0.1))
        self.wait(1.8)
        self.play(FadeIn(v2, shift=UP * 0.1))
        self.wait(2.2)
        self.play(FadeIn(decide, shift=UP * 0.1))
        self.wait(2.5)
        url = label("Read the full deep dive: gubbgub.github.io/tariffs", 22, ACCENT, LABEL).to_edge(DOWN, buff=0.45)
        self.play(FadeIn(url, shift=UP * 0.1))
        self.wait(2)
