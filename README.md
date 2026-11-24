# Lucky Domains

Company website for **Lucky Domains**, a founder-led digital venture studio and
operating company. Lucky Domains builds and operates AI applications, digital
identity systems, and internet-native ventures. Domain acquisition and brokerage
remain an active commercial service.

The site presents the ventures, experiments, and internal systems the company
builds and runs, the domain brokerage practice, and the founder. Full build
records live on [KenAshe.ai](https://kenashe.ai/), the founder's build-in-public
site. This repository is the company site only.

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
| [`docs/RUNBOOK.md`](docs/RUNBOOK.md) | Deployment, DNS, certificates, incident recovery |
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
the `.html` form.

---

## Repository layout

```
.
├── index.html                    Home: hero, operating status, featured venture, Domain Desk
├── ventures/index.html           Portfolio, grouped by type
├── ventures/zerohuman/           ZeroHuman (venture)
├── ventures/ai-agent-economy/    AI Agent Economy (experiment)
├── ventures/autonomous-seo-agent/  Autonomous SEO Agent (internal system)
├── services/index.html           Domain acquisition and brokerage, identity, selected engagements
├── services/entity-seo/          Entity SEO detail page
├── how-we-buy-domains/           How a private domain buy works
├── about/index.html              Company story and operating model
├── founder/ken-ashe/             Founder profile
├── news/index.html               Newsroom
├── news/website-relaunch/        June 2026 press release, kept as published
├── contact/index.html            Contact paths and the contact form
├── *.html (services, about, contact, how-we-buy-domains, news/website-relaunch)
│                                 Legacy noindex redirect stubs, see DECISIONS D11
├── 404.html                      Not found page (served by GitHub Pages)
├── css/styles.css                All styles, single stylesheet
├── js/main.js                    Navigation, motion, FAQ accordion, contact form
├── assets/                       Images, favicons, social share image
│   ├── fonts/                    Self hosted webfonts (SIL Open Font License)
│   └── source/                   Original brand files, used to regenerate assets
├── scripts/                      Maintenance and deployment tooling
│   ├── deploy.py                 Push the site via the GitHub API (agents without git)
│   ├── make_assets.py            Regenerate favicons, social image, reversed logo
│   └── verify_live.py            Post deployment verification of the live site
├── tests/test_site.py            Dependency free test suite
├── docs/RUNBOOK.md               Operational procedures, staging and cutover
├── docs/VENTURE_LAB_MIGRATION.md Record of the November 2026 redesign migration
├── .github/workflows/ci.yml      Runs the tests on every push and pull request
├── CNAME                         Custom domain for GitHub Pages (luckydomains.io)
├── .nojekyll                     Serve files as is, skip Jekyll processing
├── robots.txt                    Crawl directives
├── sitemap.xml                   All indexable URLs
└── site.webmanifest              PWA manifest / icons
```

There is **no database, no server side code, no cron job and no webhook** in
this project. If a task seems to require one, see `ARCHITECTURE.md` section
"What this project deliberately does not have" before adding it.

### Design system in one paragraph

Dark graphite pages, warm off-white text, and the logo green as the single
accent. The Domain Desk (home and Services) is the one warm light section and
carries the original full-color logo. Bricolage Grotesque for headings, Inter
for reading, JetBrains Mono for metadata only. Every portfolio record shows a
type and a status. Motion is limited to the hero, the featured venture, and a
scroll-linked progression line, and all of it stops under reduced motion. See
`PRODUCT.md` section 5 and `DECISIONS.md` D13.

---

## Development

### Making a change
1. Edit the HTML, CSS or JS directly.
2. Run the tests: `python3 tests/test_site.py`
3. Commit and push to `main`.

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

The suite also guards the November 2026 redesign: production pages must be
indexable, carry no staging or design-review text, keep the shared Person schema
identical, load no third party resource, show a type and a status on every
portfolio record, and keep the ZeroHuman limitation and the Domain Desk visible.
Browser checks (accessibility, responsive, reduced motion) are described in
`docs/RUNBOOK.md` section 8.

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
