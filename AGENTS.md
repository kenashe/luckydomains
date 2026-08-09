# AGENTS.md

Instructions and context for any coding agent working on this repository.

**Read this file first.** It contains the conventions, the guardrails, and the
traps that have already cost real downtime on this project. Everything you need
is in this repo. You do not need access to any prior conversation.

---

## 1. What this project is, in one paragraph

`luckydomains.io` is a four page marketing website for Lucky Domains, a business
that sells domain acquisition/brokerage and SEO services. It is hand written
static HTML, CSS and vanilla JavaScript with **no build step and no framework**.
It is hosted free on GitHub Pages, served from the `main` branch of
`kenashe/luckydomains`, on the apex custom domain `luckydomains.io`.

See `PRODUCT.md` for goals and scope, `ARCHITECTURE.md` for how it fits
together, `DECISIONS.md` for why it is built this way, and `docs/RUNBOOK.md` for
operational procedures.

---

## 2. Golden rules

These are not stylistic preferences. Breaking them has broken production before.

### 2.1 The repository must stay PUBLIC
GitHub Pages on the free plan **will not serve a private repository**. Making
this repo private silently unpublishes the site and `luckydomains.io` starts
returning 404. This has already happened once.

If it happens again: set the repo back to Public, then **re-enable Pages**
(Settings > Pages > Deploy from a branch > `main` > `/root`). Changing
visibility switches Pages off and it does **not** come back automatically.

There is no secret in this repo. The site's HTML, CSS, JS and images are served
publicly to every visitor anyway, so a public repo exposes nothing extra.

### 2.2 Never touch the MX or TXT DNS records
`luckydomains.io` runs live Google Workspace email (`info@luckydomains.io`).
The MX and TXT records at GoDaddy carry that email. Changing the website's A or
CNAME records is safe. Touching MX or TXT can take down the owner's email.
Exact record values are in `DATA_SOURCES.md`.

### 2.3 No em dashes, anywhere
The owner has an explicit style rule: **no em dashes (—) in any site copy,
comment, or committed file.** Use commas, colons, or separate sentences. The
test suite enforces this and CI will fail the build. En dashes (–) are also
disallowed in prose for the same reason.

### 2.4 One canonical URL form for every page
Every internal link must be **root absolute** and must exactly match that page's
`rel=canonical` and its `sitemap.xml` entry:

| Link to        | Correct                        | Wrong                                    |
|----------------|--------------------------------|------------------------------------------|
| Home           | `href="/"`                     | `index.html`, `/index.html`, `./index.html` |
| Services       | `href="/services.html"`        | `services.html`, `/services`             |
| About          | `href="/about.html"`           | `about.html`, `/about`                   |
| Contact        | `href="/contact.html"`         | `contact.html`, `/contact`               |
| News post      | `href="/news/website-relaunch.html"` | `news/website-relaunch.html`       |

Why this matters is explained in section 4.

### 2.5 Never block duplicate URLs in robots.txt
It is a common instinct and it backfires. A URL blocked in `robots.txt` cannot
be crawled, so Google never sees its `rel=canonical` tag and therefore cannot
consolidate it. Duplicates are handled with canonical tags, not with blocking.

### 2.6 Run the tests before you commit
```bash
python3 tests/test_site.py
```
No dependencies, no install step. CI runs the same command on every push.

---

## 3. How to work on this project

### Local development
```bash
git clone https://github.com/kenashe/luckydomains.git
cd luckydomains
python3 -m http.server 8000
# open http://localhost:8000
```
That is the entire toolchain. There is nothing to install, compile, or bundle.

Note that the local server serves `/services.html` but not `/services`, whereas
GitHub Pages serves both. Always link to the `.html` form (rule 2.4).

### Making a change
1. Edit the HTML/CSS/JS directly.
2. `python3 tests/test_site.py`
3. Commit and push to `main`.
4. GitHub Pages redeploys automatically, usually within a minute.

### Deployment
**The normal path is `git push` to `main`.** Pages serves the branch directly.
There is no pipeline to trigger and no build to run.

`scripts/deploy.py` exists only for agents that have an API token but no git
credentials. It is a convenience, not infrastructure. See `docs/RUNBOOK.md`.

