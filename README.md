# Envisioning Research (Open Dataset)

https://www.envisioning.com/research/

A public, open-access research dataset about emerging technologies.

This repository publishes structured technology research in Markdown and JSON, including metadata such as:

- Technology Readiness Level (`trl`)
- Impact score (`impact`)
- Investment score (`investment`)
- Hub/category context (`hub`, `collection`)
- Canonical permalink and image URL

The goal is simple: make high-quality technology research easy to browse, reuse, analyze, and remix.

## License

This dataset is published under the MIT License.

If you are republishing, remixing, or deriving from this dataset, please include attribution to Envisioning and link back to this repository.

## What This Repository Contains

- `content/all/*.md`
  Canonical technology entries.

- `content/by-hub/<hub>/*.md`
  Same technology entries grouped by research hub for easier thematic browsing.

- `content/hubs.md`
  Human-readable overview of all hubs and their topic descriptions.

- `indexes/technologies.json`
  Machine-readable index of all technologies.

- `indexes/hubs.json`
  Machine-readable index of all hubs.

- `indexes/tags.json`
  Tag distribution metadata by hub.

- `indexes/run-manifest.json`
  Snapshot-level metadata (`hub_count`, `technology_count`, timestamp).

## Entry Format

Each technology Markdown file uses YAML frontmatter + Markdown body.

### Frontmatter schema

```yaml
slug: federated-learning-consortiums
hub: synapse
title: Federated Learning Consortiums
summary: Privacy-preserving multi-organization model training networks.
permalink: https://www.envisioning.com/synapse/federated-learning-consortiums
collection: software
trl: 4
impact: 5
investment: 4
image_url: https://res.cloudinary.com/.../image.png
```

### Body schema

```md
# <Title>

## Summary
<short summary>

## Description
<full research description>
```

## Naming and Organization Conventions

### Canonical file names (`content/all`)

Files are named with this convention:

`<technology-slug>--<hub-slug>.md`

Example:

`federated-learning-consortiums--synapse.md`

This guarantees uniqueness while keeping filenames human-readable.

### Hub files (`content/by-hub`)

Inside each hub folder, files are named:

`<technology-slug>.md`

Example:

`content/by-hub/synapse/federated-learning-consortiums.md`

## How You Can Use This Dataset

### 1. Build websites or search interfaces

Use `content/all` for source content and `indexes/technologies.json` for listing/filtering.

### 2. Run quantitative analysis

Use `trl`, `impact`, `investment`, and `collection` fields to build score distributions, trend maps, and comparisons.

### 3. Build RAG / AI pipelines

Use Markdown bodies as source documents and frontmatter as retrieval metadata.

### 4. Track changes over time

Use Git history and `indexes/run-manifest.json` snapshots to compare evolving technology records.

## Quick Start

### Browse as content

- Start with `content/hubs.md`
- Navigate to `content/by-hub/<hub>`
- Use `content/all` for canonical records

### Use as data

Load JSON indexes directly:

- `indexes/technologies.json`
- `indexes/hubs.json`
- `indexes/tags.json`

## Replicating This Setup

If you want to run the same publishing pipeline for your own CMS/database:

### Prerequisites

- Python 3.9+
- Supabase project (or equivalent PostgREST endpoint)
- Read credentials for source tables

### Steps

1. Clone this repo.
2. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

3. Set environment variables:

- `SUPABASE_URL`
- `SUPABASE_KEY`

(Compatible alternatives: `NEXT_PUBLIC_SUPABASE_URL_CMS`, `NEXT_PUBLIC_SUPABASE_ANON_KEY_CMS`.)

4. Generate dataset:

```bash
python scripts/sync.py --full
```

5. Optional scoped update:

```bash
python scripts/sync.py --hub synapse
```

6. Validate without writing:

```bash
python scripts/sync.py --full --dry-run
```


## Contributing

Issues and pull requests are welcome for:

- data formatting improvements
- docs improvements
- tooling/consumption examples
- schema clarifications

If proposing schema changes, include migration notes so downstream users can adapt safely.
