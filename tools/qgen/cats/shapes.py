from ..common import *
from .. import svgkit as K

META = {"id": "shapes", "name": "Shapes", "icon": "🔷"}
C8 = ["red", "blue", "yellow", "green", "orange", "purple", "pink", "brown"]
HEX = K.COLORS
BASIC = ["circle", "square", "triangle", "rectangle", "star", "heart", "oval", "diamond"]
PLURAL = {"circle": "circles", "square": "squares", "triangle": "triangles", "star": "stars", "heart": "hearts"}
SIDES = {"triangle": 3, "square": 4, "rectangle": 4, "diamond": 4, "kite": 4, "trapezoid": 4, "parallelogram": 4,
         "pentagon": 5, "hexagon": 6, "heptagon": 7, "octagon": 8, "nonagon": 9, "decagon": 10}
SYM = {"square": 4, "rectangle": 2, "triangle": 1, "pentagon": 5, "hexagon": 6, "octagon": 8, "heart": 1, "star": 5,
       "diamond": 2, "cross": 4, "crescent": 1, "arrow": 1, "kite": 1, "parallelogram": 0, "trapezoid": 1, "oval": 2}
NGON = {3: "triangle", 4: "quadrilateral", 5: "pentagon", 6: "hexagon", 7: "heptagon", 8: "octagon", 9: "nonagon", 10: "decagon", 11: "hendecagon", 12: "dodecagon"}
SOLIDS = {"cube": (6, 12, 8), "rectangular prism": (6, 12, 8), "triangular pyramid": (4, 6, 4), "square pyramid": (5, 8, 5),
          "triangular prism": (5, 9, 6), "pentagonal prism": (7, 15, 10), "hexagonal prism": (8, 18, 12),
          "octahedron": (8, 12, 6), "dodecahedron": (12, 30, 20), "icosahedron": (20, 30, 12)}
ANGLE_NAMES = ["acute", "right", "obtuse", "straight", "reflex"]


def col(c): return HEX[c]
def S(name, c): return K.shape(name, col(c))
def pl(s): return PLURAL.get(s, s + "s")


