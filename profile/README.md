<div align="center">

<a href="https://blueridgesystems.us">
  <img src="assets/blue-ridge-systems-consulting-logo.svg" alt="Blue Ridge Systems Consulting" width="700" />
</a>

# Blue Ridge Systems Consulting

### Practical infrastructure. Secure connectivity. Automation that earns its keep.

[![Website](https://img.shields.io/badge/Visit-Website-2563EB?style=for-the-badge&logo=googlechrome&logoColor=white)](https://blueridgesystems.us)
[![Schedule an Intro Call](https://img.shields.io/badge/Schedule-Intro%20Call-0891B2?style=for-the-badge&logo=googlecalendar&logoColor=white)](https://meet.blueridgesystems.us)
[![Blue Ridge Nexus](https://img.shields.io/badge/Explore-Blue%20Ridge%20Nexus-7C3AED?style=for-the-badge&logo=github&logoColor=white)](https://nexus.blueridgesystems.us)

*Infrastructure engineering and IT consulting for the Upstate of South Carolina.*

</div>

---

## About Blue Ridge

Blue Ridge Systems Consulting is a focused infrastructure engineering and IT consulting organization. We design, modernize, and operate practical systems for organizations that value reliability, security, and clarity.

Our approach is deliberately straightforward: understand the work, make the system maintainable, improve visibility, and add automation where it genuinely reduces operational burden. The goal is useful engineering—not unnecessary complexity.

## What We Build

<table>
<tr>
<td width="33%" valign="top">

### Infrastructure

Enterprise Linux, Windows Server, Active Directory, ARM and x86 hosts, virtualization, and OCI containers—built for steady day-to-day operation.

</td>
<td width="33%" valign="top">

### Connectivity &amp; Security

Tailscale, Cloudflare Zero Trust, secure remote access, private networking, and policy-driven infrastructure that keeps access intentional.

</td>
<td width="33%" valign="top">

### Automation &amp; Operations

GitHub Actions, systemd, rootless Podman, monitoring, analytics, operational dashboards, and AI-assisted reporting for repeatable work.

</td>
</tr>
</table>

## Technology Stack

<div align="center">

[![Enterprise Linux](https://img.shields.io/badge/Enterprise-Linux-10B981?style=for-the-badge&logo=linux&logoColor=white)](https://www.redhat.com/en/technologies/linux-platforms/enterprise-linux)
[![Rocky Linux](https://img.shields.io/badge/Rocky-Linux-10B981?style=for-the-badge&logo=rockylinux&logoColor=white)](https://rockylinux.org/)
[![AlmaLinux](https://img.shields.io/badge/Alma-Linux-000000?style=for-the-badge&logo=almalinux&logoColor=white)](https://almalinux.org/)
[![Fedora](https://img.shields.io/badge/Fedora-51A2DA?style=for-the-badge&logo=fedora&logoColor=white)](https://fedoraproject.org/)

[![Windows Server](https://img.shields.io/badge/Windows-Server-0078D4?style=for-the-badge&logo=windows&logoColor=white)](https://www.microsoft.com/windows-server)
[![macOS](https://img.shields.io/badge/macOS-000000?style=for-the-badge&logo=apple&logoColor=white)](https://www.apple.com/macos/)
[![Microsoft 365](https://img.shields.io/badge/Microsoft-365-D83B01?style=for-the-badge&logo=microsoft365&logoColor=white)](https://www.microsoft.com/microsoft-365)
[![PowerShell](https://img.shields.io/badge/PowerShell-5391FE?style=for-the-badge&logo=powershell&logoColor=white)](https://learn.microsoft.com/powershell/)

[![Podman](https://img.shields.io/badge/Rootless-Podman-892CA0?style=for-the-badge&logo=podman&logoColor=white)](https://podman.io/)
[![Tailscale](https://img.shields.io/badge/Tailscale-111111?style=for-the-badge&logo=tailscale&logoColor=white)](https://tailscale.com/)
[![Cloudflare](https://img.shields.io/badge/Cloudflare-Zero%20Trust-F38020?style=for-the-badge&logo=cloudflare&logoColor=white)](https://www.cloudflare.com/zero-trust/)
[![GitHub Actions](https://img.shields.io/badge/GitHub-Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)](https://github.com/features/actions)

</div>

## Blue Ridge Nexus

[Blue Ridge Nexus](https://nexus.blueridgesystems.us) is the operational and platform-engineering ecosystem developed by Blue Ridge Systems Consulting. It brings together the patterns, tooling, and practical experience behind secure remote operations, infrastructure automation, systems visibility, and local-first AI integration.

Nexus is built around a simple principle: operational systems should be understandable by the people who maintain them.

The public utilities and OCI experimentation images below are intentionally separate from private deployment configuration and operational topology.

## Projects &amp; Platforms

<table>
<tr>
<td width="33%" valign="top">

### [Northstar Guard](https://github.com/Blue-Ridge-Systems-Consulting/northstar-guard-public)

**Local-first security monitoring** for macOS, Fedora COSMIC, headless Linux, and Windows. Northstar Guard explains focused findings and leaves remediation decisions with the operator.

[Explore Northstar Guard →](https://github.com/Blue-Ridge-Systems-Consulting/northstar-guard-public)

</td>
<td width="33%" valign="top">

### [Windows Maintenance](https://github.com/Blue-Ridge-Systems-Consulting/blue-ridge-windows-maintenance)

**Inspectable PowerShell operations tooling** for diagnostics, cautious maintenance, domain and server health, and security checks—built around diagnose, repair, then verify.

[Explore the toolkit →](https://github.com/Blue-Ridge-Systems-Consulting/blue-ridge-windows-maintenance)

</td>
<td width="33%" valign="top">

### [Raspberry Pi 5 Utilities](https://github.com/Blue-Ridge-Systems-Consulting/raspberry-pi-5)

**Linux and ARM utility scripts** for lightweight malware scanning with systemd scheduling and persistent USB NIC names on small infrastructure hosts.

[Explore the utilities →](https://github.com/Blue-Ridge-Systems-Consulting/raspberry-pi-5)

</td>
</tr>
</table>

The organization also publishes focused [macOS tuning scripts](https://github.com/Blue-Ridge-Systems-Consulting/MacOS-Scripts) that save a before-state and restore path before changing system preferences.

## Containers &amp; Packages

Public OCI images for AI experimentation, exploration, local prototyping, and learning are cataloged in [Blue Ridge Systems Container Images](https://github.com/Blue-Ridge-Systems-Consulting/blue-ridge-container-images). The current public packages use the `blue-ridge-public` tag; review the catalog and upstream licenses before use.

| Image | Public GHCR identifier | Purpose &amp; documentation |
| --- | --- | --- |
| [`reo-ai`](https://github.com/orgs/Blue-Ridge-Systems-Consulting/packages/container/package/reo-ai) | `ghcr.io/blue-ridge-systems-consulting/reo-ai:blue-ridge-public` | General-use OCI catalog image for AI experimentation and local prototyping. |
| [`reo-tools`](https://github.com/orgs/Blue-Ridge-Systems-Consulting/packages/container/package/reo-tools) | `ghcr.io/blue-ridge-systems-consulting/reo-tools:blue-ridge-public` | General-use OCI catalog image for experimentation and exploration. |
| [`olmoai`](https://github.com/orgs/Blue-Ridge-Systems-Consulting/packages/container/package/olmoai) | `ghcr.io/blue-ridge-systems-consulting/olmoai:blue-ridge-public` | General-use OCI catalog image for AI experimentation and learning. |

See the [container catalog](https://github.com/Blue-Ridge-Systems-Consulting/blue-ridge-container-images) for usage guidance and responsible-use boundaries.

## Open Source &amp; Public Engineering

Blue Ridge publishes focused utilities, monitor-only safety tooling, and container starting points that can be inspected and used responsibly. Public repositories document their own scope, safeguards, and support boundaries; private deployment configuration, credentials, and operational details remain private.

## Founded by [Ray Owens](https://github.com/owensreo)

Blue Ridge Systems Consulting is an independent engineering organization serving the Upstate of South Carolina.

---

<div align="center">

### Blue Ridge Systems Consulting

Upstate South Carolina  ·  [Website](https://blueridgesystems.us)  ·  [Schedule an Intro Call](https://meet.blueridgesystems.us)  ·  [Blue Ridge Nexus](https://nexus.blueridgesystems.us)

</div>
