// Page Skeleton Component
// Card #26: Code Splitting & Bundle Optimization
// Loading fallback for lazy-loaded pages

import { Fragment } from 'react';

export function PageSkeleton() {
  return (
    <Fragment>
      <div className="page-header">
        <div className="skeleton skeleton-title" />
        <div className="skeleton skeleton-subtitle" />
      </div>
      <div className="section">
        <div className="grid-kpi">
          <div className="skeleton skeleton-card" />
          <div className="skeleton skeleton-card" />
          <div className="skeleton skeleton-card" />
          <div className="skeleton skeleton-card" />
        </div>
        <div className="grid gap-4 lg:grid-cols-2 mt-6">
          <div className="skeleton skeleton-chart" />
          <div className="skeleton skeleton-chart" />
        </div>
      </div>
    </Fragment>
  );
}

export function PageSkeletonMinimal() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-secondary-50">
      <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent" />
    </div>
  );
}