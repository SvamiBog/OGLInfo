.PHONY: clean-db crawl update-deps

clean-db:
	uv run python scripts/clean_db.py

crawl:
	uv run scripts/crawl.py --project oglinfo_scraper --spider otomoto

update:
	uv tool update-shell
