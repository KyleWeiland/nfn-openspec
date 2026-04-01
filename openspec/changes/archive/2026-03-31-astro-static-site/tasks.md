## 1. JSON Export Script

- [x] 1.1 Create `scripts/export_for_astro.py` for JSON export
- [x] 1.2 Implement articles.json export with all required fields
- [x] 1.3 Implement categories.json export with alphabetical sorting
- [x] 1.4 Add date ordering (newest first) to articles export
- [x] 1.5 Test export script with existing database

## 2. Astro Project Initialization

- [x] 2.1 Create `site/` directory at repository root
- [x] 2.2 Initialize Astro project with `npm create astro@latest`
- [x] 2.3 Configure astro.config.mjs for static output mode
- [x] 2.4 Set GitHub Pages base path placeholder in config
- [x] 2.5 Update package.json with Node 20+ requirement
- [x] 2.6 Verify build, dev, and preview scripts in package.json
- [x] 2.7 Create .gitignore for node_modules and dist/

## 3. Project Structure and Base Layout

- [x] 3.1 Create directory structure: src/layouts, src/components, src/pages, src/styles
- [x] 3.2 Create `src/layouts/BaseLayout.astro` with HTML5 boilerplate
- [x] 3.3 Add meta tags (charset, viewport) to BaseLayout
- [x] 3.4 Implement dynamic page title in BaseLayout
- [x] 3.5 Add Navbar component slot in BaseLayout
- [x] 3.6 Add footer with site information in BaseLayout
- [x] 3.7 Import global.css in BaseLayout

## 4. Global Styling

- [x] 4.1 Create `src/styles/global.css`
- [x] 4.2 Define CSS custom properties for colors (light and dark modes)
- [x] 4.3 Define CSS custom properties for spacing and typography
- [x] 4.4 Implement prefers-color-scheme media query for dark mode
- [x] 4.5 Set base typography with system font stack
- [x] 4.6 Configure readable line height (1.5+) for body text
- [x] 4.7 Style heading hierarchy (h1-h6)
- [x] 4.8 Implement mobile-first base styles
- [x] 4.9 Add responsive breakpoints for tablet and desktop
- [x] 4.10 Set max-width for readable line lengths (65-75ch)
- [x] 4.11 Style links with clear differentiation
- [x] 4.12 Ensure WCAG AA contrast ratios for all text

## 5. Navigation Component

- [x] 5.1 Create `src/components/Navbar.astro`
- [x] 5.2 Add site name "NoFrills.news" with link to home
- [x] 5.3 Add tagline below site name
- [x] 5.4 Import categories.json for dynamic category links
- [x] 5.5 Render category links with proper URLs
- [x] 5.6 Implement mobile styles with horizontal scroll
- [x] 5.7 Implement desktop styles with inline layout
- [x] 5.8 Style category links with hover states

## 6. Article Card Component

- [x] 6.1 Create `src/components/ArticleCard.astro`
- [x] 6.2 Accept article object as prop
- [x] 6.3 Display article title as link to /article/{slug}
- [x] 6.4 Display category badge with distinct styling
- [x] 6.5 Format and display published_date
- [x] 6.6 Display first 150 characters of summary
- [x] 6.7 Style card layout with spacing and borders
- [x] 6.8 Add hover states for card interaction

## 7. Pagination Component

- [x] 7.1 Create `src/components/Pagination.astro`
- [x] 7.2 Accept page prop from Astro's paginate()
- [x] 7.3 Render "Previous" link when not on first page
- [x] 7.4 Render "Next" link when not on last page
- [x] 7.5 Display current page number
- [x] 7.6 Render page number links for nearby pages
- [x] 7.7 Style current page as visually distinct
- [x] 7.8 Style pagination controls with proper spacing

## 8. Home Page with Pagination

- [x] 8.1 Create `src/pages/[...page].astro` for home route
- [x] 8.2 Import articles.json
- [x] 8.3 Implement getStaticPaths with paginate() for all articles
- [x] 8.4 Set page size to 20 articles
- [x] 8.5 Sort articles by published_date descending
- [x] 8.6 Render ArticleCard for each article
- [x] 8.7 Add Pagination component
- [x] 8.8 Test home page with sample data

## 9. Category Filtered Pages

- [x] 9.1 Create `src/pages/category/[category]/[...page].astro`
- [x] 9.2 Import articles.json and categories.json
- [x] 9.3 Implement getStaticPaths for all category pages
- [x] 9.4 Filter articles by category parameter
- [x] 9.5 Implement pagination with paginate() for filtered articles
- [x] 9.6 Handle category name case-insensitively
- [x] 9.7 Render ArticleCard for each filtered article
- [x] 9.8 Add Pagination component
- [x] 9.9 Add category page heading
- [x] 9.10 Test category pages with multiple categories

## 10. Individual Article Pages

- [x] 10.1 Create `src/pages/article/[slug].astro`
- [x] 10.2 Import articles.json
- [x] 10.3 Implement getStaticPaths for all article slugs
- [x] 10.4 Find article by slug parameter
- [x] 10.5 Display full article title
- [x] 10.6 Display category badge
- [x] 10.7 Display formatted published_date
- [x] 10.8 Display complete summary text
- [x] 10.9 Add "Read Original Article" button linking to source_url
- [x] 10.10 Set link target to "_blank" with rel="noopener"
- [x] 10.11 Add back link to home page
- [x] 10.12 Style article page layout for readability

## 11. 404 Page

- [x] 11.1 Create `src/pages/404.astro`
- [x] 11.2 Add "Page Not Found" message
- [x] 11.3 Add link to return to home page
- [x] 11.4 Style 404 page consistently with site

## 12. Category Badge Styling

- [x] 12.1 Define distinct muted colors for each category in global.css
- [x] 12.2 Implement category color mapping logic
- [x] 12.3 Style badges with padding, border-radius, and subtle backgrounds
- [x] 12.4 Ensure category colors work in both light and dark modes

## 13. Build and Testing

- [x] 13.1 Run export_for_astro.py to generate JSON files from existing database
- [x] 13.2 Test dev server with `npm run dev`
- [x] 13.3 Verify home page displays articles with pagination
- [x] 13.4 Verify category pages filter correctly
- [x] 13.5 Verify individual article pages display full content
- [x] 13.6 Test navigation links work correctly
- [x] 13.7 Test pagination navigation on multi-page results
- [x] 13.8 Test responsive design on mobile viewport
- [x] 13.9 Test dark mode toggle via browser devtools
- [x] 13.10 Build production site with `npm run build`
- [x] 13.11 Verify no JavaScript files in dist/ output
- [x] 13.12 Preview built site with `npm run preview`
- [x] 13.13 Verify all pages render correctly in production build
