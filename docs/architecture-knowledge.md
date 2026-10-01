# Blue Ridge architecture knowledge

`config/blue-ridge-architecture.json` is the machine-readable source for this document. It records only repository-backed facts last reviewed on 2026-10-01.

## Major systems

| System | Source of truth | Runtime and dependencies | Recovery confidence |
| --- | --- | --- | --- |
| Private fleet control | `owensreo/tailscale-policy` | Tailscale policy/DNS, runner inventory, private SSH deployment | Partial; runtime identities are external |
| Nexus x86 and ARM containers | `blue-ridge-nexus-containers`, `blue-ridge-nexus-arm-containers` | Rootless Podman, user systemd, GHCR, Tailscale-controlled deployment | Incomplete; volumes and environment data are external |
| Preview analytics | `nexus-preview-analytics` | Rootless Podman, user systemd, local SQLite | Service rebuild only |
| Cloudflare data plane | `blue-ridge-cloudflare-os`, `cloudflare-zero-trust-policy` | Workers, D1, selected Terraform-managed Cloudflare configuration | Partial; some dashboard-managed and manual resources remain external |
| Nexus MCP | `blue-ridge-nexus-mcp` | Cloudflare Worker, D1 telemetry, OAuth KV | Service rebuild only |
| VM recovery | `vm-backups` | libvirt XML/manifests in Git; qcow2 assets in private Releases | Documented, with verify-only preflight |
| Project work tracking | `Blue-Ridge-Systems-Consulting/.github` | GitHub Actions and existing user-owned Projects | Requires separately managed GitHub authentication |

## Security and networking boundaries

- Tailscale is the private fleet control and deployment boundary. Do not publish internal services to make verification easier.
- Cloudflare Access, Turnstile, Worker authentication, tunnels, and protected ingestion boundaries remain intact during tests. A valid check can prove a rejection boundary such as an expected unauthenticated `401`; it must not bypass it.
- Rootless Podman and user-systemd deployment remain the container convention. Runtime environments, named volumes, secrets, and Tailscale state are deliberately excluded from source repositories.
- Terraform represents selected Cloudflare configuration only. Pages, some tunnel hostname configuration, and dashboard-managed resources have separately documented ownership.

## GitHub and AI conventions

- GitHub Actions use repository-local policy, protected branches, signed commits where configured, and narrowly scoped pull requests.
- The organization `.github` repository contains the Project Sync implementation. It routes merged work to existing user-owned Projects through a dedicated, least-privileged secret.
- Existing configured inference providers and local models remain preferred. Do not add metered OpenAI API use without explicit instruction.

## Keeping this synchronized

For an architecture change, update the JSON inventory in the same reviewable change as the source configuration. Run `python3 scripts/validate_architecture_inventory.py`, review that every new relationship has an evidence path, and classify affected recovery/drift impact. A merged infrastructure change should also declare or update its repository-local post-change checks.

## DO NOT ASSUME

- A successful Actions run, image build, or Terraform apply proves service health.
- A historical snapshot, report, or backup is current desired state or safe to delete.
- Runtime data, credentials, volume data, or secrets are recoverable merely because the application source is present.
- Repository age proves retirement. Retained-history repositories may still support recovery, documentation, or active deployment references.
- Tailscale, Cloudflare, firewall, DNS, authentication, or deployment boundaries may be changed without explicit instruction and human review.
