#!/usr/bin/env python3
"""Check the brain's source files. Exits non-zero on errors; warnings are printed but don't fail.

Usage: python3 scripts/validate.py [--root .] [--strict]   (--strict turns warnings into errors)
"""
import argparse, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import build  # noqa: E402

REQ_STATUS = {"verified-by-product", "draft", "inferred-from-code", "disputed"}
DEC_STATUS = {"open", "on-hold", "decided"}
GRANTS = {"allow", "deny", "conditional", "unknown"}
ID_RE = {
    "feature": re.compile(r"^[A-Z]+-FEAT-\d+$"),
    "requirement": re.compile(r"^[A-Z]+-REQ-\d+$"),
    "nfr": re.compile(r"^[A-Z]+-NFR-\d+$"),
    "decision": re.compile(r"^DEC-\d+$"),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args()
    D = build(a.root)
    errors, warnings = [], []
    E, W = errors.append, warnings.append

    seen = {}
    def uniq(i, where):
        if i in seen:
            E(f"duplicate id {i} ({where} and {seen[i]})")
        seen[i] = where

    roles = {r["id"] for r in D["roles"]}
    caps = {c["id"] for c in D["capabilities"]}
    decs = {d["id"]: d for d in D["decisions"]}
    reqs = {}

    for c in D["capabilities"]:
        uniq(c["id"], "capability")
        for rel in c.get("related", []):
            if rel not in caps:
                E(f"{c['id']}: related capability {rel} does not exist")
        if not c.get("owner"):
            W(f"{c['id']}: no product owner")
        for f in c["features"]:
            uniq(f["id"], f"feature in {c['id']}")
            if not ID_RE["feature"].match(f["id"]) or not f["id"].startswith(c["id"] + "-"):
                E(f"{f['id']}: feature id does not match capability {c['id']}")
            for d in f.get("decisions", []):
                if d not in decs:
                    E(f"{f['id']}: decision {d} does not exist")
            for act in f.get("roles", {}).get("actions", []):
                for role, g in act.get("grants", {}).items():
                    if role not in roles:
                        E(f"{f['id']}: grant for unknown role {role} on '{act['action']}'")
                    if g not in GRANTS:
                        E(f"{f['id']}: grant '{g}' for {role} on '{act['action']}' is not one of {sorted(GRANTS)}")
            for n in f.get("nfr", []):
                uniq(n["id"], f"nfr in {f['id']}")
                if n.get("status") not in REQ_STATUS:
                    E(f"{n['id']}: invalid status {n.get('status')}")
            for r in f["requirements"]:
                uniq(r["id"], f"requirement in {f['id']}")
                reqs[r["id"]] = r
                if not ID_RE["requirement"].match(r["id"]):
                    E(f"{r['id']}: malformed requirement id")
                if r.get("status") not in REQ_STATUS:
                    E(f"{r['id']}: invalid status {r.get('status')}")
                if r.get("restricted"):
                    continue
                if r.get("status") == "disputed" and not r.get("dispute"):
                    W(f"{r['id']}: disputed but no dispute summary")
                if r.get("status") != "disputed" and r.get("dispute"):
                    W(f"{r['id']}: has a dispute but status is {r.get('status')}")
                for d in r.get("decisions", []):
                    if d not in decs:
                        E(f"{r['id']}: decision {d} does not exist")
                for ac in r.get("acceptance_criteria", []):
                    uniq(ac["id"], f"acceptance criterion of {r['id']}")
                    if not ac["id"].startswith(r["id"] + "-AC"):
                        E(f"{ac['id']}: acceptance criterion id should start with {r['id']}-AC")
                    for k in ("given", "when", "then"):
                        if not ac.get(k):
                            E(f"{ac['id']}: missing '{k}'")

    for d in D["decisions"]:
        uniq(d["id"], "decision")
        if d.get("status") not in DEC_STATUS:
            E(f"{d['id']}: invalid status {d.get('status')}")
        if d.get("status") == "decided" and not d.get("decision"):
            E(f"{d['id']}: status is decided but no decision text")
        if d.get("status") != "decided" and d.get("decision"):
            W(f"{d['id']}: has decision text but status is {d.get('status')}")
        for c in d.get("capabilities", []):
            if c not in caps:
                E(f"{d['id']}: capability {c} does not exist")
        for r in d.get("requirements", []):
            if r not in reqs:
                E(f"{d['id']}: requirement {r} does not exist")

    gids = set()
    for g in D["glossary"]:
        if g["id"] in gids:
            E(f"glossary: duplicate id {g['id']}")
        gids.add(g["id"])

    for w in warnings:
        print("warning:", w)
    for e in errors:
        print("error:", e)
    print(f"{len(errors)} error(s), {len(warnings)} warning(s)")
    if errors or (a.strict and warnings):
        sys.exit(1)


if __name__ == "__main__":
    main()
