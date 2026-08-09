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
              Google Fonts <─┘         └─> Web3Forms API
              (CSS + WOFF2)                (contact form POST)
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
| Canonical | `/services.html` | 200, this is the one we use |
| Extensionless | `/services` | 200, served automatically by Pages |
| Index variant | `/` and `/index.html` | both 200, literally the same file |

Plus the `www` hostname, which **does** 301 to the apex automatically.

Since Pages cannot issue redirects, duplicates are consolidated with:

1. **A self referencing `rel=canonical`** on every page, pointing at the `.html`
   form on the apex host.
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
| `index.html` | `/` | Hero, services overview, why us, process, testimonials, FAQ, CTA |
| `services.html` | `/services.html` | Domain acquisition, SEO services, engagement tiers |
| `about.html` | `/about.html` | Story, values, founder |
| `contact.html` | `/contact.html` | Contact form, quick answers |
| `404.html` | any missing path | Served by Pages, `noindex` |
| `news/website-relaunch.html` | `/news/website-relaunch.html` | Press release, `NewsArticle` schema |

### CSS
A single stylesheet, `css/styles.css`. Design tokens are CSS custom properties
declared once in `:root` (brand colours, spacing, radii, shadows, easing).
Layout is CSS Grid and Flexbox. Responsive breakpoints at 980px, 760px and
460px. Includes a `prefers-reduced-motion` block that disables all animation.

No CSS framework, no preprocessor, no utility library.

### JavaScript
A single file, `js/main.js`, roughly 100 lines of vanilla JS in an IIFE. It
provides:

- sticky header shadow on scroll
- mobile navigation toggle
- FAQ accordion with correct `aria-expanded` handling
- reveal on scroll via `IntersectionObserver`, with a graceful fallback
- current year in the footer
- contact form submission (section 6)

There is no framework and no bundle. The file is served as written.
**The site is fully readable and navigable with JavaScript disabled**; JS only
adds progressive enhancement, except for the contact form.

### Structured data
JSON-LD is embedded per page: `ProfessionalService` and `WebSite` on the home
page, `Service` and `BreadcrumbList` on services, `AboutPage` with a `Person`
for the founder, `ContactPage` on contact, and `NewsArticle` on the news post.

---

## 6. Contact form data flow

The only dynamic behaviour on the site.

```
Visitor fills form on /contact.html
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
| Google Fonts | Inter, Plus Jakarta Sans | Fonts fall back to the system stack declared in the CSS. Site stays usable. |
| Web3Forms | Contact form delivery | Form shows its fallback message; `mailto:` still works. |
| Google Workspace | `info@luckydomains.io` | Email only, no effect on the website. |

Every dependency degrades gracefully except hosting and DNS. Full details,
including rate limits, are in `DATA_SOURCES.md`.

---

## 8. Tooling

Scripts live in `scripts/` and are plain Python 3.

| Script | Purpose | Dependencies |
|---|---|---|
| `deploy.py` | Publish the site over the GitHub REST API, for agents that have a token but no git credentials. Includes a guard that refuses to delete files present in the repo but absent locally. | standard library only |
| `make_assets.py` | Regenerate favicons, app icons and the Open Graph image from `assets/source/`. | Pillow |
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
- **No CMS.** Content is edited by changing the HTML.

The rationale for each is recorded in `DECISIONS.md`.
