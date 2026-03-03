import tempfile
import unittest
from pathlib import Path

import scripts.sync as sync


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.tech = {
            "id": "uuid-1",
            "original_id": "orbital-lattice",
            "hub_slug": "lattice",
            "hub_title": "Lattice",
            "title": "Orbital Lattice",
            "summary": "Short summary",
            "description": "Long description",
            "image": None,
            "collection_id": "hardware",
            "collection_label": "Hardware",
            "metric1": 2,
            "metric2": 3,
            "metric3": 4,
            "published": True,
            "updated_at": "2026-02-23T14:12:20.889403+00:00",
            "tags": {
                "tag1": [{"id": "t1", "label": "Alpha"}],
                "tag2": [{"id": "t2", "label": "Beta"}],
                "tag3": [],
            },
            "sources": [
                {
                    "url": "https://example.com",
                    "title": "Example",
                    "summary": "source summary",
                    "position": 0,
                }
            ],
        }
        self.hub = {
            "id": "hub-1",
            "slug": "lattice",
            "title": "Lattice",
            "topic_description": "Topic intro",
            "about": "",
            "indicator_explainers": None,
            "metrics_config": None,
        }

    def test_render_technology_markdown_deterministic(self):
        a = sync.render_technology_markdown(self.tech)
        b = sync.render_technology_markdown(self.tech)
        self.assertEqual(a, b)
        self.assertIn("# Orbital Lattice", a)
        self.assertIn("## Description", a)
        self.assertNotIn("## Sources", a)

    def test_render_hubs_markdown_deterministic(self):
        techs = [self.tech]
        hubs = [self.hub]
        a = sync.render_hubs_markdown(hubs, techs, "2026-02-01T00:00:00+00:00")
        b = sync.render_hubs_markdown(hubs, techs, "2026-02-01T00:00:00+00:00")
        self.assertEqual(a, b)
        self.assertIn("## Lattice (1)", a)
        self.assertIn("Topic intro", a)

    def test_render_hubs_markdown_missing_summary_safe(self):
        hubs = [dict(self.hub, topic_description="")]
        out = sync.render_hubs_markdown(hubs, [self.tech], "2026-02-01T00:00:00+00:00")
        self.assertIn("_No topic description available._", out)

    def test_noop_second_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "file.md"
            content = "same\n"
            first = sync.apply_file_updates({target: content}, set(), dry_run=False)
            second = sync.apply_file_updates({target: content}, set(), dry_run=False)

            self.assertEqual(first["created"], 1)
            self.assertEqual(second["created"], 0)
            self.assertEqual(second["updated"], 0)
            self.assertEqual(second["deleted"], 0)
            self.assertEqual(second["unchanged"], 1)

    def test_stale_cleanup(self):
        with tempfile.TemporaryDirectory() as tmp:
            stale = Path(tmp) / "stale.md"
            stale.parent.mkdir(parents=True, exist_ok=True)
            stale.write_text("old\n", encoding="utf-8")

            stats = sync.apply_file_updates({}, {stale}, dry_run=False)
            self.assertEqual(stats["deleted"], 1)
            self.assertFalse(stale.exists())


if __name__ == "__main__":
    unittest.main()
