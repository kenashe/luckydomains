# DECISIONS.md

Significant technical and product decisions, with the reasoning and the
alternatives that were rejected. Newest last.

Format: what was decided, why, what else was considered, and what would make us
revisit it.

---

## D1. Move off Wix to a static site on GitHub Pages
**Date:** June 2026 · **Status:** done

**Decision.** Retire the Wix site and serve a hand built static site from GitHub
Pages on the apex domain.

**Why.** The Wix site was small, dated, and carried a recurring subscription for
capability the business was not using. The owner wanted the site in GitHub so it
is portable, versioned, and editable by coding agents. A four page marketing
site is the ideal case for static hosting: free, fast, no maintenance surface,
no patching.

**Alternatives considered.**
- *Stay on Wix and restyle.* Rejected: keeps the cost and the lock in.
- *Netlify or Vercel.* Both are good and both support private repos. Rejected
  for this project because GitHub Pages needs no third party account at all and
  the repo is already the source of truth. Either remains an easy migration
  target; the site is plain files, so moving hosts means pointing DNS elsewhere.
- *A static site generator such as Hugo, Astro or Eleventy.* Rejected, see D2.

**Revisit if.** The site needs server side logic, private repository hosting, or
preview deployments per pull request. Vercel or Netlify would then be the
natural move.

---

## D2. No framework, no build step, no package manager
**Date:** June 2026 · **Status:** done

**Decision.** Hand written HTML, one CSS file, one vanilla JS file. No React, no
Tailwind, no bundler, no `package.json`, no lockfile.

**Why.** The site is six pages of largely static content. A build step would add
a toolchain to install, a lockfile to maintain, and a dependency tree to patch,
in exchange for conveniences this project does not need. Plain files can be
edited by the owner, by any coding agent, and by a text editor in ten years.
Portability was an explicit requirement, and nothing is more portable than HTML.

**Cost accepted.** Shared markup, chiefly the header and footer, is duplicated
across pages. With six pages that is a manageable amount of duplication. The
test suite catches the class of error this most commonly causes, which is
inconsistent internal links.

**Revisit if.** The page count grows past roughly fifteen, or a blog needs real
templating. Then adopt a generator that outputs static files, keeping the same
hosting.

---

## D3. Public repository
**Date:** June 2026 · **Status:** done, reaffirmed after an incident

**Decision.** `kenashe/luckydomains` is public.

**Why.** GitHub Pages on the free plan will not serve a private repository.
There is also nothing to protect: every file in the repo is delivered verbatim
to every visitor, so a public repo exposes nothing that the website does not
already publish. No credentials are stored in it.

**Incident.** The repo was briefly set to private, which silently unpublished
the site and returned 404 on the domain. Restoring visibility to public was not
sufficient by itself; Pages had to be re-enabled, because a visibility change
switches Pages off and it does not come back automatically.

**Alternative.** Paying for GitHub Pro to serve Pages from a private repo.
Rejected: money for no benefit on a site whose content is public anyway.

---

## D4. Canonical tags and consistent internal linking instead of 301 redirects
**Date:** July 2026 · **Status:** done

**Decision.** Consolidate duplicate URL forms using a self referencing
`rel=canonical` on every page plus root absolute internal links that exactly
match those canonicals. Do not attempt redirects.

**Why.** GitHub Pages offers no server side redirect control, so 301s cannot be
authored. Two of the three duplicate classes cannot be redirected even in
principle: `/` and `/index.html` are the same file, so neither can redirect to
the other. Canonical tags are Google's documented solution for exactly this
situation on static hosts.

The `www` duplicate needs no work: GitHub already issues a 301 from `www` to the
apex automatically, because the custom domain is the apex.

**What was actually wrong.** Every page carried three internal links to
`index.html`. Those links were the real problem, because they told Google the
duplicate was a genuine destination. 93 internal links were rewritten to a
single canonical root absolute form.

**Rejected.** Blocking duplicates in `robots.txt`. This is a common instinct and
it backfires: a blocked URL cannot be crawled, so its canonical tag is never
read and consolidation never happens.

---

## D5. Keep `.html` URLs rather than switching to extensionless
**Date:** July 2026 · **Status:** superseded by D11 (September 2026)

**Decision.** Canonical URLs keep the `.html` suffix, for example
`/services.html`.

