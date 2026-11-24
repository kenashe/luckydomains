#!/usr/bin/env python3
"""Regenerate every derived brand asset from the originals in assets/source/.

You only need this if the logo or the founder photo changes. All generated
files are committed to the repository, so normal work never runs this.

    python3 -m pip install Pillow
    python3 scripts/make_assets.py

Inputs, in assets/source/
    logo-wordmark-original.jpg   full "LUCKY DOMAINS" lockup on white
    logo-icon-original.png       LD clover monogram on white
    headshot-master.jpg          founder portrait, 1400x1400 master

Outputs, in assets/
    logo-wordmark.png            transparent, trimmed, 700px wide  (header)
    logo-icon.png                transparent, trimmed, 512x512     (footer, manifest)
    favicon.ico                  multi size 16/32/48
    favicon-16.png favicon-32.png favicon-48.png
    apple-touch-icon.png         180x180
    icon-192.png icon-512.png    PWA manifest icons
    og-image.png                 1200x630 social share card
    about-ken.jpg                640x640 founder portrait for the About page
    logo-wordmark-reversed.png   440px wordmark for dark backgrounds: navy recolored to
                                 warm off-white, green and geometry untouched

The source images have white backgrounds. White is keyed out to transparency so
the marks sit cleanly on the navy footer and on light sections alike.
"""
import os

try:
    from PIL import Image, ImageDraw
except ImportError:
    raise SystemExit("Pillow is required:  python3 -m pip install Pillow")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "source")
OUT = os.path.join(ROOT, "assets")

WORDMARK_SRC = os.path.join(SRC, "logo-wordmark-original.jpg")
ICON_SRC = os.path.join(SRC, "logo-icon-original.png")
HEADSHOT_SRC = os.path.join(SRC, "headshot-master.jpg")

WHITE = (255, 255, 255, 255)
GREEN = (22, 199, 132, 255)      # brand green #16C784

# Pixels at or above this in all channels are treated as background.
WHITE_THRESHOLD = 238


def white_to_transparent(img, thresh=WHITE_THRESHOLD):
    img = img.convert("RGBA")
    out = []
    for r, g, b, a in img.getdata():
        out.append((r, g, b, 0) if (r >= thresh and g >= thresh and b >= thresh)
                   else (r, g, b, a))
    img.putdata(out)
    return img


def autocrop(img, pad=0):
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    if pad:
        w, h = img.size
        canvas = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
        canvas.paste(img, (pad, pad), img)
        img = canvas
    return img


def resize_w(img, target_w):
    w, h = img.size
    if w == target_w:
        return img
    return img.resize((target_w, max(1, round(h * target_w / w))), Image.LANCZOS)


def square_on(img, size, bg):
    """Center img on a square canvas, occupying 78 percent of the width."""
    canvas = Image.new("RGBA", (size, size), bg)
    inner = round(size * 0.78)
    s = img.copy()
    w, h = s.size
    scale = inner / max(w, h)
    s = s.resize((max(1, round(w * scale)), max(1, round(h * scale))), Image.LANCZOS)
    sw, sh = s.size
    canvas.paste(s, ((size - sw) // 2, (size - sh) // 2), s)
    return canvas


def reversed_wordmark(img, navy=(12, 35, 64), green=(22, 199, 132),
                      light=(236, 231, 220)):
    """Recolor the navy parts of the wordmark for dark backgrounds."""
    img = img.convert("RGBA")
    axis = [g - n for g, n in zip(green, navy)]
    norm = float(sum(a * a for a in axis))
    out = Image.new("RGBA", img.size)
    src, dst = img.load(), out.load()
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            r, g, b, a = src[x, y]
            t = ((r - navy[0]) * axis[0] + (g - navy[1]) * axis[1]
                 + (b - navy[2]) * axis[2]) / norm
            t = 0.0 if t < 0 else 1.0 if t > 1 else t
            dst[x, y] = tuple(round(light[i] * (1 - t) + green[i] * t)
                              for i in range(3)) + (a,)
    return out


def main():
    for p in (WORDMARK_SRC, ICON_SRC, HEADSHOT_SRC):
        if not os.path.isfile(p):
            raise SystemExit("Missing source file: %s" % p)
    os.makedirs(OUT, exist_ok=True)

    # Wordmark, transparent and trimmed. 700px is comfortably retina sharp for
    # the ~170px the header actually renders it at.
    wm = resize_w(autocrop(white_to_transparent(Image.open(WORDMARK_SRC))), 700)
    wm.save(os.path.join(OUT, "logo-wordmark.png"))
    print("logo-wordmark.png", wm.size)

    # Clover monogram, transparent and trimmed.
    icon = resize_w(autocrop(white_to_transparent(Image.open(ICON_SRC)), pad=4), 512)
    icon.save(os.path.join(OUT, "logo-icon.png"))
    print("logo-icon.png", icon.size)

    # Favicons on white, which stays legible at 16px where transparency does not.
    for size in (16, 32, 48):
        square_on(icon, size, WHITE).save(os.path.join(OUT, "favicon-%d.png" % size))
    square_on(icon, 48, WHITE).save(os.path.join(OUT, "favicon.ico"),
                                    sizes=[(16, 16), (32, 32), (48, 48)])
    square_on(icon, 180, WHITE).save(os.path.join(OUT, "apple-touch-icon.png"))
    square_on(icon, 192, WHITE).save(os.path.join(OUT, "icon-192.png"))
    square_on(icon, 512, WHITE).save(os.path.join(OUT, "icon-512.png"))
    print("favicons, apple-touch-icon and manifest icons written")

    # Open Graph card: centered wordmark on white with a green accent rule.
    og_w, og_h = 1200, 630
    og = Image.new("RGBA", (og_w, og_h), WHITE)
    ogwm = resize_w(wm, round(og_w * 0.62))
    ow, oh = ogwm.size
    oy = (og_h - oh) // 2 - 18
    og.paste(ogwm, ((og_w - ow) // 2, oy), ogwm)
    rule_w = round(og_w * 0.20)
    rx = (og_w - rule_w) // 2
    ry = oy + oh + 46
    ImageDraw.Draw(og).rounded_rectangle([rx, ry, rx + rule_w, ry + 8], radius=4,
                                         fill=GREEN)
    og.convert("RGB").save(os.path.join(OUT, "og-image.png"), quality=92)
    print("og-image.png", (og_w, og_h))

    # Founder portrait for the About page: center square, 640px, compressed.
    hs = Image.open(HEADSHOT_SRC).convert("RGB")
    w, h = hs.size
    s = min(w, h)
    hs = hs.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s))
    hs = hs.resize((640, 640), Image.LANCZOS)
    hs.save(os.path.join(OUT, "about-ken.jpg"), quality=86, optimize=True,
            progressive=True)
    print("about-ken.jpg", hs.size)

    # Reversed wordmark for the dark header and footer. Only the navy changes
    # color: each pixel is placed between brand navy and brand green and the
    # navy end is swapped for warm off-white. Shapes and proportions are identical.
    # 440px wide is ample for the 153px header and 185px footer at 2x density.
    rev = resize_w(reversed_wordmark(Image.open(os.path.join(OUT, "logo-wordmark.png"))), 440)
    rev.save(os.path.join(OUT, "logo-wordmark-reversed.png"), optimize=True)
    print("logo-wordmark-reversed.png", rev.size)

    print("\nDone. Run: python3 tests/test_site.py")


if __name__ == "__main__":
    main()
