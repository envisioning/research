#!/usr/bin/env python3
"""Supabase -> Markdown mirror sync.

Exports published technologies into:
- content/all
- content/by-hub
- content/hubs.md
- indexes/*.json

Designed to be deterministic and idempotent.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from urllib.parse import quote
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTENT_ALL_DIR = REPO_ROOT / "content" / "all"
CONTENT_BY_HUB_DIR = REPO_ROOT / "content" / "by-hub"
HUBS_MD_PATH = REPO_ROOT / "content" / "hubs.md"
INDEXES_DIR = REPO_ROOT / "indexes"


def env_first(*keys: str) -> str | None:
    for key in keys:
        value = os.getenv(key)
        if value:
            return value
    return None


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9-]+", "-", value.strip().lower())
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug or "untitled"


def humanize_slug(value: str | None) -> str:
    if not value:
        return "Uncategorized"
    return " ".join(part.capitalize() for part in value.replace("_", "-").split("-"))


def build_permalink(hub_slug: str, original_id: str) -> str:
    # original_id values are typically slug-safe; quote defensively
    return f"https://www.envisioning.com/{quote(hub_slug, safe='')}/{quote(original_id, safe='')}"


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("\r\n", "\n").replace("\r", "\n")


@dataclass
class SupabaseClient:
    url: str
    key: str
    timeout: int = 60

    def __post_init__(self) -> None:
        self.base_url = f"{self.url.rstrip('/')}/rest/v1"
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Accept": "application/json",
        }

    def fetch_all(
        self,
        table: str,
        select: str,
        filters: dict[str, str] | None = None,
        order: str | None = None,
        page_size: int = 1000,
    ) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        offset = 0
        while True:
            params: dict[str, str | int] = {
                "select": select,
                "limit": page_size,
                "offset": offset,
            }
            if filters:
                params.update(filters)
            if order:
                params["order"] = order
            response = requests.get(
                f"{self.base_url}/{table}",
                headers=self.headers,
                params=params,
                timeout=self.timeout,
            )
            if response.status_code >= 400:
                raise RuntimeError(
                    f"Supabase query failed for {table}: {response.status_code} {response.text}"
                )
            chunk = response.json()
            if not isinstance(chunk, list):
                raise RuntimeError(f"Unexpected response for {table}: {chunk}")
            out.extend(chunk)
            if len(chunk) < page_size:
                break
            offset += page_size
        return out


def in_filter(values: list[str]) -> str:
    escaped = [v.replace(",", "") for v in values]
    return f"in.({','.join(escaped)})"


def chunked(values: list[str], size: int) -> list[list[str]]:
    return [values[i : i + size] for i in range(0, len(values), size)]


def fetch_data(client: SupabaseClient, hub_slug: str | None = None) -> dict[str, Any]:
    research_filters: dict[str, str] = {}
    if hub_slug:
        research_filters["slug"] = f"eq.{hub_slug}"

    research = client.fetch_all(
        "research",
        "id,slug,title,summary,welcome,about,indicator_explainers",
        filters=research_filters,
        order="slug.asc",
    )
    research = [r for r in research if r.get("slug")]
    research_ids = [str(r["id"]) for r in research]
    if not research_ids:
        return {
            "research": [],
            "technologies": [],
            "sources": [],
            "technology_tags": [],
            "tags": [],
            "research_metrics": [],
        }

    technologies = client.fetch_all(
        "technologies",
        "id,original_id,research_id,title,summary,description,image,"
        "collection_id,collection_label,metric1,metric2,metric3,published,created_at,updated_at",
        filters={
            "published": "is.true",
            "research_id": in_filter(research_ids),
        },
        order="research_id.asc,title.asc",
    )

    tech_ids = [str(t["id"]) for t in technologies]

    sources: list[dict[str, Any]] = []
    technology_tags: list[dict[str, Any]] = []
    if tech_ids:
        for tech_chunk in chunked(tech_ids, 100):
            sources.extend(
                client.fetch_all(
                    "technologies_sources",
                    "technology_id,url,title,summary,position",
                    filters={"technology_id": in_filter(tech_chunk)},
                    order="position.asc",
                )
            )
            technology_tags.extend(
                client.fetch_all(
                    "technology_tags",
                    "technology_id,tag_id",
                    filters={"technology_id": in_filter(tech_chunk)},
                )
            )

    tag_ids = sorted(
        {
            str(row.get("tag_id"))
            for row in technology_tags
            if row.get("tag_id") is not None
        }
    )
    tags: list[dict[str, Any]] = []
    if tag_ids:
        for tag_chunk in chunked(tag_ids, 200):
            tags.extend(
                client.fetch_all(
                    "tags",
                    "id,research_id,tag_type,tag_id,label,color,position,description,summary",
                    filters={"id": in_filter(tag_chunk)},
                    order="position.asc",
                )
            )

    research_metrics = client.fetch_all(
        "research_metrics",
        "id,research_id,collection_id,updated_at,metrics_config",
        filters={
            "research_id": in_filter(research_ids),
            "collection_id": "is.null",
        },
        order="updated_at.desc",
    )

    return {
        "research": research,
        "technologies": technologies,
        "sources": sources,
        "technology_tags": technology_tags,
        "tags": tags,
        "research_metrics": research_metrics,
    }


def snapshot_timestamp(data: dict[str, Any]) -> str:
    candidates: list[str] = []
    for tech in data.get("technologies", []):
        if tech.get("updated_at"):
            candidates.append(str(tech["updated_at"]))
        elif tech.get("created_at"):
            candidates.append(str(tech["created_at"]))
    for metric in data.get("research_metrics", []):
        if metric.get("updated_at"):
            candidates.append(str(metric["updated_at"]))
    return max(candidates) if candidates else "unknown"


def build_enriched(data: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    research_by_id = {str(r["id"]): r for r in data["research"]}

    metrics_latest_by_research: dict[str, dict[str, Any]] = {}
    for row in sorted(
        data.get("research_metrics", []),
        key=lambda x: str(x.get("updated_at") or ""),
        reverse=True,
    ):
        rid = str(row.get("research_id"))
        if rid not in metrics_latest_by_research:
            metrics_latest_by_research[rid] = row

    sources_by_tech: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for source in data.get("sources", []):
        tid = str(source.get("technology_id"))
        sources_by_tech[tid].append(source)
    for tid in list(sources_by_tech.keys()):
        sources_by_tech[tid] = sorted(
            sources_by_tech[tid],
            key=lambda s: (s.get("position") if s.get("position") is not None else 999999, str(s.get("url") or "")),
        )

    tag_by_row_id = {str(t["id"]): t for t in data.get("tags", [])}
    tag_map_by_tech: dict[str, dict[str, list[dict[str, str]]]] = defaultdict(
        lambda: {"tag1": [], "tag2": [], "tag3": []}
    )
    for rel in data.get("technology_tags", []):
        tid = str(rel.get("technology_id"))
        row_id = str(rel.get("tag_id"))
        tag = tag_by_row_id.get(row_id)
        if not tag:
            continue
        tag_type = str(tag.get("tag_type") or "")
        if tag_type not in {"tag1", "tag2", "tag3"}:
            continue
        tag_map_by_tech[tid][tag_type].append(
            {
                "id": str(tag.get("tag_id") or ""),
                "label": str(tag.get("label") or ""),
            }
        )

    for tid in list(tag_map_by_tech.keys()):
        for tag_type in ("tag1", "tag2", "tag3"):
            tag_map_by_tech[tid][tag_type] = sorted(
                tag_map_by_tech[tid][tag_type], key=lambda t: (t["label"], t["id"])
            )

    enriched: list[dict[str, Any]] = []
    hubs: list[dict[str, Any]] = []

    for research in sorted(data["research"], key=lambda x: str(x.get("slug") or "")):
        hubs.append(
            {
                "id": str(research["id"]),
                "slug": str(research.get("slug") or ""),
                "title": normalize_text(research.get("title") or research.get("slug") or ""),
                "topic_description": normalize_text(research.get("summary") or ""),
                "about": normalize_text(research.get("about") or ""),
                "indicator_explainers": research.get("indicator_explainers"),
                "metrics_config": metrics_latest_by_research.get(str(research["id"]), {}).get("metrics_config"),
            }
        )

    for tech in sorted(
        data["technologies"],
        key=lambda t: (
            str(research_by_id.get(str(t.get("research_id")), {}).get("slug") or ""),
            str(t.get("original_id") or t.get("id") or ""),
        ),
    ):
        research = research_by_id.get(str(tech.get("research_id")))
        if not research:
            continue
        internal_id = str(tech.get("id"))
        original_id = str(tech.get("original_id") or tech.get("id"))
        hub_slug = str(research.get("slug") or "")
        hub_title = str(research.get("title") or hub_slug)
        collection_id = str(tech.get("collection_id") or "uncategorized")
        collection_label = str(tech.get("collection_label") or humanize_slug(collection_id))
        tags_for_tech = tag_map_by_tech.get(internal_id, {"tag1": [], "tag2": [], "tag3": []})

        normalized_sources = [
            {
                "url": normalize_text(src.get("url") or ""),
                "title": normalize_text(src.get("title") or ""),
                "summary": normalize_text(src.get("summary") or ""),
                "position": src.get("position"),
            }
            for src in sources_by_tech.get(internal_id, [])
        ]

        enriched.append(
            {
                "id": internal_id,
                "original_id": original_id,
                "hub_slug": hub_slug,
                "hub_title": hub_title,
                "title": normalize_text(tech.get("title") or "Untitled"),
                "summary": normalize_text(tech.get("summary") or ""),
                "description": normalize_text(tech.get("description") or ""),
                "image": tech.get("image"),
                "collection_id": collection_id,
                "collection_label": normalize_text(collection_label),
                "metric1": tech.get("metric1"),
                "metric2": tech.get("metric2"),
                "metric3": tech.get("metric3"),
                "published": bool(tech.get("published")),
                "created_at": tech.get("created_at"),
                        "sources": normalized_sources,
                "tags": tags_for_tech,
            }
        )

    return enriched, hubs


def yaml_frontmatter(data: dict[str, Any]) -> str:
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True).strip()


def render_technology_markdown(tech: dict[str, Any]) -> str:
    frontmatter = {
        "slug": tech["original_id"],
        "hub": tech["hub_slug"],
        "title": tech["title"],
        "summary": tech["summary"],
        "permalink": build_permalink(tech["hub_slug"], tech["original_id"]),
        "collection": tech["collection_id"],
        "trl": tech.get("metric1"),
        "impact": tech.get("metric2"),
        "investment": tech.get("metric3"),
        "image_url": tech.get("image"),
    }

    lines = [
        "# " + tech["title"],
        "",
        "## Summary",
        "",
        (tech.get("summary") or "").strip() or "_No summary available._",
        "",
        "## Description",
        "",
        (tech.get("description") or "").strip() or "_No description available._",
    ]

    body = "\n".join(lines).strip() + "\n"
    return f"---\n{yaml_frontmatter(frontmatter)}\n---\n\n{body}"


def render_hubs_markdown(hubs: list[dict[str, Any]], techs: list[dict[str, Any]], snapshot_ts: str) -> str:
    count_by_slug: dict[str, int] = defaultdict(int)
    for tech in techs:
        count_by_slug[str(tech["hub_slug"])] += 1

    lines = [
        "# Research Hubs",
        "",
        "Source of truth: Supabase `research` table.",
        f"Snapshot timestamp: `{snapshot_ts}`",
        "",
    ]

    for hub in sorted(hubs, key=lambda h: h["slug"]):
        slug = hub["slug"]
        title = hub["title"]
        desc = hub.get("topic_description") or ""
        lines.extend(
            [
                f"## {title} ({count_by_slug.get(slug, 0)})",
                desc.strip() if str(desc).strip() else "_No topic description available._",
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def build_indexes(
    hubs: list[dict[str, Any]], techs: list[dict[str, Any]], snapshot_ts: str
) -> dict[str, Any]:
    hubs_sorted = sorted(hubs, key=lambda h: h["slug"])
    techs_sorted = sorted(techs, key=lambda t: (t["hub_slug"], t["original_id"]))

    technologies_index = [
        {
            "id": t["id"],
            "original_id": t["original_id"],
            "title": t["title"],
            "hub_slug": t["hub_slug"],
            "hub_title": t["hub_title"],
            "collection": t["collection_id"],
            "metric1": t.get("metric1"),
            "metric2": t.get("metric2"),
            "metric3": t.get("metric3"),
            "image_url": t.get("image"),
            "updated_at": t.get("updated_at"),
            "canonical_path": f"content/all/{slugify(t['original_id'])}--{t['hub_slug']}.md",
            "permalink": build_permalink(t["hub_slug"], t["original_id"]),
        }
        for t in techs_sorted
    ]

    hubs_index = []
    techs_by_slug: dict[str, int] = defaultdict(int)
    for t in techs_sorted:
        techs_by_slug[t["hub_slug"]] += 1

    for h in hubs_sorted:
        hubs_index.append(
            {
                "id": h["id"],
                "slug": h["slug"],
                "title": h["title"],
                "topic_description": h.get("topic_description") or "",
                "technology_count": techs_by_slug.get(h["slug"], 0),
            }
        )

    tag_counts_by_hub: dict[str, dict[str, dict[str, int]]] = defaultdict(
        lambda: {"tag1": defaultdict(int), "tag2": defaultdict(int), "tag3": defaultdict(int)}
    )
    for t in techs_sorted:
        slug = t["hub_slug"]
        for tag_type in ("tag1", "tag2", "tag3"):
            for tag in t["tags"][tag_type]:
                tag_counts_by_hub[slug][tag_type][tag["label"]] += 1

    tags_index: list[dict[str, Any]] = []
    for slug in sorted(tag_counts_by_hub.keys()):
        entry: dict[str, Any] = {"hub_slug": slug}
        for tag_type in ("tag1", "tag2", "tag3"):
            entry[tag_type] = [
                {"label": label, "count": count}
                for label, count in sorted(tag_counts_by_hub[slug][tag_type].items())
            ]
        tags_index.append(entry)

    run_manifest = {
        "snapshot_timestamp": snapshot_ts,
        "hub_count": len(hubs_index),
        "technology_count": len(technologies_index),
    }

    return {
        "technologies": technologies_index,
        "hubs": hubs_index,
        "tags": tags_index,
        "run_manifest": run_manifest,
    }


def dump_json_stable(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def list_files_recursive(base: Path, pattern: str) -> set[Path]:
    if not base.exists():
        return set()
    return {p for p in base.glob(pattern) if p.is_file()}


def planned_full_stale(expected_paths: set[Path]) -> set[Path]:
    stale = set()
    stale |= list_files_recursive(CONTENT_ALL_DIR, "*.md")
    stale |= list_files_recursive(CONTENT_BY_HUB_DIR, "*/*.md")
    stale |= list_files_recursive(INDEXES_DIR, "*.json")
    if HUBS_MD_PATH.exists():
        stale.add(HUBS_MD_PATH)
    return stale - expected_paths


def planned_hub_stale(hub_slug: str, expected_paths: set[Path]) -> set[Path]:
    stale = set(CONTENT_ALL_DIR.glob(f"{hub_slug}--*.md"))
    hub_dir = CONTENT_BY_HUB_DIR / hub_slug
    if hub_dir.exists():
        stale |= {p for p in hub_dir.glob("*.md") if p.is_file()}
    return stale - expected_paths


def apply_file_updates(
    expected_files: dict[Path, str], delete_files: set[Path], dry_run: bool
) -> dict[str, int]:
    created = 0
    updated = 0
    deleted = 0
    unchanged = 0

    for path, content in sorted(expected_files.items(), key=lambda kv: str(kv[0])):
        if path.exists():
            current = path.read_text(encoding="utf-8")
            if current == content:
                unchanged += 1
                continue
            updated += 1
        else:
            created += 1

        if not dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

    for path in sorted(delete_files, key=str):
        if path.exists():
            deleted += 1
            if not dry_run:
                path.unlink()

    # Clean empty by-hub subdirs on non-dry full runs.
    if not dry_run and CONTENT_BY_HUB_DIR.exists():
        for hub_dir in sorted(CONTENT_BY_HUB_DIR.glob("*"), key=str):
            if hub_dir.is_dir() and not any(hub_dir.iterdir()):
                hub_dir.rmdir()

    return {
        "created": created,
        "updated": updated,
        "deleted": deleted,
        "unchanged": unchanged,
    }


def build_expected_files(
    techs: list[dict[str, Any]], hubs: list[dict[str, Any]], snapshot_ts: str, mode: str
) -> dict[Path, str]:
    expected: dict[Path, str] = {}

    for tech in techs:
        original_slug = slugify(tech["original_id"])
        canonical_filename = f"{original_slug}--{tech['hub_slug']}.md"
        canonical_path = CONTENT_ALL_DIR / canonical_filename
        in_hub_path = CONTENT_BY_HUB_DIR / tech["hub_slug"] / f"{original_slug}.md"

        rendered = render_technology_markdown(tech)
        expected[canonical_path] = rendered
        expected[in_hub_path] = rendered

    if mode == "full":
        expected[HUBS_MD_PATH] = render_hubs_markdown(hubs, techs, snapshot_ts)
        indexes = build_indexes(hubs, techs, snapshot_ts)
        expected[INDEXES_DIR / "technologies.json"] = dump_json_stable(indexes["technologies"])
        expected[INDEXES_DIR / "hubs.json"] = dump_json_stable(indexes["hubs"])
        expected[INDEXES_DIR / "tags.json"] = dump_json_stable(indexes["tags"])
        expected[INDEXES_DIR / "run-manifest.json"] = dump_json_stable(indexes["run_manifest"])

    return expected


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync Supabase technologies to markdown mirror")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--full", action="store_true", help="Sync all hubs and rebuild global indexes")
    mode.add_argument("--hub", type=str, help="Sync only one hub slug")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without writing files")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    mode = "hub" if args.hub else "full"

    url = env_first("SUPABASE_URL", "NEXT_PUBLIC_SUPABASE_URL_CMS", "NEXT_PUBLIC_SUPABASE_URL")
    key = env_first("SUPABASE_KEY", "SUPABASE_ANON_KEY", "NEXT_PUBLIC_SUPABASE_ANON_KEY_CMS", "NEXT_PUBLIC_SUPABASE_ANON_KEY")

    if not url or not key:
        raise RuntimeError(
            "Missing Supabase credentials. Set SUPABASE_URL and SUPABASE_KEY (or NEXT_PUBLIC_*_CMS variants)."
        )

    client = SupabaseClient(url=url, key=key)
    raw = fetch_data(client, hub_slug=args.hub)
    techs, hubs = build_enriched(raw)
    snapshot_ts = snapshot_timestamp(raw)

    expected_files = build_expected_files(techs, hubs, snapshot_ts, mode=mode)
    expected_paths = set(expected_files.keys())

    if mode == "full":
        stale_files = planned_full_stale(expected_paths)
    else:
        assert args.hub is not None
        stale_files = planned_hub_stale(args.hub, expected_paths)

    stats = apply_file_updates(expected_files, stale_files, dry_run=args.dry_run)

    print(json.dumps({
        "mode": mode,
        "hub": args.hub,
        "dry_run": args.dry_run,
        "snapshot_timestamp": snapshot_ts,
        "hub_count": len(hubs),
        "technology_count": len(techs),
        **stats,
    }, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
