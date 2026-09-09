"""Article processing module using Newspaper4k."""

import logging
import newspaper


DOWNLOAD_TIMEOUT = 30  # seconds
BROWSER_USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/120.0.0.0 Safari/537.36'
)


JUNK_PATTERNS = [
    # Cookie / consent notices
    "we use cookies",
    "cookie policy",
    "by continuing you agree",
    "accept all cookies",
    # Security walls
    "establishing a secure connection",
    "checking your browser",
    "security service to protect",
    "please wait while we verify",
    # Privacy disclaimers
    "your privacy is important",
    "do not sell or share my personal",
    "review our terms of service",
    "we encourage you to review",
    # CAPTCHA
    "prove you are human",
    "complete the captcha",
    "verify you are not a robot",
    "please verify you are a human",
    # Paywall / subscription
    "subscribe to continue reading",
    "this content is for subscribers",
    "create a free account to",
]


def is_junk_summary(summary):
    """Detect summaries that contain non-article content.

    Returns the matched pattern if junk, or None if valid.
    """
    if not summary:
        return None
    lower = summary.lower()
    for pattern in JUNK_PATTERNS:
        if pattern in lower:
            return pattern
    return None


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

    # Check for junk summaries (cookie notices, security walls, etc.)
    junk_pattern = is_junk_summary(summary)
    if junk_pattern:
        logging.warning(f"Junk summary detected for {url} (matched: '{junk_pattern}')")
        # Fall back to truncated article text if available
        if article.text:
            words = article.text.split()
            fallback = ' '.join(words[:300])
            if not is_junk_summary(fallback):
                summary = fallback
            else:
                summary = ''
        else:
            summary = ''

    if not summary:
        logging.warning(f"Could not generate summary for: {url}")
        return None

    return {
        'summary': summary,
        'publish_date': article.publish_date,
    }
