"""Main pipeline script for fetching and processing news articles."""

import sys
import logging
from datetime import datetime
from email.utils import parsedate_to_datetime

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
        import gnews
        import newspaper
        import googlenewsdecoder
        import nltk
        return True
    except ImportError as e:
        logging.error(f"Missing dependency: {e}")
        logging.error("Please install dependencies with: pip install -r requirements.txt")
        return False


def resolve_published_date(gnews_date, newspaper_date):
    """Resolve the best available published date to an ISO format string.

    Args:
        gnews_date: RFC 2822 string from gnews (e.g. "Tue, 16 Feb 2021 11:50:43 GMT"), or None
        newspaper_date: datetime from Newspaper4k article.publish_date, or None

    Returns:
        ISO format date string
    """
    if gnews_date:
        try:
            return parsedate_to_datetime(gnews_date).isoformat()
        except Exception:
            pass

    if newspaper_date is not None:
        if hasattr(newspaper_date, 'isoformat'):
            return newspaper_date.isoformat()
        return str(newspaper_date)

    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")


def main():
    """Main pipeline execution function."""
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Import modules after dependency check
    import nltk
    from gnews import GNews
    from config import load_config
    from database import init_database, is_duplicate, insert_article
    from article_fetching import fetch_articles_from_feed
    from article_processing import process_article

    # Newspaper4k's summarizer needs this tokenizer. Cached after first download.
    nltk.download('punkt_tab', quiet=True)

    # Load configuration
    logging.info("Loading configuration...")
    config = load_config()
    if config is None:
        logging.error("Failed to load configuration. Exiting.")
        sys.exit(1)

    gnews_settings = config['gnews_settings']
    excluded_domains = config['excluded_domains']
    feeds = config['feeds']

    # Instantiate GNews client
    google_news = GNews(
        language=gnews_settings['language'],
        country=gnews_settings['country'],
        max_results=gnews_settings['max_results'],
        period=gnews_settings['period'],
        exclude_websites=excluded_domains,
    )

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
        query = feed_config['query']
        category = feed_config['category']

        logging.info(f"Fetching articles for query: '{query}' (Category: {category})")

        # Fetch articles via gnews
        articles = fetch_articles_from_feed(google_news, query, category)

        if not articles:
            logging.warning(f"No articles fetched for query: {query}")
            continue

        logging.info(f"Found {len(articles)} article(s) for query: {query}")

        # Process each article
        for article_meta in articles:
            total_processed += 1
            title = article_meta['title']
            url = article_meta['url']
            gnews_date = article_meta['gnews_date']

            logging.info(f"Processing: {title}")

            # Check for duplicates
            if is_duplicate(conn, title, url):
                logging.info(f"Skipping duplicate: {title}")
                total_skipped += 1
                continue

            # Download and process article
            result = process_article(url)
            if not result:
                logging.warning(f"Failed to process article: {title}")
                total_failed += 1
                continue

            summary = result['summary']
            published_date = resolve_published_date(gnews_date, result.get('publish_date'))

            # Store in database
            if insert_article(conn, title, url, summary, category, published_date):
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
