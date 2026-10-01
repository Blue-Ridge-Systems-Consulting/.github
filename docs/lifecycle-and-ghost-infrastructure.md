# Lifecycle and ghost-infrastructure review

The machine-readable lifecycle classification is in `config/blue-ridge-architecture.json`. It covers all 74 authorized repositories and uses `ACTIVE`, `MAINTENANCE`, `EXPERIMENTAL`, `SUPERSEDED` retained history, or `UNKNOWN`.

`SUPERSEDED` means archived or explicitly history-preserving; it does not authorize archival or deletion. `UNKNOWN` deliberately avoids guessing from commit age alone.

## Strongly evidenced retained-history relationships

- The archived personal microsite repositories have organization copies explicitly described as history-preserving. Preserve both until references and deployment ownership are reviewed.
- `new-nexus-firebat` explicitly identifies its Frappe artifacts as legacy reference material; `blue-ridge-frappe` is the current Frappe source. This is EXPECTED DRIFT and recovery evidence, not a removal candidate.
- `blue-ridge-nexus-pi` snapshot directories and historical reports are recovery/reference evidence, never live desired state.

## Ghost-infrastructure findings

| Reference | Location | Classification | Evidence and next action |
| --- | --- | --- | --- |
| Tailscale device aliases differ from last report | `tailscale-policy/devices.json` | CONFIGURATION DRIFT / UNKNOWN | The file records intended-vs-last-report aliases. Compare through an approved read-only Tailscale path before any correction. |
| Historical container/port values | reports and snapshot directories | EXPECTED DRIFT | These are historical observations. Exclude them from deletion or live drift comparisons. |
| Mixed cockpit target addresses | `new-nexus-firebat` operations host configuration | UNKNOWN | Some dependencies may be intentionally LAN-bound. Trace approved policy and callers before changing names or addresses. |
| MeshCentral backup ZIP artifacts despite exclusion documentation | `blue-ridge-nexus-pi` snapshot paths | SECURITY-RELEVANT / UNKNOWN | Possible runtime-data exposure. Human review is tracked in issue #10; do not inspect contents or delete automatically. |

Before fixing an unexpected reference, establish whether it is broken, intentional, depended upon, and observable; identify the smallest safe correction and a recurrence check.
