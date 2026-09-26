# Blue Ridge GitHub Project Sync inventory

Inventory date: 2026-09-26 (America/New_York)

## Accounts and repositories

| Scope | Repositories | Archived | Active |
| --- | ---: | ---: | ---: |
| `owensreo` | 57 | 2 | 55 |
| `Blue-Ridge-Systems-Consulting` | 16 | 1 | 15 |
| Total | 73 | 3 | 70 |

The repository audit found 216 workflows across 58 repositories, default-branch protection on 49 repositories, signing requirements on 48, and Blue Ridge Codex engineering configuration on 57. The other 24 default branches returned no direct branch protection; no repository rulesets were visible to the audit credential. No existing automatic Project-sync implementation was found. Existing CI, protections, signing, deployments, and Codex files were not changed during inventory.

## Projects

GitHub reported 31 open user-owned Projects and zero organization-owned Projects. The organization repositories therefore legitimately route to existing Projects owned by `owensreo` where configured.

| Owner | # | Project | Registry scope |
| --- | ---: | --- | --- |
| `owensreo` | 2 | Blue Ridge Nexus Container Lifecycle | `nexus-container-lifecycle` |
| `owensreo` | 3 | Blue Ridge Tailscale Operations Roadmap | `tailscale-operations` |
| `owensreo` | 4 | Blue Ridge Systems Consulting | `blue-ridge-site` |
| `owensreo` | 5 | Schedule an Intro Call | `intro-call` |
| `owensreo` | 6 | Nexus Login | `nexus-login` |
| `owensreo` | 7 | Blue Ridge Nexus | `nexus-site` |
| `owensreo` | 8 | Ray Owens | `ray-owens` |
| `owensreo` | 9 | Nexus Central | `nexus-central` |
| `owensreo` | 10 | Blue Ridge Systems Book | `book` |
| `owensreo` | 11 | Blue Ridge Signing | `signing` |
| `owensreo` | 12 | Ray Owens Resume | `resume` |
| `owensreo` | 13 | Cloudflare Policy Dashboard | `cloudflare-policy-dashboard` |
| `owensreo` | 14 | Tailscale Interactive Dashboard | `tailscale-dashboard` |
| `owensreo` | 15 | R2 Backup Dashboard | `r2-backup-dashboard` |
| `owensreo` | 16 | Blue Ridge Nexus MCP | `nexus-mcp` |
| `owensreo` | 17 | Nexus Intelligence | `nexus-intelligence` |
| `owensreo` | 18 | Blue Ridge Frappe | `frappe` |
| `owensreo` | 19 | Nexus Preview Analytics | `preview-analytics` |
| `owensreo` | 20 | Blue Ridge AI Chat | `ai-chat` |
| `owensreo` | 21 | MeshCentral | `meshcentral` |
| `owensreo` | 22 | Nexus Container Services | `container-services` |
| `owensreo` | 23 | Nexus ARM | `nexus-arm` |
| `owensreo` | 24 | Nexus Operations | `nexus-operations` |
| `owensreo` | 25 | Blue Ridge Ticketing | `ticketing` |
| `owensreo` | 26 | ISP Trend Analytics | `isp-trend-analytics` |
| `owensreo` | 27 | Website Analytics | `website-analytics` |
| `owensreo` | 28 | Nexus Insights | `nexus-insights` |
| `owensreo` | 29 | Firewall Analytics | `firewall-analytics` |
| `owensreo` | 30 | Blue Ridge Cloudflare Infrastructure | `cloudflare-infrastructure` |
| `owensreo` | 31 | Dan DL Systems Toolkit | Excluded: `lawyerdr-bit/DL` |
| `owensreo` | 32 | Dan Network and Container Operations | Excluded: `lawyerdr-bit/DL` |

The 31 Projects contained 303 items at inventory time. All have a Status field and Repository source field. Terminal status option names vary by schema: `Done`, `Completed`, and `Foundation Complete`. Nine Projects had an existing `Evidence date` date field; the remaining Projects had no date field. The engine resolves all field and option IDs live and reports missing date fields without creating schema automatically.

## Rollout evidence

Read-only dry-runs:

- `owensreo/blue-ridge-frappe#11` routed to `owensreo` Project #18, Blue Ridge Frappe.
- `Blue-Ridge-Systems-Consulting/blue-ridge-container-images#4` routed to `owensreo` Project #2, Blue Ridge Nexus Container Lifecycle.
- `owensreo/tailscale-policy#40` found and reused its existing Project #3 item.

Live pilots:

- Organization repository: `Blue-Ridge-Systems-Consulting/blue-ridge-container-images#4` was assigned to `owensreo`, added to Project #2, set to `Done`, and dated `2026-09-26`. Replays reused item `PVTI_lAHOCt4J584BgNnLzg83xkA`.
- Personal repository: existing item `PVTI_lAHOCt4J584BgNskzg2WI6w` for `owensreo/tailscale-policy#40` was assigned to `owensreo`, set to `Foundation Complete`, and dated `2026-08-19` without creating a duplicate.

Scheduled writes remain disabled until the documented Actions secret and enable variable are configured after the implementation PR is merged.
