# ⛡ Sec Radar

> A daily-updated, filterable index of the best GitHub repos on **Security**, **Architecture**, and **System Design** — hosted free on GitHub Pages.

[![Daily Update](https://img.shields.io/github/actions/workflow/status/sivolko/sec-radar/daily-update.yml?branch=main&label=daily+update&style=for-the-badge)](https://github.com/sivolko/sec-radar/actions/workflows/daily-update.yml)
[![Pages](https://img.shields.io/github/deployments/sivolko/sec-radar/github-pages?label=pages&style=for-the-badge)](https://sivolko.github.io/sec-radar)

**Live site:** https://sivolko.github.io/sec-radar

---

## What it does

Every day at 06:00 UTC, a GitHub Actions workflow:
1. Searches GitHub for repos matching **40+ queries** across three domains
2. Skips repos already indexed (deduplication via `docs/_data/seen_repos.json`)
3. Generates a Jekyll Markdown post for each new repo found
4. Commits and pushes — triggering GitHub Pages to rebuild the static site

The site has a **pure client-side filter UI** (no backend):
- Filter by **category** (Security / Architecture / System Design)
- Filter by **subcategory** (pentesting, OSINT, microservices, caching …)
- Filter by **min stars**
- Filter by **language**
- Full **text search** across name, description, topics
- **Sort** by date or stars

---

## Domains covered

| Category | Subcategories |
|---|---|
| 🔐 **Security** | pentesting, tools, vulnerability, ctf, osint, malware, web, reverse-engineering, cryptography, network, fuzzing, incident-response, threat-intel, sast, devsecops, zero-trust |
| 🏗 **Architecture** | system-design, software-arch, distributed, microservices, patterns, cloud, api, event-driven, clean-arch, ddd, hexagonal, serverless, kubernetes |
| ⚙️ **System Design** | scalability, high-availability, load-balancing, caching, messaging, database, interview, consensus, service-mesh, observability, chaos |

---

## Setup (5 min)

### 1. Enable GitHub Pages
- Go to **Settings → Pages**
- Source: **GitHub Actions**

### 2. Add workflow files (one-time manual step)

Create `.github/workflows/daily-update.yml`:
```yaml
name: Daily Repo Update
on:
  schedule:
    - cron: "0 6 * * *"
  workflow_dispatch:
permissions:
  contents: write
jobs:
  fetch-and-commit:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12", cache: pip }
      - run: pip install -r scripts/requirements.txt
      - env: { GITHUB_TOKEN: "${{ secrets.GITHUB_TOKEN }}" }
        run: python scripts/fetch_repos.py
      - run: |
          git config --global user.name "github-actions[bot]"
          git config --global user.email "github-actions[bot]@users.noreply.github.com"
          git add docs/_posts/ docs/_data/
          git diff --staged --quiet || (git commit -m "chore: daily update $(date -u +'%Y-%m-%d')" && git push)
```

Create `.github/workflows/deploy-pages.yml`:
```yaml
name: Deploy Jekyll Site
on:
  push:
    branches: [main]
    paths: ["docs/**"]
  workflow_dispatch:
permissions:
  contents: read
  pages: write
  id-token: write
concurrency:
  group: pages
  cancel-in-progress: false
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/configure-pages@v5
      - uses: actions/jekyll-build-pages@v1
        with: { source: ./docs, destination: ./_site }
      - uses: actions/upload-pages-artifact@v3
  deploy:
    environment: { name: github-pages, url: "${{ steps.deployment.outputs.page_url }}" }
    runs-on: ubuntu-latest
    needs: build
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

### 3. Trigger first fetch

Go to **Actions → Daily Repo Update → Run workflow**.

No extra secrets needed — the built-in `GITHUB_TOKEN` is sufficient.

---

## Local development

```bash
export GITHUB_TOKEN=ghp_...
make fetch          # fetch repos locally
make serve          # → http://localhost:4000/sec-radar
```

---

## Structure

```
.
├── .github/workflows/
│   ├── daily-update.yml      # Cron: fetch → commit
│   └── deploy-pages.yml      # Push → GitHub Pages
├── docs/
│   ├── _posts/               # Auto-generated (one .md per repo)
│   ├── _data/seen_repos.json # Deduplication tracker
│   ├── _layouts/             # default.html + post.html
│   ├── assets/css/main.css   # Full dark/light stylesheet
│   ├── _config.yml
│   ├── index.html            # Feed + filter UI
│   ├── archive.md
│   └── feed.xml              # Atom RSS
└── scripts/
    ├── fetch_repos.py        # GitHub API fetcher
    └── requirements.txt
```

---

## License

MIT — see [LICENSE](LICENSE). Repo metadata belongs to respective owners.
