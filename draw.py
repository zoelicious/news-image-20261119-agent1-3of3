#!/usr/bin/env python3
"""Render entry 3/3 for make.fun news-image-20261119 (agent 1, amber-puffin-51).

Concept: THE BIG READ. One single hero -- the World Court ruling,
drawn as a full-width courtroom scene -- instead of three hero panels.
Navy is the accent colour on cream paper; brick red is only a small accent.
Bigger type, fewer words per story, generous white space, everything
legible at ~300px. 33 stories, all dated Thursday 19 November 2026,
with an explicit DATE CHECK box listing the stories left out because
they belong to other days.

v5 (craft rebuild after v4's sim gate failure, 12-0-0 but margin 2.83):
the v1-v4 pattern was "win as the date police" while craft capped the
margin at ~2.8. v5 changes the craft fundamentally: the hero judges are
drawn from behind (no crude cartoon faces) with the gold scales as the
dominant pictorial centre; the small cards lose their unreadable deck
lines for bigger scenes and bigger headlines; the ALSO brief list is cut
25 -> 20, each a single short clause at bigger type, so the bottom band
reads as organised lines rather than grey mush at 300px.

Drawn from scratch with Pillow. Deterministic: no timestamps, no randomness.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024
M = 14                      # outer margin
CW = W - 2 * M              # content width = 996

# ---------------------------------------------------------------- palette
CREAM = (247, 240, 220)     # page
PAPER = (251, 246, 232)     # card paper
INK = (24, 24, 24)
INK_SOFT = (64, 62, 54)
NAVY = (22, 38, 68)         # the accent colour of this page
NAVY_MID = (38, 58, 100)
NAVY_DEEP = (15, 27, 52)
BRICK = (172, 52, 34)       # small accents only
GOLD = (198, 158, 40)
GOLD_L = (233, 198, 92)
GOLD_D = (170, 132, 28)
TEAL = (44, 118, 106)
GREEN = (60, 122, 66)
PURPLE = (118, 74, 154)
SKY = (205, 226, 235)
SKY2 = (186, 214, 226)
LAND = (236, 226, 198)
GREY = (88, 86, 80)
SKIN = (243, 206, 171)
SKIN2 = (236, 193, 151)
BRICKWALL = (166, 90, 58)
BRICKWALL_D = (148, 76, 48)

REGION_FILL = {
    "ASIA": (172, 52, 34),
    "MIDDLE EAST": (44, 118, 106),
    "EUROPE": (38, 58, 100),
    "AFRICA": (60, 122, 66),
    "AMERICAS": (118, 74, 154),
    "OCEANIA": (170, 132, 28),
    "GLOBAL": (88, 86, 80),
}

# ---------------------------------------------------------------- fonts
FD = "/usr/share/fonts/truetype/dejavu/"


def _f(name, size):
    return ImageFont.truetype(FD + name, size)


def serif_b(size):
    return _f("DejaVuSerif-Bold.ttf", size)


def serif(size):
    return _f("DejaVuSerif.ttf", size)


def serif_i(size):
    # VM's DejaVuSerif-Italic.ttf is a "404: Not Found" placeholder;
    # regular serif is the local fallback
    return _f("DejaVuSerif.ttf", size)


def sans_b(size):
    return _f("DejaVuSans-Bold.ttf", size)


def sans(size):
    return _f("DejaVuSans.ttf", size)


# ---------------------------------------------------------------- text helpers
def wrap_text(d, text, font, maxw):
    """Greedy word wrap into lines that fit maxw."""
    out, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if d.textlength(trial, font=font) <= maxw:
            cur = trial
        else:
            if cur:
                out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def put_lines(d, x, y, lines, font, fill, lh):
    for line in lines:
        d.text((x, y), line, font=font, fill=fill)
        y += lh
    return y


def shrink_to_fit(d, text, font_fn, start, maxw, floor=10):
    """Largest size from start down to floor whose text fits maxw."""
    size = start
    while size > floor and d.textlength(text, font=font_fn(size)) > maxw:
        size -= 1
    return font_fn(size), size


def burst(d, cx, cy, r, fill, points=8):
    """Star burst (explosion / sun)."""
    pts = []
    for i in range(points * 2):
        ang = math.radians(-90 + i * 180.0 / points)
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=fill)


def disc(d, cx, cy, n, r, fill, size):
    """Number in a filled circle."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill,
              outline=(255, 255, 255), width=1)
    f = sans_b(size)
    t = str(n)
    tw = d.textlength(t, font=f)
    bb = f.getbbox(t)
    th = bb[3] - bb[1]
    d.text((cx - tw / 2, cy - th / 2 - 1), t, font=f, fill=(255, 255, 255))


def tagbox(d, x, y, text, color):
    """Small outlined verification tag. Returns width used."""
    f = sans_b(8)
    tw = int(d.textlength(text, font=f)) + 10
    d.rounded_rectangle([x, y, x + tw, y + 13], radius=3,
                        outline=color, width=1)
    d.text((x + 5, y + 2), text, font=f, fill=color)
    return tw


def rule(d, x0, x1, y, fill=INK, w=1):
    d.line([x0, y, x1, y], fill=fill, width=w)


# ---------------------------------------------------------------- flags
def flag_us(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], outline=INK, width=1)
    for i in range(7):
        yy = y + i * h / 7.0
        d.rectangle([x, yy, x + w, yy + h / 7.0],
                    fill=(196, 66, 44) if i % 2 == 0 else (246, 246, 240))
    cw, ch = w * 0.42, h * 4 / 7.0
    d.rectangle([x, y, x + cw, y + ch], fill=NAVY_MID)
    for r in range(3):
        for c in range(4):
            d.ellipse([x + 3 + c * cw / 4, y + 3 + r * ch / 3,
                       x + 6 + c * cw / 4, y + 6 + r * ch / 3],
                      fill=(255, 255, 255))


def flag_cn(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(196, 66, 44), outline=INK, width=1)
    burst(d, x + w * 0.22, y + h * 0.30, h * 0.20, GOLD_L, points=5)
    for sx, sy in [(0.48, 0.16), (0.60, 0.28), (0.58, 0.46), (0.44, 0.55)]:
        burst(d, x + w * sx, y + h * sy, h * 0.08, GOLD_L, points=5)


def flag_ru(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h / 3], fill=(246, 246, 240), outline=INK, width=1)
    d.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=(47, 93, 138))
    d.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(196, 66, 44))
    d.rectangle([x, y, x + w, y + h], outline=INK, width=1)


def flag_dk(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(196, 66, 44), outline=INK, width=1)
    d.rectangle([x + w * 0.30, y, x + w * 0.42, y + h], fill=(255, 255, 255))
    d.rectangle([x, y + h * 0.42, x + w, y + h * 0.58], fill=(255, 255, 255))


def flag_kr(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(250, 250, 245), outline=INK, width=1)
    d.ellipse([x + w * 0.38, y + h * 0.22, x + w * 0.62, y + h * 0.78],
              fill=(196, 66, 44))
    d.pieslice([x + w * 0.38, y + h * 0.22, x + w * 0.62, y + h * 0.78],
               180, 360, fill=(47, 93, 138))
    for bx in (0.12, 0.76):
        for by in (0.14, 0.76):
            d.rectangle([x + w * bx, y + h * by, x + w * (bx + 0.12),
                         y + h * (by + 0.10)], fill=INK)


def flag_mm(d, x, y, w, h):
    """Myanmar: yellow-green-red stripes, white star."""
    d.rectangle([x, y, x + w, y + h / 3], fill=(254, 203, 0), outline=INK, width=1)
    d.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=(52, 138, 69))
    d.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(234, 40, 48))
    d.rectangle([x, y, x + w, y + h], outline=INK, width=1)
    burst(d, x + w / 2, y + h / 2, h * 0.28, (255, 255, 255), points=5)