**Why.** GitHub Pages serves both `/services` and `/services.html` with a 200.
Extensionless URLs look slightly cleaner, but Google had already begun indexing
the `.html` forms, and the canonicals already pointed there. Changing the
canonical form would churn indexed URLs for a purely cosmetic gain, on a site
whose SEO credibility is the product.

**Revisit if.** The site is ever rebuilt with a generator that emits directory
style URLs, in which case do the switch once, deliberately, with the sitemap and
canonicals updated in the same change.

---

## D6. Web3Forms for the contact form
**Date:** June 2026 · **Status:** done

**Decision.** The contact form posts from the browser to the Web3Forms API,
which emails the submission to the owner.

**Why.** Static hosting cannot process a form. Web3Forms needs no backend, no
account tie in to the host, and no server code, and its free tier is sufficient
for expected volume. The access key is a public identifier rather than a secret,
so embedding it in the HTML is safe and correct.

**Alternatives.** Formspree and Netlify Forms are comparable; Netlify Forms
would have required moving hosts. A self hosted handler would require a server,
which contradicts D1 and D2.

**Constraints this creates.**
- The free plan only accepts submissions originating from a browser. Server side
  POSTs are rejected, so the form must be tested in a real browser, never with
  curl.
- Delivery depends on a third party. The page therefore always shows a `mailto:`
  fallback, and `js/main.js` degrades to an explicit "email us directly" message
  if the key is missing or rejected.

**Revisit if.** Volume outgrows the free tier, or submissions need to be stored
rather than emailed. Storage would be a new architectural decision.

---

## D7. Deployment is a git push, not a tool
**Date:** August 2026 · **Status:** done

**Decision.** The canonical deployment procedure is `git push` to `main`.
`scripts/deploy.py` exists only as a convenience for agents that hold an API
token but have no git credentials.

**Why.** Deployment must not depend on any particular development tool. GitHub
Pages already redeploys on push, so the simplest correct answer is also the most
portable one. Earlier in this project the deploy tooling lived only inside an AI
development platform, which meant the ability to ship was not actually in the
owner's control. Moving the script into the repository fixed that.

**Consequence.** The personal access token is not infrastructure. It is a
workaround for one class of client. A human, or any agent with normal git
credentials, never needs it. Tokens expire roughly every 30 days and that is
expected rather than a fault.

---

## D8. Dependency free tests, run in CI
**Date:** August 2026 · **Status:** done

**Decision.** `tests/test_site.py` uses only the Python standard library and is
run by GitHub Actions on every push and pull request.

**Why.** The suite must be runnable by anyone, immediately, with no install
step. It asserts the failures this project has actually experienced rather than
generic best practice: canonical and sitemap disagreement, internal links to
duplicate URL forms, broken internal links, missing metadata, leftover
placeholder tokens, and em dashes.

**Alternatives.** pytest with an HTML parser and a link checker would be more
capable, at the cost of a dependency tree and an install step on a project that
otherwise has neither.

---

## D9. Documentation lives in the repository
**Date:** August 2026 · **Status:** done

**Decision.** All durable project knowledge lives in this repository:
`README.md`, `AGENTS.md`, `ARCHITECTURE.md`, `PRODUCT.md`, `DECISIONS.md`,
`DATA_SOURCES.md`, `.env.example`, `docs/RUNBOOK.md`, plus the scripts, the
tests and the source brand assets.

**Why.** Project state must not depend on a conversation history inside any one
AI development tool. GitHub is the durable memory; the development environment
is replaceable. Before this change, the deploy tooling, the asset pipeline, the
source logo files and every operational lesson from the Wix migration existed
only inside a chat product.

**Standing rule.** Before completing any substantial piece of work, update the
relevant document in this list so another competent agent could continue without
access to any prior conversation.

---

## D10. No analytics, for now
**Date:** August 2026 · **Status:** open

**Decision.** No analytics or tracking scripts are installed.

**Why.** Nothing has been added without the owner's explicit decision, and
adding third party tracking to a lead generation site has privacy, consent and
performance implications worth choosing deliberately.

**When revisited,** the likely options are a privacy respecting analytics
product that needs no cookie banner, or Google Analytics 4 if the owner wants
tighter integration with Search Console and Ads. Search Console itself is
verification only and carries no tracking script, so it is worth doing
regardless.

---

