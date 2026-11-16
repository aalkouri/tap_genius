#!/usr/bin/env python3
"""Paints the empty centre panel out of the title artwork, for the screens that don't put a card over it.
usage: clean_bg.py <source 1024x572 art> <out.png>   (needs opencv-python-headless, numpy)"""
import sys, cv2, numpy as np
im = cv2.imread(sys.argv[1])[:546].astype(np.float32)          # drop the taskbar rows
H, W = im.shape[:2]
mask = np.zeros((H, W), np.uint8)
mask[206:340, 344:652] = 1                                      # panel, its top glow line and the hard-edged halos beside it
mask[340:432, 358:630] = 1                                      # lower half: stop short of the tent (left) and coaster (right)
src = im.copy()
keep = (src[..., 2] > 150) & (src[..., 1] > 140)                # bright firework sparks that overlap the edges stay
keep = cv2.dilate(keep.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
mask[keep & (np.indices((H, W))[0] < 232)] = 0
# 1) horizon strip (and the bottom glow line): carry the left-hand ground colours straight across, leaving the track alone
strip = np.zeros((H, W), bool); strip[432:449, 362:660] = True
strip &= ~(src[..., 2] > src[..., 0] * 0.8)                     # reddish = race-track kerb
strip &= ~((np.indices((H, W))[1] > 600) & (src[..., 0] < 70))  # dark track surface on the right
l = src[432:449, 352:360].mean(1)
rows = np.indices((H, W))[0]
im[strip] = l[np.clip(rows[strip] - 432, 0, 16)]
# 2) sky: harmonic fill (repeated blur with the surroundings held fixed), coarse to fine
def fill(img, m, it):
    out = img.copy(); m3 = m[..., None].astype(bool)
    for _ in range(it):
        out = np.where(m3, cv2.blur(out, (5, 5)), img)
    return out
small = cv2.resize(im, (W // 4, H // 4), interpolation=cv2.INTER_AREA); ms = cv2.resize(mask, (W // 4, H // 4), interpolation=cv2.INTER_NEAREST)
start = im.copy(); start[mask > 0] = cv2.resize(fill(small, ms, 600), (W, H), interpolation=cv2.INTER_CUBIC)[mask > 0]
out = fill(np.where(mask[..., None] > 0, start, im), mask, 250); out = np.where(mask[..., None] > 0, out, im)
# 3) a little life so the patch isn't flat: grain + a scatter of stars and sparkles like the rest of the sky
rng = np.random.default_rng(11)
out += (rng.normal(0, 1.1, (H, W, 1)) * (mask[..., None] > 0)).astype(np.float32)
out = np.clip(out, 0, 255).astype(np.uint8)
for _ in range(14):
    x, y = int(rng.integers(374, 624)), int(rng.integers(222, 424))
    col = [(255, 235, 215), (255, 220, 170), (235, 225, 255)][int(rng.integers(0, 3))]
    dot = np.zeros((H, W), np.float32); cv2.circle(dot, (x, y), 1, float(rng.uniform(.35, .8)), -1, cv2.LINE_AA)
    dot = cv2.GaussianBlur(dot, (0, 0), .6)[..., None]
    out = (out * (1 - dot) + np.array(col, np.float32) * dot).astype(np.uint8)
cv2.imwrite(sys.argv[2], out)