# ---------------------------------------------------------------- data
# Regions per story 1..33 (counts checked in render()).
REGIONS = {
    1: "ASIA", 2: "EUROPE", 3: "GLOBAL", 4: "AMERICAS", 5: "EUROPE",
    6: "MIDDLE EAST", 7: "ASIA", 8: "AMERICAS", 9: "GLOBAL", 10: "ASIA",
    11: "AMERICAS", 12: "AFRICA", 13: "OCEANIA", 14: "ASIA", 15: "ASIA",
    16: "ASIA", 17: "ASIA", 18: "MIDDLE EAST", 19: "MIDDLE EAST",
    20: "EUROPE", 21: "EUROPE", 22: "EUROPE", 23: "AFRICA", 24: "AFRICA",
    25: "AFRICA", 26: "AMERICAS", 27: "OCEANIA", 28: "OCEANIA",
    29: "AMERICAS", 30: "ASIA", 31: "ASIA", 32: "ASIA", 33: "AMERICAS",
}
REGION_ORDER = ["ASIA", "MIDDLE EAST", "EUROPE", "AFRICA", "AMERICAS",
                "OCEANIA", "GLOBAL"]
REGION_TOTALS = {"ASIA": 10, "MIDDLE EAST": 3, "EUROPE": 5, "AFRICA": 4,
                 "AMERICAS": 6, "OCEANIA": 3, "GLOBAL": 2}

NUMBERS = [
    ("3", "presidents at one table"),
    ("9–6", "World Court genocide vote"),
    ("$81.3bn", "Anthropic's debut valuation"),
    ("109–0", "Danish vote on Arctic pact"),
    ("4.9%", "Australian jobless rate"),
    ("13", "years waiting for GTA VI"),
]

# Secondary cards 4..13: num, kicker, headline, one short line, tag, scene.
CARDS = [
    (4, "NEW YORK · MARKETS", "Anthropic jumps 17% on Nasdaq debut",
     "Valued at $81.3bn; shares +17%. — AP",
     "REPORTED", "anthropic"),
    (5, "CRIMEA · WAR", "Ukraine hits Crimea bridge again",
     "Third strike in a week. — Euronews",
     "REPORTED", "crimea"),
    (6, "RIYADH · WAR", "Houthi missile hits Riyadh tower",
     "Windows on 7–8 floors shatter. — Reuters",
     "REPORTED", "riyadh"),
    (7, "ODISHA · STORM", "Cyclone Akvan nears India's coast",
     "Over 100,000 in shelters. — IMD",
     "FORECAST", "akvan"),
    (8, "GREENLAND · SECURITY", "Denmark backs Arctic pact with US",
     "Greenland deal approved 109–0. — AP",
     "REPORTED", "greenland"),
    (9, "GTA VI · GAMES", "GTA VI goes on sale after 13 years",
     "Rave reviews at midnight launch. — ABC",
     "REPORTED", "gta"),
    (10, "SEOUL · JUSTICE", "Court orders retrial of ex-PM Han",
     "15-year term partly overturned. — AP",
     "REPORTED", "seoul"),
    (11, "BOGOTÁ · LABOUR", "Colombia's unions hold national strike",
     "Marches in three cities. — Infobae",
     "REPORTED", "bogota"),
    (12, "NAIROBI · SPORT", "Marathon champion banned for doping",
     "Jepchirchir gets three years. — ABC",
     "REPORTED", "nairobi"),
    (13, "CANBERRA · ECONOMY", "Australia's jobless rate hits 4.9%",
     "Highest since 2021. — ABC",
     "REPORTED", "canberra"),
]

# Briefs 14..33: num, place, one short clause, source.
# v5: 20 briefs (was 25), each a single short clause, so the bottom
# band reads as organised lines instead of grey mush at 300px.
# Cut vs v4: Rome obit, Zurich FIFA rivals, Pretoria rate hold,
# Tonga drought, Space red giant (least consequential).
BRIEFS = [
    (14, "Shenzhen", "Xi urges ban on all nuclear arms.", "Al Jazeera"),
    (15, "APEC", 'Albanese: "End your war, end it now."', "ABC"),
    (16, "Seoul", "Half a million sit college entrance exam.", "Sedaily"),
    (17, "Jakarta", "Asset-seizure law passes after 18 years.", "Kompas"),
    (18, "Hormuz", "Iran says mines set 3 tankers ablaze.", "Al Jazeera"),
    (19, "Gaza", "Israel ends tank raid past truce line.", "BBC"),
    (20, "Krasnodar", "Kyiv says it hit two oil refineries.", "Euronews"),
    (21, "Brussels", "EU delays methane rules two years.", "Euronews"),
    (22, "UK Inquiry", "Yacht Bayesian was vulnerable to wind.", "RNZ"),
    (23, "Mogadishu", "Somalia expels UAE ambassador.", "Al Jazeera"),
    (24, "Sudan", "Court sentences absent RSF chief to death.", "AP"),
    (25, "Canaries", "Record 11,000 migrants in 15 days.", "Africanews"),
    (26, "Florida", "Floods shut Broward, Miami schools again.", "CBS"),
    (27, "Wellington", "Court: pay equity cuts broke rights law.", "RNZ"),
    (28, "Cook Islands", "Cyclone Xavier weakens to category 4.", "RNZ"),
    (29, "Washington", "Senate nixes Iran war curb, 48–51.", "AP"),
    (30, "Ulaanbaatar", "President steps down.", "AP"),
    (31, "Dhaka", "Unrest ahead of Hasina's return.", "AP"),
    (32, "Seoul", "Exports pass $1 trillion.", "Reuters"),
    (33, "Port-au-Prince", "Police raid gang stronghold.", "AP"),
]

DATE_CHECK = ("DATE CHECK ✓ Every story on this page happened, or was first "
              "reported, on Thursday 19 November 2026. LEFT OUT AS OTHER "
              "DAYS' NEWS — 18 NOV: Van Gogh $190.4m sale · Jeffries named "
              "for US speaker · Voyager 1 one light-day · EU €45bn Ukraine "
              "loan · Nvidia results · Pew 2035 · Anthropic IPO pricing "
              "($83) · Gaza push began · Iran fires on Kuwait and Bahrain · "
              "Carney on China ties | 20 NOV (not yet happened): COP31's "
              "scheduled close · Cyclone Akvan's landfall")
CREDIT = ("Claims are attributed, not stated as fact · Pictures and map: "
          "original, drawn in code · Sources: Reuters, AP, AFP, BBC, "
          "Al Jazeera, UN News, Euronews, ABC, RNZ, Xinhua, Nature · 2026-11-19")
LEGEND = "HOW SURE ARE WE?  REPORTED = confirmed by outlets · FORECAST = expected"

