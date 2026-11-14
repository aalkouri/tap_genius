import math, re
from fractions import Fraction
from decimal import Decimal
from ..common import *
from .. import svgkit as K

META = {"id": "numbers", "name": "Numbers", "icon": "🔢"}
HEX = K.COLORS
KEYCAP = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
NAMES = ["Mia", "Leo", "Ava", "Sam", "Zoe", "Max", "Ella", "Ben", "Lily", "Tom", "Nora", "Jack", "Ruby", "Finn"]
THINGS = ["stickers", "marbles", "cards", "coins", "apples", "pencils", "books", "toy cars", "shells", "balloons"]
SUP = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")


def sup(n): return str(n).translate(SUP)
def pl(s): return {"circle": "circles", "star": "stars", "heart": "hearts", "square": "squares", "triangle": "triangles"}[s]


def ordinal(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def to_roman(n):
    out = ""
    for v, s in [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]:
        while n >= v:
            out += s; n -= v
    return out


def fr(x):
    x = Fraction(x)
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def dec(d):
    s = format(Decimal(d), "f")
    if "." in s: s = s.rstrip("0").rstrip(".")
    return s


def frac_mc(r, q, ans, extras, v=None, fb=True):
    ans = Fraction(ans)
    cands, seen = [], {ans}

    def add(lst):
        for e in lst:
            e = Fraction(e)
            if e > 0 and e not in seen:
                seen.add(e); cands.append(fr(e))
    add(extras)
    if fb and len(cands) < 3:
        add([ans + Fraction(1, d) for d in (2, 3, 4, 5, 6, 8, 10, 12)] + [ans - Fraction(1, d) for d in (3, 5, 7, 9, 11)])
    return mc(r, q, fr(ans), cands, v=v)


def pie(n, k, color="#1E88E5"):
    body = ""
    for i in range(n):
        a0, a1 = math.radians(-90 + 360 * i / n), math.radians(-90 + 360 * (i + 1) / n)
        x0, y0, x1, y1 = 50 + 44 * math.cos(a0), 50 + 44 * math.sin(a0), 50 + 44 * math.cos(a1), 50 + 44 * math.sin(a1)
        fill = color if i < k else "#FFFFFF"
        body += f'<path d="M50 50 L{x0:.1f} {y0:.1f} A44 44 0 0 1 {x1:.1f} {y1:.1f}Z" fill="{fill}" stroke="#555" stroke-width="2" stroke-linejoin="round"/>'
    return K._wrap(body)


def divisors(n): return [d for d in range(1, n + 1) if n % d == 0]
def is_prime(n): return n > 1 and all(n % d for d in range(2, int(n ** 0.5) + 1))


def factorization(n):
    out, d = {}, 2
    while n > 1:
        while n % d == 0:
            out[d] = out.get(d, 0) + 1; n //= d
        d += 1
    return out


def fstr(f):
    return " × ".join(f"{p}{sup(e)}" if e > 1 else str(p) for p, e in sorted(f.items()))


def ltr(expr):
    toks = re.findall(r"\d+|[+\-×÷]", expr.replace("(", "").replace(")", ""))
    v = int(toks[0])
    for i in range(1, len(toks), 2):
        op, n = toks[i], int(toks[i + 1])
        v = v + n if op == "+" else v - n if op == "-" else v * n if op == "×" else Fraction(v, n)
    return v


def evalx(expr):
    e = re.sub(r"(\d+)²", r"(\1**2)", expr).replace("×", "*").replace("÷", "/")
    return Fraction(eval(re.sub(r"(\d+)", r"Fraction(\1)", e), {"Fraction": Fraction}))


def build(band):
    r = rng_for("numbers", band)
    out = []
    if band == "2-5":
        EM = ["🍎", "🍌", "🍓", "🐶", "🐱", "⭐", "🎈", "🚗", "🐟", "🌸", "🍪", "⚽"]
        SHP = ["circle", "star", "heart", "square", "triangle"]
        COL = ["red", "blue", "yellow", "green", "orange", "purple"]
        for e in EM:
            for n in range(1, 11):
                out.append(num_choices(r, "How many do you see?", n, v=emoji(e * n), spread=2, lo=1))
        for s in SHP:
            for n in range(1, 11):
                for c in r.sample(COL, 3):
                    out.append(num_choices(r, f"How many {pl(s) if n > 1 else s} are there?", n, v=svgv(K.grid(n, s, HEX[c])), spread=2, lo=1))
            for n in range(1, 9):
                for c in r.sample(COL, 2):
                    out.append(mc(r, f"Which has {n} {c} {pl(s) if n > 1 else s}?", K.grid(n, s, HEX[c]), [K.grid(m, s, HEX[c]) for m in range(1, 11) if m != n], ct="svg"))
        for e in EM:
            for kind in ["more", "most", "fewer", "least"]:
                ns = r.sample(range(1, 9), 4)
                right = max(ns) if kind in ("more", "most") else min(ns)
                q = {"more": "Which has more?", "most": "Which has the most?", "fewer": "Which has fewer?", "least": "Which has the least?"}[kind]
                out.append(mc(r, q, e * right, [e * n for n in ns], v=emoji(e), ct="emoji"))
        for n in range(1, 11):
            for t in ["Tap the number {n}.", "Find the number {n}!", "Which one is {n}?"]:
                out.append(mc(r, t.format(n=n), str(n), [str(m) for m in range(1, 11)]))
            out.append(mc(r, "Which number is this?", str(n), [str(m) for m in range(1, 11)], v=emoji(KEYCAP[n])))
            out.append(mc(r, f"Which one shows {n}?", K.grid(n, "circle", HEX["blue"]), [K.grid(m, "circle", HEX["blue"]) for m in range(1, 11) if m != n], ct="svg"))
            out.append(mc(r, f"Which one has {n} dots?", K.grid(n, "circle", HEX["red"]), [K.grid(m, "circle", HEX["red"]) for m in range(1, 11) if m != n], ct="svg"))
        for n in range(1, 10):
            out.append(num_choices(r, f"What comes after {n}?", n + 1, spread=2, lo=1))
            out.append(num_choices(r, f"What number is just after {n}?", n + 1, v=emoji(KEYCAP[n]), spread=2, lo=1))
        for n in range(2, 11):
            out.append(num_choices(r, f"What comes before {n}?", n - 1, spread=2, lo=0))
            out.append(num_choices(r, f"What number is just before {n}?", n - 1, v=emoji(KEYCAP[n]), spread=2, lo=0))
        for s in range(1, 8):
            out.append(num_choices(r, "What comes next?", s + 3, v=emoji(f"{KEYCAP[s]} {KEYCAP[s + 1]} {KEYCAP[s + 2]} ❓"), spread=2, lo=1))
        for s in range(1, 9):
            out.append(num_choices(r, "What is missing?", s + 1, v=emoji(f"{KEYCAP[s]} ❓ {KEYCAP[s + 2] if s + 2 <= 10 else ''}"), spread=2, lo=1))
        for e in EM:
            for a in range(1, 6):
                for b in range(1, 6):
                    if a + b <= 8 and r.random() < 0.5:
                        out.append(num_choices(r, "How many in all?", a + b, v=emoji(f"{e * a}➕{e * b}"), spread=2, lo=1))
            for a in range(3, 9):
                b = r.randint(1, a - 1)
                out.append(num_choices(r, f"Take away {b}. How many left?", a - b, v=emoji(e * a), spread=2, lo=0))
        for q, a in [("How many eyes do you have?", 2), ("How many hands do you have?", 2), ("How many noses do you have?", 1), ("How many fingers on one hand?", 5),
                     ("How many wheels on a bike?", 2), ("How many legs does a dog have?", 4), ("How many ears does a cat have?", 2), ("How many wheels on a car?", 4),
                     ("How many days in a weekend?", 2), ("How many legs do you have?", 2)]:
            out.append(num_choices(r, q, a, spread=2, lo=1))
    elif band == "6-10":
        # arithmetic
        for _ in range(120):
            a, b = r.randint(11, 99), r.randint(11, 99)
            out.append(num_choices(r, f"{a} + {b} = ?", a + b, spread=12, lo=1))
        for _ in range(120):
            a, b = r.randint(30, 99), r.randint(11, 29)
            out.append(num_choices(r, f"{a} - {b} = ?", a - b, spread=12, lo=0))
        for _ in range(50):
            a, b = r.randint(101, 899), r.randint(101, 499)
            out.append(num_choices(r, f"{a} + {b} = ?", a + b, spread=40, lo=1))
            out.append(num_choices(r, f"{a + b} - {b} = ?", a, spread=40, lo=1))
        for a in range(2, 13):
            for b in range(2, 13):
                out.append(num_choices(r, f"{a} × {b} = ?", a * b, spread=max(4, a * b // 5), lo=1))
        for b in range(2, 13):
            for q in range(2, 13):
                out.append(num_choices(r, f"{b * q} ÷ {b} = ?", q, spread=4, lo=1))
        for _ in range(40):
            a, b = r.randint(12, 60), r.randint(3, 9)
            out.append(num_choices(r, f"{a} × {b} = ?", a * b, spread=max(6, a * b // 6), lo=1))
        for step in range(2, 13):
            for _ in range(4):
                st = r.randint(0, 4) * step
                seq = [st + step * i for i in range(4)]
                out.append(num_choices(r, f"Count by {step}s: {', '.join(map(str, seq))}, ...?", st + step * 4, spread=step, lo=0))
        for _ in range(40):
            step, st = r.choice([2, 5, 10, 25, 50, 100]), r.randint(1, 30)
            seq = [st + step * i for i in range(4)]
            out.append(num_choices(r, f"What number comes next? {', '.join(map(str, seq))}, ...", st + step * 4, spread=step, lo=0))
        for _ in range(40):
            a, b = r.randint(3, 40), r.randint(2, 40)
            out.append(num_choices(r, f"? + {a} = {a + b}. What is the missing number?", b, spread=6, lo=0))
            out.append(num_choices(r, f"{a + b} - ? = {a}. What is the missing number?", b, spread=6, lo=0))
        # place value
        PL = {1: "ones", 10: "tens", 100: "hundreds", 1000: "thousands"}
        for _ in range(60):
            n = r.randint(1000, 9999)
            if len(set(str(n))) < 4: continue
            place = r.choice([10, 100, 1000])
            d = int(str(n)[-len(str(place))])
            if d == 0: continue
            out.append(mc(r, f"What is the value of the digit {d} in {n:,}?", f"{d * place:,}", [f"{d * p:,}" for p in (1, 10, 100, 1000) if p != place]))
            out.append(mc(r, f"Which digit is in the {PL[place]} place of {n:,}?", str(d), [x for x in "0123456789" if x != str(d)]))
        for _ in range(40):
            n = r.randint(100, 999)
            if len(set(str(n))) < 3: continue
            h, t, o = int(str(n)[0]) * 100, int(str(n)[1]) * 10, int(str(n)[2])
            out.append(num_choices(r, f"What number is {h} + {t} + {o}?", n, spread=30, lo=100))
            out.append(num_choices(r, f"What number has {h // 100} hundreds, {t // 10} tens and {o} ones?", n, spread=30, lo=100))
        for _ in range(60):
            n = r.randint(11, 989)
            if n % 10 == 5: continue
            near = round(n / 10) * 10
            out.append(num_choices(r, f"Round {n} to the nearest ten.", near, spread=30, lo=0))
        for _ in range(40):
            n = r.randint(101, 2999)
            if n % 100 == 50: continue
            near = round(n / 100) * 100
            out.append(num_choices(r, f"Round {n} to the nearest hundred.", near, spread=300, lo=0))
        # odd/even
        for _ in range(40):
            n = r.randint(10, 999)
            out.append(mc(r, f"Is {n} odd or even?", "Even" if n % 2 == 0 else "Odd", ["Even", "Odd", "Both", "Neither"]))
        for _ in range(30):
            n = r.randint(10, 500)
            nxt = n + 2
            kind = "even" if n % 2 == 0 else "odd"
            out.append(num_choices(r, f"What is the next {kind} number after {n}?", nxt, spread=3, lo=1))
            out.append(num_choices(r, f"What is the {kind} number just before {n}?", n - 2, spread=3, lo=0))
        # fractions
        for d in [2, 3, 4, 5, 6, 8, 10]:
            for _ in range(6):
                m = r.randint(2, 12)
                N = d * m
                out.append(num_choices(r, f"What is 1/{d} of {N}?", m, spread=max(3, m // 2), lo=1))
                k = r.randint(2, d - 1) if d > 2 else 1
                out.append(num_choices(r, f"What is {k}/{d} of {N}?", k * m, spread=max(3, k * m // 3), lo=0))
        for _ in range(50):
            N = 2 * r.randint(3, 60)
            out.append(num_choices(r, f"What is half of {N}?", N // 2, spread=5, lo=1))
            out.append(num_choices(r, f"What is double {N // 2}?", N, spread=6, lo=1))
        for n in [2, 3, 4, 5, 6, 8, 10, 12]:
            for k in range(1, n):
                for col in r.sample(["#1E88E5", "#E53935", "#43A047"], 2):
                    ans = Fraction(k, n)
                    ex = [Fraction(j, n) for j in range(1, n) if j != k] + [Fraction(k, n + 1), Fraction(k, n + 2), Fraction(k + 1, n + 1), Fraction(n - k, n), Fraction(k, max(2, n - 1))]
                    out.append(frac_mc(r, "What fraction of the shape is colored?", ans, ex, v=svgv(pie(n, k, col)), fb=False))
        for a in range(2, 11):
            for b in range(2, 11):
                if a == b: continue
                out.append(mc(r, f"Which is bigger: 1/{a} or 1/{b}?", f"1/{min(a, b)}", [f"1/{max(a, b)}", "They are equal", "Can't tell"]))
        for a in range(2, 9):
            for b in range(2, 9):
                if a < b:
                    out.append(mc(r, f"Which is smaller: 1/{a} or 1/{b}?", f"1/{max(a, b)}", [f"1/{a}", "They are equal", "Can't tell"]))
        # measurement
        for h in range(2, 11):
            out.append(num_choices(r, f"How many minutes are in {h} hours?", 60 * h, spread=60, lo=1))
            out.append(num_choices(r, f"How many hours are in {h} days?", 24 * h, spread=24, lo=1))
            out.append(num_choices(r, f"How many days are in {h} weeks?", 7 * h, spread=7, lo=1))
            out.append(num_choices(r, f"How many centimetres are in {h} metres?", 100 * h, spread=100, lo=1))
            out.append(num_choices(r, f"How many months are in {h} years?", 12 * h, spread=12, lo=1))
            out.append(num_choices(r, f"How many seconds are in {h} minutes?", 60 * h, spread=60, lo=1))
            out.append(num_choices(r, f"How many cents are in {h} dollars?", 100 * h, spread=100, lo=1))
            out.append(num_choices(r, f"How many grams are in {h} kilograms?", 1000 * h, spread=1000, lo=1))
        # word problems
        for _ in range(60):
            n, t = r.choice(NAMES), r.choice(THINGS)
            a, b = r.randint(12, 60), r.randint(5, 40)
            out.append(num_choices(r, f"{n} has {a} {t} and gets {b} more. How many now?", a + b, spread=8, lo=1))
            out.append(num_choices(r, f"{n} had {a + b} {t} and gave away {b}. How many are left?", a, spread=8, lo=0))
            rows, cols = r.randint(3, 9), r.randint(3, 9)
            out.append(num_choices(r, f"There are {rows} rows of {cols} {t}. How many {t} in all?", rows * cols, spread=max(5, rows * cols // 5), lo=1))
            k, m = r.randint(2, 8), r.randint(3, 9)
            out.append(num_choices(r, f"{n} splits {k * m} {t} equally among {k} kids. How many does each kid get?", m, spread=3, lo=1))
        for _ in range(30):
            a, b = r.randint(2, 9), r.randint(3, 12)
            out.append(num_choices(r, f"A box holds {a} eggs. How many eggs are in {b} boxes?", a * b, spread=max(4, a * b // 5), lo=1))
        # roman
        for n in range(1, 40):
            out.append(num_choices(r, f"What number is the Roman numeral {to_roman(n)}?", n, spread=4, lo=1))
        for n in r.sample(range(3, 40), 20):
            out.append(mc(r, f"How do you write {n} in Roman numerals?", to_roman(n), [to_roman(n + d) for d in (-2, -1, 1, 2, 5, -5) if n + d > 0]))
        for n in range(1, 11):
            out.append(mc(r, f"Which Roman numeral means {n}?", to_roman(n), [to_roman(m) for m in range(1, 13) if m != n]))
    else:  # 11+
        for _ in range(80):
            p = r.choice([5, 10, 15, 20, 25, 30, 40, 50, 60, 75, 80, 90, 12, 35, 45])
            N = r.choice(range(20, 401, 20))
            out.append(num_choices(r, f"What is {p}% of {N}?", p * N // 100, spread=max(4, p * N // 400), lo=1) if p * N % 100 == 0 else None)
        out[:] = [q for q in out if q]
        for _ in range(60):
            N, p = r.choice(range(20, 201, 20)), r.choice([10, 15, 20, 25, 30, 40, 50, 60, 75])
            out.append(num_choices(r, f"A ${N} jacket is {p}% off. What is the sale price in dollars?", N - N * p // 100, spread=max(5, N // 10), lo=1))
            out.append(num_choices(r, f"A price of ${N} goes up by {p}%. What is the new price in dollars?", N + N * p // 100, spread=max(5, N // 10), lo=1))
        for _ in range(60):
            b = r.choice([20, 25, 40, 50, 80, 200, 250, 400])
            p = r.choice([5, 10, 15, 20, 25, 30, 40, 50, 60, 75, 80])
            if (b * p) % 100: continue
            out.append(num_choices(r, f"What percent of {b} is {b * p // 100}?", p, spread=15, lo=1, fmt=lambda x: f"{x}%"))
        for d in [2, 4, 5, 8, 10, 20, 25]:
            for n in range(1, d):
                pc = Fraction(n * 100, d)
                if math.gcd(n, d) != 1: continue
                s = dec(Decimal(pc.numerator) / Decimal(pc.denominator))
                out.append(mc(r, f"What is {n}/{d} as a percent?", f"{s}%", [f"{dec(Decimal(pc.numerator) / Decimal(pc.denominator) + x)}%" for x in (10, -10, 5, -5, 20) if pc + x > 0]))
                dd = Decimal(n) / Decimal(d)
                out.append(mc(r, f"What is {n}/{d} written as a decimal?", dec(dd), [dec(dd * 10), dec(dd / 10), dec(dd + Decimal("0.1")), dec(dd + Decimal("0.25")), dec(abs(dd - Decimal("0.05")))]))
        for _ in range(30):
            x = r.randint(1, 99)
            out.append(mc(r, f"What is {x}% written as a decimal?", dec(Decimal(x) / 100), [dec(Decimal(x) / 10), dec(Decimal(x)), dec(Decimal(x) / 1000)]))
        # ratios
        for _ in range(50):
            p, q = r.choice([(2, 3), (3, 4), (1, 4), (2, 5), (3, 5), (3, 7), (1, 3), (4, 5), (5, 6), (2, 7)]), None
            a, b = p; g = r.randint(2, 9)
            out.append(mc(r, f"Simplify the ratio {a * g}:{b * g}.", f"{a}:{b}", [f"{b}:{a}", f"{a * g // 2 if g % 2 == 0 else a + 1}:{b * g // 2 if g % 2 == 0 else b + 1}", f"{a + 1}:{b}", f"{a}:{b + 1}"]) if g > 2 or True else None)
        for _ in range(50):
            a, b = r.choice([(2, 3), (3, 4), (1, 4), (2, 5), (3, 5), (1, 2), (4, 5), (3, 7)])
            k = r.randint(3, 15)
            tot = (a + b) * k
            out.append(num_choices(r, f"Share {tot} in the ratio {a}:{b}. How much is the larger share?", max(a, b) * k, spread=max(3, k * 2), lo=1))
            out.append(num_choices(r, f"Share {tot} in the ratio {a}:{b}. How much is the smaller share?", min(a, b) * k, spread=max(3, k * 2), lo=1))
        for _ in range(40):
            n, c, m = r.randint(2, 8), r.randint(2, 9), r.randint(2, 6)
            out.append(num_choices(r, f"{n} notebooks cost ${n * c}. How much do {n * m} notebooks cost, in dollars?", n * m * c, spread=max(5, n * m * c // 6), lo=1))
            sp, t = r.randint(20, 90), r.randint(2, 6)
            out.append(num_choices(r, f"A car travels {sp * t} km in {t} hours at a steady speed. What is its speed in km/h?", sp, spread=15, lo=1))
            out.append(num_choices(r, f"A cyclist rides at {sp} km/h for {t} hours. How far does she go, in km?", sp * t, spread=max(10, sp * t // 8), lo=1))
        # negatives
        for _ in range(60):
            a, b = r.randint(-20, 20), r.randint(-20, 20)
            if a >= 0 and b >= 0: continue
            bs = f"({b})" if b < 0 else str(b)
            out.append(num_choices(r, f"{a} + {bs} = ?", a + b, spread=8, lo=-10 ** 6))
            out.append(num_choices(r, f"{a} - {bs} = ?", a - b, spread=8, lo=-10 ** 6))
        for _ in range(40):
            a, b = r.randint(2, 12), r.randint(2, 12)
            s1, s2 = r.choice([-1, 1]), r.choice([-1, 1])
            if s1 == 1 and s2 == 1: continue
            x, y = s1 * a, s2 * b
            f = lambda z: f"({z})" if z < 0 else str(z)
            out.append(num_choices(r, f"{f(x)} × {f(y)} = ?", x * y, spread=max(4, a * b // 4), lo=-10 ** 6))
            out.append(num_choices(r, f"{x * y} ÷ {f(y)} = ?", x, spread=4, lo=-10 ** 6))
        for _ in range(30):
            a, b = r.sample(range(-30, 31), 2)
            hi = max(a, b)
            out.append(mc(r, f"Which is greater: {a} or {b}?", str(hi), [str(min(a, b)), "They are equal", "Cannot tell"]))
        for n in r.sample(range(-60, 61), 30):
            if n == 0: continue
            out.append(num_choices(r, f"What is the absolute value of {n}?", abs(n), spread=6, lo=0) if n < 0 else num_choices(r, f"What is |{-n}|?", n, spread=6, lo=0))
        for _ in range(30):
            t, d = r.randint(-15, 5), r.randint(3, 20)
            out.append(num_choices(r, f"The temperature is {t}°C and then it rises by {d}°C. What is it now?", t + d, spread=6, lo=-10 ** 6, fmt=lambda x: f"{x}°C"))
            out.append(num_choices(r, f"The temperature is {t}°C and then it drops by {d}°C. What is it now?", t - d, spread=6, lo=-10 ** 6, fmt=lambda x: f"{x}°C"))
        # exponents and roots
        for b in range(2, 11):
            for e in range(2, 6):
                if b ** e > 100000: continue
                out.append(num_choices(r, f"What is {b}{sup(e)}?", b ** e, spread=max(4, b ** e // 4), lo=1))
        for b in range(2, 8):
            out.append(num_choices(r, f"What is (-{b})³?", -(b ** 3), spread=max(4, b ** 3 // 4), lo=-10 ** 6))
            out.append(num_choices(r, f"What is (-{b})²?", b * b, spread=max(4, b), lo=-10 ** 6))
            out.append(mc(r, f"What is {b}⁰?", "1", ["0", str(b), "undefined"]))
            out.append(mc(r, f"What is {b}⁻¹?", f"1/{b}", [str(-b), f"-1/{b}", str(b)]))
        for b, e in [(2, 3), (2, 4), (2, 5), (3, 2), (3, 3), (10, 2), (10, 3), (5, 2), (4, 2)]:
            out.append(mc(r, f"What is {b}{sup(-e)}?", f"1/{b ** e}", [f"-{b ** e}", f"-1/{b ** e}", f"1/{b * e}", f"{b * e}"]))
        for n in range(2, 26):
            out.append(num_choices(r, f"What is √{n * n}?", n, spread=max(3, n // 4), lo=1))
        for n in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
            out.append(num_choices(r, f"What is the cube root of {n ** 3}?", n, spread=3, lo=1))
        for n in range(2, 200):
            k = math.isqrt(n)
            if k * k == n: continue
            if r.random() < 0.35:
                out.append(mc(r, f"√{n} lies between which two whole numbers?", f"{k} and {k + 1}", [f"{k - 1} and {k}", f"{k + 1} and {k + 2}", f"{k + 2} and {k + 3}", f"{max(1, k - 2)} and {max(1, k - 1)}"]))
        for e in range(1, 8):
            out.append(mc(r, f"What is 2{sup(e + 4)} ÷ 2{sup(e)}?", str(2 ** 4), [str(2 ** 5), str(2 ** 3), "8", "32", "4"]))
        # order of operations
        TEMPL = ["{a} + {b} × {c}", "({a} + {b}) × {c}", "{a} × {b} - {c} × {d}", "{a} + {b} × {c} - {d}", "{a} - {b} + {c}", "{a} + {bc} ÷ {c}", "{a} × ({b} + {c})",
                 "{a} + {b}² × {c}", "({a} - {b}) × {c} + {d}", "{a} - {b} × {c}", "{bc} ÷ {c} + {a} × {d}", "{a} × {d} - {bc} ÷ {c}"]
        for _ in range(140):
            t = r.choice(TEMPL)
            a, b, c, d = r.randint(2, 12), r.randint(2, 9), r.randint(2, 9), r.randint(2, 9)
            if "{a} - {b} + {c}" == t and a <= b: continue
            expr = t.format(a=a, b=b, c=c, d=d, bc=b * c)
            try:
                v = evalx(expr)
            except Exception:
                continue
            if v.denominator != 1 or v < 0: continue
            v = int(v)
            pool = []
            try:
                l = ltr(expr)
                if Fraction(l).denominator == 1 and int(l) != v: pool.append(str(int(l)))
            except Exception:
                pass
            pool += [str(v + d) for d in (-3, -2, -1, 1, 2, 3, 10, -10) if v + d >= 0]
            out.append(mc(r, f"Evaluate: {expr}", str(v), pool))
        # fractions & decimals
        DEN = [2, 3, 4, 5, 6, 8, 10, 12]
        for _ in range(80):
            b, d = r.choice(DEN), r.choice(DEN)
            a, c = r.randint(1, b - 1), r.randint(1, d - 1)
            A, B = Fraction(a, b), Fraction(c, d)
            out.append(frac_mc(r, f"What is {a}/{b} + {c}/{d}?", A + B, [Fraction(a + c, b + d), A * B, A + B + Fraction(1, b * d), abs(A + B - Fraction(1, math.lcm(b, d))), A - B if A != B else A + B + 1, Fraction(a + c, math.lcm(b, d))]))
            if A != B:
                big, small = (A, B) if A > B else (B, A)
                bs, ss = (f"{a}/{b}", f"{c}/{d}") if A > B else (f"{c}/{d}", f"{a}/{b}")
                out.append(frac_mc(r, f"What is {bs} - {ss}?", big - small, [big + small, big * small, big - small + Fraction(1, 12), Fraction(abs(a - c), abs(b - d)) if b != d else big + Fraction(1, 7), big - small + Fraction(1, 10)]))
            out.append(frac_mc(r, f"What is {a}/{b} × {c}/{d}?", A * B, [A + B, Fraction(a * c, b + d), A * B * 2, Fraction(a + c, b * d), A / B]))
            out.append(frac_mc(r, f"What is {a}/{b} ÷ {c}/{d}?", A / B, [A * B, B / A if B != A else A + 1, A + B, Fraction(a * d, b * d + 1), A / B + 1]))
        for _ in range(60):
            x, y = r.randint(2, 99), r.randint(2, 99)
            X, Y = Decimal(x) / 10, Decimal(y) / 10
            if r.random() < 0.5:
                ans = X + Y
                out.append(mc(r, f"What is {dec(X)} + {dec(Y)}?", dec(ans), [dec(ans + Decimal(k)) for k in ("0.1", "-0.1", "1", "-1", "10", "0.01")]))
            else:
                ans = X * Y
                out.append(mc(r, f"What is {dec(X)} × {dec(Y)}?", dec(ans), [dec(ans * 10), dec(ans / 10), dec(ans + Decimal("0.1")), dec(ans - Decimal("0.01")), dec(ans * 100)]))
        for _ in range(30):
            a, b = r.randint(2, 40), r.randint(2, 9)
            n = r.randint(11, 99)
            out.append(mc(r, f"What is {dec(Decimal(n * b) / 10)} ÷ {b}?", dec(Decimal(n) / 10), [dec(Decimal(n)), dec(Decimal(n) / 100), dec(Decimal(n) / 10 + 1), dec(Decimal(n) / 10 - Decimal("0.1"))]))
        # primes & factors
        for n in range(1, 26):
            pr = [p for p in range(2, 200) if is_prime(p)][n - 1]
            out.append(num_choices(r, f"What is the {ordinal(n)} prime number?", pr, spread=max(3, pr // 4), lo=1))
        for n in range(10, 200, 3):
            nxt = next(p for p in range(n + 1, 400) if is_prime(p))
            wrong = [m for m in range(n + 1, nxt + 12) if not is_prime(m) and m != nxt]
            out.append(mc(r, f"What is the smallest prime number greater than {n}?", str(nxt), [str(m) for m in wrong]))
        for N in range(10, 101, 10):
            out.append(num_choices(r, f"How many prime numbers are less than {N}?", sum(is_prime(k) for k in range(2, N)), spread=3, lo=1))
        for n in range(4, 200):
            if is_prime(n) or r.random() > 0.5: continue
            sp = min(factorization(n))
            out.append(mc(r, f"What is the smallest prime factor of {n}?", str(sp), [str(x) for x in range(2, 14) if x != sp]))
            fs = factorization(n)
            alts = {fstr(factorization(n + d)) for d in (-2, -1, 1, 2, 4, 6, -4) if n + d > 1}
            alts.discard(fstr(fs))
            if len(alts) >= 3 and len(fs) >= 1 and sum(fs.values()) >= 2:
                out.append(mc(r, f"What is the prime factorization of {n}?", fstr(fs), sorted(alts)))
        for n in range(12, 151):
            if r.random() > 0.55: continue
            out.append(num_choices(r, f"How many factors does {n} have?", len(divisors(n)), spread=3, lo=1))
            fct = [d for d in divisors(n) if 1 < d < n]
            if fct:
                nf = [m for m in range(2, n) if n % m]
                out.append(mc(r, f"Which of these is a factor of {n}?", str(r.choice(fct)), [str(m) for m in nf]))
        for _ in range(60):
            g = r.randint(2, 12)
            a, b = r.choice([(2, 3), (3, 4), (2, 5), (3, 5), (4, 5), (5, 6), (3, 7), (2, 7), (4, 9), (5, 7)])
            x, y = a * g, b * g
            out.append(num_choices(r, f"What is the greatest common factor of {x} and {y}?", math.gcd(x, y), spread=max(2, g // 2 + 1), lo=1))
            out.append(num_choices(r, f"What is the lowest common multiple of {x} and {y}?", math.lcm(x, y), spread=max(6, math.lcm(x, y) // 8), lo=1))
        # algebra
        for _ in range(70):
            a, x, b = r.randint(2, 9), r.randint(-6, 12), r.randint(-12, 15)
            c = a * x + b
            bs = f"+ {b}" if b >= 0 else f"- {-b}"
            out.append(num_choices(r, f"Solve for x: {a}x {bs} = {c}", x, spread=4, lo=-10 ** 6))
        for _ in range(40):
            a, b, x = r.randint(2, 6), r.randint(2, 9), r.randint(2, 12)
            out.append(num_choices(r, f"Solve for x: x/{a} = {x}", a * x, spread=max(4, a), lo=-10 ** 6))
            out.append(num_choices(r, f"Solve for x: {a}(x + {b}) = {a * (x + b)}", x, spread=4, lo=-10 ** 6))
        for _ in range(40):
            a, c, x, b = r.randint(4, 9), r.randint(1, 3), r.randint(1, 10), r.randint(-8, 8)
            d = (a - c) * x + b
            bs = f"+ {b}" if b >= 0 else f"- {-b}"
            out.append(num_choices(r, f"Solve for x: {a}x {bs} = {c}x + {d}", x, spread=4, lo=-10 ** 6) if (a - c) * x + b == d else None)
        out[:] = [q for q in out if q]
        for _ in range(40):
            x, a, b = r.randint(2, 9), r.randint(2, 6), r.randint(1, 9)
            out.append(num_choices(r, f"If x = {x}, what is {a}x² + {b}?", a * x * x + b, spread=max(5, a * x), lo=1))
            out.append(num_choices(r, f"If x = {x}, what is {a}x - {b}?", a * x - b, spread=5, lo=-10 ** 6))
        for a in range(2, 10):
            for b in range(2, 10):
                if r.random() < 0.4:
                    out.append(mc(r, f"Expand: {a}(x + {b})", f"{a}x + {a * b}", [f"{a}x + {b}", f"x + {a * b}", f"{a + 1}x + {a * b}", f"{a}x + {a + b}"]))
        for _ in range(40):
            x1, y1, m = r.randint(-4, 5), r.randint(-5, 6), r.choice([-4, -3, -2, -1, 1, 2, 3, 4, 5])
            dx = r.randint(1, 4)
            x2, y2 = x1 + dx, y1 + m * dx
            out.append(num_choices(r, f"What is the slope of the line through ({x1}, {y1}) and ({x2}, {y2})?", m, spread=3, lo=-10 ** 6))
        # sequences
        for _ in range(40):
            a, d, n = r.randint(1, 20), r.randint(2, 9), r.randint(10, 30)
            seq = ", ".join(str(a + d * i) for i in range(3))
            out.append(num_choices(r, f"What is the {ordinal(n)} term of the sequence {seq}, ...?", a + d * (n - 1), spread=max(6, d * 2), lo=1))
        for _ in range(30):
            a, rr = r.randint(1, 5), r.choice([2, 3, 4])
            seq = [a * rr ** i for i in range(4)]
            out.append(num_choices(r, f"What comes next? {', '.join(map(str, seq))}, ...", a * rr ** 4, spread=max(4, a * rr ** 4 // 5), lo=1))
        for _ in range(30):
            a, b = r.randint(1, 4), r.randint(1, 5)
            seq = [a, b]
            while len(seq) < 7: seq.append(seq[-1] + seq[-2])
            out.append(num_choices(r, f"Each number is the sum of the two before it: {', '.join(map(str, seq))}, ... What is next?", seq[-1] + seq[-2], spread=max(5, seq[-1] // 3), lo=1))
        for n in [10, 15, 20, 25, 30, 40, 50, 60, 75, 100]:
            out.append(num_choices(r, f"What is 1 + 2 + 3 + ... + {n}?", n * (n + 1) // 2, spread=max(5, n * 2), lo=1))
        # statistics
        for _ in range(60):
            n = r.choice([5, 7])
            xs = [r.randint(2, 30) for _ in range(n - 1)]
            xs.append(r.randint(2, 30))
            xs[-1] += (-sum(xs)) % n
            r.shuffle(xs)
            s = ", ".join(map(str, xs))
            out.append(num_choices(r, f"What is the mean of {s}?", sum(xs) // n, spread=4, lo=0))
            srt = sorted(xs)
            out.append(num_choices(r, f"What is the median of {s}?", srt[n // 2], spread=4, lo=0))
            out.append(num_choices(r, f"What is the range of {s}?", max(xs) - min(xs), spread=5, lo=0))
        for _ in range(30):
            m = r.randint(2, 20)
            xs = [m, m] + r.sample([x for x in range(1, 25) if x != m], 4)
            r.shuffle(xs)
            out.append(num_choices(r, f"What is the mode of {', '.join(map(str, xs))}?", m, spread=5, lo=0))
        for _ in range(40):
            red, blue = r.randint(1, 9), r.randint(1, 9)
            if red == blue: continue
            tot = red + blue
            out.append(frac_mc(r, f"A bag has {red} red and {blue} blue marbles. What is the probability of picking red?", Fraction(red, tot), [Fraction(red, blue), Fraction(blue, tot), Fraction(1, 2), Fraction(red, tot + 1), Fraction(1, tot)]))
        for s in range(2, 13):
            ways = 6 - abs(s - 7)
            out.append(frac_mc(r, f"Two fair dice are rolled. What is the probability that the sum is {s}?", Fraction(ways, 36), [Fraction(ways + 1, 36), Fraction(1, 12) if Fraction(ways, 36) != Fraction(1, 12) else Fraction(1, 18), Fraction(ways, 12), Fraction(ways, 6), Fraction(ways + 2, 36), Fraction(1, 2)]))
        # sci notation, binary
        for m, e in [(3.2, 5), (4.5, 6), (7, 4), (1.8, 7), (6.1, 3), (2.5, 8), (9, 5), (5.6, 9), (8.4, 6), (1.2, 4), (3.7, 7), (4, 10)]:
            N = int(Decimal(str(m)) * 10 ** e)
            out.append(mc(r, f"Write {N:,} in scientific notation.", f"{m:g} × 10{sup(e)}", [f"{m:g} × 10{sup(e + 1)}", f"{m:g} × 10{sup(e - 1)}", f"{m / 10:g} × 10{sup(e)}", f"{m:g} × 10{sup(e + 2)}"]))
        for m, e in [(4.5, -4), (3, -3), (7.2, -5), (1.6, -2), (9, -6), (2.8, -3)]:
            N = Decimal(str(m)) * Decimal(10) ** e
            out.append(mc(r, f"Write {format(N, 'f')} in scientific notation.", f"{m:g} × 10{sup(e)}", [f"{m:g} × 10{sup(-e)}", f"{m:g} × 10{sup(e + 1)}", f"{m:g} × 10{sup(e - 1)}"]))
        for n in r.sample(range(5, 64), 32):
            b = bin(n)[2:]
            out.append(num_choices(r, f"What is the binary number {b} in decimal?", n, spread=6, lo=1))
        for n in r.sample(range(5, 64), 20):
            alts = {bin(n + d)[2:] for d in (-2, -1, 1, 2, 3, 4)}
            alts.discard(bin(n)[2:])
            out.append(mc(r, f"What is {n} in binary?", bin(n)[2:], sorted(alts)))
        for n in r.sample(range(40, 3999), 30):
            out.append(num_choices(r, f"What number is the Roman numeral {to_roman(n)}?", n, spread=max(10, n // 20), lo=1))
        for n in [90, 99, 400, 900, 1994, 2024, 1066, 49, 444, 1999]:
            out.append(mc(r, f"How do you write {n} in Roman numerals?", to_roman(n), [to_roman(n + d) for d in (-10, -1, 1, 10, 100, -100, 5) if n + d > 0]))
    return out
