#!/usr/bin/env python3
"""
Crawl fallout.fandom.com via MediaWiki API and emit raw page records as JSONL.
"""

from __future__ import annotations

import argparse
import json
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.parse import quote, unquote, urlparse
from urllib.request import Request, urlopen


API_URL = "https://fallout.fandom.com/api.php"
WIKI_HOST = "fallout.fandom.com"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_seed_titles(seed_path: Path) -> List[str]:
    data = json.loads(seed_path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        seeds = data.get("seed_urls", [])
    elif isinstance(data, list):
        seeds = data
    else:
        raise ValueError("Seeds must be a list or an object containing seed_urls.")
    titles = []
    for seed in seeds:
        title = url_to_title(str(seed).strip())
        if title:
            titles.append(title)
    return list(dict.fromkeys(titles))


def url_to_title(value: str) -> Optional[str]:
    if not value:
        return None
    if value.startswith("http://") or value.startswith("https://"):
        parsed = urlparse(value)
        if parsed.netloc and parsed.netloc != WIKI_HOST:
            return None
        path = parsed.path
        marker = "/wiki/"
        if marker not in path:
            return None
        raw = path.split(marker, 1)[1]
        if not raw:
            return None
        return unquote(raw).replace("_", " ")
    return value.replace("_", " ")


def title_to_url(title: str) -> str:
    return f"https://{WIKI_HOST}/wiki/{quote(title.replace(' ', '_'))}"


def api_request(params: Dict[str, Any], timeout: int, user_agent: str) -> Dict[str, Any]:
    pairs = []
    for key, value in params.items():
        pairs.append(f"{quote(str(key))}={quote(str(value))}")
    query = "&".join(pairs)
    url = f"{API_URL}?{query}"
    req = Request(url, headers={"User-Agent": user_agent})
    with urlopen(req, timeout=timeout) as resp:  # nosec B310
        body = resp.read().decode("utf-8", errors="replace")
    return json.loads(body)


def fetch_page(title: str, timeout: int, user_agent: str) -> Optional[Dict[str, Any]]:
    params = {
        "action": "query",
        "format": "json",
        "formatversion": 2,
        "redirects": 1,
        "prop": "extracts|pageimages|categories|revisions|info",
        "titles": title,
        "exintro": 1,
        "explaintext": 1,
        "piprop": "thumbnail",
        "pithumbsize": 600,
        "cllimit": "max",
        "clshow": "!hidden",
        "rvprop": "ids|timestamp",
        "rvlimit": 1,
        "inprop": "url",
    }
    data = api_request(params, timeout=timeout, user_agent=user_agent)
    pages = data.get("query", {}).get("pages", [])
    if not pages:
        return None
    page = pages[0]
    if page.get("missing"):
        return None
    categories = []
    for cat in page.get("categories", []) or []:
        title_value = cat.get("title", "")
        if title_value.startswith("Category:"):
            title_value = title_value[len("Category:") :]
        if title_value:
            categories.append(title_value)
    rev = (page.get("revisions") or [{}])[0]
    thumb = page.get("thumbnail") or {}
    summary = (page.get("extract") or "").strip()
    return {
        "page_id": page.get("pageid"),
        "title": page.get("title", title),
        "url": page.get("fullurl") or title_to_url(page.get("title", title)),
        "summary": summary,
        "categories": categories,
        "image": thumb.get("source"),
        "revision_id": rev.get("revid"),
        "revision_timestamp": rev.get("timestamp"),
    }


def fetch_links(title: str, timeout: int, user_agent: str) -> List[str]:
    links: List[str] = []
    cont: Optional[str] = None
    while True:
        params: Dict[str, Any] = {
            "action": "query",
            "format": "json",
            "formatversion": 2,
            "redirects": 1,
            "prop": "links",
            "titles": title,
            "plnamespace": 0,
            "pllimit": "max",
        }
        if cont:
            params["plcontinue"] = cont
        data = api_request(params, timeout=timeout, user_agent=user_agent)
        pages = data.get("query", {}).get("pages", [])
        if pages:
            for item in pages[0].get("links", []) or []:
                t = item.get("title")
                if t and ":" not in t:
                    links.append(t)
        next_cont = data.get("continue", {}).get("plcontinue")
        if not next_cont:
            break
        cont = next_cont
    return list(dict.fromkeys(links))


def write_jsonl(path: Path, records: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def run(args: argparse.Namespace) -> int:
    seed_titles = load_seed_titles(Path(args.seeds))
    if not seed_titles:
        raise ValueError("No valid seed titles found.")

    visited: set[str] = set()
    queued: set[str] = set(seed_titles)
    queue: deque[Tuple[str, int, str]] = deque((t, 0, t) for t in seed_titles)
    out_records: List[Dict[str, Any]] = []

    errors = 0
    while queue and len(out_records) < args.max_pages:
        title, depth, seed_title = queue.popleft()
        if title in visited:
            continue
        visited.add(title)

        try:
            page = fetch_page(title, timeout=args.timeout, user_agent=args.user_agent)
        except Exception:
            errors += 1
            continue
        if not page:
            continue

        page["depth"] = depth
        page["seed_title"] = seed_title
        page["fetched_at"] = utc_now_iso()
        out_records.append(page)

        if depth >= args.max_depth:
            continue

        try:
            links = fetch_links(page["title"], timeout=args.timeout, user_agent=args.user_agent)
        except Exception:
            errors += 1
            continue

        for link_title in links:
            if link_title in visited or link_title in queued:
                continue
            queued.add(link_title)
            queue.append((link_title, depth + 1, seed_title))

        if args.sleep_ms > 0:
            time.sleep(args.sleep_ms / 1000.0)

    write_jsonl(Path(args.out), out_records)
    print(
        json.dumps(
            {
                "run_at": utc_now_iso(),
                "seed_count": len(seed_titles),
                "pages_written": len(out_records),
                "visited": len(visited),
                "queue_remaining": len(queue),
                "errors": errors,
                "out": args.out,
            },
            indent=2,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Crawl fallout.fandom.com and emit raw page JSONL.")
    parser.add_argument("--seeds", required=True, help="Path to seeds.json")
    parser.add_argument("--max-depth", type=int, default=2, help="Max hop depth from seeds")
    parser.add_argument("--max-pages", type=int, default=500, help="Hard cap on crawled pages")
    parser.add_argument("--timeout", type=int, default=20, help="HTTP timeout seconds")
    parser.add_argument("--sleep-ms", type=int, default=75, help="Delay between page crawl steps")
    parser.add_argument("--out", required=True, help="Output JSONL path")
    parser.add_argument(
        "--user-agent",
        default="omnidatabase-pipboy-codex/1.0 (data-pipeline)",
        help="HTTP User-Agent",
    )
    return parser


if __name__ == "__main__":
    raise SystemExit(run(build_parser().parse_args()))

