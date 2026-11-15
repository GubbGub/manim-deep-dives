"""
Integrals, Antiderivatives, and u-Substitution, with applications to circuits.
A lecture-style Manim deck. Every word is typeset by LaTeX (Computer Modern).

Render one slide:  manim -pql integrals_eecs.py CapacitorEnergy
Render the deck:   manim -pqh integrals_eecs.py TitleCard Accumulation Families \
                       USubPicture USubAlgebra CapacitorEnergy YourTurn
"""
import numpy as np
from manim import *

BG    = "#FAFAF7"   # paper
INK   = "#1B1B1F"
GRAY  = "#6B6F7A"
RED   = "#A31F34"   # cardinal accent
BLUE  = "#3A6EA5"
SKY   = "#A9C3E0"

config.background_color = BG
Tex.set_default(color=INK)
MathTex.set_default(color=INK)


def axes(xr, yr, w, h, **kw):
    ax = Axes(x_range=xr, y_range=yr, x_length=w, y_length=h, tips=False,
              axis_config={"include_numbers": True, "font_size": 20, "color": GRAY,
                           "stroke_width": 1.5}, **kw)
    for a in (ax.x_axis, ax.y_axis):
        a.numbers.set_color(GRAY)
    return ax


class Lecture(Scene):
    section = ""
    slide = 0

    def frame(self, heading):
        top = Tex(self.section, font_size=24, color=GRAY).to_corner(UL, buff=0.35)
        rule = Line(LEFT * 6.7, RIGHT * 6.7, stroke_width=1.4, color=RED).next_to(top, DOWN, buff=0.1)
        rule.set_x(0)
        foot = Tex(r"Calculus for EECS", font_size=20, color=GRAY).to_corner(DL, buff=0.25)
        num = Tex(str(self.slide), font_size=20, color=GRAY).to_corner(DR, buff=0.25)
        head = Tex(heading, font_size=40).next_to(rule, DOWN, buff=0.25).to_edge(LEFT, buff=0.6)
        self.add(top, rule, foot, num)
        self.play(Write(head), run_time=1)
        return head


def strip(ax, x0, w, h, color=RED):
    return Polygon(ax.c2p(x0, 0), ax.c2p(x0 + w, 0), ax.c2p(x0 + w, h), ax.c2p(x0, h),
                   fill_color=color, fill_opacity=0.85, stroke_width=0)


# ------------------------------------------------------------------ 0
class TitleCard(Scene):
    def construct(self):
        t = Tex(r"Integrals, Antiderivatives,\\and $u$-Substitution", font_size=60)
        r = Line(LEFT, RIGHT, color=RED, stroke_width=2).scale(1.2)
        s = Tex(r"\textit{with applications to charge, energy, and circuits}", font_size=32, color=GRAY)
        g = VGroup(t, r, s).arrange(DOWN, buff=0.45)
        foot = Tex(r"Calculus for EECS \quad\textperiodcentered\quad Lecture notes", font_size=22,
                   color=GRAY).to_edge(DOWN, buff=0.5)
        self.play(Write(t), run_time=2)
        self.play(GrowFromCenter(r), FadeIn(s, shift=UP * 0.2), FadeIn(foot))
        self.wait(2)


