"""Article fetching module for RSS feed parsing."""

import feedparser
import logging
from datetime import datetime


def parse_feed(feed_url):
    """Parse an RSS feed and extract entries.

    Args:
        feed_url: The URL of the RSS feed

    Returns:
        List of feed entries, or None if parsing fails
    """
    try:
        feed = feedparser.parse(feed_url)

        # Check if feed was successfully retrieved
        if hasattr(feed, 'bozo_exception'):
            logging.error(f"Error parsing feed {feed_url}: {feed.bozo_exception}")
            return None

        return feed.entries

    except Exception as e:
        logging.error(f"Network failure fetching feed {feed_url}: {e}")
        return None


def extract_entry_metadata(entry):
    """Extract metadata from a feed entry.

    Args:
        entry: A feedparser entry object

    Returns:
        Dictionary with title, link, and published_date, or None if entry is invalid
    """
    # Validate that entry has a title
    if not hasattr(entry, 'title') or not entry.title:
        logging.warning("Skipping entry without title")
        return None

    # Extract title
    title = entry.title

    # Extract link
    link = entry.link if hasattr(entry, 'link') else None
    if not link:
        logging.warning(f"Skipping entry '{title}' without link")
        return None

    # Extract published date or use current timestamp
    published_date = None
    if hasattr(entry, 'published'):
        published_date = entry.published
    elif hasattr(entry, 'published_parsed') and entry.published_parsed:
        # Convert time struct to ISO 8601 string
        published_date = datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%dT%H:%M:%S")
    else:
        # Use current timestamp as fallback
        published_date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
        logging.info(f"Using current timestamp for entry '{title}' (missing published date)")

    return {
        'title': title,
        'link': link,
        'published_date': published_date
    }


def fetch_articles_from_feed(feed_url, category):
    """Fetch and process all articles from a single RSS feed.

    Args:
        feed_url: The URL of the RSS feed
        category: The category to assign to articles from this feed

    Returns:
        List of article metadata dictionaries with added category field
    """
    entries = parse_feed(feed_url)

    if entries is None:
        return []

    articles = []
    for entry in entries:
        metadata = extract_entry_metadata(entry)
        if metadata:
            metadata['category'] = category
            articles.append(metadata)

    return articles
