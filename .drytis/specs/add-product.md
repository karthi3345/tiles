# Add Product (dynamic) for Admin Panel

## Goal
On the Products section of the TailAdmin dashboard
(`/admin/section/products/`), add an **Add Product** button next to the
existing **Export Excel** button. Clicking it opens a modal form; submitting
creates a `TileProduct` via AJAX (fetch) without a page reload; on success the
table and record count refresh dynamically (fetch + innerHTML of the table
section), and the modal closes. Errors show inline in the modal.

## Files to change
- `tiles/views_sections.py` — `product_add` view (staff-only, POST, JSON).
- `tiles/dashboard_urls.py` — route `section/products/add/`.
- `tiles/templates/tiles/sections/products.html` — Add Product button +
  modal + JS (button placed in the same header cluster as Export Excel; base
  template untouched so other sections are unchanged).
- `tiles/tests.py` — unit + integration tests.

## Behavior
- Button visible only on the products section (next to Export Excel).
- Modal fields: Name*, Category (dropdown of all categories), Material,
  Price Min*, Price Max*, Featured (checkbox), Active (checkbox),
  Description, Image URL. Slug auto-generated from name (server-side, via
  model save), uniqueness suffix if taken.
- POST `/admin/section/products/add/` with form-encoded fields → JSON:
  - success: `{"ok": true, "id": ..., "name": ..., "slug": ...}`
  - validation error: `{"ok": false, "errors": {field: [msg, ...]}}` (400)
  - non-POST → 405; anonymous/non-staff → 302 login.
- After success, JS re-fetches the section HTML and swaps the table area +
  record count, so the new row appears without reload.

## Validation (server-side)
- `name` required, ≤300 chars; price min/max decimal ≥ 0; price_max ≥
  price_min when both > 0; image URL optional but must be a valid URL if
  given; category optional (FK nullable).

## Acceptance criteria
- [ ] Add Product button renders on products section only, beside Export Excel.
- [ ] Click opens modal (Alpine), no page navigation.
- [ ] Valid submit creates product, returns ok JSON, table refreshes with new
      row, record count increments, modal closes.
- [ ] Invalid submit (empty name / bad price / price_max < price_min / bad
      URL) returns 400 with field errors shown inline; no product created.
- [ ] Anonymous/non-staff POST → 302 login. Non-POST → 405.
- [ ] Slug auto-generated; duplicate names get unique slugs.
- [ ] Unit + integration tests cover the above; full suite green.
- [ ] Export Excel still works (unchanged route/template contract).

## Out of scope
- Editing/deleting products, file uploads (image is URL-only), other sections.