# ------------------------------------------------------------------ 1
class Accumulation(Lecture):
    section, slide = r"\textsc{i.} Accumulation", 1

    def construct(self):
        f = lambda x: 0.3 * x**2 + 0.5
        A = lambda x: 0.1 * x**3 + 0.5 * x
        head = self.frame(r"An integral adds up area")

        axL = axes([0, 4.2, 1], [0, 6, 2], 5.4, 3.3).to_corner(DL, buff=0.75)
        axR = axes([0, 4.2, 1], [0, 9, 3], 5.4, 3.3).to_corner(DR, buff=0.75)
        gf = axL.plot(f, x_range=[0, 4], color=INK, stroke_width=3)
        fl = MathTex("f(x)", font_size=32).next_to(axL.c2p(4, f(4)), UL, buff=0.1)
        self.play(Create(axL), Create(gf), Write(fl))

        rects = axL.get_riemann_rectangles(gf, x_range=[0, 4], dx=0.5, fill_opacity=0.6,
                                           stroke_width=0.8, stroke_color=BG, color=[SKY, BLUE])
        self.play(Create(rects))
        for dx in (0.25, 0.1, 0.04):
            self.play(Transform(rects, axL.get_riemann_rectangles(
                gf, x_range=[0, 4], dx=dx, fill_opacity=0.6, stroke_width=0.6 if dx > 0.05 else 0,
                stroke_color=BG, color=[SKY, BLUE])), run_time=1.1)
        cap = Tex(r"$\Delta x \to 0$: the sum becomes the exact area", font_size=26, color=GRAY)
        cap.next_to(axL, UP, buff=0.15)
        self.play(FadeIn(cap)); self.wait(0.6)
        self.play(FadeOut(rects), FadeOut(cap))

        x = ValueTracker(0.02)
        area = always_redraw(lambda: axL.get_area(gf, x_range=[0, x.get_value()], color=SKY, opacity=0.7))
        edge = always_redraw(lambda: axL.get_vertical_line(axL.c2p(x.get_value(), f(x.get_value())),
                                                           color=RED, line_func=Line, stroke_width=4))
        Al = MathTex(r"A(x)=\int_0^x f(t)\,dt", font_size=30).next_to(axR, UP, buff=0.15)
        self.play(Create(axR), Write(Al), FadeIn(area), FadeIn(edge))

        traced = always_redraw(lambda: axR.plot(A, x_range=[0, max(x.get_value(), 0.021)],
                                                color=BLUE, stroke_width=3))
        dot = always_redraw(lambda: Dot(axR.c2p(x.get_value(), A(x.get_value())), color=RED, radius=0.06))
        tan = always_redraw(lambda: Line(
            axR.c2p(x.get_value() - 0.55, A(x.get_value()) - 0.55 * f(x.get_value())),
            axR.c2p(x.get_value() + 0.55, A(x.get_value()) + 0.55 * f(x.get_value())),
            color=RED, stroke_width=2.5))
        r1 = VGroup(Tex(r"height of $f$ =", font_size=28),
                    DecimalNumber(0, num_decimal_places=2, font_size=28, color=RED)).arrange(RIGHT)
        r2 = VGroup(Tex(r"slope of $A$ =", font_size=28),
                    DecimalNumber(0, num_decimal_places=2, font_size=28, color=RED)).arrange(RIGHT)
        readout = VGroup(r1, r2).arrange(DOWN, aligned_edge=LEFT).next_to(head, DOWN, buff=0.25, aligned_edge=LEFT)
        for r in (r1, r2):
            r[1].add_updater(lambda m: m.set_value(f(x.get_value())))
        self.add(traced, dot, tan)
        self.play(FadeIn(readout))
        self.play(x.animate.set_value(4), run_time=6, rate_func=linear)
        punch = MathTex(r"A'(x) = f(x)", font_size=44, color=RED).move_to(readout, aligned_edge=LEFT)
        self.play(FadeOut(readout), Write(punch))
        self.play(Circumscribe(punch, color=RED, buff=0.12)); self.wait(1)

        # ---- engineering reading: Coulomb counting
        fl2 = MathTex(r"i(t)", r"\ \text{current}", font_size=30).move_to(fl, aligned_edge=RIGHT)
        Al2 = MathTex(r"Q(t)=\int_0^t i(\tau)\,d\tau", r"\ \text{charge}", font_size=30).move_to(Al)
        punch2 = MathTex(r"Q'(t) = i(t)", font_size=44, color=RED).move_to(punch, aligned_edge=LEFT)
        note = Tex(r"A battery's charge gauge does exactly this: it measures current and\\"
                   r"integrates it over time. Engineers call it \emph{Coulomb counting}.",
                   font_size=26, color=GRAY).next_to(punch2, RIGHT, buff=0.6)
        self.play(TransformMatchingTex(fl, fl2), TransformMatchingTex(Al, Al2),
                  TransformMatchingTex(punch, punch2))
        self.play(FadeIn(note, shift=LEFT * 0.2))
        self.wait(3)


