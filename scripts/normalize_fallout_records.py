#!/usr/bin/env python3
"""
Normalize raw Fallout Wiki crawl records into database candidate JSONL.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


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
    return out if out else text[:320].strip()


def find_year(text: str) -> Optional[int]:
    m = re.search(r"\b(19\d{2}|20\d{2}|21\d{2}|22\d{2}|23\d{2})\b", text)
    return int(m.group(1)) if m else None


def list_score(text: str, keywords: List[str]) -> int:
    t = text.lower()
    return sum(1 for kw in keywords if kw.lower() in t)


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


def infer_canon_tags(page: Dict[str, Any], rules: Dict[str, Any]) -> List[str]:
    text = " ".join(
        [
            page.get("title") or "",
            page.get("summary") or "",
            " ".join(page.get("categories") or []),
        ]
    ).lower()
    tags = ["mainline"]
    if any(kw.lower() in text for kw in rules.get("canon_keywords", {}).get("tv", [])):
        tags.append("tv")
    return list(dict.fromkeys(tags))


def infer_module_and_category(page: Dict[str, Any], rules: Dict[str, Any]) -> Tuple[Optional[str], Optional[str], float]:
    text = " ".join(
        [
            page.get("title") or "",
            page.get("summary") or "",
            " ".join(page.get("categories") or []),
        ]
    )
    module_keywords = rules.get("module_keywords", {})
    module_scores: Dict[str, int] = {m: list_score(text, kws) for m, kws in module_keywords.items()}
    module = max(module_scores, key=module_scores.get) if module_scores else None
    if not module or module_scores.get(module, 0) == 0:
        return None, None, 0.0

    if module == "timeline":
        year = find_year(text)
        cat = infer_timeline_category(year, text)
        confidence = 0.5 + min(module_scores[module], 4) * 0.1
        return module, cat, min(confidence, 0.95)

    cat_rules = (rules.get("category_keywords") or {}).get(module, {})
    if not cat_rules:
        cat = (rules.get("default_category") or {}).get(module)
        confidence = 0.45 + min(module_scores[module], 3) * 0.1
        return module, cat, min(confidence, 0.9)

    cat_scores: Dict[str, int] = {c: list_score(text, kws) for c, kws in cat_rules.items()}
    category = max(cat_scores, key=cat_scores.get) if cat_scores else None
    if category and cat_scores.get(category, 0) == 0:
        category = (rules.get("default_category") or {}).get(module)
    confidence = 0.4 + min(module_scores[module], 4) * 0.08 + min(cat_scores.get(category, 0), 3) * 0.1
    return module, category, min(confidence, 0.95)


def make_candidate(page: Dict[str, Any], rules: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], str]:
    excluded = is_excluded(page, rules)
    if excluded:
        return None, excluded

    module, category, confidence = infer_module_and_category(page, rules)
    if not module or not category:
        return None, "unmapped"

    lore = first_sentences(page.get("summary") or "", max_sentences=2)
    if len(lore) < 25:
        return None, "lore_too_short"

    title = (page.get("title") or "").strip()
    if not title:
        return None, "missing_title"

    year = find_year(" ".join([title, page.get("summary") or ""]))
    specs: Dict[str, str] = {"Source": "Fallout Wiki"}
    if year:
        specs["Year"] = str(year)
    if page.get("revision_id"):
        specs["Revision"] = str(page["revision_id"])

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
        "extracted_at": utc_now_iso(),
    }
    if confidence < float(rules.get("min_confidence", 0.45)):
        return None, "low_confidence"
    return candidate, "ok"


def run(args: argparse.Namespace) -> int:
    rules = json.loads(Path(args.mapping).read_text(encoding="utf-8"))
    pages = load_jsonl(Path(args.input_path))
    out: List[Dict[str, Any]] = []
    seen_ids: set[str] = set()
    skipped: Dict[str, int] = {}

    for page in pages:
        candidate, status = make_candidate(page, rules)
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
        out.append(candidate)

    write_jsonl(Path(args.out), out)
    print(
        json.dumps(
            {
                "run_at": utc_now_iso(),
                "input_pages": len(pages),
                "candidates": len(out),
                "skipped": skipped,
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
    parser.add_argument("--out", required=True, help="Output candidate JSONL path")
    return parser


if __name__ == "__main__":
    raise SystemExit(run(build_parser().parse_args()))

