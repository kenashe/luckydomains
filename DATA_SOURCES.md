# DATA_SOURCES.md

Every external service, API, DNS record and third party dependency this project
relies on, with limits and fallbacks.

**No secrets appear in this file.** See `.env.example` for the variables the
tooling needs and where their values live.

---

## 1. Summary

| Service | Role | Account | Criticality |
|---|---|---|---|
| GitHub Pages | Hosting, TLS, CDN | `kenashe` | Critical, site is offline without it |
| GoDaddy | Domain registrar and authoritative DNS | Owner's | Critical, site and email both depend on it |
| Google Workspace | Email for `info@luckydomains.io` | Owner's | Critical for business, no effect on the website |
| Web3Forms | Contact form delivery | Free tier | Degraded, `mailto:` fallback remains |
| Google Fonts | Two webfont families | None, public CDN | Cosmetic, system fonts fall back |
| GitHub REST API | Used by `scripts/deploy.py` | Fine grained PAT | Convenience only, `git push` needs none |

---

## 2. GitHub Pages

- **Repository:** `kenashe/luckydomains`, branch `main`, folder `/root`
- **Mode:** "Deploy from a branch". No Actions deployment stage.
- **Custom domain:** `luckydomains.io`, applied by the committed `CNAME` file
- **TLS:** Let's Encrypt, provisioned and renewed automatically by GitHub
- **Jekyll:** disabled by `.nojekyll`

**Pages IP addresses** (the apex A records point at these; GitHub publishes them
and they change very rarely):

```
185.199.108.153
185.199.109.153
185.199.110.153
185.199.111.153
```

IPv6 equivalents, optional and not currently configured:
`2606:50c0:8000::153`, `2606:50c0:8001::153`, `2606:50c0:8002::153`,
`2606:50c0:8003::153`

**Limits** (soft, published by GitHub): 1 GB repository, 1 GB published site,
100 GB/month bandwidth, 10 builds per hour. This site is roughly 1 MB and uses a
negligible fraction of each.

**Failure modes.**
- Repository set to private: site silently unpublishes and returns 404. Fix by
  setting it public **and** re-enabling Pages.
- `CNAME` file deleted: the custom domain is dropped and the site reverts to the
  `github.io` address.
- Build failure: rare here because there is no build; Pages copies files as is.

---

## 3. DNS at GoDaddy

Authoritative nameservers: `ns05.domaincontrol.com`, `ns06.domaincontrol.com`.
The domain is registered at GoDaddy and DNS is hosted there, which means the
website host and the registrar are independent.

### Website records, safe to change
| Type | Name | Value | TTL |
|---|---|---|---|
| A | `@` | `185.199.108.153` | 600 |
| A | `@` | `185.199.109.153` | 600 |
| A | `@` | `185.199.110.153` | 600 |
| A | `@` | `185.199.111.153` | 600 |
| CNAME | `www` | `kenashe.github.io` | 1 hour |

`www` returns a 301 to the apex, issued automatically by GitHub.

### Email records, DO NOT CHANGE
Changing these takes down the owner's email.

| Type | Name | Priority | Value |
|---|---|---|---|
| MX | `@` | 1 | `aspmx.l.google.com` |
| MX | `@` | 5 | `alt1.aspmx.l.google.com` |
| MX | `@` | 5 | `alt2.aspmx.l.google.com` |
| MX | `@` | 10 | `alt3.aspmx.l.google.com` |
| MX | `@` | 10 | `alt4.aspmx.l.google.com` |
| TXT | `@` | | `v=spf1 include:dc-aa8e722993._spfm.luckydomains.io ~all` |
| TXT | `@` | | `google-site-verification=Fdmehrky-pJGTAfaf_Y-ZQ0TlNyVW60lPciopiSx2hE` |

The SPF record delegates through a GoDaddy managed indirection. It has been
verified to resolve to `v=spf1 include:_spf.google.com ~all`, so Google is
correctly authorised to send for this domain.

### Known trap: Domain Connect locked records
The site previously ran on Wix, which connected the domain using GoDaddy's
Domain Connect. That marked the A and CNAME records as **managed by a third
party**, which greys out the edit and delete controls in the GoDaddy DNS panel.
Disconnecting on the Wix side did not release them; GoDaddy support had to
remove the orphaned managed records manually.

If you see greyed out trash or pencil icons next to a DNS record, that is the
cause. Ask GoDaddy support to remove the orphaned Domain Connect managed
records, naming the exact records, and explicitly asking them not to touch MX or
TXT.

---

## 4. Email authentication status

| Mechanism | Status | Note |
|---|---|---|
| SPF | **Present and correct** | Resolves to `include:_spf.google.com` |
| DKIM | **Missing** | Nothing published at the `google._domainkey` selector |
| DMARC | **Missing** | No `_dmarc` record exists |

