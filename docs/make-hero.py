# Generates docs/hero.png, the banner shown at the top of the README.
#
# Layout is a real 65% board: 5 rows, 15u wide, with the navigation cluster
# offset by a gap. Every row starts at the same x and keys advance by an exact
# unit width, so the grid lines up instead of drifting row to row.
#
# Rerun after replacing assets/irok.ico:
#   python docs\make-hero.py

import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON = os.path.join(ROOT, "assets", "irok.ico")
OUT = os.path.join(ROOT, "docs", "hero.png")

W, H = 1200, 300

# dark theme
BG = (13, 17, 23)
PANEL = (22, 27, 34)
WIN = (22, 27, 34)
WIN_BAR = (28, 33, 41)
BORDER = (48, 54, 61)
KEY = (35, 41, 49)
KEY_EDGE = (52, 59, 68)
KEY_ON = (255, 107, 74)
SIDEBAR = (26, 31, 39)
SIDE_TEXT = (72, 79, 88)
INK = (240, 244, 248)
MUTED = (139, 148, 158)
ORANGE = (255, 107, 74)

FONTS = r"C:\Windows\Fonts"

# 65% layout. Each row is (main cluster, right cluster). Widths in units.
ROWS = [
    ([("`", 1), ("1", 1), ("2", 1), ("3", 1), ("4", 1), ("5", 1), ("6", 1),
      ("7", 1), ("8", 1), ("9", 1), ("0", 1), ("-", 1), ("=", 1), ("Bksp", 2)],
     [("Del", 1)]),
    ([("Tab", 1.5), ("Q", 1), ("W", 1), ("E", 1), ("R", 1), ("T", 1), ("Y", 1),
      ("U", 1), ("I", 1), ("O", 1), ("P", 1), ("[", 1), ("]", 1), ("\\", 1.5)],
     [("Hm", 1)]),
    ([("Caps", 1.75), ("A", 1), ("S", 1), ("D", 1), ("F", 1), ("G", 1), ("H", 1),
      ("J", 1), ("K", 1), ("L", 1), (";", 1), ("'", 1), ("Enter", 2.25)],
     [("Pu", 1)]),
    ([("Shift", 2.25), ("Z", 1), ("X", 1), ("C", 1), ("V", 1), ("B", 1),
      ("N", 1), ("M", 1), (",", 1), (".", 1), ("/", 1), ("Shift", 1.75)],
     [("\u25b2", 1), ("Pd", 1)]),
    ([("Ctrl", 1.25), ("Win", 1.25), ("Alt", 1.25), ("", 6.25),
      ("Alt", 1.25), ("Fn", 1.25)],
     [("\u25c0", 1), ("\u25bc", 1), ("\u25b6", 1)]),
]

# keys drawn in the accent colour, addressed as (row, key label)
ACCENT = {(0, "Bksp"), (2, "Enter")}


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


