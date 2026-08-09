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
**Date:** July 2026 · **Status:** done

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
