# ☢️ Omni-Database Pip-Boy 3000

A retro terminal interface styled as a "Pip-Boy 3000" for exploring the Fallout universe lore database. Experience an authentic RobCo Industries terminal with CRT effects, scanlines, and phosphor green monochrome styling.

![Fallout](https://img.shields.io/badge/Fallout-Lore-33ff33?style=for-the-badge)
![License](https://img.shields.io/badge/License-Unlicense-blue?style=for-the-badge)
![HTML5](https://img.shields.io/badge/HTML5-Vanilla-orange?style=for-the-badge)

## Features

### 🎨 Visual & UX
- **Authentic CRT Effects**: Scanlines, phosphor glow, RGB color separation, terminal green (#33ff33)
- **Retro Styling**: VT323 monospace font, boot sequence animation, terminal aesthetics
- **Responsive Design**: Optimized for desktop and mobile devices
- **Dark Theme**: Near-black background (#050505) with accent colors (amber, red, blue)

### 🔍 Navigation & Search
- **Full-Text Search**: Search across all database entries with real-time results
- **Breadcrumb Navigation**: Always know where you are in the database hierarchy
- **Keyboard Shortcuts**: Fast navigation with hotkeys (see below)
- **Favorites/Bookmarks**: Save your favorite entries with localStorage persistence

### ♿ Accessibility
- **Keyboard Navigation**: Full keyboard support with arrow keys, Tab, and Enter
- **Screen Reader Compatible**: ARIA labels, semantic HTML, skip links
- **Reduced Motion Support**: Respects `prefers-reduced-motion` for animations
- **Focus Indicators**: Clear focus states for all interactive elements

### 🗂️ Database Categories
- **TECH** (Armory & Prototypes) - Power Armor, Energy Weapons, Robotics, Devices
- **TIMELINE** - Complete history from Great War (2077) to modern wasteland
- **VAULTS** - Vault-Tec experiments and facilities
- **LOCATIONS** - Atlas of the wasteland (West Coast, Mojave, East Coast)
- **BESTIARY** - Creatures and hostile entities
- **FACTIONS** - Major powers, regional governments, raiders
- **VAN BUREN** - Cancelled Fallout 3 content and lore

### 🌍 Bilingual Support
- **English** and **Polish** language options
- Complete database translations

### ⚡ Performance
- **Lazy Loading**: Images load on-demand for faster initial load
- **GPU Acceleration**: Hardware-accelerated animations for smooth performance
- **Optimized Search**: Debounced input with indexed search (300ms delay)
- **Single-Page App**: No page reloads, instant navigation

## Quick Start

### Option 1: Live Demo
Visit the live demo: [Omni-Database Pip-Boy 3000](https://your-username.github.io/omnidatabase-pipboy3000)

### Option 2: Local Development
```bash
# Clone the repository
git clone https://github.com/your-username/omnidatabase-pipboy3000.git

# Navigate to the directory
cd omnidatabase-pipboy3000

# Option A: Python 3
python -m http.server 8000

# Option B: Node.js
npx http-server

# Option C: PHP
php -S localhost:8000

# Open in browser
# Navigate to http://localhost:8000
```

### Option 3: VS Code Live Server
1. Install the "Live Server" extension
2. Open project folder in VS Code
3. Right-click [index.html](index.html) and select "Open with Live Server"

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `1-8` | Switch between tabs (STATUS, TIMELINE, TECH, etc.) |
| `/` or `Ctrl+F` | Focus search input |
| `Escape` | Go back / Clear search |
| `Arrow Keys` | Navigate grid items |
| `Enter` | Select highlighted item |
| `Tab` | Move focus between interactive elements |

## Tech Stack

- **HTML5**: Semantic markup
- **CSS3**: Custom properties, animations, media queries
- **JavaScript**: Vanilla ES6+
- **Tailwind CSS**: Utility-first styling (via CDN)
- **Google Fonts**: VT323 retro monospace terminal font
- **JSON**: Structured database files

## Project Structure

```
omnidatabase-pipboy3000/
├── index.html              # Main application (HTML + CSS + JS)
├── database-en.json        # English language database
├── database-pl.json        # Polish language database
├── CLAUDE.md               # Project instructions
├── CONTRIBUTING.md         # Contribution guidelines
├── LICENSE                 # Unlicense (public domain)
└── README.md               # This file
```

## Database Schema

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
    "categories": [
      {
        "id": "unique-id",
        "name": "CATEGORY NAME",
        "icon": "🎯",
        "desc": "Description"
      }
    ],
    "items": {
      "category-id": [
        {
          "id": "item-id",
          "name": "ITEM NAME",
          "img": "https://...",
          "specs": {
            "Key": "Value"
          },
          "lore": "Description..."
        }
      ]
    }
  }
}
```

## Lore Accuracy

This project aims for Fallout lore accuracy across all games:
- Fallout 1 & 2 (Black Isle Studios, 1997-1998)
- Fallout 3 (Bethesda, 2008)
- Fallout: New Vegas (Obsidian Entertainment, 2010)
- Fallout 4 (Bethesda, 2015)
- Van Buren (Cancelled Black Isle Fallout 3, 2003)

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Adding new database entries
- Improving translations
- Lore accuracy standards
- Code style conventions

## Security

This project implements several security best practices:
- Event delegation (no inline onclick handlers)
- Data sanitization for XSS prevention
- No external dependencies (except CDN libraries)
- Memory leak prevention (proper cleanup of intervals)

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Performance

- Lighthouse Performance: 90+
- Lighthouse Accessibility: 95+
- First Contentful Paint: <1.5s
- Time to Interactive: <2.5s

## License

This project is released under the **Unlicense** (public domain).

Anyone can freely use, modify, and distribute this code without restriction.

See [LICENSE](LICENSE) for details.

## Acknowledgments

- **Fallout Series** - Bethesda Game Studios, Obsidian Entertainment, Black Isle Studios
- **Pip-Boy Design** - Original design by Vault-Tec Industries (in-universe)
- **VT323 Font** - Peter Hull
- **Community Contributors** - All lore contributors and translators

## Disclaimer

This is a fan project and is not affiliated with Bethesda Softworks, Obsidian Entertainment, or any official Fallout property. All Fallout-related trademarks and copyrights belong to their respective owners.

---

**War. War never changes.** ☢️
