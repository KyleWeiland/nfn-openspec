## Context

NoFrills.news is a minimal news aggregation site. The Python pipeline fetches articles from Google Alerts RSS feeds, extracts content, generates summaries, and stores them in SQLite at `data/articles.db`. The frontend needs to display this content in a clean, distraction-free interface optimized for reading.

Current state: Backend pipeline is complete. No frontend exists yet. Articles are stored in SQLite with schema: id, title, source_url, summary, category, published_date, slug, created_at.

Constraints:
- Must ship zero JavaScript to the browser (static pages only)
- GitHub Pages hosting (static files only)
- Must support dark mode via CSS media queries
- Mobile and desktop responsive
- Must be built from JSON exports, not direct database access

## Goals / Non-Goals

**Goals:**
- Provide a fast, minimal reading experience for aggregated news
- Support browsing all articles, filtering by category, and reading individual articles
- Enable local development with sample data (no live feeds required)
- Deploy to GitHub Pages with automated builds
- Ship zero client-side JavaScript

**Non-Goals:**
- Search functionality (future enhancement)
- User accounts or personalization
- Comments or social features
- Real-time updates (static site rebuilds on schedule)
- Direct database queries (use exported JSON)
- Rich media or images (text-only)

## Decisions

### 1. Astro as static site generator
**Decision**: Use Astro with static output mode.

**Rationale**: Astro excels at shipping zero JavaScript while providing component-based development. Its static output mode generates pure HTML/CSS, perfect for GitHub Pages. File-based routing reduces boilerplate.

**Alternatives considered**:
- Hugo/Jekyll: Less flexible templating, steeper learning curve
- Next.js SSG: Ships unnecessary JS framework code
- Plain HTML: Too repetitive, hard to maintain

### 2. JSON export over direct database access
**Decision**: Export articles to `data/articles.json` and `data/categories.json` at build time.

**Rationale**: Astro imports happen at build time. Exporting to JSON allows caching and versioning. Simplifies deployment (no SQLite dependency in CI). Seeding and export scripts provide development flexibility.

**Alternatives considered**:
- SQLite plugin: Adds build complexity, harder to debug
- Content collections: Designed for markdown files, not database exports
- API endpoint: Requires server, defeats static hosting

### 3. File-based pagination with catch-all routes
**Decision**: Use `[...page].astro` with Astro's `paginate()` helper.

**Rationale**: Generates static pages for all pagination states at build time. No client-side routing needed. SEO-friendly URLs like `/2`, `/3`, etc.

**Alternatives considered**:
- Client-side pagination: Requires JavaScript
- Load more button: Requires JavaScript
- No pagination: Poor UX with 100+ articles

### 4. Single global.css file for styling
**Decision**: One `src/styles/global.css` with CSS custom properties for theming.

**Rationale**: Keeps styling simple and predictable. Custom properties enable dark mode with `prefers-color-scheme`. No build step complexity. Fast loading with single CSS file.

**Alternatives considered**:
- Tailwind: Adds build complexity, verbose markup
- CSS modules: Overkill for simple site
- Styled components: Requires JavaScript

### 5. Mobile-first horizontal scroll for category nav
**Decision**: Desktop shows inline category links. Mobile uses horizontal scrollable list (no hamburger menu).

**Rationale**: Simpler implementation, no JavaScript needed. Horizontal scroll is intuitive on mobile. Avoids menu state management.

**Alternatives considered**:
- Hamburger menu: Requires JavaScript for toggle
- Dropdown: Requires JavaScript
- Stacked links: Takes too much vertical space

## Risks / Trade-offs

**Risk**: Pagination generates many static HTML files as content grows.
**Mitigation**: 20 articles per page means 100 articles = 5 pages. GitHub Pages handles this easily. Can increase per-page count if needed.

**Risk**: No client-side search limits discoverability.
**Mitigation**: Category filtering provides basic organization. Can add static search index later if needed.

**Risk**: Rebuilding entire site on every article update is slow at scale.
**Mitigation**: Acceptable for MVP. Astro builds are fast (<30s for 100s of pages). GitHub Actions cron runs once daily.

**Trade-off**: Zero JavaScript means no dynamic interactions (sorting, filtering, expand/collapse).
**Acceptance**: Aligns with "minimal" design goal. Users expect static content, not interactive features.

**Trade-off**: Horizontal scroll on mobile may not be immediately discoverable.
**Mitigation**: Category nav is visually distinct. Scroll affordance is standard mobile pattern.
