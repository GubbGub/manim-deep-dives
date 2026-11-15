"""
Integrals, Antiderivatives, and u-Substitution, with applications to circuits.

Styled to match gubbgub.github.io (light mode): Apple light-gray canvas,
white cards with hairline borders, serif headings, [MONO] labels, blue accent.
Equations and headings are typeset by LaTeX in Charter.

Render one slide:  manim -pql integrals_eecs.py CapacitorEnergy
Render the deck:   manim -pqh integrals_eecs.py TitleCard Accumulation Families \
                       USubPicture USubAlgebra CapacitorEnergy YourTurn

Fonts: Charter (via LaTeX), Inter (sans), JetBrains Mono (labels).
"""
import numpy as np
from manim import *

# ---- design tokens (same names as style.css :root) -------------------------
CANVAS  = "#F5F5F7"
SURFACE = "#FFFFFF"
INK     = "#1D1D1F"
INK_2   = "#515154"
INK_3   = "#86868B"
LINE    = "#E5E5EA"
ACCENT  = "#0071E3"
GOOD    = "#248A3D"
SOFT    = "#9CC7F3"   # lighter accent for gradients

SANS, MONO = "Inter", "JetBrains Mono"
TOTAL = 6

config.background_color = CANVAS
_tpl = TexTemplate()
_tpl.add_to_preamble(r"\usepackage[T1]{fontenc}\usepackage{charter}\usepackage[italic]{mathastext}")
config.tex_template = _tpl
Tex.set_default(color=INK)
MathTex.set_default(color=INK)


# ---- building blocks --------------------------------------------------------
def tag(text, size=15, color=INK_3):
    return Text(f"[{text.upper()}]", font=MONO, font_size=size, color=color)


def sans(text, size=20, color=INK_2, weight=NORMAL):
    return Text(text, font=SANS, font_size=size, color=color, weight=weight)


def para(tex, size=26, color=INK_2):
    return Tex(tex, font_size=size, color=color, tex_environment="flushleft")


def card(w, h):
    return RoundedRectangle(corner_radius=0.22, width=w, height=h, fill_color=SURFACE,
                            fill_opacity=1, stroke_color=LINE, stroke_width=1.2)


def axes(xr, yr, w, h):
    ax = Axes(x_range=xr, y_range=yr, x_length=w, y_length=h, tips=False,
              axis_config={"include_numbers": True, "font_size": 18, "color": INK_3,
                           "stroke_width": 1.2})
    for a in (ax.x_axis, ax.y_axis):
        a.numbers.set_color(INK_3)
    return ax


def panel(ax, label, w=None, h=None):
    """White card around an axes, with a [LABEL] in its top-left corner."""
    w = w or ax.width + 0.9
    h = h or ax.height + 1.15
    c = card(w, h).move_to(ax).shift(UP * 0.2)
    t = tag(label, 13).move_to(c.get_corner(UL) + RIGHT * 0.3 + DOWN * 0.3, aligned_edge=UL)
    return c, t


def strip(ax, x0, w, h):
    return Polygon(ax.c2p(x0, 0), ax.c2p(x0 + w, 0), ax.c2p(x0 + w, h), ax.c2p(x0, h),
                   fill_color=ACCENT, fill_opacity=0.9, stroke_width=0)


class Lecture(Scene):
    label, slide = "", 0

    def frame(self, heading):
        brand = sans("Jared Bridgewater", 17, INK, SEMIBOLD).to_corner(UL, buff=0.3)
        crumb = sans("Deep Dives  ·  Integrals", 15, INK_2).to_corner(UR, buff=0.3)
        crumb.match_y(brand)
        bar = Line(LEFT * 7.2, RIGHT * 7.2, stroke_width=1, color=LINE).next_to(brand, DOWN, buff=0.22)
        bar.set_x(0)
        num = Text(f"{self.slide:02d} / {TOTAL:02d}", font=MONO, font_size=13, color=INK_3)
        num.to_corner(DR, buff=0.3)
        t = tag(self.label).next_to(bar, DOWN, buff=0.35).to_edge(LEFT, buff=0.8)
        h = Tex(heading, font_size=50).next_to(t, DOWN, buff=0.14, aligned_edge=LEFT)
        self.add(brand, crumb, bar, num)
        self.play(FadeIn(t), Write(h), run_time=1)
        return h


