# Blue Ridge Codex engineering layer

Repository-local `AGENTS.md` is authoritative. Codex is used interactively through the existing ChatGPT/Codex access and follows those repository instructions.

This engineering layer does not invoke Codex from GitHub Actions, call a metered OpenAI API, or require an OpenAI API credential. Existing repository CI remains responsible for tests, linting, builds, and security validation. GitHub branch rules and native auto-merge may merge an eligible PR only after required checks pass.

The operating principle is: Codex proposes when explicitly invoked, CI proves, GitHub records and may merge eligible low-risk work, and humans control security, infrastructure, architecture, credentials, permissions, and ambiguous changes.

Changes to `AGENTS.md`, `.agent/**`, `.github/workflows/**`, and `CODEOWNERS` always require human review.