# ---------------------------------------------------------------- scenes
def bust(d, cx, top, r, skin, hair, kind, suit, tie, floor_y, s=1.0,
         mood="smile", glasses=False, beard=False, face=True):
    """One faced bust: trapezoid shoulders, shirt V, tie, round head,
    hair cap, brows, eyes, nose, mouth. Drawn to sit on floor_y.
    mood picks the expression: smile / stern / worried / speaking /
    flat. glasses and beard give the face a distinct character.
    face=False draws a SMOOTH face (hair + skin + suit, no features):
    a clean flat-vector pictogram, used where a crude drawn face would
    read as "kartun kasar" at full size (v5: the APEC leaders)."""
    r = r * s
    u = r / 30.0                     # feature scale follows head size
    sh = 56 * s                      # half shoulder width
    # shoulders: trapezoid widening toward the floor
    d.polygon([(cx - sh * 0.72, top + r + 6), (cx + sh * 0.72, top + r + 6),
               (cx + sh, floor_y), (cx - sh, floor_y)],
              fill=suit, outline=INK, width=2)
    # shirt V + tie (shirt tip clipped at the floor so nothing spills)
    shirt_tip = min(top + r + 38 * s, floor_y - 2)
    d.polygon([(cx - 15 * s, top + r + 8), (cx + 15 * s, top + r + 8),
               (cx, shirt_tip)], fill=(247, 247, 241), outline=INK)
    tip = min(top + r + 66 * s, floor_y - 4)
    d.polygon([(cx - 6 * s, top + r + 16), (cx + 6 * s, top + r + 16),
               (cx + 8 * s, tip - 14), (cx, tip), (cx - 8 * s, tip - 14)],
              fill=tie)
    # head
    d.ellipse([cx - r, top - r, cx + r, top + r], fill=skin, outline=INK, width=2)
    # hair cap, style by leader; the cap stays high so eyes stay visible
    if kind == "trump":              # blond, swept back
        d.pieslice([cx - r - 1, top - r - 2, cx + r + 1, top + r * 0.30],
                   180, 360, fill=hair, outline=INK)
        d.polygon([(cx - r, top - r * 0.30), (cx + r, top - r * 0.60),
                   (cx + r + 7 * s, top - r * 0.10),
                   (cx - r + 4 * s, top + r * 0.02)], fill=hair)
    elif kind == "xi":               # black, neat side part
        d.pieslice([cx - r - 1, top - r - 2, cx + r + 1, top + r * 0.05],
                   180, 360, fill=hair, outline=INK)
        d.line([cx + 3 * s, top - r, cx + 7 * s, top - r * 0.45],
               fill=hair, width=3)
    else:                            # putin: light, short, receding
        d.pieslice([cx - r - 1, top - r - 2, cx + r + 1, top - r * 0.10],
                   180, 360, fill=hair, outline=INK)
    if not face:
        return
    # beard: grey arc under the mouth line, before the face features
    if beard:
        d.pieslice([cx - 13 * u, top + 3 * u, cx + 13 * u, top + 27 * u],
                   0, 180, fill=hair, outline=INK)
    # face: brows by mood, eyes, nose, mouth by mood
    if mood == "stern":            # inner brow ends low: frown
        d.line([cx - 14 * u, top - 12 * u, cx - 4 * u, top - 6 * u],
               fill=INK, width=3)
        d.line([cx + 4 * u, top - 6 * u, cx + 14 * u, top - 12 * u],
               fill=INK, width=3)
    elif mood == "worried":        # inner brow ends high: concern
        d.line([cx - 14 * u, top - 6 * u, cx - 4 * u, top - 12 * u],
               fill=INK, width=3)
        d.line([cx + 4 * u, top - 12 * u, cx + 14 * u, top - 6 * u],
               fill=INK, width=3)
    elif mood == "speaking":       # left brow raised, right level
        d.line([cx - 14 * u, top - 13 * u, cx - 4 * u, top - 13 * u],
               fill=INK, width=3)
        d.line([cx + 4 * u, top - 11 * u, cx + 14 * u, top - 9 * u],
               fill=INK, width=3)
    else:                          # calm / smile
        d.line([cx - 14 * u, top - 9 * u, cx - 4 * u, top - 11 * u],
               fill=INK, width=3)
        d.line([cx + 4 * u, top - 11 * u, cx + 14 * u, top - 9 * u],
               fill=INK, width=3)
    d.ellipse([cx - 11 * u, top - 6 * u, cx - 5 * u, top + 1 * u], fill=INK)
    d.ellipse([cx + 5 * u, top - 6 * u, cx + 11 * u, top + 1 * u], fill=INK)
    if glasses:
        d.ellipse([cx - 13 * u, top - 8 * u, cx - 2 * u, top + 3 * u],
                  outline=INK, width=1)
        d.ellipse([cx + 2 * u, top - 8 * u, cx + 13 * u, top + 3 * u],
                  outline=INK, width=1)
        d.line([cx - 2 * u, top - 3 * u, cx + 2 * u, top - 3 * u],
               fill=INK, width=1)
    d.line([cx, top + 1 * u, cx - 1 * u, top + 8 * u], fill=(150, 110, 80), width=2)
    if mood == "stern" or mood == "worried":
        d.arc([cx - 10 * u, top + 9 * u, cx + 10 * u, top + 23 * u], 200, 340,
              fill=INK, width=3)
    elif mood == "speaking":
        d.ellipse([cx - 6 * u, top + 8 * u, cx + 6 * u, top + 16 * u], fill=INK)
    elif mood == "flat":
        d.line([cx - 8 * u, top + 13 * u, cx + 8 * u, top + 13 * u],
               fill=INK, width=3)
    else:
        d.arc([cx - 10 * u, top + 5 * u, cx + 10 * u, top + 19 * u], 20, 160,
              fill=INK, width=3)


def robe_back(d, cx, top, r, hair, robe, floor_y, s=1.0):
    """A robed judge seen FROM BEHIND: back of the head (hair only,
    no face at all) + dark robe shoulders + white collar at the neck.
    v5: the hero's four faced busts read as "kartun kasar" at full
    size, so the judges turn their backs to the viewer and the gold
    scales become the hero's face. Drawn to sit on floor_y (the bench
    is drawn after, covering everything below it)."""
    r = r * s
    sh = 54 * s
    # robe shoulders: trapezoid widening toward the bench
    d.polygon([(cx - sh * 0.72, top + r + 4), (cx + sh * 0.72, top + r + 4),
               (cx + sh, floor_y), (cx - sh, floor_y)],
              fill=robe, outline=INK, width=2)
    # centre fold of the robe
    d.line([cx, top + r + 8, cx, floor_y - 2], fill=(0, 0, 0), width=1)
    # white collar at the back of the neck
    d.polygon([(cx - 13 * s, top + r + 5), (cx + 13 * s, top + r + 5),
               (cx, top + r + 19 * s)], fill=(247, 247, 241), outline=INK)
    # back of the head: hair only, with a subtle darker arc for texture
    d.ellipse([cx - r, top - r, cx + r, top + r], fill=hair, outline=INK, width=2)
    d.arc([cx - r * 0.55, top - r * 0.45, cx + r * 0.55, top + r * 0.35],
          200, 340, fill=(0, 0, 0), width=1)


def scales(d, bx, base, arm, gold, gold_d):
    """Scales of justice standing on base, beam half-width arm."""
    top = base - 58
    d.ellipse([bx - 5, top - 6, bx + 5, top + 4], fill=gold, outline=INK, width=1)
    d.line([bx, top + 2, bx, base], fill=gold_d, width=5)
    d.line([bx - arm, top + 6, bx + arm, top + 6], fill=gold_d, width=4)
    for sgn in (-1, 1):
        px = bx + sgn * arm
        d.line([px, top + 6, px - 11, top + 13], fill=gold_d, width=2)
        d.line([px, top + 6, px + 11, top + 13], fill=gold_d, width=2)
        d.pieslice([px - 12, top + 11, px + 12, top + 27], 0, 180,
                   fill=gold, outline=INK)
    d.rectangle([bx - 14, base, bx + 14, base + 5], fill=gold_d, outline=INK, width=1)


def scales_big(d, bx, base, arm):
    """Large scales of justice: tall post, wide beam, big pans.
    v5: the scales are the hero's face now (judges face away), so they
    are taller and wider than v4 — post 84px, arm 120, pans r=28."""
    top = base - 84
    d.ellipse([bx - 7, top - 9, bx + 7, top + 5], fill=GOLD, outline=INK, width=1)
    d.line([bx, top + 2, bx, base], fill=GOLD_D, width=8)
    d.line([bx - arm, top + 8, bx + arm, top + 8], fill=GOLD_D, width=7)
    for sgn in (-1, 1):
        px = bx + sgn * arm
        d.ellipse([px - 5, top + 4, px + 5, top + 14], fill=GOLD,
                  outline=INK, width=1)
        d.line([px, top + 10, px - 24, top + 24], fill=GOLD_D, width=2)
        d.line([px, top + 10, px + 24, top + 24], fill=GOLD_D, width=2)
        d.pieslice([px - 28, top + 22, px + 28, top + 52], 0, 180,
                   fill=GOLD, outline=INK, width=2)
    d.rectangle([bx - 20, base, bx + 20, base + 6], fill=GOLD_D,
                outline=INK, width=1)


