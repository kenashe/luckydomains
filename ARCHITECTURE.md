# ARCHITECTURE.md

How the Lucky Domains website is put together, what it depends on, and how data
moves through it.

---

## 1. System overview

```
                    ┌──────────────────────────┐
   Visitor ────────>│  luckydomains.io (HTTPS) │
                    └────────────┬─────────────┘
                                 │ DNS: GoDaddy (ns05/ns06.domaincontrol.com)
                                 │ apex A records -> 4 GitHub Pages IPs
                                 │ www CNAME      -> kenashe.github.io (301 to apex)
                                 v
                    ┌──────────────────────────┐
                    │      GitHub Pages        │  static file server, TLS by
                    │  kenashe/luckydomains    │  Let's Encrypt, CDN fronted
                    │      branch: main        │
                    └────────────┬─────────────┘
                                 │ serves HTML/CSS/JS/images as is (.nojekyll)
                                 v
                    ┌──────────────────────────┐
                    │   Browser renders page   │
                    └────────┬─────────┬───────┘
                             │         │
                                       └─> Web3Forms API
              (no third party request      (contact form POST,
               on a normal page view)       only on submit)
                                                   │
                                                   v
                                           info@luckydomains.io
                                           (Google Workspace)
```

The site is **entirely static**. There is no application server, no database,
no session state and no server side rendering. Every page is a complete HTML
document committed to the repository.

---

## 2. Hosting

| Property | Value |
|---|---|
| Provider | GitHub Pages (free tier) |
| Repository | `kenashe/luckydomains` (**must be public**) |
| Source | `main` branch, `/root` folder, "Deploy from a branch" |
| Custom domain | `luckydomains.io`, set by the committed `CNAME` file |
| TLS | Let's Encrypt certificate, provisioned and renewed by GitHub |
| Enforce HTTPS | Enabled |
| Jekyll | Disabled via `.nojekyll`, files are served exactly as committed |

**Deployment is a git push.** GitHub Pages watches `main` and republishes within
roughly a minute. There is no build step, no CI deployment stage, and no
artifact.

### Constraints inherited from GitHub Pages
- **No server side configuration.** No redirect rules, no custom headers, no
  `.htaccess` equivalent. This shapes the URL strategy in section 4.
- **Free tier requires a public repository.** A private repo silently
  unpublishes the site.
- Soft limits: 1 GB repository, 100 GB/month bandwidth, 10 builds/hour. This
  site is roughly 1 MB and nowhere near any limit.

---

## 3. DNS topology

Authoritative nameservers are GoDaddy's (`ns05.domaincontrol.com`,
`ns06.domaincontrol.com`). The domain is registered at GoDaddy.

| Record | Name | Value | Purpose |
|---|---|---|---|
| A | `@` | `185.199.108.153` | GitHub Pages |
| A | `@` | `185.199.109.153` | GitHub Pages |
| A | `@` | `185.199.110.153` | GitHub Pages |
| A | `@` | `185.199.111.153` | GitHub Pages |
| CNAME | `www` | `kenashe.github.io` | GitHub issues a 301 to the apex |
| MX | `@` | Google Workspace, 5 records | **Email. Do not touch.** |
| TXT | `@` | SPF and site verification | **Email. Do not touch.** |

Exact values, including the email records, are in `DATA_SOURCES.md`.

Because DNS is hosted at the registrar rather than at the website host, the
website and the email are independent. Changing where the site is hosted never
risks the email, and vice versa.

---

## 4. URL strategy

This is the least obvious part of the architecture, so it is worth stating
plainly.

GitHub Pages serves **three URL forms for the same page**:

| Form | Example | Status |
|---|---|---|
| Canonical | `/services/` | 200, this is the one we use |
| Extensionless | `/services` | 200, served automatically by Pages |
| Index variant | `/` and `/index.html` | both 200, literally the same file |

Plus the `www` hostname, which **does** 301 to the apex automatically.

Since Pages cannot issue redirects, duplicates are consolidated with:

1. **A self referencing `rel=canonical`** on every page, pointing at the
   trailing slash directory form on the apex host (DECISIONS D11).
2. **Root absolute internal links** that exactly match those canonicals, so no
   internal link ever votes for a duplicate. This is enforced by the test suite.
