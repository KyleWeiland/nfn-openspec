"""Export articles and categories from SQLite to JSON for Astro."""

import sqlite3
import json
import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Get repository root (parent of scripts directory)
REPO_ROOT = Path(__file__).parent.parent
DB_PATH = REPO_ROOT / "data" / "articles.db"
ARTICLES_JSON = REPO_ROOT / "data" / "articles.json"
CATEGORIES_JSON = REPO_ROOT / "data" / "categories.json"


def export_articles():
    """Export all articles from SQLite to JSON, ordered by date descending.

    Returns:
        List of article dictionaries, or None if export fails
    """
    try:
        # Ensure data directory exists
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)

        # Check if database exists
        if not DB_PATH.exists():
            logging.error(f"Database file not found: {DB_PATH}")
            return None

        # Connect to database
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        cursor = conn.cursor()

        # Fetch all articles, ordered by published_date descending (newest first)
        cursor.execute("""
            SELECT id, title, source_url, summary, category, published_date, slug
            FROM articles
            ORDER BY published_date DESC
        """)

        # Convert rows to dictionaries
        articles = [dict(row) for row in cursor.fetchall()]

        # Write to JSON
        try:
            with ARTICLES_JSON.open('w', encoding='utf-8') as f:
                json.dump(articles, f, indent=2, ensure_ascii=False)
        except IOError as e:
            logging.error(f"Failed to write {ARTICLES_JSON}: {e}")
            conn.close()
            return None

        conn.close()
        logging.info(f"Exported {len(articles)} articles to {ARTICLES_JSON}")
        return articles

    except sqlite3.Error as e:
        logging.error(f"Database error during article export: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error during article export: {e}")
        return None


def export_categories(articles):
    """Export unique categories to JSON, sorted alphabetically.

    Args:
        articles: List of article dictionaries

    Returns:
        List of category strings, or None if export fails
    """
    try:
        # Extract unique categories
        categories = sorted(set(article['category'] for article in articles))

        # Write to JSON
        try:
            with CATEGORIES_JSON.open('w', encoding='utf-8') as f:
                json.dump(categories, f, indent=2, ensure_ascii=False)
        except IOError as e:
            logging.error(f"Failed to write {CATEGORIES_JSON}: {e}")
            return None

        logging.info(f"Exported {len(categories)} categories to {CATEGORIES_JSON}")
        return categories

    except Exception as e:
        logging.error(f"Error during category export: {e}")
        return None


def main():
    """Main export function."""
    logging.info("Exporting data from SQLite to JSON...")

    # Export articles
    articles = export_articles()
    if articles is None:
        logging.error("Article export failed. Exiting.")
        sys.exit(1)

    # Export categories
    categories = export_categories(articles)
    if categories is None:
        logging.error("Category export failed. Exiting.")
        sys.exit(1)

    logging.info("Export complete!")
    logging.info(f"  Articles: {len(articles)}")
    logging.info(f"  Categories: {', '.join(categories)}")
    sys.exit(0)


if __name__ == "__main__":
    main()
