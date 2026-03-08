# Hubs updated by the import script (from run log)

When the OSS → CMS import script ran (before the insert-only change), it **updated** existing `technologies` rows in these hubs. Those rows had their title, summary, description, metric1/2/3, collection_label, and image overwritten from OSS markdown.

**From your run log:**

| Hub      | Inserted | Updated |
|----------|----------|---------|
| aegis    | 14       | **57**  |
| agape    | 0        | **83**  |
| agora    | 0        | **74**  |
| altitude | 11       | **67**  |
| apogee   | 9        | **64**  |
| atlas    | 7        | **52**  |
| atmos    | 10       | **55**  |
| aura     | 0        | **53**  |
| axiom    | (log truncated) | (52 techs total) |

**Hubs with updates confirmed from this log:** aegis, agape, agora, altitude, apogee, atlas, atmos, aura.

The log cuts off at **axiom**. The script processes hubs in alphabetical order, so **axiom** and every hub after it (beacon, cities, continuum, cortex, … through xenotech) would also have been processed. If the run completed, each of those hubs would have had either inserts only, updates only, or both—same pattern as above.

To get the full list of which hubs had updates and how many, paste the rest of the log (from axiom through the final summary). Then you’ll have the exact set of hubs and row counts to consider for a restore.
