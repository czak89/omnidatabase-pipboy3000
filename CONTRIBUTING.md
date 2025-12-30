# Contributing to Omni-Database Pip-Boy 3000

Thank you for your interest in contributing to the Pip-Boy 3000 database! This document provides guidelines for contributing content, code, and translations.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Content Contributions](#content-contributions)
- [Lore Accuracy Guidelines](#lore-accuracy-guidelines)
- [JSON Structure Requirements](#json-structure-requirements)
- [Translation Requirements](#translation-requirements)
- [Code Contributions](#code-contributions)
- [Testing Checklist](#testing-checklist)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

- Be respectful and constructive
- Focus on what's best for the community and lore accuracy
- Accept feedback gracefully
- No harassment or discriminatory language

## Content Contributions

### What We Accept

✅ **Accepted Contributions:**
- New database entries (items, locations, factions, etc.)
- Corrections to existing lore
- Improved descriptions
- New categories within existing modules
- Translation improvements

❌ **Not Accepted:**
- Fan fiction or non-canon content (except in Van Buren section)
- Spoilers without proper context
- Low-quality or incomplete entries
- Duplicate content
- Content from unofficial mods (unless explicitly noted)

### Submission Process

1. **Research First**: Verify information across multiple sources
2. **Check Existing Content**: Ensure no duplicates exist
3. **Follow JSON Schema**: Match the exact structure (see below)
4. **Test Locally**: Verify your changes render correctly
5. **Submit PR**: Include sources and game references

## Lore Accuracy Guidelines

### Source Hierarchy

When conflicts arise, follow this priority order:

1. **Released Games** (Fallout 1, 2, 3, NV, 4, 76)
2. **Official DLC** (Broken Steel, Dead Money, Old World Blues, etc.)
3. **Developer Commentary** (Official interviews, design docs)
4. **Van Buren Content** (Clearly marked as cancelled/non-canon)
5. **Fallout Bible** (Use cautiously - some contradictions)

### Verification Checklist

- [ ] Information appears in official game content
- [ ] Checked at least 2 independent sources (wikis, game files)
- [ ] Noted which game(s) the content appears in
- [ ] Cross-referenced dates with established timeline
- [ ] Verified spelling of proper nouns (Vault-Tec, RobCo, etc.)

### Writing Style

- **Tone**: Technical, terminal-like, in-universe perspective
- **Tense**: Present or past tense (maintain consistency)
- **Length**: 2-4 sentences for lore descriptions
- **Format**: Plain text, no markdown in JSON
- **Case**: UPPERCASE for titles/headers, normal case for descriptions

**Example:**
```
❌ Bad: "This is a really cool weapon that shoots lasers!"
✅ Good: "RobCo Industries AER9 laser rifle. Standard issue energy weapon utilizing microfusion cells. Designed for military applications during the Sino-American War."
```

## JSON Structure Requirements

### Database File Structure

Both `database-en.json` and `database-pl.json` must maintain identical structure.

### Module Schema

```json
{
  "module_name": {
    "title": "MODULE TITLE",
    "color": "text-color-class",
    "border": "border-color-class",
    "categories": [
      {
        "id": "unique-category-id",
        "name": "CATEGORY NAME",
        "icon": "📦",
        "desc": "Category description"
      }
    ],
    "items": {
      "category-id": [
        {
          "id": "unique-item-id",
          "name": "ITEM NAME",
          "img": "https://placeholder-url",
          "specs": {
            "Spec Name": "Spec Value",
            "Another Spec": "Value"
          },
          "lore": "2-4 sentence description following lore guidelines."
        }
      ]
    }
  }
}
```

### Field Requirements

| Field | Required | Type | Guidelines |
|-------|----------|------|------------|
| `id` | ✅ Yes | string | Lowercase, kebab-case, unique per category |
| `name` | ✅ Yes | string | UPPERCASE for headers, proper case for names |
| `img` | ✅ Yes | URL string | Use placehold.co or official game assets |
| `specs` | ✅ Yes | object | 2-6 key-value pairs, relevant technical data |
| `lore` | ✅ Yes | string | 2-4 sentences, lore-accurate description |

### Naming Conventions

```json
// IDs: lowercase-with-hyphens
"id": "power-armor-t51b"

// Names: Proper case or UPPERCASE
"name": "T-51b Power Armor"
"name": "BROTHERHOOD OF STEEL"

// Categories: UPPERCASE
"name": "ENERGY WEAPONS"
```

### Image Guidelines

**Preferred sources:**
1. Official game screenshots
2. Concept art (credited)
3. Placeholder images: `https://placehold.co/400x300/111/33ff33?text=ITEM+NAME`

**Image specs:**
- Aspect ratio: 4:3 or 16:9
- Minimum resolution: 400x300px
- Format: JPEG, PNG, WebP
- Hosting: Imgur, GitHub assets, or placeholders

## Translation Requirements

### Adding/Improving Translations

When translating content:

1. **Maintain Structure**: Same JSON structure as English version
2. **Translate UI Elements**: All `title`, `name`, `desc`, and `lore` fields
3. **Keep Technical Terms**: Some terms stay in English (e.g., "Pip-Boy", "Vault-Tec")
4. **Preserve Formatting**: Keep UPPERCASE patterns where applicable
5. **Test Both Languages**: Verify language switcher works correctly

### Polish Translation Guidelines

- Proper nouns: Keep original (Vault-Tec, RobCo, Brotherhood of Steel)
- Technical specs: Translate units but keep numbers
- Lore text: Full translation with cultural adaptation where needed
- UI elements: Always translate

**Example:**
```json
// English
"name": "POWER ARMOR",
"specs": {
  "Type": "Heavy Armor",
  "Weight": "45 lbs"
},
"lore": "Advanced powered combat armor developed before the Great War."

// Polish
"name": "ZBROJA ENERGETYCZNA",
"specs": {
  "Typ": "Ciężka zbroja",
  "Waga": "20 kg"
},
"lore": "Zaawansowana zbroja bojowa opracowana przed Wielką Wojną."
```

## Code Contributions

### What We Accept

- Bug fixes
- Performance improvements
- Accessibility enhancements
- New features (discuss in issue first)
- Documentation improvements

### Code Style

**HTML:**
- Semantic HTML5 elements
- ARIA labels for accessibility
- No inline event handlers (use event delegation)

**CSS:**
- CSS custom properties for theming
- Tailwind utilities where possible
- Comments for complex sections
- Mobile-first responsive design

**JavaScript:**
- Vanilla ES6+
- No frameworks/libraries (except CDN)
- Clear function names
- Comments for complex logic
- Event delegation pattern

**Example:**
```javascript
// ❌ Don't use inline handlers
<button onclick="doThing()">Click</button>

// ✅ Use event delegation
<button data-action="do-thing" data-id="123">Click</button>

// JavaScript
document.addEventListener('click', (e) => {
  const target = e.target.closest('[data-action]');
  if (target?.dataset.action === 'do-thing') {
    doThing(target.dataset.id);
  }
});
```

## Testing Checklist

Before submitting a PR, verify:

### Visual Testing
- [ ] Tested in Chrome/Edge
- [ ] Tested in Firefox
- [ ] Tested in Safari (if available)
- [ ] Tested on mobile device or emulator
- [ ] CRT effects render correctly
- [ ] Scanline animation works
- [ ] All colors match theme

### Functional Testing
- [ ] Language switcher works (EN/PL)
- [ ] Search finds new content
- [ ] Navigation works (categories → items → details)
- [ ] Breadcrumbs display correctly
- [ ] Back buttons function properly
- [ ] Favorites can be toggled
- [ ] Empty states display when appropriate

### Accessibility Testing
- [ ] Keyboard navigation works
- [ ] Focus indicators visible
- [ ] Screen reader compatible (test with NVDA/JAWS)
- [ ] ARIA labels present
- [ ] Reduced motion respected

### Data Integrity
- [ ] Valid JSON syntax
- [ ] No duplicate IDs
- [ ] All required fields present
- [ ] Images load correctly
- [ ] Lore text accurate

### Performance
- [ ] Images use lazy loading
- [ ] No console errors
- [ ] Search is responsive
- [ ] Page loads in <3 seconds

## Pull Request Process

### 1. Fork and Branch

```bash
# Fork the repository on GitHub
git clone https://github.com/YOUR-USERNAME/omnidatabase-pipboy3000.git
cd omnidatabase-pipboy3000

# Create a feature branch
git checkout -b feature/add-vault-111
```

### 2. Make Changes

- Follow all guidelines above
- Keep commits atomic and well-described
- Test thoroughly

### 3. Commit Messages

Follow conventional commits:

```
feat: add Vault 111 to database
fix: correct T-51b armor specs
docs: update README installation steps
style: improve CRT scanline effect
refactor: optimize search indexing
```

### 4. Submit PR

**PR Title:** Clear, descriptive, follows conventional commits

**PR Description Template:**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] New content (database entries)
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Translation improvement

## Content Details (if applicable)
- Module: [TECH/VAULTS/LOCATIONS/etc.]
- Number of entries: X
- Games referenced: [Fallout 3, NV, 4, etc.]

## Sources
- [Fallout Wiki - Item Name](https://fallout.fandom.com/wiki/...)
- Game: Fallout 3, location: Vault 101

## Testing
- [ ] Tested locally
- [ ] Verified JSON syntax
- [ ] Checked lore accuracy
- [ ] Tested both languages (if applicable)

## Screenshots (if applicable)
[Add screenshots showing your changes]
```

### 5. Code Review

- Address all feedback
- Keep discussion respectful and constructive
- Be patient - reviews may take a few days

### 6. Merge

Once approved:
- Squash commits if requested
- Maintainer will merge
- Delete your feature branch

## Questions?

- **Lore Questions**: Open a discussion issue
- **Bug Reports**: Create an issue with detailed steps
- **Feature Requests**: Discuss in issues before implementing
- **General Help**: Check existing issues or open a new one

## Recognition

Contributors will be recognized in:
- GitHub contributors page
- Future CHANGELOG.md (for significant contributions)

Thank you for helping preserve Fallout lore! ☢️
