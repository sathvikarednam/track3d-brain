# Track3D product brain

The record of what Track3D **should** do: 18 capabilities, their features, requirements with acceptance criteria, performance targets, role permissions, open decisions and the glossary.

This repo is the source of truth. The Brain Review page and the `track3d-brain` Claude plugin read the compiled bundle built from it.

## Layout

```
capabilities/<CAP>/capability.json        summary, owner, related capabilities, feature order
capabilities/<CAP>/features/<FEAT>.json   one feature: components, role grants, NFRs, requirements, acceptance criteria
decisions/DEC-nnn.json                    one decision: question, options, status, decision
glossary.json, roles.json
scripts/build.py      compiles everything into dist/brain.json (not committed; CI builds it)
scripts/validate.py   checks ids, references, statuses and grants
scripts/split.py      imports a compiled bundle into these files (one-off)
docs/schema.md        field reference
```

## Statuses

- **verified-by-product**: product confirmed it is intended. Only product owners set this.
- **draft**: stated by a person, not yet verified.
- **inferred-from-code**: what the system does today; not necessarily intended.
- **disputed**: stated intent and code disagree; `dispute` says how.

Decisions are `open`, `on-hold` or `decided` (decided needs the decision text).

## How changes get in

Only through pull requests to `main`:

1. Engineering and product answer gaps on the Brain Review page.
2. `/brain-review` in Claude reads the answers and opens a PR on a `brain-review/<date>` branch that edits the files above. Answers that disagree are listed as conflicts and not applied.
3. CI runs `validate.py` and builds `dist/brain.json`.
4. CODEOWNERS approve: the Tech Architect for everything, plus the capability's product owner.
5. After merge, refresh the review page and plugin from the CI build artifact.

Direct edits follow the same route: branch, edit, PR.

## Restricted items

Requirements marked `"restricted": true` are placeholders. Their content is handled with engineering separately and must not be added to this repo.

## Local use

```bash
python3 scripts/validate.py
python3 scripts/build.py          # writes dist/brain.json
```
