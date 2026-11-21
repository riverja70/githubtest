# Elohim harp cover: spaced thin-serif theme word + small reference + thin "3 HOURS | ..." strip.
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
SRC = "/mnt/project-files/Elohim Harp/King David harp 4K.png"
FONTS = "/mnt/project-files/scripts/fonts/"
OUT = "/mnt/project-files/Elohim Harp/cover/"
W, H = 1920, 1080

def spaced(draw, xy, text, font, spacing, fill, anchor_center=True, shadow=None):
    widths = [draw.textlength(c, font=font) for c in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x, y = xy
    if anchor_center: x -= total / 2
    for c, w in zip(text, widths):
        if shadow: shadow.text((x, y), c, font=font, fill=(0, 0, 0, 150))
        draw.text((x, y), c, font=font, fill=fill)
        x += w + spacing
    return total

def make(name, word, ref, strip, cx=470, wy=170, size=150, sp=26):
    img = Image.open(SRC).convert("RGB").resize((W, H), Image.LANCZOS)
    # soft darken behind text for legibility
    glow = Image.new("L", (W, H), 0); gd = ImageDraw.Draw(glow)
    gd.ellipse((cx - 560, wy - 120, cx + 560, wy + 360), fill=150)
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    img = Image.composite(Image.new("RGB", (W, H), (40, 28, 10)), img, glow)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    f_word = ImageFont.truetype(FONTS + "CormorantGaramond.ttf", size)
    try: f_word.set_variation_by_name("Light")
    except Exception: pass
    f_ref = ImageFont.truetype(FONTS + "CormorantGaramond.ttf", 44)
    try: f_ref.set_variation_by_name("Medium")
    except Exception: pass
    f_strip = ImageFont.truetype(FONTS + "CormorantGaramond.ttf", 36)
    try: f_strip.set_variation_by_name("SemiBold")
    except Exception: pass
    spaced(d, (cx, wy), word, f_word, sp, (255, 250, 238, 255), shadow=sd)
    spaced(d, (cx, wy + size + 18), ref, f_ref, 10, (236, 200, 120, 255), shadow=sd)
    sy = wy + size + 100
    tw = spaced(d, (cx, sy), strip, f_strip, 6, (255, 250, 238, 235), shadow=sd)
    d.line((cx - tw / 2 - 30, sy - 14, cx + tw / 2 + 30, sy - 14), fill=(236, 200, 120, 200), width=2)
    d.line((cx - tw / 2 - 30, sy + 52, cx + tw / 2 + 30, sy + 52), fill=(236, 200, 120, 200), width=2)
    sh = sh.filter(ImageFilter.GaussianBlur(6))
    out = Image.alpha_composite(img.convert("RGBA"), sh)
    out = Image.alpha_composite(out, layer).convert("RGB")
    out.save(OUT + f"{name} (1920).jpg", quality=93)
    out.resize((1280, 720), Image.LANCZOS).save(OUT + f"{name} (YouTube 1280x720).jpg", quality=92)

make("Cover A ELOHIM", "ELOHIM", "GENESIS 1:1", "3 HOURS  |  HARP WORSHIP")
make("Cover B PRAISE", "PRAISE HIM", "PSALM 150:3", "3 HOURS  |  HARP WORSHIP", size=118, sp=14)