def draw_key(d, x, y, w, h, label, f, fill, edge, text_fill):
    d.rounded_rectangle((x, y, x + w, y + h), radius=4, fill=fill, outline=edge, width=1)
    if not label:
        return
    bb = d.textbbox((0, 0), label, font=f)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    d.text((x + (w - tw) / 2 - bb[0], y + (h - th) / 2 - bb[1]), label, font=f, fill=text_fill)


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    icon_big = Image.open(ICON).convert("RGBA").resize((76, 76), Image.LANCZOS)
    icon_bar = Image.open(ICON).convert("RGBA").resize((13, 13), Image.LANCZOS)

    f_title = font("segoeuib.ttf", 52)
    f_tag = font("segoeui.ttf", 22)
    f_tick = font("segoeui.ttf", 15)
    f_small = font("segoeui.ttf", 10)
    f_side = font("segoeui.ttf", 11)

    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # ---------- left: icon, name, tagline, ticks ----------
    img.paste(icon_big, (64, 56), icon_big)
    d.text((168, 60), "Irok Configurator", font=f_title, fill=INK)
    d.text((170, 126), "The Irok web software, without the browser.", font=f_tag, fill=MUTED)

    ticks = [
        "One shortcut, no browser tab",
        "Opens in its own window",
        "Uses the browser you have",
    ]
    ty = 176
    for t in ticks:
        d.ellipse((170, ty + 6, 177, ty + 13), fill=ORANGE)
        d.text((190, ty), t, font=f_tick, fill=(170, 178, 188))
        ty += 26

    # ---------- right: the app window ----------
    wx, wy, ww, wh = 620, 44, 536, 212
    # drop shadow
    d.rounded_rectangle((wx + 5, wy + 7, wx + ww + 5, wy + wh + 7), radius=12, fill=(8, 11, 15))
    d.rounded_rectangle((wx, wy, wx + ww, wy + wh), radius=12, fill=WIN, outline=BORDER, width=2)

    # titlebar
    d.rounded_rectangle((wx + 1, wy + 1, wx + ww - 1, wy + 32), radius=11, fill=WIN_BAR)
    d.rectangle((wx + 1, wy + 22, wx + ww - 1, wy + 32), fill=WIN_BAR)
    d.line((wx + 1, wy + 32, wx + ww - 1, wy + 32), fill=BORDER)
    for i, c in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))):
        cx = wx + 17 + i * 18
        d.ellipse((cx, wy + 11, cx + 10, wy + 21), fill=c)
    img.paste(icon_bar, (wx + 76, wy + 10), icon_bar)
    d.text((wx + 95, wy + 10), "Irok Configurator", font=f_small, fill=(130, 138, 148))

    body_top = wy + 33
    body_h = wh - 34

    # ---------- sidebar ----------
    sb_w = 78
    d.rectangle((wx + 1, body_top, wx + sb_w, wy + wh - 1), fill=SIDEBAR)
    d.line((wx + sb_w, body_top, wx + sb_w, wy + wh - 1), fill=BORDER)
    for i in range(5):
        yy = body_top + 22 + i * 27
        if i == 0:
            d.rounded_rectangle((wx + 9, yy - 9, wx + sb_w - 10, yy + 11), radius=5,
                                fill=(45, 24, 20))
        d.rounded_rectangle((wx + 18, yy - 4, wx + 27, yy + 6), radius=2,
                            fill=ORANGE if i == 0 else (52, 59, 68))
        d.rounded_rectangle((wx + 34, yy - 2, wx + 34 + (32 - i * 2), yy + 4), radius=2,
                            fill=(86, 40, 30) if i == 0 else (48, 54, 61))

    # ---------- keyboard grid ----------
    kb_x = wx + sb_w + 16
    kb_w = (wx + ww - 18) - kb_x
    gap_u = 0.6                                   # empty units before the nav block
    main_u = 15                                   # main cluster is 15u on every row
    nav_u = max(sum(w for _, w in nav) for _, nav in ROWS)
    total_u = main_u + gap_u + nav_u
    kh, gap = 28, 3
    u = kb_w / total_u

    kb_y = body_top + (body_h - (len(ROWS) * kh - gap)) / 2
    nav_x = kb_x + u * (main_u + gap_u)

    for ri, (main, nav) in enumerate(ROWS):
        y = kb_y + ri * kh
        # main cluster: every row starts at the same x and advances by exact units
        x = kb_x
        for label, kw in main:
            on = (ri, label) in ACCENT
            draw_key(d, x, y, u * kw - gap, kh - gap, label, f_small,
                     KEY_ON if on else KEY,
                     (255, 138, 110) if on else KEY_EDGE,
                     (28, 20, 18) if on else SIDE_TEXT)
            x += u * kw
        # nav cluster: right-aligned so its far edge lands on the board's edge
        row_nav_u = sum(w for _, w in nav)
        x = nav_x + u * (nav_u - row_nav_u)
        for label, kw in nav:
            draw_key(d, x, y, u * kw - gap, kh - gap, label, f_small, KEY, KEY_EDGE, SIDE_TEXT)
            x += u * kw

    img.save(OUT, "PNG", optimize=True)
    print("wrote", OUT, img.size)


if __name__ == "__main__":
    main()
