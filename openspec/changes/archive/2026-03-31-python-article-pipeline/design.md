## Context

NoFrills.news is a minimal news aggregation site that uses a static site generator (Astro). The pipeline needs to fetch articles from Google Alerts RSS feeds, process them, and store them in SQLite. The database is committed to the repo, and the frontend reads from exported JSON files. This design covers the Python-based data pipeline only—JSON export and CI/CD integration are separate concerns.

Current state: No pipeline exists yet. The `data/` and `scripts/` directories are expected to be created.

Constraints:
- Must work with Google Alerts RSS feeds (which use redirect URLs)
- Must deduplicate articles to avoid processing the same content multiple times
- Must generate concise summaries (200-300 words)
- Must handle network failures gracefully
- Database file will be committed to git

## Goals / Non-Goals

**Goals:**
- Parse RSS feeds from configurable sources
- Extract actual article URLs from Google Alerts redirects
- Download and extract clean article text
- Generate summaries within 200-300 word limit
- Store articles in SQLite with proper schema
- Deduplicate based on normalized title + source URL
- Handle errors without crashing the entire pipeline

**Non-Goals:**
- JSON export functionality (separate change)
- GitHub Actions integration (separate change)
- Frontend modifications
- Article ranking or recommendation logic
- Image extraction or storage
- Full-text search indexing

## Decisions

### 1. SQLite for storage
**Decision**: Use SQLite with the database file committed to the repository.

**Rationale**: Simple, serverless, and fits the static site model. Since article volume is manageable and the site rebuilds from scratch, committing the DB to git provides version control and simplifies deployment.

**Alternatives considered**:
- JSON files only: Harder to deduplicate and query
- External database: Adds hosting complexity and cost

### 2. Deduplication strategy
**Decision**: Normalize title (lowercase, strip whitespace) + exact source URL match.

**Rationale**: Balances simplicity with effectiveness. Article titles may have minor variations, but the combination of normalized title and exact URL catches most duplicates without expensive fuzzy matching.

**Alternatives considered**:
- Content hashing: More accurate but requires downloading every article
- URL-only: Misses duplicate content from different URLs
- Fuzzy title matching: Adds complexity and dependencies

### 3. Google Alerts URL extraction
**Decision**: Parse the redirect URL's query parameters to extract the actual article URL.

**Rationale**: Google Alerts RSS feeds contain redirect URLs (e.g., `https://www.google.com/url?rct=j&sa=t&url=<actual-url>&...`). The actual URL is in the `url` query parameter.

**Alternatives considered**:
- Follow redirects: Slower and makes unnecessary requests
- Ignore and use redirect URL: Would fail to fetch actual article content

### 4. Summary generation
**Decision**: Use trafilatura's extracted text, truncate to first 200-300 words.

**Rationale**: Simple and fast. Trafilatura extracts clean text, and taking the first 200-300 words approximates the article's introduction.

**Alternatives considered**:
- LLM-based summarization: Too expensive and slow for batch processing
- TextRank or other extractive summarization: Adds complexity without clear benefit
- No summarization: Requires storing full article text

### 5. Database schema
**Decision**: Single `articles` table with columns: id, title, source_url, summary, category, published_date, slug, created_at.

**Rationale**: Flat structure is sufficient for current needs. Slug enables human-readable URLs. Category is denormalized from feed config for query simplicity.

**Alternatives considered**:
- Separate feeds/categories table: Over-engineering for current scale
- NoSQL document store: Adds dependency without benefit

### 6. Error handling strategy
**Decision**: Log errors and continue processing remaining articles. Skip individual articles that fail extraction or parsing.

**Rationale**: Pipeline should be resilient. One bad article shouldn't block processing of hundreds of good ones.

**Alternatives considered**:
- Fail fast: Would make pipeline fragile
- Retry with backoff: Adds complexity; most failures are permanent (e.g., paywalls)

## Risks / Trade-offs

**Risk**: Trafilatura may fail to extract content from paywalled or JavaScript-heavy sites.
**Mitigation**: Log failures and skip those articles. Consider adding fallback extractors in future if needed.

**Risk**: Normalized title matching may allow near-duplicates through.
**Mitigation**: Acceptable for MVP. Can add fuzzy matching later if it becomes a problem.

**Risk**: Committing SQLite DB to git may cause merge conflicts if multiple PRs add articles simultaneously.
**Mitigation**: Current workflow is single-branch with scheduled runs. If this becomes an issue, can move to external storage.

**Risk**: Summary truncation may cut mid-sentence.
**Mitigation**: Acceptable for MVP. Can add sentence boundary detection later if needed.

**Trade-off**: Using first 200-300 words instead of true summarization means summaries may miss key points buried later in articles.
**Acceptance**: Good enough for a minimal news site. Users can click through for full article.

**Trade-off**: No retry logic means transient network failures will skip articles until next run.
**Acceptance**: Daily cron schedule means articles will be retried within 24 hours naturally.