# ------------------------------------------------------------------ 2
class Families(Lecture):
    section, slide = r"\textsc{ii.} Antiderivatives", 2

    def construct(self):
        head = self.frame(r"Why every antiderivative carries a $+\,C$")
        q = MathTex(r"\text{Which } F \text{ satisfy } F'(x) = 2x\,?", font_size=34)
        q.next_to(head, DOWN, buff=0.3, aligned_edge=LEFT)
        self.play(Write(q))

        ax = axes([-2.5, 2.5, 1], [-2, 8, 2], 6.2, 4.4).to_edge(DOWN, buff=0.55).to_edge(LEFT, buff=0.9)
        Cs = [-1, 0, 1, 2, 3]
        cols = color_gradient([SKY, BLUE], len(Cs))
        curves = VGroup(*[ax.plot(lambda t, c=c: t**2 + c, x_range=[-2.3, 2.3], color=col, stroke_width=3)
                          for c, col in zip(Cs, cols)])
        labels = VGroup(*[MathTex(f"x^2{c:+d}" if c else "x^2", font_size=24, color=col)
                          .next_to(ax.c2p(2.3, 2.3**2 + c), RIGHT, buff=0.08) for c, col in zip(Cs, cols)])
        self.play(Create(ax))
        self.play(LaggedStart(*[Create(c) for c in curves], lag_ratio=0.2), FadeIn(labels))

        x = ValueTracker(-2)
        tans = always_redraw(lambda: VGroup(*[Line(
            ax.c2p(x.get_value() - 0.4, x.get_value()**2 + c - 0.8 * x.get_value()),
            ax.c2p(x.get_value() + 0.4, x.get_value()**2 + c + 0.8 * x.get_value()),
            color=RED, stroke_width=2.5) for c in Cs]))
        sl = VGroup(Tex(r"every slope $=2x=$", font_size=28),
                    DecimalNumber(-4, num_decimal_places=2, font_size=28, color=RED)).arrange(RIGHT)
        sl.next_to(ax, RIGHT, buff=1.4).shift(UP * 1.4)
        sl[1].add_updater(lambda m: m.set_value(2 * x.get_value()))
        self.add(tans); self.play(FadeIn(sl))
        self.play(x.animate.set_value(2), run_time=5, rate_func=smooth)

        ans = MathTex(r"F(x) = x^2 + C", font_size=40, color=RED).move_to(q, aligned_edge=LEFT)
        why = Tex(r"Shifting a curve up or down never changes\\its slope, so the derivative cannot see $C$.",
                  font_size=26).next_to(sl, DOWN, buff=0.45, aligned_edge=LEFT)
        self.play(Transform(q, ans), FadeIn(why)); self.wait(1.5)

        eng = Tex(r"\textbf{In circuits, $C$ is the initial condition.}\\"
                  r"$Q(t) = Q_0 + \int_0^t i\,d\tau$: the integral only knows\\"
                  r"\emph{changes} in charge. A gauge that started\\"
                  r"from the wrong $Q_0$ is wrong forever, which is\\"
                  r"why battery systems recalibrate at full charge.",
                  font_size=24, color=GRAY).next_to(why, DOWN, buff=0.45, aligned_edge=LEFT)
        self.play(FadeIn(eng, shift=UP * 0.15))
        self.wait(3.5)


