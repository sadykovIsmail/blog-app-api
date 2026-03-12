# Product Plan: Proof-First Blogging

This is a blog platform optimized for technical and educational writing.

## What We Solve (That Popular Blog Apps Still Do Poorly)

Most platforms treat evidence as optional and unmaintained:
- Citations are just URLs (no structure, no verification)
- Links rot silently (dead links, moved pages, content drift)
- Revisions are opaque (no clear changelog of what changed and why)

For technical posts, that is a real usability problem: readers cannot quickly validate claims, and authors cannot keep posts trustworthy over time.

## Why People Will Use This

Because it saves time and increases trust.
- Readers get an Evidence Panel that makes verification fast.
- Authors get automatic link-health monitoring so their best posts stay credible.
- Communities get fewer repetitive debates because claims map to sources.

Core loop:
1) Publish a post with structured citations.
2) Platform snapshots source metadata and checks link health.
3) When sources break or drift, the author gets notified and can patch with a transparent changelog.
4) Readers see evidence quality and revision history.

## Current Repo State (Already Implemented)

- Django 5.2 + DRF API, PostgreSQL, Docker Compose
- JWT auth (SimpleJWT)
- Authors and Blog Posts (scoped to logged-in user)
- Cover image upload endpoint
- Tests for auth, posts, permissions, uploads, edge cases

## Roadmap (Week-By-Week)

Each week should end with a demoable feature set and tests.

### Week 0: Prep (1-2 days)

- Decide product mode: public multi-user platform (recommended)
- Add a `docs/DECISIONS.md` with short decisions (slug uniqueness, public visibility rules)
- Verify CI passes locally (docker compose + tests)

Exit criteria:
- You can run `docker compose up --build` and `python manage.py test` reliably.

### Week 1: Public Reading + Editorial Workflow

Goal: Real public product while keeping authoring secure.

Build:
- Registration endpoint (or invite-only for now)
- Public profile (`handle`) separate from private username
- Post workflow fields:
  - `status`: DRAFT / SCHEDULED / PUBLISHED / ARCHIVED
  - `visibility`: PUBLIC / UNLISTED
  - `slug`, `published_at`, `scheduled_for`
- Public endpoints:
  - `GET /api/public/posts/` (published only, paginated)
  - `GET /api/public/profiles/{handle}/posts/`
- Search + ordering + pagination for feeds

Exit criteria:
- Unauthenticated users can browse only published posts.
- Authors can create drafts and schedule publishing.
- Tests cover: public visibility, status transitions, search + pagination.

### Week 2: Engagement (Followers, Comments, Reactions)

Goal: Add the features people expect so the app feels alive.

Build:
- Follows graph:
  - follow/unfollow, follower/following counts
- Comments:
  - threaded replies, edit/delete rules
- Reactions:
  - on posts and comments
- Notifications (basic):
  - new follower, comment, reply, new published post from followed author

Exit criteria:
- Users can follow authors and get notifications.
- Comments are permissioned and threaded correctly.
- Tests cover: follow uniqueness, comment threading, notification creation.

### Week 3: Trust Layer v1 (The Differentiator)

Goal: Make technical posts verifiable and maintainable.

Build:
- Structured citations attached to posts:
  - `url`, `title?`, `publisher?`, `published_at?`, `accessed_at`
- Evidence Panel endpoint:
  - citations + link health status + last checked
- Link health checker:
  - management command first (no Celery required yet)
  - store `http_status`, `checked_at`, `canonical_url`, `content_hash`
- Author alerts:
  - notify author when a citation becomes dead or changes materially (hash drift)

Exit criteria:
- Every post can show an Evidence Panel.
- A broken citation becomes visible and triggers an author notification.
- Tests cover: citation CRUD, evidence panel output, link-health updates.

### Week 4: Revisions + Reviews (Quality Flywheel)

Goal: Make edits transparent and enable quality feedback.

Build:
- Post versioning:
  - `PostVersion` with `reason_for_change` and content snapshot
  - reader-visible changelog endpoint
- Optional lightweight reviews:
  - request review, reviewers submit structured feedback (rating + notes)
- Content linting (API-side):
  - max-length limits, link count limits, basic markdown rules

Exit criteria:
- A post has a changelog users can view.
- Reviews have clear permissions and moderation controls.
- Tests cover: version creation, changelog access, review flow.

### Week 5: Production Hardening

Goal: Ship it as something stable and safe.

Build:
- Rate limiting (DRF throttles): auth, comments, follows, evidence checks
- Moderation:
  - reports, comment hiding, audit trail for actions
- Performance:
  - indexes for feeds, cursor pagination (or efficient page pagination)
  - caching for public feed (short TTL)
- Observability:
  - request IDs + structured logs

Exit criteria:
- Abuse-resistant endpoints (throttles + moderation).
- Public feed remains fast as data grows.
- CI stays green.

## What To Build First (Next Action)

Start with Week 1 (public reading + editorial workflow). Without public reading, followers/comments do not matter and the product cannot grow.

## What Makes This Resume-Grade

- You can explain a real user problem (trust + link rot) and why your system solves it.
- You demonstrate backend fundamentals: permissions, throttling, concurrency, indexing, pagination, background work, auditability.
