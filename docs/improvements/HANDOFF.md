# Agent handoff: research data improvements

You are picking up a planned improvement of Envisioning's research data. The analysis is done and the issues are filed. Your job is to carry out the plan in order, open PRs, and stop at the human decision points marked **🧑 DECIDE**.

Read first: [`README.md`](README.md) (system overview and order of work), then the runbook for whichever phase you are in.

## Repositories

| Repo | Visibility | Role |
|---|---|---|
| `envisioning/research` (this repo, also called research-oss) | public | Markdown/JSON copy of the CMS. `scripts/sync.py` exports, `scripts/audit.py` checks. |
| `envisioning/research-app` | private | Next.js monorepo serving `envisioning.com/<hub>/<slug>` from Supabase. All CMS scripts (enrichment, images, importer) live here. Read its `CLAUDE.md`. |

Supabase is the source of truth. Data flows one way: **CMS → app** and **CMS → this repo**.

## Guardrails (non-negotiable)

1. **Never edit `content/` or `indexes/` by hand.** Fix the CMS and let `sync.py` carry the change.
2. **Never write from this repo into the CMS.** Don't run `research-app/scripts/import-oss-markdown-to-cms.ts`. It overwrote production rows once.
3. **CMS writes use preview → review → apply.** Run every enrichment or rewrite script in preview mode, write the review JSON, get it approved, then `--apply`. Nothing is published automatically.
4. **Before any bulk CMS update**, export the affected rows (`select * from technologies where research_id = ...`) into a dated file under the scratchpad or `logs/`, so the change can be reverted.
5. **This repo is public.** Never commit secrets, credential names, internal URLs or infrastructure details here. Keep those in research-app.
6. **Work in `main`.** The maintainer decided on 2026-10-01: commit to `main`, one commit per issue or tightly related group, and reference the issue (`Fixes #N`). If you open a PR, merge it yourself after `validate.yml` passes. Keep `python -m unittest scripts.test_sync` green.
7. **Don't widen scope.** If you find something new, file an issue; don't fold it into the current PR.

## Access you need

- Read access to the CMS for `sync.py` (the repo secrets named in the README).
- Write access to the CMS and the content-generation services, for work in research-app. These are configured there; ask a maintainer. Never copy them into this repo.
- Search Console access for envisioning.com (held by a human) for the SEO baseline and monitoring.

If you're missing access, stop and ask; don't work around it.

## Task list (in order)

Status key: ☐ todo · 🧑 needs a human decision before continuing.

### Phase 0: stop the bleeding

| # | Task | Issue | Done when |
|---|---|---|---|
| 0.1 | 🧑 Resolve the security item in app#2 together with a human | app#2 | Issue closed by a human |
| 0.2 | 🧑 Retire the OSS → CMS importer: delete it, or harden it (dry-run by default, `published:false`, metric mapping from `metrics_config`). Ask which. | app#3 | PR merged |
| 0.3 | 🧑 Ask whether a Supabase backup from before the importer ran still exists. If yes, follow `docs/restore-only-technologies-entries.md` with a **dry-run diff first**; if no, record that the current rows are the accepted baseline in app#3 | app#3 | Decision recorded in the issue |
| 0.4 | Make sure the CMS has every repo-only edit: run `python scripts/audit.py --json` and check each `files_not_in_index`, orphan and diverged file against the CMS. Must cover the #1 Density Propulsion fix and the 3 diverged spore entries. Fix in the CMS. | app#4, research#4 | Every item ticked off in a comment on app#4 |
| 0.5 | Fix the sync credentials, run `sync.py --full --dry-run`, review the counts, then do a real run on a branch and open a PR | research#3, research#4 | Sync PR merged; `audit.py` passes every check except `score_fields_labelled` |

### Phase 1: safe pipeline

| # | Task | Issue | Done when |
|---|---|---|---|
| 1.1 | `--max-delete-ratio` and `--summary-file` in `sync.py`, with tests | research#6 | tests green |
| 1.2 | `sync.yml` pushes to `main` only after the delete guard and `audit.py --strict` pass; failure opens a "Sync failing" issue | research#6 | one run observed producing a commit or no-op |
| 1.3 | `validate.yml` on push to `main` and on pull_request: unit tests + `audit.py --strict` | research#6 | runs on a push |
| 1.4 | Re-enable the schedule | research#3 | workflow enabled |

