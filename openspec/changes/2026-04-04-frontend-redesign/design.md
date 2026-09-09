## Context

NoFrills.news is a static news aggregation site built with Astro. Articles are fetched via gnews, processed with Newspaper4k, stored in SQLite, exported to JSON, and built into static HTML pages deployed to GitHub Pages.

Current state: The frontend works but uses a narrow single-column layout (72ch), bordered article cards, flat chronological listing, and basic navigation pills. With 9 categories and ~60 articles today, scaling to 5,000–30,000+ articles in coming months.

The vision: "A very simple newspaper on the web" — easy to read, easy to navigate, low friction browsing. Not a dense dashboard (HN/SkimFeed), not a link dump (Brutalist Report). A composed, readable newspaper with purposeful use of space.

Constraints:
- Zero JavaScript shipped to browser (Astro static mode)
- No images, no ads — text-focused
- Must work well on mobile, tablet, and desktop (desktop is primary)
- Keep Astro as framework, article pipeline stays
- All existing URL routes must continue working
- System-preference dark mode only (no toggle)

## Goals / Non-Goals

**Goals:**
- Newspaper-inspired layout that uses horizontal space effectively
- Clear information hierarchy — not every article looks the same
- Homepage as jumping-off point: latest news + category sections
- Category pages as primary browsing workhorses at scale
- Article pages that aren't dead ends (related articles)
- Source attribution on every article ("via source.com")
- Navigation that handles 9–15 categories without breaking
- Relative timestamps for immediacy ("2h ago")

**Non-Goals:**
- Client-side search (would require JS)
- Dark mode toggle (system preference only)
- User preferences or personalization
- Multi-column article body text (keep single column for readability)
- Category reordering or priority system
- Infinite scroll or lazy loading (static pagination)

## Decisions

### 1. Wide fluid layout with 1200px max-width
**Decision**: Replace 72ch (~650px) max-width with 1200px max, 94% fluid width.

**Rationale**: The newspaper metaphor requires width to create multi-column layouts. 1200px provides room for 2–3 column grids while remaining comfortable on most monitors. Different page types use the width differently — homepage fills it with grids, article body text stays at 72ch within the wider frame.

**Alternatives considered**:
- Keep narrow layout: Wastes desktop space, can't do multi-column
- Full viewport width: Too wide, content becomes unmoored
- Adaptive fixed widths: More complex, less fluid

### 2. Homepage: Latest section + category grid
**Decision**: Homepage shows 5 latest articles prominently (lead story spans full width, rest in 2-col), followed by all categories in a 3-column grid with 2–3 headlines each.

**Rationale**: Newspapers put breaking news up top and section teasers below. This gives readers two modes: "what just happened" (Latest) and "jump to my section" (category grid). Each category section links to its full listing page.

**Alternatives considered**:
- Keep flat chronological list: No hierarchy, no entry points
- Category-only homepage: Loses "what's new" signal
- Single featured story: Not enough latest context

### 3. List items instead of bordered cards
**Decision**: Replace bordered card components with lightweight list items separated by subtle dividers (1px border-bottom).

**Rationale**: Every fast-scanning news site (HN, Brutalist Report, Readspike) uses lists, not cards. Cards add visual weight (borders, padding, shadows) that slows scanning. Dividers maintain separation while keeping the eye moving downward. Research across competitor sites confirmed this consistently.

**Alternatives considered**:
- Keep cards: Too heavy for scan-oriented reading
- No dividers at all: Items blend together, hard to distinguish
- Alternating background: Adds visual noise

### 4. Inline middot-separated nav (desktop) / 2-column grid (mobile)
**Decision**: Desktop nav uses inline text flow with CSS middot separators. Mobile uses a 2-column grid showing all categories.

**Rationale**: With 9 categories (growing to 12–15), horizontal scrolling hides items. Wrapping to 2 lines with middot separators looks intentional — like a newspaper section index. On mobile, a 2-column grid keeps all categories visible with good tap targets. No hamburger menus, no hidden navigation.

**Alternatives considered**:
- Horizontal scroll: Hides categories, bad on both mobile and desktop
- Hamburger menu: Requires JS, hides navigation
- Pills/buttons: Too much visual weight, wrap poorly

### 5. Article page: reading column + related sidebar
**Decision**: On desktop (1000px+), article pages use a 2-column layout: article body at 72ch on left, sticky "More in [Category]" sidebar on right. On mobile, related articles stack below.

**Rationale**: The wide layout creates space that would be wasted with centered-only text. Putting related articles in a sidebar makes the article page a navigation hub rather than a dead end. The reading column stays at 72ch for comfortable line lengths (typography best practice: 45–90 chars, ideal ~66).

**Alternatives considered**:
- Full-width article text: Lines too long for comfortable reading
- Related articles below only: Doesn't use desktop width, less discoverable
- No related articles: Dead-end pages hurt browsing flow

### 6. Source domain extraction in pipeline
**Decision**: Extract domain from `source_url` at export time, add `source_name` field to articles.json. Strip " - Source" suffix from titles.

**Rationale**: Frontend needs "via source.com" display. Titles from gnews already contain source suffixes (e.g., "Article Title - vocal.media") which would duplicate. Extracting domain from URL is 100% reliable. Cleaning happens once in the pipeline, not repeatedly in the frontend.

**Alternatives considered**:
- Parse domain in Astro components: Duplicates logic across components
- Keep title suffix as source name: Less reliable, harder to parse
- Don't show source: Loses credibility signal

### 7. Summary quality detection
**Decision**: Add detection for junk summaries (cookie notices, security walls, CAPTCHA text) in the processing pipeline. Flag or replace with truncated article text.

**Rationale**: Some articles return garbage summaries because Newspaper4k extracts consent dialogs or security challenge text instead of article content. These degrade the reading experience. Pattern-matching common anti-patterns (e.g., "establishing a secure connection", "privacy is important to us") can catch most cases.

**Alternatives considered**:
- Frontend-only mitigation: Shorter hooks hide bad summaries but don't fix them
- Manual curation: Doesn't scale with automated pipeline
- Discard articles entirely: Loses content that may have valid titles/metadata

## Risks / Trade-offs

**Risk**: Multi-column grids on the homepage may feel overwhelming with many categories.
**Mitigation**: Each category section shows only 2–3 headlines. 3-column grid prevents any single category from dominating. Visual breathing room via section headers and spacing.

**Risk**: 2-column article list on category pages may disrupt reading flow.
**Mitigation**: Articles are scan items, not long reads — users are scanning titles and hooks, not reading sequentially. Grid maintains consistent left-to-right, top-to-bottom flow within each column.

**Risk**: Related articles sidebar on article page takes space from content.
**Mitigation**: Sidebar only appears at 1000px+. Article body at 72ch is unchanged from best-practice reading width. Sidebar is additive space usage, not competitive.

**Risk**: Summary quality detection may produce false positives (reject valid summaries).
**Mitigation**: Use conservative pattern matching. Fall back to truncated article text rather than discarding. Log flagged summaries for review.

**Trade-off**: Relative timestamps ("2h ago") become less useful for older articles.
**Decision**: Use relative for <48h, switch to absolute date for older articles. Balances immediacy with archival clarity.

**Trade-off**: Homepage category grid shows limited headlines per category.
**Acceptance**: The homepage is a jumping-off point, not exhaustive. "View all" links funnel to full category pages which are the real browsing workhorses.
