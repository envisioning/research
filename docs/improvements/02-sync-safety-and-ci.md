# 02 · Sync safety and CI

Issue: envisioning/research#6

Status: done 2026-10-01. The maintainer decided to keep the sync pushing to `main` instead of opening PRs. The guards below make a direct push safe.

## Workflow

```
cron 06:00 UTC ─► unit tests ─► sync.py --full ─► audit.py --strict ─► changes? ─► commit + push to main
                                     │                    │
                                     └─ too many deletes ─┴─ failure ─► open/update "Sync failing" issue
```

A failed step stops the job before the push, so `main` never gets a snapshot that failed a check. A successful run closes any open "Sync failing" issue.

## Changes

### `scripts/sync.py`
- `--max-delete-ratio` (default `0.02`). If the share of existing files to delete is above it, the script lists the files, writes nothing and exits 2.
- `--summary-file PATH` writes the JSON counts. The workflow puts them in the commit message.
- `--hub` mode now finds `content/all/<slug>--<hub>.md`. The old glob (`<hub>--*.md`) never matched, so `--hub` never removed stale files there.

### `scripts/audit.py`
- `--ignore CHECK` keeps a named check from failing `--strict`. The workflows ignore `score_fields_labelled` until [03](03-schema-v2.md) lands. Remove the flag then.

### `.github/workflows/sync.yml`
- Steps: unit tests, sync, audit gate, commit and push.
- A manual run takes a `max_delete_ratio` input. Raise it only after you confirm in the CMS that the deletions are intended.
- Permissions: `contents: write`, `issues: write`.

### `.github/workflows/validate.yml`
On push to `main` and on `pull_request`: unit tests and `audit.py --strict --ignore score_fields_labelled`.

Pushes made by the sync job use `GITHUB_TOKEN`, so they do not start `validate.yml`. The sync job runs the same checks itself.

### Weekly link check (optional, for SEO)
Request a sample of permalinks (or all, rate-limited) and fail on non-200. See [07-seo](07-seo.md).

## Done when
- A run with no CMS changes makes no commit.
- A run with changes makes one commit with the counts in its message.
- A run that would delete more than 2% of the files stops, pushes nothing and opens a "Sync failing" issue.