def build(band):
    r = rng_for("shapes", band)
    out = []
    if band == "2-5":
        for s in BASIC:
            for c in C8:
                out.append(mc(r, "What shape is this?", s, BASIC, v=svgv(S(s, c))))
                out.append(mc(r, f"Which one is the {c} {s}?", S(s, c), [S(o, c) for o in BASIC if o != s], ct="svg"))
                out.append(mc(r, f"Can you find the {s}?  It is {c}!", S(s, c), [S(o, c) for o in BASIC if o != s], ct="svg"))
                out.append(mc(r, "What color is this shape?", c, C8, v=svgv(S(s, c))))
        for s in PLURAL:
            for n in range(1, 6):
                for c in r.sample(C8, 3):
                    out.append(num_choices(r, f"How many {c} {pl(s) if n > 1 else s} can you count?", n, v=svgv(K.grid(n, s, col(c))), spread=2, lo=1))
    elif band == "6-10":
        for s, n in SIDES.items():
            for c in C8:
                out.append(num_choices(r, "How many sides does this shape have?", n, v=svgv(S(s, c)), spread=3, lo=0))
                out.append(num_choices(r, "How many corners does this shape have?", n, v=svgv(S(s, c)), spread=3, lo=0))
        for s in ["pentagon", "hexagon", "heptagon", "octagon", "trapezoid", "parallelogram", "kite", "crescent", "cross", "semicircle", "arrow", "nonagon", "decagon"]:
            for c in C8:
                out.append(mc(r, "What is the name of this shape?", s, [x for x in K.SHAPE_NAMES if x != s], v=svgv(S(s, c))))
        pool = list(K.SHAPE_NAMES)
        for n in range(3, 11):
            names = [s for s, k in SIDES.items() if k == n]
            for c in C8:
                right = r.choice(names) if names else None
                if not right: continue
                wrong = [S(s, c) for s, k in SIDES.items() if k != n]
                out.append(mc(r, f"Which shape has {n} sides?", S(right, c), wrong, ct="svg"))
        for a in pool:
            for b in pool:
                if a != b:
                    c = r.choice(C8)
                    out.append(mc(r, f"Which one is NOT a {a}?", S(b, c), [S(a, x) for x in r.sample(C8, 3)], ct="svg"))
    else:  # 11+
        for n, name in NGON.items():
            out.append(mc(r, f"What is a polygon with {n} sides called?", name, [v for k, v in NGON.items() if k != n]))
        for n in range(5, 11):
            for c in C8:
                out.append(mc(r, "What is the name of this regular polygon?", NGON[n], [v for k, v in NGON.items() if k != n], v=svgv(K.regular(n, col(c)))))
        for n in range(3, 31):
            ans = (n - 2) * 180
            label = f"{NGON[n]}" if n in NGON else f"{n}-sided polygon"
            out.append(mc(r, f"What is the sum of the interior angles of a {label}?", f"{ans}°", [f"{(n - 2 + d) * 180}°" for d in (-2, -1, 1, 2, 3) if n - 2 + d > 0]))
        for n in [3, 4, 5, 6, 8, 9, 10, 12, 15, 18, 20, 24, 30]:
            out.append(num_choices(r, f"What is each interior angle of a regular polygon with {n} sides?", (n - 2) * 180 // n, spread=30, lo=30, fmt=lambda x: f"{x}°"))
            out.append(num_choices(r, f"What is each exterior angle of a regular polygon with {n} sides?", 360 // n, spread=20, lo=5, fmt=lambda x: f"{x}°"))
        for n in range(4, 26):
            out.append(num_choices(r, f"How many diagonals does a polygon with {n} sides have?", n * (n - 3) // 2, spread=8, lo=1))
        for x in r.sample([x for x in range(5, 355) if x not in (90, 180)], 60):
            kind = "acute" if x < 90 else "obtuse" if x < 180 else "reflex"
            out.append(mc(r, f"What kind of angle measures {x}°?", kind, ANGLE_NAMES))
        for x in r.sample(range(5, 86), 25):
            out.append(num_choices(r, f"What is the complement of a {x}° angle?", 90 - x, spread=20, lo=1, fmt=lambda v: f"{v}°"))
        for x in r.sample(range(10, 171), 25):
            out.append(num_choices(r, f"What is the supplement of a {x}° angle?", 180 - x, spread=30, lo=1, fmt=lambda v: f"{v}°"))
        for _ in range(40):
            a, b = r.randint(20, 100), r.randint(20, 100)
            if a + b < 170:
                out.append(num_choices(r, f"Two angles of a triangle are {a}° and {b}°. What is the third?", 180 - a - b, spread=20, lo=1, fmt=lambda v: f"{v}°"))
        for _ in range(60):
            w, h = r.randint(2, 15), r.randint(2, 15)
            if w == h: continue
            out.append(num_choices(r, f"What is the area of a rectangle {w} by {h}?", w * h, spread=max(4, w * h // 4), lo=1))
            out.append(num_choices(r, f"What is the perimeter of a rectangle {w} by {h}?", 2 * (w + h), spread=6, lo=4))
        for _ in range(30):
            b, h = r.randint(2, 20), r.randint(2, 20)
            if b * h % 2 == 0:
                out.append(num_choices(r, f"What is the area of a triangle with base {b} and height {h}?", b * h // 2, spread=max(4, b * h // 6), lo=1))
        for rad in range(2, 13):
            out.append(num_choices(r, f"What is the area of a circle with radius {rad}? (use π)", rad * rad, spread=max(4, rad * 2), lo=1, fmt=lambda x: f"{x}π"))
            out.append(num_choices(r, f"What is the circumference of a circle with radius {rad}? (use π)", 2 * rad, spread=6, lo=1, fmt=lambda x: f"{x}π"))
        for a, b, c in [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25), (6, 8, 10), (9, 12, 15), (20, 21, 29), (9, 40, 41), (12, 16, 20), (15, 20, 25), (10, 24, 26), (12, 35, 37)]:
            out.append(num_choices(r, f"A right triangle has legs {a} and {b}. How long is the hypotenuse?", c, spread=6, lo=2))
        for name, (f, e, v) in SOLIDS.items():
            pool_n = lambda x: [str(y) for y in (x - 2, x - 1, x + 1, x + 2, x + 4) if y > 0]
            out.append(mc(r, f"How many faces does a {name} have?", str(f), pool_n(f)))
            out.append(mc(r, f"How many edges does a {name} have?", str(e), pool_n(e)))
            out.append(mc(r, f"How many vertices does a {name} have?", str(v), pool_n(v)))
        for s, k in SYM.items():
            for c in C8:
                out.append(num_choices(r, "How many lines of symmetry does this shape have?", k, v=svgv(S(s, c)), spread=2, lo=0))
    return out
