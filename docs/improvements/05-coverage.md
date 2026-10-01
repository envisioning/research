# 05 · Coverage

Issues: envisioning/research#12 · envisioning/research-app#9

## Hub sizes
`python scripts/audit.py` → `hub_sizes.below_min` (threshold 40).

For each thin hub (impulse, harvest, stride, solace, vector, cradle, synapse, polis, vitals, vortex, eclipse), decide:

| Option | When |
|---|---|
| Grow to 40+ entries | the topic has search demand and fits the business |
| Merge into a neighbouring hub | heavy overlap (e.g. harvest ↔ spore, vitals ↔ helix) |
| Freeze as an archive | client project that's finished; keep it published but mark it not maintained |

Decide on `lexicon` (0 entries) and the local-data hubs coconut, democracy and wennink in app#9.

## Quarterly gap analysis
1. For each hub, build a reference list:
   - Wikipedia "List of emerging technologies" (see `docs/wikipedia-list-we-had.md`);
   - WEF Top 10 Emerging Technologies, OECD and Gartner hype cycle entries for the domain;
   - **search demand**: Search Console queries reaching the hub that have no matching page, plus keyword-tool volume for the hub topic.
2. Match each item against existing titles and embeddings, and keep only those with no match.
3. Create the remaining items as **unpublished** CMS drafts with enrichment (description, evidence, image, scores).
4. An editor reviews and publishes them.
5. Record what was added in the quarterly CHANGELOG.

## Languages
moradia is Portuguese (pt-BR). Add `language` to the hub record (see 03) so users of the data and the site's `hreflang` handle it correctly.
