# kenashe.ai newsroom and press release patch (Task 4, kenashe/kenashe repo)

> **Status (2026-09-20):** historical patch record. Section 4 was applied on 2026-09-10 (the founder
> profile URL is in `personKenAshe.sameAs`), and the shared Person node has since gained further
> `sameAs` entries (author profiles on 2026-09-11, Wikidata Q141507904 on 2026-09-20). The snippets
> below are not a copy of the node; the source of truth is `src/data/schema.ts` in kenashe/kenashe,
> mirrored into the three HTML files named in AGENTS.md (DECISIONS D9).

Applies to the Astro site in `kenashe/kenashe`. Two files change. Nothing here touches
`src/data/schema.ts`; the shared Person node stays byte-identical (DECISIONS D9).

## 1. `src/pages/news/site-launch.astro`: linked author byline

Insert directly after the closing `</figure>` of `.release-hero` and before `<div class="prose">`:

```astro
<!-- AUTHOR BYLINE: standard block for every kenashe.ai release. Never "Admin" or "Staff". -->
<div class="release-byline">
  <img src="/images/ken-ashe.jpeg" alt="Ken Ashe" width="48" height="48" loading="lazy" decoding="async" />
  <div>
    <span class="by">Published by</span>
    <a class="name" href="/about/" rel="author">Ken Ashe</a>
    <span class="role">
      , AI application builder, CPA, PMP. Founder and operator of
      <a href="https://luckydomains.io/founder/ken-ashe/" target="_blank" rel="noopener">Lucky Domains</a>.
    </span>
  </div>
  <time datetime="2026-06-24">June 24, 2026</time>
</div>
```

Add to the page `<style>` block:

```css
.release-byline {
  display: flex; align-items: center; gap: 0.9rem;
  margin: 0 0 2rem; padding: 0.9rem 1.1rem;
  border: 1px solid var(--border); border-radius: 6px;
}
.release-byline img { width: 48px; height: 48px; border-radius: 50%; object-fit: cover; flex: none; }
.release-byline .by { font-family: var(--font-mono); font-size: 0.6875rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); display: block; }
.release-byline .name { color: var(--fg); font-weight: 600; text-decoration: none; }
.release-byline .name:hover { color: var(--accent); }
.release-byline .role { color: var(--muted); font-size: 0.9375rem; }
.release-byline .role a { color: var(--accent); }
.release-byline time { margin-left: auto; font-family: var(--font-mono); font-size: 0.75rem; color: var(--muted); white-space: nowrap; }
.founder-quote { margin: 1.5rem 0 2rem; padding: 1.2rem 1.4rem; border-left: 3px solid var(--accent); background: var(--surface, transparent); }
.founder-quote p { margin: 0 0 0.8rem; }
.founder-quote footer { font-size: 0.9375rem; color: var(--muted); }
.founder-quote footer a { color: var(--accent); }
```

In the `releaseSchema` graph, the `NewsArticle.author` already resolves to the shared
Person `@id`. Add the cross-domain profile reference on the NewsArticle node only:

```ts
author: {
  '@id': 'https://kenashe.ai/#ken-ashe',
  subjectOf: { '@id': 'https://luckydomains.io/founder/ken-ashe/#profilepage' },
},
```

## 2. Standardized founder quote (both sites)

Replace the first quote paragraph in the `.prose` body of the release with the template.
On kenashe.ai releases the attribution is "founder of KenAshe.ai and founder and operator of
Lucky Domains"; on Lucky Domains releases it is "founder and operator of Lucky Domains".

```astro
<blockquote class="founder-quote" cite="https://kenashe.ai/about/">
  <p>
    "AI is moving too quickly for theory alone," said Ken Ashe, founder of KenAshe.ai and
    founder and operator of Lucky Domains. "The point of this site is to show the work: what
    I'm building, what shipped, what broke, and what other operators can learn from it."
  </p>
  <p>
    "The same discipline runs my agency. Lucky Domains is where the AI applications and
    automated workflows I build get tested against a real business with real clients," Ashe
    said. "A CPA and a PMP would call that controls and delivery discipline. I call it building
    in public with something at stake."
  </p>
  <footer>
    Ken Ashe is an AI application builder, CPA, and PMP who documents his work at
    <a href="/about/">KenAshe.ai</a> and is the
    <a href="https://luckydomains.io/founder/ken-ashe/" target="_blank" rel="noopener">founder and operator of Lucky Domains</a>.
  </footer>
</blockquote>
```

### Reusable quote template (fill the brackets)

```html
<blockquote class="founder-quote" cite="https://luckydomains.io/founder/ken-ashe/">
  <p>"[Quote about the announcement, one or two sentences]," said Ken Ashe, founder and operator of Lucky Domains.</p>
  <p>"[Bridge sentence: how the AI builder / operator discipline shows up in this announcement]," Ashe said.</p>
  <footer>Ken Ashe is the <a href="https://luckydomains.io/founder/ken-ashe/">founder and operator of Lucky Domains</a> and an AI application builder who documents his work at <a href="https://kenashe.ai/" rel="noopener" target="_blank">kenashe.ai</a>.</footer>
</blockquote>
```

Rules for the template:
- Attribution on first mention is always "Ken Ashe, founder and operator of Lucky Domains" (or the
  kenashe.ai variant). Never "a spokesperson", "the team", "Admin", or "Staff".
- The second paragraph is the identity bridge. It must mention AI applications or automated workflows
  AND the CPA or PMP discipline in the same breath.
- The footer links both entities every time: the founder page on luckydomains.io and kenashe.ai.
- No em dashes or en dashes anywhere (house rule on both repos).

## 3. `src/pages/newsroom/index.astro`: byline on the press release list

Add a `byline` field to each entry in `releases` and render it in the `.meta` line:

```ts
const releases = [
  {
    date: 'June 24, 2026',
    byline: 'Ken Ashe',
    bylineHref: '/about/',
    title: 'KenAshe.ai Launches as a Public Build Log for Practical AI Projects and Website Development',
    href: '/news/site-launch/',
    external: false,
    summary: '...unchanged...',
  },
  {
    date: 'June 24, 2026',
    byline: 'Ken Ashe',
    bylineHref: 'https://luckydomains.io/founder/ken-ashe/',
    title: 'Lucky Domains Launches Redesigned Website for Premium Domain Acquisition and SEO',
    href: 'https://luckydomains.io/news/website-relaunch.html',
    external: true,
    summary: '...unchanged...',
  },
];
```

```astro
<p class="meta">
  {r.date} · By <a href={r.bylineHref} target={r.external ? '_blank' : undefined} rel={r.external ? 'author noopener' : 'author'}>{r.byline}</a>
</p>
```

Also add one line to Fast Facts so the founder page is discoverable from the media kit:

```astro
<dt>Also</dt><dd>Founder and operator, <a href="https://luckydomains.io/founder/ken-ashe/" target="_blank" rel="noopener">Lucky Domains</a></dd>
```

## 4. Proposed shared-node change (requires the mirrored D9 pass)

Add the new founder profile URL to `personKenAshe.sameAs` in `src/data/schema.ts`, then mirror the
identical node into luckydomains `index.html`, `news/website-relaunch.html`, and
`founder/ken-ashe/index.html` in the same pass:

```ts
'https://luckydomains.io/founder/ken-ashe/',
```

This is deliberately NOT applied in this change set so the node stays byte-identical until the
owner does both repos together.
