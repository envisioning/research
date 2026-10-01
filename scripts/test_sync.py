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
        self.assertIn("## Sources\n\n- [Example](https://example.com)\n", a)
        self.assertIn("last_reviewed: null", a)
        self.assertIn("updated_at: '2026-02-23T14:12:20.889403+00:00'", a)

    def test_render_without_sources_has_no_sources_section(self):
        tech = {**self.tech, "sources": []}
        self.assertNotIn("## Sources", sync.render_technology_markdown(tech))

    def test_evidence_replaces_legacy_sources(self):
        data = {
            "research": [{"id": "hub-1", "slug": "lattice", "title": "Lattice"}],
            "technologies": [
                {"id": "uuid-1", "original_id": "orbital-lattice", "research_id": "hub-1",
                 "title": "Orbital Lattice", "published": True, "last_reviewed_at": "2026-10-01T00:00:00+00:00"},
            ],
            "sources": [{"technology_id": "uuid-1", "url": "https://legacy.example", "title": "Legacy", "position": 0}],
            "technology_tags": [], "tags": [], "research_metrics": [],
            "links": {"technology_evidence": [
                {"id": "e2", "technology_id": "uuid-1", "url": "https://old.example", "title": "Old", "year": 2019},
                {"id": "e1", "technology_id": "uuid-1", "url": "https://new.example", "title": "New", "year": 2025},
                {"id": "e3", "technology_id": "uuid-1", "url": None, "title": "No link", "year": 2026},
            ]},
        }
        techs, _ = sync.build_enriched(data)
        self.assertEqual([s["url"] for s in techs[0]["sources"]], ["https://new.example", "https://old.example"])
        self.assertEqual(techs[0]["last_reviewed_at"], "2026-10-01T00:00:00+00:00")

    def test_link_files_are_sorted_jsonl_per_table(self):
        data = {"links": {"technology_tags": [
            {"id": "b", "technology_id": "uuid-1", "tag_id": "t2"},
            {"id": "a", "technology_id": "uuid-1", "tag_id": "t1"},
        ]}, "organizations": []}
        files = sync.build_link_files(data)
        tags = files[sync.LINKS_DIR / "technology_tags.jsonl"]
        self.assertEqual(tags.splitlines()[0], '{"id": "a", "tag_id": "t1", "technology_id": "uuid-1"}')
        self.assertEqual(files[sync.LINKS_DIR / "technology_evidence.jsonl"], "")
        self.assertIn(sync.LINKS_DIR / "organizations.jsonl", files)

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

    def test_delete_ratio(self):
        with tempfile.TemporaryDirectory() as tmp:
            kept = [Path(tmp) / f"kept-{i}.md" for i in range(9)]
            stale = Path(tmp) / "stale.md"
            for p in [*kept, stale]:
                p.write_text("x\n", encoding="utf-8")
            new = Path(tmp) / "new.md"

            self.assertAlmostEqual(sync.delete_ratio({*kept, new}, {stale}), 0.1)
            self.assertEqual(sync.delete_ratio({new}, set()), 0.0)

    def test_planned_hub_stale_matches_slug_hub_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            all_dir = Path(tmp) / "all"
            by_hub_dir = Path(tmp) / "by-hub"
            (by_hub_dir / "lattice").mkdir(parents=True)
            all_dir.mkdir()
            keep = all_dir / "orbital-lattice--lattice.md"
            gone = all_dir / "old-entry--lattice.md"
            other = all_dir / "old-entry--grid.md"
            gone_by_hub = by_hub_dir / "lattice" / "old-entry.md"
            for p in (keep, gone, other, gone_by_hub):
                p.write_text("x\n", encoding="utf-8")

            orig = sync.CONTENT_ALL_DIR, sync.CONTENT_BY_HUB_DIR
            sync.CONTENT_ALL_DIR, sync.CONTENT_BY_HUB_DIR = all_dir, by_hub_dir
            try:
                stale = sync.planned_hub_stale("lattice", {keep})
            finally:
                sync.CONTENT_ALL_DIR, sync.CONTENT_BY_HUB_DIR = orig

            self.assertEqual(stale, {gone, gone_by_hub})


if __name__ == "__main__":
    unittest.main()
