#!/bin/bash

# Local development script for NoFrills.news
# This script exports articles from SQLite to JSON and starts the Astro dev server

set -e  # Exit on error

echo "Exporting articles from SQLite to JSON..."
python scripts/export_for_astro.py || {
    echo "Error: Failed to export articles. Check that data/articles.db exists and export_for_astro.py is working."
    exit 1
}

echo "Starting Astro development server..."
cd site && npm run dev || {
    echo "Error: Failed to start Astro development server. Check that node_modules are installed (run: cd site && npm install)"
    exit 1
}
