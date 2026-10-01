# Configuration drift detection

Drift detection compares committed desired state with read-only observations. It reports differences; it never applies configuration to production.

## Classification

| Class | Meaning | Response |
| --- | --- | --- |
| EXPECTED DRIFT | Documented difference outside the desired-state owner | Record owner and preserve boundary |
| BENIGN DRIFT | Runtime identity, timestamps, metrics, caches, generated reports | Exclude from alarms |
| CONFIGURATION DRIFT | Committed desired state differs from a declared runtime observation | Create diagnostic report and review |
| SECURITY-RELEVANT DRIFT | Difference affects authentication, access, routes, ports, identity, permissions, DNS, or credentials | Stop at report and require human review |
| UNKNOWN | Observation or ownership is incomplete | Gather approved evidence; do not infer correction |

## Current compare surfaces

- `tailscale-policy`: committed deployment plan versus its existing secure post-deploy Podman inspect/info collection. Candidate assertions are service count, selected image identity, running state, health, and unexpected services. This is review-first because it touches deployment automation.
- Nexus Quadlets/Containerfiles: committed units versus host-local systemd/Podman state acquired only through an existing secure runner path.
- `cloudflare-zero-trust-policy`: Terraform desired state versus read-only Cloudflare configuration. Authentication, tunnel, Access, route, and DNS observations are security-relevant.
- GitHub runner configuration: labels, installed versions, and runner service state are UNKNOWN until collected from existing self-hosted runner paths.

Do not use `reports/`, `snapshots/`, `container-backup/`, or `*.bak*` as desired state. They are historical evidence and can legitimately differ from live services.

## Deterministic process

1. Extract expected values from committed Quadlets, Containerfiles, systemd units, Terraform, or workflow plans.
2. Collect read-only observations through the already approved control path.
3. Normalize volatile fields such as IDs, timestamps, metrics, cache paths, and generated artifacts.
4. Classify each remaining difference with owner, evidence, and dependency impact.
5. Open or update a deduplicated issue for concrete drift. Security-relevant drift stops for human review.
