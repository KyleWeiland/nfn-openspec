"""Article processing module using Newspaper4k."""

import logging
import newspaper


DOWNLOAD_TIMEOUT = 30  # seconds
BROWSER_USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/120.0.0.0 Safari/537.36'
)


def process_article(url):
    """Download, extract, and summarize an article using Newspaper4k.

    Args:
        url: The article URL

    Returns:
        Dictionary with 'summary' and 'publish_date' keys, or None if processing fails
    """
    try:
        config = newspaper.Config()
        config.request_timeout = DOWNLOAD_TIMEOUT
        config.browser_user_agent = BROWSER_USER_AGENT

        article = newspaper.Article(url, config=config)
        article.download()
        article.parse()

    except Exception as e:
        logging.warning(f"Failed to download/parse article {url}: {e}")
        return None

    if not article.text:
        logging.warning(f"No text extracted from article: {url}")
        return None

    try:
        article.nlp()
        summary = article.summary
    except Exception as e:
        logging.warning(f"NLP failed for {url}: {e}")
        summary = ''

    if not summary and article.text:
        # Fallback: truncate article text to ~300 words
        words = article.text.split()
        summary = ' '.join(words[:300])

    if not summary:
        logging.warning(f"Could not generate summary for: {url}")
        return None

    return {
        'summary': summary,
        'publish_date': article.publish_date,
    }
