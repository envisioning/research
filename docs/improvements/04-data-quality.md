# 04 · Data quality

Issues: envisioning/research#9, #10, #11 · envisioning/research-app#7

All fixes happen in the CMS using the app repo's preview → review JSON → `--apply` scripts. Check progress here with `python scripts/audit.py` after each sync.

## Missing and invalid scores
| Item | Action |
|---|---|
| interface: the 99 entries that had no impact or investment in March now all have impact = 3 and investment = 3 (the hub uses the standard TRL / Impact / Investment scales) | a uniform 3 looks like a bulk default: score them, or accept and document it |
| moradia × 15 unscored | score against `metrics_config` definitions, or unpublish |
| ~~cities `scooter-sharing-system` metric3 = 5 (scale 1–4)~~ | done 2026-10-01: set to 3 (Maturity). The other 114 importer-inserted rows are in range (app#3) |
| prevent recurrence | database check: value ≤ max `definitions.value` for the hub's metric |

## Impact calibration
In hubs that really use impact, 89% of entries have impact 4–5, so the score barely tells entries apart.

1. Write anchored definitions (what a 1, 3 and 5 look like, with 2 real examples each) into the hub `metrics_config`.
2. Re-score one hub at a time with the enrichment script in preview mode. Have the model return the anchor it matched and one sentence of reasoning.
3. An editor reviews the outliers, then applies.
4. Target distribution, roughly: 1 → 10%, 2 → 20%, 3 → 35%, 4 → 25%, 5 → 10%. Check with `audit.py` (`impact_distribution`).

## Duplicates across hubs (#10)
1. Candidates: identical slugs (99 today, from `audit.py --json` → `cross_hub_duplicates`) plus pairs above the cosine threshold in the CMS similarities table.
2. Decide each group:
   - **Differentiate:** the hub's angle goes in the title, summary and first paragraph; set a distinct `meta_description`.
   - **Consolidate:** keep the best page; the others get `rel=canonical` to it or are unpublished.
3. Give every member of a group the same `entity_id`, and show "Also tracked in" links on the site.

## Evidence level (#11)
- `evidence_level ∈ {established, emerging, speculative}`.
- xenotech: Plausibility 1–2 → speculative, 3 → emerging, 4–5 → established. subspace: use Scientific Basis.
- Other hubs: default `emerging`; editors raise it to `established` when there are peer-reviewed or commercial-deployment sources.
- Publish it in the dataset and show it on the site (badge + framing paragraph on speculative pages).

## Writing quality
- Filler phrases: "unprecedented" appears in 301 entries, "seamless" in 244, "paradigm shift" in 114. Add them to the rewriter skill's rubric as banned phrases and re-run the summary/description rewrite on the worst offenders.
- Every description should carry at least 2 sources in `technology_evidence` (enrich with `enrich-technology-evidence`).

## Images
254 entries have no image (top: wonen 57, interface 52). In the app repo, run `scripts/regenerate-hub-images.ts --hub <hub> --missing-only`.
