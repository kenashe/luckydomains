# PRODUCT.md

Product goals, scope, constraints and UX principles for the Lucky Domains
website.

---

## 1. The business

**Lucky Domains** is a digital presence studio for the AI era. The company
description, used word for word across the site, is:

> Lucky Domains helps businesses build a digital presence that people, search
> engines, and AI systems can find, understand, and trust.

Five services, in the commercial order the site presents them:

1. **Website Design & Development.** A first-class commercial service, not a
   supporting capability for SEO: modern visual design, typography and layout,
   a consistent visual identity, responsive pages, intuitive navigation, clear
   calls to action, interactive elements and purposeful animation, on strong
   search, accessibility and performance foundations. Review an existing site,
   or design and build one on the client's own domain. Named engagement:
   Website Build. Lucky Domains does not sell standalone graphic design or
   brand design.
2. **SEO & Search Visibility.** One-time SEO audits, technical SEO reviews,
   scoped implementation projects, and search and content strategy. Ongoing
   optimization and monitoring by agreement. The engagement is named SEO Audits
   & Optimization. There is no named monthly package (the "Growth SEO" package
   was retired in November 2026).
3. **AI Visibility & Brand Authority.** Improve the content and supporting
   evidence that search engines and AI systems use when they understand,
   describe, cite, or answer questions about a business.
4. **Entity SEO & Digital Identity.** Establish a clear, consistent, verifiable
   identity for a person, organization, or brand. Named engagement, shared with
   AI Visibility: Entity and AI Visibility Audit.
5. **Domain Acquisition & Brokerage.** Valuation, confidential owner outreach,
   negotiation, escrow backed transfer, and representation for sellers. The
   buyer's identity is kept confidential during initial outreach and
   negotiation wherever possible; anonymity in all circumstances is never
   promised. Buyer side: the brokerage fee is success based and agreed in
   writing before outreach, and with no purchase there is no success fee.
   Seller side: brokerage is success based and agreed in writing before any
   buyer is contacted. Do not state any other fee or term.

Website design and SEO remain major commercial services. AI changes how the
work is done and where a business needs to be recognized. It does not replace
website ownership, domain ownership, technical SEO, useful content, entity
clarity, or credible third party references.

The framework that ties the services together is **Domain, Website, Search,
Entity, AI**, and the company story is **"Domains were the beginning. Not the
boundary."** The original site described the work as the name, the site, and
the rankings. The current site keeps that order and adds the two layers that
now shape how a business is understood.

Lucky Domains is **not** a venture studio, an AI agent company, a crypto
company, a technology lab, or a personal project portfolio. It does not sell AI
consulting or AI automation consulting, paid ads, social media management, or
monthly retainers. The founder's AI experiments support the company's expertise
where they are relevant. They are not the commercial offering.

**Founder:** Ken Ashe, CPA, PMP. Roughly two decades in accounting, financial
reporting, and project, product, and program leadership, and about 20 years
working with HTML, CSS, websites, and WordPress. More recently he has used
AI-assisted development to build websites and applications. Do not describe
this as 20 years of professional software engineering.

**Two sites, two jobs.** LuckyDomains.io is the commercial business. KenAshe.ai
is Ken's personal creator brand: AI application builds, experiments, writing,
videos, and speaking. The sites link to each other where a link is useful to
the reader. Neither duplicates the other.

**Location:** Berkeley Heights, New Jersey. No street address is shown.

---

## 2. What the website is for

The site is a **lead generation and credibility instrument**. It is not a
storefront or an app.

Success means a qualified visitor understands what Lucky Domains does, believes
the firm is competent and honest, and starts a conversation.

**Primary conversion:** the contact form on `/contact/`.
**Secondary conversion:** a direct email to `info@luckydomains.io`.

Every page ends in a call to action pointing at one of those two.

### How the site earns credibility
There is no portfolio and there are no client case studies, logos, or
testimonials. This is an owner decision (DECISIONS D15). Credibility comes from:

- depth of the service pages, including what the work looks at
- useful educational articles in Insights, with sources
- transparent processes, such as How we buy domains
- the founder's experience
- first party examples, always labeled as the company's or the founder's own
  work, an internal system, or research, and never as client results
- honest descriptions of what the work can and cannot promise
- a useful free tool, the Digital Presence Check

### Audience
- Businesses that need a website people, search engines, and AI systems can
  understand.
