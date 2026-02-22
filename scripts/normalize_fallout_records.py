#!/usr/bin/env python3
"""
Normalize enriched raw Fallout Wiki crawl records into database candidate JSONL.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


FIELD_WEIGHTS = {
    "title": 4.0,
    "categories": 3.0,
    "lead_summary": 2.0,
    "full_text": 1.0,
    "sections": 1.2,
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, records: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^\w\s-]", "", value)
    value = re.sub(r"[\s-]+", "_", value).strip("_")
    return value[:80] if value else "unknown"


def first_sentences(text: str, max_sentences: int = 2) -> str:
    text = " ".join((text or "").split())
    if not text:
        return ""
    pieces = re.split(r"(?<=[.!?])\s+", text)
    out = " ".join(pieces[:max_sentences]).strip()
    return out if out else text[:360].strip()


def find_year(text: str) -> Optional[int]:
    m = re.search(r"\b(19\d{2}|20\d{2}|21\d{2}|22\d{2}|23\d{2})\b", text)
    return int(m.group(1)) if m else None


def clean_text(value: str) -> str:
    return " ".join((value or "").split()).lower()


def page_fields(page: Dict[str, Any]) -> Dict[str, str]:
    section_lines = []
    for s in page.get("sections", []) or []:
        line = s.get("line")
        if line:
            section_lines.append(str(line))
    return {
        "title": clean_text(page.get("title", "")),
        "categories": clean_text(" ".join(page.get("categories", []) or [])),
        "lead_summary": clean_text(page.get("lead_summary") or page.get("summary") or ""),
        "full_text": clean_text(page.get("full_text") or ""),
        "sections": clean_text(" ".join(section_lines)),
    }


def keyword_score(fields: Dict[str, str], keywords: List[str]) -> float:
    score = 0.0
    for kw in keywords:
        token = kw.lower()
        for field_name, text in fields.items():
            if token and token in text:
                score += FIELD_WEIGHTS.get(field_name, 1.0)
    return score


def is_excluded(page: Dict[str, Any], rules: Dict[str, Any]) -> Optional[str]:
    url = (page.get("url") or "").lower()
    title = (page.get("title") or "").lower()
    cats = " ".join(page.get("categories") or []).lower()
    for pat in rules.get("exclude_url_patterns", []):
        if pat.lower() in url:
            return "url_blocked"
    for pat in rules.get("exclude_title_patterns", []):
        if pat.lower() in title:
            return "title_blocked"
    for pat in rules.get("exclude_category_patterns", []):
        if pat.lower() in cats:
            return "category_blocked"
    return None


def infer_timeline_category(year: Optional[int], text: str) -> str:
    t = text.lower()
    if year is None:
        if "great war" in t or "nuclear exchange" in t:
            return "greatwar"
        return "modern"
    if year <= 2076:
        return "prewar"
    if year == 2077 and ("great war" in t or "bomb" in t or "nuclear" in t):
        return "greatwar"
    if year <= 2159:
        return "darkages"
    if year <= 2241:
        return "heroic"
    return "modern"


def infer_canon_tags(page: Dict[str, Any], rules: Dict[str, Any]) -> List[str]:
    fields = page_fields(page)
    text = " ".join(fields.values())
    tags = ["mainline"]
    if any(kw.lower() in text for kw in rules.get("canon_keywords", {}).get("tv", [])):
        tags.append("tv")
    return list(dict.fromkeys(tags))


def infer_module_and_category(
    page: Dict[str, Any], rules: Dict[str, Any]
) -> Tuple[Optional[str], Optional[str], float, float, float]:
    fields = page_fields(page)

    module_keywords = rules.get("module_keywords", {})
    module_scores: Dict[str, float] = {m: keyword_score(fields, kws) for m, kws in module_keywords.items()}
    if not module_scores:
        return None, None, 0.0, 0.0, 0.0

    module = max(module_scores, key=module_scores.get)
    module_score = module_scores.get(module, 0.0)
    if module_score <= 0:
        return None, None, 0.0, 0.0, 0.0

    page_context = " ".join(
        [
            page.get("title") or "",
            page.get("lead_summary") or page.get("summary") or "",
            page.get("full_text") or "",
            " ".join(page.get("categories") or []),
        ]
    )
    year = find_year(page_context)

    if module == "timeline":
        category = infer_timeline_category(year, page_context)
        category_score = 4.5 if year else 2.5
    else:
        category_rules = (rules.get("category_keywords") or {}).get(module, {})
        if category_rules:
            category_scores = {c: keyword_score(fields, kws) for c, kws in category_rules.items()}
            category = max(category_scores, key=category_scores.get)
            category_score = category_scores.get(category, 0.0)
            if category_score <= 0:
                category = (rules.get("default_category") or {}).get(module)
        else:
            category = (rules.get("default_category") or {}).get(module)
            category_score = 1.0

    module_norm = min(module_score / 24.0, 1.0)
    category_norm = min(category_score / 14.0, 1.0)
    confidence = 0.30 + (0.45 * module_norm) + (0.20 * category_norm)
    if year is not None:
        confidence += 0.05
    confidence = max(0.0, min(confidence, 0.99))
    return module, category, confidence, module_score, category_score


def min_confidence_for_module(
    module: str, rules: Dict[str, Any], thresholds: Dict[str, Any]
) -> float:
    module_map = thresholds.get("module_min_confidence", {}) if isinstance(thresholds, dict) else {}
    global_default = (
        thresholds.get("global_default", rules.get("min_confidence", 0.45))
        if isinstance(thresholds, dict)
        else rules.get("min_confidence", 0.45)
    )
    return float(module_map.get(module, global_default))


def make_candidate(
    page: Dict[str, Any], rules: Dict[str, Any], thresholds: Dict[str, Any]
) -> Tuple[Optional[Dict[str, Any]], str]:
    excluded = is_excluded(page, rules)
    if excluded:
        return None, excluded

    module, category, confidence, module_score, category_score = infer_module_and_category(page, rules)
    if not module or not category:
        return None, "unmapped"

    lead = page.get("lead_summary") or page.get("summary") or ""
    full = page.get("full_text") or ""
    lore = first_sentences(lead, max_sentences=2)
    if len(lore) < 45:
        lore = first_sentences(full, max_sentences=3)
    if len(lore) < 25:
        return None, "lore_too_short"

    title = (page.get("title") or "").strip()
    if not title:
        return None, "missing_title"

    page_context = " ".join([title, lead, full, " ".join(page.get("categories") or [])])
    year = find_year(page_context)
    specs: Dict[str, str] = {"Source": "Fallout Wiki"}
    if year:
        specs["Year"] = str(year)
    if page.get("revision_id"):
        specs["Revision"] = str(page["revision_id"])

    min_conf = min_confidence_for_module(module, rules, thresholds)
    if confidence < min_conf:
        return None, "low_confidence"

    candidate = {
        "source_url": page.get("url"),
        "source_title": title,
        "source_revision_id": page.get("revision_id"),
        "module": module,
        "category_id": category,
        "id": slugify(title),
        "name": title.upper(),
        "img": page.get("image") or "",
        "specs": specs,
        "lore": lore,
        "canon_tags": infer_canon_tags(page, rules),
        "confidence": round(confidence, 3),
        "signals": {
            "module_score": round(module_score, 3),
            "category_score": round(category_score, 3),
            "min_confidence_required": round(min_conf, 3),
        },
        "extracted_at": utc_now_iso(),
    }
    return candidate, "ok"


def run(args: argparse.Namespace) -> int:
    rules = json.loads(Path(args.mapping).read_text(encoding="utf-8"))
    thresholds: Dict[str, Any] = {}
    if args.thresholds and Path(args.thresholds).exists():
        thresholds = json.loads(Path(args.thresholds).read_text(encoding="utf-8"))

    pages = load_jsonl(Path(args.input_path))
    out: List[Dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_urls: set[str] = set()
    skipped: Dict[str, int] = {}

    for page in pages:
        source_url = page.get("url")
        if source_url and source_url in seen_urls:
            skipped["duplicate_url"] = skipped.get("duplicate_url", 0) + 1
            continue

        candidate, status = make_candidate(page, rules, thresholds)
        if status != "ok" or not candidate:
            skipped[status] = skipped.get(status, 0) + 1
            continue

        base_id = candidate["id"]
        dedupe_id = base_id
        n = 2
        while dedupe_id in seen_ids:
            dedupe_id = f"{base_id}_{n}"
            n += 1
        candidate["id"] = dedupe_id
        seen_ids.add(dedupe_id)
        if source_url:
            seen_urls.add(source_url)
        out.append(candidate)

    write_jsonl(Path(args.out), out)
    print(
        json.dumps(
            {
                "run_at": utc_now_iso(),
                "input_pages": len(pages),
                "candidates": len(out),
                "skipped": skipped,
                "thresholds": args.thresholds,
                "out": args.out,
            },
            indent=2,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Normalize raw Fallout Wiki pages into candidate records.")
    parser.add_argument("--in", dest="input_path", required=True, help="Input raw JSONL path")
    parser.add_argument("--mapping", required=True, help="Path to mapping rules JSON")
    parser.add_argument(
        "--thresholds",
        default="scripts/config/module_thresholds.json",
        help="Per-module thresholds JSON path",
    )
    parser.add_argument("--out", required=True, help="Output candidate JSONL path")
    return parser


if __name__ == "__main__":
    raise SystemExit(run(build_parser().parse_args()))