---

## 4. Context you would otherwise have to rediscover painfully

### GitHub Pages cannot do redirects
There is no server side configuration, no `.htaccess`, no redirect rules. This
has three consequences:

1. **`www` to apex already works.** GitHub issues that 301 automatically because
   the custom domain is the apex. Do not try to build it yourself.
2. **`/` and `/index.html` both return 200** and cannot be redirected to one
   another, because they are literally the same file. The fix is `rel=canonical`
   plus never linking internally to `/index.html`. This is Google's documented
   approach for static hosts.
3. **Extensionless URLs also resolve.** GitHub Pages serves `/services` as well
   as `/services.html`. Both return 200. Canonical tags point at the `.html`
   form, so Google consolidates them. Keep internal links on `.html`.

### The site was migrated off Wix in June 2026
Wix had connected the domain through GoDaddy's Domain Connect, which **locked**
the A and CNAME records so they could not be edited or deleted from the GoDaddy
DNS panel, even after disconnecting on the Wix side. GoDaddy support had to
remove the orphaned managed records manually. If you ever see greyed out
trash/pencil icons on a DNS record at GoDaddy, that is what you are looking at.

### The deploy token expires
The fine grained personal access token used by `scripts/deploy.py` defaults to
30 day expiry. A `401 Bad credentials` from any API call means it lapsed. This
is expected and is not a code fault. Rotation steps are in `docs/RUNBOOK.md`.

### Deploying to an empty repository
The Git Data API cannot create blobs in a repository with zero commits. It
returns `409 Git Repository is empty`. `scripts/deploy.py` handles this by
creating a bootstrap commit through the Contents API first.

---

## 5. Verification checklist

After any change that touches links, metadata, or deployment, confirm:

```bash
# 1. Tests pass
python3 tests/test_site.py

# 2. The live site serves and returns real content
curl -sS -o /dev/null -w "%{http_code}\n" https://luckydomains.io/

# 3. www still redirects to the apex
curl -sS -o /dev/null -D - https://www.luckydomains.io/ | grep -i "^location"

# 4. Email DNS is untouched
python3 scripts/verify_live.py
```

`scripts/verify_live.py` runs all of the above plus DNS and canonical checks in
one pass. Run it after every deployment.

---

## 6. Known content debt

Do not treat the current site copy as final or verified.

- **The three homepage testimonials are fabricated.** "Rachel M.", "David K."
  and "Alicia T." were placeholders generated during the original build and were
  never replaced. They are live on a commercial site, which is a credibility
  problem and runs against FTC endorsement rules. They should be replaced with
  real client quotes or removed. Flag this to the owner; do not quietly keep
  shipping them.
- **Pricing tiers have no figures.** The Services page shows tier structure with
  "Project", "Monthly" and "Custom" instead of prices, pending the owner's input.
- **Email authentication is incomplete.** SPF is correct, but DKIM and DMARC are
  missing. See `DATA_SOURCES.md`.

---

## 7. House style

- **Voice:** confident, plain spoken, no jargon, no hype. Short sentences.
- **Punctuation:** no em dashes (rule 2.3).
- **Contact details:** `info@luckydomains.io` only. No phone number, no business
  hours, no social media links. This is deliberate; do not add them back.
- **Brand colours:** green `#16C784`, darker green `#0FA968` for text contrast,
  deep navy `#0C2340`, mint `#ECFBF4`.
- **Fonts:** Plus Jakarta Sans for headings, Inter for body, loaded from Google
  Fonts.
- **Accessibility:** keep the skip link, the `aria-label`s, the focus styles and
  the `prefers-reduced-motion` block in `css/styles.css`.
- **Images:** always set `width` and `height` to protect layout stability, and
  add `loading="lazy"` to anything below the fold.

---

## 8. Do not introduce

- A framework, bundler, or package manager. See `DECISIONS.md` for why.
- A dependency on any single AI development tool or platform. This repository is
  the source of truth and must stay usable with git and a text editor alone.
- Server side code. There is no server. The only dynamic behaviour is the
  contact form, which posts to a third party API from the browser.
- Tracking or analytics without asking the owner first.
