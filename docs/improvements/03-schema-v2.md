# 03 · Correct fields and schema v2

Issues: envisioning/research#5, envisioning/research#7, envisioning/research#8

## Step 1: fix what sync.py drops (no breaking changes)

In `scripts/sync.py`:

| Fix | Where |
|---|---|
| Pass `updated_at` through | `build_enriched()`: add `"updated_at": tech.get("updated_at")` |
| Export `collection_label` | `render_technology_markdown()` frontmatter + technologies index |
| Export tags | frontmatter `tags: {tag1: [...], tag2: [...], tag3: [...]}` (labels) |
| Export sources | select `technology_evidence` (fall back to `technologies_sources`), render as `## Sources` list |
| Export hub metadata | `hubs.json`: `about`, `metrics_config`, `language` |
| Leave out empty or unpublished hubs | filter `research.published` and hubs with 0 published technologies (`lexicon`) |

Add a test in `scripts/test_sync.py` for each of these.

## Step 2: hub-specific metrics (breaking change, so version it)

Today `metric1/2/3` are exported as `trl/impact/investment` for every hub. In 9 hubs they mean something else (see #5 and `HUB_METRICS` in `scripts/audit.py`).

v2 frontmatter:

```yaml
schema_version: 2
slug: scalar-waves
hub: xenotech
language: en
title: Scalar Waves
summary: ...
permalink: https://www.envisioning.com/xenotech/scalar-waves
collection: energy-systems
collection_label: Energy Systems
metrics:
  metric1: {name: Citation Frequency, value: 2, max: 5}
  metric2: {name: Plausibility Score, value: 1, max: 5}
  metric3: {name: Technology Readiness Level, value: 1, max: 9}
evidence_level: speculative
entity_id: null          # set when the same technology exists in several hubs (#10)
created_at: 2025-11-02T...
updated_at: 2026-03-04T...
last_reviewed: null
image_url: ...
tags: {...}
```

- Keep the v1 keys `trl/impact/investment` for **one release**, filled only for hubs whose metric really is TRL/impact/investment, and announce the removal in the README and CHANGELOG.
- Once `hubs.json` carries `metrics_config`, delete the temporary `HUB_METRICS` table from `scripts/audit.py`.

## Step 3: extra outputs
- `indexes/technologies.jsonl`: one full record per line (frontmatter, body and sources) for search and AI pipelines.
- `CHANGELOG.md`, generated from the sync summary at release time (see 06).

## Migration notes for users of the data
- `trl` → the metric whose `name` is "Technology Readiness Level". For xenotech that is `metric3`; agape, datatrends, moradia, sakan and wonen don't have one.
- Don't compare `metric2` across hubs unless the `name` matches.
