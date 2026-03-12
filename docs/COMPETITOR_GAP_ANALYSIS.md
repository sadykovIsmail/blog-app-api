# Competitor Gap Analysis (High Level)

This is not an exhaustive list of every blogging product; it focuses on widely-used platforms that set user expectations.

## Platforms Considered

- Medium (social reading + distribution)
- Substack (newsletter + subscriptions + community)
- Ghost (open-source publishing + memberships)
- WordPress (ecosystem + plugins, self-host and hosted)

## Common Strengths (Most Have These)

- Publishing workflow: draft/publish, editor, media
- Engagement: followers/subscribers, comments/responses, likes/reactions (varies)
- Discovery: tags/topics, recommendation feeds (varies), SEO
- Monetization: subscriptions/memberships (Substack/Ghost; WordPress via plugins)

## Common Gaps (Where Most Apps Are Weak)

- Evidence is informal: links are unstructured, credibility is unclear, and there is no claim-to-source mapping.
- Link rot: sources disappear or change; posts lose trust over time; authors rarely get alerted.
- Revision transparency: edits are not first-class and changelogs are uncommon.
- Review workflow: no lightweight peer review for technical posts, no structured feedback loop.

## Differentiator: Proof-First Trust Layer For Technical Blogging

Build features that make readers say: "I trust this platform more for technical topics."

- Structured citations: URL + publisher + published/accessed dates + canonical URL.
- Evidence Panel: show citation health and snapshot status per post.
- Source snapshots: store content hash + extracted text (optional); detect drift and dead links.
- Claims: optional author-highlighted claims with required citations.
- Reviews: request review, structured feedback, rating, and reviewer identity.
- Linting: broken-link checks + markdownlint-style rules + readability heuristics.
- Transparency: post versions + reason-for-change, with reader-visible changelog.

## MVP That People Actually Use

- Public feed of published posts (search, ordering, pagination)
- Profiles + follows + notifications
- Comments + reactions + reports/moderation
- Citations + evidence panel + versions
