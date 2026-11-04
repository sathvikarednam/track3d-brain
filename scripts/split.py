#!/usr/bin/env python3
"""Split a compiled brain bundle (brain.json) into the repo's source files.

Usage: python3 scripts/split.py path/to/brain.json [--root .]

Writes capabilities/<CAP>/capability.json, capabilities/<CAP>/features/<FEAT>.json,
decisions/<DEC>.json, glossary.json and roles.json. Existing files are overwritten.
Use it once to import a bundle; after that, edit the source files through PRs.
"""
import argparse, json, os


def dump(path, obj):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bundle")
    ap.add_argument("--root", default=".")
    a = ap.parse_args()
    with open(a.bundle, encoding="utf-8") as fh:
        D = json.load(fh)
    R = a.root
    for c in D["capabilities"]:
        base = os.path.join(R, "capabilities", c["id"])
        cap = {k: v for k, v in c.items() if k != "features"}
        cap.setdefault("owner", None)
        cap["feature_order"] = [f["id"] for f in c["features"]]
        dump(os.path.join(base, "capability.json"), cap)
        for f in c["features"]:
            dump(os.path.join(base, "features", f["id"] + ".json"), f)
    for d in D["decisions"]:
        dump(os.path.join(R, "decisions", d["id"] + ".json"), d)
    dump(os.path.join(R, "glossary.json"), D["glossary"])
    dump(os.path.join(R, "roles.json"), D["roles"])
    print(f'{len(D["capabilities"])} capabilities, {sum(len(c["features"]) for c in D["capabilities"])} features, '
          f'{len(D["decisions"])} decisions written under {os.path.abspath(R)}')


if __name__ == "__main__":
    main()
