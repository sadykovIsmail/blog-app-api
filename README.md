<div align="center">

# Blog Platform API

### Production-grade REST API — Django · PostgreSQL · Redis · Celery · Docker

[![CI](https://github.com/yourusername/blog-app-api/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/blog-app-api/actions)
[![Coverage](https://codecov.io/gh/yourusername/blog-app-api/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/blog-app-api)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2-092E20?style=flat-square&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.16-ff1709?style=flat-square)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-316192?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=flat-square&logo=redis&logoColor=white)](https://redis.io/)
[![Celery](https://img.shields.io/badge/Celery-5.4-37814A?style=flat-square&logo=celery&logoColor=white)](https://docs.celeryq.dev/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)
[![Sentry](https://img.shields.io/badge/Sentry-Monitored-362D59?style=flat-square&logo=sentry&logoColor=white)](https://sentry.io/)
[![JWT](https://img.shields.io/badge/Auth-JWT-000000?style=flat-square&logo=jsonwebtokens&logoColor=white)](https://jwt.io/)
[![Swagger](https://img.shields.io/badge/Docs-Swagger_UI-85EA2D?style=flat-square&logo=swagger&logoColor=black)](https://swagger.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

**A full-featured, production-hardened blog platform REST API. 50+ test files, async task queue, Redis caching, structured JSON logging, GDPR compliance, and a 4-stage CI/CD pipeline.**

[Quick Start](#quick-start) · [API Docs](#api-documentation) · [Architecture](#architecture) · [Tech Stack](#tech-stack) · [Features](#features) · [Testing](#testing)

</div>

---

## Quick Start

```bash
# 1. Clone and enter the project
git clone https://github.com/yourusername/blog-app-api.git
cd blog-app-api

# 2. Create your environment file
cp .env.example .env
# Edit .env — set SECRET_KEY to a long random string

# 3. Start the full stack (Django + PostgreSQL + Redis + Celery + Nginx)
docker compose up --build

# 4. Create a superuser (in a second terminal)
docker compose exec web python manage.py createsuperuser

# 5. Open the interactive API explorer
open http://localhost:8000/api/v1/docs/
```

That's it. The stack auto-runs migrations, collects static files, and starts all services.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        Docker Compose                        │
│                                                              │
│  ┌─────────┐   ┌──────────────────────────────────────────┐ │
│  │  nginx  │──▶│                  web                     │ │
│  │ :80     │   │   Django 5.2 + Gunicorn (4 workers)      │ │
│  │ (Alpine)│   └──────────────┬─────────────┬─────────────┘ │
│  └─────────┘                  │             │               │
│       │             ┌─────────▼──┐   ┌──────▼───────┐      │
│       │ /static/    │ PostgreSQL │   │    Redis 7   │      │
│       │ /media/     │    :5432   │   │    :6379     │      │
│       │ volumes     └────────────┘   └──────┬───────┘      │
│                                             │               │
│                           ┌─────────────────┼────────────┐  │
│                           │  celery-worker  │ celery-beat│  │
│                           │  (4 concurrency)│ (scheduler)│  │
│                           └─────────────────┴────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### Request Lifecycle

```
Client → Nginx → Gunicorn → RequestIDMiddleware
                          → CorsMiddleware
                          → Django Router
                          → View (JWT auth + permissions)
                          → ORM (PostgreSQL)
                          → Redis (cache layer)
                          → JSON Response (with X-Request-ID header)
```

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Framework | Django 5.2 + DRF 3.16 | Battle-tested, mature ecosystem |
| Database | PostgreSQL 16 | Full-text search, ACID transactions, JSON fields |
| Cache / Broker | Redis 7 | Sub-millisecond reads, pub/sub, Celery broker |
| Async Tasks | Celery 5.4 + django-celery-beat | Scheduled jobs, email, link health |
| Auth | JWT (SimpleJWT) | Stateless, scalable, industry standard |
| Error Tracking | Sentry SDK | Real-time error alerts + performance tracing |
| API Docs | drf-spectacular (Swagger UI) | Auto-generated, interactive OpenAPI 3.0 |
| WSGI Server | Gunicorn | Production-grade multi-worker server |
| Reverse Proxy | Nginx Alpine | Static/media serving, security headers |
| Containerisation | Docker Compose | Single-command reproducible environment |
| CI/CD | GitHub Actions (4 jobs) | Lint → Security → Tests → Docker build |
| Testing | pytest + factory_boy + pytest-cov | Industry-standard, 75%+ coverage enforced |
| Search | PostgreSQL Full-Text Search | No extra service — `SearchVector` + `SearchRank` |

---

## Features

<details>
<summary><strong>Content & Publishing</strong></summary>

- Blog posts with **status machine**: `DRAFT → SCHEDULED → PUBLISHED → ARCHIVED`
- **Visibility controls**: `PUBLIC` / `UNLISTED`
- **Scheduled publishing** — set `scheduled_for`; Celery Beat auto-publishes every 5 min
- **Post versioning** — every edit creates a `PostVersion` snapshot with diff reason
- **Image uploads** with automatic resize to max 1200 px width (Pillow)
- **Rich metadata**: reading time, view count, reaction count, co-authors, tags
- **Unique auto-slug** generation with collision handling
- **Content linting** — max 20 external links enforced on published posts

</details>

<details>
<summary><strong>Social & Community</strong></summary>

- **Follows / Unfollow** with notification on follow
- **Block users** — blocks filter feed and interactions
- **Reactions** on posts and comments (toggle)
- **Nested comments** with parent reply threading
- **Bookmarks** — personal reading list
- **Co-authors** — invite collaborators to a post
- **Post series** — curated ordered collections of posts
- **Pin posts** — highlight one post per user profile

</details>

<details>
<summary><strong>Notifications & Subscriptions</strong></summary>

- Real-time notification model for: `follow`, `comment`, `reply`, `citation_dead`, `citation_drift`
- **Mark all read** in a single PATCH request
- **Newsletter subscriptions** — follow an author's feed
- **RSS feeds** (Atom 1.0) — per-author and global latest posts
- **XML Sitemap** for SEO (`/sitemap.xml`)

</details>

<details>
<summary><strong>Discovery & Search</strong></summary>

- **PostgreSQL full-text search** with `SearchVector` on title (weight A) + content (weight B)
- **Ranked results** via `SearchRank` with minimum relevance threshold
- **Tag filtering** by slug
- **Trending posts** — ranked by reactions + comments in last 30 days
- **Public feed** with Redis caching (30-second TTL on page 1)
- **OpenGraph metadata** endpoint per post slug

</details>

<details>
<summary><strong>Citations & Evidence</strong></summary>

- **Citations panel** — attach external URLs to posts as sourced evidence
- **Automated link health checks** (Celery Beat, daily 02:00 UTC)
  - Detects dead links (4xx / 5xx / timeouts)
  - Detects content drift (ETag / Last-Modified hash comparison)
  - Notifies post authors automatically

</details>

<details>
<summary><strong>Moderation</strong></summary>

- **Report posts and comments** with reason
- **Staff-only hide comment** endpoint
- **ModerationAuditLog** — immutable record of every staff action
- **Post reviews** — 1–5 star peer review system

</details>

<details>
<summary><strong>Security & Compliance</strong></summary>

- **SECRET_KEY** enforced via env var — raises `ImproperlyConfigured` if missing
- **ALLOWED_HOSTS** from env var — no `["*"]` in any environment
- **HSTS** (1 year + preload), **CSRF/session secure cookies** in production
- **CORS** controlled per-origin via `CORS_ALLOWED_ORIGINS`
- **Security headers** via Django + Nginx (`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`)
- **Rate limiting** per endpoint: register (10/min), comments (30/min), follows (20/min)
- **GDPR right to erasure** — `DELETE /api/auth/account/` permanently deletes all user data
- **GDPR data export** — `GET /api/auth/export/` returns all user data as JSON
- **IP hashing** for view counts (SHA-256, never store raw IPs)

</details>

<details>
<summary><strong>Observability</strong></summary>

- **Sentry** — automatic error capture + 10% transaction sampling (configurable)
- **Health check endpoint** — `GET /api/v1/health/` checks DB + Redis, returns 503 on degradation
- **Structured JSON logging** across all services
- **X-Request-ID** header propagated on every request + response for distributed tracing
- **Request duration** logged in milliseconds

</details>

---

## API Documentation

Interactive Swagger UI: `http://localhost:8000/api/v1/docs/`
OpenAPI schema: `http://localhost:8000/api/v1/schema/`

### Endpoint Summary

| Category | Count | Example |
|---|---|---|
| Auth | 6 | `POST /api/v1/token/`, `GET /api/v1/auth/me/` |
| Posts (CRUD) | 7 | `GET /api/v1/posts/`, `POST /api/v1/posts/{id}/upload-image/` |
| Public Feed | 5 | `GET /api/v1/public/posts/`, `GET /api/v1/public/posts/trending/` |
| Comments | 4 | `POST /api/v1/posts/{id}/comments/`, `PATCH /api/v1/comments/{id}/` |
| Social | 8 | `POST /api/v1/users/{id}/follow/`, `POST /api/v1/users/{id}/block/` |
| Citations | 5 | `POST /api/v1/posts/{id}/citations/`, `GET /api/v1/posts/{id}/evidence/` |
| Tags | 3 | `GET /api/v1/tags/`, `POST /api/v1/posts/{id}/tags/` |
| Series | 4 | `POST /api/v1/series/`, `POST /api/v1/series/{id}/posts/` |
| Notifications | 3 | `GET /api/v1/notifications/`, `PATCH /api/v1/notifications/mark-read/` |
| Moderation | 4 | `POST /api/v1/posts/{id}/report/`, `POST /api/v1/comments/{id}/hide/` |
| GDPR | 2 | `GET /api/auth/export/`, `DELETE /api/auth/account/` |
| Feeds & SEO | 3 | `GET /feed/`, `GET /sitemap.xml` |
| Infra | 1 | `GET /api/v1/health/` |

**Total: 55+ endpoints across 2 versioned URL namespaces (`/api/` and `/api/v1/`).**

---

## Testing

```bash
# Run full test suite with coverage (inside Docker)
docker compose run --rm web pytest -q

# Run in parallel (faster)
docker compose run --rm web pytest -n auto -q

# Run a specific test file
docker compose run --rm web pytest author/tests/test_data_export.py -v

# Coverage report only
docker compose run --rm web pytest --cov=author --cov-report=html
```

### Test Infrastructure

| Tool | Purpose |
|---|---|
| `pytest` + `pytest-django` | Test runner — cleaner fixtures, no `TestCase` boilerplate |
| `factory_boy` | Declarative test data factories (User, Post, Comment, Tag, …) |
| `pytest-cov` | Coverage measurement with XML output for CI upload |
| `pytest-xdist` | Parallel test execution (`-n auto`) |
| `conftest.py` | Shared fixtures: `auth_client`, `user`, `published_post`, etc. |

### Coverage

Minimum enforced: **75%** (`fail_under` in `.coveragerc`). The CI pipeline blocks merges below this threshold.

---

## Environment Variables

Copy `.env.example` → `.env` and fill in your values:

```bash
cp .env.example .env
```

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | **Yes** | Django secret key (50+ random chars) |
| `DEBUG` | No | `1` = dev mode, `0` = production (default) |
| `ALLOWED_HOSTS` | No | Comma-separated hostnames (default: `localhost,127.0.0.1`) |
| `POSTGRES_DB` | **Yes** | Database name |
| `POSTGRES_USER` | **Yes** | Database user |
| `POSTGRES_PASSWORD` | **Yes** | Database password |
| `DB_HOST` | No | DB hostname (default: `db`) |
| `REDIS_URL` | No | Redis connection URL (default: `redis://redis:6379/0`) |
| `CORS_ALLOWED_ORIGINS` | No | Comma-separated frontend origins |
| `SENTRY_DSN` | No | Sentry project DSN (blank = disabled) |
| `ENVIRONMENT` | No | `production` / `staging` / `development` |

---

## Docker Services

```bash
docker compose up --build        # Start everything
docker compose up web redis      # Start only web + Redis (skip Celery)
docker compose logs -f web       # Tail Django logs
docker compose exec web python manage.py shell
docker compose exec web python manage.py createsuperuser
docker compose down -v           # Stop + delete all volumes
```

| Service | Image | Role |
|---|---|---|
| `db` | `postgres:16` | Primary database with health check |
| `redis` | `redis:7-alpine` | Cache + Celery broker |
| `web` | Custom (python:3.12-slim) | Django + Gunicorn (4 workers) |
| `celery-worker` | Same as web | Async task consumer |
| `celery-beat` | Same as web | Periodic task scheduler |
| `nginx` | `nginx:alpine` | Reverse proxy + static/media serving |

---

## CI/CD Pipeline

Four jobs run on every push and pull request:

```
push/PR ──► lint ──► security ──► test ──► (parallel) docker-build
              │           │           │
           flake8      bandit      pytest
           black       safety      coverage
                                  codecov
```

| Job | What it checks |
|---|---|
| **lint** | `flake8` style + `black` formatting |
| **security** | `bandit` static analysis + `safety` CVE scan |
| **test** | Full pytest suite against a real DB + Redis; uploads to Codecov |
| **docker-build** | Verifies the production Docker image builds and passes `manage.py check --deploy` |

---

## Project Structure

```
blog-app-api/
├── app/
│   ├── core/
│   │   ├── celery.py           # Celery app + autodiscover
│   │   ├── settings.py         # All settings — env-driven, security hardened
│   │   ├── urls.py             # Root URL config
│   │   └── urls_v1.py          # /api/v1/ versioned routes
│   ├── author/
│   │   ├── models.py           # 17+ models (Post, Comment, Citation, Notification, …)
│   │   ├── serializers.py      # 15+ serializers with computed fields
│   │   ├── views.py            # 35+ class-based views
│   │   ├── tasks.py            # Celery tasks (link health, publish, email)
│   │   ├── middleware.py       # RequestIDMiddleware + timing
│   │   ├── throttles.py        # Per-endpoint rate limits
│   │   ├── feeds.py            # RSS / Atom feeds
│   │   ├── sitemaps.py         # XML sitemap
│   │   ├── management/
│   │   │   └── commands/       # check_link_health, publish_scheduled
│   │   └── tests/
│   │       ├── conftest.py     # pytest fixtures
│   │       ├── factories.py    # factory_boy factories
│   │       └── test_*.py       # 50+ test modules
│   ├── accounts/
│   │   └── models.py           # Custom User with unique handle
│   ├── pytest.ini              # pytest + coverage config
│   └── requirements.txt
├── docker/
│   └── nginx/default.conf      # Reverse proxy + security headers
├── .github/
│   └── workflows/ci.yml        # 4-job CI pipeline
├── .env.example                # Environment variable template
├── docker-compose.yml          # Full 6-service stack
└── Dockerfile                  # python:3.12-slim, non-root user
```

---

## Key Design Decisions

**Why PostgreSQL full-text search instead of Elasticsearch?**
Eliminates a separate service. PostgreSQL `SearchVector` + `SearchRank` handles the scale of a blog platform; Elasticsearch would be premature optimization.

**Why Celery Beat via `DatabaseScheduler` instead of cron?**
Periodic tasks are editable at runtime via Django admin without redeployment. Also survives container restarts without losing schedule state.

**Why `CONN_MAX_AGE=60`?**
Persistent database connections eliminate TCP handshake overhead on every request. Safe with Gunicorn since each worker maintains its own connection pool.

**Why `X-Request-ID` middleware?**
Enables end-to-end request tracing across Nginx logs, Django logs, Celery task logs, and Sentry — essential for debugging distributed systems.

---

<div align="center">

Built with Django 5.2 · PostgreSQL 16 · Redis 7 · Celery 5.4

</div>
