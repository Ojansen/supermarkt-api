# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A JSON API serving weekly Dutch supermarket deals (bonus folders) for Albert Heijn, Jumbo, Plus, and Kruidvat. Deployed on Vercel as a Python/Flask serverless function. The API endpoints (`/v1/ah`, `/v1/jumbo`, `/v1/plus`, `/v1/kruidvat`) currently redirect to static JSON files in `public/v1/`.

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Flask app locally
flask --app api/index run

# Run the standalone scraper script
python main.py
```

There is no test suite or linter configured.

## Architecture

- **`api/index.py`** — Flask app deployed as a Vercel serverless function. Serves the home page and a `/api/cron` endpoint. The `/v1/<store>` dynamic route is commented out; deals are served as static JSON via Vercel redirects instead.
- **`main.py`** — Standalone script that scrapes Publitas-hosted folder pages. Extracts image URLs from embedded JavaScript `var data = {...}` blocks. Contains commented-out OpenAI integration for parsing folder images into structured `FolderItem` data (Pydantic model).
- **`public/v1/*.json`** — Static JSON files with deal data per supermarket. Updated via the cron endpoint or manually.
- **`vercel.json`** — Routing config: rewrites all non-static routes to `api/index`, redirects `/v1/<store>` to static JSON, sets 1-week cache headers, and schedules a weekly cron (Mondays at 12:00 UTC).

## Key Patterns

- Publitas scraping: fetch page HTML, regex-extract `var data = {...}` JSON, then pull image URLs from `spreads[].pages[].images.at600`.
- Deal JSON structure: `{ "week": int, "producten": [{ "naam", "omschrijving", "items", "aanbieding", "prijs_eerst", "prijs_nu" }] }` (Dutch field names).
