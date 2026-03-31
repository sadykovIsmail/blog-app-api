"""
Management command: create_demo_data

Creates 3 demo users and 12 published posts so the app has content
to browse immediately after `docker compose up`.

Usage:
    python manage.py create_demo_data
    python manage.py create_demo_data --reset   # wipe and recreate
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from author.models import AuthorModel, BlogPostModel, Tag

User = get_user_model()

DEMO_USERS = [
    {
        "username": "alice",
        "email": "alice@example.com",
        "password": "Demo1234!",
        "handle": "alice",
        "name": "Alice Johnson",
        "is_staff": False,
    },
    {
        "username": "bob",
        "email": "bob@example.com",
        "password": "Demo1234!",
        "handle": "bob",
        "name": "Bob Smith",
        "is_staff": False,
    },
    {
        "username": "admin",
        "email": "admin@example.com",
        "password": "Admin1234!",
        "handle": "admin",
        "name": "Admin User",
        "is_staff": True,
        "is_superuser": True,
    },
]

TAGS = ["python", "django", "javascript", "webdev", "tutorial", "ai", "devops", "ux"]

POSTS = [
    {
        "author_handle": "alice",
        "title": "Getting Started with Django REST Framework",
        "content": """Django REST Framework (DRF) is one of the most powerful tools in a Python developer's arsenal. Whether you're building a simple API for a mobile app or a complex microservice, DRF makes it surprisingly straightforward.

## Why DRF?

DRF gives you a clean, consistent way to expose your Django models as JSON endpoints. Serializers handle validation and conversion, ViewSets reduce boilerplate to near zero, and the browsable API makes debugging a joy.

## Your first serializer

```python
from rest_framework import serializers
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'created_at']
```

## Authentication

JWT authentication with `djangorestframework-simplejwt` is the modern default. Add it to your settings and you get `/api/token/` and `/api/token/refresh/` out of the box.

## Pagination

Always paginate. Your API will thank you at scale. DRF's `PageNumberPagination` is two lines of config.

Start small, ship fast, iterate.""",
        "tags": ["python", "django", "tutorial"],
    },
    {
        "author_handle": "alice",
        "title": "JWT Authentication: Access Tokens vs Refresh Tokens",
        "content": """If you've worked with modern APIs you've encountered JWT. But the split between access tokens and refresh tokens trips up a lot of developers. Let me clarify.

## Access tokens

Short-lived (15 minutes is common). Sent with every API request in the `Authorization: Bearer <token>` header. If stolen, they expire quickly.

## Refresh tokens

Long-lived (7–30 days). Stored securely (httpOnly cookie or localStorage). Used *only* to obtain a new access token. Never sent to your regular API endpoints.

## The flow

1. User logs in → server returns both tokens
2. Client uses access token for API calls
3. Access token expires → client sends refresh token to `/api/token/refresh/`
4. Server validates refresh token → returns new access token
5. If refresh token is invalid/expired → force logout

## Storage decisions

- Access token in memory (not localStorage) — can't be stolen by XSS
- Refresh token in httpOnly cookie — can't be read by JavaScript

