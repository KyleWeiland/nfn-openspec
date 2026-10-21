"""Smoke test for the pipeline's runtime dependencies.

dependency-check.yml imports every pipeline module, which catches a removed
function but not a changed behaviour. This script exercises the parts of the
pipeline that only the daily run otherwise reaches:

  1. the NLTK tokenizer download that Newspaper4k's summarizer needs
  2. Newspaper4k extraction and summarization, offline, on a bundled fixture
  3. one gnews search and the Google News URL decode (network)
  4. one real article extraction from those results (network)

Run from the scripts/ directory, like the pipeline itself:

    python smoke_test.py            # all checks
    python smoke_test.py --offline  # checks 1 and 2 only

Exits non-zero and prints a traceback for every check that failed.
"""

import argparse
import logging
import sys
import traceback
from pathlib import Path

FIXTURE = Path(__file__).parent / "fixtures" / "smoke_article.html"
FIXTURE_URL = "https://example.com/how-a-static-news-site-rebuilds-itself"
SEARCH_QUERY = "Cybersecurity"
MIN_FIXTURE_WORDS = 300
MIN_SUMMARY_WORDS = 20

logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")


def check_tokenizer():
    """nltk.download('punkt_tab') works and the tokenizer splits sentences."""
    import nltk

    nltk.download("punkt_tab", quiet=True)
    nltk.data.find("tokenizers/punkt_tab")
    sentences = nltk.sent_tokenize("The first sentence ends here. The second one follows it.")
    assert len(sentences) == 2, f"expected 2 sentences, got {sentences!r}"


def check_summarizer():
    """Newspaper4k extracts and summarizes the bundled fixture without the network."""
    import newspaper
    from article_processing import is_junk_summary

    html = FIXTURE.read_text(encoding="utf-8")
    article = newspaper.Article(FIXTURE_URL)
    article.download(input_html=html)
    article.parse()

    words = len(article.text.split())
    assert words >= MIN_FIXTURE_WORDS, f"extracted only {words} words from the fixture"
    assert article.title, "no title extracted from the fixture"

    article.nlp()
    summary = article.summary.strip()
    assert len(summary.split()) >= MIN_SUMMARY_WORDS, f"summary too short: {summary!r}"
    assert is_junk_summary(summary) is None, f"fixture summary matched a junk pattern: {summary!r}"
    assert len(summary) < len(article.text), "summary is not shorter than the article"


def check_search():
    """gnews returns results and googlenewsdecoder resolves them to publisher URLs."""
    from gnews import GNews
    from article_fetching import fetch_articles_from_feed

    client = GNews(
        language="en",
        country="US",
        max_results=5,
        period="7d",
        exclude_websites=["youtube.com", "reddit.com"],
    )
    articles = fetch_articles_from_feed(client, SEARCH_QUERY, "smoke")
    assert articles, f"gnews returned no results for {SEARCH_QUERY!r}"

    decoded = [a for a in articles if "news.google.com" not in a["url"]]
    assert decoded, (
        "none of the Google News URLs could be decoded to a publisher URL: "
        + ", ".join(a["url"] for a in articles)
    )
    return decoded


def check_extraction(articles):
    """process_article() produces a usable summary for at least one real result."""
    from article_processing import process_article

    attempts = []
    for article in articles:
        result = process_article(article["url"])
        if result and len(result["summary"].split()) >= MIN_SUMMARY_WORDS:
            print(f"      extracted: {article['url']}")
            return
        attempts.append(article["url"])
    raise AssertionError(
        f"no usable summary from {len(attempts)} article(s): " + ", ".join(attempts)
    )


def run(name, func, *args):
    try:
        value = func(*args)
    except Exception:
        print(f"FAIL  {name}")
        traceback.print_exc()
        return False, None
    print(f"ok    {name}")
    return True, value


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--offline", action="store_true", help="skip the checks that use the network")
    args = parser.parse_args()

    failed = []

    ok, _ = run("tokenizer download (nltk punkt_tab)", check_tokenizer)
    if not ok:
        failed.append("tokenizer")

    ok, _ = run("summarize bundled fixture (Newspaper4k + NLTK)", check_summarizer)
    if not ok:
        failed.append("summarizer")

    if not args.offline:
        ok, articles = run(f"gnews search + URL decode ({SEARCH_QUERY!r})", check_search)
        if not ok:
            failed.append("search")
        else:
            ok, _ = run("extract a real article (process_article)", check_extraction, articles)
            if not ok:
                failed.append("extraction")

    if failed:
        print(f"\n{len(failed)} check(s) failed: {', '.join(failed)}")
        sys.exit(1)
    print("\nall checks passed")


if __name__ == "__main__":
    main()
