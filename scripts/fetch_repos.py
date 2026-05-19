#!/usr/bin/env python3
"""
Fetch GitHub repos related to Security, Architecture, and System Design.
Generates Jekyll posts for newly discovered repos. Runs daily via GitHub Actions.
"""

import os
import json
import time
import re
import requests
from datetime import datetime, timezone
from pathlib import Path

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise SystemExit("ERROR: GITHUB_TOKEN environment variable is required.")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

BASE_DIR = Path(__file__).parent.parent
POSTS_DIR = BASE_DIR / "docs" / "_posts"
DATA_DIR = BASE_DIR / "docs" / "_data"
SEEN_FILE = DATA_DIR / "seen_repos.json"

POSTS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

SEARCHES = [
    # Security
    ("topic:penetration-testing stars:>300",     "security",      "pentesting"),
    ("topic:security-tools stars:>500",          "security",      "tools"),
    ("topic:vulnerability stars:>400",           "security",      "vulnerability"),
    ("topic:ctf stars:>400",                     "security",      "ctf"),
    ("topic:osint stars:>300",                   "security",      "osint"),
    ("topic:malware-analysis stars:>300",        "security",      "malware"),
    ("topic:cybersecurity stars:>600",           "security",      "general"),
    ("topic:exploit stars:>300",                 "security",      "exploitation"),
    ("topic:cryptography stars:>400",            "security",      "cryptography"),
    ("topic:network-security stars:>300",        "security",      "network"),
    ("topic:web-security stars:>400",            "security",      "web"),
    ("topic:reverse-engineering stars:>400",     "security",      "reverse-engineering"),
    ("topic:fuzzing stars:>200",                 "security",      "fuzzing"),
    ("topic:incident-response stars:>200",       "security",      "incident-response"),
    ("topic:threat-intelligence stars:>200",     "security",      "threat-intel"),
    ("topic:sast stars:>200",                    "security",      "sast"),
    ("topic:devsecops stars:>200",               "security",      "devsecops"),
    ("topic:zero-trust stars:>200",              "security",      "zero-trust"),
    # Architecture
    ("topic:system-design stars:>600",           "architecture",  "system-design"),
    ("topic:software-architecture stars:>400",   "architecture",  "software-arch"),
    ("topic:distributed-systems stars:>400",     "architecture",  "distributed"),
    ("topic:microservices stars:>400",           "architecture",  "microservices"),
    ("topic:design-patterns stars:>400",         "architecture",  "patterns"),
    ("topic:cloud-architecture stars:>300",      "architecture",  "cloud"),
    ("topic:api-design stars:>300",              "architecture",  "api"),
    ("topic:event-driven stars:>300",            "architecture",  "event-driven"),
    ("topic:clean-architecture stars:>300",      "architecture",  "clean-arch"),
    ("topic:domain-driven-design stars:>300",    "architecture",  "ddd"),
    ("topic:hexagonal-architecture stars:>200",  "architecture",  "hexagonal"),
    ("topic:serverless stars:>400",              "architecture",  "serverless"),
    ("topic:kubernetes-architecture stars:>200", "architecture",  "kubernetes"),
    # System Design
    ("topic:scalability stars:>300",             "system-design", "scalability"),
    ("topic:high-availability stars:>200",       "system-design", "high-availability"),
    ("topic:load-balancing stars:>200",          "system-design", "load-balancing"),
    ("topic:caching stars:>400",                 "system-design", "caching"),
    ("topic:message-queue stars:>300",           "system-design", "messaging"),
    ("topic:database-design stars:>300",         "system-design", "database"),
    ("system design interview stars:>2000",      "system-design", "interview"),
    ("topic:consensus-algorithm stars:>200",     "system-design", "consensus"),
    ("topic:service-mesh stars:>300",            "system-design", "service-mesh"),
    ("topic:observability stars:>300",           "system-design", "observability"),
    ("topic:chaos-engineering stars:>200",       "system-design", "chaos"),
]


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def stars_display(n: int) -> str:
    if n >= 1_000:
        return f"{n / 1000:.1f}k"
    return str(n)


def load_seen() -> set:
    if SEEN_FILE.exists():
        return set(json.loads(SEEN_FILE.read_text()))
    return set()


def save_seen(seen: set) -> None:
    SEEN_FILE.write_text(json.dumps(sorted(seen), indent=2))


def search_github(query: str, max_pages: int = 3) -> list:
    repos = []
    for page in range(1, max_pages + 1):
        resp = requests.get(
            "https://api.github.com/search/repositories",
            headers=HEADERS,
            params={"q": query, "sort": "stars", "order": "desc",
                    "per_page": 30, "page": page},
            timeout=20,
        )
        if resp.status_code == 422:
            break
        if resp.status_code == 403:
            reset = int(resp.headers.get("X-RateLimit-Reset", time.time() + 60))
            wait = max(reset - time.time(), 5)
            print(f"    Rate limited — sleeping {wait:.0f}s")
            time.sleep(wait)
            continue
        resp.raise_for_status()
        items = resp.json().get("items", [])
        repos.extend(items)
        if len(items) < 30:
            break
        time.sleep(1.5)
    return repos


def make_post(repo: dict, category: str, subcategory: str, date_str: str) -> tuple[str, str]:
    owner   = repo["owner"]["login"]
    name    = repo["name"]
    desc    = (repo.get("description") or "").replace('"', "'").replace("\\", "\\\\").strip()
    stars   = repo.get("stargazers_count", 0)
    forks   = repo.get("forks_count", 0)
    lang    = repo.get("language") or "Unknown"
    topics  = json.dumps(repo.get("topics", []))
    url     = repo["html_url"]
    updated = (repo.get("updated_at") or "")[:10]
    slug    = f"{slugify(owner)}-{slugify(name)}"

    frontmatter = f"""---
layout: post
title: "{owner}/{name}"
date: {date_str}
repo: "{owner}/{name}"
description: "{desc}"
stars: {stars}
stars_display: "{stars_display(stars)}"
forks: {forks}
language: "{lang}"
category: "{category}"
subcategory: "{subcategory}"
topics: {topics}
github_url: "{url}"
last_updated: "{updated}"
---
"""
    body = f"""{desc}

**[\u2192 View on GitHub]({url})**
"""
    return f"{date_str}-{slug}.md", frontmatter + "\n" + body


def main() -> None:
    seen = load_seen()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    added = 0

    for query, category, subcategory in SEARCHES:
        print(f"\U0001f50d  [{category}/{subcategory}]  {query}")
        try:
            repos = search_github(query)
        except Exception as exc:
            print(f"    \u26a0  {exc}")
            time.sleep(5)
            continue

        for repo in repos:
            full_name = repo["full_name"]
            if full_name in seen:
                continue
            if repo.get("archived") or repo.get("fork"):
                continue
            if not repo.get("description"):
                continue

            seen.add(full_name)
            filename, content = make_post(repo, category, subcategory, today)
            path = POSTS_DIR / filename
            if not path.exists():
                path.write_text(content, encoding="utf-8")
                added += 1
                print(f"    \u2705  {full_name}  \u2b50{repo.get('stargazers_count', 0):,}")

        time.sleep(3)

    save_seen(seen)
    print(f"\n\U0001f389  Done \u2014 added {added} new repos (total seen: {len(seen)})")


if __name__ == "__main__":
    main()
