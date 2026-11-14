#!/usr/bin/env python3
"""Cuts the 9-panel 'altered princess' strip into transparent PNGs: public/img/disney/altered-01..09.png
Usage: python3 tools/cutout_altered.py path/to/strip.jpg"""
import sys, collections, os
from PIL import Image, ImageFilter

SRC = sys.argv[1]
OUT = os.path.join(os.path.dirname(__file__), "..", "public", "img", "disney")
BOUNDS = [0, 165, 293, 407, 512, 621, 736, 842, 935, 1024]   # stripe edges in the 1024x434 source
TOL = 34

def dist(a, b): return max(abs(i - j) for i, j in zip(a, b))

im = Image.open(SRC).convert("RGB")
W, H = im.size
os.makedirs(OUT, exist_ok=True)
for i in range(9):
    x0, x1 = BOUNDS[i] + (0 if i == 0 else 3), BOUNDS[i + 1] - (0 if i == 8 else 3)
    p = im.crop((x0, 0, x1, H)); w, h = p.size
    px = p.load()
    edge = [px[x, 2] for x in range(w)] + [px[1, y] for y in range(h)] + [px[w - 2, y] for y in range(h)]
    bg = tuple(c + 4 for c in collections.Counter(tuple(c // 8 * 8 for c in e) for e in edge).most_common(1)[0][0])
    if i == 2:   # figure 2's green/gold hem spills into this stripe (bottom-left): paint it as background
        for y in range(330, h):
            for x in range(0, 60):
                r, g, b = px[x, y]
                if g > b + 10: px[x, y] = bg
    seen = bytearray(w * h); stack = [(x, y) for x in range(w) for y in (0, h - 1)] + [(x, y) for y in range(h) for x in (0, w - 1)]
    mask = Image.new("L", (w, h), 255); mp = mask.load()
    while stack:
        x, y = stack.pop()
        if x < 0 or y < 0 or x >= w or y >= h or seen[y * w + x]: continue
        seen[y * w + x] = 1
        if dist(px[x, y], bg) <= TOL:
            mp[x, y] = 0; stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    mask = mask.filter(ImageFilter.MedianFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
    rgba = p.convert("RGBA"); rgba.putalpha(mask)
    rgba = rgba.crop(mask.point(lambda v: 255 if v > 128 else 0).getbbox())
    s = max(rgba.size) + 16
    can = Image.new("RGBA", (s, s), (0, 0, 0, 0)); can.paste(rgba, ((s - rgba.width) // 2, (s - rgba.height) // 2), rgba)
    can.resize((420, 420), Image.LANCZOS).save(os.path.join(OUT, f"altered-{i + 1:02d}.png"), optimize=True)
print("done")
