# Theme Toggle - Quick Start Guide

## 🚀 Getting Started in 30 Seconds

The theme toggle is already fully implemented and ready to use!

### User Perspective

1. **Click the sun/moon button** in the top-right corner
2. **Use keyboard:** Tab to focus, Space or Enter to toggle
3. **Theme persists** across page reloads

### Developer Perspective

```javascript
// Get current theme (multiple ways)
const theme = getCurrentTheme(); // Returns: 'light' or 'dark'
const theme = document.documentElement.dataset.theme; // Modern approach
const theme = document.documentElement.getAttribute('data-theme'); // Alternative

// Change theme programmatically
toggleTheme(); // Switches to opposite theme

// Apply specific theme
applyTheme('light', true);  // With animation
applyTheme('dark', false);  // Without animation

// Listen to theme changes
window.addEventListener('themeChanged', (event) => {
    console.log('New theme:', event.detail.theme);
    console.log('Previous theme:', event.detail.previousTheme);
});
```

---

## 🎨 Using Theme Colors in Your CSS

All theme colors are available as CSS variables:

```css
.my-element {
    background-color: var(--background);
    color: var(--text-primary);
    border: 1px solid var(--border-color);
}

.my-element:hover {
    background-color: var(--surface-hover);
    color: var(--primary-color);
}
```

### Available CSS Variables

```css
--primary-color       /* Brand color (blue) */
--primary-hover       /* Darker blue for hover */
--background          /* Main background */
--surface             /* Card/panel backgrounds */
--surface-hover       /* Hover state for surfaces */
--text-primary        /* Primary text color */
--text-secondary      /* Muted text color */
--border-color        /* Border and divider color */
--shadow              /* Box shadow value */
--focus-ring          /* Focus indicator color */
```

---

## 🔄 Adding Smooth Transitions

Simply add a transition property to your elements:

```css
.my-element {
    transition: background-color 0.3s ease,
                color 0.3s ease,
                border-color 0.3s ease;
}
```

The transition duration matches the theme toggle (300ms) for consistency.

---

## 🎯 Theme-Specific Styles

Target specific themes using the `data-theme` attribute (modern approach):

```css
/* Light theme only */
:root[data-theme="light"] .my-element {
    background: #ffffff;
    color: #0f172a;
}

/* Dark theme only */
:root[data-theme="dark"] .my-element {
    background: #1e293b;
    color: #f1f5f9;
}

/* Backwards compatible (supports both methods) */
:root[data-theme="light"],
:root.light-theme .my-element {
    /* Light theme styles */
}
```

### Why data-theme?

✅ **Semantic HTML5** - Follows data-* attribute standards
✅ **Better Readability** - Clear intent: `data-theme="light"`
✅ **Easy Querying** - `document.documentElement.dataset.theme`
✅ **Future-Proof** - Can easily add more themes (e.g., "high-contrast")

---

## ♿ Accessibility

Everything is handled automatically:

✅ ARIA labels update dynamically
✅ Keyboard navigation works out of the box
✅ Focus indicators are visible
✅ Respects `prefers-reduced-motion`
✅ High contrast ratios (WCAG AA/AAA)

---

## 📊 Analytics Integration

Track theme changes for analytics:

```javascript
window.addEventListener('themeChanged', (event) => {
    // Google Analytics
    gtag('event', 'theme_toggle', {
        theme: event.detail.theme
    });

    // Or any other analytics service
    analytics.track('Theme Changed', {
        theme: event.detail.theme
    });
});
```

---

## 🧪 Testing Your Theme Support

### Quick Test Checklist

```javascript
// 1. Toggle theme
toggleTheme();

// 2. Check it changed
console.log(getCurrentTheme()); // Should show new theme

// 3. Reload page
location.reload();

// 4. Check it persisted
console.log(getCurrentTheme()); // Should still show new theme
```

### Visual Check

1. Toggle to light theme
2. Check all your custom elements look good
3. Toggle to dark theme
4. Check again
5. Verify smooth transitions

---

## 📝 Common Use Cases

### 1. Update Component on Theme Change

```javascript
window.addEventListener('themeChanged', (event) => {
    myComponent.updateColors(event.detail.theme);
});
```

### 2. Initialize External Library with Current Theme

```javascript
const currentTheme = getCurrentTheme();
externalLibrary.init({
    theme: currentTheme,
    colors: currentTheme === 'light' ? lightColors : darkColors
});
```

### 3. Show Theme-Specific Content

```javascript
const theme = getCurrentTheme();
const isDark = theme === 'dark';

document.getElementById('theme-message').textContent =
    isDark ? 'You are in dark mode' : 'You are in light mode';
```

---

## 🐛 Troubleshooting

### Theme Doesn't Persist

**Check:** Is localStorage enabled?
```javascript
try {
    localStorage.setItem('test', 'test');
    localStorage.removeItem('test');
    console.log('localStorage is working');
} catch (e) {
    console.error('localStorage is disabled:', e);
}
```

### Colors Don't Update

**Check:** Are you using CSS variables?
```css
/* ❌ Don't do this */
.my-element {
    background: #ffffff;
}

/* ✅ Do this */
.my-element {
    background: var(--background);
}
```

### Transitions Not Smooth

**Check:** Reduced motion preference
```javascript
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
console.log('Reduced motion:', reducedMotion);
```

---

## 📚 More Information

- **Full Implementation Details:** See `javascript-theme-implementation.md`
- **Accessibility Report:** See `light-theme-accessibility-report.md`
- **Complete Feature Guide:** See `frontend-changes.md`

---

## 💡 Pro Tips

1. **Always use CSS variables** for colors to ensure theme compatibility
2. **Add transitions** to your custom elements for smooth theme switches
3. **Test both themes** during development
4. **Use the event system** to keep external components in sync
5. **Respect reduced motion** - transitions will automatically disable

---

## ✨ That's It!

The theme system is designed to be **simple to use** and **powerful to extend**. Start building theme-aware components and enjoy the smooth transitions! 🎉

**Questions?** Check the detailed documentation files for comprehensive guides.
