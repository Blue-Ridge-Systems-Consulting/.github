#!/usr/bin/env python3
import importlib.util
import sys
import unittest
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


class IdempotencyTests(unittest.TestCase):
    def test_existing_pr_node_is_reused(self):
        pull = {"node_id": "PR_node", "html_url": "https://github.com/o/r/pull/1", "title": "Work"}
        items = [{"node_id": "ITEM", "content": {"node_id": "PR_node", "title": "Work"}}]
        self.assertEqual(SYNC.find_existing_item(items, pull, []), items[0])

    def test_unique_title_fallback_is_reused(self):
        pull = {"node_id": "PR_node", "html_url": "https://github.com/o/r/pull/1", "title": "Work"}
        items = [{"node_id": "ITEM", "content": {"node_id": "OTHER", "title": " work "}}]
        self.assertEqual(SYNC.find_existing_item(items, pull, []), items[0])

    def test_duplicate_titles_are_not_guessed(self):
        pull = {"node_id": "PR_node", "html_url": "https://github.com/o/r/pull/1", "title": "Work"}
        items = [
            {"node_id": "A", "content": {"node_id": "A1", "title": "Work"}},
            {"node_id": "B", "content": {"node_id": "B1", "title": "Work"}},
        ]
        self.assertIsNone(SYNC.find_existing_item(items, pull, []))


if __name__ == "__main__":
    unittest.main()
