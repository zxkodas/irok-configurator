# Generates docs/hero.png, the banner shown at the top of the README.
#
# The key grid follows the physical Irok ND63 MAX: five rows, 15u wide, with the
# arrow and navigation keys sitting inline at the right of rows 4 and 5 rather
# than in a separated cluster. That is what makes the keys come out the right
# size; adding a cluster gap would need ~18.6u and shrink every key.
#
# Keycaps are drawn empty, with no legends, and ignore the board's own styling.
#
# Rerun after replacing assets/irok.ico:
#   python docs\make-hero.py

import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON = os.path.join(ROOT, "assets", "irok.ico")
OUT = os.path.join(ROOT, "docs", "hero.png")

W, H = 1200, 300

BG = (13, 17, 23)
WIN = (22, 27, 34)
WIN_BAR = (28, 33, 41)
BORDER = (48, 54, 61)
SIDEBAR = (26, 31, 39)
KEY = (35, 41, 49)
KEY_EDGE = (54, 61, 70)
KEY_ON = (255, 107, 74)
KEY_ON_EDGE = (255, 138, 110)
INK = (240, 244, 248)
MUTED = (139, 148, 158)
ORANGE = (255, 107, 74)

FONTS = r"C:\Windows\Fonts"

# 15u per row, matching the board. Empty string means an unmarked modifier.
# (width, key id or None)
ROWS = [
    # row 1: Esc .. Backspace(2u)
    [(1, None), (1, None), (1, None), (1, None), (1, None), (1, None),
     (1, None), (1, None), (1, None), (1, None), (1, None), (1, None),
     (1, None), (2, None)],
    # row 2: Tab(1.5) .. backslash(1.5)
    [(1.5, None), (1, None), (1, None), (1, None), (1, None), (1, None),
     (1, None), (1, None), (1, None), (1, None), (1, None), (1, None),
     (1, None), (1.5, None)],
    # row 3: Caps(1.75) .. Enter(2.25)
    [(1.75, None), (1, None), (1, None), (1, None), (1, None), (1, None),
     (1, None), (1, None), (1, None), (1, None), (1, None), (1, None),
     (2.25, "enter")],
    # row 4: Shift(2.25) .. Shift(0.75), Up, Del. The right shift is narrower so
    # the arrow and Del keys fit inline; that is what keeps the row at 15u.
    [(2.25, None), (1, None), (1, None), (1, None), (1, None), (1, None),
     (1, None), (1, None), (1, None), (1, None), (1, None), (0.75, None),
     (1, "up"), (1, None)],
    # row 5: Ctrl(1.25) Win Alt Space(6.25) Alt Fn arrows
    [(1.25, None), (1.25, None), (1.25, None), (6.25, None), (1, None),
     (1, None), (1, "left"), (1, "down"), (1, "right")],
]

ACCENT = {"left", "down", "right"}


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    icon_big = Image.open(ICON).convert("RGBA").resize((76, 76), Image.LANCZOS)
    icon_bar = Image.open(ICON).convert("RGBA").resize((13, 13), Image.LANCZOS)

    f_title = font("segoeuib.ttf", 52)
    f_tag = font("segoeui.ttf", 22)
    f_tick = font("segoeui.ttf", 15)
    f_small = font("segoeui.ttf", 10)

    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # ---------- left ----------
    img.paste(icon_big, (64, 56), icon_big)
    d.text((168, 60), "Irok Configurator", font=f_title, fill=INK)
    d.text((170, 126), "The Irok web software, without the browser.", font=f_tag, fill=MUTED)

    for i, t in enumerate([
        "One shortcut, no browser tab",
        "Opens in its own window",
        "Uses the browser you have",
    ]):
        ty = 176 + i * 26
        d.ellipse((170, ty + 6, 177, ty + 13), fill=ORANGE)
        d.text((190, ty), t, font=f_tick, fill=(170, 178, 188))

    # ---------- window ----------
    wx, wy, ww, wh = 620, 44, 536, 212
    d.rounded_rectangle((wx + 5, wy + 7, wx + ww + 5, wy + wh + 7), radius=12, fill=(8, 11, 15))
    d.rounded_rectangle((wx, wy, wx + ww, wy + wh), radius=12, fill=WIN, outline=BORDER, width=2)

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
        d.rounded_rectangle((wx + 34, yy - 2, wx + 34 + (30 - i * 2), yy + 4), radius=2,
                            fill=(86, 40, 30) if i == 0 else (48, 54, 61))

    # ---------- keyboard ----------
    # Board is 15u wide. Key height is derived from the unit so the caps come out
    # roughly as wide as they are tall, which is how the board reads in person.
    kb_x = wx + sb_w + 18
    kb_w = (wx + ww - 18) - kb_x
    gap = 3
    u = kb_w / 15.0
    kh = u * 0.94
    board_h = len(ROWS) * kh + (len(ROWS) - 1) * gap
    kb_y = body_top + (body_h - board_h) / 2

    for ri, row in enumerate(ROWS):
        y = kb_y + ri * (kh + gap)
        x = kb_x
        for kw, kid in row:
            on = kid in ACCENT
            w = u * kw - gap
            h = kh - gap
            d.rounded_rectangle(
                (x, y, x + w, y + h), radius=4,
                fill=KEY_ON if on else KEY,
                outline=KEY_ON_EDGE if on else KEY_EDGE, width=1)
            x += u * kw

    img.save(OUT, "PNG", optimize=True)
    print("wrote", OUT, img.size)
    print("key unit %.1fpx, cap %.1f x %.1f" % (u, u - gap, kh - gap))


if __name__ == "__main__":
    main()
