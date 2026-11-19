"""Colors and fonts for the tariff animation, matched to gubbgub.github.io (light mode).
Same design tokens as integrals/integrals_eecs.py.

LEARN: put the colors and fonts in one file and import them, the same way the
website keeps them in CSS variables. Change a color here and every scene follows.
"""
from manim import config

CANVAS = "#F5F5F7"   # page background
SURFACE = "#FFFFFF"  # cards
INK = "#1D1D1F"      # main text
INK_2 = "#515154"    # secondary text
INK_3 = "#86868B"    # labels
LINE = "#E5E5EA"     # hairlines
ACCENT = "#0071E3"   # the site's blue

SANS = "Inter"
SERIF = "Lora"   # Charter (the site's serif) only exists here as an old Type 1 font Pango can't load
LABEL = "Inter Medium"   # small caps-style labels. The site uses SF Mono for [TAGS], but the only
                         # monospaces here (DejaVu, Liberation) look out of place next to Inter.

config.background_color = CANVAS
GOLD = "#C9A227"     # used only where the subject is literally gold