This is an open gap. Without DKIM and DMARC, outbound mail is more likely to be
filtered and the domain can be spoofed by anyone, which matters for a firm
selling digital credibility.

**To add DKIM:** Google Admin console > Apps > Google Workspace > Gmail >
Authenticate email. Select the domain, generate a new 2048 bit record with the
`google` prefix, publish the supplied value at GoDaddy as a TXT record named
`google._domainkey`, then return to the console and click Start authentication.

**To add DMARC:** publish a TXT record at GoDaddy.

```
Name:  _dmarc
Value: v=DMARC1; p=none; rua=mailto:info@luckydomains.io
```

Run `p=none` for a few weeks and read the aggregate reports, then tighten to
`p=quarantine` and eventually `p=reject`.

---

## 5. Web3Forms

Delivers contact form submissions by email. See `ARCHITECTURE.md` section 6 for
the data flow.

- **Endpoint:** `POST https://api.web3forms.com/submit`
- **Auth:** an `access_key` field in the request body
- **Where the key lives:** in `contact.html`, as `data-access-key` on the form
- **Is the key a secret?** No. Web3Forms access keys are public identifiers
  designed to sit in client side code. They are safe in a public repository.
  A leaked key can only cause spam to the registered inbox, and it can be
  rotated at web3forms.com.
- **Delivery address:** the address registered with Web3Forms by the owner
- **Spam protection:** a hidden `botcheck` honeypot field in the form

**Free tier limits.** 250 submissions per month. The important restriction is
not volume but origin:

> **The free plan only accepts submissions sent from a browser.** Server side
> requests, including curl and CI, are rejected with "This method is not
> allowed. Use our API in client side". Always test the form in a real browser.

**Fallbacks.** If the key is absent or unconfigured, `js/main.js` shows a message
directing the visitor to email `info@luckydomains.io`. A `mailto:` link is also
present on the contact page and in every footer, so the site still converts with
JavaScript disabled or Web3Forms down.

**Rotation.** Generate a new key at web3forms.com, replace the `data-access-key`
value in `contact.html`, run the tests, and push.

---

## 6. Google Fonts

- **Families:** Inter (400, 500, 600) and Plus Jakarta Sans (600, 700, 800)
- **Loaded from:** `fonts.googleapis.com` and `fonts.gstatic.com`, with
  `preconnect` hints and `display=swap`
- **Auth:** none, public CDN
- **Limits:** none in practice

**Fallback.** The CSS declares a full system font stack after each family, so if
Google Fonts is blocked or slow the site renders immediately in system fonts
with no layout shift beyond the swap. Purely cosmetic.

**Privacy note.** Requests to Google Fonts expose visitor IPs to Google. If that
ever becomes a concern, the two families can be self hosted in `assets/fonts/`
and the `@font-face` rules moved into `css/styles.css`, removing the third party
request entirely.

---

## 7. GitHub REST API, used by `scripts/deploy.py`

Only relevant to agents that have a token but no git credentials. A normal
`git push` uses none of this.

- **Base:** `https://api.github.com`
- **Auth:** `Authorization: Bearer <GITHUB_PAT>`
- **Token type:** fine grained personal access token, scoped to **only** the
  `luckydomains` repository
- **Permissions needed:** Contents read and write. Pages read and write is
  optional and only required to toggle Pages or set the custom domain by API.
- **Endpoints used:** repository metadata, git trees, git blobs, git commits,
  git refs, repository contents, and Pages.

**Rate limits.** 5,000 requests per hour for an authenticated token, 60 per hour
unauthenticated. A full deploy of this site is roughly 30 requests.

**Failure modes.**
- `401 Bad credentials`: the token expired, which happens roughly every 30 days
  by default, or it was revoked. Rotate it, see `docs/RUNBOOK.md`.
- `403` on Pages endpoints: the token lacks Pages write. The commit still
  succeeds; only the Pages and custom domain calls are skipped, and the
  committed `CNAME` still applies the domain.
- `409 Git Repository is empty`: the Git Data API cannot write to a repository
  with no commits. `scripts/deploy.py` handles this automatically.

---

## 8. Services deliberately NOT used

Recorded so their absence is understood as a choice, not an oversight.

- **No database, no object storage, no cache.** Nothing is persisted.
- **No analytics or tag manager.** See `DECISIONS.md` D10.
- **No CDN beyond what GitHub Pages provides.**
- **No error monitoring**, since there is no server and almost no JavaScript.
- **No CI deployment stage.** CI runs tests only; Pages deploys from the branch.
- **No cron jobs, scheduled tasks or webhooks.**
