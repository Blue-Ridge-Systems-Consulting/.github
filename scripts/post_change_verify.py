#!/usr/bin/env python3
"""Run explicitly declared, read-only post-change checks without shell evaluation."""

import argparse
import json
import socket
import subprocess
import urllib.error
import urllib.request
from pathlib import Path


def fail(check_id: str, detail: str) -> bool:
    print(f"FAIL {check_id}: {detail}")
    return False


def run_check(check: dict, allow_network: bool) -> bool:
    check_id = check.get("id", "unnamed")
    kind = check.get("type")
    if kind == "file":
        path = Path(check["path"])
        return path.exists() or fail(check_id, f"missing {path}")
    if kind == "command":
        command = check.get("argv")
        if not isinstance(command, list) or not command or not all(isinstance(x, str) for x in command):
            return fail(check_id, "argv must be a non-empty string array")
        result = subprocess.run(command, capture_output=True, text=True, timeout=check.get("timeout_seconds", 30))
        if result.returncode == 0:
            return True
        output = (result.stderr or result.stdout).strip().replace("\n", " ")[:500]
        return fail(check_id, f"exit {result.returncode}: {output}")
    if kind not in {"http", "tcp"}:
        return fail(check_id, f"unsupported check type {kind!r}")
    if not allow_network:
        return fail(check_id, "network checks require --allow-network")
    if kind == "tcp":
        try:
            with socket.create_connection((check["host"], int(check["port"])), timeout=check.get("timeout_seconds", 10)):
                return True
        except OSError as error:
            return fail(check_id, str(error))
    url = check.get("url", "")
    if not url.startswith("https://") or "@" in url or "?" in url:
        return fail(check_id, "HTTP URLs must be HTTPS without userinfo or query values")
    try:
        with urllib.request.urlopen(url, timeout=check.get("timeout_seconds", 10)) as response:
            if response.status != check.get("expect_status", 200):
                return fail(check_id, f"expected HTTP {check.get('expect_status', 200)}, got {response.status}")
            body = response.read(128 * 1024)
            keys = check.get("expect_json_keys", [])
            if keys:
                payload = json.loads(body)
                missing = [key for key in keys if key not in payload]
                if missing:
                    return fail(check_id, f"JSON keys missing: {', '.join(missing)}")
            return True
    except (OSError, ValueError, urllib.error.HTTPError) as error:
        return fail(check_id, str(error))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path, help="JSON file containing a checks array")
    parser.add_argument("--run", action="store_true", help="execute checks; default only validates and prints the plan")
    parser.add_argument("--allow-network", action="store_true", help="permit declared HTTPS/TCP probes during --run")
    args = parser.parse_args()
    data = json.loads(args.config.read_text())
    checks = data.get("checks", [])
    if not isinstance(checks, list):
        raise SystemExit("checks must be an array")
    for check in checks:
        if not isinstance(check, dict) or "id" not in check or "type" not in check:
            raise SystemExit("every check requires id and type")
    if not args.run:
        for check in checks:
            print(f"PLAN {check['id']}: {check['type']}")
        return
    results = [run_check(check, args.allow_network) for check in checks]
    passed = all(results)
    if not passed:
        raise SystemExit(1)
    print(f"PASS {len(checks)} checks")


if __name__ == "__main__":
    main()
