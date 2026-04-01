## 1. Local Development Script

- [x] 1.1 Create scripts/run_local.sh file
- [x] 1.2 Add shebang line (#!/bin/bash) at top of script
- [x] 1.3 Add status message: "Exporting articles from SQLite to JSON..."
- [x] 1.4 Add command to run python scripts/export_for_astro.py
- [x] 1.5 Add error handling: exit if export fails
- [x] 1.6 Add status message: "Starting Astro development server..."
- [x] 1.7 Add command to cd site && npm run dev
- [x] 1.8 Add error handling: exit if dev server fails to start
- [x] 1.9 Make script executable: chmod +x scripts/run_local.sh
- [x] 1.10 Test script execution on local machine

## 2. README Documentation

- [x] 2.1 Create README.md at repository root
- [x] 2.2 Write project overview section (what NoFrills.news is)
- [x] 2.3 Write architecture section with ASCII data flow diagram
- [x] 2.4 Document technology stack (Python, Node, SQLite, Astro, GitHub Actions/Pages)
- [x] 2.5 Write quick start section
- [x] 2.6 Write local development setup instructions (Python deps, Node deps, seed data)
- [x] 2.7 Document run_local.sh convenience script usage
- [x] 2.8 Write feed management section (how to add/remove feeds in feeds.config.json)
- [x] 2.9 Document feeds.config.json structure (url and category fields)
- [x] 2.10 Write CI/CD pipeline section with workflow diagram
- [x] 2.11 Document daily cron schedule (6 AM UTC)
- [x] 2.12 Document manual trigger via GitHub Actions UI
- [x] 2.13 Document skip_fetch parameter for rebuild-only runs
- [x] 2.14 Mention gh CLI option for triggering workflows
- [x] 2.15 Write detailed future enhancements section covering:
  - Content aggregation upgrade (GNews API with filtering)
  - Article processing improvements (Newspaper4k, smart dedupe, title cleanup)
  - AI-powered summaries (Claude Haiku API)
  - Frontend redesign (typography, spacing, dark mode)
  - Additional features (custom domain, search, RSS output)
- [x] 2.16 Review README for clarity and completeness

## 3. Code Review - Python Scripts

- [x] 3.1 Review scripts/fetch_articles.py for error handling
- [x] 3.2 Verify network requests have try/except blocks in fetch_articles.py
- [x] 3.3 Verify file I/O has error handling in fetch_articles.py
- [x] 3.4 Check logging: INFO for progress, ERROR for failures
- [x] 3.5 Review scripts/export_for_astro.py for error handling
- [x] 3.6 Verify file operations have try/except in export_for_astro.py
- [x] 3.7 Check export_for_astro.py logging completeness
- [x] 3.8 Review scripts/article_processing.py for error handling
- [x] 3.9 Verify trafilatura/requests calls have error handling
- [x] 3.10 Review scripts/article_fetching.py for error handling
- [x] 3.11 Verify feedparser calls have error handling
- [x] 3.12 Review scripts/database.py for error handling
- [x] 3.13 Verify SQLite operations have try/except blocks
- [x] 3.14 Review scripts/url_extraction.py for error handling
- [x] 3.15 Check all scripts for hardcoded values that should be configurable
- [x] 3.16 Verify no magic numbers (use named constants)
- [x] 3.17 Verify all file paths use os.path.join or pathlib.Path
- [x] 3.18 Verify paths work relative to repository root
- [x] 3.19 Test scripts from different working directories
- [x] 3.20 Fix any issues found during code review

## 4. Code Review - Astro Components

- [x] 4.1 Review site/src components for error handling
- [x] 4.2 Verify all components use import.meta.env.BASE_URL correctly
- [x] 4.3 Check for any hardcoded values in components
- [x] 4.4 Verify page routing works with base path
- [x] 4.5 Fix any issues found in Astro code

## 5. Gitignore Verification

- [x] 5.1 Verify .gitignore excludes node_modules/
- [x] 5.2 Verify .gitignore excludes .astro/
- [x] 5.3 Verify .gitignore excludes site/dist/
- [x] 5.4 Verify .gitignore excludes __pycache__/
- [x] 5.5 Verify .gitignore excludes *.pyc files
- [x] 5.6 Verify .gitignore excludes data/articles.json (generated)
- [x] 5.7 Verify .gitignore excludes data/categories.json (generated)
- [x] 5.8 Verify .gitignore does NOT exclude data/articles.db (version-controlled)
- [x] 5.9 Verify .gitignore excludes .env and .env.local
- [x] 5.10 Update .gitignore if any gaps found
- [x] 5.11 Run git status after build to verify no unwanted files tracked

## 6. End-to-End Testing

- [x] 6.1 Check if scripts/seed_data.py exists
- [x] 6.2 Run python scripts/seed_data.py if it exists
- [x] 6.3 Run python scripts/export_for_astro.py
- [x] 6.4 Verify data/articles.json was created/updated
- [x] 6.5 Verify data/categories.json was created/updated
- [x] 6.6 Run cd site && npm run build
- [x] 6.7 Verify site/dist directory was created
- [x] 6.8 Verify site/dist contains index.html and expected files
- [x] 6.9 Run cd site && npm run preview
- [x] 6.10 Spot-check article rendering in browser
- [x] 6.11 Test category navigation links
- [x] 6.12 Test article detail pages
- [x] 6.13 Test pagination if multiple pages exist
- [x] 6.14 Verify no console errors in browser

## 7. Final Verification

- [x] 7.1 Test ./scripts/run_local.sh works correctly
- [x] 7.2 Read through README as if you're a new contributor
- [x] 7.3 Verify all README instructions are accurate
- [x] 7.4 Check git status shows only intentional changes
- [x] 7.5 Commit all changes with comprehensive message