- Businesses that are hard to find in search, or recovering from a bad vendor.
- Founders and companies whose identity is inconsistent across the web.
- Businesses that want to understand how AI systems describe them.
- Founders and companies that cannot get the domain they want, and domain
  owners who want a discreet, well negotiated sale.

The site sells SEO, so **the site itself is a proof point**. Sloppy technical
SEO on this site is a credibility failure. That is why the URL rules and the
test suite exist.

---

## 3. Scope

The site has three complementary areas. Keep the structure expandable, and do
not add empty sections or placeholder pages.

### Services
- Overview at `/services/` and one page per service:
  `/services/website-design/`, `/services/seo/`, `/services/ai-visibility/`,
  `/services/entity-seo/`, `/services/domain-acquisition/`.
- One process page: `/how-we-buy-domains/`.

### Tools
- `/tools/digital-presence-check/`: ten questions in five areas, with Yes, No,
  and Not sure. It names areas worth investigating and never gives a score. It
  runs entirely in the browser: no account, no email address, no storage, no
  network request. It must always carry the sentence "This is a preliminary
  self-check, not a technical audit." There is no `/tools/` index page until
  there is more than one tool.

### Insights
- Library at `/insights/` and one page per article at `/insights/<slug>/`.
- Articles are written for business owners, cite primary sources, and are
  approved by the owner before publication. Nothing is published
  automatically. Insights is an evergreen library, not a publication with a
  schedule. See `docs/INSIGHTS.md`.

### Also in scope
- Home, About, the founder profile (`/founder/ken-ashe/`), Contact.
- News at `/news/`, listing real releases as they were published. Historical
  announcements are never rewritten to match newer positioning.
- A working contact form that delivers to the owner's inbox.
- Strong technical SEO: canonical URLs, metadata, Open Graph, structured data,
  a sitemap, and fast static delivery.
- Mobile first responsive design and accessibility.

### Interactive elements, and their limits
Two interactions carry the homepage, and motion elsewhere stays quiet:

1. **The presence map** in the hero: six signals around one identity, with
   Fragmented and Recognized states, selectable signals, and a Pause control.
2. **"What is holding you back?"** directly under the hero: five options, each
   with a starting point and a link to the relevant service.

The five layer progression draws a line once on scroll. Do not add a second
map, auto advancing widgets, carousels, sticky scroll sections, or a
questionnaire on the homepage. All motion respects `prefers-reduced-motion`,
works with keyboard and touch, and has a complete static fallback.

### Out of scope
- A portfolio, case studies, client logos, or testimonials.
- E-commerce, payments, or online checkout.
- Client accounts, dashboards, or logins.
- A CMS, a database, or a mandatory build step.
- Lead capture on the Digital Presence Check.
- Live chat, booking widgets, or third party embeds.
- Analytics and tracking, pending an explicit decision.
- Multi language or localisation.

Anything in the out of scope list becomes an architectural decision if it is
ever added. Record it in `DECISIONS.md`.

---

## 4. Constraints

| Constraint | Consequence |
|---|---|
| Free static hosting on GitHub Pages | No server side code, no redirects, no secrets, no databases |
| Repository must be public | Nothing confidential may ever be committed |
| No build step | Plain HTML, CSS and JS that a person can edit directly |
| Owner edits content himself | Markup must stay legible, no framework abstractions |
| Live business email on the domain | DNS changes must never touch MX or TXT records |
| Must remain portable | No lock in to any single AI tool or vendor |

---

## 5. Brand and design system

| Token | Value | Use |
|---|---|---|
| Brand green | `#16C784` | Accents, highlights, the CTA band |
| Green (text safe) | `#0A7A4B` | Links, button fills and text on light backgrounds. The older `#0FA968` fell short of WCAG AA on white |
| Green (dark) | `#0b8f57` | Hover states, eyebrow text |
| Deep navy | `#0C2340` | Headings, hero background, footer |
| Mint | `#ECFBF4` | Icon badges, subtle fills |
| Soft background | `#F4F7F6` | Alternating section bands |

**Typography.** Plus Jakarta Sans (600/700/800) for headings and UI, Inter
(400/500/600) for body text. Both are self hosted in `assets/fonts/` with
`font-display: swap` (DECISIONS D13).

**Logo.** The LD monogram with a four leaf clover, in green and navy. The
wordmark is used in the header, the icon in the footer. Originals are in
`assets/source/` and derived assets are regenerated with
`scripts/make_assets.py`.

