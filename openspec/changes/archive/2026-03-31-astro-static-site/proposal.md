## Why

The NoFrills.news project needs a minimal, fast static frontend to display aggregated news articles. The backend Python pipeline is complete and storing articles in SQLite, but there's no way for users to browse and read the content. A text-focused Astro site provides a clean reading experience with zero client-side JavaScript and GitHub Pages deployment.

## What Changes

- Create Astro static site in `site/` directory with static output mode
- Implement home page with paginated article listings (20 per page)
- Add category-filtered pages with pagination
- Build individual article detail pages
- Create reusable components (ArticleCard, Navbar, Pagination)
- Design minimal, utilitarian styling with dark mode support
- Add JSON export script to transform SQLite data for Astro consumption
- Configure for GitHub Pages deployment

## Capabilities

### New Capabilities
- `astro-project-setup`: Astro project initialization, dependencies, and static output configuration
- `json-export`: Export articles and categories from SQLite to JSON files for Astro
- `page-routing`: Home, category, and article page implementations with pagination
- `site-components`: Reusable Astro components for article cards, navigation, and pagination
- `minimal-styling`: CSS design system with custom properties, dark mode, and mobile-first responsive layout

### Modified Capabilities
<!-- No existing capabilities are being modified -->

## Impact

- New directory: `site/` containing complete Astro project
- New script: `scripts/export_for_astro.py`
- New data files: `data/articles.json` and `data/categories.json` (build-time exports)
- Dependencies: Node.js 20+, Astro, and related npm packages
- GitHub Pages deployment requires repository configuration
- Frontend consumes real articles from existing SQLite database
