---
id: 26
title: "Code Splitting & Bundle Optimization"
priority: medium
type: tech-debt
agent: frontend
sprint: 3
estimate: M
status: ready
created: 2026-11-03
reviewed_by: techlead
---

# Card #26: Code Splitting & Bundle Optimization

## Description
Reduce the frontend bundle size from ~995kB to <500kB by implementing code splitting (lazy routes), tree shaking optimization, and bundle analysis.

## Current State
- `pnpm build` produces ~995kB main chunk (gzipped ~280kB)
- All routes loaded eagerly in `App.tsx`
- No dynamic imports for pages
- Heavy dependencies: Recharts, Radix UI, @tanstack/react-query, axios, zod, @faker-js/faker (dev)

## Acceptance Criteria

### Lazy Route Implementation
- [ ] Convert all page imports in `App.tsx` to `React.lazy()`
- [ ] Wrap routes with `<Suspense fallback={<PageSkeleton />}>`
- [ ] Create `PageSkeleton` component using design system classes
- [ ] Verify each page loads as separate chunk

### Bundle Analysis
- [ ] Run `pnpm build --analyze` (add to vite.config.ts)
- [ ] Identify largest dependencies
- [ ] Document findings in card

### Tree Shaking & Dependency Optimization
- [ ] Audit imports: ensure ES modules used (not CommonJS)
- [ ] Check for barrel exports causing full library imports
- [ ] Replace `import * as` with named imports where possible
- [ ] Consider lighter alternatives for heavy deps (e.g., date-fns instead of moment if used)

### Vite Config Optimizations
- [ ] Configure `build.rollupOptions.output.manualChunks` for vendor splitting
- [ ] Separate: react-vendor, radix-vendor, query-vendor, charts-vendor, utils-vendor
- [ ] Enable `build.cssCodeSplit: true`
- [ ] Configure `build.minify: 'esbuild'` (default) or `terser` for better compression

### Target Chunk Sizes
| Chunk | Target (gzipped) |
|-------|------------------|
| Main (app) | < 100kB |
| React vendor | < 50kB |
| Radix UI vendor | < 50kB |
| TanStack Query vendor | < 30kB |
| Recharts vendor | < 50kB |
| Other vendors | < 50kB |
| **Total** | **< 300kB gzipped** |

## Technical Requirements

### Files to Modify
- `frontend/src/App.tsx` - Lazy routes + Suspense
- `frontend/vite.config.ts` - Bundle analysis, manualChunks
- `frontend/src/components/PageSkeleton.tsx` - New component
- `frontend/src/pages/*.tsx` - Ensure default exports for lazy loading

### Implementation Pattern
```tsx
// App.tsx - BEFORE
import { Dashboard } from './pages/Dashboard';
import { Documents } from './pages/Documents';

// App.tsx - AFTER
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
const Documents = React.lazy(() => import('./pages/Documents'));

// Wrap in Suspense
<Suspense fallback={<PageSkeleton />}>
  <Routes>
    <Route path="/dashboard" element={<Dashboard />} />
    <Route path="/documents" element={<Documents />} />
  </Routes>
</Suspense>
```

### PageSkeleton Component
```tsx
// src/components/PageSkeleton.tsx
export function PageSkeleton() {
  return (
    <div className="page-header">
      <div className="skeleton skeleton-title" />
      <div className="skeleton skeleton-subtitle" />
    </div>
    <div className="section">
      <div className="skeleton skeleton-card" />
      <div className="skeleton skeleton-card" />
      <div className="skeleton skeleton-card" />
    </div>
  );
}
```

Add skeleton styles to `index.css`:
```css
.skeleton { background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%); background-size: 200% 100%; animation: shimmer 1.5s infinite; }
.skeleton-title { height: 28px; width: 40%; border-radius: 4px; }
.skeleton-subtitle { height: 16px; width: 60%; border-radius: 4px; margin-top: 8px; }
.skeleton-card { height: 120px; border-radius: 8px; }
@keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
```

### Vite Config - manualChunks
```typescript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'radix-vendor': [
            '@radix-ui/react-dialog',
            '@radix-ui/react-dropdown-menu',
            '@radix-ui/react-avatar',
            '@radix-ui/react-tabs',
            '@radix-ui/react-select',
            '@radix-ui/react-tooltip',
            '@radix-ui/react-toast',
          ],
          'query-vendor': ['@tanstack/react-query'],
          'charts-vendor': ['recharts'],
          'forms-vendor': ['react-hook-form', '@hookform/resolvers', 'zod'],
          'utils-vendor': ['axios', 'clsx', 'tailwind-merge', 'date-fns'],
        },
      },
    },
    cssCodeSplit: true,
  },
});
```

## Dependencies
- Card #01: Testing infrastructure (DONE)
- Card #03: Dashboard Charts (Recharts - after this is done)
- Card #07: Design System (Toast, Tooltip, Tabs, Select - after these are done)

## Testing Requirements
- Verify all lazy routes load correctly
- Test Suspense fallback shows during load
- Run `pnpm build` and verify chunk sizes
- Run `pnpm build --analyze` and review report
- Ensure no regression in functionality

## Definition of Done
- [ ] All pages lazy loaded with Suspense
- [ ] PageSkeleton component created and styled
- [ ] Vite config optimized with manualChunks
- [ ] Build produces chunks meeting target sizes
- [ ] Bundle analysis report reviewed and documented
- [ ] All quality gates pass: `pnpm lint && pnpm build && pnpm test`
- [ ] No runtime errors from lazy loading
- [ ] Card moved to `review/`

## Notes
- This is a technical debt card - no new features
- Run `pnpm build && npx vite-bundle-analyzer dist` to analyze
- Consider: `@vitejs/plugin-react` already handles React refresh
- Radix UI: only import primitives you use (tree shaking works well)
- Recharts: consider if all charts needed or use lighter alternative for simple charts