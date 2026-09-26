#!/usr/bin/env python3
"""Idempotently route merged Blue Ridge pull requests into GitHub Projects v2."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


API_VERSION = "2026-03-10"
PROJECT_MARKER = re.compile(
    r"(?im)^Project-Sync-Project:\s*([A-Za-z0-9_.-]+)#(\d+)\s*$"
)
CLOSING_ISSUE = re.compile(
    r"(?i)\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+"
    r"(?:(https://github\.com/[^/\s]+/[^/\s]+/issues/(\d+))|#(\d+))"
)


class ApiError(RuntimeError):
    pass


class GitHub:
    def __init__(self, token: str | None = None) -> None:
        self.env = os.environ.copy()
        if token:
            self.env["GH_TOKEN"] = token

    def api(
        self,
        path: str,
        *,
        method: str = "GET",
        body: dict[str, Any] | None = None,
        paginate: bool = False,
    ) -> Any:
        command = [
            "gh",
            "api",
            "-H",
            f"X-GitHub-Api-Version: {API_VERSION}",
            "-H",
            "Accept: application/vnd.github+json",
        ]
        if paginate:
            command.append("--paginate")
        if method != "GET":
            command.extend(["--method", method])
        if body is not None:
            command.extend(["--input", "-"])
        command.append(path)
        completed = subprocess.run(
            command,
            input=json.dumps(body) if body is not None else None,
            text=True,
            capture_output=True,
            env=self.env,
            check=False,
        )
        if completed.returncode:
            raise ApiError(f"GitHub API {method} {path} failed: {completed.stderr.strip()}")
        if not completed.stdout.strip():
            return None
        if paginate:
            decoder = json.JSONDecoder()
            text = completed.stdout.lstrip()
            pages: list[Any] = []
            while text:
                value, index = decoder.raw_decode(text)
                pages.append(value)
                text = text[index:].lstrip()
            if all(isinstance(page, list) for page in pages):
                return [item for page in pages for item in page]
            return pages
        return json.loads(completed.stdout)


@dataclass(frozen=True)
class RouteResult:
    project: dict[str, Any] | None
    signal: str
    candidates: tuple[str, ...] = ()


def load_registry(path: Path) -> dict[str, Any]:
    registry = json.loads(path.read_text(encoding="utf-8"))
    if registry.get("version") != 1:
        raise ValueError("unsupported routing registry version")
    owners = registry.get("repository_owners", [])
    if len(owners) != len(set(owners)) or not owners:
        raise ValueError("repository_owners must be a non-empty unique list")
    project_keys = [project["key"] for project in registry.get("projects", [])]
    if len(project_keys) != len(set(project_keys)):
        raise ValueError("project keys must be unique")
    return registry


def normalize(value: str | None) -> str:
    return " ".join((value or "").casefold().split())


def explicit_override(pr: dict[str, Any], registry: dict[str, Any]) -> tuple[str, int] | None:
    repo = pr["repository_url"].removeprefix("https://api.github.com/repos/")
    configured = registry.get("explicit_overrides", {}).get(repo)
    if configured:
        owner, number = configured.rsplit("#", 1)
        return owner, int(number)
    match = PROJECT_MARKER.search(pr.get("body") or "")
    return (match.group(1), int(match.group(2))) if match else None


def project_identity(project: dict[str, Any]) -> tuple[str, int]:
    return project["owner"], int(project["number"])


def route_pr(
    pr: dict[str, Any],
    registry: dict[str, Any],
    *,
    membership_projects: Iterable[tuple[str, int]] = (),
    linked_issue_projects: Iterable[tuple[str, int]] = (),
    changed_paths: Iterable[str] = (),
) -> RouteResult:
    projects = registry["projects"]
    by_identity = {project_identity(project): project for project in projects}

    memberships = [by_identity[key] for key in membership_projects if key in by_identity]
    if len(memberships) == 1:
        return RouteResult(memberships[0], "existing-project-membership")
    if len(memberships) > 1:
        return RouteResult(None, "routing-review", tuple(item["key"] for item in memberships))

    override = explicit_override(pr, registry)
    if override:
        project = by_identity.get(override)
        if project:
            return RouteResult(project, "explicit-override")
        return RouteResult(None, "invalid-explicit-override", (f"{override[0]}#{override[1]}",))

    repo = pr["repository_url"].removeprefix("https://api.github.com/repos/")
    repo_matches = [project for project in projects if repo in project.get("repositories", [])]
    if len(repo_matches) == 1:
        return RouteResult(repo_matches[0], "repository")

    issue_matches = [by_identity[key] for key in linked_issue_projects if key in by_identity]
    if len(issue_matches) == 1:
        return RouteResult(issue_matches[0], "linked-issue-membership")
    if len(issue_matches) > 1:
        return RouteResult(None, "routing-review", tuple(item["key"] for item in issue_matches))

    labels = {normalize(label["name"]) for label in pr.get("labels", [])}
    label_matches = [
        project
        for project in projects
        if labels.intersection(normalize(label) for label in project.get("labels", []))
    ]
    if len(label_matches) == 1:
        return RouteResult(label_matches[0], "labels")

    paths = tuple(changed_paths)
    path_matches = [
        project
        for project in projects
        if any(path.startswith(prefix) or path == prefix for prefix in project.get("paths", []) for path in paths)
    ]
    if len(path_matches) == 1:
        return RouteResult(path_matches[0], "changed-paths")

    haystack = normalize(f"{pr.get('title', '')} {pr.get('body', '')}")
    keyword_matches = [
        project
        for project in projects
        if any(normalize(keyword) in haystack for keyword in project.get("keywords", []))
    ]
    if len(keyword_matches) == 1:
        return RouteResult(keyword_matches[0], "keywords")

    candidates = repo_matches or label_matches or path_matches or keyword_matches
    return RouteResult(None, "routing-review", tuple(sorted({item["key"] for item in candidates})))


def project_base(project: dict[str, Any]) -> str:
    segment = "users" if project["owner_type"] == "user" else "orgs"
    return f"{segment}/{project['owner']}/projectsV2/{project['number']}"


def linked_issue_numbers(pr: dict[str, Any]) -> list[int]:
    numbers: set[int] = set()
    for match in CLOSING_ISSUE.finditer(pr.get("body") or ""):
        url = match.group(1)
        if url:
            repo = pr["repository_url"].removeprefix("https://api.github.com/repos/")
            if url.startswith(f"https://github.com/{repo}/issues/"):
                numbers.add(int(match.group(2)))
        else:
            numbers.add(int(match.group(3)))
    return sorted(numbers)


def item_content_node(item: dict[str, Any]) -> str | None:
    return (item.get("content") or {}).get("node_id")


def item_references(item: dict[str, Any], urls: Iterable[str]) -> bool:
    content = item.get("content") or {}
    known = {content.get("html_url"), content.get("pull_request", {}).get("html_url") if isinstance(content.get("pull_request"), dict) else None}
    body = content.get("body") or ""
    return bool(set(urls).intersection(known)) or any(url in body for url in urls)


def find_existing_item(
    items: Iterable[dict[str, Any]],
    pr: dict[str, Any],
    linked_issues: Iterable[dict[str, Any]],
) -> dict[str, Any] | None:
    nodes = {pr.get("node_id"), *(issue.get("node_id") for issue in linked_issues)}
    urls = {pr.get("html_url"), *(issue.get("html_url") for issue in linked_issues)}
    nodes.discard(None)
    urls.discard(None)
    for item in items:
        if item_content_node(item) in nodes or item_references(item, urls):
            return item
    title = normalize(pr.get("title"))
    title_matches = [
        item for item in items if normalize((item.get("content") or {}).get("title")) == title
    ]
    return title_matches[0] if len(title_matches) == 1 else None


def completed_field_updates(
    project: dict[str, Any], fields: list[dict[str, Any]], merge_date: str
) -> tuple[list[dict[str, Any]], list[str]]:
    updates: list[dict[str, Any]] = []
    warnings: list[str] = []
    status = next((field for field in fields if field["name"] == "Status"), None)
    if not status:
        warnings.append("Status field missing")
    else:
        wanted = normalize(project["completed_status"])
        option = next(
            (option for option in status.get("options", []) if normalize(option["name"]["raw"] if isinstance(option.get("name"), dict) else option.get("name")) == wanted),
            None,
        )
        if option:
            updates.append({"id": status["id"], "value": option["id"]})
        else:
            warnings.append(f"Status option {project['completed_status']!r} missing")

    date_field = next(
        (
            field
            for name in project.get("date_fields", [])
            for field in fields
            if field["name"] == name and field["data_type"] == "date"
        ),
        None,
    )
    if date_field:
        updates.append({"id": date_field["id"], "value": merge_date})
    else:
        warnings.append("No configured existing completion/evidence date field")
    return updates, warnings


def fetch_recent_prs(client: GitHub, owners: list[str], since: dt.datetime) -> list[dict[str, Any]]:
    found: dict[str, dict[str, Any]] = {}
    date = since.date().isoformat()
    for owner in owners:
        qualifier = f"org:{owner}" if owner == "Blue-Ridge-Systems-Consulting" else f"user:{owner}"
        query = f"is:pr is:merged {qualifier} merged:>={date}"
        result = client.api(f"search/issues?q={query.replace(' ', '+')}&per_page=100")
        for item in result.get("items", []):
            repo = item["repository_url"].removeprefix("https://api.github.com/repos/")
            pr = client.api(f"repos/{repo}/pulls/{item['number']}")
            pr["repository_url"] = f"https://api.github.com/repos/{repo}"
            if pr.get("merged_at") and dt.datetime.fromisoformat(pr["merged_at"].replace("Z", "+00:00")) >= since:
                found[pr["html_url"]] = pr
    return sorted(found.values(), key=lambda pr: pr["merged_at"])


def fetch_pr(client: GitHub, repository: str, number: int) -> dict[str, Any]:
    pr = client.api(f"repos/{repository}/pulls/{number}")
    pr["repository_url"] = f"https://api.github.com/repos/{repository}"
    return pr


def fetch_changed_paths(client: GitHub, repository: str, number: int) -> list[str]:
    return [item["filename"] for item in client.api(f"repos/{repository}/pulls/{number}/files?per_page=100", paginate=True)]


def fetch_linked_issues(client: GitHub, pr: dict[str, Any]) -> list[dict[str, Any]]:
    repo = pr["repository_url"].removeprefix("https://api.github.com/repos/")
    return [client.api(f"repos/{repo}/issues/{number}") for number in linked_issue_numbers(pr)]


def inventory_project_memberships(
    client: GitHub, registry: dict[str, Any], pr: dict[str, Any], linked_issues: list[dict[str, Any]]
) -> tuple[dict[tuple[str, int], list[dict[str, Any]]], list[tuple[str, int]], list[tuple[str, int]]]:
    items_by_project: dict[tuple[str, int], list[dict[str, Any]]] = {}
    pr_memberships: list[tuple[str, int]] = []
    issue_memberships: list[tuple[str, int]] = []
    for project in registry["projects"]:
        identity = project_identity(project)
        items = client.api(f"{project_base(project)}/items?per_page=100", paginate=True)
        items_by_project[identity] = items
        if any(item_content_node(item) == pr.get("node_id") or item_references(item, [pr["html_url"]]) for item in items):
            pr_memberships.append(identity)
        issue_nodes = {issue["node_id"] for issue in linked_issues}
        issue_urls = [issue["html_url"] for issue in linked_issues]
        if any(item_content_node(item) in issue_nodes or item_references(item, issue_urls) for item in items):
            issue_memberships.append(identity)
    return items_by_project, pr_memberships, issue_memberships


def assign_content(client: GitHub, repository: str, number: int, assignee: str) -> None:
    client.api(
        f"repos/{repository}/issues/{number}/assignees",
        method="POST",
        body={"assignees": [assignee]},
    )


def recover_eventually_consistent_item(
    client: GitHub,
    project: dict[str, Any],
    pr: dict[str, Any],
    linked_issues: list[dict[str, Any]],
) -> dict[str, Any] | None:
    for delay in (1, 2, 4, 8, 16):
        time.sleep(delay)
        items = client.api(f"{project_base(project)}/items?per_page=100", paginate=True)
        existing = find_existing_item(items, pr, linked_issues)
        if existing:
            return existing
    return None


def verify_write_response(
    client: GitHub,
    patch_response: dict[str, Any],
    repository: str,
    content_number: int,
    assignee: str,
    expected_status: str,
    expected_date: str,
    expect_date: bool,
) -> None:
    content = client.api(f"repos/{repository}/issues/{content_number}")
    assigned = assignee in {user["login"] for user in content.get("assignees", [])}
    values = {field["name"]: field.get("value") for field in patch_response.get("fields", [])}
    status_value = values.get("Status") or {}
    status_name = status_value.get("name", {}) if isinstance(status_value, dict) else {}
    if isinstance(status_name, dict):
        status_name = status_name.get("raw")
    date_matches = True
    if expect_date:
        date_matches = any(
            isinstance(value, str) and value.startswith(expected_date)
            for name, value in values.items()
            if "date" in name.casefold()
        )
    if not (assigned and normalize(status_name) == normalize(expected_status) and date_matches):
        raise ApiError("write response did not contain the expected assignee, Status, and date fields")


def process_pr(client: GitHub, registry: dict[str, Any], pr: dict[str, Any], dry_run: bool) -> dict[str, Any]:
    repository = pr["repository_url"].removeprefix("https://api.github.com/repos/")
    repository_owner = repository.split("/", 1)[0]
    if repository_owner not in registry["repository_owners"]:
        return {"result": "excluded-owner", "repository": repository, "pr": pr["html_url"]}
    if not pr.get("merged_at"):
        return {"result": "not-merged", "repository": repository, "pr": pr["html_url"]}

    linked_issues = fetch_linked_issues(client, pr)
    items_by_project, memberships, linked_memberships = inventory_project_memberships(
        client, registry, pr, linked_issues
    )
    paths = fetch_changed_paths(client, repository, pr["number"])
    route = route_pr(
        pr,
        registry,
        membership_projects=memberships,
        linked_issue_projects=linked_memberships,
        changed_paths=paths,
    )
    if not route.project:
        return {
            "result": route.signal,
            "repository": repository,
            "repository_owner": repository_owner,
            "pr": pr["html_url"],
            "merge_date": pr["merged_at"],
            "candidates": list(route.candidates),
        }

    project = route.project
    items = items_by_project[project_identity(project)]
    existing = find_existing_item(items, pr, linked_issues)
    content = linked_issues[0] if linked_issues else pr
    action = "update-existing" if existing else "create-from-linked-issue" if linked_issues else "create-from-pr"
    fields = client.api(f"{project_base(project)}/fields?per_page=100", paginate=True)
    merge_date = pr["merged_at"][:10]
    updates, warnings = completed_field_updates(project, fields, merge_date)

    result = {
        "repository": repository,
        "repository_owner": repository_owner,
        "pr": pr["html_url"],
        "merged_by": (pr.get("merged_by") or {}).get("login"),
        "merge_date": pr["merged_at"],
        "detected_scope": project["key"],
        "destination_project": project["title"],
        "project_owner": project["owner"],
        "project_number": project["number"],
        "routing_signal": route.signal,
        "existing_item": existing["node_id"] if existing else None,
        "action": action,
        "assignee": registry["assignee"],
        "status": project["completed_status"],
        "completion_date": merge_date,
        "warnings": warnings,
        "result": "dry-run" if dry_run else "pending-write",
    }
    if dry_run:
        return result

    assign_content(client, repository, content["number"], registry["assignee"])
    if not existing:
        try:
            created = client.api(
                f"{project_base(project)}/items",
                method="POST",
                body={"type": "Issue" if linked_issues else "PullRequest", "id": content["id"]},
            )
            existing = created.get("value", created)
        except ApiError as error:
            if "HTTP 422" not in str(error) or "Content already exists" not in str(error):
                raise
            existing = recover_eventually_consistent_item(client, project, pr, linked_issues)
            if not existing:
                raise ApiError(
                    "GitHub reported existing Project content, but it remained absent from "
                    "the item listing after bounded consistency retries"
                ) from error
            action = "update-existing"
            result["action"] = action
    patch_response = existing
    if updates:
        patch_response = client.api(
            f"{project_base(project)}/items/{existing['id']}",
            method="PATCH",
            body={"fields": updates},
        )
    verify_write_response(
        client,
        patch_response,
        repository,
        content["number"],
        registry["assignee"],
        project["completed_status"],
        merge_date,
        any(field["data_type"] == "date" for field in fields if any(field["name"] == name for name in project.get("date_fields", []))),
    )
    result["existing_item"] = existing["node_id"]
    result["result"] = "updated" if action == "update-existing" else "created"
    return result


def print_report(result: dict[str, Any]) -> None:
    print("BLUE RIDGE PROJECT SYNC")
    for label, key in (
        ("Repository", "repository"),
        ("Repository owner", "repository_owner"),
        ("PR", "pr"),
        ("Merged by", "merged_by"),
        ("Merge date", "merge_date"),
        ("Detected scope", "detected_scope"),
        ("Destination Project", "destination_project"),
        ("Project owner", "project_owner"),
        ("Existing item", "existing_item"),
        ("Action", "action"),
        ("Assignee", "assignee"),
        ("Status", "status"),
        ("Completion date", "completion_date"),
        ("Result", "result"),
    ):
        print(f"{label}: {result.get(key, '')}")
    if result.get("candidates"):
        print(f"Candidates: {', '.join(result['candidates'])}")
    for warning in result.get("warnings", []):
        print(f"Warning: {warning}")
    print()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=Path(__file__).with_name("routes.json"))
    parser.add_argument("--repository", help="exact OWNER/REPOSITORY")
    parser.add_argument("--pr", type=int, help="pull request number")
    parser.add_argument("--recent-hours", type=int, default=48)
    parser.add_argument("--write", action="store_true", help="apply writes; default is dry-run")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if bool(args.repository) != bool(args.pr):
        raise SystemExit("--repository and --pr must be supplied together")
    registry = load_registry(args.registry)
    client = GitHub()
    if args.repository:
        prs = [fetch_pr(client, args.repository, args.pr)]
    else:
        since = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=args.recent_hours)
        prs = fetch_recent_prs(client, registry["repository_owners"], since)
    if not prs:
        print("No eligible merged pull requests found.")
        return 0
    failures = 0
    for pr in prs:
        try:
            result = process_pr(client, registry, pr, dry_run=not args.write)
        except ApiError as error:
            result = {
                "repository": pr["repository_url"].removeprefix("https://api.github.com/repos/"),
                "pr": pr["html_url"],
                "result": "error",
                "warnings": [str(error)],
            }
        print_report(result)
        if result["result"] in {"error", "routing-review", "invalid-explicit-override"}:
            failures += 1
    return 2 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