## D11. Directory-style extensionless URLs, with legacy `.html` stubs
**Date:** September 2026 · **Status:** done

**Decision.** Every page now lives at `<slug>/index.html` and its canonical URL
is the trailing-slash form, for example `https://luckydomains.io/services/`.
The old `<slug>.html` files remain in the repo as tiny noindex stubs that carry
a canonical tag and an instant meta refresh to the new URL.

**Why.** D5 kept `.html` because Google had indexed those URLs and GitHub Pages
cannot redirect. Both facts still hold, but the site is only seven URLs and a
few months old, so the re-indexing cost is the smallest it will ever be, and the
founder page had already been shipped in directory form. Directory URLs are the
one shape GitHub Pages genuinely redirects (`/services` 301s to `/services/`
once no `services.html` file exists), so the site ends with a single consistent
URL grammar.

**How legacy URLs are handled.** GitHub Pages cannot 301 `/services.html`, so
the stub approach is the strongest available signal: `noindex, follow`, a
`rel=canonical` to the new URL, `http-equiv=refresh` with a zero delay, and a
JavaScript `location.replace` that preserves query strings and hashes. Google
treats an instant meta refresh plus a matching canonical as a permanent
redirect. The stubs must stay crawlable (never block them in `robots.txt`) or
Google cannot read the signal.

**Observed on deploy (2026-09-14).** While a stub file exists, GitHub Pages
resolves the slash-less `/services` to `services.html` (the stub) instead of
301ing to `/services/`. So during the transition both legacy forms are served
by the stub and consolidate through it. Once Search Console shows the `.html`
URLs dropped, delete the stubs; the native 301 from `/services` to `/services/`
appears immediately (the founder page, which never had a stub, already behaves
this way).

**Consequences.** Internal links, canonicals, `og:url`, sitemap, breadcrumbs and
JSON-LD `@id`s all use the trailing-slash form. The test suite forbids every
`.html` and slash-less form. If true 301s are ever wanted, put a proxy such as
Cloudflare in front (proxy only the A records, never MX or TXT) or move hosts;
the directory layout works unchanged on either.

**Revisit if.** Search Console shows the legacy URLs still indexed after a
couple of months, in which case a proxy-level 301 is the next step.

---

## D12. Reposition as a digital presence studio, and rebuild the site around five services
**Date:** November 2026 · **Status:** production candidate, awaiting owner approval to launch

**Decision.** Lucky Domains is presented as a digital presence studio for the
AI era: it "helps businesses build a digital presence that people, search
engines, and AI systems can find, understand, and trust." The site is organized
around five services (Website Design & Development, SEO & Search Visibility, AI
Visibility & Brand Authority, Entity SEO & Digital Identity, Domain Acquisition
& Brokerage), a Tools area and an Insights area, and the framework Domain,
Website, Search, Entity, AI.

**How we got here.** This is recorded in full so nobody has to reconstruct it.

1. **The original site (June to November 2026).** Three service lines framed as
   one job: the name, the site, the rankings. Navy hero, white sections, green
   accent. The owner liked this design.
