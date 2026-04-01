"""Main pipeline script for fetching and processing news articles."""

import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def check_dependencies():
    """Validate that required dependencies are available.

    Returns:
        True if all dependencies are available, False otherwise
    """
    try:
        import feedparser
        import trafilatura
        return True
    except ImportError as e:
        logging.error(f"Missing dependency: {e}")
        logging.error("Please install dependencies with: pip install -r requirements.txt")
        return False


def main():
    """Main pipeline execution function."""
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Import modules after dependency check
    from config import load_config
    from database import init_database, is_duplicate, insert_article
    from article_fetching import fetch_articles_from_feed
    from url_extraction import get_article_url
    from article_processing import process_article

    # Load configuration
    logging.info("Loading configuration...")
    feeds = load_config()
    if feeds is None:
        logging.error("Failed to load configuration. Exiting.")
        sys.exit(1)

    # Initialize database
    logging.info("Initializing database...")
    conn = init_database()

    # Track statistics
    total_processed = 0
    total_stored = 0
    total_skipped = 0
    total_failed = 0

    # Process each feed
    for feed_config in feeds:
        feed_url = feed_config['url']
        category = feed_config['category']

        logging.info(f"Processing feed: {feed_url} (Category: {category})")

        # Fetch articles from feed
        articles = fetch_articles_from_feed(feed_url, category)

        if not articles:
            logging.warning(f"No articles fetched from feed: {feed_url}")
            continue

        logging.info(f"Found {len(articles)} article(s) in feed")

        # Process each article
        for article_meta in articles:
            total_processed += 1
            title = article_meta['title']
            link = article_meta['link']
            published_date = article_meta['published_date']

            logging.info(f"Processing: {title}")

            # Extract actual URL from Google Alerts redirect if needed
            actual_url = get_article_url(link)
            if not actual_url:
                logging.error(f"Failed to extract URL for: {title}")
                total_failed += 1
                continue

            # Check for duplicates
            if is_duplicate(conn, title, actual_url):
                logging.info(f"Skipping duplicate: {title}")
                total_skipped += 1
                continue

            # Download and process article
            result = process_article(actual_url)
            if not result:
                logging.error(f"Failed to process article: {title}")
                total_failed += 1
                continue

            summary = result['summary']

            # Store in database
            if insert_article(conn, title, actual_url, summary, category, published_date):
                logging.info(f"Stored: {title} ({category})")
                total_stored += 1
            else:
                logging.error(f"Failed to store article: {title}")
                total_failed += 1

    # Close database connection
    conn.close()

    # Print summary
    logging.info("=" * 60)
    logging.info("Pipeline execution complete")
    logging.info(f"Total articles processed: {total_processed}")
    logging.info(f"Articles stored: {total_stored}")
    logging.info(f"Duplicates skipped: {total_skipped}")
    logging.info(f"Failed: {total_failed}")
    logging.info("=" * 60)

    # Exit with status code 0 (success)
    sys.exit(0)


if __name__ == "__main__":
    main()
