# PRODUCT.md

Product goals, scope, constraints and UX principles for the Lucky Domains
website.

---

## 1. The business

**Lucky Domains** is a founder-led digital venture studio and operating company.
It builds and operates AI applications, digital identity systems, and
internet-native ventures. Domain acquisition and brokerage remain active.

The company began as a focused practice for domain acquisition, brokerage,
websites, and search. In November 2026 its public identity was broadened
(DECISIONS D12). It did not stop doing the original work.

What the company does, in the site's own three words:

1. **Build.** AI applications and internet-native ventures.
2. **Operate.** Autonomous services, internal systems, and digital identities.
3. **Acquire.** Private domain acquisition and brokerage for clients.

Lines of work:

- **AI applications and autonomous services.** Built in public by the founder
  and operated by the company. ZeroHuman is the first operating venture.
- **Documented experiments.** Bounded public tests with a written result, such
  as the AI Agent Economy experiment.
- **Internal systems.** Software the company runs for itself, such as the
  Autonomous SEO Agent.
- **Digital identity systems.** Domains, structured data, entity presence, and
  first-party experience with ENS.
- **Domain acquisition and brokerage.** The original practice and the clearest
  commercial service: valuation, anonymous owner outreach, negotiation against
  an agreed range, escrow backed transfer, expiring, auction and backorder
  hunting, and representation for sellers who want a discreet sale. The fee is
  success-based and agreed in writing before outreach.
- **Selected website, search, and entity work.** Taken on only where it supports
  a venture, a rebrand, a domain acquisition, or an important digital identity.

### The relationship with kenashe.ai

- **Ken Ashe** builds and documents in public. **kenashe.ai** is his personal
  creator and build-in-public site: build logs, experiments, what worked, what
  failed, evidence, videos and writing.
- **Lucky Domains** builds and operates the ventures and runs the commercial
  services. **luckydomains.io** is the company, venture home, and services site.
- **Standalone brands** may face their own users or customers. A project can be
  built or operated by Lucky Domains without using its name as a consumer brand.
- **Domain brokerage** remains an active Lucky Domains service.

luckydomains.io summarizes a project and links to the full build record on
kenashe.ai. It must not become a second build log.

### What the company does not sell

Lucky Domains is **not** a general marketing agency, **not** an open-ended web
shop, and **not** an AI consultancy. It does not sell: AI consulting, AI
transformation or automation consulting, paid ads, social media management,
monthly marketing retainers, open-ended web retainers, e-commerce platform
maintenance, visual-only redesigns, or ENS naming as a commercial service. ENS
appears as first-party experience and project evidence only.

**Founder:** Ken Ashe. Entrepreneur, AI application builder, CPA, PMP, and an
experienced product and program leader. The credentials are operating evidence,
not the headline.

**Positioning line:** "Domains were the beginning. Not the boundary." The older
line, "Fortune favors the prepared," stays as the operating philosophy on the
About page.

---

## 2. What the website is for

1. Say plainly what Lucky Domains is and does within one screen.
2. Show the real work: ventures, experiments, and internal systems, each with a
   type, a status, evidence, and its limits.
3. Keep domain acquisition and brokerage prominent and easy to reach.
4. Make the relationship between Ken Ashe, Lucky Domains, and kenashe.ai clear.
5. Give four clear ways to get in touch.

### Audience

| Audience | What they need |
|---|---|
| Domain buyers and sellers | To trust the practice, understand the process and the fee, and start an inquiry |
| Builders, partners, and technical readers | To see what is being built, how it works, what the evidence shows, and what it does not prove |
| Media and event organizers | A clear company description, the founder's background, and a contact path |
| Search engines and AI systems | Consistent, machine-readable facts about the company, the founder, and how they relate |

### Conversion paths

- **Domain acquisition or brokerage:** header call to action, the home Domain
  Desk, `/services/#domains`, `/how-we-buy-domains/`, and the first contact path.
