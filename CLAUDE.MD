# Omni-Database Pip-Boy 3000 Project

## Project Overview

This is a Fallout-themed retro terminal interface styled as a "Pip-Boy 3000" that displays a comprehensive database of Fallout universe lore. The application mimics a RobCo Industries terminal with authentic CRT effects, scanlines, and green monochrome styling.

## Tech Stack

- **Frontend**: Vanilla HTML, CSS, JavaScript
- **Styling**: Tailwind CSS (via CDN)
- **Fonts**: VT323 (Google Fonts) - authentic retro monospace terminal font
- **Data Storage**: JSON files (database-en.json, database-pl.json)
- **Deployment**: GitHub Pages

## File Structure

```
/
├── index.html           # Main application file
├── database-en.json     # English language database
├── database-pl.json     # Polish language database
├── LICENSE              # Unlicense (public domain)
└── .github/
    └── workflows/       # GitHub Actions for deployment
```

## Design Philosophy

### Visual Style
- **Terminal Green**: Primary color (#33ff33)
- **Dark Background**: Near-black (#050505)
- **Accent Colors**: Amber (#ffb000), Red (#ff3333), Blue (#33bbff)
- **CRT Effects**: Scanlines, RGB color separation, phosphor glow
- **Retro Aesthetics**: VT323 monospace font, boot sequence, terminal styling

### Content Categories
1. **TECH** (Armory & Prototypes) - Amber themed
   - Power Armor, Energy Weapons, Robotics, Devices
2. **TIMELINE** (History) - Blue themed
3. **VAULTS** - Green themed
4. **LOCATIONS** (Atlas) - Location database
5. **BESTIARY** - Creature database
6. **FACTIONS** - Faction information
7. **VAN BUREN** - Cancelled Fallout 3 content
8. **STATUS** - System status screen

## Code Conventions

### HTML Structure
- Semantic HTML5 elements
- Polish language (`lang="pl"`) as default
- Responsive viewport meta tag
- Single-page application structure

### CSS Practices
- CSS custom properties for theming (--term-green, --term-amber, etc.)
- Tailwind utility classes for layout
- Custom styles for CRT effects and animations
- VT323 font family throughout
- Component-based class naming (.pip-btn, .content-box, .crt-overlay)

### JavaScript Patterns
- Vanilla JavaScript (no frameworks)
- Data-driven rendering from JSON
- Module system with categories
- Language switching between EN/PL
- Boot sequence animation
- Dynamic content loading

### JSON Data Structure
```json
{
  "ui": {
    "title": "...",
    "nav": {...},
    "status_msg": "..."
  },
  "tech": {
    "title": "...",
    "color": "text-amber-300",
    "border": "border-amber-300",
    "categories": [...],
    "items": {...}
  }
}
```

## Development Guidelines

### When Adding New Content

1. **Maintain Consistency**
   - Use appropriate terminal-style language
   - Keep descriptions concise and lore-accurate
   - Follow existing color theming per category

2. **Data Updates**
   - Always update BOTH database-en.json AND database-pl.json
   - Maintain consistent structure across both language files
   - Use placeholder images with appropriate text

3. **Visual Elements**
   - Preserve CRT aesthetic (scanlines, phosphor glow, green tint)
   - Use appropriate color for each module (amber for tech, blue for timeline, etc.)
   - Maintain consistent button styling (.pip-btn class)

4. **Animations**
   - Keep animations subtle and period-appropriate
   - Maintain scanline animation speed (4s linear)
   - Use appropriate hover effects (glow, color inversion)

### Code Style
- Use 4-space indentation
- Keep JavaScript functions focused and modular
- Comment complex sections
- Maintain semantic HTML structure
- Use Tailwind utilities where possible, custom CSS when needed

### Performance Considerations
- All styles and scripts inline in index.html
- External resources loaded via CDN
- JSON data files kept reasonably sized
- Minimal JavaScript for fast loading

## Lore Accuracy

This project aims for Fallout lore accuracy across all games:
- Fallout 1 & 2 (Black Isle)
- Fallout 3 & 4 (Bethesda)
- Fallout: New Vegas (Obsidian)
- Van Buren (cancelled Black Isle Fallout 3)

When adding content:
- Verify information against multiple sources
- Note which game(s) content appears in
- Respect established canon
- Clearly mark Van Buren content as cancelled/non-canon

## Testing Checklist

Before committing changes:
- [ ] Test in multiple browsers (Chrome, Firefox, Safari)
- [ ] Verify CRT effects render correctly
- [ ] Test language switching (EN/PL)
- [ ] Verify all navigation buttons work
- [ ] Check mobile responsiveness
- [ ] Validate JSON syntax
- [ ] Test boot sequence animation
- [ ] Verify all data displays correctly

## Deployment

The site deploys automatically via GitHub Pages when changes are pushed to the main branch. The GitHub Actions workflow handles the deployment process.

## License

This project is released under the Unlicense (public domain). Anyone can freely use, modify, and distribute this code without restriction.

## Theme & Atmosphere

Maintain the authentic Pip-Boy terminal feel:
- All text in UPPERCASE for headers
- Terminal-style loading messages
- Boot sequence authenticity
- RobCo Industries branding
- Year 2077 timeline context
- Post-apocalyptic wasteland aesthetic
