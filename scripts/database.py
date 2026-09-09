"""Database operations module for article storage."""

import sqlite3
import os
import re
import logging
from datetime import datetime
from pathlib import Path


# Get repository root (parent of scripts directory)
REPO_ROOT = Path(__file__).parent.parent
DB_PATH = REPO_ROOT / "data" / "articles.db"

# Identifies which extraction pipeline produced a row. Rows predating the
# gnews/Newspaper4k migration are backfilled as "trafilatura".
EXTRACTION_METHOD = "newspaper4k"
LEGACY_EXTRACTION_METHOD = "trafilatura"


def init_database():
    """Initialize the database and create the articles table if it doesn't exist.

    Returns:
        sqlite3.Connection: Database connection object
    """
    # Ensure data directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Connect to database
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # Create articles table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            source_url TEXT NOT NULL,
            summary TEXT,
            category TEXT NOT NULL,
            published_date TEXT,
            slug TEXT NOT NULL,
            created_at TEXT NOT NULL,
            extraction_method TEXT
        )
    """)

    # Migrate pre-existing databases: the table above is only created once, so
    # older databases need the column added and their rows attributed.
    cursor.execute("PRAGMA table_info(articles)")
    columns = {row[1] for row in cursor.fetchall()}
    if "extraction_method" not in columns:
        logging.info("Migrating database: adding extraction_method column")
        cursor.execute("ALTER TABLE articles ADD COLUMN extraction_method TEXT")

    # Attribute any unmarked rows to the legacy pipeline. Idempotent.
    cursor.execute(
        "UPDATE articles SET extraction_method = ? WHERE extraction_method IS NULL",
        (LEGACY_EXTRACTION_METHOD,)
    )
    if cursor.rowcount > 0:
        logging.info(f"Marked {cursor.rowcount} existing article(s) as {LEGACY_EXTRACTION_METHOD}")

    conn.commit()
    return conn


def generate_slug(title):
    """Generate a URL-friendly slug from a title.

    Args:
        title: The article title

    Returns:
        A slugified version of the title
    """
    # Convert to lowercase
    slug = title.lower()

    # Replace spaces and special characters with hyphens
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)

    # Remove leading/trailing hyphens
    slug = slug.strip('-')

    return slug


def normalize_title(title):
    """Normalize a title for deduplication.

    Args:
        title: The article title

    Returns:
        Normalized title (lowercase, stripped whitespace)
    """
    return title.lower().strip()


def is_duplicate(conn, title, source_url):
    """Check if an article is a duplicate based on normalized title and source URL.

    Args:
        conn: Database connection
        title: Article title
        source_url: Article source URL

    Returns:
        True if the article is a duplicate, False otherwise
    """
    cursor = conn.cursor()
    normalized = normalize_title(title)

    # Check for exact source URL match (regardless of title)
    cursor.execute(
        "SELECT COUNT(*) FROM articles WHERE source_url = ?",
        (source_url,)
    )
    url_count = cursor.fetchone()[0]
    if url_count > 0:
        return True

    # Check for normalized title + source URL match
    cursor.execute(
        "SELECT COUNT(*) FROM articles WHERE LOWER(TRIM(title)) = ? AND source_url = ?",
        (normalized, source_url)
    )
    count = cursor.fetchone()[0]

    return count > 0


def get_iso8601_timestamp():
    """Generate an ISO 8601 formatted timestamp.

    Returns:
        Current UTC time in ISO 8601 format
    """
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")


def insert_article(conn, title, source_url, summary, category, published_date,
                   extraction_method=EXTRACTION_METHOD):
    """Insert an article into the database.

    Args:
        conn: Database connection
        title: Article title
        source_url: Article source URL
        summary: Article summary
        category: Article category
        published_date: Article published date
        extraction_method: Pipeline that produced this row (defaults to the current one)

    Returns:
        True if insertion successful, False otherwise
    """
    try:
        cursor = conn.cursor()

        # Generate slug and timestamp
        slug = generate_slug(title)
        created_at = get_iso8601_timestamp()

        # Insert article
        cursor.execute("""
            INSERT INTO articles (title, source_url, summary, category, published_date, slug, created_at, extraction_method)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, source_url, summary, category, published_date, slug, created_at,
              extraction_method))

        conn.commit()
        return True

    except Exception as e:
        logging.error(f"Error inserting article '{title}': {e}")
        conn.rollback()
        return False
