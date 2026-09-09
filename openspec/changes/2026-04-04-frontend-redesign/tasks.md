## 1. Pipeline: Source Domain Extraction

- [x] 1.1 Add `extract_source_name(url)` function to `scripts/export_for_astro.py` that parses domain from `source_url` (strip www., keep rest)
- [x] 1.2 Add `clean_title(title)` function that strips " - Source" suffix from article titles using the last ` - ` delimiter
- [x] 1.3 Update `export_articles()` to include `source_name` field and cleaned `title` in each article dict
- [x] 1.4 Test export with existing database — verify `source_name` values and cleaned titles in articles.json
- [x] 1.5 Update `data/articles.json` schema expectations in any documentation

## 2. Pipeline: Summary Quality Detection

- [x] 2.1 Create `is_junk_summary(summary)` function in `scripts/article_processing.py` with pattern matching for common anti-patterns (cookie notices, security walls, CAPTCHA text, privacy disclaimers)
- [x] 2.2 Integrate junk detection into the article processing flow — when junk detected, fall back to truncated `article.text` (~300 words)
- [x] 2.3 Add logging for flagged junk summaries (log the article title and matched pattern)
- [x] 2.4 Test with known junk summaries from current database to verify detection accuracy

## 3. CSS Foundation: Layout & Custom Properties

- [x] 3.1 Update `global.css` root variables: `--max-width: 1200px`, `--content-width: 94%`, add `--reading-width: 72ch`
- [x] 3.2 Replace category-specific color variables with simpler category label approach (uppercase text, no colored badges)
- [x] 3.3 Add section header styles: 2px bottom rule, uppercase title, flexbox with "All articles →" link
- [x] 3.4 Add responsive breakpoints: 768px (2-col), 900px (category 2-col list), 1000px (article sidebar), 1100px (3-col category grid)
- [x] 3.5 Update typography: tighten font sizes for meta/nav (0.7–0.75rem), increase lead story title (1.5rem), maintain body readability
- [x] 3.6 Replace card styles with divider-separated list item styles (border-bottom, no border/shadow/border-radius)
- [x] 3.7 Update dark mode variables to match new color scheme
- [x] 3.8 Add middot separator styles for nav (`a + a::before { content: "·" }`)

## 4. Navigation Component Redesign

- [x] 4.1 Rewrite `Navbar.astro` — masthead with title + tagline, separate section-nav bar below
- [x] 4.2 Implement desktop nav: inline flex-wrap flow with CSS middot separators, 0.7rem uppercase
- [x] 4.3 Implement mobile nav: 2-column grid layout, all categories visible, good tap targets
- [x] 4.4 Add active state for current category (bold text color, no underline/border)
- [x] 4.5 Pass current category as prop to Navbar for active state highlighting
- [x] 4.6 Update `BaseLayout.astro` to accommodate new masthead + nav structure

## 5. Homepage Redesign

- [x] 5.1 Rewrite `[...page].astro` homepage — remove flat article list, add Latest section + category grid
- [x] 5.2 Create `ArticleLatest.astro` component for prominent latest items (title, hook, category label, relative time, source)
- [x] 5.3 Implement Latest section: first article spans full width as lead story, remaining 4 in 2-column grid (desktop)
- [x] 5.4 Create `ArticleCompact.astro` component for category grid items (title, source, relative time — no summary)
- [x] 5.5 Implement category grid: import categories.json, filter articles per category, show top 2–3 per category
- [x] 5.6 Add section headers with "All articles →" links to category pages
- [x] 5.7 Implement responsive grid: 1-col mobile → 2-col 768px → 3-col 1100px for category sections
- [x] 5.8 Add `formatRelativeTime(dateString)` helper function (returns "2h ago", "1d ago", or absolute date if >48h)
- [x] 5.9 Remove pagination from homepage (homepage is now a curated front page, not a paginated list)

## 6. Category Page Redesign

- [x] 6.1 Update `category/[category]/[...page].astro` with new layout and wider content area
- [x] 6.2 Create `ArticleItem.astro` component for category listings (title, 2-line summary hook, relative time, source)
- [x] 6.3 Add page header with category name, article count, and "Page X of Y"
- [x] 6.4 Implement 2-column article grid on desktop (900px+)
- [x] 6.5 Apply `-webkit-line-clamp: 2` to summary hooks for consistent item height
- [x] 6.6 Pass category name to Navbar for active state
- [x] 6.7 Update Pagination component styling: subtle borders, current page uses text color fill, smaller type

## 7. Article Detail Page Redesign

- [x] 7.1 Update `article/[slug].astro` with new 2-column layout structure
- [x] 7.2 Implement reading column (72ch max-width): back nav → category label → title → byline → body → source link container
- [x] 7.3 Back link navigates to category page (not home) — use article's category to build URL
- [x] 7.4 Display "via source_name" in byline using new JSON field
- [x] 7.5 Style source link container: subtle background, label + domain link
- [x] 7.6 Create `RelatedArticles.astro` component — shows 4 most recent articles from same category (excluding current)
- [x] 7.7 Implement sticky sidebar layout on desktop (1000px+): related articles in right column with left border
- [x] 7.8 Implement stacked layout on mobile: related articles below source link

## 8. Relative Timestamp Utility

- [x] 8.1 Create shared `formatRelativeTime(dateString)` utility function accessible to all components
- [x] 8.2 Implement logic: <1h → "Xm ago", <24h → "Xh ago", <48h → "1d ago", >48h → formatted date (e.g., "Apr 2, 2026")
- [x] 8.3 Handle timezone edge cases (published_date may include timezone offset or be naive UTC)
- [x] 8.4 Apply to all components: ArticleLatest, ArticleCompact, ArticleItem, RelatedArticles

## 9. Cleanup & Removed Components

- [x] 9.1 Remove old `ArticleCard.astro` component (replaced by ArticleLatest, ArticleCompact, ArticleItem)
- [x] 9.2 Remove unused CSS: old `.article-card`, `.category-badge`, `.category-*` color classes
- [x] 9.3 Remove category color variables from `:root` and dark mode override
- [x] 9.4 Update 404 page to use new layout styling

## 10. Testing & Verification

- [x] 10.1 Run updated export script — verify `source_name` field and cleaned titles in articles.json
- [ ] 10.2 Run `npm run dev` — verify homepage renders with Latest + category grid
- [ ] 10.3 Verify category pages display 2-column grid with article counts and pagination
- [ ] 10.4 Verify article pages show reading column + related sidebar on desktop
- [ ] 10.5 Verify article pages stack properly on mobile (related below content)
- [ ] 10.6 Test navigation: middot-separated desktop, 2-col grid mobile, active state highlighting
- [ ] 10.7 Test relative timestamps display correctly across recent and older articles
- [ ] 10.8 Test dark mode (system preference) — all new styles have dark variants
- [ ] 10.9 Test responsive breakpoints: mobile (<768px), tablet (768–1099px), desktop (1100px+)
- [x] 10.10 Run `npm run build` — verify zero JS files in dist/ output
- [ ] 10.11 Compare rendered pages against mockups in `mockups/*.html` for design fidelity
