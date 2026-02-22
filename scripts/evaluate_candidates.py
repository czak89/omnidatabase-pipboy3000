#!/usr/bin/env python3
"""
Evaluate candidate quality and coverage before merge.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def norm_text(value: str) -> str:
    value = (value or "").lower().strip()
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"[^\w\s]", "", value)
    return value


def confidence_bucket(value: float) -> str:
    if value >= 0.9:
        return "0.90-1.00"
    if value >= 0.8:
        return "0.80-0.89"
    if value >= 0.7:
        return "0.70-0.79"
    if value >= 0.6:
        return "0.60-0.69"
    if value >= 0.5:
        return "0.50-0.59"
    return "<0.50"


def run(args: argparse.Namespace) -> int:
    candidates = load_jsonl(Path(args.input_path))

    module_counts = Counter()
    category_counts = Counter()
    confidence_counts = Counter()
    canon_counts = Counter()
    id_counts = Counter()
    url_counts = Counter()
    lore_counts = Counter()

    low_conf = 0
    missing_required = 0
    weak_records: List[Dict[str, Any]] = []

    for c in candidates:
        module = c.get("module", "")
        category = c.get("category_id", "")
        cid = c.get("id", "")
        url = c.get("source_url", "")
        lore = c.get("lore", "")
        conf = float(c.get("confidence", 0.0))

        if not all([module, category, cid, lore]):
            missing_required += 1
        if conf < 0.5:
            low_conf += 1
            if len(weak_records) < 20:
                weak_records.append(
                    {
                        "id": cid,
                        "module": module,
                        "category_id": category,
                        "confidence": conf,
                        "source_url": url,
                    }
                )

        module_counts[module] += 1
        category_counts[f"{module}.{category}"] += 1
        confidence_counts[confidence_bucket(conf)] += 1
        id_counts[cid] += 1
        if url:
            url_counts[url] += 1
        lore_counts[norm_text(lore)] += 1

        for tag in c.get("canon_tags", []) or []:
            canon_counts[tag] += 1

    dup_ids = sorted([k for k, v in id_counts.items() if v > 1])
    dup_urls = sorted([k for k, v in url_counts.items() if v > 1])
    dup_lore = sorted([k for k, v in lore_counts.items() if k and v > 1])

    report = {
        "run_at": utc_now_iso(),
        "input_candidates": len(candidates),
        "coverage": {
            "modules": dict(sorted(module_counts.items())),
            "module_categories": dict(sorted(category_counts.items())),
        },
        "quality": {
            "confidence_histogram": dict(sorted(confidence_counts.items())),
            "low_confidence_count": low_conf,
            "missing_required_fields_count": missing_required,
            "weak_record_samples": weak_records,
        },
        "duplicates": {
            "duplicate_id_count": len(dup_ids),
            "duplicate_url_count": len(dup_urls),
            "exact_duplicate_lore_count": len(dup_lore),
            "duplicate_id_samples": dup_ids[:25],
            "duplicate_url_samples": dup_urls[:25],
        },
        "canon_tags": dict(sorted(canon_counts.items())),
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate candidate quality before merge.")
    parser.add_argument("--in", dest="input_path", required=True, help="Candidate JSONL path")
    parser.add_argument(
        "--out",
        default="scripts/reports/candidate_evaluation.json",
        help="Evaluation report JSON output",
    )
    return parser


if __name__ == "__main__":
    raise SystemExit(run(build_parser().parse_args()))

