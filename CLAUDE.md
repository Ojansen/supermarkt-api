# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A JSON API serving weekly Dutch supermarket deals (bonus folders) for 19 supermarkets (Albert Heijn, Jumbo, Plus, Kruidvat, Lidl, Aldi, Dirk, Vomar, Hoogvliet, Poiesz, Dekamarkt, Spar, Boni, Nettorama, Trekpleister, Makro, Coop, MCD, Boons Markt). Deployed on Vercel as a Python/Flask serverless function. The API endpoints (`/v1/<store>`) redirect to static JSON files in `public/v1/`.

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Flask app locally
flask --app api/index run

# Run the scraper/OCR pipeline (generates public/v1/*.json)
python run.py
```

There is no test suite or linter configured.

## Architecture

- **`api/index.py`** — Flask app deployed as a Vercel serverless function. Serves the home page. Does NOT import the pipeline to avoid heavy dependencies at deploy time.
- **`pipeline.py`** — Scraping and OCR logic. Fetches deal entries from voordeelmuis.nl, filters to active deals, builds PDFs from deal images, and uses Mistral OCR to extract structured product data.
- **`run.py`** — Standalone entry point to run the full pipeline (`python run.py`). Loads `.env` and calls `pipeline.run_all()`.
- **`public/v1/*.json`** — Static JSON files with deal data per supermarket. Updated by running the pipeline.
- **`vercel.json`** — Routing config: rewrites all non-static routes to `api/index`, redirects `/v1/<store>` to static JSON, and sets 1-week cache headers.

## Key Patterns

- voordeelmuis.nl scraping: AJAX endpoint returns JSON with deal entries per store (by `wk_id`). Entries are filtered to those active today based on their `period` field. Deal images are fetched from `https://www.voordeelmuis.nl/img/jpg240/{id // 1000}/{id}.jpg`.
- Deal JSON structure: `{ "winkel": str, "winkel_naam": str, "week": int, "van": "YYYY-MM-DD", "tot": "YYYY-MM-DD", "producten": [{ "naam", "omschrijving", "items", "aanbieding", "prijs_eerst", "prijs_nu" }] }` (Dutch field names).