- **Venture or product partnership:** `/ventures/` and the second contact path.
- **Media or speaking:** `/founder/ken-ashe/`, `/news/#media-resources`, and the
  third contact path.
- **General inquiry:** the fourth contact path, which also takes selected
  website and entity engagements.
- **Direct email:** `info@luckydomains.io`, in every footer.

---

## 3. Scope

### In scope
- The thirteen pages listed in `ARCHITECTURE.md` section 5
- A grouped portfolio with a type and a status on every record
- One venture page per project that has a public build record worth summarizing
- The contact form with four inquiry paths
- Structured data that states the company, the founder, and their relationship

### Out of scope, for now
- A blog or a second build log. Build records live on kenashe.ai
- A CMS, a database, accounts, or any server side code
- Analytics or tracking (DECISIONS D10)
- Pricing tables, engagement tiers, or package pages
- Testimonials, client logos, or adoption metrics that are not real and
  owner-supplied
- Press releases that the owner has not approved. The News page lists the June
  2026 release and dated project updates that link to public build records

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

The production design is Venture Lab, chosen from three reviewed concepts and
refined once (DECISIONS D13). It should feel like a premium digital venture
studio meeting an experimental technology lab: dark, quietly technical,
evidence-led, founder-led, and precise.

| Element | Value |
|---|---|
| Page background | Graphite `#0A0C0B` |
| Primary text | Warm off-white `#ECE7DC` |
| Secondary text | `#B5B6AE` and `#C9C3B8` |
| Accent | Logo green `#16C784` |
| Limits and cautions | Amber `#E6B866` |
| Domain Desk | Warm paper `#F3EFE6`, navy `#0C2340` text, green `#0A7A4B` |
| Headings | Bricolage Grotesque |
| Body | Inter |
| Metadata | JetBrains Mono, for status, dates, networks and payloads only |

Rules:

- **The logo is not redesigned.** The reversed wordmark is used on dark. The
  original full-color wordmark is used on the light Domain Desk.
- **One light moment.** The Domain Desk is the only light section. It marks the
  established client practice against the experimental work around it.
- **Evidence is the imagery.** Order of presentation: an understandable process
  first, a selected result second, raw technical evidence third.
- **Type and status are separate.** Never let a status chip stand in for what a
  thing is.
- **Motion is concentrated.** The hero may feel alive. Reading sections stay
  still. Everything stops under reduced motion.
- **No generic AI imagery,** stock photography, invented dashboards, or fake
  product interfaces.
- **Headline:** "Domains were the beginning. Not the boundary."

---

## 6. UX principles

1. **Lead with what it is, then show how it works.** A plain explanation comes
   before any payload, transaction, or diagram.
2. **Two clear paths.** What the company builds, and the domain desk. A visitor
   should be able to reach either from the first screen.
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
   and three self hosted font files. Images carry explicit dimensions and lazy load below
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

- **Every fact on a venture page comes from its public build record on
  kenashe.ai.** When that record changes, update the page here in the same pass.
- **ZeroHuman's limitation is part of the content.** As of November 20, 2026 no
  outside agent has bought from it. It stays on the home page and the venture
  page until the public record says otherwise.
- **Sir Pitches-a-Lot shows no date.** Its two public sources disagree.
- **No testimonials.** The fabricated homepage quotes were removed on
  2026-09-11 and must not return. Only real, owner-supplied material may be
  added.
- **The June 2026 release is history.** Its body is kept as published and
  describes the company as it stood then.
- **Email authentication is incomplete.** See `DATA_SOURCES.md`.

---

## 9. Roadmap candidates

- A venture page for each new project that earns one, added to its group on
  `/ventures/` with a type and a status
- An approved announcement of the broadened company, published on `/news/`
- A weekly check that flags changes on kenashe.ai build records so the summaries
  here stay current, with the owner approving each change
- Removing the legacy `.html` stubs once Search Console shows them consolidated
  (DECISIONS D11)
- Privacy friendly analytics, if the owner decides to measure (DECISIONS D10)

