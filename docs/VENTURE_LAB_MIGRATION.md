# VENTURE_LAB_MIGRATION.md

Record of the November 2026 redesign: the move from the agency-first site to
the Venture Lab design and the digital venture studio positioning.

**Owner approval status: NOT YET APPROVED FOR PRODUCTION.** The design direction
and the positioning are approved. This branch is a production candidate. It has
not been merged, and the live site has not changed. Update this line when the
owner approves the cutover, and again when it is live.

---

## 1. Sources

| Item | Value |
|---|---|
| Design source | `kenashe/luckydomains-design-concepts`, Venture Lab v2, commit `d05e5c1ca94c33d77506093d7c0bf3b306f6a568` |
| Production branch | `venture-lab-production-candidate` in this repository |
| Branched from | `main` at `efed1ded196d8ecc157f6d02f41f170b69033f45` (2026-11-23) |
| Staging copy | Exported from this branch into the design repository under `production-candidate/`. Noindex, form disabled |
| Fact sources | The public build records on kenashe.ai, read 2026-11-23, and this repository's own pages |
| Decisions | `DECISIONS.md` D12 (positioning) and D13 (design and architecture) |

The pages were written once by a migration script during the port. That script
is not in this repository and is not needed again. From here on, the HTML files
are edited by hand like before.

---

## 2. Page mapping

Every URL that existed before still exists. Four are new. None was retired.

| URL | Before | After |
|---|---|---|
| `/` | Agency home: services overview, process, FAQ, fit | Hero, operating status, Build/Operate/Acquire, ZeroHuman, more from the lab, progression, Domain Desk, how it fits together |
| `/ventures/` | Did not exist | **New.** Portfolio in four groups |
| `/ventures/zerohuman/` | Did not exist | **New.** Venture page |
| `/ventures/ai-agent-economy/` | Did not exist | **New.** Experiment page |
| `/ventures/autonomous-seo-agent/` | Did not exist | **New.** Internal system page |
| `/services/` | Domains, websites, SEO grid, engagement tiers | Domain Desk first, then Digital Identity and Presence, then Selected Website and Entity Engagements |
| `/services/entity-seo/` | Entity SEO detail | Same content, new design |
| `/how-we-buy-domains/` | Buying process | Same content, new design |
| `/about/` | Story, values, how we work | Evolution in five steps, operating philosophy, company timeline, operating model |
| `/founder/ken-ashe/` | Founder profile framed around the domain and SEO practice | Founder profile framed around the builder and the company, same credentials and links |
| `/news/` | One release, media resources | The release, dated project updates, media resources |
| `/news/website-relaunch/` | June 24, 2026 release | Body unchanged, new design |
| `/contact/` | One form with a "need" select | One form with four inquiry paths |
| `/404.html` | Not found | Not found, new design |
| `services.html`, `about.html`, `contact.html`, `how-we-buy-domains.html`, `news/website-relaunch.html` | Legacy stubs | Unchanged, byte for byte |

Anchors kept because other pages and kenashe.ai link to them:
`/services/#domains`, `#selling`, `#websites`, `#seo`, `#pricing`,
`/founder/ken-ashe/#connect`, `/news/#media-resources`. The `?need=buying`,
`selling`, `website` and `seo` query values on `/contact/` still work.

Anchors that no longer exist: `/#fit`, `/#services-overview`,
`/founder/ken-ashe/#fit`, `/founder/ken-ashe/#ai-builds`, `/about/#founder`
(kept as an id on the founder button). Nothing in this repository links to the
removed ones. A link to a missing anchor simply lands at the top of the page.

---

## 3. Content mapping

| Old content | Where it went |
|---|---|
| Domain acquisition and brokerage copy, included list, fee terms | `/services/#domains` and the home Domain Desk, kept and made primary |
| Seller representation, "how a quiet sale runs" | `/services/#selling`, kept |
| "What this is not" list | `/services/#domains` and `/how-we-buy-domains/`, kept |
| Websites: consult, build, what a build includes | Condensed into Selected Website and Entity Engagements, `/services/#websites` |
| Technical SEO, on-page, content built on search demand | Kept as scope items under `/services/#websites` and `#identity` |
| Entity SEO | Kept as `/services/entity-seo/`, linked from `/services/#identity` |
| Local SEO, authority and links, monthly reporting | **Retired.** They read as retainer services, which the company no longer advertises |
| Engagement tiers ("Project", "Monthly", "Custom") | **Retired.** No package or pricing presentation |
| Home FAQ, "who this is for" | **Retired** from the home page. The Entity SEO page keeps its own FAQ and fit section |
| About: story, values, how we work | Rewritten as evolution, philosophy ("Fortune favors the prepared."), timeline, operating model |
| Founder: operating discipline, credentials, career, Forbes Business Council, quote, Connect links | Kept on the Founder page |
| Founder: "Practical AI" section | Replaced by links to the ventures and to the build logs on kenashe.ai |
| June 24, 2026 press release | Kept as published |
| Media Resources block | Kept on `/news/` |

New copy fixed by the owner: the company description, the hero headline, the
Build, Operate, Acquire lines, "Built by Ken Ashe. Operated by Lucky Domains.",
"Some experiments became systems that run.", "The domain desk is still open.",
and the project classifications in `DECISIONS.md` D12.

