# 02 · Sync safety and CI

Issue: envisioning/research#6

## Target workflow

```
cron 06:00 UTC ─► sync.py --full ─► changes? ─► branch sync/<date> ─► PR with counts
                         │                                              │
                         └─ failure ─► open/update "Sync failing" issue  └─ validate.yml must pass
```

## Changes

### `scripts/sync.py`
- Add `--max-delete-ratio` (default `0.02`). Before applying changes, if `len(stale_files) / len(existing_files)` is above it, exit non-zero with the list of files.
- Add `--summary-file PATH`, which writes the JSON counts so the workflow can put them in the PR body.

### `.github/workflows/sync.yml`
- After the sync, use `peter-evans/create-pull-request@v6` (branch `sync/auto`, title `chore(sync): CMS snapshot <date>`, body from the summary file), not `git push`.
- Add a step with `if: failure()` that opens or updates an issue titled "Sync failing" with the run URL (`actions/github-script`).
- Permissions: `contents: write`, `pull-requests: write`, `issues: write`.

### `.github/workflows/validate.yml` (new)
On `pull_request`:
```yaml
- run: pip install -r requirements.txt
- run: python -m unittest scripts.test_sync
- run: python scripts/audit.py --strict
```

### Weekly link check (optional, for SEO)
Request a sample of permalinks (or all, rate-limited) and fail on non-200. See [07-seo](07-seo.md).

## Done when
- A scheduled run with no CMS changes produces no PR.
- A run with changes produces one PR with counts, and CI is green on it.
- Deleting a test CMS row on a staging project produces a PR that removes exactly that file.
