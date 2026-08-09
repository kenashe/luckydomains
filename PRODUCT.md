# PRODUCT.md

Product goals, scope, constraints and UX principles for the Lucky Domains
website.

---

## 1. The business

**Lucky Domains** helps businesses secure the domain name they actually want,
including names that are already registered by someone else, and then earn
search rankings so that name gets found.

Two service lines:

1. **Domain acquisition and brokerage.** Valuation, anonymous owner outreach,
   negotiation, escrow backed transfer, expiring and backorder hunting, and
   representation for sellers who want a discreet sale.
2. **SEO services.** Technical SEO, on page optimisation, content strategy,
   local SEO, authority and link building, and reporting tied to business
   outcomes rather than vanity metrics.

**Founder:** Ken Ashe. CPA, PMP, and an experienced product and project leader.
That background is a genuine differentiator against typical SEO agencies and the
site leans on it for credibility.

**Positioning line:** the wins that look like luck from the outside are the
product of preparation. Hence the name, and hence the recurring "fortune favours
the prepared" thread through the copy.

---

## 2. What the website is for

The site is a **lead generation and credibility instrument**. It is not a
storefront, an app, or a content platform.

Success means a qualified visitor understands the two services, believes this
firm is competent and trustworthy, and starts a conversation.

**Primary conversion:** the contact form on `/contact.html`.
**Secondary conversion:** a direct email to `info@luckydomains.io`.

Every page ends in a call to action pointing at one of those two.

### Audience
- Founders and business owners who cannot get the `.com` they want.
- Companies stuck on a compromised domain, with extra words or an odd extension.
- Businesses that are invisible on Google, or recovering from a bad SEO vendor.
- Companies rebranding, who need both a name and rankings.
- Domain owners who want a discreet, well negotiated sale.

Note the site sells SEO, so **the site itself is a proof point**. Sloppy
technical SEO on this site is a credibility failure, not just a missed
optimisation. That is why the URL canonicalisation work and the test suite exist.

---

## 3. Scope

### In scope
- Four core pages: Home, Services, About, Contact.
- A news/press area, currently one post at `/news/website-relaunch.html`.
- A working contact form that delivers to the owner's inbox.
- Strong technical SEO: canonical URLs, metadata, Open Graph, structured data,
  a sitemap, and fast static delivery.
- Mobile first responsive design and reasonable accessibility.

### Out of scope, for now
- E-commerce, payments, or online checkout.
- Client accounts, dashboards, or logins.
- A blog CMS. Additional posts are hand authored HTML in `news/`.
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
| Green (text safe) | `#0FA968` | Links and text on light backgrounds |
| Green (dark) | `#0b8f57` | Hover states, eyebrow text |
| Deep navy | `#0C2340` | Headings, hero background, footer |
| Mint | `#ECFBF4` | Icon badges, subtle fills |
| Soft background | `#F4F7F6` | Alternating section bands |

**Typography.** Plus Jakarta Sans (600/700/800) for headings and UI, Inter
(400/500/600) for body text, both from Google Fonts with `display=swap`.

**Logo.** The LD monogram with a four leaf clover, in green and navy. The
wordmark is used in the header, the icon in the footer. Originals are in
`assets/source/` and derived assets are regenerated with
`scripts/make_assets.py`.

**Visual register.** Confident and clean, closer to a modern professional
services firm than to a startup landing page. Navy hero with a subtle dot grid,
white content sections, generous whitespace, rounded cards with soft shadows,
one green accent band for the closing call to action.

---

## 6. UX principles

1. **Lead with the outcome, not the mechanism.** Visitors care about getting the
   name and being found, not about escrow workflows or crawl budgets.
2. **Two clear paths.** Domains and SEO are presented as equals that pair well,
   never as an upsell funnel.
3. **Always offer the next step.** Every section ends somewhere useful; no dead
   ends.
4. **Plain language.** No jargon without an immediate plain English gloss. This
   is a deliberate contrast with typical SEO vendors.
5. **Honest tone.** No fake urgency, no countdown timers, no dark patterns. The
   free consultation is described as genuinely free and obligation free.
6. **Accessible by default.** Skip link, semantic landmarks, labelled controls,
   visible focus states, sufficient contrast, and full keyboard operation.
   Animation is disabled under `prefers-reduced-motion`.
7. **Fast.** No framework, no bundle, no render blocking beyond one stylesheet
   and one font request. Images carry explicit dimensions and lazy load below
   the fold.
8. **Works without JavaScript.** Content and navigation function with JS
   disabled. Only the form's inline submission needs it, and a `mailto:`
   fallback is always present.

---

## 7. Copy rules

- **No em dashes.** An explicit owner preference, enforced by the test suite.
  Use commas, colons or separate sentences.
- **Contact details are `info@luckydomains.io` only.** No phone number, no
  business hours, no social media links. This is deliberate; do not add them.
- Short sentences. Active voice. Second person for the visitor, first person
  plural for the firm.
- No superlatives that cannot be substantiated.

---

## 8. Content status and debt

Not all copy is verified. Anyone continuing this project should know exactly
what is real and what is not.

| Item | Status | Action needed |
|---|---|---|
| Service descriptions | Real, approved by the owner | None |
| Founder bio and photo | Real, supplied by the owner | None |
| Contact email | Real and working | None |
| News post | Real, published | None |
| **Homepage testimonials** | **Fabricated placeholders** | **Replace with real quotes or remove** |
| Pricing tiers | Structure only, no figures | Owner to confirm pricing |
| Statistics band | Removed at the owner's request | None, do not reinstate invented numbers |

### The testimonials, in plain terms
The three homepage quotes attributed to "Rachel M.", "David K." and "Alicia T."
were generated as placeholders during the original build and were never
replaced. They are currently live on a commercial website. That is a credibility
risk and it runs against FTC endorsement rules, which require testimonials to
reflect genuine experiences.

They should be replaced with real client quotes or removed. Any agent working on
this site should raise it rather than continuing to ship them silently.

---

## 9. Roadmap candidates

Not committed, listed so context is not lost:

- Replace or remove the placeholder testimonials. **Highest priority.**
- Add pricing figures, or an explicit "pricing after consultation" position.
- Complete email authentication: DKIM and DMARC. See `DATA_SOURCES.md`.
- Google Search Console verification and sitemap submission.
- A small insights or guides section targeting real search intent, for example
  "how to buy a domain that is already taken". The firm sells SEO, so publishing
  useful content is both a lead source and a proof point.
- A decision on privacy respecting analytics.
- Real case studies with permission and numbers.