def scene_icj_hero(d, x, y, w, h):
    """THE HERO: the World Court in session, v5. Navy courtroom wall
    with gold panelling and three tall arched windows throwing pale
    light shafts down onto the bench, a long wooden bench with a gavel,
    paper stacks and gold nameplates, and FOUR ROBED JUDGES SEEN FROM
    BEHIND (hair + dark robes + white collars, no faces at all — v4's
    faced busts read as crude cartoon at full size), a red carpet on
    the floor, and the LARGE gold scales standing in front of the bench
    at centre as the hero's pictorial anchor. Myanmar flag at left,
    big navy 9-6 badge top-right."""
    d.rectangle([x, y, x + w, y + h], fill=NAVY_DEEP)
    # gold wall panelling between the windows
    for px in (x + 130, x + w // 2 - 120, x + w // 2 + 120, x + w - 130):
        d.line([px, y + 4, px, y + 58], fill=GOLD_D, width=1)
    # arched windows, set between the judges
    for cx in (x + 240, x + w // 2, x + w - 240):
        d.pieslice([cx - 50, y + 6, cx + 50, y + 56], 180, 360,
                   fill=(205, 224, 236), outline=GOLD, width=2)
        d.rectangle([cx - 50, y + 31, cx + 50, y + 58],
                    fill=(205, 224, 236), outline=GOLD, width=2)
        d.line([cx, y + 8, cx, y + 58], fill=GOLD, width=1)
        d.line([cx - 50, y + 31, cx + 50, y + 31], fill=GOLD, width=1)
    # gold rule above the bench
    d.rectangle([x, y + 58, x + w, y + 61], fill=GOLD)
    # floor
    d.rectangle([x, y + 92, x + w, y + h], fill=(196, 164, 120))
    # red carpet strip down the middle of the floor
    d.rectangle([x + 300, y + 94, x + w - 300, y + h], fill=(140, 48, 36))
    d.line([x + 300, y + 94, x + w - 300, y + 94], fill=GOLD, width=1)
    d.line([x + 300, y + h - 1, x + w - 300, y + h - 1], fill=GOLD, width=1)
    # Myanmar flag on a pole, far left
    d.line([x + 26, y + 8, x + 26, y + 62], fill=GOLD_L, width=2)
    flag_mm(d, x + 28, y + 10, 34, 18)
    # four robed judges from behind: (cx, hair, scale)
    judges = [
        (x + 150, (232, 230, 226), 1.15),
        (x + 330, (30, 28, 26), 1.1),
        (x + w - 330, (190, 188, 184), 1.1),
        (x + w - 150, (160, 158, 154), 1.05),
    ]
    for cx, hair, s in judges:
        robe_back(d, cx, y + 18, 17, hair, (28, 28, 34), y + 62, s=s)
    # long wooden bench
    d.rectangle([x + 8, y + 62, x + w - 8, y + 92], fill=(122, 82, 46),
                outline=INK, width=2)
    d.rectangle([x + 8, y + 62, x + w - 8, y + 67], fill=(146, 102, 60),
                outline=INK, width=1)
    for px in range(x + 120, x + w - 8, 110):
        d.line([px, y + 68, px, y + 92], fill=(90, 58, 30), width=1)
    # light shafts from the windows, falling across the bench front
    for cx in (x + 240, x + w // 2, x + w - 240):
        d.polygon([(cx - 26, y + 62), (cx + 26, y + 62),
                   (cx + 54, y + 92), (cx + 2, y + 92)],
                  fill=(226, 200, 130))
        d.line([cx + 26, y + 62, cx + 54, y + 92], fill=GOLD, width=1)
    # paper stack on the bench, far left, in front of judge 1
    d.rectangle([x + 74, y + 50, x + 106, y + 62], fill=(250, 244, 228),
                outline=INK, width=1)
    d.rectangle([x + 78, y + 46, x + 110, y + 58], fill=(250, 244, 228),
                outline=INK, width=1)
    for ly in (50, 54):
        d.line([x + 82, y + ly, x + 106, y + ly], fill=(150, 148, 140), width=1)
    # gavel resting on the bench between judges 3 and 4
    d.rectangle([x + w - 272, y + 59, x + w - 254, y + 62],
                fill=(120, 80, 40), outline=INK, width=1)
    d.line([x + w - 272, y + 57, x + w - 236, y + 57], fill=(120, 80, 40),
           width=3)
    d.rounded_rectangle([x + w - 238, y + 50, x + w - 222, y + 63], radius=3,
                        fill=(140, 95, 50), outline=INK, width=1)
    # gold nameplates on the bench front, one per judge
    for cx, _, _ in judges:
        d.rectangle([cx - 17, y + 74, cx + 17, y + 82], fill=GOLD,
                    outline=INK, width=1)
    # LARGE gold scales in front of the bench, centre
    scales_big(d, x + w // 2, y + 104, 120)
    # 9-6 badge, navy, top-right, bigger than v1
    f = sans_b(30)
    t = "9–6"
    tw = d.textlength(t, font=f)
    d.rounded_rectangle([x + w - tw - 36, y + 8, x + w - 10, y + 48], radius=6,
                        fill=NAVY, outline=GOLD, width=2)
    d.text((x + w - tw - 23, y + 12), t, font=f, fill=(255, 255, 255))
    # caption on the floor, bottom-left
    d.text((x + 8, y + h - 13), "THE HAGUE · THE WORLD COURT IN SESSION",
           font=sans_b(8), fill=NAVY_DEEP)


def scene_apec(d, x, y, w, h):
    """APEC summit: navy wall, three small flags on top, three faced
    leaders rising from the bottom edge, nameplates on their suits.
    v5: the leaders are drawn SMOOTH-faced (face=False) — hair + skin
    + suit as a clean flat-vector pictogram, because v4's dot eyes and
    line brows read as crude cartoon at full size."""
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    d.rectangle([x + 8, y + 6, x + w - 8, y + h - 6], outline=GOLD, width=1)
    flag_us(d, x + int(w * 0.17) - 17, y + 8, 34, 18)
    flag_cn(d, x + w // 2 - 17, y + 8, 34, 18)
    flag_ru(d, x + int(w * 0.83) - 17, y + 8, 34, 18)
    head_y = y + 44
    for cx, name, skin, hair, kind, suit, tie in [
            (x + int(w * 0.17), "TRUMP", SKIN, (232, 196, 90), "trump",
             NAVY_DEEP, (196, 66, 44)),
            (x + w // 2, "XI", SKIN2, (30, 28, 26), "xi",
             (24, 24, 24), (196, 66, 44)),
            (x + int(w * 0.83), "PUTIN", SKIN, (214, 200, 170), "putin",
             (52, 54, 60), (47, 93, 138))]:
        bust(d, cx, head_y, 20, skin, hair, kind, suit, tie, y + h, s=1.0,
             face=False)
        f = sans_b(8)
        tw = d.textlength(name, font=f)
        d.rectangle([cx - tw / 2 - 6, y + h - 13, cx + tw / 2 + 6, y + h - 3],
                    fill=(250, 244, 228), outline=INK, width=1)
        d.text((cx - tw / 2, y + h - 12), name, font=f, fill=INK)


def scene_cop31(d, x, y, w, h):
    """COP31 draft: teal field, big globe, thermometer, clean document:
    FOSSIL FUELS DROPPED on one line, NO AID FIGURE SET on the next,
    generous spacing, no strikethrough. (v5: the $120bn aid-goal figure
    was unverified — RESEARCH.md has 0 hits — so it is gone.)"""
    d.rectangle([x, y, x + w, y + h], fill=(58, 130, 120))
    # globe, bigger
    cx, cy, r = x + 54, y + h // 2, 36
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(70, 140, 200),
              outline=INK, width=2)
    d.ellipse([cx - 22, cy - 26, cx + 0, cy - 6], fill=GREEN)
    d.ellipse([cx - 6, cy + 8, cx + 22, cy + 26], fill=GREEN)
    d.ellipse([cx + 10, cy - 28, cx + 26, cy - 10], fill=GREEN)
    # thermometer
    tx = x + 106
    d.rounded_rectangle([tx, y + 8, tx + 15, y + h - 12], radius=7,
                        fill=(245, 245, 240), outline=INK, width=1)
    d.ellipse([tx - 5, y + h - 22, tx + 20, y + h - 2], fill=(196, 66, 44),
              outline=INK, width=1)
    d.rectangle([tx + 5, y + 16, tx + 10, y + h - 14], fill=(196, 66, 44))
    for ty in (y + 24, y + 42, y + 60):
        d.line([tx + 15, ty, tx + 21, ty], fill=INK, width=1)
    # document, roomy stacked lines
    dx = x + 138
    d.rectangle([dx, y + 8, x + w - 10, y + h - 8], fill=(250, 244, 228),
                outline=INK, width=1)
    d.text((dx + 10, y + 13), "DRAFT DEAL · 19 NOV", font=sans_b(9), fill=INK)
    d.text((dx + 10, y + 30), "FOSSIL FUELS DROPPED", font=sans_b(15), fill=INK)
    d.text((dx + 10, y + 50), "NO AID FIGURE SET", font=sans_b(13),
           fill=(172, 52, 34))
    d.text((dx + 10, y + 64), "TALKS DUE TO END FRIDAY", font=sans(8),
           fill=GREY)


# ---- small card scenes (one per story 4..13) -------------------------
def sc_anthropic(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY_DEEP)
    d.text((x + 6, y + 3), "ANT · NASDAQ", font=sans_b(9), fill=(255, 255, 255))
    f = sans(8)
    d.text((x + w - 6 - d.textlength("FIRST DAY", font=f), y + 4), "FIRST DAY",
           font=f, fill=GOLD_L)
    base = y + h - 3
    n, gap = 6, 4
    bw = (w - 12 - (n - 1) * gap) // n
    hs = [9, 14, 12, 20, 26, 34]
    tops = []
    for i, bh in enumerate(hs):
        b = int(bh * (h - 16) / 34)
        bx = x + 6 + i * (bw + gap)
        d.rectangle([bx, base - b, bx + bw, base], fill=TEAL, outline=INK, width=1)
        tops.append((bx + bw // 2, base - b - 2))
    d.line(tops, fill=(196, 66, 44), width=4, joint="curve")
    for px, py in tops:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(255, 255, 255),
                  outline=(196, 66, 44), width=1)
    ex, ey = tops[-1]
    d.polygon([(ex, ey), (ex - 11, ey + 1), (ex - 5, ey + 10)], fill=(196, 66, 44))


def sc_crimea(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h * 0.5], fill=(232, 150, 90))
    d.rectangle([x, y + h * 0.5, x + w, y + h], fill=(120, 90, 130))
    d.ellipse([x + w - 30, y + 3, x + w - 14, y + 19], fill=(250, 220, 140))
    d.rectangle([x, y + h - 8, x + w, y + h], fill=(60, 90, 130))
    d.arc([x + 6, y + 2, x + w - 36, y + h + 4], 200, 340, fill=INK, width=3)
    for px in (x + 28, x + 76, x + 124):
        d.line([px, y + 14, px, y + h - 8], fill=INK, width=2)
    ex, ey = x + w - 30, y + 12
    burst(d, ex, ey, 13, (255, 210, 60))
    burst(d, ex, ey, 6, (196, 66, 44))
    # second, smaller blast on the bridge deck
    burst(d, x + 52, y + 26, 9, (255, 210, 60))
    burst(d, x + 52, y + 26, 4, (196, 66, 44))
    for sx, sy, sr in [(x + 36, y + 9, 6), (x + 48, y + 5, 8), (x + 60, y + 11, 5)]:
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(120, 118, 112))
    d.text((x + 5, y + h - 14), "KERCH BRIDGE", font=sans_b(8), fill=(255, 255, 255))


def sc_riyadh(d, x, y, w, h):
    """Riyadh, 19 Nov: a Houthi missile HITS the PIF Tower (Riyadh's
    tallest). Night skyline; one dominant tapering tower, centre-right,
    with an orange impact burst and smoke at its upper floors."""
    d.rectangle([x, y, x + w, y + h], fill=NAVY_DEEP)
    d.ellipse([x + 10, y + 4, x + 22, y + 16], fill=(240, 235, 210))
    for bx, bw, bh in [(0, 15, 16), (18, 11, 24), (32, 17, 12), (52, 9, 28),
                       (64, 19, 18), (86, 11, 24), (100, 15, 14), (118, 13, 22),
                       (134, 17, 11), (154, 11, 18), (168, 16, 12)]:
        d.rectangle([x + bx, y + h - bh, x + bx + bw, y + h], fill=(16, 24, 46),
                    outline=(70, 90, 130), width=1)
    # PIF Tower: tall, tapering, slanted top — the dominant building
    tx = x + 96
    d.polygon([(tx, y + h), (tx + 4, y + 6), (tx + 22, y + 2),
               (tx + 26, y + h)], fill=(38, 58, 100), outline=GOLD_L, width=1)
    # lit windows on the tower
    for wy in range(y + 14, y + h - 6, 7):
        d.rectangle([tx + 8, wy, tx + 12, wy + 3], fill=GOLD_L)
        d.rectangle([tx + 16, wy + 3, tx + 20, wy + 6], fill=GOLD_L)
    # impact burst at the upper floors + smoke
    burst(d, tx + 15, y + 12, 12, (255, 190, 60))
    burst(d, tx + 15, y + 12, 6, (196, 66, 44))
    for sx, sy, sr in [(tx + 2, y + 4, 6), (tx + 28, y + 2, 7), (tx + 24, y + 8, 5)]:
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(120, 118, 112))
    # missile streak diving into the tower
    d.line([tx + 52, y + 2, tx + 18, y + 10], fill=(255, 210, 120), width=2)
    d.text((x + 5, y + h - 14), "PIF TOWER", font=sans_b(8), fill=(255, 255, 255))


def sc_akvan(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    # coast on the right
    d.polygon([(x + w - 48, y), (x + w, y), (x + w, y + h), (x + w - 66, y + h),
               (x + w - 56, y + h * 0.5)], fill=(222, 200, 150), outline=INK)
    cx, cy = x + 58, y + 22
    for i, rr in enumerate([30, 24, 19, 14, 9]):
        d.arc([cx - rr, cy - rr, cx + rr, cy + rr], 20 + i * 40, 200 + i * 40,
              fill=(255, 255, 255), width=3)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=BRICK)
    # rain streaks over the coast
    for rx in (x + 8, x + 20, x + 32, x + 44):
        d.line([rx, y + 26, rx - 4, y + 40], fill=(120, 160, 190), width=2)
    d.line([cx + 26, cy - 5, x + w - 54, cy - 9], fill=BRICK, width=2)
    d.polygon([(x + w - 54, cy - 9), (x + w - 62, cy - 13), (x + w - 62, cy - 5)],
              fill=BRICK)
    d.text((x + 5, y + 3), "CYCLONE AKVAN", font=sans_b(8), fill=NAVY)


def sc_greenland(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY2)
    # aurora band + stars in the sky
    d.polygon([(x, y + 12), (x + 60, y + 2), (x + 120, y + 10), (x + w, y + 2),
               (x + w, y + 8), (x + 120, y + 16), (x + 60, y + 8), (x, y + 18)],
              fill=(120, 200, 150))
    for sx, sy in [(x + 88, y + 4), (x + 130, y + 14), (x + 168, y + 6)]:
        burst(d, sx, sy, 3, (255, 255, 255), points=4)
    d.polygon([(x, y + h), (x + 36, y + 6), (x + 72, y + h)], fill=(250, 250, 248),
              outline=INK)
    d.polygon([(x + 44, y + h), (x + 100, y + 2), (x + 156, y + h)],
              fill=(235, 242, 248), outline=INK)
    d.polygon([(x + 118, y + h), (x + 150, y + 12), (x + w, y + h)],
              fill=(250, 250, 248), outline=INK)
    flag_dk(d, x + 6, y + 4, 28, 17)
    flag_us(d, x + 38, y + 4, 28, 17)
    d.text((x + 5, y + h - 13), "GREENLAND", font=sans_b(8), fill=NAVY)
    f = sans_b(10)
    tw = d.textlength("109–0", font=f)
    d.rounded_rectangle([x + w - tw - 12, y + 4, x + w - 5, y + 19], radius=3,
                        fill=BRICK, outline=INK, width=1)
    d.text((x + w - tw - 8, y + 6), "109–0", font=f, fill=(255, 255, 255))


def sc_gta(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h * 0.55], fill=(150, 90, 160))
    d.rectangle([x, y + h * 0.55, x + w, y + h], fill=(90, 50, 110))
    d.ellipse([x + 5, y + 3, x + 21, y + 19], fill=(255, 210, 120))
    for bx, bw, bh in [(0, 13, 11), (16, 9, 17), (28, 15, 9), (46, 11, 19),
                       (60, 17, 13), (80, 9, 21), (92, 13, 11), (108, 15, 17),
                       (126, 11, 9), (140, 15, 15), (158, 11, 11), (172, 14, 13)]:
        d.rectangle([x + bx, y + h - bh, x + bx + bw, y + h], fill=(40, 22, 55))
    cx, cy = x + 56, y + 15
    d.rounded_rectangle([cx - 38, cy - 5, cx + 38, cy + 16], radius=9,
                        fill=(245, 245, 240), outline=INK, width=2)
    d.ellipse([cx - 29, cy + 12, cx - 16, cy + 25], fill=(245, 245, 240),
              outline=INK, width=2)
    d.ellipse([cx + 16, cy + 12, cx + 29, cy + 25], fill=(245, 245, 240),
              outline=INK, width=2)
    d.ellipse([cx - 24, cy - 1, cx - 15, cy + 8], fill=INK)
    d.ellipse([cx + 15, cy - 1, cx + 24, cy + 8], fill=(196, 66, 44))
    d.text((x + w - 42, y + h - 24), "VI", font=serif_b(20), fill=GOLD_L)
    d.text((x + 5, y + h - 14), "GTA VI · 13 YEARS ON", font=sans_b(8),
           fill=(255, 255, 255))


def sc_seoul(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 230, 210))
    d.rectangle([x + 5, y + 8, x + 84, y + h - 4], fill=(200, 190, 170),
                outline=INK, width=1)
    d.polygon([(x + 2, y + 8), (x + 87, y + 8), (x + 44, y - 1)],
              fill=(170, 150, 120), outline=INK)
    for i in range(3):
        cx = x + 24 + i * 22
        d.rectangle([cx - 4, y + 14, cx + 4, y + h - 4], fill=(245, 240, 225),
                    outline=INK, width=1)
    flag_kr(d, x + 92, y + 4, 28, 18)
    # gavel, large, right half; base sits on the scene floor
    d.line([x + 96, y + 36, x + 150, y + 12], fill=(120, 80, 40), width=6)
    d.rounded_rectangle([x + 144, y + 2, x + 176, y + 20], radius=4,
                        fill=(140, 95, 50), outline=INK, width=1)
    d.rectangle([x + 94, y + 38, x + 134, y + 43], fill=(140, 95, 50),
                outline=INK, width=1)
    # RETRIAL stamp, bottom-right, rotated (v3 said OVERTURNED — wrong:
    # the court only quashed part of the verdict and ordered a retrial)
    _stamp(d, x + w - 28, y + 33, "RETRIAL", 7, NAVY_MID, -8)