This is the pattern used in this blog app's frontend.""",
        "tags": ["python", "webdev", "tutorial"],
    },
    {
        "author_handle": "alice",
        "title": "Celery + Redis: Async Tasks the Right Way",
        "content": """Background tasks are one of those things that seem optional until your users start complaining that sending an email takes 4 seconds. Here's how to do it properly.

## The stack

- **Celery** — Python task queue
- **Redis** — message broker (and result backend)
- **django-celery-beat** — periodic tasks stored in DB, configurable via admin

## Basic task

```python
from celery import shared_task

@shared_task(bind=True, max_retries=3)
def send_welcome_email(self, user_id: int):
    try:
        user = User.objects.get(id=user_id)
        # send email...
    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)
```

## Calling it

```python
send_welcome_email.delay(user.id)  # fire and forget
```

## Scheduled tasks

Use `CELERY_BEAT_SCHEDULE` in settings to define cron-like jobs. The `DatabaseScheduler` lets you modify schedules at runtime through Django admin.

## Production tip

Always set `--worker-tmp-dir /dev/shm` on Gunicorn when running in Docker to avoid Permission denied errors on the control socket.""",
        "tags": ["python", "devops", "tutorial"],
    },
    {
        "author_handle": "bob",
        "title": "Next.js 14 App Router: What Actually Changed",
        "content": """The App Router in Next.js 13/14 is a complete rethink of how you structure a React application. After building several projects with it, here's my honest assessment.

## Server Components by default

This is the big one. Components render on the server unless you add `"use client"`. The benefit: zero JavaScript sent to the browser for static content. The gotcha: you can't use hooks, browser APIs, or event handlers in server components.

## File-based routing is now folder-based

```
app/
  page.tsx        → /
  about/
    page.tsx      → /about
  posts/
    [slug]/
      page.tsx    → /posts/:slug
```

## Layout nesting

Each folder can have a `layout.tsx` that wraps its children. Layouts persist across navigations — no re-render. This is great for things like sidebars and navigation.

## When to use `"use client"`

- Event handlers (onClick, onChange)
- React hooks (useState, useEffect, useContext)
- Browser APIs (localStorage, window)

Everything else: keep it server.

## Data fetching

Fetch directly in async server components. No need for useEffect or SWR for initial data:

```tsx
export default async function PostsPage() {
  const posts = await fetch('https://api.example.com/posts').then(r => r.json());
  return <PostList posts={posts} />;
}
```

The mental model shift is worth it. Your apps will be faster.""",
        "tags": ["javascript", "webdev"],
    },
    {
        "author_handle": "bob",
        "title": "Docker Compose: From Zero to Production-Ready",
        "content": """Most tutorials show you a docker-compose.yml with two services and call it done. Here's what a real production-ready setup looks like.

## Health checks everywhere

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
  interval: 5s
  retries: 5
```

Use `condition: service_healthy` in `depends_on` so services only start when their dependencies are truly ready — not just started.

## Named volumes for databases

```yaml
volumes:
  postgres_data:
  redis_data:
```

Never use bind mounts for database data in production. Named volumes are managed by Docker and survive container recreation.

## Separate concerns

Don't put your web server, task worker, and scheduler in the same container. Each should be its own service:

- `web` — Gunicorn/uvicorn
- `celery-worker` — task processing
- `celery-beat` — scheduled tasks
- `nginx` — static files + reverse proxy

## Environment variables

Never hardcode secrets. Use `.env` files with `env_file:` directive, and validate in your app that required vars are set (raise `ImproperlyConfigured` if not).

## Resource limits

In production, always set `mem_limit` and `cpus` on each service. Runaway tasks can kill your whole host otherwise.""",
        "tags": ["devops", "tutorial"],
    },
    {
        "author_handle": "bob",
        "title": "Why Your API Needs Rate Limiting Yesterday",
        "content": """Rate limiting is one of those defensive measures that feels unnecessary until the moment a bot hammers your signup endpoint 10,000 times in a minute.

## What to limit

- Authentication endpoints (login, register, password reset) — critical
- Write endpoints (POST, PUT, PATCH, DELETE) — important
- Read endpoints — optional unless you have expensive queries

## Django implementation

`djangorestframework` has basic throttling built in:

```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    }
}
```

## Nginx layer limiting

Add rate limiting at the Nginx layer too — it's cheaper than hitting Django:

```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req zone=api burst=20 nodelay;
```

## Redis-backed throttling

For distributed setups (multiple app servers), use Redis-backed throttling so limits apply globally, not per-server.

Defense in depth: limit at Nginx, limit at Django, monitor anomalies with Sentry.""",
        "tags": ["webdev", "devops"],
    },
    {
        "author_handle": "alice",
        "title": "PostgreSQL Indexing: The Queries Your ORM Hides",
        "content": """Django's ORM is a gift — until it generates a sequential scan on a table with 2 million rows and your response time goes from 50ms to 12 seconds.

## EXPLAIN ANALYZE is your best friend

```sql
EXPLAIN ANALYZE
SELECT * FROM author_blogpostmodel
WHERE status = 'PUBLISHED' AND visibility = 'PUBLIC'
ORDER BY published_at DESC
LIMIT 20;
```

Look for `Seq Scan` on large tables — that's your target.

## Composite indexes match your queries

```python
class Meta:
    indexes = [
        models.Index(fields=['status', 'visibility']),
        models.Index(fields=['-published_at']),
    ]
```

The order in `fields` matters. `(status, visibility)` helps queries that filter on both. A query filtering only on `visibility` won't use it.

## select_related and prefetch_related

N+1 queries kill performance silently. Always use `select_related` for FK traversals and `prefetch_related` for M2M in list views.

```python
BlogPostModel.objects.select_related('user', 'author').prefetch_related('tags')
```

## Django Debug Toolbar

Install it in development. Every page shows you exactly how many queries ran and how long they took. It will horrify you the first time.""",
        "tags": ["python", "django"],
    },
    {
        "author_handle": "bob",
        "title": "Designing APIs That Don't Make Developers Cry",
        "content": """A well-designed API is a joy. A poorly designed one generates support tickets at 2am. Here's what separates them.

## Consistent naming

Pick a convention and stick to it. `snake_case` for JSON fields. Plural nouns for resources (`/posts/`, not `/post/`). No verbs in URLs (that's what HTTP methods are for).

## Meaningful status codes

- `200 OK` — success with body
- `201 Created` — resource created (include `Location` header)
- `204 No Content` — success without body (DELETE, mark-read)
- `400 Bad Request` — client error, include validation details
- `401 Unauthorized` — not authenticated
- `403 Forbidden` — authenticated but not allowed
- `404 Not Found` — resource doesn't exist
- `409 Conflict` — state conflict (already following, already bookmarked)
- `422 Unprocessable Entity` — semantic validation failure

## Error responses

Always return structured errors:

```json
{
  "detail": "No active account found with the given credentials"
}
```

or for field errors:

```json
{
  "username": ["This field is required."],
  "email": ["Enter a valid email address."]
}
```

## Pagination

Always. Return `count`, `next`, `previous`, and `results`. Never return unbounded lists.

## Versioning

Prefix from day one: `/api/v1/`. Changing it later is painful.""",
        "tags": ["webdev", "ux"],
    },
    {
        "author_handle": "alice",
        "title": "pytest vs unittest: Why pytest Wins Every Time",
        "content": """I've written Django tests with both `unittest.TestCase` and `pytest`. Here's why I'll never go back.

## Less boilerplate

unittest:
```python
class MyTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(...)

    def test_something(self):
        self.assertEqual(result, expected)
```

pytest:
```python
def test_something(user):  # user is a fixture
    assert result == expected
```

## Fixtures compose

pytest fixtures are dependency-injected functions. They compose naturally:

```python
@pytest.fixture
def auth_client(client, user):
    client.force_authenticate(user=user)
    return client
```

## Parametrize

```python
@pytest.mark.parametrize("status,expected", [
    ("DRAFT", 0),
    ("PUBLISHED", 1),
])
def test_visibility(status, expected, published_post):
    ...
```

## factory_boy integration

`factory_boy` + pytest fixtures = test data that's clean, composable, and readable.

```python
@pytest.fixture
def post(user):
    return PostFactory(user=user, status="PUBLISHED")
```

## Coverage

`pytest-cov` gives you coverage in one flag: `--cov=myapp`. Set `fail_under = 80` in `.coveragerc` and CI will enforce it.""",
        "tags": ["python", "tutorial"],
    },
    {
        "author_handle": "bob",
        "title": "GitHub Actions CI That Actually Catches Bugs",
        "content": """Most CI pipelines run tests and call it done. Here's a 4-job pipeline that catches real problems.

## Job 1: Lint

```yaml
- run: flake8 app/ --max-line-length=100
- run: black --check app/
```

Enforce style automatically. No more "fix formatting" commits.

## Job 2: Security scan

```yaml
- run: bandit -r app/ -ll
- run: safety check
```

`bandit` catches common Python security issues (hardcoded passwords, use of `eval`, SQL injection patterns). `safety` checks your dependencies against known CVE databases.

## Job 3: Tests with coverage

```yaml
- run: pytest --cov=author --cov=core --cov-report=xml -q
- uses: codecov/codecov-action@v4
```

Upload to Codecov for trend tracking. Set `fail_under = 80` so coverage regressions break CI.

## Job 4: Docker build

```yaml
- run: docker build -t blog-app .
- run: docker compose run --rm web python manage.py check --deploy
```

`manage.py check --deploy` runs Django's production readiness checks. Catches things like missing `SECRET_KEY`, `DEBUG=True`, and weak `ALLOWED_HOSTS`.

## Concurrency cancellation

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

Cancels old runs when you push a new commit. Saves minutes and money.""",
        "tags": ["devops", "tutorial"],
    },
    {
        "author_handle": "alice",
        "title": "GDPR for Developers: What You Actually Need to Build",
        "content": """GDPR compliance sounds terrifying. In practice, for a web app, it boils down to a handful of concrete features.

## Right of access (Article 15)

Users can request all data you hold about them. Build a data export endpoint:

```
GET /api/auth/export/
```

Return a JSON blob with their profile, posts, comments, bookmarks, and follow relationships. ZIP it if it's large.

## Right to erasure (Article 17)

Users can delete their account and all associated data. Build a delete endpoint:

```
DELETE /api/auth/account/
```

Django's `CASCADE` deletes handle most of this automatically. Double-check: logs, analytics, email lists, S3 uploads.

## Data minimization (Article 5)

Only collect what you need. Don't ask for phone numbers if you're not calling anyone.

## Consent

Be explicit. "By signing up you agree to our Terms of Service" is the minimum. Don't pre-tick marketing opt-ins.

## Storage limitation

Don't keep data forever. Add `created_at` to everything and build a cleanup job for stale data (inactive accounts, expired tokens, old logs).

## Breach notification

You have 72 hours to notify authorities of a data breach. Have a plan. Sentry + a documented incident response process is a start.

GDPR isn't a legal problem — it's an engineering problem with a legal deadline.""",
        "tags": ["webdev", "tutorial"],
    },
    {
        "author_handle": "bob",
        "title": "AI-Assisted Code Review: What Works and What Doesn't",
        "content": """I've spent six months using AI tools in my code review workflow. Here's an honest breakdown.

## What AI is genuinely good at

**Catching obvious bugs**: null pointer dereferences, off-by-one errors, missing await keywords, incorrect regex.

**Documentation**: "What does this function do?" is almost always answered well.

**Boilerplate generation**: Tests, serializers, CRUD endpoints. Fast and mostly correct.

**Explaining unfamiliar code**: Drop in a 200-line function and ask for a summary. Saves 20 minutes of reading.

## Where AI falls short

**Business logic**: AI doesn't know your domain. It can't tell you if a discount calculation is wrong for your pricing model.

**Architecture decisions**: "Should this be a separate service?" requires context AI doesn't have.

**Security edge cases**: AI often misses subtle auth bugs, race conditions, and injection vectors that require adversarial thinking.

**Performance**: AI suggests correct code, not optimal code. It won't notice that your query runs in O(n²).

## My workflow

1. AI for initial review pass (5 min)
2. Human reviewer for business logic and architecture (20 min)
3. Security review for auth/data access changes (manual, always)

AI is a junior reviewer who's very fast and never tired. Use it accordingly.""",
        "tags": ["ai", "webdev"],
    },
]


