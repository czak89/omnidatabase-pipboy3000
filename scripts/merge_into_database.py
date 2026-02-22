#!/usr/bin/env python3
"""
Merge normalized candidates into database-en.json with provenance and safety guardrails.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.parse import quote_plus


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def append_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def make_placeholder_image(name: str) -> str:
    txt = quote_plus(name[:26])
    return f"https://placehold.co/300x200/111100/33ff33?text={txt}"


def norm_text(value: str) -> str:
    value = (value or "").lower().strip()
    value = re.sub(r"\s+", " ", value)
    return value


def text_similarity(a: str, b: str) -> float:
    return SequenceMatcher(a=norm_text(a), b=norm_text(b)).ratio()


def preferred_value(old: Any, new: Any) -> Any:
    if new is None or new == "":
        return old
    return new


def merge_specs(old: Dict[str, Any], new: Dict[str, Any], mode: str) -> Dict[str, Any]:
    if mode == "prefer_newer":
        merged = dict(old)
        merged.update({k: v for k, v in new.items() if v not in (None, "")})
        return merged
    if mode == "conservative":
        merged = dict(old)
        for k, v in new.items():
            if (k not in merged) or (merged[k] in (None, "")):
                merged[k] = v
        return merged
    return old


def build_id_index(db: Dict[str, Any]) -> Dict[str, Tuple[str, str, int]]:
    index: Dict[str, Tuple[str, str, int]] = {}
    for module, modv in db.items():
        if not isinstance(modv, dict) or "items" not in modv:
            continue
        for category, arr in modv.get("items", {}).items():
            for i, item in enumerate(arr):
                item_id = item.get("id")
                if item_id:
                    index[item_id] = (module, category, i)
    return index


def build_lore_index(db: Dict[str, Any]) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    for module, modv in db.items():
        if not isinstance(modv, dict) or "items" not in modv:
            continue
        for category, arr in modv.get("items", {}).items():
            for item in arr:
                lore = item.get("lore") or ""
                if lore.strip():
                    out.append(
                        {
                            "module": module,
                            "category_id": category,
                            "id": item.get("id", ""),
                            "lore": lore,
                        }
                    )
    return out


def normalize_item(candidate: Dict[str, Any]) -> Dict[str, Any]:
    name = candidate.get("name") or candidate.get("source_title") or "UNKNOWN"
    return {
        "id": candidate["id"],
        "name": str(name).upper(),
        "img": candidate.get("img") or make_placeholder_image(str(name).upper()),
        "specs": candidate.get("specs") or {"Source": "Fallout Wiki"},
        "lore": candidate.get("lore") or "",
    }


def is_allowed_canon(candidate: Dict[str, Any], allowed: set[str]) -> bool:
    tags = set(candidate.get("canon_tags") or [])
    return bool(tags & allowed)


def find_near_duplicate(
    lore_index: List[Dict[str, str]],
    module: str,
    category_id: str,
    item_id: str,
    lore: str,
    threshold: float,
) -> Optional[Dict[str, Any]]:
    if not lore.strip():
        return None
    best_match: Optional[Dict[str, Any]] = None
    best_score = 0.0
    for row in lore_index:
        if row["module"] != module or row["category_id"] != category_id:
            continue
        if row["id"] == item_id:
            continue
        score = text_similarity(lore, row["lore"])
        if score >= threshold and score > best_score:
            best_score = score
            best_match = row
    if not best_match:
        return None
    return {"similarity": round(best_score, 4), "matched_id": best_match["id"]}


def run(args: argparse.Namespace) -> int:
    run_id = build_run_id()
    db_path = Path(args.db)
    db = json.loads(db_path.read_text(encoding="utf-8"))
    candidates = load_jsonl(Path(args.input_path))

    allowed_canon = set(x.strip() for x in args.canon.split(",") if x.strip())
    valid_targets = {
        (module, cat)
        for module, modv in db.items()
        if isinstance(modv, dict) and "items" in modv
        for cat in modv.get("items", {}).keys()
    }

    id_index = build_id_index(db)
    lore_index = build_lore_index(db)

    inserted = 0
    updated = 0
    skipped = 0
    skipped_reasons: Dict[str, int] = {}
    provenance_rows: List[Dict[str, Any]] = []
    decision_rows: List[Dict[str, Any]] = []

    for cand in candidates:
        decision: Dict[str, Any] = {
            "timestamp": utc_now_iso(),
            "run_id": run_id,
            "id": cand.get("id"),
            "module": cand.get("module"),
            "category_id": cand.get("category_id"),
            "source_url": cand.get("source_url"),
            "decision": "",
            "reason": "",
        }

        if not is_allowed_canon(cand, allowed_canon):
            skipped += 1
            skipped_reasons["canon_filtered"] = skipped_reasons.get("canon_filtered", 0) + 1
            decision["decision"] = "skip"
            decision["reason"] = "canon_filtered"
            decision_rows.append(decision)
            continue

        target = (cand.get("module"), cand.get("category_id"))
        if target not in valid_targets:
            skipped += 1
            skipped_reasons["invalid_target"] = skipped_reasons.get("invalid_target", 0) + 1
            decision["decision"] = "skip"
            decision["reason"] = "invalid_target"
            decision_rows.append(decision)
            continue

        item = normalize_item(cand)
        item_id = item["id"]
        action: Optional[str] = None

        if item_id in id_index:
            if args.conflict == "skip_existing":
                skipped += 1
                skipped_reasons["existing_id_skipped"] = skipped_reasons.get("existing_id_skipped", 0) + 1
                decision["decision"] = "skip"
                decision["reason"] = "existing_id_skipped"
                decision_rows.append(decision)
                continue
            if args.max_updates > 0 and updated >= args.max_updates:
                skipped += 1
                skipped_reasons["update_limit_reached"] = skipped_reasons.get("update_limit_reached", 0) + 1
                decision["decision"] = "skip"
                decision["reason"] = "update_limit_reached"
                decision_rows.append(decision)
                continue

            module, category, idx = id_index[item_id]
            current = db[module]["items"][category][idx]
            if args.conflict == "prefer_newer":
                current["name"] = preferred_value(current.get("name"), item.get("name"))
                current["img"] = preferred_value(current.get("img"), item.get("img"))
                current["lore"] = preferred_value(current.get("lore"), item.get("lore"))
                current["specs"] = merge_specs(current.get("specs", {}), item.get("specs", {}), mode="prefer_newer")
            elif args.conflict == "conservative":
                current["name"] = current.get("name") or item.get("name")
                current["img"] = current.get("img") or item.get("img")
                current["lore"] = current.get("lore") or item.get("lore")
                current["specs"] = merge_specs(current.get("specs", {}), item.get("specs", {}), mode="conservative")

            updated += 1
            action = "update"
            decision["decision"] = "update"
            decision["reason"] = "existing_id_merge"
        else:
            if args.max_inserts > 0 and inserted >= args.max_inserts:
                skipped += 1
                skipped_reasons["insert_limit_reached"] = skipped_reasons.get("insert_limit_reached", 0) + 1
                decision["decision"] = "skip"
                decision["reason"] = "insert_limit_reached"
                decision_rows.append(decision)
                continue

            near_dup = find_near_duplicate(
                lore_index=lore_index,
                module=str(cand.get("module")),
                category_id=str(cand.get("category_id")),
                item_id=item_id,
                lore=item.get("lore", ""),
                threshold=args.similarity_threshold,
            )
            if near_dup:
                skipped += 1
                skipped_reasons["near_duplicate_lore"] = skipped_reasons.get("near_duplicate_lore", 0) + 1
                decision["decision"] = "skip"
                decision["reason"] = "near_duplicate_lore"
                decision["near_duplicate"] = near_dup
                decision_rows.append(decision)
                continue

            module, category = target
            db[module]["items"][category].append(item)
            id_index[item_id] = (module, category, len(db[module]["items"][category]) - 1)
            lore_index.append(
                {
                    "module": module,
                    "category_id": category,
                    "id": item_id,
                    "lore": item.get("lore", ""),
                }
            )
            inserted += 1
            action = "insert"
            decision["decision"] = "insert"
            decision["reason"] = "new_id"

        provenance_rows.append(
            {
                "timestamp": utc_now_iso(),
                "run_id": run_id,
                "action": action,
                "id": item_id,
                "module": cand.get("module"),
                "category_id": cand.get("category_id"),
                "source_url": cand.get("source_url"),
                "source_title": cand.get("source_title"),
                "source_revision_id": cand.get("source_revision_id"),
                "confidence": cand.get("confidence"),
            }
        )
        decision_rows.append(decision)

    db_path.write_text(json.dumps(db, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    append_jsonl(Path(args.provenance), provenance_rows)
    append_jsonl(Path(args.decision_log), decision_rows)

    summary = {
        "run_id": run_id,
        "run_at": utc_now_iso(),
        "db": str(db_path),
        "candidates_in": len(candidates),
        "inserted": inserted,
        "updated": updated,
        "skipped": skipped,
        "skipped_reasons": skipped_reasons,
        "conflict_mode": args.conflict,
        "canon_allowed": sorted(allowed_canon),
        "decision_log": args.decision_log,
        "provenance": args.provenance,
    }

    summary_path = Path(args.summary_out)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    run_manifest_path = Path(args.run_manifest_dir) / f"{run_id}.json"
    run_manifest_path.parent.mkdir(parents=True, exist_ok=True)
    run_manifest_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Merge candidate records into database-en.json.")
    parser.add_argument("--db", required=True, help="Database JSON path (database-en.json)")
    parser.add_argument("--in", dest="input_path", required=True, help="Candidate JSONL path")
    parser.add_argument("--provenance", required=True, help="Provenance JSONL output path")
    parser.add_argument(
        "--decision-log",
        default="scripts/reports/merge_decisions.jsonl",
        help="Per-candidate decision JSONL output path",
    )
    parser.add_argument(
        "--conflict",
        choices=["prefer_newer", "conservative", "skip_existing"],
        default="prefer_newer",
        help="Conflict policy for existing IDs",
    )
    parser.add_argument("--canon", default="mainline,tv", help="Allowed canon tags, comma separated")
    parser.add_argument("--max-inserts", type=int, default=0, help="Maximum inserts for this run (0 = unlimited)")
    parser.add_argument("--max-updates", type=int, default=0, help="Maximum updates for this run (0 = unlimited)")
    parser.add_argument(
        "--similarity-threshold",
        type=float,
        default=0.92,
        help="Lore similarity threshold for near-duplicate guard",
    )
    parser.add_argument(
        "--summary-out",
        default="scripts/reports/last_run_summary.json",
        help="Run summary JSON output",
    )
    parser.add_argument(
        "--run-manifest-dir",
        default="scripts/reports/runs",
        help="Directory for per-run manifest JSON files",
    )
    return parser


if __name__ == "__main__":
    raise SystemExit(run(build_parser().parse_args()))