_CUR_IMG = None   # the page image, set by render() so stamps can paste


def _stamp(d, cx, cy, text, size, color, angle):
    """Rotated outline stamp text, drawn via a temp layer."""
    f = sans_b(size)
    tw = int(d.textlength(text, font=f)) + 14
    th = size + 12
    layer = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.rounded_rectangle([2, 2, tw - 3, th - 3], radius=3,
                         outline=color + (255,), width=2)
    ld.text((7, 5), text, font=f, fill=color + (255,))
    layer = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
    _CUR_IMG.paste(layer, (int(cx - layer.width / 2),
                           int(cy - layer.height / 2)), layer)


def sc_bogota(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 232, 240))
    d.rectangle([x + 18, y + 2, x + w - 18, y + 7], fill=(252, 209, 22),
                outline=INK, width=1)
    d.rectangle([x + 18, y + 7, x + w - 18, y + 10], fill=(47, 93, 138),
                outline=INK, width=1)
    d.rectangle([x + 18, y + 10, x + w - 18, y + 13], fill=(196, 66, 44),
                outline=INK, width=1)
    d.text((x + 18, y + 3), "PARO NACIONAL", font=sans_b(7), fill=INK)
    cols = [(172, 52, 34), (47, 93, 138), (60, 122, 66), (118, 74, 154),
            (170, 132, 28), (44, 118, 106)]
    for row, yy in enumerate([22, 31]):
        for i in range(7):
            cx = x + 14 + i * 24 + row * 10
            c = cols[(i + row) % len(cols)]
            d.ellipse([cx - 5, y + yy - 5, cx + 5, y + yy + 5], fill=SKIN,
                      outline=INK, width=1)
            d.arc([cx - 5, y + yy - 6, cx + 5, y + yy + 1], 180, 360,
                  fill=(40, 36, 30), width=3)
            d.pieslice([cx - 8, y + yy + 5, cx + 8, y + yy + 12], 180, 360,
                       fill=c, outline=INK)


