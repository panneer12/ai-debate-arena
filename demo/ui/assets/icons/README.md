# Agent Icons

This directory is reserved for agent avatar icons/images.

## Icon Specifications

- **Format**: SVG or PNG
- **Size**: 64x64 pixels (or vector for SVG)
- **Style**: Minimalist, monochrome or simple color
- **Naming**: `{agent-id}.svg` or `{agent-id}.png`

## Example Icons Needed

- `moderator.svg` - 🎯 Gavel or scales
- `conservative.svg` - 🔴 Elephant or shield
- `progressive.svg` - 🔵 Raised fist or star
- `factchecker.svg` - ✅ Magnifying glass or checkmark
- `devilsadvocate.svg` - 😈 Question mark or devil icon
- `synthesizer.svg` - 🧠 Brain or light bulb
- `libertarian.svg` - 🟡 Liberty torch or porcupine
- `international.svg` - 🌍 Globe or world map

## Current Implementation

The UI currently uses emoji as placeholders. To add custom icons:

1. Add icon file to this directory
2. Update `createMessageCard()` in `js/debate.js`:

```javascript
// Replace emoji with img tag
<div class="agent-avatar">
    <img src="assets/icons/${agent}.svg" alt="${agent}">
</div>
```

3. Add CSS styling in `styles/components.css`:

```css
.agent-avatar img {
    width: 100%;
    height: 100%;
    object-fit: contain;
}
```

## Free Icon Resources

- [Font Awesome](https://fontawesome.com/)
- [Heroicons](https://heroicons.com/)
- [Feather Icons](https://feathericons.com/)
- [Material Icons](https://fonts.google.com/icons)
- [Iconify](https://iconify.design/)

## License

Ensure any icons used are properly licensed for this project.
