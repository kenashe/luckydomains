# URL_MAP.md

Every URL on luckydomains.io before and after the November 2026 redesign
(DECISIONS D12). No existing URL changes or disappears, so the launch needs no
redirects. The rules for URL shape are in `AGENTS.md` section 2.4.

## Existing URLs, all preserved

| URL before | URL after | Notes |
|---|---|---|
| `/` | `/` | Same file. New content |
| `/services/` | `/services/` | Now an overview of five services. The `#websites`, `#seo`, `#domains` and `#selling` anchors still exist, so old links through `services.html#seo` and similar keep working |
| `/services/entity-seo/` | `/services/entity-seo/` | Same URL. Now "Entity SEO & Digital Identity" |
| `/how-we-buy-domains/` | `/how-we-buy-domains/` | Same URL and same process |
| `/about/` | `/about/` | Same URL |
| `/founder/ken-ashe/` | `/founder/ken-ashe/` | Same URL. The design concept used `/founder/`; production keeps the live URL |
| `/contact/` | `/contact/` | Same URL, same form provider. `?need=` accepts `website`, `seo`, `ai`, `entity`, `buying`, `selling` |
| `/news/` | `/news/` | Same URL |
| `/news/website-relaunch/` | `/news/website-relaunch/` | Same URL. Headline, text, dates and `NewsArticle` data exactly as published. The shared header and footer changed, and the shared Organization record in its structured data is kept current, as the shared Person record already was |
| `/404.html` | `/404.html` | Updated, still `noindex` |

## Legacy redirect stubs, unchanged

These files are byte for byte what they were. They stay until Search Console
shows the `.html` URLs dropped (DECISIONS D11).

| Legacy URL | Redirects to |
|---|---|
| `/services.html` | `/services/` |
| `/about.html` | `/about/` |
| `/contact.html` | `/contact/` |
| `/how-we-buy-domains.html` | `/how-we-buy-domains/` |
| `/news/website-relaunch.html` | `/news/website-relaunch/` |

## New URLs

| URL | Page |
|---|---|
| `/services/website-design/` | Website Design & Development |
| `/services/seo/` | SEO & Search Visibility |
| `/services/ai-visibility/` | AI Visibility & Brand Authority |
| `/services/domain-acquisition/` | Domain Acquisition & Brokerage |
| `/tools/digital-presence-check/` | Digital Presence Check |
| `/insights/` | Insights article library |
| `/insights/what-ai-search-reads-on-your-website/` | What AI Search Reads When It Reads Your Website |
| `/insights/fix-or-rebuild-your-website/` | When to Fix a Website and When to Rebuild It |
| `/insights/entity-seo-for-founders/` | Entity SEO for Founders: One Name, Many Profiles |
| `/insights/how-a-private-domain-purchase-works/` | How a Private Domain Purchase Actually Works |
| `/insights/domains-identity-for-ai-agents/` | Can Domains Become the Identity Layer for AI Agents? |

There is deliberately no `/tools/` index page and no `/work/` or portfolio URL.

## What changed inside existing pages

- The home page section anchor `/#fit` no longer exists. A link to it lands at
  the top of the home page.
- Sitemap: every indexable page is listed. An Insights article is added when
  it is published, by `scripts/articles.py`. Drafts are not listed.
- Canonical tags, `og:url`, breadcrumbs and JSON-LD `@id` values all use the
  trailing slash form on `https://luckydomains.io`.

## Mapping from the design concept

The approved design lived in a separate review repository with its own paths.
Two differ in production.

| Design concept path | Production URL |
|---|---|
| `founder/` | `/founder/ken-ashe/` |
| `services/domains/` | `/services/domain-acquisition/` |
| every other path | the same path |
