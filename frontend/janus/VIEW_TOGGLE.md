# View Toggle Documentation

## Overview

The view toggle is a segmented control that allows users to switch between "Node editor" and "chart" views in the application.

## Component: ViewToggle

**Location**: `/src/components/ViewToggle.tsx`

### Features

✅ **Two views**:
- Node editor (default)
- Chart view

✅ **Visual design**:
- White rounded pill background
- Active button has white background with shadow
- Inactive buttons are transparent with gray text
- Smooth transitions between states
- Icons for each view

✅ **Interactive**:
- Hover effects on inactive buttons
- Click to switch views
- Smooth color transitions

## Usage

### Basic Implementation

```typescript
import ViewToggle from '@/components/ViewToggle';
import { useState } from 'react';

function MyComponent() {
  const [activeView, setActiveView] = useState<'node-editor' | 'chart'>('node-editor');

  return (
    <ViewToggle
      activeView={activeView}
      onViewChange={setActiveView}
    />
  );
}
```

### Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `activeView` | `'node-editor' \| 'chart'` | Yes | Current active view |
| `onViewChange` | `(view: 'node-editor' \| 'chart') => void` | Yes | Callback when view changes |

## Current Implementation

### CanvasWithPolling.tsx

The toggle is positioned at the top-left of the canvas:

```typescript
<div className="absolute left-8 top-8 z-10">
  <ViewToggle activeView={activeView} onViewChange={setActiveView} />
</div>
```

### View Rendering

The component conditionally renders content based on the active view:

**Node Editor View**:
- ReactFlow canvas with nodes and edges
- Floating ChatBox at bottom
- Full interactive graph editing

**Chart View** (Placeholder):
- Centered placeholder with chart icon
- "Coming soon..." message
- Ready for future implementation

## Styling

### Active Button
```css
background: white
color: black
box-shadow: medium shadow
border-radius: full (pill shape)
padding: 0.75rem 1.5rem
```

### Inactive Button
```css
background: transparent
color: gray-400
hover:color: gray-600
border-radius: full
padding: 0.75rem 1.5rem
```

### Container
```css
background: white
border-radius: full
padding: 0.25rem
box-shadow: large shadow
```

## Icons

### Node Editor Icon
- **Type**: Grid/nodes icon
- **Design**: 4 small squares arranged in a 2x2 grid
- **Represents**: Node-based editing

### Chart Icon
- **Type**: Bar chart icon
- **Design**: 3 vertical bars of different heights
- **Represents**: Data visualization/analytics

## Adding the Chart View

When ready to implement the chart view, replace the placeholder:

```typescript
{activeView === 'node-editor' ? (
  // Node editor view
  <NodeEditorView />
) : (
  // Replace placeholder with actual chart component
  <ChartView data={yourData} />
)}
```

### Recommended Chart Libraries

- **Recharts**: Simple, React-native charts
- **Chart.js**: Popular, feature-rich
- **D3.js**: Powerful, customizable
- **Victory**: React-focused charting

## Future Enhancements

### Possible Additional Views
```typescript
type View = 'node-editor' | 'chart' | 'table' | 'timeline';
```

### View Persistence
```typescript
// Save view preference to localStorage
useEffect(() => {
  localStorage.setItem('preferred-view', activeView);
}, [activeView]);

// Load on mount
const [activeView, setActiveView] = useState(() => {
  return (localStorage.getItem('preferred-view') as View) || 'node-editor';
});
```

### Keyboard Shortcuts
```typescript
useEffect(() => {
  const handleKeyPress = (e: KeyboardEvent) => {
    if (e.metaKey || e.ctrlKey) {
      if (e.key === '1') setActiveView('node-editor');
      if (e.key === '2') setActiveView('chart');
    }
  };

  window.addEventListener('keydown', handleKeyPress);
  return () => window.removeEventListener('keydown', handleKeyPress);
}, []);
```

### Tooltips
```typescript
<button title="Switch to Node Editor (⌘1)">
  Node editor
</button>
```

## Positioning Options

### Current (Top-Left)
```typescript
<div className="absolute left-8 top-8 z-10">
  <ViewToggle />
</div>
```

### Alternative Positions

**Top-Center**:
```typescript
<div className="absolute left-1/2 top-8 z-10 -translate-x-1/2">
  <ViewToggle />
</div>
```

**Top-Right**:
```typescript
<div className="absolute right-8 top-8 z-10">
  <ViewToggle />
</div>
```

## Customization

### Different Colors

```typescript
// Active button with brand color
className={`... ${
  activeView === 'node-editor'
    ? 'bg-blue-500 text-white'  // Brand color
    : 'bg-transparent text-gray-400'
}`}
```

### More Views

```typescript
<button onClick={() => onViewChange('table')}>
  <TableIcon />
  <span>Table</span>
</button>
```

### Vertical Layout

```css
flex-direction: column
```

## Accessibility

### Keyboard Navigation
- ✅ Tab to focus buttons
- ✅ Enter/Space to activate
- ✅ Arrow keys to navigate (can be added)

### Screen Readers
```typescript
<button
  aria-pressed={activeView === 'node-editor'}
  aria-label="Switch to node editor view"
>
  Node editor
</button>
```

### Focus States
Add focus rings:
```css
focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
```

## Testing

### Manual Testing Checklist
- [ ] Click "Node editor" - canvas appears
- [ ] Click "chart" - placeholder appears
- [ ] Toggle back and forth - smooth transitions
- [ ] Hover over inactive button - color changes
- [ ] Visual feedback on active button

### Unit Testing
```typescript
import { render, fireEvent } from '@testing-library/react';

test('switches views on click', () => {
  const handleChange = jest.fn();
  const { getByText } = render(
    <ViewToggle activeView="node-editor" onViewChange={handleChange} />
  );

  fireEvent.click(getByText('chart'));
  expect(handleChange).toHaveBeenCalledWith('chart');
});
```

## Browser Compatibility

The component uses standard React and Tailwind CSS:
- ✅ Chrome/Edge (all versions)
- ✅ Firefox (all versions)
- ✅ Safari (all versions)
- ✅ Mobile browsers

## Performance

The component is lightweight:
- **Bundle size**: ~2KB
- **Re-renders**: Only on view change
- **No external dependencies**: Pure React

## Migration Guide

If you want to replace the placeholder chart view:

1. Create `ChartView.tsx`:
```typescript
export default function ChartView({ nodes, edges }) {
  return (
    <div className="h-full w-full">
      {/* Your chart implementation */}
    </div>
  );
}
```

2. Update `CanvasWithPolling.tsx`:
```typescript
import ChartView from './ChartView';

// In render:
{activeView === 'chart' && (
  <ChartView nodes={nodes} edges={edges} />
)}
```

3. Done! The toggle will automatically work with your new view.
