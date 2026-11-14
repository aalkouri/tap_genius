"""Tiny SVG toolkit (viewBox 0 0 100 100, no width/height so CSS sizes it)."""
import math

COLORS = {  # name -> hex
    "red": "#E53935", "blue": "#1E88E5", "yellow": "#FDD835", "green": "#43A047", "orange": "#FB8C00",
    "purple": "#8E24AA", "pink": "#F06292", "brown": "#6D4C41", "black": "#212121", "white": "#FFFFFF", "gray": "#9E9E9E",
}
STROKE = 'stroke="#00000055" stroke-width="2" stroke-linejoin="round"'


def _wrap(body):
    return f'<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">{body}</svg>'


def poly(points, fill):
    return _wrap(f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in points)}" fill="{fill}" {STROKE}/>')


def regular(n, fill, r=44, rot=-90):
    return poly([(50 + r * math.cos(math.radians(rot + 360 * i / n)), 50 + r * math.sin(math.radians(rot + 360 * i / n))) for i in range(n)], fill)


def star(fill, points=5, ro=46, ri=19):
    pts = []
    for i in range(points * 2):
        rad = ro if i % 2 == 0 else ri
        a = math.radians(-90 + 180 * i / points)
        pts.append((50 + rad * math.cos(a), 50 + rad * math.sin(a)))
    return poly(pts, fill)


def shape(name, color="#1E88E5"):
    """name -> svg markup. See SHAPE_NAMES."""
    f = color
    if name == "circle":    return _wrap(f'<circle cx="50" cy="50" r="42" fill="{f}" {STROKE}/>')
    if name == "square":    return _wrap(f'<rect x="12" y="12" width="76" height="76" fill="{f}" {STROKE}/>')
    if name == "rectangle": return _wrap(f'<rect x="5" y="25" width="90" height="50" fill="{f}" {STROKE}/>')
    if name == "oval":      return _wrap(f'<ellipse cx="50" cy="50" rx="45" ry="29" fill="{f}" {STROKE}/>')
    if name == "triangle":  return poly([(50, 9), (93, 86), (7, 86)], f)
    if name == "diamond":   return poly([(50, 5), (90, 50), (50, 95), (10, 50)], f)
    if name == "kite":      return poly([(50, 5), (82, 38), (50, 95), (18, 38)], f)
    if name == "trapezoid": return poly([(27, 22), (73, 22), (95, 78), (5, 78)], f)
    if name == "parallelogram": return poly([(28, 25), (96, 25), (72, 75), (4, 75)], f)
    if name == "star":      return star(f)
    if name == "pentagon":  return regular(5, f)
    if name == "hexagon":   return regular(6, f, rot=0)
    if name == "heptagon":  return regular(7, f)
    if name == "octagon":   return regular(8, f, rot=-67.5)
    if name == "nonagon":   return regular(9, f)
    if name == "decagon":   return regular(10, f)
    if name == "heart":
        return _wrap(f'<path d="M50 90 C8 58 4 30 24 18 C38 10 50 20 50 30 C50 20 62 10 76 18 C96 30 92 58 50 90Z" fill="{f}" {STROKE}/>')
    if name == "crescent":
        return _wrap(f'<path d="M62 8 A42 42 0 1 0 62 92 A34 34 0 1 1 62 8Z" fill="{f}" {STROKE}/>')
    if name == "cross":
        return poly([(35, 8), (65, 8), (65, 35), (92, 35), (92, 65), (65, 65), (65, 92), (35, 92), (35, 65), (8, 65), (8, 35), (35, 35)], f)
    if name == "semicircle":
        return _wrap(f'<path d="M6 70 A44 44 0 0 1 94 70Z" fill="{f}" {STROKE}/>')
    if name == "arrow":
        return poly([(8, 38), (55, 38), (55, 14), (94, 50), (55, 86), (55, 62), (8, 62)], f)
    raise KeyError(name)


SHAPE_NAMES = ["circle", "square", "rectangle", "oval", "triangle", "diamond", "kite", "trapezoid", "parallelogram", "star",
               "pentagon", "hexagon", "heptagon", "octagon", "nonagon", "decagon", "heart", "crescent", "cross", "semicircle", "arrow"]


def swatch(hexcolor):
    return _wrap(f'<rect x="8" y="8" width="84" height="84" rx="14" fill="{hexcolor}" {STROKE}/>')


def grid(count, name="circle", color="#1E88E5", cols=None):
    """`count` small copies of a shape laid out in a grid - for counting questions (count <= 20)."""
    cols = cols or (5 if count > 12 else 4 if count > 6 else 3 if count > 4 else count)
    rows = -(-count // cols)
    cell = min(90 / cols, 90 / rows, 30)
    inner = shape(name, color).replace('<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">', "").replace("</svg>", "")
    out = []
    for i in range(count):
        cx = 50 + (i % cols - (cols - 1) / 2) * cell * 1.1
        cy = 50 + (i // cols - (rows - 1) / 2) * cell * 1.1
        s = cell * 0.9 / 100
        out.append(f'<g transform="translate({cx - 50 * s:.1f},{cy - 50 * s:.1f}) scale({s:.3f})">{inner}</g>')
    return _wrap("".join(out))
