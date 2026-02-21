# Fallout Wiki Data Pipeline

This pipeline automatically discovers and ingests new data from `https://fallout.fandom.com/wiki` into `database-en.json`.

## What It Does
- Crawls wiki pages from curated seeds with internal-link expansion.
- Normalizes raw pages into app schema candidates.
- Auto-merges candidates into `database-en.json`.
- Appends source provenance to `scripts/data-sources.jsonl`.
- Writes run metrics to `scripts/reports/last_run_summary.json`.

## Commands
Run from repository root:

```bash
python scripts/scrape_fallout_wiki.py --seeds scripts/config/seeds.json --max-depth 2 --out tmp/raw_pages.jsonl
python scripts/normalize_fallout_records.py --in tmp/raw_pages.jsonl --mapping scripts/config/mapping_rules.json --out tmp/candidates.jsonl
python scripts/merge_into_database.py --db database-en.json --in tmp/candidates.jsonl --provenance scripts/data-sources.jsonl --conflict prefer_newer --canon mainline,tv
```

## Policy Defaults
- Publish mode: direct merge into `database-en.json`.
- Crawl breadth: seed + 2 hops.
- Canon: `mainline,tv`.
- Conflict policy: `prefer_newer`.
- Provenance storage: sidecar JSONL, not inline in database records.

## Files
- `scripts/config/seeds.json`: seed page list.
- `scripts/config/mapping_rules.json`: extraction/mapping heuristics.
- `scripts/data-sources.jsonl`: append-only provenance records.
- `scripts/reports/last_run_summary.json`: latest run totals and skip reasons.

## Notes
- The crawler uses MediaWiki API endpoints for structured retrieval.
- Only namespace-0 article links are followed.
- Exclusion patterns (user/talk/file/template/category/mod pages) are configured in `mapping_rules.json`.
- This phase updates EN only. PL translation flow is intentionally out of scope.

