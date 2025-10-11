# Layout Components

## PageLayout

A wrapper component that provides consistent layout for all dashboard pages.

### Usage

```tsx
import PageLayout from "@/components/layout/page-layout";

export default function MyPage() {
  return (
    <PageLayout>
      <div className="p-8">
        {/* Your page content here */}
        <h1>My Page</h1>
      </div>
    </PageLayout>
  );
}
```

### Features

- **Dark sidebar**: Consistent navigation across all pages
- **Responsive**: Adapts to different screen sizes
- **Overflow handling**: Content area scrolls independently
- **Custom styling**: Pass additional className for content area

### Props

- `children`: ReactNode - The page content
- `className?`: string - Additional CSS classes for the content area

### Layout Structure

```
┌─────────────────────────────────────┐
│ PageLayout (flex h-screen bg-gray-50) │
├─────────────┬───────────────────────┤
│   Sidebar   │    Content Area       │
│  (w-80)     │   (flex-1 overflow-   │
│             │    auto + className)  │
│             │                       │
│             │   {children}          │
│             │                       │
└─────────────┴───────────────────────┘
```

This component is used by:
- Dashboard page
- Reddit Leads page
- Any other dashboard-style pages

Pages that DON'T use this layout:
- Landing page (marketing site)
- 404/Not Found page (standalone)