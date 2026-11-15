"""
Integrals, antiderivatives, and u-substitution, in Manim.

Render one scene:   manim -pql integrals.py Accumulation
Render all scenes:  manim -pqh integrals.py Accumulation PlusC USubPicture USubAlgebra

Scenes
  1. Accumulation  - an integral adds up area; the area function's slope is f  (FTC)
  2. PlusC         - every vertical shift of an antiderivative has the same slope  (+C)
  3. USubPicture   - u = x^2 turns each thin strip into a strip of equal area
  4. USubAlgebra   - the same idea written out, then a problem for you
"""
import numpy as np
from manim import *

INK = "#E9ECF4"
DIM = "#8A94AE"
BLUE_ = "#5B8DEF"
GOLD = "#FFB34D"
GREEN_ = "#7BD389"

config.background_color = "#0B0E1A"


def ax_cfg():
    return {"include_numbers": True, "font_size": 22, "color": DIM}


# --------------------------------------------------------------------------- 1
class Accumulation(Scene):
    def construct(self):
        f = lambda x: 0.3 * x**2 + 0.5
        A = lambda x: 0.1 * x**3 + 0.5 * x          # A(x) = integral of f from 0 to x

        title = Text("1 · An integral adds up area", font_size=34, color=INK).to_edge(UP)
        self.play(Write(title))

        axL = Axes(x_range=[0, 4.2, 1], y_range=[0, 6, 2], x_length=5.4, y_length=3.8,
                   tips=False, axis_config=ax_cfg()).to_corner(DL, buff=0.7)
        axR = Axes(x_range=[0, 4.2, 1], y_range=[0, 9, 3], x_length=5.4, y_length=3.8,
                   tips=False, axis_config=ax_cfg()).to_corner(DR, buff=0.7)
        gf = axL.plot(f, x_range=[0, 4], color=INK)
        fl = MathTex("f(x)", color=INK, font_size=34).next_to(axL.c2p(4, f(4)), UL, buff=0.1)
        self.play(Create(axL), Create(gf), Write(fl))

        # Riemann sums getting thinner
        cap = Text("rectangles of width Δx", font_size=24, color=DIM).next_to(axL, UP, buff=0.15)
        rects = axL.get_riemann_rectangles(gf, x_range=[0, 4], dx=0.5, fill_opacity=0.55,
                                           stroke_width=0.6, color=[BLUE_, GREEN_])
        self.play(FadeIn(cap), Create(rects))
        for dx in (0.25, 0.1, 0.04):
            new = axL.get_riemann_rectangles(gf, x_range=[0, 4], dx=dx, fill_opacity=0.55,
                                             stroke_width=0.3 if dx > 0.05 else 0, color=[BLUE_, GREEN_])
            self.play(Transform(rects, new), run_time=1.2)
        cap2 = Text("Δx → 0 gives the exact area", font_size=24, color=DIM).move_to(cap)
        self.play(Transform(cap, cap2))
        self.wait(0.8)
        self.play(FadeOut(rects), FadeOut(cap))

        # area as a function of the right endpoint
        x = ValueTracker(0.02)
        area = always_redraw(lambda: axL.get_area(gf, x_range=[0, x.get_value()], color=BLUE_, opacity=0.45))
        edge = always_redraw(lambda: axL.get_vertical_line(axL.c2p(x.get_value(), f(x.get_value())),
                                                           color=GOLD, line_func=Line, stroke_width=4))

        Al = MathTex(r"A(x)=\int_0^x f(t)\,dt", color=INK, font_size=32).next_to(axR, UP, buff=0.15)
        self.play(Create(axR), Write(Al), FadeIn(area), FadeIn(edge))

        traced = always_redraw(lambda: axR.plot(A, x_range=[0, max(x.get_value(), 0.021)], color=BLUE_))
        dot = always_redraw(lambda: Dot(axR.c2p(x.get_value(), A(x.get_value())), color=GOLD))

        def tangent():
            xv = x.get_value()
            h = 0.55
            return Line(axR.c2p(xv - h, A(xv) - h * f(xv)), axR.c2p(xv + h, A(xv) + h * f(xv)),
                        color=GOLD, stroke_width=3)
        tan = always_redraw(tangent)

        r1 = VGroup(MathTex(r"\text{height of } f =", font_size=30, color=INK),
                    DecimalNumber(0, num_decimal_places=2, font_size=30, color=GOLD)).arrange(RIGHT)
        r2 = VGroup(MathTex(r"\text{slope of } A =", font_size=30, color=INK),
                    DecimalNumber(0, num_decimal_places=2, font_size=30, color=GOLD)).arrange(RIGHT)
        readout = VGroup(r1, r2).arrange(DOWN, aligned_edge=LEFT).next_to(title, DOWN, buff=0.35).to_edge(LEFT, buff=0.9)
        r1[1].add_updater(lambda m: m.set_value(f(x.get_value())))
        r2[1].add_updater(lambda m: m.set_value(f(x.get_value())))   # A'(x) — the point of the scene
        self.add(traced, dot, tan)
        self.play(FadeIn(readout))
        self.play(x.animate.set_value(4), run_time=7, rate_func=linear)
        self.wait(0.5)

        punch = MathTex(r"A'(x) = f(x)", font_size=48, color=GOLD)
        sub = Text("The area function is an antiderivative of f.", font_size=24, color=INK)
        box = VGroup(punch, sub).arrange(DOWN, aligned_edge=LEFT).move_to(readout, aligned_edge=LEFT)
        self.play(FadeOut(readout), FadeIn(box))
        self.play(Circumscribe(punch, color=GOLD))
        self.wait(2)