3. **A `sitemap.xml`** listing only the canonical forms.
4. **A permissive `robots.txt`.** Duplicates are deliberately left crawlable,
   because a blocked URL cannot be crawled and therefore its canonical tag can
   never be read.

---

## 5. Front end structure

### Pages
| File | URL | Notes |
|---|---|---|
| `index.html` | `/` | Hero with the presence map, diagnostic, five layers, five services, story, how we work, founder, contact band |
| `services/index.html` | `/services/` | The five services, engagements, what Lucky Domains is not |
| `services/website-design/index.html` | `/services/website-design/` | Service page |
| `services/seo/index.html` | `/services/seo/` | Service page |
| `services/ai-visibility/index.html` | `/services/ai-visibility/` | Service page |
| `services/entity-seo/index.html` | `/services/entity-seo/` | Service page (URL unchanged from the earlier site) |
| `services/domain-acquisition/index.html` | `/services/domain-acquisition/` | Service page |
| `how-we-buy-domains/index.html` | `/how-we-buy-domains/` | The acquisition process |
| `tools/digital-presence-check/index.html` | `/tools/digital-presence-check/` | Free self-check, browser only |
| `about/index.html` | `/about/` | Company story, values, how we work |
| `founder/ken-ashe/index.html` | `/founder/ken-ashe/` | Founder profile, `ProfilePage` and the shared `Person` node |
| `insights/index.html` | `/insights/` | Article library. Its cards are maintained by `scripts/articles.py` |
| `insights/<slug>/index.html` | `/insights/<slug>/` | One article each, `Article` schema |
| `news/index.html` | `/news/` | News index |
| `news/website-relaunch/index.html` | `/news/website-relaunch/` | June 2026 press release, `NewsArticle` schema, body left as published |
| `contact/index.html` | `/contact/` | Contact form |
| `404.html` | any missing path | Served by Pages, `noindex` |
| `services.html`, `about.html`, `contact.html`, `how-we-buy-domains.html`, `news/website-relaunch.html` | legacy | noindex redirect stubs (DECISIONS D11) |

The complete old to new URL map is in `docs/URL_MAP.md`.

### Shared page chrome
Every page carries the same header, footer and shared head lines between
comment markers: `<!-- head-common:start -->`, `<!-- header:start -->` and
`<!-- footer:start -->`. The test suite checks that they match the home page on
every page. There is no include mechanism, by design (DECISIONS D2); the markers
exist so the blocks can be compared and, for articles, copied by
`scripts/articles.py`.

### CSS
A single stylesheet, `css/styles.css`. The first part is the stylesheet as it
was before November 2026. The second part, under a dated banner comment, adds
the self hosted fonts, the Services menu, the presence map, the diagnostic, the
five layer progression, the short light page heroes, the service page lists, the
Digital Presence Check, the Insights library and the article layout, and a few
accessibility corrections (text safe green, content visible without
JavaScript). Design tokens are CSS custom properties in `:root`. Layout is CSS
Grid and Flexbox. Breakpoints at 980px, 760px and 460px. Every animation is
disabled under `prefers-reduced-motion`.

No CSS framework, no preprocessor, no utility library.

### JavaScript
A single file, `js/main.js`, vanilla JS in three self contained sections:

1. **Shared behaviour:** sticky header shadow, mobile navigation, the Services
   menu, Escape to close, FAQ accordion, reveal on scroll, and the
   "What is holding you back?" diagnostic.
2. **Interactions:** the presence map (SVG built in the browser from a small
   JSON block in the page, with a text fallback), the five layer progression,
   and the Digital Presence Check, which totals answers in the page.
3. **Footer year, the contact form (section 6), and the article contents list.**

There is no framework and no bundle. The file is served as written.
**The site is fully readable and navigable with JavaScript disabled**; JS only
adds progressive enhancement, except for the contact form.

The script makes exactly one kind of network request, the contact form
submission, and uses no cookies and no browser storage. The test suite checks
both.

### Structured data
JSON-LD is embedded per page: `Organization`, `WebSite`, `ProfilePage` and the
shared `Person` on the home page; `Service`, `WebPage` and `BreadcrumbList` on
each service page; `CollectionPage` on Services and Insights; `AboutPage`;
`ContactPage`; `NewsArticle` on the news post; and `Article` with
`BreadcrumbList` on each Insights article. A draft article carries no
`datePublished`.

