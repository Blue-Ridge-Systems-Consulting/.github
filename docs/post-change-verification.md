# Post-change verification framework

CI success verifies a workflow execution. This framework adds service evidence after merge or deployment without changing production state.

## Standard

Each repository that deploys a service should declare a small JSON check file and run it only from an already approved path. Checks are deterministic and read-only:

- `file`: required generated files, unit files, manifests, or release artifacts exist.
- `command`: an explicit argument array runs an existing repository verifier. Shell evaluation is not supported.
- `http`: an HTTPS health or schema endpoint returns the declared status and optional JSON keys.
- `tcp`: a declared secure host and port is reachable.

`scripts/post_change_verify.py` validates plans by default. `--run` executes checks; network calls require the separate `--allow-network` gate. It refuses HTTP URLs, query strings, userinfo, custom headers, and shell commands. It never restarts workloads or logs response bodies, tokens, or credentials.

Example repository-local check file:

```json
{
  "checks": [
    {"id": "service-unit", "type": "file", "path": "systemd/example.service"},
    {"id": "local-health", "type": "command", "argv": ["./healthcheck-now.sh"]}
  ]
}
```

Run the plan with `python3 scripts/post_change_verify.py verification/targets.json`. `config/post-change-verification.example.json` is a non-networked example that validates this inventory. Add `--run` only in the existing trusted deployment context. Add `--allow-network` only for declared secure endpoints.

## Current coverage

| Repository | Existing post-change evidence | Status |
| --- | --- | --- |
| `owensreo/blue-ridge-nexus-mcp` | bounded routing, status/schema, D1, and expected-401 verification | Implemented |
| `owensreo/nexus-preview-analytics` | loopback health script and container health check | Implemented |
| `owensreo/vm-backups` | release/checksum/qemu-image `--verify-only` preflight | Implemented for recovery assets |
| `owensreo/blue-ridge-writing` | D1 health handler | Service-specific evidence exists |
| `owensreo/netgear-router-configs` | published report/checksum verifier | Implemented for artifact publication |
| `owensreo/career-ops` | report/data link verifiers | Implemented for pipeline artifacts |
| `owensreo/tailscale-policy` | secure post-deploy inventory collection, but no assertions | Needs review; issue #293 |
| GitHub Pages deployment repositories | deployment succeeds without declared reachability/content marker | Needs repository-specific safe probes |
| Cloudflare Zero Trust Terraform | plan/protected-resource validation without full live readback | Human review required |

Do not add generic public probes to private services. Use loopback, existing Tailscale paths, existing self-hosted runners, or already-public Pages URLs with a harmless expected marker.

## Failure diagnostics

The runner prints check identity, expected versus observed status, missing JSON keys, connection error, or explicit command exit detail. It truncates command diagnostics and does not print HTTP bodies. Failures are evidence for investigation; no automatic restart, rollback, or configuration overwrite is permitted.
