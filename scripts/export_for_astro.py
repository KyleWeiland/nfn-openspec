"""Export articles and categories from SQLite to JSON for Astro."""

import sqlite3
import json
import os


DB_PATH = "data/articles.db"
ARTICLES_JSON = "data/articles.json"
CATEGORIES_JSON = "data/categories.json"


def export_articles():
    """Export all articles from SQLite to JSON, ordered by date descending."""
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)

    # Connect to database
    conn = sqlite3.connect(DB_PATH)
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
    with open(ARTICLES_JSON, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)

    conn.close()
    print(f"Exported {len(articles)} articles to {ARTICLES_JSON}")
    return articles


def export_categories(articles):
    """Export unique categories to JSON, sorted alphabetically."""
    # Extract unique categories
    categories = sorted(set(article['category'] for article in articles))

    # Write to JSON
    with open(CATEGORIES_JSON, 'w', encoding='utf-8') as f:
        json.dump(categories, f, indent=2, ensure_ascii=False)

    print(f"Exported {len(categories)} categories to {CATEGORIES_JSON}")
    return categories


def main():
    """Main export function."""
    print("Exporting data from SQLite to JSON...")

    # Export articles
    articles = export_articles()

    # Export categories
    categories = export_categories(articles)

    print("\nExport complete!")
    print(f"  Articles: {len(articles)}")
    print(f"  Categories: {', '.join(categories)}")


if __name__ == "__main__":
    main()