### Phase 2: correct data

| # | Task | Issue | Done when |
|---|---|---|---|
| 2.1 | Pass through `updated_at`, `collection_label`, tags and sources (`technology_evidence`) and hub `about`/`metrics_config`/`language`; leave out empty or unpublished hubs | research#7 | tests per field; `updated_at` non-null in the index |
| 2.2 | Schema v2 metrics block + `schema_version`; keep the v1 keys only for hubs on default metrics; README migration notes | research#5, research#8 | `score_fields_labelled` passes; remove `HUB_METRICS` from `audit.py` |
| 2.3 | `indexes/technologies.jsonl` + attribution line in every body | research#8, research#14 | files generated by sync |

### Phase 3: SEO (3.1 can start immediately, in parallel with phases 0–2)

| # | Task | Issue | Done when |
|---|---|---|---|
| 3.1 | 🧑 Find out why `app/[slug]/sitemap.old` was turned off (ask, or check Vercel build logs), then restore it with absolute envisioning.com URLs and `lastModified` | app#5 | `/<hub>/sitemap/<id>.xml` returns valid XML in production |
| 3.2 | 🧑 Ask a human to record the Search Console baseline (indexed, impressions, clicks per hub) and submit the sitemaps | app#5 | numbers recorded in app#5 |
| 3.3 | Check canonical, `noindex` on the Vercel host, JSON-LD and og:image in `@envisioning/app`; fix or file upstream | app#6 | checklist in `07-seo.md` updated |
| 3.4 | Measure `meta_description` coverage; fill gaps with `rewrite-summaries-and-meta.ts` (preview → review → apply) | app#6 | 100% coverage on published rows |
| 3.5 | Check whether this repo is deployed (it has a `vercel.json`); if so, `noindex` `/content/*` | research#14 | header verified with curl |

### Phase 4: quality (per hub, small batches)

| # | Task | Issue | Done when |
|---|---|---|---|
| 4.1 | Fix the cities out-of-range value; check metrics on all importer-inserted rows | app#7 | `scores_in_range` passes |
| 4.2 | 🧑 interface metric2: fill or remove? moradia ×15: score or unpublish? | app#7 | `scores_present` passes or exceptions documented |
| 4.3 | Database check that scores stay within each hub's scale | app#7 | migration merged |
| 4.4 | Images for the 254 entries that lack one (`regenerate-hub-images.ts --missing-only`) | research#9 | `images_present` passes |
| 4.5 | Impact re-calibration, one default-metrics hub per batch | research#9 | share of 4–5 ≤ 50% |
| 4.6 | Duplicate groups: propose differentiate vs. consolidate per group in a table, 🧑 approve, then apply | research#10 | `entity_id` set; canonicals live |
| 4.7 | `evidence_level` for all entries (xenotech/subspace from metrics, others default `emerging`); site badge | research#11 | field exported; badge live |

### Phase 5–6: coverage and freshness

| # | Task | Issue |
|---|---|---|
| 5.1 | 🧑 Decide grow, merge or archive for each of the 11 thin hubs, lexicon, and coconut/democracy/wennink | research#12, app#9 |
| 5.2 | Clean up stale tooling and docs in research-app | app#9 |
| 5.3 | First quarterly gap analysis → unpublished drafts | research#12 |
| 6.1 | `technologies.last_reviewed` column + weekly review-queue job | app#8 |
| 6.2 | Monthly signal/evidence scan in preview mode | app#8 |
| 6.3 | First tagged release `v2026.4` + CHANGELOG | research#13 |

## How to verify progress

```bash
# this repo
python -m unittest scripts.test_sync
python scripts/audit.py            # human report
python scripts/audit.py --strict   # CI gate (blocking checks)
```

Record the `audit.py --json` summary at the start and end of each phase in the relevant issue, so progress is visible.

## When to stop and ask

- Any step marked 🧑.
- A dry run shows deletes you can't explain, or more than 2% of files.
- A CMS write would touch more than 50 rows in one go.
- Anything involving credentials, a restore, or unpublishing content.
- A finding that contradicts this plan (e.g. the CMS already contains a fix the plan assumes is missing).

## Reporting

At the end of each work session, comment on each issue you touched: what changed, PR links, audit numbers before and after, and open questions. Update the status columns in `07-seo.md` as items land.
