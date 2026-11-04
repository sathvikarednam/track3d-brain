# Brain schema

Source files hold the same objects as the compiled bundle: `capabilities/<CAP>/capability.json` is a capability without its features (plus `owner` and `feature_order`), each `features/<FEAT>.json` is one feature with its requirements and NFRs, and each `decisions/<DEC>.json` is one decision. `scripts/build.py` assembles them into `dist/brain.json` with the shape below.

Top level: `generated {commit, date}`, `capabilities[]`, `decisions[]`, `roles[]`, `glossary[]`.

## Capability
`id` (e.g. `PROG`), `name`, `summary`, `related[]` (other capability ids), `features[]`. An `owner` field may be added by review (product owner's user id).

## Feature
`id` (`PROG-FEAT-02`), `name`, `summary`, `components[]` (provisional ids such as `svc.api-2d-progress`, `web.track3d-web`, `mod.progress-agent`), `decisions[]`, `roles`, `nfr[]`, `requirements[]`.

`roles`: `status`, `note`, `actions[]`, each `{action, permission (string or null), grants {roleId: allow|deny|conditional|unknown}, note}`.

`nfr[]` (performance and volume targets): `id` (`AI-NFR-001`), `kind` (latency, volume, …), `statement`, `target` (null until set), `status`, `open_question`.

## Requirement
- `id` (`PROG-REQ-005`), `type`, `title`, `statement`, `rationale`
- `status`: `verified-by-product` | `draft` | `inferred-from-code` | `disputed`
- `dispute`: null or `{raised_by, date, summary}`
- `decisions[]`: decision ids that limit it
- `implemented_by[]`: component ids
- `legacy_ids[]`: older ids such as `T3D-BR-037`
- `sources[]`: `{type (code|…), ref (SRC-nnn), title, at, code ("repo:path#Lnn@sha" or null)}`
- `open_checks[]`: verification still owed, as text
- `acceptance_criteria[]`: `{id (REQ-ID-ACn), given, when, then, status}`
- `restricted: true` marks a redacted item; its content is not in this copy.

## Decision
`id` (`DEC-001`), `title`, `status` (`open` | `on-hold` | `decided`), `question`, `context`, `options[]`, `decision` (null until decided), `capabilities[]`, `requirements[]`.

## Role
`id`, `name`, `scope` (`project` | `company` | `region` | `platform`). Ids: admin, collaborator, viewer, company-super-admin, regional-admin, support-user, custom-project-role.

## Glossary
`id`, `term`, `definition`, `status`.
