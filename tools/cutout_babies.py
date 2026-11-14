#!/usr/bin/env python3
"""Cuts the 'baby princesses' row photo into transparent PNGs: public/img/disney/<slug>.png
Each baby is marked with seed points (source-pixel coordinates); a watershed on the colour image splits touching
characters along their drawn outlines, and the pastel backdrop is removed.
Usage: python3 tools/cutout_babies.py path/to/photo.jpg [debug_overlay.png]   (needs opencv-python-headless, numpy)"""
import sys, os
import cv2, numpy as np

SRC = sys.argv[1]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "public", "img", "disney")
X0, Y0, X1, Y1 = 50, 300, 750, 560
K = 3
SEEDS = {   # slug -> seed points (x, y) in the source photo
    "snow-white": [(80, 385), (118, 392), (140, 332), (125, 450), (108, 482), (82, 520), (70, 440), (152, 385)],
    "ariel":      [(178, 338), (190, 365), (245, 372), (216, 402), (190, 440), (180, 500), (135, 512), (228, 452)],
    "cinderella": [(272, 342), (322, 335), (298, 402), (298, 452), (290, 500), (330, 515), (342, 446)],
    "tiana":      [(390, 322), (366, 380), (396, 402), (402, 470), (406, 440), (430, 520), (385, 520)],
    "jasmine":    [(455, 382), (522, 360), (487, 342), (496, 402), (500, 452), (512, 490), (570, 522)],
    "aurora":     [(548, 382), (600, 352), (602, 336), (566, 407), (575, 470), (606, 452), (596, 530)],
    "belle":      [(640, 358), (697, 346), (672, 402), (652, 490), (712, 440), (728, 372), (642, 333)],
}
SLUGS = list(SEEDS)
# the lower bodies overlap and have white clothing that blends with the backdrop, so each cut-out is a
# head-and-shoulders portrait that fades out at this source-pixel row
BUST_Y = {"snow-white": 448, "ariel": 462, "cinderella": 462, "tiana": 458, "jasmine": 462, "aurora": 478, "belle": 470}
FADE = 16

src = cv2.imread(SRC)[Y0:Y1, X0:X1]
up = cv2.resize(src, None, fx=K, fy=K, interpolation=cv2.INTER_CUBIC)
h, w = up.shape[:2]
hsv = cv2.cvtColor(up, cv2.COLOR_BGR2HSV)
light = ((hsv[..., 1] < 45) & (hsv[..., 2] > 205)).astype(np.uint8)
# backdrop = light pixels connected to the image border
bg = np.zeros((h, w), np.uint8)
for (sx, sy) in [(x, y) for x in range(0, w, 8) for y in (0, h - 1)] + [(x, y) for y in range(0, h, 8) for x in (0, w - 1)]:
    if light[sy, sx] and not bg[sy, sx]:
        t = light.copy(); cv2.floodFill(t, np.zeros((h + 2, w + 2), np.uint8), (sx, sy), 2); bg |= (t == 2).astype(np.uint8)
fg = (bg == 0).astype(np.uint8)
fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))

markers = np.zeros((h, w), np.int32)
markers[cv2.erode(bg, np.ones((7, 7), np.uint8)) == 1] = 100       # sure background
for i, slug in enumerate(SLUGS, 1):
    for (x, y) in SEEDS[slug]:
        cv2.circle(markers, ((x - X0) * K, (y - Y0) * K), 7 * K // 2, i, -1)
smooth = cv2.bilateralFilter(up, 7, 40, 7)
ws = cv2.watershed(smooth, markers.copy())

os.makedirs(OUT, exist_ok=True)
for i, slug in enumerate(SLUGS, 1):
    m = ((ws == i) & (fg == 1)).astype(np.uint8) * 255
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m)
    big = stats[1:, cv2.CC_STAT_AREA].max()
    keep = np.zeros_like(m)
    for j in range(1, n):
        if stats[j, cv2.CC_STAT_AREA] >= 0.02 * big: keep[lab == j] = 255
    keep = cv2.morphologyEx(keep, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    # drop big near-white blobs left inside the shape (backdrop trapped between hair and body)
    pale = (((hsv[..., 1] < 28) & (hsv[..., 2] > 222)) & (keep > 0)).astype(np.uint8)
    pn, plab, pst, _ = cv2.connectedComponentsWithStats(pale)
    for j in range(1, pn):
        if pst[j, cv2.CC_STAT_AREA] > 700: keep[cv2.dilate((plab == j).astype(np.uint8), np.ones((3, 3), np.uint8)) == 1] = 0
    keep = cv2.GaussianBlur(keep, (0, 0), 1.5)
    rows = np.arange(h, dtype=np.float32)[:, None]
    keep = (keep * np.clip(((BUST_Y[slug] - Y0) * K - rows) / (FADE * K), 0, 1)).astype(np.uint8)
    rgba = cv2.cvtColor(up, cv2.COLOR_BGR2BGRA); rgba[..., 3] = keep
    ys, xs = np.where(keep > 128)
    rgba = rgba[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    s = max(rgba.shape[:2]) + 24
    can = np.zeros((s, s, 4), np.uint8)
    oy, ox = (s - rgba.shape[0]) // 2, (s - rgba.shape[1]) // 2
    can[oy:oy + rgba.shape[0], ox:ox + rgba.shape[1]] = rgba
    cv2.imwrite(os.path.join(OUT, f"{slug}.png"), cv2.resize(can, (420, 420), interpolation=cv2.INTER_AREA))
    print(slug, "ok")

if len(sys.argv) > 2:   # debug: seeds + region borders on the photo
    dbg = up.copy(); dbg[ws == -1] = (0, 0, 255)
    for i, slug in enumerate(SLUGS, 1):
        for (x, y) in SEEDS[slug]: cv2.circle(dbg, ((x - X0) * K, (y - Y0) * K), 8, (255, 0, 0), -1)
    cv2.imwrite(sys.argv[2], dbg)
