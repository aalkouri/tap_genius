from ..common import *
from .. import svgkit as K

META = {"id": "colors", "name": "Colors", "icon": "🎨"}
HEX = dict(K.COLORS)
C10 = ["red", "blue", "yellow", "green", "orange", "purple", "pink", "brown", "black", "white"]
SH8 = ["circle", "square", "triangle", "star", "heart", "diamond", "oval", "rectangle"]
EMO = {
    "red": ["🍎", "🍓", "🍒", "🚒", "🌹", "🐞", "❤️", "🍅"],
    "orange": ["🍊", "🥕", "🎃", "🧡", "🏀"],
    "yellow": ["🍌", "🍋", "🌽", "🐥", "💛", "🌻", "⭐"],
    "green": ["🐸", "🥒", "🥦", "🌲", "🐢", "💚", "🍏", "🥬"],
    "blue": ["💙", "🐳", "🫐", "🔵"],
    "purple": ["🍇", "🍆", "💜", "🟣"],
    "pink": ["🐷", "🌸", "🦩", "🎀"],
    "brown": ["🐻", "🧸", "🥔", "🌰", "🍫", "🤎"],
    "black": ["🖤", "⚫", "🎱", "🕷️"],
    "white": ["🤍", "⚪", "☁️", "⛄"],
}
SHADES = {
    "red": ["#E53935", "#C62828", "#EF5350", "#B71C1C"], "orange": ["#FB8C00", "#EF6C00", "#FFA726", "#E65100"],
    "yellow": ["#FDD835", "#FBC02D", "#FFEE58", "#F9A825"], "blue": ["#1E88E5", "#1565C0", "#42A5F5", "#0D47A1"],
    "green": ["#43A047", "#2E7D32", "#66BB6A", "#1B5E20"], "purple": ["#8E24AA", "#6A1B9A", "#AB47BC", "#4A148C"],
}
RB = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]
RBHEX = dict(HEX, indigo="#4B0082", violet="#8F00FF", cyan="#00FFFF", magenta="#FF00FF")
ORD = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh"]


def sw(c): return K.swatch(HEX[c])


