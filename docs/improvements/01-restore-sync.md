# 01 · Restore the sync safely

Issues: envisioning/research#3, envisioning/research#4, envisioning/research-app#3, envisioning/research-app#4

The scheduled sync has never succeeded. If it is fixed naively, it deletes anything that isn't in the CMS and reverts hand edits. Do these steps in order.

## 1. Audit the current repo

```bash
python -m pip install -r requirements.txt
python scripts/audit.py            # report
python scripts/audit.py --json > /tmp/audit-before.json
```

Keep `audit-before.json`: it lists every orphan, diverged and unindexed file.

## 2. Make sure the CMS has every deliberate edit

For each item in `files_not_in_index`, `by_hub_mirrors_all.orphans` and `by_hub_mirrors_all.diverged`:

- Check the CMS has the row (`research.slug` = hub, `technologies.original_id` = slug) with the intended text.
- Pay particular attention to:
  - `xenotech/spacetime-density-propulsion-systems` (the #1 fix);
  - the three diverged `spore` entries;
  - the image removals and `foundations` → `applications` changes in commits `1dee3ea` and `e7423f1`.

Fix gaps **in the CMS** (admin UI or a reviewed SQL update), never by editing Markdown here.

## 3. Fix credentials

Repo → Settings → Secrets and variables → Actions:

| Secret | Value |
|---|---|
| `SUPABASE_URL` | CMS project URL |
| `SUPABASE_KEY` | anon key (enough if row-level security allows reading published rows); never the service-role key |

Check locally first:

```bash
export SUPABASE_URL=... SUPABASE_KEY=...
python scripts/sync.py --full --dry-run
```

## 4. Read the dry run

The JSON summary prints `created`, `updated`, `deleted`, `unchanged`.

- `deleted` should be 0, or exactly the files you have decided should go (for example duplicates you removed in the CMS on purpose).
- For `updated`, compare a sample with `git diff` after a real run on a scratch branch:

```bash
git switch -c sync/first-run
python scripts/sync.py --full
git diff --stat
python scripts/audit.py --strict   # consistency checks should now pass
```

`score_fields_labelled` will keep failing until the schema fix in 03 lands. Every other blocking check should pass.

## 5. Merge and re-enable

Open a PR from `sync/first-run`, review it and merge. Re-enable the workflow (Actions → Supabase Markdown Sync → Enable). Before leaving it on a schedule, finish [02](02-sync-safety-and-ci.md) so later runs open PRs instead of pushing straight to `main`.
