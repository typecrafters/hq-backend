# TypeCrafters HQ — v1 Completion Audit

## Context

The repo has three independent apps meant to work together: **hq-backend** (FastAPI, port from an earlier NestJS implementation on `main`), **hq-admin** (SvelteKit admin panel), and **hq-web** (SvelteKit public landing site). Every idea for v1 exists *somewhere* — a DB model here, a page shell there, an email template elsewhere — but almost nothing is connected end-to-end. This audit inventories exactly what's done, what's stubbed, and what's missing across all three, so the remaining work can be scoped and estimated.

**Scoping decisions confirmed with the user:**
- **FactuScan** (invoice/receipt feature) — v1 scope is **upload + manual data entry only**, no OCR/automated extraction.
- **Test coverage** — the 90%-coverage gate already configured in `hq-backend/pyproject.toml` will be **relaxed for v1**; tests are a post-launch concern, not budgeted below.

---

## Current State Summary

### hq-backend (FastAPI)
- **Working:** login (session-cookie based), user create/list, Argon2 password hashing, MinIO presign helper (unwired), 7 DB models (User, Role, Session, Token, Message, Post, Project), 2 polished HTML email templates (unwired).
- **Stubbed:** `POST /auth/password/forgot` is a bare `pass`; `AuthService` hardcodes IP/user-agent to `''`.
- **Missing entirely:** logout, password-reset completion, email verification, any routes/services for messages/posts/projects/roles/tokens, permission enforcement, file-upload endpoint, working email sending (TemplatingService is broken — `FileSystemLoader()` has no search path), DB migrations (currently dev-only `create_all`), FactuScan (not started at all here).
- Known schema/model mismatches: `role_id` missing FK constraint; `UserWithRole`/`Session` response schemas declare non-nullable fields that the DB models allow as nullable; `CreateUser.can_access_panel` is accepted but silently dropped.

### hq-admin (SvelteKit)
- **UI-shell only, zero backend integration** — no fetch/axios/API client anywhere in the codebase, no `.env`, no `hooks.server.ts`.
- Login and forgot-password forms exist but their server actions are **empty** — submitting does nothing.
- `(protected)` route group has **no auth guard** — any URL is reachable without logging in.
- Users/Projects/Messages pages render **hardcoded mock arrays** (no create/update/delete anywhere); Blog and FactuScan/media pages are just a header bar over an **empty div**.
- All "create new" buttons link to `/hq/{section}/new` routes that **don't exist** (404 today).
- `legal/privacy` and `legal/terms` pages are **empty files** (0 bytes).

### hq-web (SvelteKit)
- Single page (`/`), no `load()` functions anywhere, **zero backend integration**.
- Project and Team sections render **exactly one hardcoded card each** despite grid CSS built for many, and copy claiming "four projects."
- Blog section is a **heading with no content** at all.
- Contact form has **no `action`/handler** — submitting it does nothing.
- No SEO meta tags, no Open Graph, no sitemap/robots.txt, no analytics, no `<title>`.
- Hero CTA buttons link to `/` (dead links). Two lockfiles present (`bun.lock` + `package-lock.json`) — inconsistent package-manager usage.

---

## Punch List & Estimate

### A. Backend (hq-backend)
| # | Item | Hours |
|---|---|---|
| 1 | Auth completion: logout endpoint, wire the existing (unused) `get_current`/`RequiresCurrent` guard onto protected routes, capture real IP/user-agent, session revocation | 4–6 |
| 2 | Password reset flow: token issuance via existing `Token` model, reset-confirm endpoint, fix `TemplatingService` (missing loader path), wire `EmailService` to send the existing HTML template instead of plaintext, wire `frontend_url` into the reset link | 6–8 |
| 3 | Email verification flow (schema + route + service, tie to existing `Token` model + `verify-email.html.j2`) | 4–5 |
| 4 | Users CRUD completion: get-by-id, update, delete routes; fix nullable-field schema mismatches and dropped `can_access_panel`; add `role_id` FK constraint | 5–7 |
| 5 | Messages module (schema + service + routes: list/get/reply/mark-read) — backs both admin inbox and web contact form | 6–8 |
| 6 | Posts/Blog module (schema + service + CRUD routes) | 6–8 |
| 7 | Projects module (schema + service + CRUD routes) | 6–8 |
| 8 | File-upload route exposing the existing `FileService` (MinIO presign) | 3–4 |
| 9 | Role/permission enforcement on protected routes | 3–4 |
| 10 | Alembic migrations (replace dev-only `create_all`) | 3–4 |
| 11 | FactuScan backend: invoice/receipt model + upload + manual-entry CRUD routes (no OCR) | 10–14 |
| **Subtotal** | | **56–76** |

### B. Admin (hq-admin)
| # | Item | Hours |
|---|---|---|
| 1 | API client + env config (base URL, cookie forwarding, CORS-aware fetch wrapper) | 3–4 |
| 2 | Auth wiring: real login action, forgot-password action, `(protected)` layout guard, logout | 6–8 |
| 3 | Users page: real CRUD (list/create/edit/delete), remove mock data | 6–8 |
| 4 | Projects page: real CRUD | 6–8 |
| 5 | Messages page: real list + mark-read/reply | 4–6 |
| 6 | Blog page: real CRUD + editor for the JSONB content field | 8–10 |
| 7 | FactuScan/media page: upload widget (presigned URL) + manual entry form + list | 12–16 |
| 8 | Legal privacy/terms content (currently empty files) | 2–4 |
| **Subtotal** | | **47–64** |

### C. Web (hq-web)
| # | Item | Hours |
|---|---|---|
| 1 | API integration/env wiring to hq-backend | 4–6 |
| 2 | Contact form → messages backend, with success/error UI | 3–4 |
| 3 | Project section made dynamic + `/projects/[slug]` detail pages | 6–8 |
| 4 | Blog section built out (listing) + `/blog/[slug]` detail pages | 8–12 |
| 5 | Team section made dynamic (pull from `User.show_on_page`) | 3–4 |
| 6 | SEO: meta tags, Open Graph, sitemap, robots.txt, analytics | 4–6 |
| 7 | Fix dead hero CTA links; resolve dual lockfiles (bun vs npm) | 1–2 |
| **Subtotal** | | **29–42** |

### D. Cross-cutting
| # | Item | Hours |
|---|---|---|
| 1 | CORS config across all three apps | 1–2 |
| 2 | Deployment/adapter decisions (pin hq-admin's adapter, resolve hq-web lockfile duplication) | 2–3 |
| 3 | End-to-end integration QA pass once everything is wired | 4–6 |
| **Subtotal** | | **7–11** |

---

## Total Estimate: **~140–195 hours**

At 40 hrs/week solo full-time, that's roughly **3.5–5 weeks**; part-time (~15–20 hrs/week) it's closer to **7–13 weeks**.

**Excluded from this estimate** (per scoping decisions above, or out of bounds for a code audit):
- Full automated test suite to hit the configured 90% coverage gate (deferred post-v1)
- FactuScan OCR/automated data extraction (deferred post-v1; only manual entry is scoped)
- Infra/hosting setup (servers, domains, CI/CD pipelines) — not evidenced as started or requested
- Content/copywriting beyond legal pages (marketing copy, real team bios/photos, real project descriptions) — currently placeholder, may need non-dev time
