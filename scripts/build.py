#!/usr/bin/env python3
"""Compile the source files into dist/brain.json, the bundle the review page and the plugin read.

Usage: python3 scripts/build.py [--root .] [--out dist/brain.json]
"""
import argparse, datetime, glob, json, os, subprocess


def load(p):
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def commit(root):
    try:
        return subprocess.check_output(["git", "-C", root, "rev-parse", "--short", "HEAD"], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None


def build(root):
    caps = []
    for cp in sorted(glob.glob(os.path.join(root, "capabilities", "*", "capability.json"))):
        cap = load(cp)
        fdir = os.path.join(os.path.dirname(cp), "features")
        feats = {load(p)["id"]: load(p) for p in glob.glob(os.path.join(fdir, "*.json"))}
        order = cap.pop("feature_order", None) or sorted(feats)
        order += sorted(set(feats) - set(order))
        cap["features"] = [feats[i] for i in order if i in feats]
        caps.append(cap)
    decs = [load(p) for p in glob.glob(os.path.join(root, "decisions", "*.json"))]
    decs.sort(key=lambda d: int(d["id"].split("-")[-1]) if d["id"].split("-")[-1].isdigit() else 0)
    return {
        "generated": {"commit": commit(root), "date": datetime.date.today().isoformat()},
        "capabilities": caps,
        "decisions": decs,
        "roles": load(os.path.join(root, "roles.json")),
        "glossary": load(os.path.join(root, "glossary.json")),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default="dist/brain.json")
    a = ap.parse_args()
    D = build(a.root)
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as fh:
        json.dump(D, fh, ensure_ascii=False)
    print(f"wrote {a.out}: {len(D['capabilities'])} capabilities, {len(D['decisions'])} decisions")


if __name__ == "__main__":
    main()
