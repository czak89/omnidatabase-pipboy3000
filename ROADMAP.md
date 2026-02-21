# Product Roadmap

This roadmap captures the next five improvements for Omni-Database Pip-Boy 3000, ordered by long-term impact and maintainability.

## 1) Modularize the App Architecture
**Objective:** Reduce risk and complexity by separating structure, styles, and behavior.

**Key tasks:**
- Split inline JavaScript and CSS from `index.html` into `src/js/` and `src/css/`.
- Keep `index.html` as a minimal shell and load modular assets.
- Separate rendering, state, search, and navigation logic into focused modules.

**Expected outcome:** Faster feature delivery, simpler debugging, and easier contributor onboarding.

## 2) Add Deep-Link Routing and State Restore
**Objective:** Make app state shareable and browser navigation predictable.

**Key tasks:**
- Encode state in URL hash/query (`tab`, `category`, `item`, `search`, `favorites`).
- Restore view state on page load.
- Handle browser Back/Forward transitions without UI desync.

**Expected outcome:** Shareable links to specific content and improved navigation UX.

## 3) Add JSON Schema Validation in CI
**Objective:** Prevent content regressions before deployment.

**Key tasks:**
- Define schema for `database-en.json` and `database-pl.json`.
- Validate required fields, field types, ID uniqueness, and EN/PL structure parity.
- Add validation step to GitHub Actions before Pages deploy.

**Expected outcome:** Fewer broken releases and higher confidence in data changes.

## 4) Upgrade Search Quality
**Objective:** Improve discovery speed and relevance across large lore content.

**Key tasks:**
- Add filters by module and category.
- Add typo-tolerant/fuzzy matching.
- Implement weighted ranking (`name > specs > lore`) and result highlighting.

**Expected outcome:** Users find correct entries faster with less trial-and-error.

## 5) Ship Offline-Ready PWA
**Objective:** Improve repeat-load performance and mobile resilience.

**Key tasks:**
- Add `manifest.webmanifest` and install metadata.
- Implement service worker with stale-while-revalidate caching for app shell and data.
- Cache core assets (`index.html`, JSON files, key images, fonts) with safe versioning.

**Expected outcome:** Installable app experience with offline browsing and faster subsequent loads.
