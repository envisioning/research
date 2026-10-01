# 06 · Update strategy

Issues: envisioning/research#13 · envisioning/research-app#8

## Principles
- An entry is only as good as the date it was last reviewed. Store that date and show it.
- Automation proposes changes; people publish them.
- The public dataset is released on a fixed rhythm so it can be cited.

## Cadence
| What | Frequency | Mechanism |
|---|---|---|
| CMS → repo sync | daily | `sync.yml` opens a PR (see 02) |
| Review queue | weekly | job lists published rows past their review date |
| Signal/evidence scan | monthly | `enrich-technology-signals` + `enrich-technology-evidence` in preview mode on due rows |
| Gap analysis | quarterly | see 05 |
| Dataset release | quarterly | git tag `vYYYY.Q` + CHANGELOG |
| Search Console review | monthly | see 07 |

## Review due dates
Based on the hub's maturity metric (TRL, or its equivalent such as Market Maturity or Innovation Stage):

| Maturity | Review every |
|---|---|
| TRL 7–9 (deployed, fast-moving market) | 6 months |
| TRL 4–6 | 12 months |
| TRL 1–3 | 18 months |

`due = last_reviewed + interval`. Rows with no `last_reviewed` count as due now, oldest `updated_at` first.

## Review loop
1. The weekly job posts the due list, capped at a batch size (e.g. 50).
2. The monthly scan writes proposed changes (new evidence, changed scores, rewritten paragraphs) to review JSON. Nothing is applied yet.
3. An editor works the batch in the `research-tech-page-rewriter` tracker: todo → qa_review → published.
4. `--apply` writes the approved changes and sets `last_reviewed = now()`.
5. The next daily sync opens a PR here, CI runs the audit, and someone merges it.

## Releases
At the start of each quarter:
```bash
python scripts/audit.py --json > /tmp/audit.json      # should have no blocking failures
git tag v2026.4 && git push origin v2026.4
```
Generate `CHANGELOG.md` from `git diff --stat <prev-tag>..HEAD -- content/all` (added, updated and removed per hub), and create a GitHub Release with the counts.
