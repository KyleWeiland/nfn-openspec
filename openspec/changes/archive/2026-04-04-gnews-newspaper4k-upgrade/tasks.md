## 1. Dependencies

- [x] 1.1 Update `scripts/requirements.txt`: remove `feedparser` and `trafilatura`; add `gnews`, `newspaper4k`, `lxml_html_clean`, and `googlenewsdecoder`

## 2. Feed Configuration

- [x] 2.1 Rewrite `feeds.config.json` with the new format: add top-level `gnews_settings` block (`language`, `country`, `max_results`, `period`) and `excluded_domains` array
- [x] 2.2 Convert each existing feed entry from `{"url": "...", "category": "..."}` to `{"query": "<category>", "category": "<category>"}` — populate all 9 existing categories (Autonomous Trucks, Autonomous Vehicles, Connected Car, Cybersecurity, Image Recognition, IoT Cyber, Quantum Computers, Smart Cities, Sim Racing)

## 3. Pipeline Rewrite — Discovery (gnews)

- [x] 3.1 Remove `import feedparser` and all redirect-URL parsing code from `scripts/fetch_articles.py`
- [x] 3.2 Add `from gnews import GNews` import and NLTK startup download (`nltk.download('punkt_tab', quiet=True)`)
- [x] 3.3 Load `gnews_settings` and `excluded_domains` from config; instantiate `GNews` with those settings and `exclude_websites`
- [x] 3.4 For each feed entry, call `google_news.get_news(query)` and collect results; log a warning (don't error) if a query returns zero results
- [x] 3.5 Decode Google News internal URLs (`news.google.com/rss/articles/CBMi...`) to actual article URLs using `googlenewsdecoder` before passing to Newspaper4k

## 4. Pipeline Rewrite — Processing (Newspaper4k)

- [x] 4.1 Remove `import trafilatura` and all trafilatura extraction code
- [x] 4.2 Add `import newspaper` (Newspaper4k) import
- [x] 4.3 For each gnews result, create a `newspaper.Article(url)` with `config.request_timeout=30` and a standard `browser_user_agent`; call `download()` and `parse()`; wrap in try/except — log warning and skip on any failure
- [x] 4.4 Call `article.nlp()` to generate the NLP summary; use `article.summary` as the stored summary
- [x] 4.5 Implement fallback: if `article.summary` is empty but `article.text` is non-empty, truncate `article.text` to ~300 words as the summary; skip article if both are empty
- [x] 4.6 Use gnews `published_date` (convert datetime to ISO string with `.isoformat()`) as primary date; fall back to `article.publish_date` if gnews date is missing; fall back to current timestamp if both are absent

## 5. Docs

- [x] 5.1 Update `CLAUDE.md` architecture section: replace feedparser/trafilatura/Google Alerts RSS references with gnews/Newspaper4k; note no API key needed
- [x] 5.2 Update `README.md` feed configuration section: document new `feeds.config.json` format (query/category pairs, gnews_settings, excluded_domains) and update setup instructions to include `newspaper4k` and NLTK
