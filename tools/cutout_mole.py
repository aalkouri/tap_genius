#!/usr/bin/env python3
"""Cuts the head out of a portrait photo for the whack-a-mole game -> public/img/mole.png
Usage: python3 tools/cutout_mole.py photo.jpg   (needs opencv-python-headless, numpy)
The numbers below (head box, face ellipse, chin line) are in the photo resized to 750x1000."""
import sys, os
import cv2, numpy as np

src = cv2.imread(sys.argv[1])
im = cv2.resize(src, (750, 1000), interpolation=cv2.INTER_AREA)
h, w = im.shape[:2]
RECT = (268, 176, 356, 290)          # x, y, w, h around hair + face
FACE = ((455, 362), (90, 92))        # centre, radii: certainly head
CHIN_Y = 458                         # everything below is neck / dress

mask = np.full((h, w), cv2.GC_BGD, np.uint8)
x, y, rw, rh = RECT
mask[y:y + rh, x:x + rw] = cv2.GC_PR_FGD
cv2.ellipse(mask, FACE[0], FACE[1], 0, 0, 360, cv2.GC_FGD, -1)
# hair on top of the head is certainly foreground too
cv2.ellipse(mask, (455, 268), (105, 55), 0, 180, 360, cv2.GC_FGD, -1)
mask[CHIN_Y:, :] = cv2.GC_BGD
bgd, fgd = np.zeros((1, 65)), np.zeros((1, 65))
cv2.grabCut(im, mask, None, bgd, fgd, 6, cv2.GC_INIT_WITH_MASK)
a = np.where((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
n, lab, stats, _ = cv2.connectedComponentsWithStats(a)
a = np.where(lab == 1 + stats[1:, cv2.CC_STAT_AREA].argmax(), 255, 0).astype(np.uint8)   # biggest blob only
a = cv2.morphologyEx(a, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
a = cv2.GaussianBlur(a, (0, 0), 1.6)
# round off the chin cut so it does not end in a hard straight line
rows = np.arange(h, dtype=np.float32)[:, None]
a = (a * np.clip((CHIN_Y - rows) / 10.0, 0, 1)).astype(np.uint8)
rgba = cv2.cvtColor(im, cv2.COLOR_BGR2BGRA); rgba[..., 3] = a
ys, xs = np.where(a > 100)
rgba = rgba[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
s = max(rgba.shape[:2]) + 12
can = np.zeros((s, s, 4), np.uint8)
oy, ox = (s - rgba.shape[0]) // 2, (s - rgba.shape[1]) // 2
can[oy:oy + rgba.shape[0], ox:ox + rgba.shape[1]] = rgba
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "public", "img", "mole.png")
cv2.imwrite(out, cv2.resize(can, (320, 320), interpolation=cv2.INTER_AREA))
print("wrote", os.path.normpath(out))
