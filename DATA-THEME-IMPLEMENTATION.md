# data-theme Attribute Implementation Guide

## Overview

The theme system now uses the **`data-theme` HTML attribute** as the primary method for theme management, following modern web development standards while maintaining backwards compatibility with class-based approaches.

## What Changed

### Before (Class-based)
```html
<html class="light-theme">
```
```javascript
element.classList.contains('light-theme')
```
```css
:root.light-theme { }
```

### After (data-theme Attribute)
```html
<html data-theme="light" class="light-theme">
```
```javascript
element.dataset.theme // 'light'
```
```css
:root[data-theme="light"],
:root.light-theme { }
```

## Implementation Details

### JavaScript Changes

**Setting Theme:**
```javascript
function applyTheme(theme, animate = true) {
    const root = document.documentElement;

    // Primary method: data-theme attribute
    root.setAttribute('data-theme', theme);

    // Backwards compatibility: class
    if (theme === 'light') {
        root.classList.add('light-theme');
    } else {
        root.classList.remove('light-theme');
    }
}
```

**Getting Theme:**
```javascript
function getCurrentTheme() {
    const root = document.documentElement;

    // Check data-theme attribute first
    return root.getAttribute('data-theme') ||
           // Fallback to class-based check
           (root.classList.contains('light-theme') ? 'light' : 'dark');
}
```

### CSS Changes

**All theme-specific selectors now support both methods:**

```css
/* Light theme variables */
:root[data-theme="light"],
:root.light-theme {
    --background: #f8fafc;
    --text-primary: #0f172a;
    /* ... */
}

/* Dark theme (explicit) */
:root[data-theme="dark"] {
    /* Dark theme vars */
}

/* Component-specific overrides */
:root[data-theme="light"] .my-component,
.light-theme .my-component {
    background: var(--surface);
}
```

## Benefits of data-theme Attribute

### 1. Semantic HTML

✅ **Purpose-Built:** Data attributes are specifically designed for custom data
✅ **Self-Documenting:** `data-theme="light"` clearly describes its purpose
✅ **HTML5 Standard:** Follows official HTML5 data-* attribute specification

### 2. Better JavaScript API

```javascript
// Modern way (clean, simple)
const theme = document.documentElement.dataset.theme;
document.documentElement.dataset.theme = 'light';

// vs. Class-based (more verbose)
const theme = element.classList.contains('light-theme') ? 'light' : 'dark';
element.classList.add('light-theme');
```

### 3. Clearer CSS Selectors

```css
/* Clear intent - checking a theme value */
:root[data-theme="light"] { }

/* vs. Class-based - less obvious */
:root.light-theme { }
```

### 4. Extensibility

Easy to add multiple themes:

```html
<html data-theme="light">
<html data-theme="dark">
<html data-theme="high-contrast">
<html data-theme="colorblind">
<html data-theme="custom-brand">
```

```css
:root[data-theme="high-contrast"] {
    --background: #000000;
    --text-primary: #ffffff;
    /* Maximum contrast */
}
```

### 5. Framework Compatibility

Works seamlessly with modern frameworks:

**React:**
```jsx
useEffect(() => {
    document.documentElement.dataset.theme = theme;
}, [theme]);
```

**Vue:**
```javascript
watch(theme, (newTheme) => {
    document.documentElement.dataset.theme = newTheme;
});
```

**Svelte:**
```javascript
$: document.documentElement.dataset.theme = $theme;
```

### 6. Better Developer Experience

```javascript
// Query current theme
const currentTheme = document.documentElement.dataset.theme;

// Easy conditionals
if (document.documentElement.dataset.theme === 'light') {
    // Do something in light mode
}

// Observe changes with MutationObserver
const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        if (mutation.attributeName === 'data-theme') {
            console.log('Theme changed to:', mutation.target.dataset.theme);
        }
    });
});
```

## Backwards Compatibility

### Dual Selector Pattern

All CSS rules use **both selectors** to ensure compatibility:

```css
/* Modern browsers with data-theme */
:root[data-theme="light"] .component,
/* Legacy support for class-based */
:root.light-theme .component {
    /* Styles apply with either method */
}
```

### JavaScript Compatibility

The `getCurrentTheme()` function checks **both** sources:

```javascript
function getCurrentTheme() {
    // 1. Try data-theme attribute (modern)
    const dataTheme = document.documentElement.getAttribute('data-theme');
    if (dataTheme) return dataTheme;

    // 2. Fall back to class-based check (legacy)
    return document.documentElement.classList.contains('light-theme')
        ? 'light'
        : 'dark';
}
```

### Migration Path

**Phase 1 (Current):** Both methods active
- data-theme attribute set
- Classes still maintained
- All selectors support both

**Phase 2 (Future):** Can remove class-based approach
- Simply remove class manipulation from JavaScript
- Remove class selectors from CSS
- Keep only data-theme selectors

## Usage Examples

### Reading Theme in JavaScript

```javascript
// Method 1: Direct attribute access (Recommended)
const theme = document.documentElement.dataset.theme;
// or
const theme = document.documentElement.getAttribute('data-theme');

// Method 2: Helper function (checks both sources)
const theme = getCurrentTheme();

// Method 3: From localStorage
const theme = localStorage.getItem('theme');
```

### Setting Theme in JavaScript

```javascript
// Use the applyTheme function (handles both attribute and class)
applyTheme('light', true);

// Or manually set both (not recommended - use applyTheme)
document.documentElement.dataset.theme = 'light';
document.documentElement.classList.add('light-theme');
```

