#!/usr/bin/env python3
"""Validate the version-controlled Blue Ridge architecture inventory offline."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "config" / "blue-ridge-architecture.json"
VERIFICATION = ROOT / "config" / "post-change-verification.json"


def fail(message: str) -> None:
    raise SystemExit(f"inventory validation failed: {message}")


def load(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        fail(f"{path}: {error}")


def main() -> None:
    inventory = load(INVENTORY)
    verification = load(VERIFICATION)
    if inventory.get("schema_version") != 1:
        fail("unsupported architecture schema version")
    if verification.get("schema_version") != 1:
        fail("unsupported verification schema version")

    services = inventory.get("services")
    if not isinstance(services, list) or not services:
        fail("services must be a non-empty list")
    service_ids = [item.get("id") for item in services]
    if any(not isinstance(item, str) or not item for item in service_ids):
        fail("every service requires a non-empty id")
    if len(service_ids) != len(set(service_ids)):
        fail("service ids must be unique")
    for item in services:
        for key in ("source", "configuration", "persistent_data", "recovery", "evidence"):
            if key not in item:
                fail(f"service {item['id']} is missing {key}")

    lifecycle = inventory.get("lifecycle", {})
    allowed = {"active", "maintenance", "experimental", "superseded_retained_history", "unknown"}
    if set(lifecycle) != allowed:
        fail("lifecycle classifications do not match the supported set")
    repositories = [repo for values in lifecycle.values() for repo in values]
    if len(repositories) != len(set(repositories)):
        fail("a repository appears in multiple lifecycle classifications")
    if any("/" not in repo for repo in repositories):
        fail("repository names must use OWNER/REPOSITORY form")

    check_types = set(verification.get("check_types", []))
    if check_types != {"file", "command", "http", "tcp"}:
        fail("verification check types changed without validator review")
    print(f"validated {len(services)} services and {len(repositories)} repository lifecycle records")


if __name__ == "__main__":
    main()
