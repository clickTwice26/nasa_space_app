# TerraPulse Design System Documentation

## Overview
This document outlines the TerraPulse global CSS design system with comprehensive branding colors, components, and utilities for consistent UI development across the entire application.

## 🎨 Color Palette

### Primary Brand Colors
- **Terra Green**: The main brand color representing environmental sustainability
  - `--terra-green-600` (#059669) - Primary brand color
  - `--terra-green-50` to `--terra-green-950` - Full spectrum
  - Usage: `color: var(--terra-green-600)` or `background-color: var(--primary-color)`

### Secondary Colors
- **Terra Blue**: Represents water and sky elements
  - `--terra-blue-500` (#0ea5e9) - Secondary brand color
  - Full spectrum available

### Alert Colors
- **Terra Red**: Error states and high-risk warnings
- **Terra Yellow**: Warnings and moderate-risk alerts  
- **Terra Orange**: Urgent notifications and cautions

### Neutral Colors
- **Terra Gray**: Text, borders, and background variations
  - `--terra-gray-50` - Lightest background
  - `--terra-gray-900` - Primary text color

## 🏗️ Component Library

### Buttons
```html
<!-- Primary Button -->
<button class="btn btn-primary">Save Changes</button>

<!-- Secondary Button -->
<button class="btn btn-secondary">Cancel</button>

<!-- Outline Button -->
<button class="btn btn-outline">Learn More</button>

<!-- Ghost Button -->
<button class="btn btn-ghost">Skip</button>

<!-- Danger Button -->
<button class="btn btn-danger">Delete</button>

<!-- Button Sizes -->
<button class="btn btn-primary btn-sm">Small</button>
<button class="btn btn-primary">Default</button>
<button class="btn btn-primary btn-lg">Large</button>
<button class="btn btn-primary btn-xl">Extra Large</button>

<!-- Full Width Button -->
<button class="btn btn-primary btn-full">Full Width</button>
```

### Cards
```html
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Environmental Data</h3>
    <p class="card-subtitle">Real-time monitoring results</p>
  </div>
  <div class="card-body">
    <p>Card content goes here...</p>
  </div>
  <div class="card-footer">
    <button class="btn btn-primary">View Details</button>
  </div>
</div>
```

### Forms
```html
<div class="form-group">
  <label class="form-label" for="location">Location</label>
  <input type="text" id="location" class="form-input" placeholder="Enter location">
  <div class="form-error">Please enter a valid location</div>
</div>

<div class="form-group">
  <label class="form-label" for="crop">Crop Type</label>
  <select id="crop" class="form-select">
    <option>Select crop type</option>
    <option>Rice</option>
    <option>Wheat</option>
  </select>
</div>

<div class="form-group">
  <label class="form-label" for="notes">Notes</label>
  <textarea id="notes" class="form-textarea" placeholder="Additional notes"></textarea>
</div>
```

### Badges
```html
<span class="badge badge-primary">New</span>
<span class="badge badge-success">Completed</span>
<span class="badge badge-warning">Pending</span>
<span class="badge badge-danger">Critical</span>
<span class="badge badge-info">Info</span>
```

### Alerts
```html
<div class="alert alert-success">
  Operation completed successfully!
</div>

<div class="alert alert-warning">
  Please review your input data.
</div>

<div class="alert alert-danger">
  An error occurred. Please try again.
</div>

<div class="alert alert-info">
  New features are available in this update.
</div>
```

## 🛠️ Utility Classes

### Typography
```html
<!-- Font Sizes -->
<p class="text-xs">Extra small text</p>
<p class="text-sm">Small text</p>
<p class="text-base">Base text</p>
<p class="text-lg">Large text</p>
<p class="text-xl">Extra large text</p>

<!-- Font Weights -->
<p class="font-light">Light weight</p>
<p class="font-normal">Normal weight</p>
<p class="font-medium">Medium weight</p>
<p class="font-semibold">Semibold weight</p>
<p class="font-bold">Bold weight</p>

<!-- Text Colors -->
<p class="text-primary">Primary text color</p>
<p class="text-secondary">Secondary text color</p>
<p class="text-muted">Muted text color</p>
<p class="text-green">Brand green color</p>
<p class="text-red">Error red color</p>
```

### Spacing
```html
<!-- Margin -->
<div class="m-4">Margin all sides</div>
<div class="mt-4">Margin top</div>
<div class="mb-4">Margin bottom</div>

<!-- Padding -->
<div class="p-4">Padding all sides</div>
<div class="px-4">Padding horizontal</div>
<div class="py-4">Padding vertical</div>

<!-- Space Between Elements -->
<div class="space-y-4">
  <div>Item 1</div>
  <div>Item 2</div>
  <div>Item 3</div>
</div>
```

### Layout
```html
<!-- Flexbox -->
<div class="flex items-center justify-between">
  <div>Left content</div>
  <div>Right content</div>
</div>

<div class="flex flex-col space-y-4">
  <div>Stacked item 1</div>
  <div>Stacked item 2</div>
</div>

<!-- Display -->
<div class="block">Block element</div>
<div class="inline-block">Inline block</div>
<div class="hidden">Hidden element</div>
```

### Backgrounds & Colors
```html
<div class="bg-primary">Primary background</div>
<div class="bg-secondary">Secondary background</div>
<div class="bg-brand">Brand color background</div>
<div class="gradient-primary">Primary gradient background</div>
```

### Border Radius
```html
<div class="rounded">Default radius</div>
<div class="rounded-lg">Large radius</div>
<div class="rounded-xl">Extra large radius</div>
<div class="rounded-2xl">2X large radius</div>
<div class="rounded-full">Full radius (circle)</div>
```

### Shadows
```html
<div class="shadow-sm">Small shadow</div>
<div class="shadow">Default shadow</div>
<div class="shadow-lg">Large shadow</div>
<div class="shadow-brand">Brand shadow (green tint)</div>
```

## 🌱 TerraPulse Specific Components

### Risk Score Display
```html
<div class="badge risk-low">Low Risk</div>
<div class="badge risk-moderate">Moderate Risk</div>
<div class="badge risk-high">High Risk</div>
```

### Gradient Backgrounds
```html
<div class="gradient-primary">Primary gradient</div>
<div class="gradient-success">Success gradient</div>
<div class="gradient-warning">Warning gradient</div>
<div class="gradient-danger">Danger gradient</div>
```

### Glass Effect
```html
<div class="glass">
  Glassmorphism effect with backdrop blur
</div>
```

### Navigation Items
```html
<a href="/dashboard" class="nav-item nav-item-active">Dashboard</a>
<a href="/predictions" class="nav-item">Predictions</a>
```

### Floating Action Button
```html
<button class="fab w-14 h-14 bg-brand text-white rounded-full">
  <i data-lucide="plus" class="w-6 h-6"></i>
</button>
```

## 📱 Responsive Design

### Breakpoints
- **Small (sm)**: 640px and up
- **Medium (md)**: 768px and up
- **Large (lg)**: 1024px and up
- **Extra Large (xl)**: 1280px and up

### Responsive Utilities
```html
<!-- Show/hide at different breakpoints -->
<div class="block md:hidden">Mobile only</div>
<div class="hidden md:block">Desktop only</div>

<!-- Responsive text sizes -->
<h1 class="text-2xl md:text-4xl lg:text-6xl">Responsive heading</h1>

<!-- Responsive spacing -->
<div class="p-4 md:p-8 lg:p-10">Responsive padding</div>
```

## 🎭 Animations
```html
<div class="animate-fade-in">Fade in animation</div>
<div class="animate-slide-in-up">Slide up animation</div>
<div class="animate-pulse">Pulse animation</div>
```

## ♿ Accessibility

### Focus States
All interactive elements include proper focus states with `outline: 2px solid var(--primary-color)`.

### Touch Targets
On mobile devices, all buttons and interactive elements have minimum 44px touch targets.

### Reduced Motion
Animation respects `prefers-reduced-motion` for users who prefer less motion.

## 🔧 CSS Custom Properties

You can use CSS custom properties (variables) directly in your styles:

```css
.custom-component {
  background-color: var(--primary-color);
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  transition: all var(--transition-normal);
}

.custom-component:hover {
  background-color: var(--primary-dark);
  box-shadow: var(--shadow-brand);
}
```

## 📋 Best Practices

### 1. Use Semantic Color Variables
```css
/* Good */
color: var(--text-primary);
background-color: var(--primary-color);

/* Avoid */
color: #111827;
background-color: #059669;
```

### 2. Consistent Spacing
```html
<!-- Use predefined spacing scale -->
<div class="p-4 mb-6">
  <div class="space-y-4">
    <!-- content -->
  </div>
</div>
```

### 3. Component Composition
```html
<!-- Combine base classes with utilities -->
<button class="btn btn-primary btn-lg shadow-brand">
  Get Started
</button>
```

### 4. Mobile-First Approach
```html
<!-- Start with mobile styles, then add larger breakpoint styles -->
<div class="text-sm md:text-base lg:text-lg p-4 md:p-6 lg:p-8">
  Content
</div>
```

## 🚀 Quick Start Examples

### Environmental Dashboard Card
```html
<div class="card">
  <div class="card-header">
    <h3 class="card-title flex items-center space-x-2">
      <i data-lucide="thermometer" class="w-5 h-5 text-orange"></i>
      <span>Temperature Alert</span>
    </h3>
  </div>
  <div class="card-body">
    <div class="flex items-center justify-between mb-4">
      <span class="text-2xl font-bold">32°C</span>
      <span class="badge risk-moderate">Moderate Risk</span>
    </div>
    <p class="text-secondary">Current temperature is 2°C above average for this region.</p>
  </div>
  <div class="card-footer">
    <button class="btn btn-primary btn-sm">View Details</button>
  </div>
</div>
```

### Prediction Form
```html
<form class="space-y-6">
  <div class="form-group">
    <label class="form-label" for="crop-select">Crop Type</label>
    <select id="crop-select" class="form-select">
      <option>Select crop type</option>
      <option>Rice</option>
      <option>Wheat</option>
      <option>Potato</option>
    </select>
  </div>
  
  <div class="grid grid-cols-2 gap-4">
    <div class="form-group">
      <label class="form-label" for="soil-ph">Soil pH</label>
      <input type="number" id="soil-ph" class="form-input" placeholder="6.5" step="0.1">
    </div>
    <div class="form-group">
      <label class="form-label" for="moisture">Soil Moisture (%)</label>
      <input type="number" id="moisture" class="form-input" placeholder="65">
    </div>
  </div>
  
  <button type="submit" class="btn btn-primary btn-full">
    Generate Prediction
  </button>
</form>
```

This design system ensures consistency, accessibility, and maintainability across your entire TerraPulse application while providing the flexibility to create custom components when needed.