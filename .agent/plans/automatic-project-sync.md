# Automatic GitHub Project Sync

## Objective

Maintain the existing GitHub Projects v2 operational record for merged pull requests in both `owensreo/*` and `Blue-Ridge-Systems-Consulting/*` from one central automation.

## Existing behavior

Project reconciliation is manual. The 2026-09-26 inventory found 57 personal repositories, 16 organization repositories, 31 open user-owned Projects, no organization-owned Projects, and no existing Project-sync workflow.

## Proposed behavior

A central scheduled/manual workflow discovers recently merged pull requests in both repository-owner scopes. A deterministic registry routes work to an existing Project regardless of repository owner. The engine updates an existing item when possible, otherwise adds the merged PR or a linked issue, assigns `owensreo`, resolves the live terminal status option, and records the merge date in an existing configured date field.

## Constraints

- Full `owner/repository` identity is mandatory.
- Only merged pull requests are eligible.
- Ambiguous routing is reported for review, never guessed.
- Existing Projects remain with their current owners.
- Archived repositories and non-Blue-Ridge Projects are inventoried but excluded from automatic writes.
- The central job stays write-disabled until authentication is configured and pilot routing is approved.

## Security considerations

Existing user-owned Projects cannot currently be managed by GitHub App, GitHub App user, installation, or fine-grained tokens through GitHub's Projects REST API. The workflow therefore supports a dedicated classic token stored only as an Actions secret. It must be limited to the scopes needed for private repository issue/PR access and user Project access. The workflow has read-only `GITHUB_TOKEN` permissions; writes use only the explicit secret and are gated by `BLUE_RIDGE_PROJECT_SYNC_ENABLED=true`.

## Implementation milestones

1. Inventory both scopes and all Project schemas.
2. Commit the declarative routing registry and schema preferences.
3. Implement deterministic routing, idempotent lookup, assignment, field updates, and review reporting.
4. Add unit tests and live dry-run support.
5. Add the centrally scheduled/manual workflow with writes disabled by default.
6. Validate recent merged PRs from both owners.
7. Pilot one approved item, rerun it, then enable the schedule.

## Validation

- Python unit tests cover routing precedence, ambiguity, merge gating, and existing-item reuse.
- JSON and workflow syntax are checked.
- Live dry-runs cover merged PRs from both scopes.
- A later approved pilot must prove assignment, status/date update, and idempotent rerun before scheduled writes are enabled.

## Rollback considerations

Set `BLUE_RIDGE_PROJECT_SYNC_ENABLED=false` (or remove it) to stop scheduled writes. The workflow does not delete Project items, issues, PRs, fields, Projects, or repositories. Removing the workflow and registry reverts automation without changing historical Project records.

## Decisions made during implementation

- Use the existing organization `.github` repository as the central home.
- Use polling instead of dozens of event callers, keeping repository-local changes at zero.
- Keep Project ownership independent of repository ownership.
- Resolve field and option IDs live from configured names.
- Treat Projects 31 and 32 as non-Blue-Ridge exceptions because they represent `lawyerdr-bit/DL`, outside both requested repository scopes.

## Final outcome

The central registry, sync engine, tests, gated workflow, operating guide, and dated inventory are implemented. Live dry-runs covered both repository-owner scopes. A live organization-repository pilot created one Project item and its replay updated the same item; a personal-repository pilot updated an existing item. Both pilots assigned `owensreo` and set the configured terminal Status and merge date. Scheduled writes remain disabled pending protected PR review/landing and manual secret/variable configuration.
