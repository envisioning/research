# Restore only the overwritten `technologies` rows (no full DB rollback)

Supabase does **not** support restoring a single table or subset of rows. A normal restore rolls back the **entire** database. To fix only the overwritten technology rows:

---

## 1. Restore to a **new** project (not in-place)

- **Dashboard:** [Database Backups](https://supabase.com/dashboard/project/_/database/backups) → **Restore to a New Project** (or [Point in Time](https://supabase.com/dashboard/project/_/database/backups/pitr) if you have PITR).
- Choose a backup / time **just before** you ran the import script.
- Restore **into a new project** (clone). That gives you:
  - **Production** = current DB (with the bad updates).
  - **Restored** = new project with the good state from before the import.

You do **not** overwrite production; production stays as-is.

---

## 2. Copy only `technologies` from restored → production

After the new project is ready:

1. **Identify which rows to restore**  
   Those are the rows that were **updated** (same hub + slug as in OSS). From your log, the hubs that had updates include at least: aegis, agape, agora, altitude, apogee, atlas, atmos, aura, and the rest through xenotech (see `docs/hubs-touched-by-import-script.md`).

2. **Option A – Script (two Supabase clients)**  
   - Connect to **restored** project (read-only): list `research` by slug for those hubs, then fetch all `technologies` for those `research_id`s.
   - Connect to **production**: for each row from restored, run  
     `UPDATE technologies SET title=..., summary=..., description=..., metric1=..., metric2=..., metric3=..., collection_label=..., image=... WHERE id = $id`.
   - Match by `id` (same UUID in both projects if the clone was a full DB copy) **or** by `(research_id, original_id)` if you don’t have the same IDs.  
   - Use a **dry-run** (e.g. log what would be updated, no writes) first.

3. **Option B – SQL + export/import**  
   - In the **restored** project SQL editor, export the rows you need, e.g.:
     ```sql
     -- Export technologies for affected hubs (run in restored project, export result as CSV/JSON)
     SELECT t.id, t.research_id, t.original_id, t.title, t.summary, t.description,
            t.metric1, t.metric2, t.metric3, t.collection_label, t.image
     FROM technologies t
     JOIN research r ON r.id = t.research_id
     WHERE r.slug IN ('aegis','agape','agora','altitude','apogee','atlas','atmos','aura','axiom', ...);
     ```
   - In **production**, load that into a temporary table, then:
     ```sql
     UPDATE technologies AS prod
     SET
       title = bak.title,
       summary = bak.summary,
       description = bak.description,
       metric1 = bak.metric1,
       metric2 = bak.metric2,
       metric3 = bak.metric3,
       collection_label = bak.collection_label,
       image = bak.image
     FROM temp_technologies_restored AS bak
     WHERE prod.research_id = bak.research_id AND prod.original_id = bak.original_id;
     ```
   - Drop the temp table when done.

---

## 3. Important details

- **Same project vs new project:** If you use “Restore to a new project”, the **new** project gets new UUIDs for `research` and `technologies`. So you **cannot** match by `id` between production and restored; match by `(research_id, original_id)` by joining on `research.slug` in the restored project to get `research_id`, then `original_id` from `technologies`. In production you already have the same slugs and original_ids, so you join production `technologies` to production `research` by `research_id`, and match to the restored data by `(research.slug, technologies.original_id)`.
- **New inserts:** The import also **inserted** new rows (the “X added”). Don’t delete those in production; only **update** rows that already existed (the “Y updated”). The UPDATE approach above only touches rows that exist in both restored and production and match on (research_id, original_id).
- **Backup:** Before running any mass UPDATE in production, take a manual export of `technologies` (or at least the affected hubs) so you can revert if needed.

---

## Summary

1. Restore to a **new** project from a time before the import.  
2. Export or read from that project only the `technologies` rows for the hubs that had updates.  
3. In production, UPDATE those same rows (matched by hub + original_id) with the restored values.  
4. Leave the rest of the DB (and the newly inserted technologies) unchanged.

This way you restore only the overwritten technology entries and do not roll back the whole database.
