"""Unit tests for the pipeline's pure functions and the database migration.

Run from anywhere:

    python -m pytest scripts/test_pipeline.py -q

CI runs this in the import-check job of dependency-check.yml. Nothing here
touches the network or data/articles.db: database tests use a temporary file.
"""

import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import database  # noqa: E402
from article_processing import is_junk_summary  # noqa: E402
from config import load_config  # noqa: E402
import config as config_module  # noqa: E402
from database import (  # noqa: E402
    FALLBACK_SLUG,
    MAX_SLUG_BYTES,
    generate_slug,
    init_database,
    insert_article,
    is_duplicate,
    normalize_title,
    unique_slug,
)
from export_for_astro import clean_title, extract_source_name  # noqa: E402
from fetch_articles import resolve_published_date  # noqa: E402


# --- generate_slug ---------------------------------------------------------

# The cap is a documented requirement (CLAUDE.md: "capped at 100 UTF-8 bytes"),
# so the tests assert the literal, not the module constant: raising the constant
# must fail them.
SLUG_CAP = 100


def test_slug_cap_is_100_bytes():
    assert MAX_SLUG_BYTES == SLUG_CAP

@pytest.mark.parametrize("title, expected", [
    ("Hello World", "hello-world"),
    ("Quantum: Computing & You!", "quantum-computing-you"),
    ("  Leading and trailing  ", "leading-and-trailing"),
    ("Multiple   spaces -- and hyphens", "multiple-spaces-and-hyphens"),
    ("Already-hyphenated title", "already-hyphenated-title"),
    ("Tesla's Q3 results: 2026", "teslas-q3-results-2026"),
])
def test_generate_slug_basic(title, expected):
    assert generate_slug(title) == expected


def test_generate_slug_strips_html_tags_and_entities():
    # Legacy Google Alerts titles carried <b>...</b> search-term highlighting,
    # which once produced slugs like "bsim-racingb-rig-costs" (issue #6).
    assert generate_slug("<b>Sim Racing</b> Rig Costs") == "sim-racing-rig-costs"
    assert generate_slug("Tom &amp; Jerry &lt;3 Cheese") == "tom-jerry-3-cheese"
    assert generate_slug("<a href='x'>Linked</a> title") == "linked-title"


@pytest.mark.parametrize("title", ["", "   ", "---", "🚀🚀🚀", "<b></b>", "!!! ???"])
def test_generate_slug_fallback_when_nothing_usable(title):
    assert generate_slug(title) == FALLBACK_SLUG


def test_generate_slug_caps_length_at_word_boundary():
    words = ["quantum", "computing", "explained", "simply", "for", "everyday", "users"] * 10
    title = " ".join(words)
    full = "-".join(words)
    slug = generate_slug(title)

    assert len(slug.encode("utf-8")) <= SLUG_CAP
    assert not slug.endswith("-")
    assert full.startswith(slug)
    # Cut landed between words, not inside one
    assert full[len(slug)] == "-"


def test_generate_slug_short_titles_are_not_truncated():
    title = "a" * SLUG_CAP
    assert generate_slug(title) == title


def test_generate_slug_no_spaces_is_hard_cut():
    slug = generate_slug("a" * 150)
    assert len(slug) == SLUG_CAP


def test_generate_slug_counts_bytes_not_characters_and_never_splits_a_character():
    # Each CJK character is 3 bytes; 60 of them is 180 bytes
    slug = generate_slug("量" * 60)
    assert len(slug.encode("utf-8")) <= SLUG_CAP
    assert set(slug) == {"量"}
    assert len(slug) == SLUG_CAP // 3


def test_generate_slug_cjk_with_spaces_cuts_at_word_boundary():
    title = " ".join(["量子計算機"] * 20)
    slug = generate_slug(title)
    assert len(slug.encode("utf-8")) <= SLUG_CAP
    assert all(part == "量子計算機" for part in slug.split("-"))


def test_generate_slug_is_stable():
    title = "Stable Slugs Are Never Regenerated"
    assert generate_slug(title) == generate_slug(title)


# --- unique_slug -----------------------------------------------------------

@pytest.fixture
def cursor():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE articles (id INTEGER PRIMARY KEY, slug TEXT NOT NULL)")
    yield conn.cursor()
    conn.close()


def test_unique_slug_returns_slug_when_free(cursor):
    assert unique_slug(cursor, "fresh") == "fresh"


def test_unique_slug_takes_lowest_free_suffix(cursor):
    cursor.executemany("INSERT INTO articles (slug) VALUES (?)", [("taken",), ("taken-2",), ("taken-4",)])
    assert unique_slug(cursor, "taken") == "taken-3"