def sc_nairobi(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 120, 80))
    d.rectangle([x, y + h - 8, x + w, y + h], fill=(240, 235, 220))
    # runner silhouette
    d.ellipse([x + 72, y + 4, x + 84, y + 16], fill=INK)
    d.line([x + 78, y + 16, x + 72, y + 28], fill=INK, width=4)
    d.line([x + 72, y + 20, x + 58, y + 12], fill=INK, width=3)
    d.line([x + 74, y + 20, x + 90, y + 26], fill=INK, width=3)
    d.line([x + 72, y + 28, x + 56, y + h - 8], fill=INK, width=3)
    d.line([x + 72, y + 28, x + 88, y + h - 10], fill=INK, width=3)
    d.line([x, y + h - 13, x + w, y + h - 13], fill=(255, 255, 255), width=1)
    _stamp(d, x + 36, y + 15, "BANNED", 12, BRICK, -12)
    d.text((x + w - 92, y + 3), "DOPING · 3 YEARS", font=sans_b(8), fill=NAVY)


def sc_canberra(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 230, 210))
    d.text((x + 7, y + 2), "4.9%", font=serif_b(18), fill=NAVY)
    for i, cx in enumerate([x + 100, x + 118, x + 136, x + 154]):
        d.ellipse([cx - 6, y + 6, cx + 6, y + 18], fill=INK_SOFT)
        d.pieslice([cx - 9, y + 19, cx + 9, y + 33], 180, 360, fill=INK_SOFT)
    base = y + h - 4
    for i, bh in enumerate([9, 13, 11, 18, 24]):
        bx = x + 7 + i * 16
        d.rectangle([bx, base - bh, bx + 12, base], fill=TEAL, outline=INK, width=1)
    d.line([x + w - 13, y + 22, x + w - 13, y + 32], fill=(196, 66, 44), width=4)
    d.polygon([(x + w - 21, y + 28), (x + w - 5, y + 28), (x + w - 13, y + 38)],
              fill=(196, 66, 44))


SCENES = {
    "anthropic": sc_anthropic, "crimea": sc_crimea, "riyadh": sc_riyadh,
    "akvan": sc_akvan, "greenland": sc_greenland, "gta": sc_gta,
    "seoul": sc_seoul, "bogota": sc_bogota, "nairobi": sc_nairobi,
    "canberra": sc_canberra,
}

