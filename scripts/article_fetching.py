"""Article fetching module using gnews."""

import logging
from googlenewsdecoder import new_decoderv1


def decode_url(url):
    """Decode a Google News internal URL to the actual article URL.

    Args:
        url: URL from gnews result (may be a Google News internal URL)

    Returns:
        Actual article URL, or original URL if decoding fails
    """
    if 'news.google.com' not in url:
        return url
    try:
        result = new_decoderv1(url)
        if result.get('status') and result.get('decoded_url'):
            return result['decoded_url']
    except Exception as e:
        logging.warning(f"Failed to decode Google News URL: {e}")
    return url


def fetch_articles_from_feed(google_news, query, category):
    """Fetch articles for a search query using the provided GNews instance.

    Args:
        google_news: An instantiated GNews client
        query: The search query string
        category: The category to assign to fetched articles

    Returns:
        List of article metadata dicts with title, url, gnews_date, category
    """
    try:
        results = google_news.get_news(query)
    except Exception as e:
        logging.error(f"Error fetching news for query '{query}': {e}")
        return []

    if not results:
        logging.warning(f"No articles returned for query: {query}")
        return []

    articles = []
    for result in results:
        title = result.get('title')
        if not title:
            logging.warning("Skipping result without title")
            continue

        raw_url = result.get('url')
        if not raw_url:
            logging.warning(f"Skipping result '{title}' without URL")
            continue

        url = decode_url(raw_url)
        gnews_date = result.get('published_date')

        articles.append({
            'title': title,
            'url': url,
            'gnews_date': gnews_date,
            'category': category
        })

    return articles
