# 07 · SEO and AI visibility

Issues: envisioning/research#14, #10, #11 · envisioning/research-app#5, #6

## How the research data serves SEO
- **envisioning.com/<hub>/<slug>** (served by research-app through the envisioning.com proxy) is where search ranking happens: about 3,500 long-tail technology pages plus 58 hub landing pages.
- **This repo** supports that in three ways: it is a source of links back to envisioning.com (every `permalink`), it can be listed in Google Dataset Search, and AI crawlers read GitHub, which lets AI answers cite Envisioning.

Everything else in this plan affects ranking: duplicate pages compete with each other, missing dates weaken freshness signals, unlabelled pseudoscience lowers trust in the whole site, and empty scores and images make thin pages.

## Site checklist (research-app)
| # | Item | Status | Issue |
|---|---|---|---|
| 1 | Per-hub sitemaps live, absolute URLs, `lastmod` from `updated_at` | **off** (`app/[slug]/sitemap.old`) | app#5 |
| 2 | envisioning.com robots.txt / sitemap index lists hub sitemaps | to check | app#5 |
| 3 | `rel=canonical` → `https://www.envisioning.com/<hub>/<slug>` | to check (in `@envisioning/app`) | app#6 |
| 4 | Vercel app host is `noindex` | to check | app#6 |
| 5 | `meta_description` on 100% of published rows | to measure | app#6 |
| 6 | JSON-LD (`Article`/`DefinedTerm` + `BreadcrumbList`, `dateModified`) | to check | app#6 |
| 7 | `og:image` on every page (254 entries have no image) | gap | app#6, research#9 |
| 8 | Cross-hub duplicates differentiated or canonicalised | 99 groups | research#10 |
| 9 | Speculative pages labelled, lowest tier `noindex` | not started | research#11 |
| 10 | "Last reviewed" date visible on pages | not started | research#13 |
| 11 | `hreflang`/`lang` correct for moradia (pt-BR) | to check | research#12 |

## Dataset checklist (this repo)
| # | Item | How |
|---|---|---|
| 1 | Every permalink returns 200 | weekly link-check job (see 02) |
| 2 | No indexable copy of `content/` on another domain | if this repo is deployed (it has a `vercel.json`), send `X-Robots-Tag: noindex` for `/content/*` or don't serve it |
| 3 | Attribution in every body | end each body with `Source: [Envisioning](<permalink>)` (add in `render_technology_markdown`) |
| 4 | Dataset Search listing | landing page at envisioning.com/research with schema.org `Dataset` JSON-LD (name, description, license MIT, `distribution` → this repo's releases, `creator` Envisioning) |
| 5 | Machine-readable index for AI | `indexes/technologies.jsonl` + `llms.txt` listing hubs and permalinks |

## Measuring
Monthly, from Search Console (property envisioning.com, filtered by `/<hub>/`):
- indexed vs. submitted pages per hub (after sitemaps return);
- impressions and clicks per hub, plus the top queries with no matching page (feeds the gap analysis in 05);
- pages with **zero impressions after 90 days**: rewrite, merge into a canonical page (research#10) or unpublish.

Record the before numbers when sitemaps go live so the effect of each phase can be measured.
