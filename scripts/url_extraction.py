"""URL extraction module for Google Alerts redirect URLs."""

import urllib.parse
import logging


def is_google_alerts_redirect(url):
    """Detect if a URL is a Google Alerts redirect.

    Args:
        url: The URL to check

    Returns:
        True if the URL is a Google Alerts redirect, False otherwise
    """
    return url.startswith("https://www.google.com/url")


def extract_actual_url(redirect_url):
    """Extract the actual article URL from a Google Alerts redirect URL.

    Args:
        redirect_url: The Google Alerts redirect URL

    Returns:
        The extracted and decoded actual URL, or None if extraction fails
    """
    try:
        # Parse the redirect URL
        parsed = urllib.parse.urlparse(redirect_url)

        # Extract query parameters
        params = urllib.parse.parse_qs(parsed.query)

        # Get the 'url' parameter
        if 'url' not in params:
            logging.error(f"Missing 'url' parameter in redirect URL: {redirect_url}")
            return None

        # Get the first value (parse_qs returns lists)
        actual_url = params['url'][0]

        # URL decode the extracted URL
        actual_url = urllib.parse.unquote(actual_url)

        # Validate the extracted URL
        if not is_valid_url(actual_url):
            logging.error(f"Invalid extracted URL: {actual_url}")
            return None

        return actual_url

    except Exception as e:
        logging.error(f"Error extracting URL from {redirect_url}: {e}")
        return None


def is_valid_url(url):
    """Validate that a URL is well-formed and uses HTTP or HTTPS.

    Args:
        url: The URL to validate

    Returns:
        True if the URL is valid, False otherwise
    """
    try:
        parsed = urllib.parse.urlparse(url)
        return parsed.scheme in ('http', 'https') and bool(parsed.netloc)
    except Exception:
        return False


def get_article_url(url):
    """Get the article URL, extracting from redirect if necessary.

    Args:
        url: The URL from the RSS feed (may be a redirect)

    Returns:
        The actual article URL, or None if extraction fails
    """
    if is_google_alerts_redirect(url):
        return extract_actual_url(url)
    elif is_valid_url(url):
        return url
    else:
        logging.error(f"Invalid URL: {url}")
        return None
