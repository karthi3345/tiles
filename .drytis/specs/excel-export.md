# Excel Export for Admin Panel

## Goal
Add an "Export Excel" button to every data section of the TailAdmin-style admin
dashboard (`/admin/section/<name>/`) that downloads the section's data as a
real `.xlsx` workbook (generated with `openpyxl` server-side — not CSV).

## Scope
- All 20 existing sections: countries, states, cities, villages, categories,
  effects, finishes, sizes, products, showrooms, insights, chats, messages,
  images, users, profiles, notifications, orders, order-items, payments.
- Export honors the same search filter (`?q=`) as the section list view, so
  admins can export filtered results. Exports ALL matching rows (not just the
  current page).
- Export is staff-only (`@staff_member_required`) — same gate as section views.
- No DB schema changes. No env changes. No new background services.

## Files to change
- `requirements.txt` — add `openpyxl`.
- `tiles/export.py` (NEW) — workbook builder + per-section queryset/columns.
- `tiles/views_sections.py` — one export view dispatching to `tiles/export.py`.
- `tiles/dashboard_urls.py` — route `section/<str:section>/export/`.
- `tiles/templates/tiles/sections/base_section.html` — Export Excel button in
  the header area (shown on all sections).
- `tiles/tests.py` — unit + integration tests.

## Behavior
1. Staff clicks "Export Excel" on any section page.
2. GET `/admin/section/<section>/export/?q=...` streams an `.xlsx` response:
   - `Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
   - `Content-Disposition: attachment; filename="<section>_<yyyymmdd_HHMMSS>.xlsx"`
3. Workbook: one sheet named after the section (≤31 chars, valid chars),
   bold header row, auto column widths, `?q=` search filter applied,
   values rendered as native cell types (numbers as numbers, dates as dates).

## Section columns (match the on-screen tables)
- countries: name, flag, continent, ranking, top producer, top consumer, products
- states: name, type, country, is hub, cities
- cities: name, type, state, country, lat, lng, is hub
- villages: name, type, city, state, country, pincode, showrooms
- categories: name, usage, tile type, sort order, products
- effects: name, products
- finishes: name, products
- sizes: label, width_mm, height_mm, thickness_mm, products
- products: name, category, material, price_min, price_max, featured, active, created
- showrooms: name, village, city, state, country, phone, active, products
- insights: country, title, year, source, created
- chats: title, session_id, messages, created, updated
- messages: session, role, content, created
- images: prompt, model, user email, created
- users: email, username, name, staff, joined, orders, images
- profiles: user email, full name, phone, country, city, created
- notifications: user email, type, message, read, created
- orders: order_id, customer, email, phone, amount, currency, status, items, created
- order-items: order, tile, qty, price, size, total
- payments: order, payment id, amount, status, created

## Security
- `staff_member_required` on the export view (no anonymous/user export).
- Unknown section → 404 (no exception leak).
- Missing commerce tables → empty export, same safe fallback as section views.

## Acceptance criteria
- [ ] Export button visible on every section page, links to the export URL.
- [ ] GET export URL as staff returns 200, correct xlsx content-type,
      attachment disposition with timestamped filename.
- [ ] Exported workbook opens as valid xlsx (openpyxl can re-read it) and
      sheet header + row count match DB.
- [ ] `?q=` filter is honored in export (row counts match filtered section).
- [ ] Non-staff (anonymous) request redirects to admin login (302).
- [ ] Invalid section name → 404.
- [ ] Unit tests: sheet-name sanitization, cell value rendering.
- [ ] Integration tests: staff export 200 + xlsx + row count; anonymous 302;
      unknown section 404; q filter applied.
- [ ] Full existing test suite still passes.

## Out of scope
- CSV export, dashboard-level combined workbook, per-column selection,
  exporting Django admin (`/django-admin/`) pages.