**Visual register.** Confident and clean, closer to a modern professional
services firm than to a startup landing page, an agency template, or a software
dashboard. White navigation, a navy homepage hero with a subtle dot grid, short
light heroes on interior pages, white and soft grey content sections, generous
whitespace, rounded cards with soft shadows, and one green accent band for the
closing call to action. The site is predominantly light.

---

## 6. UX principles

1. **Lead with the outcome, not the mechanism.** Visitors care about getting the
   name and being found, not about escrow workflows or crawl budgets.
2. **Five services that stand on their own.** Each has its own page. Most
   visitors need one. Nobody is told they must start with a domain.
3. **Always offer the next step.** Every section ends somewhere useful; no dead
   ends.
4. **Plain language.** No jargon without an immediate plain English gloss. This
   is a deliberate contrast with typical SEO vendors.
5. **Honest tone.** No fake urgency, no countdown timers, no dark patterns. The
   free consultation is described as genuinely free and obligation free.
6. **Accessible by default.** Skip link, semantic landmarks, labelled controls,
   visible focus states, sufficient contrast, and full keyboard operation.
   Animation is disabled under `prefers-reduced-motion`.
7. **Fast.** No framework, no bundle, no third party requests, and nothing
   render blocking beyond one stylesheet. Images carry explicit dimensions and lazy load below
   the fold.
8. **Works without JavaScript.** Content and navigation function with JS
   disabled. Only the form's inline submission needs it, and a `mailto:`
   fallback is always present.

---

## 7. Copy rules

- **No em dashes.** An explicit owner preference, enforced by the test suite.
  Use commas, colons or separate sentences.
- **Contact details are `info@luckydomains.io` only.** No phone number, no
  business hours, no company social media links. This is deliberate; do not add
  them. The location shown is Berkeley Heights, New Jersey.
- **No guarantees.** Never promise rankings, AI citations or recommendations,
  mentions in any AI system, or a Knowledge Panel. Never claim that special
  markup or a proprietary technique produces AI visibility.
- **No invented proof.** No client examples, statistics, testimonials, search
  results, or AI citations that were not supplied and approved by the owner.
- **Positive, confident language.** Say what Lucky Domains does. Keep real
  limits and disclosures, state each one once, and do not criticize other
  providers. Preferred phrasings include "Flexible engagements, scoped around
  your needs", "We set realistic expectations and measure progress
  transparently", and "Sustainable, ethical search practices".
- **Plain words first.** Homepage summaries, the diagnostic and service
  introductions are written for business owners. Technical terms belong on the
  detailed service pages, with a plain explanation beside them.
- **No absolutes about search or AI systems.** They "may draw on" signals. The
  site never says every system reads or weighs the same things.
- **Response time.** "Typically within one business day", never a guarantee.
- **The Autonomous SEO Agent** appears only as the labeled first party example
  on the SEO page.
- Short sentences. Active voice. Second person for the visitor, first person
  plural for the firm.
- No superlatives that cannot be substantiated.

---

## 8. Content status and debt

| Item | Status | Action needed |
|---|---|---|
| Positioning and five services | Approved by the owner, November 2026 | None |
| Service descriptions | Approved by the owner | None |
| Founder bio and photo | Real, supplied or confirmed by the owner | None |
| Contact email | Real and working | None |
| News post (June 2026) | Real, published. Headline, text and dates left exactly as published | None |
| Insights articles | Five articles, approved by the owner and published 2026-11-25, byline Ken Ashe | Recheck sources when an article is revised (`docs/INSIGHTS.md`) |
| Pricing | No figures. Every engagement is scoped in writing | Owner to confirm if figures are ever published |
| Testimonials, client logos, case studies | None, by owner decision | Do not add |
| Statistics band | Removed at the owner's request | Do not reinstate invented numbers |

### The testimonials, in plain terms
The three homepage quotes attributed to "Rachel M.", "David K." and "Alicia T."
were generated as placeholders during the original build. They were removed on
2026-09-11. In November 2026 the owner decided the site will not showcase client
work at all (DECISIONS D15).

---

## 9. Roadmap candidates

Not committed, listed so context is not lost:

- More Insights articles, from the backlog in `docs/INSIGHTS.md`.
- A second free tool, at which point `/tools/` gets an index page.
- A documented, systematic AI visibility experiment, published only if it is
  real and the method is described.
- Complete email authentication: DKIM and DMARC. See `DATA_SOURCES.md`.
- Google Search Console sitemap resubmission after the redesign launches.
