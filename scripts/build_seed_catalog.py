#!/usr/bin/env python3
"""
Build expanded seed catalog from curated category pages + existing seeds.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import quote, unquote, urlparse
from urllib.request import Request, urlopen


API_URL = "https://fallout.fandom.com/api.php"
WIKI_HOST = "fallout.fandom.com"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def api_request(params: Dict[str, Any], timeout: int, user_agent: str) -> Dict[str, Any]:
    query = "&".join(f"{quote(str(k))}={quote(str(v))}" for k, v in params.items())
    req = Request(f"{API_URL}?{query}", headers={"User-Agent": user_agent})
    with urlopen(req, timeout=timeout) as resp:  # nosec B310
        body = resp.read().decode("utf-8", errors="replace")
    return json.loads(body)


def url_to_title(value: str) -> Optional[str]:
    if not value:
        return None
    if value.startswith("http://") or value.startswith("https://"):
        parsed = urlparse(value)
        if parsed.netloc and parsed.netloc != WIKI_HOST:
            return None
        marker = "/wiki/"
        if marker not in parsed.path:
            return None
        return unquote(parsed.path.split(marker, 1)[1]).replace("_", " ")
    return value.replace("_", " ")


def title_to_url(title: str) -> str:
    return f"https://{WIKI_HOST}/wiki/{quote(title.replace(' ', '_'))}"


def normalize_category_title(value: str) -> Optional[str]:
    t = url_to_title(value or "")
    if not t:
        return None
    if t.startswith("Category:"):
        return t
    return f"Category:{t}"


def load_seed_titles(seed_path: Path) -> Set[str]:
    data = json.loads(seed_path.read_text(encoding="utf-8"))
    seeds = data.get("seed_urls", []) if isinstance(data, dict) else data
    out: Set[str] = set()
    for s in seeds or []:
        t = url_to_title(str(s))
        if t:
            out.add(t)
    return out


def load_category_titles(path: Path) -> List[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("category_urls", []) if isinstance(data, dict) else data
    out: List[str] = []
    for item in items or []:
        t = normalize_category_title(str(item))
        if t:
            out.append(t)
    return list(dict.fromkeys(out))


def fetch_category_members(
    category_title: str, timeout: int, user_agent: str, cm_limit: int
) -> List[str]:
    members: List[str] = []
    cont: Optional[str] = None
    while len(members) < cm_limit:
        params: Dict[str, Any] = {
            "action": "query",
            "format": "json",
            "formatversion": 2,
            "list": "categorymembers",
            "cmtitle": category_title,
            "cmnamespace": 0,
            "cmlimit": "max",
        }
        if cont:
            params["cmcontinue"] = cont
        data = api_request(params, timeout=timeout, user_agent=user_agent)
        for row in data.get("query", {}).get("categorymembers", []) or []:
            title = row.get("title")
            if title and ":" not in title:
                members.append(title)
                if len(members) >= cm_limit:
                    break
        next_cont = data.get("continue", {}).get("cmcontinue")
        if not next_cont:
            break
        cont = next_cont
    return list(dict.fromkeys(members))


def run(args: argparse.Namespace) -> int:
    base_seeds = load_seed_titles(Path(args.seeds))
    categories = load_category_titles(Path(args.categories))

    all_titles: Set[str] = set(base_seeds)
    discovered_from: Dict[str, List[str]] = {}
    errors = 0

    for cat in categories:
        try:
            members = fetch_category_members(
                category_title=cat,
                timeout=args.timeout,
                user_agent=args.user_agent,
                cm_limit=args.members_per_category,
            )
        except Exception:
            errors += 1
            continue
        for title in members:
            all_titles.add(title)
            discovered_from.setdefault(title, [])
            discovered_from[title].append(cat)

    seed_urls = [title_to_url(t) for t in sorted(all_titles)]
    metadata = {
        "generated_at": utc_now_iso(),
        "base_seed_count": len(base_seeds),
        "categories_count": len(categories),
        "expanded_seed_count": len(seed_urls),
        "errors": errors,
    }
    output = {
        "seed_urls": seed_urls,
        "metadata": metadata,
        "discovered_from": {k: sorted(set(v)) for k, v in discovered_from.items()},
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metadata, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build expanded seed catalog from curated categories.")
    parser.add_argument("--seeds", default="scripts/config/seeds.json", help="Base seeds JSON path")
    parser.add_argument(
        "--categories",
        default="scripts/config/seed_categories.json",
        help="Category seed JSON path",
    )
    parser.add_argument("--out", default="tmp/expanded_seeds.json", help="Expanded seeds output JSON")
    parser.add_argument("--members-per-category", type=int, default=200, help="Member cap per category")
    parser.add_argument("--timeout", type=int, default=20, help="HTTP timeout seconds")
    parser.add_argument(
        "--user-agent",
        default="omnidatabase-pipboy-codex/1.0 (seed-catalog)",
        help="HTTP User-Agent",
    )
    return parser


if __name__ == "__main__":
    raise SystemExit(run(build_parser().parse_args()))

