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

# Cover C (Winning Long-Video Formula, Jose 2026-11-22): huge white serif Name of God + script subtitle + small 3 HOURS tag
B4K = __import__("os").path.dirname(__import__("os").path.abspath(__file__)) + "/covers/cover_C.jpg"
def make_c(name="Cover C ELOHIM Davids Harp", S=2):
    W, H = 1920*S, 1080*S; cx, wy, size, sp = 540*S, 120*S, 205*S, 10*S
    img = Image.open(SRC).convert("RGB").resize((W, H), Image.LANCZOS)
    glow = Image.new("L", (W, H), 0); gd = ImageDraw.Draw(glow)
    gd.ellipse((cx - 640*S, wy - 140*S, cx + 640*S, wy + 470*S), fill=165)
    glow = glow.filter(ImageFilter.GaussianBlur(130*S))
    img = Image.composite(Image.new("RGB", (W, H), (34, 24, 10)), img, glow)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    f_word = ImageFont.truetype(FONTS + "CormorantGaramond.ttf", size)
    try: f_word.set_variation_by_name("SemiBold")
    except Exception: pass
    f_script = ImageFont.truetype(FONTS + "GreatVibes-Regular.ttf", 120*S)
    f_strip = ImageFont.truetype(FONTS + "CormorantGaramond.ttf", 38*S)
    try: f_strip.set_variation_by_name("Bold")
    except Exception: pass
    spaced(d, (cx, wy), "ELOHIM", f_word, sp, (255, 255, 255, 255), shadow=sd)
    sy = wy + size + 10*S
    tw = d.textlength("David's Harp", font=f_script)
    sd.text((cx - tw / 2, sy), "David's Harp", font=f_script, fill=(0, 0, 0, 170))
    d.text((cx - tw / 2, sy), "David's Harp", font=f_script, fill=(240, 205, 125, 255))
    ty = sy + 175*S
    tw = spaced(d, (cx, ty), "3 HOURS  |  SOAKING WORSHIP", f_strip, 7*S, (255, 252, 242, 240), shadow=sd)
    d.line((cx - tw / 2 - 30*S, ty - 14*S, cx + tw / 2 + 30*S, ty - 14*S), fill=(240, 205, 125, 210), width=2*S)
    d.line((cx - tw / 2 - 30*S, ty + 54*S, cx + tw / 2 + 30*S, ty + 54*S), fill=(240, 205, 125, 210), width=2*S)
    sh = sh.filter(ImageFilter.GaussianBlur(7*S))
    out = Image.alpha_composite(img.convert("RGBA"), sh)
    out = Image.alpha_composite(out, layer).convert("RGB")
    out.save(OUT + f"{name} (4K).jpg", quality=94)
    out.save(B4K, quality=95)
    out.resize((1280, 720), Image.LANCZOS).save(OUT + f"{name} (YouTube 1280x720).jpg", quality=92)
    return out

if __name__ == "__main__" and "C" in sys.argv[1:]:
    make_c()
