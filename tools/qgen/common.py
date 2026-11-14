"""Shared helpers for question generators. Each category module (tools/qgen/cats/<id>.py) defines:
    META  = {"id": "animals", "name": "Animals", "icon": "🐾"}
    build(band) -> list[dict]     # band in BANDS; return AT LEAST 200 distinct questions (more is fine; build trims to 200)
Build with:  python3 tools/build_questions.py
"""
import hashlib, random

BANDS = ["2-5", "6-10", "11+"]
N = 200


def rng_for(*parts):
    """Deterministic RNG so rebuilds produce identical files."""
    return random.Random(hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest())


# --- visuals: shown big above the question -------------------------------------------------
def emoji(s):  return {"t": "emoji", "v": s}
def svgv(m):   return {"t": "svg", "v": m}
def img(path): return {"t": "img", "v": path}       # relative to public/img/ ; question is dropped if file is missing


def mc(r, q, ans, pool, *, v=None, ct="text", k=3):
    """Multiple choice: `ans` is the right answer, `pool` is a list of candidate WRONG answers
    (may contain ans/duplicates; they are filtered). ct = how CHOICES render: text | emoji | svg | img.
    Returns {"q","c":[4 choices],"a":index,["v"],["ct"]}."""
    wrong, seen = [], {ans}
    cand = list(pool)
    r.shuffle(cand)
    for x in cand:
        if x not in seen:
            wrong.append(x); seen.add(x)
        if len(wrong) == k:
            break
    if len(wrong) < k:
        raise ValueError(f"not enough distractors for {q!r}")
    choices = wrong + [ans]
    r.shuffle(choices)
    d = {"q": q, "c": choices, "a": choices.index(ans)}
    if v:
        d["v"] = v
    if ct != "text":
        d["ct"] = ct
    return d


def num_choices(r, q, ans, *, v=None, spread=None, lo=0, k=3, fmt=str):
    """Numeric multiple choice with plausible nearby wrong answers (all >= lo, all distinct)."""
    spread = spread or max(2, abs(ans) // 3 or 2)
    cand = [c for c in range(ans - spread, ans + spread + 1) if c != ans and c >= lo]
    step = 1
    while len(cand) < k:                      # near the lower bound: widen upwards
        cand = [c for c in range(max(lo, ans - spread), ans + spread + step + 1) if c != ans]
        step += 1
    return mc(r, q, fmt(ans), [fmt(c) for c in cand], v=v, k=k)
