# Generates docs/hero.png, the banner shown at the top of the README.
#
# Draws a Windows-keypress -> Start search -> app window sequence using the real
# Irok favicon, so the README leads with a picture of the actual flow rather than
# a paragraph explaining it.
#
# Rerun after replacing assets/irok.ico:
#   python docs\make-hero.py

import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON = os.path.join(ROOT, "assets", "irok.ico")
OUT = os.path.join(ROOT, "docs", "hero.png")

W, H = 1280, 420
BG = (255, 255, 255)
INK = (23, 23, 26)
MUTED = (108, 112, 120)
LINE = (226, 228, 232)
PANEL = (247, 248, 250)
ORANGE = (255, 107, 74)

FONTS = r"C:\Windows\Fonts"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


def rounded(draw, box, radius, **kw):
    draw.rounded_rectangle(box, radius=radius, **kw)


def centered(draw, cx, y, text, f, fill):
    l, t, r, b = draw.textbbox((0, 0), text, font=f)
    draw.text((cx - (r - l) / 2, y), text, font=f, fill=fill)


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    icon = Image.open(ICON).convert("RGBA").resize((44, 44), Image.LANCZOS)

    f_key = font("segoeuib.ttf", 21)
    f_win = font("seguisb.ttf", 27)
    f_app = font("segoeuib.ttf", 17)
    f_cap = font("segoeui.ttf", 15)
    f_title = font("segoeuib.ttf", 46)
    f_sub = font("segoeui.ttf", 21)
    f_step = font("seguisb.ttf", 15)

    # --- headline ---
    d.text((60, 44), "Irok Configurator", font=f_title, fill=INK)
    d.text((62, 104), "Win key, type \u201cIrok\u201d, done.", font=f_sub, fill=MUTED)

    # --- the three-step flow ---
    y0, h = 168, 132
    xs = [60, 448, 836]
    labels = ["Press Win", "Type \u201cIrok\u201d", "Configurator opens"]
    w = 300

    for i, x in enumerate(xs):
        rounded(d, (x, y0, x + w, y0 + h), 14, fill=PANEL, outline=LINE, width=2)

        # step badge
        d.ellipse((x + 18, y0 + 18, x + 18 + 26, y0 + 18 + 26), fill=ORANGE)
        centered(d, x + 18 + 13, y0 + 22, str(i + 1), f_step, (255, 255, 255))

        if i == 0:
            # windows key glyph
            gx, gy, gw, gh = x + 122, y0 + 40, 56, 56
            for dx, dy in ((0, 0), (gw / 2 + 3, 0), (0, gh / 2 + 3), (gw / 2 + 3, gh / 2 + 3)):
                d.rectangle((gx + dx, gy + dy, gx + dx + gw / 2 - 3, gy + dy + gh / 2 - 3), fill=INK)
        elif i == 1:
            # start search pill with the app name
            bx, by, bw, bh = x + 40, y0 + 42, 220, 48
            rounded(d, (bx, by, bx + bw, by + bh), 8, fill=(255, 255, 255), outline=(198, 202, 208), width=2)
            mag_cx, mag_cy, mag_r = bx + 26, by + bh / 2, 8
            d.ellipse((mag_cx - mag_r, mag_cy - mag_r, mag_cx + mag_r, mag_cy + mag_r), outline=MUTED, width=2)
            d.line((mag_cx + mag_r - 3, mag_cy + mag_r - 3, mag_cx + mag_r + 4, mag_cy + mag_r + 4), fill=MUTED, width=2)
            d.text((bx + 44, by + 13), "Irok", font=f_app, fill=INK)
        else:
            # a mock app window with the real favicon as its titlebar icon
            wx, wy, ww, wh = x + 40, y0 + 40, 220, 60
            rounded(d, (wx, wy, wx + ww, wy + wh), 6, fill=(255, 255, 255), outline=(198, 202, 208), width=2)
            d.rectangle((wx + 1, wy + 1, wx + ww - 1, wy + 22), fill=(241, 242, 245))
            d.line((wx + 1, wy + 22, wx + ww - 1, wy + 22), fill=(214, 217, 222))
            d.ellipse((wx + 8, wy + 8, wx + 16, wy + 16), fill=(255, 95, 86))
            d.ellipse((wx + 19, wy + 8, wx + 27, wy + 16), fill=(255, 189, 46))
            d.ellipse((wx + 30, wy + 8, wx + 38, wy + 16), fill=(39, 201, 63))
            img.paste(icon.resize((13, 13), Image.LANCZOS), (wx + 46, wy + 5), icon.resize((13, 13), Image.LANCZOS))
            d.text((wx + 65, wy + 5), "Irok Configurator", font=font("segoeui.ttf", 11), fill=MUTED)
            # fake keyboard rows
            for r in range(2):
                for c in range(9):
                    kx = wx + 12 + c * 23
                    ky = wy + 32 + r * 13
                    d.rounded_rectangle((kx, ky, kx + 18, ky + 9), radius=2, fill=(233, 235, 239))

        centered(d, x + w / 2, y0 + h + 14, labels[i], f_cap, MUTED)

        if i < 2:
            ax = x + w + 30
            d.line((ax, y0 + h / 2, ax + 26, y0 + h / 2), fill=(200, 204, 210), width=2)
            d.polygon(
                [(ax + 26, y0 + h / 2 - 5), (ax + 33, y0 + h / 2), (ax + 26, y0 + h / 2 + 5)],
                fill=(200, 204, 210),
            )

    img.save(OUT, "PNG", optimize=True)
    print("wrote", OUT, img.size)


if __name__ == "__main__":
    main()
