# Repository Guidelines

## Project Structure & Module Organization
This is a static web app. Core logic, styling, and markup live in `index.html`.
Content data is stored in `database-en.json` and `database-pl.json` (plus `_updated` variants used during edits/migrations).
Image assets live in `img/`. Deployment automation is in `.github/workflows/deploy-to-github-pages.yml`.
Keep content and UI changes separate when possible: UI behavior in `index.html`, lore/content in JSON files.

## Build, Test, and Development Commands
No build step is required. Run a local static server from the repository root:
- `python -m http.server 8000` - serve locally on port 8000.
- `npx http-server` - alternative Node-based static server.
- `php -S localhost:8000` - alternative PHP static server.
Open `http://localhost:8000` and validate both EN/PL datasets and key flows.

## Coding Style & Naming Conventions
Use semantic HTML, accessible attributes (ARIA where needed), and vanilla ES6+ JavaScript.
Prefer event delegation and `data-*` actions over inline handlers.
Use 2-space indentation in HTML/CSS/JS blocks in `index.html`.
For JSON content:
- keep valid JSON (double quotes, no trailing commas),
- use lowercase kebab-case IDs (example: `power-armor-t51b`),
- keep structure aligned between English and Polish files.

## Testing Guidelines
There is no automated test suite currently; use manual validation before PRs:
- JSON parses cleanly and has no duplicate IDs.
- Navigation, search, breadcrumbs, favorites, and language switcher work.
- Keyboard navigation and focus visibility remain intact.
- New/changed images load and do not break layout on mobile.

## Commit & Pull Request Guidelines
History includes mixed commit styles, but contributors should use Conventional Commit prefixes:
`feat:`, `fix:`, `docs:`, `style:`, `refactor:`.
Keep commits small and atomic (separate data-only and UI-only changes).
PRs should include:
- a short change summary,
- affected modules/files,
- testing notes,
- screenshots/GIFs for UI changes,
- lore sources when content is added or corrected.

## Deployment Notes
GitHub Pages deploys automatically on pushes to `main` via `.github/workflows/deploy-to-github-pages.yml`.
Ensure `index.html`, JSON files, and `img/` assets are production-ready before merging.
