#!/usr/bin/env python3
"""Builds questions/<category>.json (200 questions x 3 age bands per category) from tools/qgen/cats/*.py"""
import importlib, json, pathlib, sys, collections
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from qgen.common import BANDS, N, rng_for

ORDER = ["disney", "animals", "shapes", "colors", "numbers", "fruits_veg", "dinosaurs", "space", "ocean", "vehicles"]


def validate(q, where):
    assert isinstance(q.get("q"), str) and 3 <= len(q["q"]) <= 140, f"{where}: bad text {q.get('q')!r}"
    assert "{" not in q["q"] and "}" not in q["q"], f"{where}: unformatted template {q['q']!r}"
    c = q.get("c"); assert isinstance(c, list) and len(c) == 4 and len(set(map(str, c))) == 4, f"{where}: need 4 distinct choices {c!r}"
    assert isinstance(q.get("a"), int) and 0 <= q["a"] < 4, f"{where}: bad answer index"
    assert q.get("ct", "text") in ("text", "emoji", "svg", "img"), f"{where}: bad ct"
    assert all(isinstance(x, str) and x for x in c), f"{where}: empty/non-str choice"
    if q.get("ct", "text") == "text":
        assert all(len(x) <= 60 for x in c), f"{where}: choice too long {c!r}"
    v = q.get("v")
    if v is not None:
        assert v.get("t") in ("emoji", "svg", "img") and isinstance(v.get("v"), str) and v["v"], f"{where}: bad visual"


def main():
    only = set(sys.argv[1:])
    total = 0
    for cid in ORDER:
        if only and cid not in only: continue
        try:
            mod = importlib.import_module(f"qgen.cats.{cid}")
        except ModuleNotFoundError as e:
            if e.name == f"qgen.cats.{cid}":
                print(f"- {cid}: (module missing, skipped)"); continue
            raise
        meta = dict(mod.META); assert meta["id"] == cid
        out = {**meta, "bands": {}}
        for band in BANDS:
            seen, qs = set(), []
            for q in mod.build(band):
                key = (q["q"], json.dumps(q.get("v"), sort_keys=True), tuple(sorted(map(str, q["c"]))))
                if key in seen: continue
                seen.add(key); qs.append(q)
            # one question text+visual at most once, so players never see an exact repeat with reshuffled answers
            uniq, seen2 = [], set()
            for q in qs:
                k2 = (q["q"], json.dumps(q.get("v"), sort_keys=True))
                if k2 in seen2: continue
                seen2.add(k2); uniq.append(q)
            if len(uniq) < N:
                raise SystemExit(f"{cid} [{band}]: only {len(uniq)} distinct questions, need {N}")
            r = rng_for("order", cid, band); r.shuffle(uniq); uniq = uniq[:N]
            for i, q in enumerate(uniq):
                validate(q, f"{cid}[{band}]#{i}")
                q["id"] = f"{cid}-{band}-{i:03d}"
            out["bands"][band] = uniq
        p = ROOT / "questions" / f"{cid}.json"
        p.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")))
        kinds = collections.Counter((q.get("v") or {}).get("t", "none") for b in out["bands"].values() for q in b)
        print(f"+ {cid}: {sum(len(b) for b in out['bands'].values())} questions, {p.stat().st_size // 1024} KB, visuals={dict(kinds)}")
        total += 600
    print("total", total)


if __name__ == "__main__":
    main()
