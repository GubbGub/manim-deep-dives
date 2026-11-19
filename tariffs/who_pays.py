"""Who actually pays a tariff?  (companion to gubbgub.github.io/tariffs.html, Figure 2)

Render:  cd tariffs && manim -pqh who_pays.py WhoPays

The model: a part costs $100 from a foreign exporter, and the U.S. adds a 25% tariff.
If the exporter keeps its price, Americans pay the whole tariff. If it cuts its price
to $80, the tariff is 25% of $80 = $20 and the importer still pays $100, so the
exporter has effectively paid it. Real life lands in between; the studies in the
article tell us where.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))   # so site_style.py next to this file is found

from manim import *
from site_style import *
LABEL_FONT = LABEL

T = 0.25                  # tariff rate
K = 0.034                 # scene units per dollar (bar height)
BASE = -2.55              # bar baseline (y)
EX_X, IM_X, BAR_W = -4.7, -2.3, 1.45


def share_us(p):
    """Share of the tariff borne in the U.S. when the exporter charges p."""
    return max(0.0, (1 + T) * p - 100) / (T * p)


def price_for_share(s):
    """Exporter price that gives a U.S. share s.  From (1+T)p - 100 = s*T*p."""
    return 100 / (1 + T - s * T)


def label(text, size=24, color=INK, font=SANS, weight=NORMAL):
    return Text(text, font=font, font_size=size, color=color, weight=weight)


class WhoPays(Scene):
    def construct(self):
        p = ValueTracker(100)     # what the exporter charges
        on = ValueTracker(0)      # 0 = no tariff yet, 1 = tariff applied
        grow = ValueTracker(0)    # 0 -> 1 as the bars rise into place at the start
        y = lambda dollars: BASE + dollars * K

        # ---------- Title ----------
        tag = label("DEEP DIVE · ECONOMICS", 18, INK_3, LABEL)
        title = label("Who actually pays a tariff?", 54, INK, SERIF)
        VGroup(tag, title).arrange(DOWN, buff=0.3)
        self.play(FadeIn(tag, shift=UP * 0.2), Write(title), run_time=1.6)
        self.wait(1.2)
        header = label("Who actually pays a tariff?", 30, INK, SERIF).to_corner(UL, buff=0.5)
        self.play(FadeOut(tag), ReplacementTransform(title, header))

        # ---------- The bars ----------
        axis = Line([EX_X - 1.1, BASE, 0], [IM_X + 1.1, BASE, 0], color=INK_3, stroke_width=2)

        def ex_bar():
            return Rectangle(width=BAR_W, height=max(grow.get_value() * p.get_value() * K, 0.001), stroke_width=0,
                             fill_color=INK_3, fill_opacity=0.45).move_to([EX_X, BASE, 0], aligned_edge=DOWN)

        def im_base():
            return Rectangle(width=BAR_W, height=max(grow.get_value() * p.get_value() * K, 0.001), stroke_width=0,
                             fill_color=INK_3, fill_opacity=0.45).move_to([IM_X, BASE, 0], aligned_edge=DOWN)

        def tariff_block():
            h = max(on.get_value() * T * p.get_value() * K, 0.001)
            return Rectangle(width=BAR_W, height=h, stroke_width=0, fill_color=ACCENT,
                             fill_opacity=on.get_value()).move_to([IM_X, y(p.get_value()), 0], aligned_edge=DOWN)

        bars = VGroup(always_redraw(ex_bar), always_redraw(im_base), always_redraw(tariff_block))

        ex_value = always_redraw(lambda: label(f"${p.get_value():.0f}", 28, INK, weight=BOLD)
                                 .move_to([EX_X, y(p.get_value() * grow.get_value()) - 0.35, 0])
                                 .set_opacity(max(0, grow.get_value() * 2 - 1)))
        im_value = always_redraw(lambda: label(f"${p.get_value() * (1 + T * on.get_value()):.0f}", 30, INK, weight=BOLD)
                                 .next_to([IM_X, y(grow.get_value() * p.get_value() * (1 + T * on.get_value())), 0], UP, buff=0.15)
                                 .set_opacity(max(0, grow.get_value() * 2 - 1)))
        ex_name = label("Exporter receives", 18, INK_2).next_to([EX_X, BASE, 0], DOWN, buff=0.2)
        im_name = label("Importer pays", 18, INK_2).next_to([IM_X, BASE, 0], DOWN, buff=0.2)

        ref = DashedLine([EX_X - 1.0, y(100), 0], [IM_X + 1.0, y(100), 0], color=INK_2, dash_length=0.12, stroke_width=2)
        ref_label = label("Price before the tariff", 16, INK_2).next_to(ref, UP, buff=0.1).align_to(ref, LEFT)

        self.play(Create(axis), FadeIn(ex_name, shift=UP * 0.1), FadeIn(im_name, shift=UP * 0.1), run_time=1)
        self.add(bars, ex_value, im_value)
        # LEARN: the bars' heights are tied to `grow`, so animating it from 0 to 1 makes them rise smoothly.
        self.play(grow.animate.set_value(1), run_time=1.8, rate_func=smooth)
        self.play(Create(ref), FadeIn(ref_label), run_time=1)

        # ---------- Right-hand panel ----------
        panel_x = 0.6

        def note(*lines, size=23):
            g = VGroup(*[label(l, size, INK if i == 0 else INK_2, weight=BOLD if i == 0 else NORMAL)
                         for i, l in enumerate(lines)]).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
            g.move_to([panel_x, 2.6, 0], aligned_edge=UL)
            # Keep a safe margin from the right edge of the frame, whatever the text says.
            room = config.frame_width / 2 - 0.55 - panel_x
            if g.width > room:
                g.scale(room / g.width, about_edge=UL)
            return g

        cur = note("A $100 part, made abroad.", "With no tariff, the importer pays", "exactly what the exporter charges.")
        self.play(FadeIn(cur, shift=UP * 0.15))
        self.wait(2.2)

        # The split bar: who bears the tariff
        SPLIT_W, SPLIT_Y = 5.9, -1.85
        split_title = label("WHO BEARS THE TARIFF", 17, INK_3, LABEL).move_to([panel_x, SPLIT_Y + 0.75, 0], aligned_edge=LEFT)
        frame = Rectangle(width=SPLIT_W, height=0.55, stroke_color=LINE, stroke_width=2) \
            .move_to([panel_x, SPLIT_Y, 0], aligned_edge=LEFT)

        def split_us():
            s = share_us(p.get_value())
            return Rectangle(width=max(SPLIT_W * s, 0.001), height=0.55, stroke_width=0, fill_color=ACCENT,
                             fill_opacity=1).move_to([panel_x, SPLIT_Y, 0], aligned_edge=LEFT)

        def split_foreign():
            s = share_us(p.get_value())
            return Rectangle(width=max(SPLIT_W * (1 - s), 0.001), height=0.55, stroke_width=0, fill_color=INK_3,
                             fill_opacity=0.45).move_to([panel_x + SPLIT_W, SPLIT_Y, 0], aligned_edge=RIGHT)

        def split_text():
            s = share_us(p.get_value())
            us = label(f"U.S. {s * 100:.0f}%", 20, ACCENT, weight=BOLD)
            fr = label(f"Exporter {100 - s * 100:.0f}%", 20, INK_2)
            us.next_to(frame, DOWN, buff=0.15).align_to(frame, LEFT)
            fr.next_to(frame, DOWN, buff=0.15).align_to(frame, RIGHT)
            return VGroup(us, fr)

        split = VGroup(always_redraw(split_us), always_redraw(split_foreign), frame, always_redraw(split_text))

        # ---------- Case A: the tariff lands on Americans ----------
        new = note("Case A: add a 25% tariff.", "The exporter keeps charging $100,",
                   "so the importer pays $100 + $25 = $125.", "Americans pay the whole tariff.")
        self.play(FadeOut(cur, shift=UP * 0.15), run_time=0.4); self.play(FadeIn(new, shift=UP * 0.15), run_time=0.6)
        cur = new
        self.play(on.animate.set_value(1), run_time=1.6, rate_func=smooth)
        brace_us = always_redraw(lambda: BraceBetweenPoints(
            [IM_X + BAR_W / 2 + 0.08, max(y((1 + T) * p.get_value()), y(100) + 0.001), 0],
            [IM_X + BAR_W / 2 + 0.08, y(100), 0], direction=RIGHT, color=ACCENT))
        brace_text = always_redraw(lambda: label("Paid in\nthe U.S.", 16, ACCENT)
                                   .next_to(brace_us, RIGHT, buff=0.08)
                                   .set_opacity(min(1, max(0, ((1 + T) * p.get_value() - 100) / 4))))
        self.play(FadeIn(brace_us), FadeIn(brace_text), FadeIn(split_title), FadeIn(split))
        self.wait(2.8)

        # ---------- Case B: the exporter eats it ----------
        new = note("Case B: the exporter cuts to $80.",
                   "The tariff is 25% of $80 = $20,",
                   "so the importer pays $100, same as before.",
                   "The exporter effectively paid it.")
        self.play(FadeOut(cur, shift=UP * 0.15), run_time=0.4); self.play(FadeIn(new, shift=UP * 0.15), run_time=0.6)
        cur = new
        gap = always_redraw(lambda: Rectangle(
            width=BAR_W, height=max(y(100) - y(p.get_value()), 0.001), stroke_color=INK_2, stroke_width=2,
            fill_opacity=0).set_stroke(opacity=min(1, (100 - p.get_value()) / 3))
            .move_to([EX_X, y(p.get_value()), 0], aligned_edge=DOWN))
        self.add(gap)
        self.play(p.animate.set_value(80), run_time=2.4, rate_func=smooth)
        self.wait(2.8)

        # ---------- Reality: in between ----------
        new = note("Real life lands in between.", "Researchers compare millions of",
                   "shipments to see how far exporters'", "prices actually fell.")
        self.play(FadeOut(cur, shift=UP * 0.15), run_time=0.4); self.play(FadeIn(new, shift=UP * 0.15), run_time=0.6)
        cur = new
        self.wait(1.5)

        studies = [("New York Fed", 0.94), ("Kiel Institute", 0.96), ("Caroline Freund", 0.53)]
        study_label = None
        for name, s in studies:
            target = price_for_share(s)
            txt = label(f"{name}: {s * 100:.0f}% paid in the U.S.", 22, INK, weight=BOLD) \
                .move_to([panel_x, 0.05, 0], aligned_edge=LEFT)
            sub = label(f"Exporter price ≈ ${target:.2f}", 18, INK_2).next_to(txt, DOWN, buff=0.1).align_to(txt, LEFT)
            group = VGroup(txt, sub)
            anims = [p.animate.set_value(target)]
            if study_label is not None:
                self.play(FadeOut(study_label, shift=UP * 0.1), run_time=0.35)
            anims.append(FadeIn(group, shift=UP * 0.1))
            self.play(*anims, run_time=1.8, rate_func=smooth)
            study_label = group
            self.wait(1.6)

        # ---------- The rule ----------
        self.play(*[FadeOut(m) for m in self.mobjects if m is not header])
        rule = label("Whoever has fewer alternatives pays.", 44, INK, SERIF)
        formula = MathTex(r"\text{Buyers' share} = \frac{\varepsilon_s}{\varepsilon_s + \varepsilon_d}",
                          color=INK, font_size=46)
        gloss = VGroup(
            MathTex(r"\varepsilon_s", color=INK_2, font_size=50), label("How easily sellers can sell elsewhere", 20, INK_2),
            MathTex(r"\varepsilon_d", color=INK_2, font_size=50), label("How easily buyers can switch", 20, INK_2),
        ).arrange(RIGHT, buff=0.18)
        gloss[2].shift(RIGHT * 0.5); gloss[3].shift(RIGHT * 0.5)
        VGroup(rule, formula, gloss).arrange(DOWN, buff=0.55)
        self.play(Write(rule), run_time=1.6)
        self.play(FadeIn(formula, shift=UP * 0.2), FadeIn(gloss))
        self.wait(2.8)

        url = label("Read the full deep dive: gubbgub.github.io/tariffs", 22, ACCENT, LABEL).to_edge(DOWN, buff=0.6)
        self.play(FadeIn(url, shift=UP * 0.1))
        self.wait(2)
