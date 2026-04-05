## Why

NoFrills.news has a functional but basic frontend — flat chronological lists, bordered cards, narrow single-column layout, and no visual hierarchy between articles. As the site scales from ~60 articles to 5,000–30,000+, the current design won't support efficient browsing, category exploration, or comfortable reading at scale.

The article pipeline is solid (gnews + Newspaper4k → SQLite → JSON → Astro). Now the frontend needs to match — an ultra-performant, newspaper-inspired reading experience that makes it easy to scan, navigate, and read across categories and thousands of articles.

## What Changes

### Frontend (Astro site)
- Widen page layout from 72ch to 1200px max-width with fluid responsive breakpoints
- Redesign homepage as a newspaper front page: "Latest" section (lead story + 2-col grid) followed by 3-column category section grid
- Convert article list items from bordered cards to lightweight divider-separated list items
- Redesign category pages with 2-column article grid on desktop
- Redesign article detail page with reading column (72ch) + sticky related-articles sidebar
- Replace category pill navigation with inline middot-separated section nav (desktop) / 2-column grid (mobile)
- Add relative timestamps ("2h ago", "1d ago") instead of absolute dates
- Add source domain display ("via source.com") on all article references
- Implement stronger typographic hierarchy: lead stories larger, compact items tighter
- Back navigation from article page goes to category, not home
- Add "More in [Category]" related articles on article pages
- Update all CSS: new custom properties, responsive grid layouts, section headers with rules

### Pipeline (prerequisites for frontend)
- Extract `source_name` from `source_url` domain in export script, add to JSON schema
- Strip " - Source" suffix from article titles in export to avoid duplication with source display
- Add summary quality detection to filter junk summaries (cookie notices, security walls, paywalls)

## Capabilities

### Modified Capabilities
- `minimal-styling`: Wide layout, newspaper typography, section rules, list-based items, responsive grids
- `site-components`: New component architecture — ArticleLatest, ArticleCompact, ArticleItem, SectionHeader, RelatedArticles; reworked Navbar, Pagination
- `page-routing`: Homepage restructured (latest + category grid), category pages with 2-col grid, article pages with sidebar layout
- `json-export`: Add `source_name` field, clean title suffixes

### New Capabilities
- `source-extraction`: Extract and clean source domain names from article URLs
- `summary-quality`: Detect and handle junk summaries from failed article extraction

## Impact

- All files in `site/src/` modified (components, pages, layouts, styles)
- `scripts/export_for_astro.py` modified (source extraction, title cleaning)
- `scripts/article_processing.py` modified (summary quality detection)
- `data/articles.json` schema gains `source_name` field
- Visual mockups at `mockups/*.html` serve as reference
- No new dependencies required
- Zero JS to browser maintained
- All existing routes preserved (no breaking URL changes)
