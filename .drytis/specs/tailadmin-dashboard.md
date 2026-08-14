# TailAdmin Dashboard for Studio Mathri

## Goal
A beautiful, high-themed TailAdmin eCommerce admin dashboard at `/dashboard/` that pulls ALL real data from existing Django models. NO modifications to any existing files except `tiles/urls.py` (one line added).

## Files to create (ALL NEW)
1. `tiles/views_dashboard.py` — Django view with `@staff_member_required`
2. `tiles/templates/tiles/dashboard.html` — Full TailAdmin dashboard
3. `.drytis/specs/tailadmin-dashboard.md` — This spec

## Files to modify (ONE ONLY)
- `tiles/urls.py` — add `path('dashboard/', ...)` route

## Data sources (all from existing models)
- **Stat cards**: Total Users, Total Products, Total Countries, Total AI Generations (images+chats)
- **Charts**:
  - Bar chart: Products per Category (top 10)
  - Donut chart: Products per Material
  - Area chart: Monthly registrations + product additions
  - Pie chart: Order status distribution (if orders exist)
- **Maps**: jsvectormap world map showing country rankings (all 10 countries)
- **Tables**:
  - Recent products (image, name, category, material, price)
  - Recent users (email, join date)
  - Recent AI chats
  - Recent generated images
  - Top countries (flag, ranking, producer/consumer badges)

## UI Requirements
- Tailwind CSS (via CDN, dark mode)
- ApexCharts for charts
- jsvectormap for world map
- Alpine.js for dropdowns/sidebar collapse
- Dark/light theme toggle (localStorage)
- Collapsible sidebar with sections
- Top navbar with search + user dropdown
- Responsive

## Acceptance Criteria
- [ ] Dashboard loads at /dashboard/ and shows real data
- [ ] All 4 chart types render with real data
- [ ] World map shows all 10 countries
- [ ] All 5 tables populate with real records
- [ ] Dark/light toggle persists in localStorage
- [ ] Sidebar collapses on mobile
- [ ] Storefront pages (/ , /tiles/, etc.) unaffected
- [ ] Zero JS console errors