### Insights articles
Each article is a complete page. Its settings are a JSON block inside the page
(`<script type="application/json" id="article-meta">`), and its text sits
between `<!-- article:start -->` and `<!-- article:end -->`.
`scripts/articles.py sync` re-renders the rest of the page from
`scripts/templates/article.html`, and refreshes the cards on `/insights/` and
the article entries in `sitemap.xml`. See `docs/INSIGHTS.md` and DECISIONS D14.

---

## 6. Contact form data flow

The only dynamic behaviour on the site.

```
Visitor fills form on /contact/
        │
        │  js/main.js intercepts submit, builds FormData,
        │  appends the Web3Forms access key
        v
POST https://api.web3forms.com/submit   (fetch, from the browser)
        │
        │  Web3Forms validates the key and the request origin
        v
Email delivered to the address registered with Web3Forms
        │
        v
Success message rendered in the page, form reset
```

Details that matter:

- **The access key is embedded in the page HTML** as a `data-access-key`
  attribute. This is by design: Web3Forms keys are public identifiers, not
  secrets. They are safe in client side code.
- **The Web3Forms free plan only accepts submissions from a browser.** Server
  side POSTs (curl, CI, scripts) are rejected with "This method is not allowed".
  Test the form in a real browser, never with curl.
- **Spam protection** is a hidden `botcheck` honeypot field.
- **Fallback.** If the key is missing or unconfigured, `js/main.js` detects it
  and shows a message directing the visitor to email `info@luckydomains.io`
  directly. A plain `mailto:` link is also present on the page and in the footer,
  so the page still works with JavaScript disabled.

---

## 7. External dependencies

| Dependency | Used for | Failure mode if it disappears |
|---|---|---|
| GitHub Pages | Hosting, TLS, CDN | Site offline. Any static host can serve this repo unchanged. |
| GoDaddy DNS | Domain resolution | Site and email unreachable. |
| Web3Forms | Contact form delivery | Form shows its fallback message; `mailto:` still works. |
| Google Workspace | `info@luckydomains.io` | Email only, no effect on the website. |

Fonts are self hosted in `assets/fonts/` and are not an external dependency
(DECISIONS D13). Every dependency degrades gracefully except hosting and DNS. Full details,
including rate limits, are in `DATA_SOURCES.md`.

---

## 8. Tooling

Scripts live in `scripts/` and are plain Python 3.

| Script | Purpose | Dependencies |
|---|---|---|
| `deploy.py` | Publish the site over the GitHub REST API, for agents that have a token but no git credentials. Includes a guard that refuses to delete files present in the repo but absent locally. | standard library only |
| `make_assets.py` | Regenerate favicons, app icons and the Open Graph image from `assets/source/`. | Pillow |
| `articles.py` | Keep Insights articles, the `/insights/` cards and the sitemap entries in sync, and set publication dates on the owner's instruction. Optional: the pages it writes are committed HTML. | standard library only |
| `verify_live.py` | Post deployment checks: HTTP status of every page, the `www` redirect, canonical correctness, DNS records, and that email DNS is intact. | standard library only |

`tests/test_site.py` is the test suite, standard library only, run by CI in
`.github/workflows/ci.yml`.

---

## 9. What this project deliberately does not have

Listed explicitly so nobody spends time looking for something that was never
there:

- **No database.** Nothing is persisted. The contact form hands off to a third
  party API which emails the owner; no submission is stored by this project. If
  a future feature needs storage, that is a new architectural decision and
  belongs in `DECISIONS.md`.
- **No migrations**, because there is no database.
- **No server side code, no API of our own, no serverless functions.**
- **No cron jobs, scheduled tasks or webhooks.**
- **No authentication, accounts or user state.**
- **No build step, bundler, transpiler, package manager or lockfile.**
- **No analytics or tracking**, pending an explicit decision by the owner.
- **No CMS.** Content is edited by changing the HTML. Insights articles have an
  optional helper script, not a content system (DECISIONS D14).
- **No portfolio or client case studies** (DECISIONS D15).

The rationale for each is recorded in `DECISIONS.md`.
