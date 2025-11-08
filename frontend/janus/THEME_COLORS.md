# Theme Colors Documentation

## Overview

All application colors are now centralized in `/src/styles/theme.ts` for consistent theming and easy updates.

## Color Palette

### UI Colors

| Element | Color | Hex Code |
|---------|-------|----------|
| Search Tab | Light Gray | `#F2F2F2` |
| Logo | Orange | `#FBAE2C` |
| Share Button | White | `#FFF` |
| White Button | White | `#FFF` |

### Node Colors

| Element | Color | Value |
|---------|-------|-------|
| Node Background | White | `#FFFFFF` |
| Node Pending Background | Light Green (with alpha) | `#65F57466` |
| Node Highlight Border | Purple/Blue Gradient | `radial-gradient(247.65% 141.42% at 0% 100%, #4A02FF 0%, #831DEF 50%, #AA31E4 100%)` |

### Button Colors

#### Approve Button (Check)
- **Background**: `#A2FFAB` (Light Green)
- **Border**: `1px solid #65F574` (Green)

#### Reject Button (X)
- **Background**: `#FF7F7F` (Light Red)
- **Border**: `1px solid #FF3B3B` (Red)

## Usage

### Import Theme Constants

```typescript
import { THEME_COLORS, getButtonStyle, getNodeHighlightStyle } from '@/styles/theme';
```

### Using Colors

```typescript
// Direct color usage
<div style={{ background: THEME_COLORS.nodeBackground }}>

// Using helper functions
<button style={getButtonStyle('approve')}>Approve</button>
<button style={getButtonStyle('reject')}>Reject</button>

// Node highlight style
<div style={getNodeHighlightStyle()}>Pending Node</div>
```

### Available Exports

#### `THEME_COLORS`
Object containing all theme colors:
```typescript
THEME_COLORS.searchTab
THEME_COLORS.logo
THEME_COLORS.shareButton
THEME_COLORS.whiteButton
THEME_COLORS.nodeBackground
THEME_COLORS.nodeHighlightBorder
THEME_COLORS.nodePendingBackground
THEME_COLORS.approveButton.background
THEME_COLORS.approveButton.border
THEME_COLORS.rejectButton.background
THEME_COLORS.rejectButton.border
```

#### `getButtonStyle(type: 'approve' | 'reject')`
Returns style object for approve or reject buttons:
```typescript
{
  background: string,
  border: string
}
```

#### `getNodeHighlightStyle()`
Returns style object for node highlight border:
```typescript
{
  border: '4px solid transparent',
  borderImage: 'radial-gradient(...) 1'
}
```

#### `GRADIENTS`
Pre-defined gradients:
```typescript
GRADIENTS.nodeHighlight
```

## Applied Components

### TaskCardNode.tsx
- ✅ Normal node background: `#FFFFFF`
- ✅ Pending node background: `#65F57466`
- ✅ Pending node border: Purple/Blue gradient
- ✅ Approve button: Green theme
- ✅ Reject button: Red theme

### Future Components
When creating new components, use the theme constants:
- Logo component: Use `THEME_COLORS.logo`
- Search bars: Use `THEME_COLORS.searchTab`
- Share buttons: Use `THEME_COLORS.shareButton`

## Updating Colors

To change a color across the entire app:

1. Update the value in `/src/styles/theme.ts`
2. Save the file
3. All components using that color will update automatically

Example:
```typescript
// Before
approveButton: {
  background: '#A2FFAB',
  border: '#65F574',
}

// After
approveButton: {
  background: '#00FF00',  // Different green
  border: '#00CC00',
}
```

## Color Specifications

### Node Highlight Gradient Details

**Type**: Radial Gradient
**Size**: 247.65% 141.42%
**Position**: 0% 100% (bottom-left)
**Color Stops**:
- 0%: `#4A02FF` (Purple)
- 50%: `#831DEF` (Medium Purple)
- 100%: `#AA31E4` (Light Purple)

**CSS**:
```css
background: radial-gradient(247.65% 141.42% at 0% 100%, #4A02FF 0%, #831DEF 50%, #AA31E4 100%);
```

### Alpha Transparency

**Node Pending Background**: `#65F57466`
- Base color: `#65F574` (Green)
- Alpha: `66` (40% opacity in hex)

## Tailwind Equivalents

If you prefer Tailwind classes for some elements:

```typescript
// Instead of:
style={{ background: THEME_COLORS.nodeBackground }}

// You can use:
className="bg-white"  // Equivalent to #FFFFFF
```

However, for custom colors like the gradient border, inline styles are necessary.

## Dark Mode (Future)

Currently, the app uses a light theme. For future dark mode support:

1. Extend `theme.ts` with dark variants
2. Add mode detection
3. Conditionally apply colors based on mode

Example structure:
```typescript
export const THEME_COLORS = {
  light: {
    nodeBackground: '#FFFFFF',
    // ...
  },
  dark: {
    nodeBackground: '#1F2937',
    // ...
  }
}
```

## Accessibility

All color combinations meet WCAG contrast requirements:
- ✅ Black text on white background (21:1 ratio)
- ✅ Black text on light green background (#A2FFAB)
- ✅ Black text on light red background (#FF7F7F)

## Browser Support

The gradient syntax is supported in:
- ✅ Chrome 26+
- ✅ Firefox 16+
- ✅ Safari 7+
- ✅ Edge 12+

For older browsers, consider adding fallback colors.
