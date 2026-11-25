# Lucky Domains

Marketing website for **Lucky Domains**, a digital presence studio for the AI
era. Lucky Domains helps businesses build a digital presence that people,
search engines, and AI systems can find, understand, and trust: website design
and development, SEO, AI visibility, digital identity, and domain acquisition
and brokerage.

**Live site:** https://luckydomains.io
**Hosting:** GitHub Pages, served from the `main` branch of this repository
**Stack:** hand written static HTML, CSS, and vanilla JavaScript. No build step.

> **Working on this with a coding agent?** Read [`AGENTS.md`](AGENTS.md) first.
> It contains the conventions and the production traps that are easy to trip.

---

## Contents

| Document | Purpose |
|---|---|
| [`AGENTS.md`](AGENTS.md) | Instructions, conventions and guardrails for coding agents |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | How the site, hosting, DNS and integrations fit together |
| [`PRODUCT.md`](PRODUCT.md) | Product goals, audience, scope, brand and UX principles |
| [`DECISIONS.md`](DECISIONS.md) | Significant decisions and the reasoning behind them |
| [`DATA_SOURCES.md`](DATA_SOURCES.md) | External services, APIs, DNS records, limits and fallbacks |
| [`docs/RUNBOOK.md`](docs/RUNBOOK.md) | Deployment, staging review, launch checklist, rollback, DNS, incident recovery |
| [`docs/INSIGHTS.md`](docs/INSIGHTS.md) | How Insights articles are researched, written, approved and published |
| [`docs/URL_MAP.md`](docs/URL_MAP.md) | Every URL before and after the November 2026 redesign |
| [`.env.example`](.env.example) | Environment variables required by the tooling |

---

## Quick start

```bash
git clone https://github.com/kenashe/luckydomains.git
cd luckydomains
python3 -m http.server 8000
```

Open http://localhost:8000. That is the entire toolchain: no install, no
compile, no bundler. Python 3 is used only to serve static files; any static
file server works equally well.

One difference from production: the local server serves `/services/` but not
the extensionless `/services`, whereas GitHub Pages serves both. Always link to
the trailing slash form, for example `/services/`.

---

## Repository layout

```
.
├── index.html               Home
├── services/
│   ├── index.html           The five services and engagements
│   ├── website-design/      Website Design & Development
│   ├── seo/                 SEO & Search Visibility
│   ├── ai-visibility/       AI Visibility & Brand Authority
│   ├── entity-seo/          Entity SEO & Digital Identity
│   └── domain-acquisition/  Domain Acquisition & Brokerage
├── how-we-buy-domains/      The acquisition process
├── tools/
│   └── digital-presence-check/   Free self-check, runs in the browser
├── insights/
│   ├── index.html           Article library
│   └── <slug>/index.html    One article each
├── about/index.html         Company story
├── founder/ken-ashe/        Founder profile page
├── contact/index.html       Contact form
├── news/
│   ├── index.html           News index
│   └── website-relaunch/    June 2026 press release (legacy .html stub alongside)
├── *.html (services, about, contact, how-we-buy-domains)
│                            Legacy noindex redirect stubs, see DECISIONS D11
├── 404.html                 Not found page (served by GitHub Pages)
├── css/styles.css           All styles, single stylesheet
├── js/main.js               Navigation, presence map, diagnostic, presence check, contact form
├── assets/                  Images, favicons, social share image
│   ├── fonts/               Self hosted Plus Jakarta Sans and Inter (DECISIONS D13)
│   └── source/              Original brand files, used to regenerate assets
├── scripts/                 Maintenance and deployment tooling
│   ├── articles.py          Keep Insights articles, the library and the sitemap in sync
│   ├── templates/article.html   The article page layout used by articles.py
│   ├── deploy.py            Push the site via the GitHub API (agents without git)
│   ├── make_assets.py       Regenerate favicons and social image from source
│   └── verify_live.py       Post deployment verification of the live site
├── tests/test_site.py       Dependency free test suite
├── docs/                    Runbook, Insights instructions, URL map
├── .github/workflows/ci.yml Runs the tests on every push and pull request
├── CNAME                    Custom domain for GitHub Pages (luckydomains.io)
├── .nojekyll                Serve files as is, skip Jekyll processing
├── robots.txt               Crawl directives
├── sitemap.xml              All indexable URLs
└── site.webmanifest         PWA manifest / icons
```

There is **no database, no server side code, no cron job and no webhook** in
this project. If a task seems to require one, see `ARCHITECTURE.md` section
"What this project deliberately does not have" before adding it.

---

## Development

### Making a change
1. Edit the HTML, CSS or JS directly.
2. Run the tests: `python3 tests/test_site.py`
3. Commit and push to `main`.

### Adding an Insights article
```bash
python3 scripts/articles.py new my-article-slug "The article title"
# write the article in insights/my-article-slug/index.html, then:
python3 scripts/articles.py sync
python3 tests/test_site.py
```
The article is a draft (noindex, not in the sitemap) until the owner approves
it and a publication date is set with `articles.py publish`. The full
procedure is in [`docs/INSIGHTS.md`](docs/INSIGHTS.md).

### Regenerating brand assets
Favicons, the app icons and the Open Graph image are generated from the files in
`assets/source/`:

```bash
python3 -m pip install Pillow      # only dependency, only for this script
python3 scripts/make_assets.py
```

You only need this if the logo changes. The generated assets are committed, so
normal work never runs it.

---

## Testing

```bash
python3 tests/test_site.py
```

Pure standard library, no packages to install. The suite checks the things that
have actually broken on this project:

- every page has a `rel=canonical` that matches its `sitemap.xml` entry
- no internal link points at a duplicate URL form such as `/index.html`
- every internal link resolves to a file that exists
- required meta tags, Open Graph tags and structured data are present
- no leftover placeholder tokens (for example an unconfigured form key)
- no em dashes, which is a house style rule
- `CNAME`, `robots.txt` and `sitemap.xml` are internally consistent
- the header and footer are identical on every page
- titles and descriptions are unique, and structured data is valid JSON
- Insights articles are in sync, and a draft never carries a publication date
- the Digital Presence Check stores and sends nothing
- owner decisions hold: no portfolio, no monthly SEO package, no guarantees

Before a production launch, run `python3 tests/test_site.py --launch`. It also
fails while any Insights article is still a draft.

CI runs the identical command on every push and pull request.

---

## Deployment

**Push to `main`.** GitHub Pages serves the branch directly and redeploys within
about a minute. There is no pipeline to trigger and nothing to build.

```bash
git add -A && git commit -m "Describe the change" && git push origin main
```

Two constraints that matter:

- **The repository must stay public.** GitHub Pages on the free plan will not
  serve a private repo. Making it private silently takes the site offline.
- **`CNAME` must keep containing `luckydomains.io`.** Deleting it drops the
  custom domain.

For agents that have a GitHub API token but no git credentials, `scripts/deploy.py`
publishes over the REST API instead. It is a convenience, not infrastructure.
Full procedures, DNS records and recovery steps are in [`docs/RUNBOOK.md`](docs/RUNBOOK.md).

After deploying:

```bash
python3 scripts/verify_live.py
```

---

## Ownership and contacts

- **Owner:** Ken Ashe, founder of Lucky Domains
- **Contact:** info@luckydomains.io
- **Registrar and DNS:** GoDaddy
- **Email:** Google Workspace
- **Contact form delivery:** Web3Forms

Credentials are never stored in this repository. See [`.env.example`](.env.example).