# --------------------------------------------------------------------------- 2
class PlusC(Scene):
    def construct(self):
        title = Text("2 · Why antiderivatives get a + C", font_size=34, color=INK).to_edge(UP)
        q = MathTex(r"\text{Which } F(x) \text{ has } F'(x) = 2x\,?", font_size=36, color=INK).next_to(title, DOWN)
        self.play(Write(title), Write(q))

        ax = Axes(x_range=[-2.5, 2.5, 1], y_range=[-2, 8, 2], x_length=7, y_length=4.6,
                  tips=False, axis_config=ax_cfg()).to_edge(DOWN, buff=0.4)
        self.play(Create(ax))
        Cs = [-1, 0, 1, 2, 3]
        cols = color_gradient([BLUE_, GREEN_], len(Cs))
        curves = VGroup(*[ax.plot(lambda t, c=c: t**2 + c, x_range=[-2.3, 2.3], color=col)
                          for c, col in zip(Cs, cols)])
        labels = VGroup(*[MathTex(f"x^2{c:+d}" if c else "x^2", font_size=26, color=col)
                          .next_to(ax.c2p(2.3, 2.3**2 + c), RIGHT, buff=0.1)
                          for c, col in zip(Cs, cols)])
        self.play(LaggedStart(*[Create(c) for c in curves], lag_ratio=0.2), FadeIn(labels))

        x = ValueTracker(-2)
        def tangents():
            xv, h = x.get_value(), 0.45
            return VGroup(*[Line(ax.c2p(xv - h, xv**2 + c - h * 2 * xv), ax.c2p(xv + h, xv**2 + c + h * 2 * xv),
                                 color=GOLD, stroke_width=3) for c in Cs])
        tans = always_redraw(tangents)
        slope = VGroup(MathTex(r"\text{every slope} = 2x =", font_size=30, color=INK),
                       DecimalNumber(-4, num_decimal_places=2, font_size=30, color=GOLD)).arrange(RIGHT)
        slope.to_corner(UL).shift(DOWN * 1.3)
        slope[1].add_updater(lambda m: m.set_value(2 * x.get_value()))
        self.add(tans)
        self.play(FadeIn(slope))
        self.play(x.animate.set_value(2), run_time=5, rate_func=smooth)
        self.wait(0.3)

        ans = MathTex(r"F(x) = x^2 + C", font_size=46, color=GOLD).move_to(q)
        why = Text("Shifting a curve up or down never changes its slope,\nso the derivative can't tell these apart.",
                   font_size=24, color=INK, line_spacing=0.8).to_corner(UR).shift(DOWN * 1.2)
        self.play(Transform(q, ans), FadeIn(why))
        self.play(Circumscribe(q, color=GOLD))
        self.wait(2)