# ------------------------------------------------------------------ 0
class TitleCard(Scene):
    def construct(self):
        brand = sans("Jared Bridgewater", 17, INK, SEMIBOLD).to_corner(UL, buff=0.3)
        bar = Line(LEFT * 7.2, RIGHT * 7.2, stroke_width=1, color=LINE).next_to(brand, DOWN, buff=0.22)
        bar.set_x(0)
        t = tag("Deep dive")
        title = Tex(r"Integrals, antiderivatives,\\and $u$-substitution.", font_size=76,
                    tex_environment="flushleft")
        lede = para(r"Where area, slope and change of variables meet,\\"
                    r"and why they show up in every circuit.", 30)
        hero = VGroup(t, title, lede).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        hero.to_edge(LEFT, buff=1.0).shift(UP * 0.75)

        cells = [("Accumulate", "Area under a curve"), ("Families", r"Why answers get a $+C$"),
                 ("Substitute", "A change of ruler"), ("Apply", "Energy in circuits")]
        row = card(12.2, 1.25)
        row.next_to(hero, DOWN, buff=0.55).set_x(0)
        cw = row.width / 4
        content = VGroup()
        for i, (k, v) in enumerate(cells):
            x0 = row.get_left()[0] + i * cw
            g = VGroup(tag(k, 12), Tex(v, font_size=24)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
            g.move_to([x0 + 0.3, row.get_y(), 0], aligned_edge=LEFT)
            content.add(g)
            if i:
                content.add(Line([x0, row.get_top()[1], 0], [x0, row.get_bottom()[1], 0],
                                 color=LINE, stroke_width=1.2))
        self.add(brand, bar)
        self.play(FadeIn(t), Write(title), run_time=2)
        self.play(FadeIn(lede, shift=UP * 0.15))
        self.play(FadeIn(row), LaggedStart(*[FadeIn(m) for m in content], lag_ratio=0.12))
        self.wait(2)


# ------------------------------------------------------------------ 1
class Accumulation(Lecture):
    label, slide = "Accumulation", 1

    def construct(self):
        f = lambda x: 0.3 * x**2 + 0.5
        A = lambda x: 0.1 * x**3 + 0.5 * x
        head = self.frame(r"An integral adds up area")

        axL = axes([0, 4.2, 1], [0, 6, 2], 5.1, 2.75).move_to([-3.45, -1.45, 0])
        axR = axes([0, 4.2, 1], [0, 9, 3], 5.1, 2.75).move_to([3.45, -1.45, 0])
        cL, tL = panel(axL, "Rate")
        cR, tR = panel(axR, "Accumulated")
        gf = axL.plot(f, x_range=[0, 4], color=INK, stroke_width=2.5)
        fl = MathTex("f(x)", font_size=30).next_to(tL, RIGHT, buff=0.3)
        self.play(FadeIn(cL, tL), Create(axL), Create(gf), Write(fl))

        rk = dict(fill_opacity=0.5, stroke_width=0.8, stroke_color=SURFACE, color=[SOFT, ACCENT])
        rects = axL.get_riemann_rectangles(gf, x_range=[0, 4], dx=0.5, **rk)
        cap = para(r"$\Delta x \to 0$: the sum becomes the exact area", 24, INK_3)
        cap.next_to(head, RIGHT, buff=0.8).align_to(head, DOWN)
        self.play(Create(rects))
        for dx in (0.25, 0.1, 0.04):
            rk["stroke_width"] = 0.6 if dx > 0.05 else 0
            self.play(Transform(rects, axL.get_riemann_rectangles(gf, x_range=[0, 4], dx=dx, **rk)),
                      run_time=1.1)
        self.play(FadeIn(cap)); self.wait(0.6)
        self.play(FadeOut(rects), FadeOut(cap))

        x = ValueTracker(0.02)
        area = always_redraw(lambda: axL.get_area(gf, x_range=[0, x.get_value()], color=ACCENT, opacity=0.16))
        edge = always_redraw(lambda: axL.get_vertical_line(axL.c2p(x.get_value(), f(x.get_value())),
                                                           color=ACCENT, line_func=Line, stroke_width=3.5))
        Al = MathTex(r"A(x)=\int_0^x f(t)\,dt", font_size=26).next_to(tR, RIGHT, buff=0.3)
        self.play(FadeIn(cR, tR), Create(axR), Write(Al), FadeIn(area), FadeIn(edge))

        traced = always_redraw(lambda: axR.plot(A, x_range=[0, max(x.get_value(), 0.021)],
                                                color=ACCENT, stroke_width=2.8))
        dot = always_redraw(lambda: Dot(axR.c2p(x.get_value(), A(x.get_value())), color=ACCENT, radius=0.06))
        tan = always_redraw(lambda: Line(
            axR.c2p(x.get_value() - 0.55, A(x.get_value()) - 0.55 * f(x.get_value())),
            axR.c2p(x.get_value() + 0.55, A(x.get_value()) + 0.55 * f(x.get_value())),
            color=INK, stroke_width=2))

        def row(name):
            return VGroup(tag(name, 13), DecimalNumber(0, num_decimal_places=2, font_size=34, color=ACCENT)
                          ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        r1, r2 = row("height of f"), row("slope of A")
        readout = VGroup(r1, r2).arrange(RIGHT, buff=0.9)
        rc = card(readout.width + 0.7, readout.height + 0.5).move_to(readout)
        rbox = VGroup(rc, readout).to_edge(RIGHT, buff=0.8).align_to(head, DOWN)
        for r in (r1, r2):
            r[1].add_updater(lambda m: m.set_value(f(x.get_value())))
        self.add(traced, dot, tan)
        self.play(FadeIn(rbox))
        self.play(x.animate.set_value(4), run_time=6, rate_func=linear)

        punch = MathTex(r"A'(x) = f(x)", font_size=46, color=ACCENT).move_to(readout)
        self.play(FadeOut(readout), Write(punch))
        self.play(Indicate(punch, color=ACCENT, scale_factor=1.08)); self.wait(1)

        # ---- the engineering reading: Coulomb counting
        tL2, tR2 = tag("Current", 13).move_to(tL, aligned_edge=LEFT), tag("Charge", 13).move_to(tR, aligned_edge=LEFT)
        fl2 = MathTex(r"i(t)", font_size=30).next_to(tL2, RIGHT, buff=0.3)
        Al2 = MathTex(r"Q(t)=\int_0^t i(\tau)\,d\tau", font_size=26).next_to(tR2, RIGHT, buff=0.3)
        punch2 = MathTex(r"Q'(t) = i(t)", font_size=46, color=ACCENT).move_to(punch)
        note = para(r"A battery's charge gauge does exactly this: it measures current\\"
                    r"and integrates it over time. Engineers call it \emph{Coulomb counting}.", 22)
        note.next_to(VGroup(cL, cR), UP, buff=0.3).align_to(cL, LEFT)
        self.play(*[Transform(a, b) for a, b in ((tL, tL2), (tR, tR2), (fl, fl2), (Al, Al2), (punch, punch2))])
        self.play(FadeIn(note, shift=UP * 0.1))
        self.wait(3)


# ------------------------------------------------------------------ 2
class Families(Lecture):
    label, slide = "Antiderivatives", 2

    def construct(self):
        head = self.frame(r"Why every antiderivative carries a $+\,C$")

        ax = axes([-2.5, 2.5, 1], [-2, 8, 2], 5.6, 4.0).move_to([-3.3, -1.05, 0])
        c, t = panel(ax, r"Solutions of F'(x) = 2x", h=ax.height + 1.0)
        Cs = [-1, 0, 1, 2, 3]
        cols = color_gradient([SOFT, ACCENT], len(Cs))
        curves = VGroup(*[ax.plot(lambda s, k=k: s**2 + k, x_range=[-2.3, 2.3], color=col, stroke_width=2.6)
                          for k, col in zip(Cs, cols)])
        self.play(FadeIn(c, t), Create(ax))
        self.play(LaggedStart(*[Create(cv) for cv in curves], lag_ratio=0.2))

        x = ValueTracker(-2)
        tans = always_redraw(lambda: VGroup(*[Line(
            ax.c2p(x.get_value() - 0.4, x.get_value()**2 + k - 0.8 * x.get_value()),
            ax.c2p(x.get_value() + 0.4, x.get_value()**2 + k + 0.8 * x.get_value()),
            color=INK, stroke_width=2) for k in Cs]))

        # right column
        sl_card = card(5.6, 1.15)
        sl = VGroup(tag("every slope = 2x", 13),
                    DecimalNumber(-4, num_decimal_places=2, font_size=36, color=ACCENT)
                    ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        sl_card.move_to([3.55, 1.0, 0]); sl.move_to(sl_card).align_to(sl_card, LEFT).shift(RIGHT * 0.35)
        sl[1].add_updater(lambda m: m.set_value(2 * x.get_value()))
        self.add(tans); self.play(FadeIn(sl_card, sl))
        self.play(x.animate.set_value(2), run_time=5, rate_func=smooth)

        ans = MathTex(r"F(x) = x^2 + C", font_size=46, color=ACCENT).next_to(sl_card, DOWN, buff=0.4)
        ans.align_to(sl_card, LEFT)
        why = para(r"Shifting a curve up or down never changes its slope,\\"
                   r"so the derivative cannot see $C$.", 24).next_to(ans, DOWN, buff=0.2, aligned_edge=LEFT)
        self.play(Write(ans), FadeIn(why)); self.wait(1.2)

        eng_c = card(5.6, 1.95).next_to(why, DOWN, buff=0.3).align_to(sl_card, LEFT)
        eng = VGroup(tag("In circuits", 13),
                     para(r"$C$ is the initial condition. In $Q(t) = Q_0 + \int_0^t i\,d\tau$\\"
                          r"the integral only measures \emph{change}, so a gauge\\"
                          r"that starts from the wrong $Q_0$ stays wrong. That's\\"
                          r"why battery systems recalibrate at full charge.", 22, INK)
                     ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        eng.move_to(eng_c).align_to(eng_c, LEFT).shift(RIGHT * 0.3)
        self.play(FadeIn(eng_c, eng, shift=UP * 0.1))
        self.wait(3.5)


# ------------------------------------------------------------------ 3
class USubPicture(Lecture):
    label, slide = "u-Substitution", 3

    def construct(self):
        g = lambda x: 2 * x * np.cos(x**2)
        b = np.sqrt(np.pi / 2)
        head = self.frame(r"Substitution is a change of ruler")

        axL = axes([0, 1.4, 0.5], [0, 1.5, 0.5], 5.0, 2.1).move_to([-3.45, -1.95, 0])
        axR = axes([0, 1.7, 0.5], [0, 1.5, 0.5], 5.0, 2.1).move_to([3.45, -1.95, 0])
        cL, tL = panel(axL, "In x", h=axL.height + 1.3)
        cR, tR = panel(axR, "In u", h=axR.height + 1.3)
        for cc, tt in ((cL, tL), (cR, tR)):
            cc.shift(UP * 0.15); tt.shift(UP * 0.15)
        gL = axL.plot(g, x_range=[0, b], color=INK, stroke_width=2.5)
        gR = axR.plot(np.cos, x_range=[0, np.pi / 2], color=INK, stroke_width=2.5)
        aL = axL.get_area(gL, x_range=[0, b], color=ACCENT, opacity=0.14)
        aR = axR.get_area(gR, x_range=[0, np.pi / 2], color=ACCENT, opacity=0.14)
        iL = MathTex(r"\int_0^{\sqrt{\pi/2}} 2x\cos(x^2)\,dx", font_size=28).next_to(cL.get_corner(UR), DL, buff=0.22)
        iR = MathTex(r"\int_0^{\pi/2} \cos(u)\,du", font_size=28).next_to(cR.get_corner(UR), DL, buff=0.22)
        self.play(FadeIn(cL, tL, cR, tR), Create(axL), Create(axR))
        self.play(Create(gL), Create(gR), FadeIn(aL, aR), Write(iL), Write(iR))

        dx, x = 0.07, ValueTracker(0.15)
        sL = always_redraw(lambda: strip(axL, x.get_value(), dx, g(x.get_value())))
        sR = always_redraw(lambda: strip(axR, x.get_value()**2, 2 * x.get_value() * dx, np.cos(x.get_value()**2)))
        self.add(sL, sR)

        nc = card(12.8, 1.45).next_to(head, DOWN, buff=0.3).set_x(0)
        note = VGroup(
            MathTex(r"\text{width: } dx \;\longrightarrow\; du = 2x\,dx", font_size=26),
            MathTex(r"\text{height: } 2x\cos(x^2) \;\longrightarrow\; \cos(u)", font_size=26),
            MathTex(r"\text{width}\times 2x,\ \text{height}\div 2x\ \Rightarrow\ \text{equal area, strip by strip}",
                    font_size=26, color=ACCENT),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1).move_to(nc).align_to(nc, LEFT).shift(RIGHT * 0.35)
        mid = VGroup(tag("substitute", 12), MathTex(r"u = x^2", font_size=40, color=ACCENT)
                     ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        mid.move_to(nc).align_to(nc, RIGHT).shift(LEFT * 0.5)
        self.play(FadeIn(nc), FadeIn(mid), FadeIn(note[0])); self.play(x.animate.set_value(1.1), run_time=3.5)
        self.play(FadeIn(note[1])); self.play(x.animate.set_value(0.3), run_time=3)
        self.play(FadeIn(note[2])); self.play(x.animate.set_value(b - dx), run_time=3.5)
        self.play(FadeOut(sL, sR), aL.animate.set_opacity(0.35), aR.animate.set_opacity(0.35))
        eq = MathTex(r"\text{both areas} = \sin\!\left(\tfrac{\pi}{2}\right) - \sin 0 = 1",
                     font_size=34, color=ACCENT).move_to(nc)
        eq.align_to(nc, LEFT).shift(RIGHT * 0.35)
        self.play(FadeOut(note), FadeIn(eq)); self.wait(2.5)


# ------------------------------------------------------------------ 4
class USubAlgebra(Lecture):
    label, slide = "u-Substitution", 4

    def construct(self):
        head = self.frame(r"The same move, in symbols")
        l1 = MathTex(r"\int", r"2x", r"\cos(", r"x^2", r")\,dx", font_size=44)
        l1[1].set_color(GOOD); l1[3].set_color(ACCENT)
        hint = para(r"Look for an inside function (blue) whose derivative (green) is also there.", 24, INK_3)
        l2 = MathTex(r"u = x^2", r"\qquad", r"du = 2x\,dx", font_size=36)
        l2[0].set_color(ACCENT); l2[2].set_color(GOOD)
        l3 = MathTex(r"= \int \cos(u)\,du = \sin(u) + C = \sin(x^2) + C", font_size=40)
        chk = MathTex(r"\text{check: }\ \tfrac{d}{dx}\sin(x^2) = \cos(x^2)\cdot 2x\ \checkmark", font_size=30, color=GOOD)
        col = VGroup(l1, hint, l2, l3, chk).arrange(DOWN, buff=0.32)
        c = card(10.6, col.height + 0.8)
        VGroup(c, col).next_to(head, DOWN, buff=0.35).set_x(0)
        col.move_to(c)
        self.play(FadeIn(c))
        for m in col:
            self.play(Write(m) if m is not hint else FadeIn(m)); self.wait(0.7)
        take = Tex(r"$u$-substitution is the chain rule, run backwards.", font_size=32, color=ACCENT)
        take.next_to(c, DOWN, buff=0.35)
        self.play(FadeIn(take)); self.wait(2.5)


# ------------------------------------------------------------------ 5
class CapacitorEnergy(Lecture):
    label, slide = "Application", 5

    def construct(self):
        head = self.frame(r"How much energy does a capacitor store?")

        d = VGroup(
            MathTex(r"P(t) = v(t)\,i(t)", font_size=30),
            MathTex(r"i(t) = C\,\frac{dv}{dt}", font_size=30),
            MathTex(r"W = \int_0^T C\,v(t)\,v'(t)\,dt", font_size=30),
            MathTex(r"u = v(t),\quad du = v'(t)\,dt", font_size=28, color=ACCENT),
            MathTex(r"W = \int_0^{V} C\,u\,du = \tfrac12\,C\,V^2", font_size=36),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        tags = VGroup(tag("power in", 12), tag("capacitor law", 12), tag("energy = ∫ power", 12))
        dc = card(6.4, 5.45).move_to([-3.55, -0.9, 0])
        dt_ = tag("Derivation", 13).move_to(dc.get_corner(UL) + RIGHT * 0.3 + DOWN * 0.3, aligned_edge=UL)
        d.next_to(dt_, DOWN, buff=0.22, aligned_edge=LEFT)
        for tg, m in zip(tags, d[:3]):
            tg.next_to(m, RIGHT, buff=0.3)
        self.play(FadeIn(dc, dt_))

        v = lambda t: 1 - np.exp(-t)
        dv = lambda t: np.exp(-t)
        p = lambda t: v(t) * dv(t)
        axT = axes([0, 5, 1], [0, 0.3, 0.1], 4.6, 1.35).move_to([3.5, 0.5, 0])
        axU = axes([0, 1.05, 0.5], [0, 1.05, 0.5], 4.6, 1.35).move_to([3.5, -2.4, 0])
        cT, tT = panel(axT, "Power vs. time", h=axT.height + 0.95)
        cU, tU = panel(axU, "Cu vs. voltage u = v", h=axU.height + 0.95)
        gT = axT.plot(p, x_range=[0, 5], color=INK, stroke_width=2.5)
        gU = axU.plot(lambda u: u, x_range=[0, 1], color=INK, stroke_width=2.5)
        aT = axT.get_area(gT, x_range=[0, 5], color=ACCENT, opacity=0.14)
        aU = axU.get_area(gU, x_range=[0, 1], color=ACCENT, opacity=0.14)

        self.play(Write(d[0]), FadeIn(tags[0])); self.play(Write(d[1]), FadeIn(tags[1]))
        self.play(Write(d[2]), FadeIn(tags[2]))
        self.play(FadeIn(cT, tT), Create(axT), Create(gT), FadeIn(aT))
        self.play(Write(d[3]))
        self.play(FadeIn(cU, tU), Create(axU), Create(gU), FadeIn(aU))

        step, t = 0.18, ValueTracker(0.1)
        sT = always_redraw(lambda: strip(axT, t.get_value(), step, p(t.get_value())))
        sU = always_redraw(lambda: strip(axU, v(t.get_value()), dv(t.get_value()) * step, v(t.get_value())))
        self.add(sT, sU)
        self.play(t.animate.set_value(4.3), run_time=6, rate_func=linear)
        self.play(FadeOut(sT, sU))
        self.play(Write(d[4])); self.play(Indicate(d[4], color=ACCENT, scale_factor=1.05))

        take = para(r"Double the voltage, store \emph{four} times the energy.\\"
                    r"That's why a camera flash charges to hundreds of volts.", 20, INK_2)
        take.next_to(d, DOWN, buff=0.22, aligned_edge=LEFT)
        self.play(FadeIn(take)); self.wait(3.5)


# ------------------------------------------------------------------ 6
class YourTurn(Lecture):
    label, slide = "Your turn", 6

    def construct(self):
        head = self.frame(r"Energy in an inductor")
        c = card(11.6, 5.15).next_to(head, DOWN, buff=0.3).set_x(0)
        given = VGroup(
            Tex(r"An inductor obeys $\;v(t) = L\,\dfrac{di}{dt}$. Its current ramps from $0$ to $I$.", font_size=30),
            MathTex(r"\text{Find}\quad W = \int_0^T v(t)\,i(t)\,dt.", font_size=36),
        ).arrange(DOWN, buff=0.25).next_to(c.get_top(), DOWN, buff=0.35)
        self.play(FadeIn(c), FadeIn(given[0])); self.play(Write(given[1]))

        pause = tag("Pause and work it out before the answer appears", 13).next_to(given, DOWN, buff=0.4)
        track = RoundedRectangle(corner_radius=0.04, width=7, height=0.08, fill_color=LINE, fill_opacity=1,
                                 stroke_width=0).next_to(pause, DOWN, buff=0.25)
        bar = track.copy().set_fill(ACCENT)
        self.play(FadeIn(pause, track)); self.add(bar)
        self.play(bar.animate.stretch_to_fit_width(0.02).align_to(track, LEFT), run_time=10, rate_func=linear)
        self.play(FadeOut(pause, track, bar))

        sol = VGroup(
            MathTex(r"W = \int_0^T L\,i(t)\,i'(t)\,dt", font_size=30),
            MathTex(r"u = i(t),\quad du = i'(t)\,dt", font_size=28, color=ACCENT),
            MathTex(r"W = \int_0^{I} L\,u\,du = \tfrac12\,L\,I^2", font_size=38),
        ).arrange(DOWN, buff=0.22).next_to(given, DOWN, buff=0.4)
        for m in sol:
            self.play(Write(m)); self.wait(0.5)
        self.play(Indicate(sol[2], color=ACCENT, scale_factor=1.05))
        duo = para(r"$\tfrac12 CV^2$ and $\tfrac12 LI^2$: capacitors store energy in voltage, inductors in current.",
                   22, INK_3).next_to(c, DOWN, buff=0.25)
        self.play(FadeIn(duo)); self.wait(3.5)
