# Estate Verification and Recovery Inventory

## Objective

Create an evidence-backed, version-controlled baseline for post-change verification, configuration-drift reporting, disaster recovery, service dependencies, lifecycle status, and ghost-infrastructure review across authorized Blue Ridge repositories.

## Existing behavior

Repository-specific checks and recovery material are distributed among application, container, Tailscale-policy, and backup repositories. A central organization documentation repository already owns shared engineering and project-automation guidance, but has no estate inventory or post-change verification contract.

## Proposed behavior

Add a machine-readable inventory and a companion architecture guide to this organization repository. Add deterministic validators and a safe, opt-in verification runner that report evidence without changing production state. Link factual recovery and drift findings to review issues where a concrete gap warrants it.

## Constraints

- Record only relationships supported by repository configuration, documentation, or verified metadata.
- Do not store secrets, credentials, private addresses, token values, Tailscale state, or private service endpoints.
- Do not test through public exposure, restart services, overwrite deployed configuration, or change security boundaries.
- Keep repository-specific `AGENTS.md` guidance authoritative.

## Security considerations

Verification is read-only and opt-in. Production/network/authentication/deployment drift remains a report-and-review concern. Tests must use only declared secure paths and must never print authorization material.

## Implementation milestones

1. Collect repository and documentation evidence with read-only specialized audits.
2. Define inventory and verification schemas plus deterministic validation.
3. Publish a factual architecture/recovery/lifecycle/ghost-infrastructure baseline.
4. Validate documentation and scripts, review scope and secret safety, then open a review PR.

## Validation

Run Python syntax checks, inventory/schema validation, documentation reference checks, and `git diff --check`. Do not run production probes unless a repository explicitly declares a safe secure path and authorization exists.

## Rollback considerations

The work adds documentation and opt-in scripts only. Reverting the commit removes the framework without production impact.

## Decisions made during implementation

- Use the organization `.github` repository as the cross-repository home because it already owns shared policy and automation documentation.
- Use JSON rather than a new YAML dependency so validators work with the standard Python runtime.
- Keep endpoint targets and credentials out of the central inventory. Repositories declare their own secure verification targets.
- Treat reports, snapshots, and backup paths as historical evidence rather than desired state so drift automation cannot recommend destructive cleanup.
- Record concrete recovery and deployment-verification gaps as human-review issues instead of changing infrastructure.

## Final outcome

Added a validated architecture inventory, an opt-in read-only verification runner, drift/recovery/lifecycle documentation, and six assigned review issues for concrete gaps. No production configuration, service, route, authentication boundary, or secret was modified.
