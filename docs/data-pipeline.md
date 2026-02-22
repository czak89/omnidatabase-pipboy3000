# Fallout Wiki Data Pipeline

This pipeline automatically discovers and ingests new data from `https://fallout.fandom.com/wiki` into `database-en.json`.

## What It Does
- Builds expanded seeds from curated category pages.
- Crawls wiki pages from expanded seeds with internal-link expansion.
- Normalizes enriched raw pages into app schema candidates.
- Evaluates candidate quality/coverage before merge.
- Auto-merges candidates into `database-en.json` with guardrails.
- Appends source provenance to `scripts/data-sources.jsonl`.
- Writes run metrics to `scripts/reports/last_run_summary.json`.

## Commands
Run from repository root:

```bash
python scripts/build_seed_catalog.py --seeds scripts/config/seeds.json --categories scripts/config/seed_categories.json --out tmp/expanded_seeds.json
python scripts/scrape_fallout_wiki.py --seeds tmp/expanded_seeds.json --max-depth 2 --out tmp/raw_pages.jsonl
python scripts/normalize_fallout_records.py --in tmp/raw_pages.jsonl --mapping scripts/config/mapping_rules.json --thresholds scripts/config/module_thresholds.json --out tmp/candidates.jsonl
python scripts/evaluate_candidates.py --in tmp/candidates.jsonl --out scripts/reports/candidate_evaluation.json
python scripts/merge_into_database.py --db database-en.json --in tmp/candidates.jsonl --provenance scripts/data-sources.jsonl --decision-log scripts/reports/merge_decisions.jsonl --conflict prefer_newer --canon mainline,tv --similarity-threshold 0.92
```

## Policy Defaults
- Publish mode: direct merge into `database-en.json`.
- Crawl breadth: expanded seed catalog + 2 hops.
- Canon: `mainline,tv`.
- Conflict policy: `prefer_newer`.
- Run cadence: manual.
- Provenance storage: sidecar JSONL, not inline in database records.

## Files
- `scripts/config/seeds.json`: seed page list.
- `scripts/config/seed_categories.json`: category pages used for seed expansion.
- `scripts/config/mapping_rules.json`: extraction/mapping heuristics.
- `scripts/config/module_thresholds.json`: per-module confidence thresholds.
- `scripts/data-sources.jsonl`: append-only provenance records.
- `scripts/reports/merge_decisions.jsonl`: per-candidate merge decisions.
- `scripts/reports/last_run_summary.json`: latest run totals and skip reasons.
- `scripts/reports/runs/<run_id>.json`: per-run manifest snapshot.

## Notes
- The crawler uses MediaWiki API endpoints for structured retrieval (lead summary + full text + section metadata).
- Only namespace-0 article links are followed.
- Exclusion patterns (user/talk/file/template/category/mod pages) are configured in `mapping_rules.json`.
- This phase updates EN only. PL translation flow is intentionally out of scope.
