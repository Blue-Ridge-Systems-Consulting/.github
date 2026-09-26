# Blue Ridge Project Sync

Blue Ridge Project Sync centrally maintains existing GitHub Projects v2 for merged pull requests in both supported repository-owner scopes:

- `owensreo/*`
- `Blue-Ridge-Systems-Consulting/*`

Project ownership is independent of repository ownership. The live 2026-09-26 inventory found 31 open Projects owned by `owensreo` and no Projects owned by `Blue-Ridge-Systems-Consulting`; the registry therefore preserves the existing user-owned Projects and can support organization-owned destinations later without moving or recreating anything.

## Live status

Project Sync is deployed and enabled. Activation PR [#3](https://github.com/Blue-Ridge-Systems-Consulting/.github/pull/3) merged on 2026-09-26 and the tracked activation flag is `true` on `main`.

The first authenticated write-mode Actions run, [36221849895](https://github.com/Blue-Ridge-Systems-Consulting/.github/actions/runs/36221849895), completed successfully. It processed the merged activation PR itself, routed `Blue-Ridge-Systems-Consulting/.github#3` to `owensreo` Project #24, Nexus Operations, assigned `owensreo`, set `Completed`, and recorded `2026-09-26` as the completion date. This confirms the deployed secret, cross-scope routing, native assignment, Project update, and date-update path.

## Lifecycle

The central workflow polls recently merged pull requests from both scopes. It rejects open PRs and closed-unmerged PRs. For each merged PR it:

1. Searches configured destination Projects for the PR and linked issues.
2. Routes by existing membership, explicit override, exact `OWNER/REPOSITORY`, linked-issue membership, labels, changed paths, then title/body keywords.
3. Stops with `routing-review` if the result is ambiguous.
4. Reuses an existing item when its content, references, or unique normalized title match.
5. Otherwise adds the first linked closing issue, or the merged PR when no issue is linked.
6. Uses native issue/PR assignment for `owensreo`.
7. Resolves the live configured completed Status option by name.
8. Writes the actual merge date to the first matching existing configured date field.

The registry is `.github/project-sync/routes.json`. It stores stable owner, project number, titles, repository mappings, routing signals, and field/option names. Live numeric/node IDs are discovered on every run.

## Authentication

GitHub's current user-owned Projects REST endpoints do not accept GitHub App user tokens, GitHub App installation tokens, or fine-grained personal access tokens. Because every currently relevant Project is user-owned, configure a dedicated classic token as the repository Actions secret `BLUE_RIDGE_PROJECT_SYNC_TOKEN`.

Required classic scopes for the current private cross-scope inventory:

- `project` — read and update user-owned Projects v2.
- `repo` — read merged PRs/issues in private repositories and assign their native issue/PR records.

Do not reuse an interactive admin token. Do not grant `admin:org`, `workflow`, package, delete, or other unrelated scopes. If the Projects are later moved or new destinations are created under the organization, a GitHub App with organization Projects write and repository Issues/Pull requests write can be evaluated for those organization-owned destinations; it cannot replace the classic token while user-owned Projects remain in scope.

## Safe rollout

Writes are fail-closed behind both controls:

- Actions secret `BLUE_RIDGE_PROJECT_SYNC_TOKEN`
- tracked `.github/project-sync/activation.json` with `scheduled_writes_enabled: true`

Manual dispatch defaults to dry-run. Keep the activation file absent or set its value to `false` while reviewing dry-run routing. Then select one merged PR, dispatch with `write=true`, verify the assignment/status/date, and dispatch the same PR again to prove `update-existing` instead of duplicate creation. Enabling or disabling scheduled writes is a normal reviewed PR change.

The schedule runs at minutes 17 and 47 and searches the prior two hours, intentionally overlapping runs. Idempotent lookup makes overlap safe and covers delayed workflow starts.

## Local validation

With an authenticated `gh` CLI:

```bash
python3 -m unittest .github/project-sync/test_project_sync.py
python3 .github/project-sync/project_sync.py --repository OWNER/REPOSITORY --pr NUMBER
python3 .github/project-sync/project_sync.py --recent-hours 48
```

Omit `--write` for every dry-run. A write requires explicit `--write` and appropriately scoped authentication.

## Exceptions

- Archived repositories remain inventoried but are not scheduled rollout targets.
- Projects 31 and 32 represent `lawyerdr-bit/DL`, outside the two requested repository-owner scopes, and are excluded.
- Repositories without a confident route are reported for routing review.
- A Project without a configured existing date field still receives assignment and Status during a write, but reports the missing date field for schema review; the engine does not create redundant fields automatically.
