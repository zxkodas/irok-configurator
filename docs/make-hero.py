# Generates docs/hero.png, the banner shown at the top of the README.
#
# Draws the launcher as a Start menu entry opening the configurator in its own
# window, using the real Irok favicon.
#
# Rerun after replacing assets/irok.ico:
#   python docs\make-hero.py

import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON = os.path.join(ROOT, "assets", "irok.ico")
OUT = os.path.join(ROOT, "docs", "hero.png")

W, H = 1200, 300
BG = (255, 255, 255)
INK = (23, 23, 26)
MUTED = (108, 112, 120)
LINE = (222, 225, 230)
PANEL = (248, 249, 251)
ORANGE = (255, 107, 74)

FONTS = r"C:\Windows\Fonts"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


def rounded(draw, box, radius, **kw):
    draw.rounded_rectangle(box, radius=radius, **kw)


def centered(draw, cx, y, text, f, fill):
    l, t, r, b = draw.textbbox((0, 0), text, font=f)
    draw.text((cx - (r - l) / 2, y), text, font=f, fill=fill)


def keycap(d, x, y, w, h, label, f, fill, text_fill):
    rounded(d, (x, y, x + w, y + h), 4, fill=fill, outline=LINE, width=1)
    l, t, r, b = d.textbbox((0, 0), label, font=f)
    d.text((x + (w - (r - l)) / 2, y + (h - (b - t)) / 2 - t), label, font=f, fill=text_fill)


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    icon_big = Image.open(ICON).convert("RGBA").resize((76, 76), Image.LANCZOS)
    icon_sm = Image.open(ICON).convert("RGBA").resize((30, 30), Image.LANCZOS)
    icon_bar = Image.open(ICON).convert("RGBA").resize((13, 13), Image.LANCZOS)

    f_title = font("segoeuib.ttf", 52)
    f_tag = font("segoeui.ttf", 22)
    f_app = font("segoeuib.ttf", 16)
    f_lbl = font("seguisb.ttf", 12)
    f_small = font("segoeui.ttf", 11)

    # --- left: icon + name + one-line description ---
    img.paste(icon_big, (64, 56), icon_big)

    d.text((168, 60), "Irok Configurator", font=f_title, fill=INK)
    d.text((170, 126), "The Irok web software, without the browser.", font=f_tag, fill=MUTED)

    # three quiet feature ticks, no arrows, no numbered steps
    f_tick = font("segoeui.ttf", 15)
    ticks = ["One shortcut to the configurator", "Opens in its own window", "Nothing to configure"]
    ty = 176
    for t in ticks:
        d.ellipse((170, ty + 6, 170 + 7, ty + 13), fill=ORANGE)
        d.text((190, ty), t, font=f_tick, fill=(78, 82, 90))
        ty += 26

    # --- right: the app window, as it appears ---
    wx, wy, ww, wh = 620, 52, 516, 200
    rounded(d, (wx + 6, wy + 8, wx + ww + 6, wy + wh + 8), 12, fill=(234, 236, 240))
    rounded(d, (wx, wy, wx + ww, wy + wh), 12, fill=(255, 255, 255), outline=LINE, width=2)

    # titlebar
    rounded(d, (wx + 1, wy + 1, wx + ww - 1, wy + 34), 11, fill=(242, 243, 246))
    d.rectangle((wx + 1, wy + 24, wx + ww - 1, wy + 34), fill=(242, 243, 246))
    d.line((wx + 1, wy + 34, wx + ww - 1, wy + 34), fill=LINE)
    for i, c in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))):
        cx = wx + 18 + i * 18
        d.ellipse((cx, wy + 12, cx + 10, wy + 22), fill=c)
    img.paste(icon_bar, (wx + 78, wy + 11), icon_bar)
    d.text((wx + 97, wy + 11), "Irok Configurator", font=f_small, fill=(92, 96, 104))

    # window body: sidebar + keyboard grid, standing in for the configurator UI
    d.rectangle((wx + 1, wy + 35, wx + 132, wy + wh - 1), fill=(250, 250, 252))
    d.line((wx + 132, wy + 35, wx + 132, wy + wh - 1), fill=LINE)
    for i in range(5):
        yy = wy + 52 + i * 24
        sel = i == 0
        if sel:
            rounded(d, (wx + 12, yy - 7, wx + 122, yy + 9), 4, fill=(255, 234, 228))
        d.rounded_rectangle((wx + 22, yy - 4, wx + 32, yy + 6), radius=2,
                            fill=ORANGE if sel else (216, 219, 224))
        d.rounded_rectangle((wx + 40, yy - 2, wx + 40 + (44 - i * 4), yy + 4), radius=2,
                            fill=(206, 210, 216) if not sel else (246, 170, 150))

    # keyboard grid, sized from the widest row so nothing spills past the window
    rows = [
        [1] * 15,
        [1.4, 1.2, 1.4, 1.8],
        [1.3, 1.3, 5.4, 1.3, 1.3],
        [1.6, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1, 1.8],
        [2.3, 1.1, 1.1, 1.1, 1.1, 2.5],
    ]
    kx0, ky0 = wx + 156, wy + 58
    grid_w = (wx + ww - 28) - kx0
    kh, gap = 28, 4
    # widest row, in key units; gap is subtracted once per key, not per unit
    units = max(sum(r) for r in rows)
    max_keys = max(len(r) for r in rows)
    kw = (grid_w + gap * max_keys) / units

    highlights = {(3, 3), (2, 7)}

    for ri, keys in enumerate(rows):
        y = ky0 + ri * kh
        row_w = kw * sum(keys)
        x = kx0 + (grid_w - row_w) / 2
        for ki, k in enumerate(keys):
            fill = (255, 214, 203) if (ri, ki) in highlights else (240, 242, 245)
            keycap(d, x, y, kw * k - gap, kh - gap, "", f_small, fill, INK)
            x += kw * k

    img.save(OUT, "PNG", optimize=True)
    print("wrote", OUT, img.size)


if __name__ == "__main__":
    main()
