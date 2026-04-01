"""Simple unit tests for the article pipeline modules."""

import sys
sys.path.insert(0, '.')

from database import generate_slug, normalize_title
from url_extraction import is_google_alerts_redirect, extract_actual_url, is_valid_url


def test_slug_generation():
    """Test slug generation function."""
    print("Testing slug generation...")

    test_cases = [
        ("Apple Releases New iPhone", "apple-releases-new-iphone"),
        ("Breaking: Tech Company's Big Win!", "breaking-tech-companys-big-win"),
        ("Multiple   Spaces   Here", "multiple-spaces-here"),
        ("Special!@#$%Characters", "specialcharacters"),
    ]

    for title, expected_slug in test_cases:
        actual_slug = generate_slug(title)
        status = "✓" if actual_slug == expected_slug else "✗"
        print(f"  {status} '{title}' → '{actual_slug}' (expected: '{expected_slug}')")

    print()


def test_title_normalization():
    """Test title normalization for deduplication."""
    print("Testing title normalization...")

    test_cases = [
        ("Tech News", "tech news"),
        (" tech news ", "tech news"),
        ("TECH NEWS", "tech news"),
        ("  Multiple   Spaces  ", "multiple   spaces"),
    ]

    for title, expected in test_cases:
        actual = normalize_title(title)
        status = "✓" if actual == expected else "✗"
        print(f"  {status} '{title}' → '{actual}' (expected: '{expected}')")

    print()


def test_url_detection():
    """Test Google Alerts redirect URL detection."""
    print("Testing URL redirect detection...")

    test_cases = [
        ("https://www.google.com/url?q=https://example.com", True),
        ("https://example.com/article", False),
        ("http://www.google.com/url?test=1", False),  # Must be https
    ]

    for url, expected in test_cases:
        actual = is_google_alerts_redirect(url)
        status = "✓" if actual == expected else "✗"
        print(f"  {status} is_redirect('{url[:50]}...') → {actual} (expected: {expected})")

    print()


def test_url_validation():
    """Test URL validation."""
    print("Testing URL validation...")

    test_cases = [
        ("https://example.com", True),
        ("http://example.com/article", True),
        ("ftp://example.com", False),
        ("not-a-url", False),
        ("", False),
    ]

    for url, expected in test_cases:
        actual = is_valid_url(url)
        status = "✓" if actual == expected else "✗"
        print(f"  {status} is_valid('{url}') → {actual} (expected: {expected})")

    print()


def test_url_extraction():
    """Test URL extraction from Google Alerts redirects."""
    print("Testing URL extraction...")

    # Test case with a Google Alerts redirect
    redirect_url = "https://www.google.com/url?rct=j&sa=t&url=https%3A%2F%2Fexample.com%2Farticle&ct=ga"
    expected = "https://example.com/article"
    actual = extract_actual_url(redirect_url)
    status = "✓" if actual == expected else "✗"
    print(f"  {status} Extracted URL: {actual} (expected: {expected})")

    # Test case with missing url parameter
    invalid_redirect = "https://www.google.com/url?rct=j&sa=t"
    actual = extract_actual_url(invalid_redirect)
    status = "✓" if actual is None else "✗"
    print(f"  {status} Invalid redirect returns None: {actual} (expected: None)")

    print()


if __name__ == "__main__":
    print("=" * 60)
    print("Running Pipeline Module Tests")
    print("=" * 60)
    print()

    test_slug_generation()
    test_title_normalization()
    test_url_detection()
    test_url_validation()
    test_url_extraction()

    print("=" * 60)
    print("Tests complete!")
    print("=" * 60)