# --------------------------------------------------------------------------- 3
class USubPicture(Scene):
    def construct(self):
        g = lambda x: 2 * x * np.cos(x**2)
        b = np.sqrt(np.pi / 2)                       # x from 0 to sqrt(pi/2)  <->  u from 0 to pi/2

        title = Text("3 · u-substitution is a change of ruler", font_size=34, color=INK).to_edge(UP)
        self.play(Write(title))

        axL = Axes(x_range=[0, 1.4, 0.5], y_range=[0, 1.5, 0.5], x_length=5.2, y_length=2.9,
                   tips=False, axis_config=ax_cfg()).to_corner(DL, buff=0.45)
        axR = Axes(x_range=[0, 1.7, 0.5], y_range=[0, 1.5, 0.5], x_length=5.2, y_length=2.9,
                   tips=False, axis_config=ax_cfg()).to_corner(DR, buff=0.45)
        xl = MathTex("x", color=DIM, font_size=30).next_to(axL.x_axis, RIGHT, buff=0.1)
        ul = MathTex("u", color=DIM, font_size=30).next_to(axR.x_axis, RIGHT, buff=0.1)
        gL = axL.plot(g, x_range=[0, b], color=INK)
        gR = axR.plot(np.cos, x_range=[0, np.pi / 2], color=INK)
        aL = axL.get_area(gL, x_range=[0, b], color=BLUE_, opacity=0.25)
        aR = axR.get_area(gR, x_range=[0, np.pi / 2], color=BLUE_, opacity=0.25)
        iL = MathTex(r"\int_0^{\sqrt{\pi/2}} 2x\cos(x^2)\,dx", font_size=32, color=INK).next_to(axL, UP, buff=0.2)
        iR = MathTex(r"\int_0^{\pi/2} \cos(u)\,du", font_size=32, color=INK).next_to(axR, UP, buff=0.2)
        arrow = MathTex(r"u = x^2", font_size=36, color=GOLD).move_to((iL.get_center() + iR.get_center()) / 2)
        self.play(Create(axL), Create(axR), FadeIn(xl, ul))
        self.play(Create(gL), Create(gR), FadeIn(aL, aR), Write(iL), Write(iR))
        self.play(Write(arrow))
        self.wait(0.5)

        # one thin strip on each side, linked by u = x^2
        dx = 0.07
        x = ValueTracker(0.15)

        def stripL():
            xv = x.get_value()
            return Polygon(axL.c2p(xv, 0), axL.c2p(xv + dx, 0), axL.c2p(xv + dx, g(xv)), axL.c2p(xv, g(xv)),
                           fill_color=GOLD, fill_opacity=0.85, stroke_width=0)

        def stripR():
            xv = x.get_value()
            u, du = xv**2, 2 * xv * dx
            return Polygon(axR.c2p(u, 0), axR.c2p(u + du, 0), axR.c2p(u + du, np.cos(u)), axR.c2p(u, np.cos(u)),
                           fill_color=GOLD, fill_opacity=0.85, stroke_width=0)
        sL, sR = always_redraw(stripL), always_redraw(stripR)
        self.add(sL, sR)

        note = VGroup(
            MathTex(r"\text{width: } dx \;\longrightarrow\; du = 2x\,dx", font_size=30, color=INK),
            MathTex(r"\text{height: } 2x\cos(x^2) \;\longrightarrow\; \cos(u)", font_size=30, color=INK),
            MathTex(r"\text{width} \times 2x,\;\; \text{height} \div 2x \;\Rightarrow\; \text{same area}",
                    font_size=30, color=GOLD),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18).next_to(title, DOWN, buff=0.25)
        self.play(FadeIn(note[0]))
        self.play(x.animate.set_value(1.1), run_time=4)
        self.play(FadeIn(note[1]))
        self.play(x.animate.set_value(0.3), run_time=3)
        self.play(FadeIn(note[2]))
        self.play(x.animate.set_value(b - dx), run_time=4)
        self.wait(0.5)

        # strip-by-strip equal => total equal
        self.play(FadeOut(sL), FadeOut(sR), aL.animate.set_opacity(0.6), aR.animate.set_opacity(0.6))
        eq = MathTex(r"\text{both areas} = \sin\!\left(\tfrac{\pi}{2}\right) - \sin(0) = 1",
                     font_size=34, color=GOLD).move_to(note)
        self.play(FadeOut(note), FadeIn(eq))
        self.wait(2.5)


