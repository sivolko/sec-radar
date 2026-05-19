.PHONY: install fetch serve build clean

install:
	pip install -r scripts/requirements.txt

fetch:
	@echo "→ Fetching repos (requires GITHUB_TOKEN env var)"
	python scripts/fetch_repos.py

serve:
	@echo "→ Serving Jekyll site at http://localhost:4000"
	cd docs && bundle exec jekyll serve --livereload

build:
	@echo "→ Building Jekyll site"
	cd docs && bundle exec jekyll build

clean:
	rm -rf docs/_site docs/.jekyll-cache