### Targeting Theme in CSS

```css
/* Recommended: Support both methods */
:root[data-theme="light"] .my-component,
:root.light-theme .my-component {
    background: white;
}

/* Modern only (if backwards compatibility not needed) */
:root[data-theme="light"] .my-component {
    background: white;
}

/* Multiple themes */
:root[data-theme="light"] .btn { background: white; }
:root[data-theme="dark"] .btn { background: black; }
:root[data-theme="high-contrast"] .btn {
    background: black;
    border: 3px solid white;
}
```

### React Hook Example

```javascript
import { useEffect, useState } from 'react';

function useTheme() {
    const [theme, setTheme] = useState(
        document.documentElement.dataset.theme || 'dark'
    );

    useEffect(() => {
        // Update attribute when theme changes
        document.documentElement.dataset.theme = theme;

        // Maintain class for backwards compatibility
        if (theme === 'light') {
            document.documentElement.classList.add('light-theme');
        } else {
            document.documentElement.classList.remove('light-theme');
        }

        // Save to localStorage
        localStorage.setItem('theme', theme);
    }, [theme]);

    const toggleTheme = () => {
        setTheme(prev => prev === 'light' ? 'dark' : 'light');
    };

    return [theme, toggleTheme];
}

// Usage
function App() {
    const [theme, toggleTheme] = useTheme();

    return (
        <button onClick={toggleTheme}>
            Current theme: {theme}
        </button>
    );
}
```

## Testing

### Verify data-theme Attribute

```javascript
// In browser console
console.log(document.documentElement.dataset.theme); // 'light' or 'dark'
console.log(document.documentElement.getAttribute('data-theme')); // 'light' or 'dark'

// Toggle and verify
toggleTheme();
console.log(document.documentElement.dataset.theme); // Should show new theme
```

### Verify CSS Application

```javascript
// Check computed styles
const root = document.documentElement;
const styles = getComputedStyle(root);
console.log(styles.getPropertyValue('--background')); // Should change with theme
```

### Verify Backwards Compatibility

```javascript
// Both should return same result
console.log(document.documentElement.dataset.theme);
console.log(document.documentElement.classList.contains('light-theme') ? 'light' : 'dark');
```

## Performance Considerations

### Why data-theme is Efficient

1. **Single Attribute Change:** One setAttribute() call updates theme
2. **CSS Cascade:** Browser handles all style updates automatically
3. **No JavaScript Style Manipulation:** No need to update individual element styles
4. **GPU Acceleration:** CSS transitions can be GPU-accelerated
5. **Minimal DOM Mutations:** Only the root element's attribute changes

### Benchmark Comparison

```javascript
// Class-based approach
console.time('class-based');
document.documentElement.classList.add('light-theme');
console.timeEnd('class-based');

// data-theme approach
console.time('data-theme');
document.documentElement.dataset.theme = 'light';
console.timeEnd('data-theme');

// Result: Both are equally fast (< 1ms typically)
// Performance is identical, so use the more semantic approach!
```

## Future Enhancements

With data-theme, these become trivial to implement:

### Multiple Theme Support

```javascript
const themes = ['light', 'dark', 'high-contrast', 'sepia'];
let currentIndex = 0;

function cycleTheme() {
    currentIndex = (currentIndex + 1) % themes.length;
    document.documentElement.dataset.theme = themes[currentIndex];
}
```

### System Theme Detection

```javascript
function detectSystemTheme() {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const prefersLight = window.matchMedia('(prefers-color-scheme: light)').matches;
    const prefersContrast = window.matchMedia('(prefers-contrast: more)').matches;

    if (prefersContrast) return 'high-contrast';
    if (prefersDark) return 'dark';
    if (prefersLight) return 'light';
    return 'dark'; // default
}

document.documentElement.dataset.theme = detectSystemTheme();
```

### Theme Scheduling

```javascript
function scheduleTheme() {
    const hour = new Date().getHours();

    if (hour >= 6 && hour < 18) {
        document.documentElement.dataset.theme = 'light';
    } else {
        document.documentElement.dataset.theme = 'dark';
    }
}
```

## Best Practices

### ✅ DO

- Use `data-theme` attribute as primary theme indicator
- Maintain class-based approach during transition period
- Use CSS custom properties for all theme colors
- Support both selectors in CSS for compatibility
- Use helper functions that check both sources

### ❌ DON'T

- Don't rely solely on classes for new code
- Don't forget to update localStorage
- Don't manipulate individual element styles
- Don't skip backwards compatibility selectors (yet)
- Don't use hardcoded colors instead of variables

## Migration Checklist

- [x] JavaScript sets data-theme attribute
- [x] JavaScript maintains class for backwards compatibility
- [x] getCurrentTheme() checks data-theme first
- [x] All CSS selectors include data-theme version
- [x] All CSS selectors maintain class version
- [x] Documentation updated
- [x] Tests verify both methods work
- [ ] Future: Remove class-based selectors (when ready)
- [ ] Future: Remove class manipulation from JS (when ready)

## Conclusion

The **data-theme attribute** provides a modern, semantic, and extensible way to manage themes while maintaining full backwards compatibility with the existing class-based approach. This implementation positions the codebase for future enhancements while following current web standards.

**Key Takeaways:**

✅ More semantic HTML
✅ Cleaner JavaScript API
✅ Better CSS readability
✅ Future-proof for multiple themes
✅ Full backwards compatibility
✅ Standards-compliant
✅ Framework-friendly
✅ Better developer experience

The implementation achieves the best of both worlds: modern semantics with zero breaking changes.