# ------------------------------------------------------------------ 3
class USubPicture(Lecture):
    section, slide = r"\textsc{iii.} $u$-Substitution", 3

    def construct(self):
        g = lambda x: 2 * x * np.cos(x**2)
        b = np.sqrt(np.pi / 2)
        head = self.frame(r"Substitution is a change of ruler")

        axL = axes([0, 1.4, 0.5], [0, 1.5, 0.5], 5.2, 2.8).to_corner(DL, buff=0.6)
        axR = axes([0, 1.7, 0.5], [0, 1.5, 0.5], 5.2, 2.8).to_corner(DR, buff=0.6)
        xl = MathTex("x", font_size=28, color=GRAY).next_to(axL.x_axis, RIGHT, buff=0.1)
        ul = MathTex("u", font_size=28, color=GRAY).next_to(axR.x_axis, RIGHT, buff=0.1)
        gL = axL.plot(g, x_range=[0, b], color=INK, stroke_width=3)
        gR = axR.plot(np.cos, x_range=[0, np.pi / 2], color=INK, stroke_width=3)
        aL = axL.get_area(gL, x_range=[0, b], color=SKY, opacity=0.5)
        aR = axR.get_area(gR, x_range=[0, np.pi / 2], color=SKY, opacity=0.5)
        iL = MathTex(r"\int_0^{\sqrt{\pi/2}} 2x\cos(x^2)\,dx", font_size=30).next_to(axL, UP, buff=0.15)
        iR = MathTex(r"\int_0^{\pi/2} \cos(u)\,du", font_size=30).next_to(axR, UP, buff=0.15)
        mid = MathTex(r"u = x^2", font_size=34, color=RED).move_to((iL.get_center() + iR.get_center()) / 2)
        self.play(Create(axL), Create(axR), FadeIn(xl, ul))
        self.play(Create(gL), Create(gR), FadeIn(aL, aR), Write(iL), Write(iR), Write(mid))

        dx, x = 0.07, ValueTracker(0.15)
        sL = always_redraw(lambda: strip(axL, x.get_value(), dx, g(x.get_value())))
        sR = always_redraw(lambda: strip(axR, x.get_value()**2, 2 * x.get_value() * dx, np.cos(x.get_value()**2)))
        self.add(sL, sR)
        note = VGroup(
            MathTex(r"\text{width: } dx \;\longrightarrow\; du = 2x\,dx", font_size=28),
            MathTex(r"\text{height: } 2x\cos(x^2) \;\longrightarrow\; \cos(u)", font_size=28),
            MathTex(r"\text{width}\times 2x,\ \text{height}\div 2x\ \Rightarrow\ \text{equal area, strip by strip}",
                    font_size=28, color=RED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).next_to(head, DOWN, buff=0.25, aligned_edge=LEFT)
        self.play(FadeIn(note[0])); self.play(x.animate.set_value(1.1), run_time=3.5)
        self.play(FadeIn(note[1])); self.play(x.animate.set_value(0.3), run_time=3)
        self.play(FadeIn(note[2])); self.play(x.animate.set_value(b - dx), run_time=3.5)
        self.play(FadeOut(sL, sR), aL.animate.set_opacity(0.85), aR.animate.set_opacity(0.85))
        eq = MathTex(r"\text{both areas} = \sin\!\left(\tfrac{\pi}{2}\right) - \sin 0 = 1",
                     font_size=32, color=RED).move_to(note, aligned_edge=LEFT)
        self.play(FadeOut(note), FadeIn(eq)); self.wait(2.5)


# ------------------------------------------------------------------ 4
class USubAlgebra(Lecture):
    section, slide = r"\textsc{iii.} $u$-Substitution", 4

    def construct(self):
        head = self.frame(r"The same move, in symbols")
        l1 = MathTex(r"\int", r"2x", r"\cos(", r"x^2", r")\,dx", font_size=44)
        l1[1].set_color(BLUE); l1[3].set_color(RED)
        hint = Tex(r"Look for an inside function (red) whose derivative (blue) is also present.",
                   font_size=26, color=GRAY)
        l2 = MathTex(r"u = x^2", r"\qquad", r"du = 2x\,dx", font_size=38)
        l2[0].set_color(RED); l2[2].set_color(BLUE)
        l3 = MathTex(r"= \int \cos(u)\,du = \sin(u) + C = \sin(x^2) + C", font_size=42)
        chk = MathTex(r"\text{check: }\ \tfrac{d}{dx}\sin(x^2) = \cos(x^2)\cdot 2x\ \checkmark", font_size=32, color=GRAY)
        col = VGroup(l1, hint, l2, l3, chk).arrange(DOWN, buff=0.35).next_to(head, DOWN, buff=0.45)
        col.set_x(0)
        for m in col:
            self.play(Write(m) if m is not hint else FadeIn(m)); self.wait(0.8)
        take = Tex(r"$u$-substitution is the chain rule, run backwards.", font_size=32, color=RED)
        take.to_edge(DOWN, buff=0.7)
        self.play(FadeIn(take)); self.wait(2.5)


# ------------------------------------------------------------------ 5
class CapacitorEnergy(Lecture):
    section, slide = r"\textsc{iv.} Application", 5

    def construct(self):
        head = self.frame(r"How much energy does a capacitor store?")

        # derivation column
        d = VGroup(
            MathTex(r"P(t) = v(t)\,i(t)", font_size=32),
            MathTex(r"i(t) = C\,\frac{dv}{dt}", font_size=32),
            MathTex(r"W = \int_0^T C\,v(t)\,v'(t)\,dt", font_size=32),
            MathTex(r"u = v(t),\quad du = v'(t)\,dt", font_size=30, color=RED),
            MathTex(r"W = \int_0^{V} C\,u\,du = \tfrac12\,C\,V^2", font_size=36),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.32).next_to(head, DOWN, buff=0.45, aligned_edge=LEFT)
        tags = VGroup(
            Tex(r"power into the capacitor", font_size=22, color=GRAY),
            Tex(r"capacitor law", font_size=22, color=GRAY),
            Tex(r"energy = $\int$ power", font_size=22, color=GRAY),
        )
        for t, m in zip(tags, d[:3]):
            t.next_to(m, RIGHT, buff=0.3)

        # charging curve v(t) = V(1 - e^{-t/tau}), V = C = tau = 1
        v = lambda t: 1 - np.exp(-t)
        dv = lambda t: np.exp(-t)
        p = lambda t: v(t) * dv(t)
        axT = axes([0, 5, 1], [0, 0.3, 0.1], 4.5, 2.0).to_edge(RIGHT, buff=1.1).shift(UP * 0.85)
        axU = axes([0, 1.05, 0.5], [0, 1.05, 0.5], 4.5, 2.0).next_to(axT, DOWN, buff=0.7)
        tT = MathTex("t", font_size=26, color=GRAY).next_to(axT.x_axis, RIGHT, buff=0.1)
        tU = MathTex("u", font_size=26, color=GRAY).next_to(axU.x_axis, RIGHT, buff=0.1)
        gT = axT.plot(p, x_range=[0, 5], color=INK, stroke_width=3)
        gU = axU.plot(lambda u: u, x_range=[0, 1], color=INK, stroke_width=3)
        aT = axT.get_area(gT, x_range=[0, 5], color=SKY, opacity=0.5)
        aU = axU.get_area(gU, x_range=[0, 1], color=SKY, opacity=0.5)
        lT = MathTex(r"C\,v\,v'\ \text{vs. time}", font_size=24, color=GRAY).next_to(axT, UP, buff=0.08)
        lU = MathTex(r"C\,u\ \text{vs. voltage } u = v", font_size=24, color=GRAY).next_to(axU, UP, buff=0.08)

        self.play(Write(d[0]), FadeIn(tags[0])); self.play(Write(d[1]), FadeIn(tags[1]))
        self.play(Write(d[2]), FadeIn(tags[2]))
        self.play(Create(axT), FadeIn(tT, lT), Create(gT), FadeIn(aT))
        self.play(Write(d[3]))
        self.play(Create(axU), FadeIn(tU, lU), Create(gU), FadeIn(aU))

        dt, t = 0.18, ValueTracker(0.1)
        sT = always_redraw(lambda: strip(axT, t.get_value(), dt, p(t.get_value())))
        sU = always_redraw(lambda: strip(axU, v(t.get_value()), dv(t.get_value()) * dt, v(t.get_value())))
        self.add(sT, sU)
        self.play(t.animate.set_value(4.3), run_time=6, rate_func=linear)
        self.play(FadeOut(sT, sU))
        self.play(Write(d[4])); self.play(Circumscribe(d[4], color=RED, buff=0.1))

        take = Tex(r"Double the voltage and you store \emph{four} times the energy,\\"
                   r"which is why a camera flash charges its\\capacitor to hundreds of volts.",
                   font_size=23, color=GRAY).next_to(d, DOWN, buff=0.4, aligned_edge=LEFT)
        self.play(FadeIn(take)); self.wait(3.5)


# ------------------------------------------------------------------ 6
class YourTurn(Lecture):
    section, slide = r"\textsc{iv.} Application", 6

    def construct(self):
        head = self.frame(r"Your turn: energy in an inductor")
        given = VGroup(
            Tex(r"An inductor obeys $\;v(t) = L\,\dfrac{di}{dt}$.", font_size=32),
            Tex(r"Its current ramps from $0$ to $I$. Find the stored energy", font_size=32),
            MathTex(r"W = \int_0^T v(t)\,i(t)\,dt.", font_size=40),
        ).arrange(DOWN, buff=0.22).next_to(head, DOWN, buff=0.3).set_x(0)
        self.play(FadeIn(given[0])); self.play(FadeIn(given[1])); self.play(Write(given[2]))
        pause = Tex(r"\textit{Pause and work it out before the answer appears.}", font_size=26, color=GRAY)
        pause.next_to(given, DOWN, buff=0.4)
        bar = Rectangle(width=7, height=0.06, fill_color=RED, fill_opacity=1, stroke_width=0)
        bar.next_to(pause, DOWN, buff=0.3)
        self.play(FadeIn(pause)); self.add(bar)
        self.play(bar.animate.stretch_to_fit_width(0.01).align_to(bar, LEFT), run_time=10, rate_func=linear)
        self.remove(bar)
        self.play(FadeOut(pause))

        sol = VGroup(
            MathTex(r"W = \int_0^T L\,i(t)\,i'(t)\,dt", font_size=30),
            MathTex(r"u = i(t),\quad du = i'(t)\,dt", font_size=28, color=RED),
            MathTex(r"W = \int_0^{I} L\,u\,du = \tfrac12\,L\,I^2", font_size=36),
        ).arrange(DOWN, buff=0.22).next_to(given, DOWN, buff=0.4)
        for m in sol:
            self.play(Write(m)); self.wait(0.6)
        self.play(Circumscribe(sol[2], color=RED, buff=0.1))
        duo = Tex(r"$\tfrac12 CV^2$ and $\tfrac12 LI^2$: capacitors store energy in voltage, inductors in current.",
                  font_size=24, color=GRAY).to_edge(DOWN, buff=0.55)
        self.play(FadeIn(duo)); self.wait(3.5)