# --------------------------------------------------------------------------- 4
class USubAlgebra(Scene):
    def construct(self):
        title = Text("4 · The same move, in symbols", font_size=34, color=INK).to_edge(UP)
        self.play(Write(title))

        l1 = MathTex(r"\int", r"2x", r"\cos(", r"x^2", r")\,dx", font_size=46, color=INK)
        l1[1].set_color(GREEN_); l1[3].set_color(GOLD)
        hint = Text("Spot an inside function (gold) whose derivative (green) is also there.",
                    font_size=24, color=DIM)
        l2 = MathTex(r"u = x^2", r"\qquad", r"du = 2x\,dx", font_size=40, color=INK)
        l2[0].set_color(GOLD); l2[2].set_color(GREEN_)
        l3 = MathTex(r"= \int \cos(u)\,du", font_size=46, color=INK)
        l4 = MathTex(r"= \sin(u) + C", r"\;=\;", r"\sin(x^2) + C", font_size=46, color=INK)
        l4[2].set_color(GOLD)
        chk = MathTex(r"\text{check: }\frac{d}{dx}\sin(x^2) = \cos(x^2)\cdot 2x \;\checkmark",
                      font_size=34, color=GREEN_)
        col = VGroup(l1, hint, l2, l3, l4, chk).arrange(DOWN, buff=0.32).next_to(title, DOWN, buff=0.4)

        self.play(Write(l1)); self.play(FadeIn(hint)); self.wait(1)
        self.play(Write(l2)); self.wait(1)
        self.play(Write(l3)); self.wait(1)
        self.play(Write(l4)); self.wait(1)
        self.play(Write(chk))
        note = Text("u-sub is the chain rule, run backwards.", font_size=28, color=GOLD).to_edge(DOWN)
        self.play(FadeIn(note))
        self.wait(2.5)
        self.play(*[FadeOut(m) for m in (col, note)])

        # your turn
        yt = Text("Your turn", font_size=40, color=GOLD).next_to(title, DOWN, buff=0.6)
        prob = MathTex(r"\int x\,e^{x^2}\,dx", font_size=60, color=INK).next_to(yt, DOWN, buff=0.5)
        pause = Text("Pause the video and solve it before the answer appears.", font_size=26, color=DIM)
        pause.next_to(prob, DOWN, buff=0.5)
        self.play(FadeIn(yt), Write(prob), FadeIn(pause))

        bar = Rectangle(width=8, height=0.08, fill_color=GOLD, fill_opacity=1, stroke_width=0)
        bar.next_to(pause, DOWN, buff=0.5)
        self.add(bar)
        self.play(bar.animate.stretch_to_fit_width(0.01).align_to(bar, LEFT), run_time=8, rate_func=linear)
        self.remove(bar)

        h = MathTex(r"u = x^2,\quad du = 2x\,dx \;\Rightarrow\; x\,dx = \tfrac{1}{2}\,du",
                    font_size=34, color=INK).next_to(pause, DOWN, buff=0.5)
        a = MathTex(r"\int x\,e^{x^2}\,dx = \tfrac12\int e^{u}\,du = \tfrac12 e^{x^2} + C",
                    font_size=40, color=GOLD).next_to(h, DOWN, buff=0.4)
        self.play(FadeIn(h)); self.wait(1.5)
        self.play(Write(a)); self.play(Circumscribe(a, color=GOLD))
        self.wait(3)
