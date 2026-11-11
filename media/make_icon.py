"""Draws the Camelus' Movable Roll Frame icon.

The same badge and camel as Camelus' Enhanced Quest Log, with a loot die
in place of the check mark.
Usage: python3 make_icon.py OUT_DIR
Writes icon_512.png (master), preview_256.png and CamelusMovableRollFrame.tga (64x64).
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

S = 512  # master size, scaled down at the end for smooth edges
out_dir = sys.argv[1]


def radial_disc(size, radius, inner, outer):
    """A disc with a radial gradient from inner (centre) to outer (edge)."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = img.load()
    c = size / 2
    for y in range(size):
        for x in range(size):
            d = math.hypot(x - c + 0.5, y - c + 0.5)
            if d <= radius:
                t = min(1.0, d / radius)
                t = t * t
                px[x, y] = tuple(int(inner[i] + (outer[i] - inner[i]) * t) for i in range(3)) + (255,)
    return img


def camel_mask():
    """Camel silhouette (dromedary, facing right) as a white-on-black mask."""
    m = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(m)
    # body
    d.ellipse((112, 232, 334, 320), fill=255)
    # hump: a smooth hill, steeper at the back, peak a little behind the middle
    hump = []
    for i in range(0, 41):
        t = i / 40
        x = 132 + t * 184
        h = math.sin(math.pi * t) ** 1.6 * (1 - 0.25 * t)
        hump.append((x, 262 - h * 112))
    d.polygon(hump + [(316, 280), (132, 280)], fill=255)
    # chest / base of the neck
    d.ellipse((268, 222, 338, 300), fill=255)
    # neck, curving forward and up
    d.polygon([(300, 250), (330, 232), (352, 196), (368, 150), (392, 136),
               (400, 160), (382, 206), (360, 252), (330, 286)], fill=255)
    # head and muzzle
    d.ellipse((364, 118, 418, 162), fill=255)
    d.polygon([(392, 124), (440, 140), (444, 156), (430, 166), (396, 162)], fill=255)
    # ear
    d.polygon([(372, 124), (378, 104), (388, 122)], fill=255)
    # legs (slightly tapered, knees a bit thicker)
    for x0, x1, lean in ((150, 172, -6), (186, 207, 4), (282, 303, -4), (312, 333, 6)):
        d.polygon([(x0, 290), (x1, 290), (x1 + lean + 2, 352), (x1 + lean - 1, 404),
                   (x0 + lean + 1, 404), (x0 + lean - 2, 352)], fill=255)
        d.ellipse((x0 + lean - 4, 342, x1 + lean + 4, 362), fill=255)   # knee
        d.ellipse((x0 + lean - 5, 396, x1 + lean + 6, 412), fill=255)  # foot
    # tail
    d.polygon([(124, 252), (110, 262), (100, 312), (108, 314), (122, 272)], fill=255)
    return m


def die_layers():
    """A white die with dark pips, tilted a little, in the lower right like a stamp."""
    box = (300, 300, 470, 470)
    outline = Image.new("L", (S, S), 0)
    ImageDraw.Draw(outline).rounded_rectangle((box[0] - 10, box[1] - 10, box[2] + 10, box[3] + 10), radius=40, fill=255)
    face = Image.new("L", (S, S), 0)
    ImageDraw.Draw(face).rounded_rectangle(box, radius=32, fill=255)
    pips = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(pips)
    cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
    off, r = 48, 17
    for dx, dy in ((-off, -off), (off, -off), (0, 0), (-off, off), (off, off)):
        d.ellipse((cx + dx - r, cy + dy - r, cx + dx + r, cy + dy + r), fill=255)
    tilt = lambda m: m.rotate(-12, resample=Image.BICUBIC, center=(cx, cy))
    return tilt(outline), tilt(face), tilt(pips)


def solid(color, mask):
    layer = Image.new("RGBA", (S, S), color)
    layer.putalpha(mask)
    return layer


img = Image.new("RGBA", (S, S), (0, 0, 0, 0))

# outer dark edge, gold ring, dark inner ring, brown inner field
img.alpha_composite(radial_disc(S, 252, (40, 26, 12), (20, 12, 6)))
img.alpha_composite(radial_disc(S, 244, (255, 222, 120), (170, 118, 36)))
img.alpha_composite(radial_disc(S, 222, (60, 38, 18), (30, 18, 8)))
img.alpha_composite(radial_disc(S, 214, (112, 72, 34), (46, 28, 12)))

# soft shadow, then the camel in parchment
cm = camel_mask()
shadow = cm.filter(ImageFilter.GaussianBlur(8))
img.alpha_composite(solid((0, 0, 0, 255), shadow.point(lambda v: int(v * 0.6))), (6, 8))
img.alpha_composite(solid((244, 224, 176, 255), cm))

# clip everything inside the inner field (keeps legs off the ring)
field = Image.new("L", (S, S), 0)
ImageDraw.Draw(field).ellipse((S / 2 - 214, S / 2 - 214, S / 2 + 214, S / 2 + 214), fill=255)
base = Image.new("RGBA", (S, S), (0, 0, 0, 0))
base.alpha_composite(radial_disc(S, 252, (40, 26, 12), (20, 12, 6)))
base.alpha_composite(radial_disc(S, 244, (255, 222, 120), (170, 118, 36)))
base.alpha_composite(radial_disc(S, 222, (60, 38, 18), (30, 18, 8)))
inner = img.copy()
inner.putalpha(field)
base.alpha_composite(inner)
img = base

# loot die with a dark outline, may overlap the ring like a stamp
outline, face, pips = die_layers()
img.alpha_composite(solid((0, 0, 0, 255), outline.filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * 0.7))), (5, 7))
img.alpha_composite(solid((20, 12, 6, 255), outline))
img.alpha_composite(solid((246, 242, 232, 255), face))
img.alpha_composite(solid((150, 20, 20, 255), pips))

os.makedirs(out_dir, exist_ok=True)
img.save(os.path.join(out_dir, "icon_512.png"))
img.resize((256, 256), Image.LANCZOS).save(os.path.join(out_dir, "preview_256.png"))
small = img.resize((64, 64), Image.LANCZOS)
small.save(os.path.join(out_dir, "preview_64.png"))
small.save(os.path.join(out_dir, "CamelusMovableRollFrame.tga"))
print("done")
