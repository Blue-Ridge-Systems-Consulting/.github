# Disaster recovery baseline

This is a source-and-documentation audit, not a restore test. It records recovery confidence and missing evidence without accessing secret values or changing hosts.

| Service | Source and configuration | Persistent data / backup | Restore procedure | Confidence |
| --- | --- | --- | --- | --- |
| Libvirt exit-node VMs | `owensreo/vm-backups` scripts, XML, metadata, manifests, checksums | qcow2 assets in private GitHub Releases and host payload repositories | `restore-vm.sh --verify-only` validates archive and image before host change | High, pending compatible-host rehearsal |
| Nexus staging databases | `tailscale-policy` scheduled backup workflow | encrypted MariaDB, MongoDB, and Redis objects in R2 | approved restore procedure is referenced but not versioned | Partial; issue #292 |
| Frappe CRM/ERP | `blue-ridge-frappe` stack and fixed identities | database backups are partial; site/log/Redis volumes and runtime environment are not established in the recovery path | no complete host-loss runbook | Partial; issue #292 |
| Nexus ARM services | `new-nexus-arm` catalog, user units, snapshot tooling | local snapshots; off-host replication documented disabled | no documented full restore rehearsal | Partial; issue `new-nexus-arm#20` |
| Preview analytics | source, Containerfile, user unit, loopback health | host-local SQLite | no documented data backup/restore | Service-only; issue #14 |
| Nexus MCP | Worker source and telemetry documentation | D1 authoritative; export/retention evidence absent | Git rollback does not restore D1 | Service-only; issue #83 |
| Cloudflare Zero Trust | Terraform and remote state backup | selected resources represented in Terraform | manual Pages/tunnel/dashboard-owned resources remain external | Partial, expected ownership boundary |

Recovery work must inventory source, image, configuration, persistent data, network dependencies, authentication prerequisites, backup retention, and a non-destructive verification method before claiming host-loss recovery.

## Documentation validation performed

The audit confirmed that the core recovery-script paths named by `vm-backups`, `staging-host-vm-backups`, `new-nexus-arm`, `new-nexus-firebat`, and `nexus-preview-analytics` currently exist. Shell syntax and Python compilation passed for the `vm-backups` backup/restore tooling. No large asset download or destructive restore was run.