def test_unique_slug_suffix_does_not_collide_with_a_real_title(cursor):
    # A title that genuinely ends in "-2" occupies that slug; the next clash skips it
    cursor.executemany("INSERT INTO articles (slug) VALUES (?)", [("race",), ("race-2",)])
    assert unique_slug(cursor, "race") == "race-3"
    assert unique_slug(cursor, "race-2") == "race-2-2"


# --- init_database migration -----------------------------------------------

OLD_SCHEMA = """
    CREATE TABLE articles (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        source_url TEXT NOT NULL,
        summary TEXT,
        category TEXT NOT NULL,
        published_date TEXT,
        slug TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
"""


@pytest.fixture
def legacy_db(tmp_path, monkeypatch):
    """A pre-migration database: no extraction_method column, no slug index,
    three articles sharing one slug and one on its own."""
    path = tmp_path / "articles.db"
    monkeypatch.setattr(database, "DB_PATH", path)
    conn = sqlite3.connect(path)
    conn.execute(OLD_SCHEMA)
    rows = [
        (1, "Dup", "https://a.example/1", "s", "Cat", "2026-01-01T00:00:00", "dup", "2026-01-01"),
        (2, "Dup", "https://a.example/2", "s", "Cat", "2026-03-01T00:00:00", "dup", "2026-03-01"),
        (3, "Dup", "https://a.example/3", "s", "Cat", "2026-02-01T00:00:00", "dup", "2026-02-01"),
        (4, "Solo", "https://a.example/4", "s", "Cat", "2026-02-15T00:00:00", "solo", "2026-02-15"),
    ]
    conn.executemany("INSERT INTO articles VALUES (?, ?, ?, ?, ?, ?, ?, ?)", rows)
    conn.commit()
    conn.close()
    return path


def slugs_by_id(conn):
    return dict(conn.execute("SELECT id, slug FROM articles ORDER BY id").fetchall())


def test_migration_keeps_the_published_article_on_its_url(legacy_db):
    conn = init_database()
    # Export order is published_date DESC (2, 3, 1): Astro gave the page to the
    # last one, id 1, so id 1 keeps "dup" and the others get suffixes in id order.
    assert slugs_by_id(conn) == {1: "dup", 2: "dup-2", 3: "dup-3", 4: "solo"}
    conn.close()


def test_migration_backfills_extraction_method_and_adds_index(legacy_db):
    conn = init_database()
    methods = {m for (m,) in conn.execute("SELECT DISTINCT extraction_method FROM articles")}
    assert methods == {database.LEGACY_EXTRACTION_METHOD}
    indexes = {n for (n,) in conn.execute("SELECT name FROM sqlite_master WHERE type = 'index'")}
    assert "idx_articles_slug" in indexes
    conn.close()


def test_migration_is_idempotent(legacy_db):
    conn = init_database()
    first = slugs_by_id(conn)
    conn.close()
    conn = init_database()
    assert slugs_by_id(conn) == first
    conn.close()


def test_unique_index_rejects_a_duplicate_slug_after_migration(legacy_db):
    conn = init_database()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO articles (title, source_url, category, slug, created_at) VALUES ('x', 'u', 'c', 'dup', 't')"
        )
    conn.close()


def test_insert_article_assigns_next_free_slug_and_current_method(legacy_db):
    conn = init_database()
    assert insert_article(conn, "Dup", "https://a.example/5", "summary", "Cat", "2026-04-01T00:00:00")
    row = conn.execute("SELECT slug, extraction_method FROM articles WHERE source_url = 'https://a.example/5'").fetchone()
    assert row == ("dup-4", database.EXTRACTION_METHOD)
    conn.close()


def test_insert_article_slug_is_never_longer_than_cap_plus_suffix(legacy_db):
    conn = init_database()
    title = "word " * 60
    assert insert_article(conn, title, "https://a.example/long1", "s", "Cat", None)
    assert insert_article(conn, title, "https://a.example/long2", "s", "Cat", None)
    slugs = [s for (s,) in conn.execute("SELECT slug FROM articles WHERE source_url LIKE '%long%' ORDER BY id")]
    assert slugs[1] == slugs[0] + "-2"
    assert len(slugs[0].encode("utf-8")) <= SLUG_CAP
    conn.close()


# --- deduplication ---------------------------------------------------------

def test_normalize_title():
    assert normalize_title("  Hello World  ") == "hello world"
    assert normalize_title("ALL CAPS") == "all caps"