class Command(BaseCommand):
    help = "Create demo users and posts for local development and testing."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing demo data before creating new data.",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            handles = [u["handle"] for u in DEMO_USERS]
            deleted, _ = User.objects.filter(handle__in=handles).delete()
            self.stdout.write(self.style.WARNING(f"Deleted {deleted} existing demo records."))

        # Tags
        tags_map = {}
        for tag_name in TAGS:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            tags_map[tag_name] = tag
        self.stdout.write(f"  Tags ready: {', '.join(TAGS)}")

        # Users + AuthorModel
        authors_map = {}
        for u in DEMO_USERS:
            if User.objects.filter(handle=u["handle"]).exists():
                self.stdout.write(f"  Skipping existing user: {u['handle']}")
                user = User.objects.get(handle=u["handle"])
            else:
                user = User.objects.create_user(
                    username=u["username"],
                    email=u["email"],
                    password=u["password"],
                    handle=u["handle"],
                    is_staff=u.get("is_staff", False),
                    is_superuser=u.get("is_superuser", False),
                )
                self.stdout.write(f"  Created user: @{u['handle']} / password: {u['password']}")

            author, _ = AuthorModel.objects.get_or_create(
                user=user,
                defaults={"name": u["name"], "email": u["email"]},
            )
            authors_map[u["handle"]] = (user, author)

        # Posts
        created_count = 0
        for p in POSTS:
            user, author = authors_map[p["author_handle"]]
            if BlogPostModel.objects.filter(title=p["title"]).exists():
                continue

            post = BlogPostModel.objects.create(
                title=p["title"],
                content=p["content"],
                author=author,
                user=user,
                status=BlogPostModel.Status.PUBLISHED,
                visibility=BlogPostModel.Visibility.PUBLIC,
                published_at=timezone.now(),
            )
            post.tags.set([tags_map[t] for t in p["tags"]])
            created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nDemo data ready! Created {created_count} post(s).\n"
            f"\n  Login credentials:"
            f"\n  alice / Demo1234!   (regular user)"
            f"\n  bob   / Demo1234!   (regular user)"
            f"\n  admin / Admin1234!  (staff + superuser)"
            f"\n\n  Admin panel: http://localhost:8000/admin/"
        ))