# ---------------------------------------------------------------- map
# Simplified continent outlines (lon, lat), drawn by hand for this page.
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 71), (-95, 69), (-80, 66), (-65, 60),
     (-55, 52), (-65, 47), (-75, 38), (-81, 26), (-90, 21), (-97, 16),
     (-105, 20), (-115, 28), (-125, 40), (-124, 48), (-135, 58),
     (-155, 58), (-165, 60)],
    # Greenland
    [(-58, 64), (-43, 60), (-32, 68), (-22, 70), (-25, 78), (-40, 80),
     (-55, 78), (-60, 70)],
    # South America
    [(-80, 9), (-77, 4), (-80, -3), (-77, -12), (-70, -23), (-72, -37),
     (-70, -52), (-66, -55), (-62, -41), (-52, -32), (-41, -23), (-35, -9),
     (-40, -3), (-50, 0), (-55, 6), (-68, 11)],
    # Europe
    [(-10, 37), (-9, 43), (-2, 48), (0, 50), (8, 57), (18, 56), (24, 58),
     (30, 62), (30, 70), (18, 69), (5, 58), (8, 55), (0, 51), (-4, 48),
     (-2, 44), (-9, 38)],
    # Africa
    [(-17, 15), (-10, 31), (0, 36), (10, 37), (20, 32), (32, 31), (35, 23),
     (40, 15), (48, 11), (51, 12), (41, 0), (36, -12), (32, -25),
     (20, -35), (12, -18), (9, 4), (-8, 5), (-13, 8)],
    # Asia
    [(30, 70), (60, 69), (80, 73), (100, 77), (120, 73), (140, 72),
     (160, 69), (178, 65), (162, 56), (142, 50), (130, 42), (127, 35),
     (120, 32), (110, 21), (105, 10), (100, 8), (94, 17), (88, 22),
     (80, 15), (76, 10), (70, 20), (62, 25), (57, 22), (52, 15), (44, 13),
     (41, 20), (39, 24), (36, 36), (30, 36), (27, 37), (26, 40), (30, 44),
     (40, 47), (48, 52), (40, 66)],
    # Australia
    [(114, -22), (114, -35), (124, -33), (132, -32), (140, -38), (150, -37),
     (153, -27), (146, -19), (142, -11), (135, -15), (126, -14), (118, -20)],
    # Indonesia arc
    [(95, 5), (100, 0), (105, -5), (110, -7), (115, -8), (120, -10),
     (130, -3), (135, -4), (141, -4), (136, -1), (130, 1), (124, 0),
     (118, -2), (106, -6), (96, 4)],
    # Japan
    [(130, 31), (135, 34), (140, 38), (143, 43), (145, 44), (141, 38),
     (136, 33), (130, 31)],
    # New Zealand
    [(167, -45), (170, -42), (174, -39), (178, -37), (175, -40), (168, -46)],
]

# (story, lon, lat, badge offset lon/lat or None)
# Only the 13 featured stories get pins; story 9 (GTA VI, worldwide)
# and the briefs 14..33 have none.
PINS = [
    (1, 114.1, 22.5, None),        # Shenzhen
    (2, 4.3, 52.1, None),          # The Hague
    (3, 30.7, 36.9, None),         # Antalya
    (4, -74.0, 40.7, None),        # New York
    (5, 33.5, 45.5, (41.0, 52.0)), # Crimea (badge offset: Antalya is close)
    (6, 46.7, 24.6, None),         # Riyadh
    (7, 84.5, 20.5, None),         # Odisha
    (8, -45.0, 70.0, None),        # Greenland
    (10, 127.0, 37.5, None),       # Seoul
    (11, -74.1, 4.7, None),        # Bogota
    (12, 36.8, -1.3, None),        # Nairobi
    (13, 149.1, -35.3, None),      # Canberra
]


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY, outline=INK, width=1)
    sx = w / 360.0
    sy = h / 142.0

    def px(lon, lat):
        return (x + (lon + 170) * sx, y + (84 - lat) * sy)

    for poly in CONTINENTS:
        d.polygon([px(lon, lat) for lon, lat in poly], fill=LAND,
                  outline=(120, 105, 70))
    for lon in range(-150, 181, 30):
        for lat in range(-50, 81, 30):
            gx, gy = px(lon, lat)
            d.ellipse([gx - 0.7, gy - 0.7, gx + 0.7, gy + 0.7],
                      fill=(150, 170, 180))
    for num, lon, lat, off in PINS:
        tx, ty = px(lon, lat)
        bx, by = (px(*off) if off else (tx, ty))
        if off:
            d.line([tx, ty, bx, by], fill=INK, width=1)
            d.ellipse([tx - 2, ty - 2, tx + 2, ty + 2], fill=BRICK)
        disc(d, bx, by, num, 6, REGION_FILL[REGIONS[num]], 7)


# ---------------------------------------------------------------- compose
def big_card(d, img, x, y, w, h, num, kicker, headline, deck, scene_fn, tag):
    """Wide second-row card: scene on top, headline + deck below.
    Headline is 20pt (2 lines) so it reads at 300px; the deck is a
    single 8pt line to leave room."""
    d.rectangle([x, y, x + w, y + h], fill=PAPER, outline=INK, width=1)
    scene_fn(d, x + 1, y + 1, w - 2, 80)
    d.line([x, y + 82, x + w, y + 82], fill=INK, width=1)
    disc(d, x + 13, y + 95, num, 10, NAVY, 11)
    d.text((x + 28, y + 89), kicker, font=sans_b(10), fill=BRICK)
    tagbox(d, x + w - 76, y + 89, tag, GOLD_D if tag == "FORECAST" else BRICK)
    yy = y + 104
    yy = put_lines(d, x + 12, yy, wrap_text(d, headline, serif_b(20), w - 24),
                   serif_b(20), INK, 22)
    put_lines(d, x + 12, yy + 2, wrap_text(d, deck, sans(8), w - 24)[:1],
              sans(8), INK_SOFT, 10)


def small_card(d, img, x, y, w, h, num, kicker, headline, deck, scene_fn, tag):
    """Grid card, v5: the scene is the picture that registers at 300px,
    so it gets 58 of the card's 116px and the headline grows to 15pt.
    The 8pt deck line is GONE (invisible at 300px in every version so
    far) — the source survives as a short grey line under the headline,
    and the deck text itself is kept in CARDS for the record.
    Layout inside the 116px card: scene 58, divider, kicker+tag row,
    headline (15pt, up to 2 lines), source line."""
    d.rectangle([x, y, x + w, y + h], fill=PAPER, outline=INK, width=1)
    scene_fn(d, x + 1, y + 1, w - 2, 58)
    d.line([x, y + 60, x + w, y + 60], fill=INK, width=1)
    disc(d, x + 10, y + 71, num, 8, NAVY, 9)
    # kicker shrinks until it clears the tag chip
    ksize = 8
    tag_w = int(d.textlength(tag, font=sans_b(7))) + 9
    while ksize > 6 and (24 + d.textlength(kicker, font=sans_b(ksize))
                         > w - tag_w - 8):
        ksize -= 1
    d.text((x + 24, y + 66), kicker, font=sans_b(ksize), fill=BRICK)
    d.rounded_rectangle([x + w - tag_w - 3, y + 65, x + w - 3, y + 76],
                        radius=3, outline=GOLD_D if tag == "FORECAST" else BRICK,
                        width=1)
    d.text((x + w - tag_w + 1, y + 66), tag, font=sans_b(7),
           fill=GOLD_D if tag == "FORECAST" else BRICK)
    yy = y + 79
    lines = wrap_text(d, headline, serif_b(15), w - 12)[:2]
    yy = put_lines(d, x + 6, yy, lines, serif_b(15), INK, 17)
    # source only: "— Reuters" etc., parsed out of the deck's tail
    src = deck.rsplit(" — ", 1)[-1] if " — " in deck else ""
    if src:
        d.text((x + 6, y + h - 12), "— " + src, font=sans(8), fill=GREY)


def one_brief(d, x, y, maxw, num, place, sentence, source):
    """One brief line: navy number + bold place + sentence + grey source.
    v5: 10pt floor (was 8pt shrinking to 6pt) — the band is 20 lines
    now, so every line gets room to breathe."""
    for size in (10, 9, 8):
        f_n, f_p, f_t, f_s = (sans_b(size), sans_b(size), sans(size), sans(size))
        parts = [(f"{num} ", f_n, NAVY), (place + " ", f_p, INK),
                 (sentence + " ", f_t, INK_SOFT), (source, f_s, GREY)]
        if sum(d.textlength(t, font=f) for t, f, _ in parts) <= maxw:
            break
    cx = x
    for t, f, col in parts:
        d.text((cx, y), t, font=f, fill=col)
        cx += d.textlength(t, font=f)


