# Research dataset improvement plan

How the Envisioning research data is produced, where it is broken today, and the order in which to fix it. Each step has a runbook in this folder and a tracking issue.

## How the system works

```
Supabase CMS (source of truth)
  ├─► research-app (Next.js) ──► envisioning.com/<hub>/<slug>   ← SEO surface, ~3,500 pages
  └─► scripts/sync.py ──► this repo (Markdown + JSON)            ← open dataset, links back to envisioning.com
```

- **Editing happens in the CMS only.** This repo is a downstream copy. Hand edits here are overwritten by the next sync.
- **Each hub defines its own three metrics** (`research_metrics.metrics_config`). Only some hubs use TRL / impact / investment.
- **The goal is search and AI visibility for envisioning.com.** This dataset supports that goal: it links back to envisioning.com, gives Google Dataset Search something to list, and puts citable data where AI crawlers read it.

## Current state (2026-10-01)

Run `python scripts/audit.py` for live numbers.

| Area | State |
|---|---|
| Export | Every scheduled sync has failed since 2026-03-01; the schedule is now off |
| Consistency | 115 files missing from the index, 32 orphan by-hub files, 4 diverged copies, 22 stale hub counts |
| Metrics | `trl/impact/investment` labels are wrong for 9 hubs (986 entries) |
| Scores | interface metric2 empty; 15 moradia entries unscored; 89% of entries have impact 4–5 |
| Content | no sources or dates published; 99 technologies written separately in several hubs; 254 entries without images |
| SEO | per-hub sitemaps switched off in the app; canonical tags and structured data not checked |

## Order of work

| Phase | Goal | Runbook | Issues |
|---|---|---|---|
| 0. Stop the bleeding | Nothing overwrites anything by accident | [01-restore-sync](01-restore-sync.md) | research #3, #4 · app #2, #3, #4 |
| 1. Safe pipeline | Every change shows up as a reviewable PR | [02-sync-safety-and-ci](02-sync-safety-and-ci.md) | research #6 |
| 2. Correct data | Fields mean what they say | [03-schema-v2](03-schema-v2.md) | research #5, #7, #8 |
| 3. Quality | Scores spread properly, labels added, duplicates resolved | [04-data-quality](04-data-quality.md) | research #9, #10, #11 · app #7 |
| 4. SEO | Pages discoverable, canonical, trusted | [07-seo](07-seo.md) | research #14 · app #5, #6 |
| 5. Coverage | Thin hubs grown or merged, gaps found on schedule | [05-coverage](05-coverage.md) | research #12 · app #9 |
| 6. Freshness | Reviews on a schedule, quarterly releases | [06-update-strategy](06-update-strategy.md) | research #13 · app #8 |

Phases 0–2 are sequential. Phases 3–6 can run in parallel once the pipeline is safe. SEO quick wins (turning sitemaps back on, app #5) don't depend on any of them and can ship now.

## Ground rules

1. Never edit `content/` or `indexes/` by hand. Fix the CMS and let the sync carry the change.
2. Never write from this repo into the CMS. The old importer overwrote production rows.
3. All AI-generated changes go through preview → review → apply. Nothing is published automatically.
4. Every sync is a PR; `scripts/audit.py --strict` must pass before merge.