def pattern(seq):
    body = ""
    for i, h in enumerate(seq):
        cx, cy = 20 + (i % 3) * 30, 30 + (i // 3) * 40
        if h is None:
            body += f'<circle cx="{cx}" cy="{cy}" r="13" fill="#E0E0E0" {K.STROKE}/><text x="{cx}" y="{cy + 8}" font-size="22" font-weight="bold" text-anchor="middle" fill="#555">?</text>'
        else:
            body += f'<circle cx="{cx}" cy="{cy}" r="13" fill="{h}" {K.STROKE}/>'
    return K._wrap(body)


def mixsvg(h1, h2):
    return K._wrap(f'<circle cx="25" cy="50" r="20" fill="{h1}" {K.STROKE}/><text x="50" y="60" font-size="30" text-anchor="middle" fill="#555">+</text><circle cx="75" cy="50" r="20" fill="{h2}" {K.STROKE}/>')


def build(band):
    r = rng_for("colors", band)
    out = []
    if band == "2-5":
        for c in C10:
            for s in SH8:
                v = svgv(K.shape(s, HEX[c]))
                out.append(mc(r, "What color is this?", c, C10, v=v))
                out.append(mc(r, "Tap the same color!", sw(c), [sw(o) for o in C10 if o != c], v=v, ct="svg"))
            for t in ["Tap the {c} one.", "Find {c}!", "Which is {c}?", "Where is {c}?"]:
                out.append(mc(r, t.format(c=c), sw(c), [sw(o) for o in C10 if o != c], ct="svg"))
            for t in ["Which thing is {c}?", "Tap something {c}.", "Find a {c} thing!"]:
                ans = r.choice(EMO[c])
                out.append(mc(r, t.format(c=c), ans, [e for o in C10 if o != c for e in EMO[o]], ct="emoji"))
            for s in SH8:
                out.append(mc(r, f"Which {s} is {c}?", K.shape(s, HEX[c]), [K.shape(s, HEX[o]) for o in C10 if o != c], ct="svg"))
            for e in EMO[c]:
                out.append(mc(r, "What color is this?", sw(c), [sw(o) for o in C10 if o != c], v=emoji(e), ct="svg"))
                out.append(mc(r, "Pick the color name.", c, C10, v=emoji(e)))
        six = ["red", "blue", "yellow", "green", "orange", "purple"]
        for a in six:
            for b in six:
                if a != b:
                    out.append(mc(r, "What comes next?", sw(b), [sw(o) for o in C10 if o != b], v=svgv(pattern([HEX[a], HEX[b], HEX[a], HEX[b], HEX[a], None])), ct="svg"))
    elif band == "6-10":
        MIX = [("red", "yellow", "orange"), ("red", "blue", "purple"), ("blue", "yellow", "green"), ("red", "white", "pink"),
               ("black", "white", "gray"), ("blue", "white", "light blue"), ("red", "green", "brown")]
        RESULTS = ["orange", "purple", "green", "pink", "gray", "light blue", "brown", "yellow", "red", "blue", "black", "white"]
        for a, b, res in MIX:
            for x, y in ((a, b), (b, a)):
                v = svgv(mixsvg(HEX[x], HEX[y]))
                out.append(mc(r, f"Mix {x} and {y} paint. What color is made?", res, RESULTS, v=v))
                out.append(mc(r, f"{x} + {y} = ?", res, RESULTS, v=v))
                out.append(mc(r, f"What do you get if you mix {x} and {y}?", res, RESULTS))
            pairs = [f"{p} + {q}" for p, q, z in MIX if z != res]
            out.append(mc(r, f"Which two colors make {res}?", f"{a} + {b}", pairs))
            out.append(mc(r, f"To make {res} paint, which two colors do you mix?", f"{b} + {a}", pairs))
        for c in ["red", "blue", "yellow"]:
            for sh in SHADES[c]:
                out.append(mc(r, "Is this a primary or secondary color?", "Primary", ["Secondary", "Neutral", "Metallic"], v=svgv(K.swatch(sh))))
            out.append(mc(r, f"Is {c} a primary or secondary color?", "Primary", ["Secondary", "Neutral", "Metallic"]))
        for c in ["orange", "green", "purple"]:
            for sh in SHADES[c]:
                out.append(mc(r, "Is this a primary or secondary color?", "Secondary", ["Primary", "Neutral", "Metallic"], v=svgv(K.swatch(sh))))
            out.append(mc(r, f"Is {c} a primary or secondary color?", "Secondary", ["Primary", "Neutral", "Metallic"]))
        for c in ["black", "white", "gray"]:
            out.append(mc(r, f"In art, {c} is usually called what kind of color?", "Neutral", ["Primary", "Secondary", "Metallic"]))
        out.append(mc(r, "Which set has only primary colors?", "Red, yellow, blue", ["Red, green, orange", "Orange, green, purple", "Blue, green, pink"]))
        out.append(mc(r, "Which set has only secondary colors?", "Orange, green, purple", ["Red, yellow, blue", "Red, green, blue", "Pink, brown, red"]))
        out.append(mc(r, "How many primary colors are there in paint?", "3", ["2", "4", "5", "6", "7"]))
        out.append(mc(r, "How many secondary colors are there?", "3", ["2", "4", "5", "6", "7"]))
        for c in ["red", "orange", "yellow", "blue", "green"]:
            ans = "Warm" if c in ("red", "orange", "yellow") else "Cool"
            for sh in SHADES[c]:
                out.append(mc(r, "Is this a warm or cool color?", ans, ["Warm", "Cool", "Neutral", "Metallic"], v=svgv(K.swatch(sh))))
            out.append(mc(r, f"Is {c} a warm or cool color?", ans, ["Warm", "Cool", "Neutral", "Metallic"]))
        for w in ["red", "orange", "yellow"]:
            for cl in ["blue", "green"]:
                out.append(mc(r, f"Which is a warm color: {w} or {cl}?", w, [cl, "Both", "Neither"]))
                out.append(mc(r, f"Which is a warm color: {cl} or {w}?", w, [cl, "Both", "Neither"]))
                out.append(mc(r, f"Which is a cool color: {w} or {cl}?", cl, [w, "Both", "Neither"]))
                out.append(mc(r, f"Which is a cool color: {cl} or {w}?", cl, [w, "Both", "Neither"]))
        off = ["pink", "brown", "black", "white", "gray"]
        for i in range(6):
            a, b = RB[i], RB[i + 1]
            out.append(mc(r, f"In the rainbow, which color comes right after {a}?", b, [x for x in RB + off if x != b]))
            out.append(mc(r, f"In the rainbow, which color comes right before {b}?", a, [x for x in RB + off if x != a]))
            out.append(mc(r, f"What color comes after {a} in the rainbow?", b, [x for x in RB + off if x != b], v=emoji("🌈")))
            out.append(mc(r, f"Which color is just before {b} in the rainbow?", a, [x for x in RB + off if x != a], v=emoji("🌈")))
        for i in range(5):
            out.append(mc(r, f"Which rainbow color is between {RB[i]} and {RB[i + 2]}?", RB[i + 1], [x for x in RB + off if x != RB[i + 1]]))
        for i, o in enumerate(ORD):
            out.append(mc(r, f"Which color is {o} in the rainbow (red is first)?", RB[i], [x for x in RB + off if x != RB[i]]))
        for i in range(5):
            out.append(mc(r, f"Count two colors after {RB[i]} in the rainbow. Which color?", RB[i + 2], [x for x in RB + off if x != RB[i + 2]]))
        out.append(mc(r, "How many colors are in a rainbow?", "7", ["5", "6", "8", "9", "10"], v=emoji("🌈")))
        for ans in off:
            out.append(mc(r, "Which of these is NOT a rainbow color?", ans, RB))
        for x in off:
            out.append(mc(r, f"Is {x} one of the colors of the rainbow?", "No", ["Yes", "Only at night", "Only after snow"]))
        for x in RB:
            out.append(mc(r, f"Is {x} one of the colors of the rainbow?", "Yes", ["No", "Only at night", "Only after snow"]))
        OBJ = [("🍌", "banana", "yellow"), ("🍋", "lemon", "yellow"), ("🍓", "strawberry", "red"), ("🍒", "cherry", "red"), ("🫐", "blueberry", "blue"),
               ("🥕", "carrot", "orange"), ("🥦", "broccoli", "green"), ("🍅", "tomato", "red"), ("🎃", "pumpkin", "orange"),
               ("🐸", "frog", "green"), ("🌻", "sunflower", "yellow"), ("🚒", "fire truck", "red"), ("🐳", "whale", "blue"), ("🌲", "pine tree", "green"),
               ("🍆", "eggplant", "purple"), ("🐻", "teddy bear", "brown"), ("⛄", "snowman", "white"), ("🥒", "cucumber", "green"), ("🍇", "grapes", "purple")]
        CN = ["red", "orange", "yellow", "green", "blue", "purple", "pink", "brown", "black", "white"]
        for e, n, c in OBJ:
            art = "an" if n[0] in "aeiou" else "a"
            out.append(mc(r, f"What color is this {n}?", c, CN, v=emoji(e)))
            out.append(mc(r, f"What color is {art} {n}, usually?", c, CN))
        for q, a, w in [("What color is the sky on a clear day?", "blue", ["green", "pink", "brown"]), ("What color are most leaves in summer?", "green", ["blue", "pink", "purple"]),
                        ("What color is fresh snow?", "white", ["green", "brown", "blue"]), ("What color is coal?", "black", ["white", "yellow", "pink"]),
                        ("What color is the middle of a ripe watermelon?", "red", ["blue", "purple", "white"]), ("What color is the inside of a banana?", "white", ["blue", "purple", "green"]),
                        ("What color does a leaf turn in autumn? (one common color)", "orange", ["blue", "pink", "purple"]), ("What color is a polar bear's fur?", "white", ["brown", "black", "orange"]),
                        ("What color is a stop sign?", "red", ["green", "blue", "yellow"]), ("What color is a school bus in the USA?", "yellow", ["red", "blue", "green"])]:
            out.append(mc(r, q, a, w))
        for col, mean in [("red", "Stop"), ("green", "Go"), ("yellow", "Get ready to stop")]:
            out.append(mc(r, f"What does a {col} traffic light mean?", mean, ["Stop", "Go", "Get ready to stop", "Dance", "Turn off", "Fly"] ))
            out.append(mc(r, f"At a traffic light, {col} means...", mean, ["Stop", "Go", "Get ready to stop", "Dance", "Turn off", "Fly"], v=emoji("🚦")))
        for mean, col in [("Stop", "red"), ("Go", "green"), ("Be careful and slow down", "yellow")]:
            out.append(mc(r, f"Which traffic light color means \"{mean}\"?", col, ["red", "green", "yellow", "blue", "purple", "pink"], v=emoji("🚦")) if col != "yellow" else mc(r, "Which traffic light color tells you to slow down?", col, ["green", "blue", "purple", "pink"], v=emoji("🚦")))
        out.append(mc(r, "If someone is \"feeling blue\", how do they feel?", "Sad", ["Happy", "Hungry", "Cold"]))
        out.append(mc(r, "If someone is \"green with envy\", they feel...", "Jealous", ["Sick with a cold", "Very happy", "Sleepy"]))
        out.append(mc(r, "If you \"see red\", you are probably...", "Very angry", ["Very happy", "Sleepy", "Hungry"]))
        # patterns
        six = ["red", "blue", "yellow", "green", "orange", "purple", "pink", "brown"]
        for a in six:
            for b in six:
                if a == b: continue
                h = lambda x: HEX[x]
                out.append(mc(r, "What color comes next in the pattern?", sw(b), [sw(o) for o in six if o != b], v=svgv(pattern([h(a), h(b), h(a), h(b), h(a), None])), ct="svg"))
                out.append(mc(r, "Which color finishes the pattern?", sw(b), [sw(o) for o in six if o != b], v=svgv(pattern([h(a), h(a), h(b), h(a), h(a), None])), ct="svg"))
        for _ in range(80):
            a, b, c = r.sample(six, 3)
            out.append(mc(r, "Which color completes the pattern?", sw(c), [sw(o) for o in six if o != c], v=svgv(pattern([HEX[a], HEX[b], HEX[c], HEX[a], HEX[b], None])), ct="svg"))
    else:  # 11+
        RYB = [("red", "green"), ("blue", "orange"), ("yellow", "purple")]
        RYBN = ["red", "blue", "yellow", "orange", "green", "purple"]
        for p, q in RYB:
            for a, b in ((p, q), (q, p)):
                out.append(mc(r, f"On the traditional red-yellow-blue wheel, what is the complement of {a}?", b, [x for x in RYBN if x not in (a, b)]))
                out.append(mc(r, f"Which color sits directly opposite {a} on the red-yellow-blue color wheel?", b, [x for x in RYBN if x not in (a, b)]))
        RGBW = [("red", "cyan"), ("green", "magenta"), ("blue", "yellow")]
        RGBN = ["red", "green", "blue", "cyan", "magenta", "yellow"]
        for p, q in RGBW:
            for a, b in ((p, q), (q, p)):
                out.append(mc(r, f"On the RGB (light) color wheel, which color is opposite {a}?", b, [x for x in RGBN if x not in (a, b)]))
                out.append(mc(r, f"In RGB color theory, the complement of {a} is...", b, [x for x in RGBN if x not in (a, b)]))
        for a, b, res in [("red", "green", "yellow"), ("green", "blue", "cyan"), ("red", "blue", "magenta")]:
            for x, y in ((a, b), (b, a)):
                out.append(mc(r, f"On a screen, {x} light plus {y} light makes which color?", res, ["white", "black", "orange", "purple", "cyan", "magenta", "yellow", "gray"], v=svgv(mixsvg(RBHEX.get(x, HEX.get(x)), RBHEX.get(y, HEX.get(y))))))
        for a, b, res in [("cyan", "yellow", "green"), ("magenta", "yellow", "red"), ("cyan", "magenta", "blue")]:
            for x, y in ((a, b), (b, a)):
                out.append(mc(r, f"Mixing {x} and {y} ink (subtractive mixing) gives which color?", res, ["green", "red", "blue", "orange", "yellow", "white", "pink"], v=svgv(mixsvg(RBHEX[x] if x in RBHEX else HEX[x], RBHEX[y] if y in RBHEX else HEX[y]))))
        PURE = {"red": "#FF0000", "green": "#00FF00", "blue": "#0000FF", "yellow": "#FFFF00", "cyan": "#00FFFF", "magenta": "#FF00FF", "white": "#FFFFFF", "black": "#000000"}
        RGBV = {"red": (255, 0, 0), "green": (0, 255, 0), "blue": (0, 0, 255), "yellow": (255, 255, 0), "cyan": (0, 255, 255), "magenta": (255, 0, 255), "white": (255, 255, 255), "black": (0, 0, 0)}
        SHORT = {"red": "#F00", "green": "#0F0", "blue": "#00F", "yellow": "#FF0", "cyan": "#0FF", "magenta": "#F0F", "white": "#FFF", "black": "#000"}
        for n, h in PURE.items():
            others = [x for k, x in PURE.items() if k != n]
            names = [k for k in PURE if k != n]
            out.append(mc(r, "Which hex code produces exactly this color?", h, others, v=svgv(K.swatch(h))))
            out.append(mc(r, f"What is the hex code for pure {n} (full-intensity RGB)?", h, others))
            out.append(mc(r, f"Which color is the hex code {h}?", n, names))
            out.append(mc(r, f"Which color does rgb{RGBV[n]} display?", n, names, v=svgv(K.swatch(h))))
            out.append(mc(r, f"What color is the shorthand hex code {SHORT[n]}?", n, names))
            out.append(mc(r, f"Which RGB triple gives {n}?", str(RGBV[n]), [str(x) for k, x in RGBV.items() if k != n]))
        out.append(mc(r, "Which hex code is a mid-gray?", "#808080", ["#FF8000", "#800000", "#008080", "#FF0080"], v=svgv(K.swatch("#808080"))))
        out.append(mc(r, "Which hex code gives orange (255, 165, 0)?", "#FFA500", ["#00A5FF", "#A5FF00", "#FF00A5", "#FFFA05"], v=svgv(K.swatch("#FFA500"))))
        for _ in range(40):
            n = r.randint(17, 254)
            h = f"{n:02X}"
            out.append(num_choices(r, f"What is the hexadecimal value {h} in decimal?", n, spread=20, lo=1))
        for _ in range(30):
            n = r.randint(17, 254)
            alts = {f"{max(0, n + d):02X}" for d in (-17, -16, -1, 1, 15, 16, 17, 32)}
            alts.discard(f"{n:02X}")
            out.append(mc(r, f"What is {n} written as a two-digit hex number?", f"{n:02X}", sorted(alts)))
        for k, v in [("A", 10), ("B", 11), ("C", 12), ("D", 13), ("E", 14), ("F", 15)]:
            out.append(num_choices(r, f"In hexadecimal, what decimal value does the digit {k} stand for?", v, spread=4, lo=1))
        S6 = ["red", "orange", "yellow", "green", "blue", "violet"]
        for i, a in enumerate(S6):
            for j, b in enumerate(S6):
                if i == j: continue
                longer = a if i < j else b
                higher = a if i > j else b
                out.append(mc(r, f"Which has the longer wavelength: {a} light or {b} light?", longer, [b if longer == a else a, "They are identical", "It depends on the brightness"]))
                out.append(mc(r, f"Which visible light has the higher frequency: {a} or {b}?", higher, [b if higher == a else a, "They are identical", "It depends on the brightness"]))
                out.append(mc(r, f"Photons of which light carry more energy: {a} or {b}?", higher, [b if higher == a else a, "They carry equal energy", "It depends on the brightness"]))
        FACTS = [
            ("What do the letters in CMYK stand for?", "Cyan, Magenta, Yellow, Key (black)", ["Cyan, Maroon, Yellow, Khaki", "Crimson, Magenta, Yellow, Kelly", "Cyan, Magenta, Yellow, Kiwi"]),
            ("In CMYK, what does the K stand for?", "Key (black)", ["Khaki", "Kelvin", "Kilo"]),
            ("Which color model do computer screens use to make colors?", "RGB", ["CMYK", "RYB", "Pantone"]),
            ("Which color model do most color printers use?", "CMYK", ["RGB", "Hexadecimal", "Grayscale only"]),
            ("What do the letters in RGB stand for?", "Red, Green, Blue", ["Red, Gold, Brown", "Rose, Green, Black", "Red, Gray, Blue"]),
            ("Which kind of color mixing starts with black (no light) and gets lighter as lights are added?", "Additive mixing", ["Subtractive mixing", "Pigment mixing", "Complementary mixing"]),
            ("Mixing paints or inks, which tends to get darker the more you mix, is called...", "Subtractive mixing", ["Additive mixing", "Spectral mixing", "Digital mixing"]),
            ("What color do you get by adding red, green and blue light at full strength?", "White", ["Black", "Gray", "Brown"]),
            ("What is the approximate wavelength range of visible light?", "400-700 nanometres", ["100-300 nanometres", "700-1100 nanometres", "1-10 millimetres"]),
            ("Which color of visible light has the longest wavelength?", "Red", ["Violet", "Green", "Blue"]),
            ("Which color of visible light has the shortest wavelength?", "Violet", ["Red", "Green", "Yellow"]),
            ("Which scientist used a prism to show that white light is made of a spectrum of colors?", "Isaac Newton", ["Galileo Galilei", "Charles Darwin", "Thomas Edison"]),
            ("How many colors did Isaac Newton name in the rainbow spectrum?", "7", ["5", "6", "8"]),
            ("In color theory, which word describes the purity or intensity of a color?", "Saturation", ["Hue", "Tint", "Value"]),
            ("In color theory, what is the name for the pure color family, like red or blue?", "Hue", ["Saturation", "Tint", "Shade"]),
            ("In color theory, what does \"value\" describe?", "How light or dark a color is", ["How warm a color is", "How pure a color is", "How many colors are used"]),
            ("What do you get when you add white to a pure hue?", "A tint", ["A shade", "A complement", "A primary"]),
            ("What do you get when you add black to a pure hue?", "A shade", ["A tint", "A complement", "A secondary"]),
            ("What do you get when you add gray to a pure hue?", "A tone", ["A tint", "A shade", "A triad"]),
            ("Colors that sit next to each other on the color wheel are called...", "Analogous", ["Complementary", "Triadic", "Monochromatic"]),
            ("Colors directly opposite each other on the color wheel are called...", "Complementary", ["Analogous", "Triadic", "Monochromatic"]),
            ("A color scheme using several tints and shades of one hue is called...", "Monochromatic", ["Analogous", "Complementary", "Triadic"]),
            ("A color scheme using three hues evenly spaced around the wheel is called...", "Triadic", ["Analogous", "Monochromatic", "Complementary"]),
            ("How many tertiary colors are on a standard 12-color wheel?", "6", ["3", "9", "12"]),
            ("A tertiary color is made by mixing...", "A primary and a neighboring secondary", ["Two primaries", "Two secondaries", "Black and white"]),
            ("Which of these is a tertiary color?", "Yellow-green", ["Orange", "Purple", "Red"]),
            ("On the red-yellow-blue wheel, which of these is a tertiary color?", "Red-orange", ["Green", "Yellow", "Blue"]),
            ("Why do plant leaves look green?", "Chlorophyll reflects green light", ["Chlorophyll reflects red light", "Leaves glow green", "Leaves absorb only green light"]),
            ("Why is the sky blue in the daytime?", "Air scatters short blue wavelengths the most", ["The ocean reflects onto the sky", "Clouds absorb red light", "The sun only gives off blue light"]),
            ("A red apple looks red because it mostly...", "Reflects red light", ["Absorbs red light", "Gives off red light", "Reflects blue light"]),
            ("A pure blue object lit only by pure red light looks...", "Very dark or black", ["Bright blue", "Purple", "Bright red"]),
            ("Which color of star is the hottest?", "Blue-white", ["Red", "Orange", "Yellow"]),
            ("Which color of star is the coolest?", "Red", ["Blue-white", "White", "Yellow"]),
            ("What is the most common type of color blindness?", "Red-green", ["Blue-yellow", "Total color blindness", "Black-white"]),
            ("Which cells in the human eye let us see color?", "Cones", ["Rods", "Lenses", "Corneas"]),
            ("Which cells in the human eye work best in dim light?", "Rods", ["Cones", "Pupils", "Irises"]),
            ("How many types of cone cells do most people have?", "3", ["1", "2", "5"]),
            ("Why is magenta missing from the rainbow?", "It is not a single wavelength of light", ["It is too bright to see", "It is invisible to everyone", "It only exists in paint"]),
            ("Placed side by side, complementary colors create...", "Strong contrast", ["A blended gradient", "A neutral gray", "No difference at all"]),
            ("How many different colors can 24-bit RGB (8 bits per channel) display?", "16,777,216", ["65,536", "256", "4,294,967,296"]),
            ("In 8-bit RGB, what is the maximum value of one channel?", "255", ["100", "256", "999"]),
            ("How many values (0 to 255) can one 8-bit RGB channel take?", "256", ["255", "100", "512"]),
            ("What does rgb(0, 0, 0) display?", "Black", ["White", "Gray", "Transparent"]),
            ("What does rgb(255, 255, 255) display?", "White", ["Black", "Gray", "Transparent"]),
            ("Hexadecimal is a number system with what base?", "16", ["8", "10", "12"]),
            ("Which characters make up hex color digits?", "0-9 and A-F", ["0-9 and A-Z", "0-7 and A-F", "A-Z only"]),
            ("In HSL, what does the L stand for?", "Lightness", ["Length", "Latitude", "Layer"]),
            ("In HSL, what does the S stand for?", "Saturation", ["Shade", "Spectrum", "Sharpness"]),
            ("In HSL, hue is measured in degrees around a circle. How many degrees is a full circle?", "360", ["180", "255", "100"]),
            ("In HSL, which hue angle is pure red?", "0 degrees", ["60 degrees", "120 degrees", "240 degrees"]),
            ("In HSL, which hue angle is pure yellow?", "60 degrees", ["0 degrees", "120 degrees", "240 degrees"]),
            ("In HSL, which hue angle is pure green?", "120 degrees", ["0 degrees", "60 degrees", "240 degrees"]),
            ("In HSL, which hue angle is pure cyan?", "180 degrees", ["0 degrees", "120 degrees", "300 degrees"]),
            ("In HSL, which hue angle is pure blue?", "240 degrees", ["0 degrees", "120 degrees", "60 degrees"]),
            ("In HSL, which hue angle is pure magenta?", "300 degrees", ["0 degrees", "60 degrees", "180 degrees"]),
            ("Which color has the highest frequency in the visible spectrum?", "Violet", ["Red", "Green", "Yellow"]),
            ("Beyond the red end of the visible spectrum lies which radiation?", "Infrared", ["Ultraviolet", "X-rays", "Gamma rays"]),
            ("Beyond the violet end of the visible spectrum lies which radiation?", "Ultraviolet", ["Infrared", "Microwaves", "Radio waves"]),
            ("What color do the primary colors of light (RGB) make when overlapped at full strength?", "White", ["Black", "Brown", "Gray"]),
            ("Which gives carrots their orange color?", "Beta-carotene", ["Chlorophyll", "Lycopene", "Anthocyanin"]),
            ("Which pigment makes tomatoes red?", "Lycopene", ["Chlorophyll", "Beta-carotene", "Melanin"]),
            ("Which pigment in skin and hair gives them brown and black color?", "Melanin", ["Lycopene", "Chlorophyll", "Keratin"]),
            ("Which pigment lets plants absorb sunlight for photosynthesis?", "Chlorophyll", ["Melanin", "Lycopene", "Hemoglobin"]),
            ("Which pigment makes human blood red?", "Hemoglobin", ["Chlorophyll", "Melanin", "Carotene"]),
        ]
        for q, a, w in FACTS:
            out.append(mc(r, q, a, w))
        # HSL hue naming from angle
        HUES = [(0, "red"), (60, "yellow"), (120, "green"), (180, "cyan"), (240, "blue"), (300, "magenta")]
        for ang, n in HUES:
            out.append(mc(r, f"An HSL color with hue {ang}° at full saturation and 50% lightness is which color?", n, [x for _, x in HUES if x != n], v=svgv(K.swatch(PURE[n]))))
    return out
