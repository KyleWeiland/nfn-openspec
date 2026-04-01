"""Article processing module for downloading and extracting content."""

import requests
import trafilatura
import logging


DOWNLOAD_TIMEOUT = 30  # seconds


def download_article(url):
    """Download HTML content from an article URL.

    Args:
        url: The article URL

    Returns:
        HTML content as string, or None if download fails
    """
    try:
        response = requests.get(url, timeout=DOWNLOAD_TIMEOUT)

        # Check for HTTP errors
        if response.status_code == 404:
            logging.error(f"Article not found (404): {url}")
            return None
        elif response.status_code == 403:
            logging.error(f"Access forbidden (403): {url}")
            return None
        elif response.status_code >= 500:
            logging.error(f"Server error ({response.status_code}): {url}")
            return None
        elif response.status_code != 200:
            logging.error(f"HTTP error {response.status_code}: {url}")
            return None

        return response.text

    except requests.exceptions.Timeout:
        logging.error(f"Download timeout for {url}")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error downloading {url}: {e}")
        return None


def extract_content(html):
    """Extract clean article text from HTML.

    Args:
        html: HTML content

    Returns:
        Extracted text, or None if extraction fails
    """
    try:
        text = trafilatura.extract(html)

        if not text:
            logging.error("Trafilatura could not extract text from HTML")
            return None

        return text

    except Exception as e:
        logging.error(f"Error extracting content: {e}")
        return None


def count_words(text):
    """Count words in text by splitting on whitespace.

    Args:
        text: The text to count words in

    Returns:
        Number of words
    """
    return len(text.split())


def generate_summary(text, min_words=200, max_words=300):
    """Generate a summary from article text.

    Takes the first 200-300 words of the text.

    Args:
        text: The extracted article text
        min_words: Minimum number of words for summary
        max_words: Maximum number of words for summary

    Returns:
        Summary text (plain text, no HTML)
    """
    words = text.split()
    word_count = len(words)

    # If article is shorter than min_words, use entire text
    if word_count <= min_words:
        return text

    # Take first max_words
    summary_words = words[:max_words]
    summary = ' '.join(summary_words)

    return summary


def process_article(url):
    """Download, extract, and summarize an article.

    Args:
        url: The article URL

    Returns:
        Dictionary with 'summary' key, or None if processing fails
    """
    # Download HTML
    html = download_article(url)
    if not html:
        return None

    # Extract content
    text = extract_content(html)
    if not text:
        return None

    # Generate summary
    summary = generate_summary(text)

    return {
        'summary': summary
    }
