#!/usr/bin/env python3
"""Offline audit of the published dataset.

Checks the files under content/ and indexes/ for consistency and data-quality
problems. Needs no Supabase credentials.

Usage:
    python scripts/audit.py              # human-readable report
    python scripts/audit.py --json       # machine-readable report
    python scripts/audit.py --strict     # exit 1 if any blocking check fails
    python scripts/audit.py --strict --ignore score_fields_labelled
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTENT_ALL_DIR = REPO_ROOT / "content" / "all"
CONTENT_BY_HUB_DIR = REPO_ROOT / "content" / "by-hub"
INDEXES_DIR = REPO_ROOT / "indexes"

SCORE_FIELDS = ("trl", "impact", "investment")  # exported names for metric1/2/3
DEFAULT_METRICS = (("Technology Readiness Level", 9), ("Impact", 5), ("Investment", 5))
# Hubs whose metric1/2/3 are not TRL/impact/investment, from each hub's
# research_metrics.metrics_config in the CMS. None means the hub has no such metric.
# Remove once indexes/hubs.json exports metrics_config.
HUB_METRICS = {
    "agape": (("Maturity Ring", 4), ("Systemic Leverage", 4), ("Ethical Tension", 4)),
    "cities": (("Technology Readiness Level", 9), ("Diffusion of Innovation", 5), ("Technology Life Cycle", 4)),
    "datatrends": (("Innovation Stage", 6), ("Implementation Complexity", 3), ("Urgency for Competitiveness", 3)),
    "moradia": (("Grau de Adoção", 5), ("Escala de Inclusividade", 5), ("Fricção Operacional e Cultural", 5)),
    "sakan": (("Market Maturity", 5), ("Regional Readiness", 5), ("Investment Intensity", 5)),
    "subspace": (("Technology Readiness Level", 9), ("Prominence", 5), ("Scientific Basis", 3)),
    "wonen": (("Regulatory Complexity", 5), ("Community Acceptance", 5), ("Social Value Generation", 5)),
    "xenotech": (("Citation Frequency", 5), ("Plausibility Score", 5), ("Technology Readiness Level", 9)),
}
FILLER_PHRASES = ["unprecedented", "seamless", "paradigm shift", "revolutioniz", "cutting-edge"]
MIN_HUB_SIZE = 40


def parse_entry(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    _, frontmatter, body = text.split("---\n", 2)
    data = yaml.safe_load(frontmatter) or {}
    data["_path"] = str(path.relative_to(REPO_ROOT))
    data["_text"] = text
    data["_body"] = body
    return data


def audit() -> dict[str, Any]:
    entries = [parse_entry(p) for p in sorted(CONTENT_ALL_DIR.glob("*.md"))]
    techs_index = json.loads((INDEXES_DIR / "technologies.json").read_text(encoding="utf-8"))
    hubs_index = json.loads((INDEXES_DIR / "hubs.json").read_text(encoding="utf-8"))
    manifest = json.loads((INDEXES_DIR / "run-manifest.json").read_text(encoding="utf-8"))

    all_paths = {e["_path"] for e in entries}
    index_paths = {t["canonical_path"] for t in techs_index}

    # Every by-hub file must have an identical canonical copy in content/all.
    by_hub_orphans: list[str] = []
    by_hub_diverged: list[str] = []
    by_hub_count = 0
    for path in sorted(CONTENT_BY_HUB_DIR.glob("*/*.md")):
        by_hub_count += 1
        canonical = CONTENT_ALL_DIR / f"{path.stem}--{path.parent.name}.md"
        rel = str(path.relative_to(REPO_ROOT))
        if not canonical.exists():
            by_hub_orphans.append(rel)
        elif canonical.read_text(encoding="utf-8") != path.read_text(encoding="utf-8"):
            by_hub_diverged.append(rel)
    all_missing_by_hub = sorted(
        e["_path"]
        for e in entries
        if not (CONTENT_BY_HUB_DIR / e["hub"] / f"{Path(e['_path']).stem.rsplit('--', 1)[0]}.md").exists()
    )

    hub_sizes = Counter(e["hub"] for e in entries)
    stale_hub_counts = [
        {"hub": h["slug"], "index": h["technology_count"], "files": hub_sizes.get(h["slug"], 0)}
        for h in hubs_index
        if h["technology_count"] != hub_sizes.get(h["slug"], 0)
    ]

    score_missing: dict[str, list[str]] = defaultdict(list)
    score_out_of_range: list[dict[str, Any]] = []
    for e in entries:
        metrics = HUB_METRICS.get(e["hub"], DEFAULT_METRICS)
        for field, metric in zip(SCORE_FIELDS, metrics):
            if metric is None:
                continue
            value = e.get(field)
            if value is None:
                score_missing[field].append(e["_path"])
            elif not 1 <= value <= metric[1]:
                score_out_of_range.append({"path": e["_path"], "field": field, "metric": metric[0], "value": value})

    mislabelled = {
        hub: {f: (m[0] if m else None) for f, m in zip(SCORE_FIELDS, metrics)}
        for hub, metrics in sorted(HUB_METRICS.items())
        if hub in hub_sizes and metrics != DEFAULT_METRICS
    }

    # Impact skew is only meaningful where metric2 really is impact.
    impact = Counter(
        e.get("impact") for e in entries if e["hub"] not in HUB_METRICS and e.get("impact") is not None
    )
    impact_total = sum(impact.values()) or 1

    slug_hubs: dict[str, list[str]] = defaultdict(list)
    for e in entries:
        slug_hubs[str(e["slug"])].append(e["hub"])
    duplicates = {s: sorted(h) for s, h in slug_hubs.items() if len(h) > 1}

    opaque_collections = sorted(
        {(e["hub"], e["collection"]) for e in entries if re.fullmatch(r"[A-Za-z0-9_-]{22}", str(e.get("collection")))}
    )

    filler = {p: sum(1 for e in entries if p in e["_body"].lower()) for p in FILLER_PHRASES}

    checks = {
        # Blocking: the published files disagree with each other.
        "index_matches_files": {
            "blocking": True,
            "ok": all_paths == index_paths and manifest["technology_count"] == len(entries),
            "files": len(entries),
            "index_rows": len(techs_index),
            "manifest_count": manifest["technology_count"],
            "files_not_in_index": sorted(all_paths - index_paths),
            "index_not_in_files": sorted(index_paths - all_paths),
        },
        "by_hub_mirrors_all": {
            "blocking": True,
            "ok": not (by_hub_orphans or by_hub_diverged or all_missing_by_hub),
            "by_hub_files": by_hub_count,
            "orphans": by_hub_orphans,
            "diverged": by_hub_diverged,
            "all_without_by_hub": all_missing_by_hub,
        },
        "hub_counts_current": {"blocking": True, "ok": not stale_hub_counts, "stale": stale_hub_counts},
        "scores_in_range": {"blocking": True, "ok": not score_out_of_range, "out_of_range": score_out_of_range},
        "score_fields_labelled": {
            "blocking": True,
            "ok": not mislabelled,
            "hubs": len(mislabelled),
            "entries": sum(hub_sizes[h] for h in mislabelled),
            "actual_metrics": mislabelled,
        },
        # Non-blocking: data-quality work items.
        "scores_present": {
            "blocking": False,
            "ok": not score_missing,
            "missing_by_field": {f: len(p) for f, p in score_missing.items()},
            "missing_by_hub": {
                f: dict(Counter(p.rsplit("--", 1)[1][:-3] for p in paths)) for f, paths in score_missing.items()
            },
        },
        "impact_distribution": {
            "blocking": False,
            "ok": (impact[4] + impact[5]) / impact_total <= 0.5,
            "share_4_or_5": round((impact[4] + impact[5]) / impact_total, 3),
            "counts": dict(sorted(impact.items())),
        },
        "images_present": {
            "blocking": False,
            "ok": all(e.get("image_url") for e in entries),
            "missing_by_hub": dict(Counter(e["hub"] for e in entries if not e.get("image_url")).most_common()),
        },
        "cross_hub_duplicates": {
            "blocking": False,
            "ok": not duplicates,
            "count": len(duplicates),
            "top": dict(sorted(duplicates.items(), key=lambda kv: -len(kv[1]))[:20]),
        },
        "collections_labelled": {
            "blocking": False,
            "ok": not opaque_collections,
            "opaque": [f"{h}:{c}" for h, c in opaque_collections],
        },
        "hub_sizes": {
            "blocking": False,
            "ok": min(hub_sizes.values()) >= MIN_HUB_SIZE,
            "below_min": {h: n for h, n in sorted(hub_sizes.items(), key=lambda kv: kv[1]) if n < MIN_HUB_SIZE},
            "empty_hubs": [h["slug"] for h in hubs_index if hub_sizes.get(h["slug"], 0) == 0],
        },
        "filler_phrases": {"blocking": False, "ok": True, "entries_containing": filler},
    }
    return {"snapshot_timestamp": manifest.get("snapshot_timestamp"), "hub_count": len(hub_sizes), "checks": checks}


def print_report(report: dict[str, Any]) -> None:
    print(f"Snapshot: {report['snapshot_timestamp']}  hubs with entries: {report['hub_count']}\n")
    for name, check in report["checks"].items():
        status = "PASS" if check["ok"] else ("FAIL" if check["blocking"] else "WARN")
        print(f"[{status}] {name}")
        for key, value in check.items():
            if key in {"ok", "blocking"}:
                continue
            if isinstance(value, list):
                print(f"    {key}: {len(value)}")
                for item in value[:10]:
                    print(f"      - {item}")
                if len(value) > 10:
                    print(f"      ... {len(value) - 10} more (use --json)")
            else:
                print(f"    {key}: {value}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit the published research dataset")
    parser.add_argument("--json", action="store_true", help="Print the full report as JSON")
    parser.add_argument("--strict", action="store_true", help="Exit 1 if any blocking check fails")
    parser.add_argument(
        "--ignore", action="append", default=[], metavar="CHECK", help="Do not let this check fail --strict"
    )
    args = parser.parse_args()

    report = audit()
    unknown = set(args.ignore) - set(report["checks"])
    if unknown:
        parser.error(f"unknown check: {', '.join(sorted(unknown))}")
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print_report(report)

    failed = [n for n, c in report["checks"].items() if c["blocking"] and not c["ok"] and n not in args.ignore]
    return 1 if args.strict and failed else 0


if __name__ == "__main__":
    sys.exit(main())