Structured data: the `Organization` description and `knowsAbout` list were
updated on every page that carries them, including the release page. The shared
`Person` node is byte-identical to `main`. The release's `NewsArticle` is
unchanged.

---

## 4. Staging-only transformations

Staging is generated by `tools/export_staging.py` in the design repository. It
differs from this branch in exactly these ways:

1. A path prefix on root-absolute links, because staging is served from a
   subfolder.
2. `noindex,nofollow,noarchive` on every page.
3. Canonical, `og:url`, `og:image` and `twitter:image` point at the staging URL.
4. A slim notice bar at the top of every page.
5. The contact form cannot send: the access key is removed, the endpoint is
   replaced, and a small script blocks submit.
6. `CNAME`, `robots.txt`, `sitemap.xml`, documentation, tests and scripts are
   not copied.

Nothing from staging is ever copied back into this repository.

---

## 5. SEO checklist

- [x] Every page has a unique title, description, canonical, Open Graph and Twitter tags
- [x] Canonicals use the trailing-slash form and match `sitemap.xml`
- [x] `sitemap.xml` lists all thirteen indexable pages, apex host only
- [x] `robots.txt` unchanged. No duplicate URL form is blocked
- [x] Legacy `.html` stubs unchanged: `noindex, follow`, canonical, instant refresh, query and hash preserved
- [x] No internal link to `/index.html`, a `.html` path, a slashless path, or a staging URL
- [x] Normal pages carry no robots meta. Only `404.html` and the stubs are noindex
- [x] Structured data parses on every page. Breadcrumbs on ventures, venture pages and services
- [x] The domain brokerage service stays in `Organization.knowsAbout` and in the `Service` catalog
- [x] No claim of a software product, a customer, a rating, a location, or an employee count was added
- [ ] After launch: resubmit the sitemap in Search Console and inspect the four new URLs

## 6. Form checklist

- [x] Web3Forms access key unchanged (the tests assert the exact value)
- [x] Honeypot `botcheck` kept
- [x] Success, API-failure and network-failure messages verified in a browser with the endpoint mocked
- [x] Required-field handling verified. Domain fields are required only on the domain path
- [x] `mailto:info@luckydomains.io` fallback and a `<noscript>` note present
- [x] Old `?need=` links still preselect a path
- [ ] **One real submission.** Not completed before launch: the build environment could not reach `api.web3forms.com` (HTTP 403 at the network edge), so no test email was sent. Do this once on the live site at cutover (RUNBOOK section 9)

## 7. Test results on this branch (2026-11-23)

- `python3 tests/test_site.py`: all checks pass
- Chromium and Firefox, 14 pages at 320, 375, 390, 768, 1024 and 1440 pixels: no horizontal overflow, no console errors, no broken images, no missing alt text, no text under 12px, no undersized touch targets
- axe-core 4.10, WCAG 2 and 2.1 A and AA plus best practice, 14 pages at 375 and 1440 pixels: no violations
- Reduced motion: no running animation and no hidden content on any page
- No JavaScript: navigation, headings, all status rows and all FAQ answers visible
- Layout shift: 0.0002 at most
- **Not run:** WebKit could not start in the build environment, so Safari is untested. Lighthouse could not be installed (the package registry is blocked there) and the PageSpeed API returned quota errors. Run both at cutover

Page weight, first uncached load, uncompressed, measured locally: 230 to 355 KB
on twelve pages. The press release page is 874 KB, most of which is its existing
hero image. The three font files are 156 KB of every first load and are cached
after the first page. The previous pages were about 105 to 150 KB plus Google
Fonts (754 KB for the release). The increase is the fonts, which now come from
this site, so the pages make no third party request. GitHub Pages compresses
HTML, CSS and JavaScript in transit, which the local measurement does not show.

---

## 8. Launch checklist

See `docs/RUNBOOK.md` section 11. In short: owner approval, rebase, tests,
record the rollback commit, merge, watch Pages deploy, `verify_live.py`, live
form test, SEO spot checks, `www` redirect, DNS unchanged, Safari and iPhone,
Search Console, then the kenashe.ai cross-links, then final screenshots.

## 9. Rollback

Rollback commit: `efed1ded196d8ecc157f6d02f41f170b69033f45`, or whatever `main`
is immediately before the merge. Record it at step 5 of the cutover.

Procedure: `docs/RUNBOOK.md` section 12. It is a `git revert` of the merge and a
push. No DNS, Pages, or form change is involved in either direction.

---

## 10. Unresolved factual questions

1. **Sir Pitches-a-Lot date.** The kenashe.ai build index says June 2026. Its
   build page says August 2026. No date is shown here.
2. **"Longtime Bitcoin and Ethereum participant."** No public source states how
   long. The Founder page says only that his public focus areas include AI
   agents, Bitcoin, digital identity, and domain names, which the kenashe.ai
   newsroom states.
3. **Autonomous SEO Agent counts.** "63 researched, 8 confirmed live" is the
   figure on its build record, which is undated. Update when the record changes.
4. **ZeroHuman outside purchases.** The limitation is dated November 20, 2026.
   Update the home page and the venture page when the build record changes.
5. **Founding date.** `Organization.foundingDate` (2025-08-01) and the legal name
   were already in the structured data and were left as they were. No founding
   date appears in visible copy.
6. **A public announcement of the new positioning.** None has been approved, so
   none is published. `/news/` shows the June release and dated project updates.