def test_is_duplicate_matches_on_url(legacy_db):
    conn = init_database()
    assert is_duplicate(conn, "Completely different title", "https://a.example/1")
    assert not is_duplicate(conn, "Dup", "https://a.example/new")
    conn.close()


# --- junk detection --------------------------------------------------------

@pytest.mark.parametrize("summary, pattern", [
    ("We use cookies to improve your experience.", "we use cookies"),
    ("Checking your browser before accessing the site.", "checking your browser"),
    ("Please verify you are not a robot to continue.", "verify you are not a robot"),
    ("SUBSCRIBE TO CONTINUE READING this story", "subscribe to continue reading"),
])
def test_is_junk_summary_matches_known_patterns(summary, pattern):
    assert is_junk_summary(summary) == pattern


@pytest.mark.parametrize("summary", [
    None,
    "",
    "Researchers demonstrated a 50-qubit error-corrected processor on Tuesday.",
    "The cookie recipe calls for brown sugar.",  # "cookie" alone is not junk
])
def test_is_junk_summary_passes_real_text(summary):
    assert is_junk_summary(summary) is None


# --- published date --------------------------------------------------------

def test_resolve_published_date_prefers_gnews_rfc2822():
    assert resolve_published_date("Tue, 16 Feb 2021 11:50:43 GMT", datetime(2020, 1, 1)) == "2021-02-16T11:50:43+00:00"


def test_resolve_published_date_falls_back_to_newspaper_datetime():
    assert resolve_published_date("not a date", datetime(2026, 9, 21, 8, 30)) == "2026-09-21T08:30:00"
    assert resolve_published_date(None, datetime(2026, 9, 21, tzinfo=timezone.utc)) == "2026-09-21T00:00:00+00:00"


def test_resolve_published_date_falls_back_to_now():
    value = resolve_published_date(None, None)
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", value)
    assert value[:4] == str(datetime.utcnow().year)


# --- export helpers --------------------------------------------------------

@pytest.mark.parametrize("title, expected", [
    ("Big News - The Source", "Big News"),
    ("A - B - C", "A - B"),
    ("No delimiter here", "No delimiter here"),
    ("Hyphen-ated word - Site", "Hyphen-ated word"),
])
def test_clean_title(title, expected):
    assert clean_title(title) == expected


@pytest.mark.parametrize("url, expected", [
    ("https://www.example.com/path?q=1", "example.com"),
    ("http://news.example.co.uk/x", "news.example.co.uk"),
    ("", ""),
    ("not a url", ""),
])
def test_extract_source_name(url, expected):
    assert extract_source_name(url) == expected


# --- config ----------------------------------------------------------------

@pytest.fixture
def config_file(tmp_path, monkeypatch):
    path = tmp_path / "feeds.config.json"
    monkeypatch.setattr(config_module, "CONFIG_PATH", path)
    return path


def test_load_config_valid(config_file):
    config_file.write_text("""{
        "gnews_settings": {"language": "en", "country": "US", "max_results": 10, "period": "1d"},
        "excluded_domains": ["youtube.com"],
        "feeds": [{"query": "Sim Racing", "category": "Sim Racing"}]
    }""")
    config = load_config()
    assert config["feeds"] == [{"query": "Sim Racing", "category": "Sim Racing"}]
    assert config["excluded_domains"] == ["youtube.com"]
    assert config["gnews_settings"]["period"] == "1d"


def test_load_config_skips_malformed_feeds_but_keeps_valid_ones(config_file):
    config_file.write_text("""{
        "gnews_settings": {"language": "en", "country": "US", "max_results": 10, "period": "1d"},
        "feeds": [{"query": "", "category": "Empty"}, {"query": "Ok"}, "junk", {"query": "Good", "category": "Good"}]
    }""")
    config = load_config()
    assert config["feeds"] == [{"query": "Good", "category": "Good"}]
    assert config["excluded_domains"] == []


@pytest.mark.parametrize("body", [
    '{"feeds": [{"query": "q", "category": "c"}]}',  # no gnews_settings
    '{"gnews_settings": {"language": "en"}, "feeds": [{"query": "q", "category": "c"}]}',  # missing fields
    '{"gnews_settings": {"language": "en", "country": "US", "max_results": 1, "period": "1d"}, "feeds": []}',
    '{not json',
])
def test_load_config_rejects_invalid_config(config_file, body):
    config_file.write_text(body)
    assert load_config() is None


def test_load_config_missing_file(config_file):
    assert load_config() is None