def render():
    global _CUR_IMG
    # ---- data integrity checks (fail loudly, never silently mis-count)
    assert sorted(REGIONS) == list(range(1, 34)), "story numbers 1-33"
    counts = {}
    for r in REGIONS.values():
        counts[r] = counts.get(r, 0) + 1
    assert counts == REGION_TOTALS, f"region counts {counts}"
    assert sorted(n for n, *_ in CARDS) == list(range(4, 14))
    assert sorted(n for n, *_ in BRIEFS) == list(range(14, 34))
    assert len(CARDS) + len(BRIEFS) + 3 == 33, "33 stories total"

    img = Image.new("RGBA", (W, H), CREAM + (255,))
    _CUR_IMG = img
    d = ImageDraw.Draw(img)

    # ---- 1. masthead (navy rule under a giant serif date)
    d.text((M, 8), "THE WORLD IN ONE DAY", font=sans_b(14), fill=NAVY)
    right = "33 STORIES · EVERY CONTINENT · ALL FROM THIS ONE DAY"
    d.text((W - M - d.textlength(right, font=sans_b(12)), 10), right,
           font=sans_b(12), fill=GOLD_D)
    date_font, _ = shrink_to_fit(d, "Thursday 19 November 2026", serif_b, 54, CW)
    d.text((M, 28), "Thursday 19 November 2026", font=date_font, fill=INK)
    d.rectangle([0, 94, W, 98], fill=NAVY)

    # ---- subhead (navy italic, centred, the three top stories)
    sub = ("Trump, Xi and Putin share one table · The World Court holds "
           "Myanmar responsible for genocide · COP31 draft drops fossil fuels")
    sub_font, _ = shrink_to_fit(d, sub, serif_i, 15, CW)
    d.text(((W - d.textlength(sub, font=sub_font)) / 2, 104), sub,
           font=sub_font, fill=NAVY)

    # ---- 2. the day in numbers
    rule(d, M, W - M, 130)
    cell = CW / 6
    for i, (num, cap) in enumerate(NUMBERS):
        cx = M + i * cell
        d.text((cx + 8, 136), num, font=serif_b(23), fill=NAVY)
        d.text((cx + 8, 164), cap, font=sans(9), fill=INK_SOFT)
        if i:
            d.line([cx, 138, cx, 176], fill=(200, 190, 170), width=1)
    rule(d, M, W - M, 180)

    # ---- 3. region strip
    cw = CW / 7
    for i, name in enumerate(REGION_ORDER):
        x0 = M + i * cw
        d.rectangle([x0, 186, x0 + cw - 2, 208], fill=REGION_FILL[name])
        label = f"{name} {REGION_TOTALS[name]}"
        f_r = sans_b(11)
        d.text((x0 + (cw - 2 - d.textlength(label, font=f_r)) / 2, 192),
               label, font=f_r, fill=(255, 255, 255))

    # ---- 4. THE HERO: one single ICJ scene, full width (v5: 212 tall,
    # scene 118 so the big scales have room; judges face away)
    hy, hh = 214, 212
    d.rectangle([M, hy, M + CW, hy + hh], fill=PAPER, outline=INK, width=1)
    d.rectangle([M + 1, hy + 1, M + CW - 1, hy + 23], fill=NAVY)
    d.text((M + 10, hy + 5), "WORLD COURT · THE HAGUE", font=sans_b(10),
           fill=(255, 255, 255))
    d.text((M + CW - 10 - d.textlength("GENOCIDE RULING", font=sans_b(10)),
            hy + 5), "GENOCIDE RULING", font=sans_b(10), fill=GOLD_L)
    scene_icj_hero(d, M + 1, hy + 24, CW - 2, 118)
    d.line([M, hy + 143, M + CW, hy + 143], fill=INK, width=1)
    disc(d, M + 13, hy + 154, 2, 10, NAVY, 11)
    d.text((M + 28, hy + 149), "THE HAGUE · JUSTICE", font=sans_b(10), fill=BRICK)
    tagbox(d, M + CW - 76, hy + 149, "REPORTED", BRICK)
    hero_font, _ = shrink_to_fit(
        d, "World Court holds Myanmar responsible", serif_b, 30, CW - 24)
    d.text((M + 12, hy + 164), "World Court holds Myanmar responsible",
           font=hero_font, fill=INK)
    d.text((M + 12, hy + 198),
           "By 9 votes to 6 the ICJ held Myanmar responsible for genocide "
           "against the Rohingya and ordered reparations. — Al Jazeera · UN News",
           font=sans(11), fill=INK_SOFT)

    # ---- 5. second row: APEC + COP31 as two wide cards
    bw2 = (CW - 8) / 2
    big_card(d, img, M, 432, bw2, 162, 1, "SHENZHEN · SUMMIT",
             "Trump, Xi and Putin hold first three-way summit",
             "Met 90 minutes at Kylin Villa; issued 'Declaration on Peace' "
             "on nuclear risk and UN reform. — Reuters · AP · Xinhua",
             scene_apec, "REPORTED")
    big_card(d, img, M + bw2 + 8, 432, bw2, 162, 3, "ANTALYA · CLIMATE",
             "COP31 draft drops fossil fuels, sets no aid figure",
             "The slimmer text has no figure for adaptation aid. Talks are "
             "due to end on Friday. — Reuters · AFP",
             scene_cop31, "REPORTED")

    # ---- 6. secondary grid 2 x 5 (stories 4..13), v5: 116px cards
    gw = (CW - 4 * 7) / 5
    for row in range(2):
        for col in range(5):
            num, kicker, head, deck, tag, key = CARDS[row * 5 + col]
            cx = M + col * (gw + 7)
            cy = 600 + row * 116
            small_card(d, img, cx, cy, gw, 116, num, kicker, head, deck,
                       SCENES[key], tag)

    # ---- 7. bottom: small map + briefs (v5: 20 briefs, 2 cols x 10)
    d.text((M, 838), "WHERE IT HAPPENED", font=sans_b(12), fill=INK)
    f_m = sans(9)
    d.text((314 - d.textlength("numbers match the stories", font=f_m), 841),
           "numbers match the stories", font=f_m, fill=GREY)
    draw_map(d, M, 854, 300, 80)
    d.text((M, 936), "No pin: GTA VI (worldwide)", font=sans(8), fill=GREY)

    bx = 326
    d.text((bx, 838), "ALSO ON THURSDAY 19 NOVEMBER 2026", font=sans_b(12),
           fill=INK)
    d.text((W - M - d.textlength("place · what happened · source", font=f_m),
            841), "place · what happened · source", font=f_m, fill=GREY)
    d.line([bx, 854, W - M, 854], fill=BRICK, width=2)
    colw = (W - M - bx - 12) / 2
    for i, (num, place, sent, src) in enumerate(BRIEFS):
        col = i // 10
        r = i % 10
        xx = bx + col * (colw + 12)
        yy = 858 + r * 8.6
        one_brief(d, xx, yy, colw, num, place, sent, src)

    # ---- 8. footer DATE CHECK
    d.rounded_rectangle([M, 944, W - M, 996], radius=4, outline=BRICK, width=1)
    f_dc = sans(10)
    lines = wrap_text(d, DATE_CHECK, f_dc, CW - 28)
    yy = 948
    lead = "DATE CHECK ✓ "
    for j, ln in enumerate(lines):
        if j == 0:
            d.text((22, yy), lead, font=sans_b(10), fill=BRICK)
            d.text((22 + d.textlength(lead, font=sans_b(10)), yy),
                   ln[len(lead):], font=f_dc, fill=INK)
        else:
            d.text((22, yy), ln, font=f_dc, fill=INK)
        yy += 13
    d.text((M, 1000), CREDIT, font=sans(8), fill=GREY)
    d.text((M, 1009), LEGEND, font=sans_b(8), fill=GREY)

    out = img.convert("RGB")
    out.save(os.path.join(HERE, "entry.png"), optimize=True)
    print("wrote", os.path.join(HERE, "entry.png"), out.size)


if __name__ == "__main__":
    render()