2. **Design exploration, phase 1 (November 2026).** Three concepts in a separate
   review repository (`kenashe/luckydomains-design-concepts`): Venture Lab, The
   Register, Namespace. Venture Lab was refined and carried to a production
   candidate branch and a draft pull request (#4). It positioned the company as
   a digital venture studio built around the founder's AI experiments.
3. **Correction.** The owner rejected the venture studio positioning. The
   business is websites, search, identity, AI visibility, and domains, for
   clients. Pull request #4 was closed without merging and its branch deleted.
4. **Phase 2.** Three light concepts with the corrected message. The owner did
   not like the visual designs.
5. **Version 3.** Three concepts built on the original production stylesheet,
   with a fuller set of pages. The owner chose Original Interactive, asked for
   one refinement (one presence map, a shorter homepage, lighter interior
   pages, no portfolio, a standalone Digital Presence Check), and approved it.
6. **This candidate.** The approved refinement ported into this repository as
   plain HTML, CSS and JavaScript, with final content decisions applied.

**What stayed.** The logo, the navy hero, the green accent, the typography, the
original component styles (`css/styles.css` keeps the earlier rules and adds to
them), the domain brokerage offer, the contact integration, every existing URL,
the legacy `.html` stubs, and the June 2026 press release: its headline, text,
dates and `NewsArticle` data are exactly as published. That page also carries the
shared Organization and Person records, which are kept identical to the home page
on every page that carries them, so the Organization record there was updated
along with the others. The release itself was not rewritten.

**What was rejected.** Venture studio positioning. Presenting the founder's
experiments (ZeroHuman, the AI Agent Economy experiment, ENS naming) as the
commercial offer. A dark, technical "lab" aesthetic. A second presence map,
auto advancing widgets and a questionnaire on the homepage.

**Revisit if.** The service mix changes. Positioning changes are owner
decisions and belong here before they reach the HTML.

---

## D13. Self host the two font families
**Date:** November 2026 · **Status:** production candidate

**Decision.** Plus Jakarta Sans and Inter are served from `assets/fonts/` as two
variable WOFF2 files (Latin subset), preloaded in the page head. The Google
Fonts stylesheet and preconnect lines are removed.

**Why.** `DATA_SOURCES.md` already named this as the option if third party
requests became a concern. Self hosting removes the only third party request a
normal page view made, stops visitor IP addresses reaching Google on every
visit, removes a render blocking cross origin stylesheet, and lets the fonts be
preloaded, which removed the layout shift measured during design review. The
site now makes no third party request except the contact form submission.

**Cost.** About 75 KB of font files in the repository, cached by the browser
after the first page. Both families are licensed under the SIL Open Font
License (see `assets/fonts/LICENSE.txt`).

**Revisit if.** A new weight, style or script is needed. Replace the files and
the two `@font-face` rules in `css/styles.css`.

---

## D14. Insights articles: complete HTML pages, kept in sync by an optional script
**Date:** November 2026 · **Status:** production candidate

**Decision.** Each article is a complete HTML page at
`insights/<slug>/index.html`. Its settings (title, summary, status, dates,
related links, sources) live in a small JSON block inside the page, and its
text lives between two comment markers. `scripts/articles.py` re-renders the
repetitive parts (head tags, structured data, byline, contents list, sources,
related links, shared header and footer), the cards on `/insights/`, and the
article entries in `sitemap.xml`.

**Why this does not break D2.** There is still no build step: the pages are
committed as plain HTML and the site deploys with a git push. The script is a
convenience in the same sense as `scripts/deploy.py`. It uses only the standard
library, and an article can still be edited by hand. The alternative, copying a
whole page by hand for each article, is how layouts drift.

**Editorial rules built into it.** A draft never carries a publication date,
is marked `noindex`, stays out of the sitemap, and shows "Editorial draft" in
its byline. Dates are set only by `articles.py publish --date`, with a date the
owner chose. Nothing publishes automatically. `tests/test_site.py --launch`
fails while any draft remains.

**Rejected.** A CMS, a static site generator, Markdown with a build step, and
unattended publication. Each adds a dependency or removes the owner's review.

**Revisit if.** The library grows past a few dozen articles, or more than one
person writes for it.

---

## D15. No portfolio, no client case studies, no testimonials
**Date:** November 2026 · **Status:** done

**Decision.** The site does not showcase client work. There is no Work
navigation item, portfolio page, case study, client logo row, testimonial, or
performance claim.

**Why.** The owner does not intend to publish client work. Earlier placeholder
testimonials were fabricated and had to be removed (see `PRODUCT.md`). Invented
or anonymized "client" examples are the same problem in a different form.

**What replaces it.** Nothing with that shape. Credibility comes from the depth
of the service pages, the Insights articles, transparent processes, the founder,
honest limits, and a small number of first party examples, each labeled as the
company's or founder's own work, an internal system, or research.

**Revisit if.** The owner supplies real, approved client material and asks for
it to be published.

---

## D16. A free, browser only Digital Presence Check
**Date:** November 2026 · **Status:** production candidate

**Decision.** `/tools/digital-presence-check/` asks ten questions in five areas
with Yes, No and Not sure, and names areas worth investigating with a link to
the relevant service. It gives no numerical score. It has no form element, asks
for no email address, stores nothing, and makes no network request.

**Why.** A useful free tool earns more trust than a lead capture form, and a
score would imply a technical assessment that ten self reported answers cannot
support. The page states: "This is a preliminary self-check, not a technical
audit."

**Revisit if.** A second tool is added (then `/tools/` gets an index page), or
the owner wants results to be shareable. Sharing must not require storing
answers on a server.
