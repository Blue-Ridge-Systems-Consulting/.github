#!/usr/bin/env python3
import importlib.util
import sys
import unittest
from unittest.mock import patch
import subprocess
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("project_sync.py")
SPEC = importlib.util.spec_from_file_location("project_sync", MODULE_PATH)
SYNC = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
sys.modules[SPEC.name] = SYNC
SPEC.loader.exec_module(SYNC)


def registry():
    return {
        "repository_owners": ["owensreo", "Blue-Ridge-Systems-Consulting"],
        "explicit_overrides": {},
        "projects": [
            {
                "key": "cloudflare",
                "owner": "owensreo",
                "number": 30,
                "repositories": ["owensreo/cloudflare-zero-trust-policy"],
                "labels": ["cloudflare"],
                "keywords": ["workers"],
                "paths": ["terraform/"],
            },
            {
                "key": "operations",
                "owner": "owensreo",
                "number": 24,
                "repositories": ["Blue-Ridge-Systems-Consulting/.github"],
                "labels": ["operations"],
                "keywords": ["project sync"],
                "paths": [".github/project-sync/"],
            },
        ],
    }


def pr(repo="Blue-Ridge-Systems-Consulting/.github", body="", labels=None):
    return {
        "repository_url": f"https://api.github.com/repos/{repo}",
        "body": body,
        "title": "Generic maintenance",
        "labels": labels or [],
    }


class ProjectCacheTests(unittest.TestCase):
    def test_project_reads_reused_until_destination_mutates(self):
        client = SYNC.GitHub()
        a = "users/owensreo/projectsV2/3/items?per_page=100"
        b = "users/owensreo/projectsV2/4/items?per_page=100"
        reply = subprocess.CompletedProcess([], 0, stdout="[]", stderr="")
        with patch.object(SYNC.subprocess, "run", return_value=reply) as run:
            client.api(a, paginate=True)
            client.api(b, paginate=True)
            client.api(a, paginate=True)
            self.assertEqual(run.call_count, 2)
            client.api("users/owensreo/projectsV2/3/items", method="POST", body={})
            client.api(b, paginate=True)
            client.api(a, paginate=True)
            self.assertEqual(run.call_count, 4)


class RoutingTests(unittest.TestCase):
    def test_existing_membership_wins(self):
        result = SYNC.route_pr(pr(), registry(), membership_projects=[("owensreo", 30)])
        self.assertEqual(result.project["key"], "cloudflare")
        self.assertEqual(result.signal, "existing-project-membership")

    def test_explicit_override_wins_over_repository(self):
        item = pr(body="Project-Sync-Project: owensreo#30")
        result = SYNC.route_pr(item, registry())
        self.assertEqual(result.project["key"], "cloudflare")
        self.assertEqual(result.signal, "explicit-override")

    def test_full_repository_mapping(self):
        result = SYNC.route_pr(pr(), registry())
        self.assertEqual(result.project["key"], "operations")
        self.assertEqual(result.signal, "repository")

    def test_owner_is_part_of_repository_identity(self):
        result = SYNC.route_pr(pr("owensreo/.github"), registry())
        self.assertIsNone(result.project)
        self.assertEqual(result.signal, "routing-review")

    def test_ambiguous_labels_require_review(self):
        data = registry()
        data["projects"][1]["labels"].append("cloudflare")
        result = SYNC.route_pr(pr("owensreo/unmapped", labels=[{"name": "cloudflare"}]), data)
        self.assertIsNone(result.project)
        self.assertEqual(set(result.candidates), {"cloudflare", "operations"})

    def test_container_repository_is_configured_for_fanout(self):
        data = registry()
        data["fanout_repositories"] = ["owensreo/blue-ridge-nexus-containers"]
        self.assertIn("owensreo/blue-ridge-nexus-containers", data["fanout_repositories"])


class IdempotencyTests(unittest.TestCase):
    def test_existing_pr_node_is_reused(self):
        pull = {"node_id": "PR_node", "html_url": "https://github.com/o/r/pull/1", "title": "Work"}
        items = [{"node_id": "ITEM", "content": {"node_id": "PR_node", "title": "Work"}}]
        self.assertEqual(SYNC.find_existing_item(items, pull, []), items[0])

    def test_unique_title_fallback_is_reused(self):
        pull = {"node_id": "PR_node", "html_url": "https://github.com/o/r/pull/1", "title": "Work"}
        items = [{"node_id": "ITEM", "content_type": "DraftIssue", "content": {"node_id": "OTHER", "title": " work "}}]
        self.assertEqual(SYNC.find_existing_item(items, pull, []), items[0])

    def test_same_title_other_pull_request_is_not_reused(self):
        pull = {"node_id": "PR_A", "html_url": "https://github.com/o/a/pull/1", "title": "Brand README"}
        items = [{"content_type": "PullRequest", "content": {"node_id": "PR_B", "title": "Brand README"}}]
        self.assertIsNone(SYNC.find_existing_item(items, pull, []))

    def test_duplicate_titles_are_not_guessed(self):
        pull = {"node_id": "PR_node", "html_url": "https://github.com/o/r/pull/1", "title": "Work"}
        items = [
            {"node_id": "A", "content_type": "DraftIssue", "content": {"node_id": "A1", "title": "Work"}},
            {"node_id": "B", "content_type": "DraftIssue", "content": {"node_id": "B1", "title": "Work"}},
        ]
        self.assertIsNone(SYNC.find_existing_item(items, pull, []))


class FetchTests(unittest.TestCase):
    def test_archived_repositories_are_not_scanned(self):
        class ArchivedClient:
            def api(self, path, **kwargs):
                if path.count("/") != 2:
                    raise AssertionError("Archived PRs must not be scanned")
                return {"archived": True}
        since = SYNC.dt.datetime(2026, 10, 18, tzinfo=SYNC.dt.timezone.utc)
        pulls, warnings = SYNC.fetch_recent_prs(ArchivedClient(), registry(), since)
        self.assertEqual(pulls, [])
        self.assertEqual(len(warnings), 2)
        self.assertTrue(all("Skipped archived repository" in w for w in warnings))

    def test_fetch_uses_configured_repositories_and_skips_missing_results(self):
        class FakeClient:
            def __init__(self):
                self.paths = []

            def api(self, path, **kwargs):
                self.paths.append(path)
                if path.count("/") == 2:
                    return {"archived": False}
                if path == "repos/Blue-Ridge-Systems-Consulting/.github/pulls?state=closed&sort=updated&direction=desc&per_page=100":
                    raise SYNC.ApiError("GitHub API GET ... failed: HTTP 404")
                if path == "repos/owensreo/cloudflare-zero-trust-policy/pulls?state=closed&sort=updated&direction=desc&per_page=100":
                    return [
                        {
                            "number": 9,
                            "merged_at": "2026-10-18T05:00:00Z",
                            "html_url": "https://github.com/owensreo/cloudflare-zero-trust-policy/pull/9",
                        }
                    ]
                raise AssertionError(f"unexpected API path: {path}")

        client = FakeClient()
        since = SYNC.dt.datetime(2026, 10, 18, 4, tzinfo=SYNC.dt.timezone.utc)
        pulls, warnings = SYNC.fetch_recent_prs(client, registry(), since)

        self.assertEqual([pull["number"] for pull in pulls], [9])
        self.assertEqual(len(warnings), 1)
        self.assertTrue(any("repos/Blue-Ridge-Systems-Consulting/.github/pulls?" in path for path in client.paths))
        self.assertTrue(any("repos/owensreo/cloudflare-zero-trust-policy/pulls?" in path for path in client.paths))


if __name__ == "__main__":
    unittest.main()
