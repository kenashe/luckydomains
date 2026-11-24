# INSIGHTS.md

How an article for `/insights/` is researched, written, checked, approved by the
owner, and published. Written so that a person or a coding agent can follow it
without any prior conversation.

The short version: an article is one HTML file. You write the text, a small
script keeps the rest of the page and the library in step, and nothing is
published until Ken Ashe approves it and chooses the date.

---

## 1. What an article is

Each article is a complete page at `insights/<slug>/index.html`, served at
`https://luckydomains.io/insights/<slug>/`. Two parts of that file are yours to
edit:

1. **Settings**, a JSON block near the top of the file:

   ```html
   <script type="application/json" id="article-meta">
   {
     "title": "When to Fix a Website and When to Rebuild It",
     "description": "One or two sentences for search results.",
     "summary": "The short introduction shown under the title.",
     "category": "Guide",
     "topic": "Websites",
     "author": "Ken Ashe",
     "status": "draft",
     "drafted": "2026-11-24",
     "published": "",
     "updated": "",
     "order": 2,
     "services": ["websites", "seo", "check"],
     "related": ["what-ai-search-reads-on-your-website"],
     "sources": [
       {"title": "Site moves with URL changes", "publisher": "Google Search Central", "url": "https://..."}
     ],
     "sources_checked": "2026-11-24"
   }
   </script>
   ```

2. **The article text**, between these two comments:

   ```html
   <!-- article:start -->
   <p>Opening paragraph.</p>
   <h2 id="a-short-id">A section heading</h2>
   <p>Text.</p>
   <!-- article:end -->
   ```

Everything else in the file is rendered by `scripts/articles.py sync` from
`scripts/templates/article.html`: the page title and description, the canonical
URL, Open Graph tags, `Article` and `BreadcrumbList` structured data, the
byline, the reading time, the contents list, the sources list, the related
services and articles, and the site header and footer. Do not edit those parts
by hand. They are overwritten on the next sync.

### Settings reference

| Setting | Meaning |
|---|---|
| `title` | The headline. Also the `h1`, the Open Graph title and the structured data headline |
| `seo_title` | Optional. The browser title. Defaults to the title plus " \| Lucky Domains" |
| `description` | Meta description, 50 to 200 characters, unique across the site |
| `summary` | The introduction under the title and on the library card |
| `category` | The kind of piece: Guide, Explainer, Research |
| `topic` | The subject label: Websites, SEO, AI visibility, Digital identity, Domains |
| `author` | The byline. Owner approval is required for attribution |
| `status` | `draft` or `published`. Change it only with the `publish` command |
| `drafted` | The date the draft was written. Shown only while it is a draft |
| `published`, `updated` | Set by the `publish` and `update` commands. Never typed in by hand |
| `order` | Position among drafts in the library. Published articles sort by date, newest first |
| `services` | Pages to point readers to. Keys: `websites`, `seo`, `ai`, `entity`, `domains`, `buy`, `check`, `founder`, `contact` |
| `related` | Slugs of other articles to show under "Keep reading" |
| `sources` | The sources list: `title`, `publisher`, `url` |
| `sources_checked` | The date every source link was last opened and read |

### Building blocks for the text

Plain HTML. Give every `h2` an `id`, because the contents list is built from
them. These classes are already styled:

| Markup | Use |
|---|---|
| `<div class="callout" role="note"><p><strong>Label.</strong> Text.</p></div>` | A takeaway or a limit. Use `class="callout warn"` for a caution |
| `<ol class="flow"><li><strong>Step name.</strong> Text.</li></ol>` | A numbered sequence |
| `<figure class="art-fig"><div class="lanes"><div class="lane">...</div></div><figcaption>...</figcaption></figure>` | A side by side diagram. `lanes two` for two columns |
| `<div class="art-table" tabindex="0" role="region" aria-label="..."><table>...</table></div>` | A table that scrolls sideways on a phone. Use `<caption>` and `<th scope>` |
| `<ul class="check">` | A checklist |

Diagrams are built from HTML and CSS so they stay readable, accessible and
light. Do not add stock photos or decorative images.

---

## 2. The commands

```bash
python3 scripts/articles.py new <slug> "Article title"   # start a draft
python3 scripts/articles.py sync                         # re-render after any edit
python3 scripts/articles.py status                       # what is a draft, what is published
python3 scripts/articles.py publish <slug> --date YYYY-MM-DD
python3 scripts/articles.py publish --all --date YYYY-MM-DD
python3 scripts/articles.py update <slug> --date YYYY-MM-DD   # after a real revision
python3 tests/test_site.py                               # always, before committing
```

`sync` also refreshes the cards on `/insights/` and the article entries in
`sitemap.xml`. Standard library only. Nothing to install.

---

## 3. The editorial workflow

Nothing here is automatic. Each step has an owner.

### Step 1. Choose the question
One article answers one clearly defined question a business owner would ask.
Write the question down before anything else. If the answer is "it depends" and
nothing more, it is not ready.

### Step 2. Research
- Prefer primary sources: official documentation from Google Search Central,
  Bing, the AI platform providers, ICANN, W3C, schema.org. Avoid generic SEO
  blogs and summaries written by AI systems.
- Open and read every page you intend to cite. Documentation changes. Note the
  date you read it.
- Record what the source actually says, not what you expected it to say.
- First party examples must be real and already documented, on this site or on
  KenAshe.ai. Label them as the company's or the founder's own work.

### Step 3. Draft
```bash
python3 scripts/articles.py new <slug> "Article title"
```
Then write between the article markers. Aim for 1,000 to 1,500 words when the
subject needs it. Do not pad.

House rules, all of which apply to articles:
- No em dashes or en dashes. The test suite fails on them.
- Plain language. Explain an acronym the first time it appears.
- No guarantees of rankings, AI citations, AI recommendations or Knowledge
  Panels. No claim that special markup or a technique guarantees AI visibility.
- No invented experience, client, statistic, quotation, search result or AI
  answer. If there is no evidence, say so.
- Say what the reader can control and what they cannot.
- Link to the relevant service pages where it helps the reader, not in every
  paragraph.

### Step 4. Fact check
Before the owner sees it, check the draft against this list:

- [ ] The title matches what the article delivers.
- [ ] Every factual claim is supported by a source in the sources list, or is
      plainly the company's own practice or opinion.
- [ ] Every source link was opened today and still says what the article says.
      Set `sources_checked` to today's date.
- [ ] Nothing was invented. First party examples are labeled.
- [ ] No guarantee and no fear based claim.
- [ ] Internal links resolve. `python3 tests/test_site.py` passes.
- [ ] The description is unique and reads well in a search result.

### Step 5. Owner review
The owner reviews the draft on a staging copy or a local preview
(`docs/RUNBOOK.md` section 8). The owner approves three things separately:

1. the text
2. the byline
3. the publication date

A draft is safe to keep in the repository while this happens. It is marked
`noindex`, it is left out of the sitemap, and its byline reads "Editorial
draft".

### Step 6. Publish
Only after the owner has approved, and with the date the owner gave:

```bash
python3 scripts/articles.py publish <slug> --date 2026-12-01
python3 tests/test_site.py --launch
git add -A && git commit -m "Publish: <article title>" && git push
```

`publish` removes the draft marking, writes the date into the byline, the Open
Graph tags and the structured data, and adds the article to the sitemap. Never
type a publication date into the file by hand, and never backdate one.

### Step 7. Connect it
- Add the new slug to the `related` setting of one or two existing articles,
  then run `sync`.
- Where a service page has a "Related reading" list and the article belongs
  there, add one line to that list by hand.
- If the article changes what a service page says, change the service page too.

### Step 8. Keep it true
When a source changes or the article is revised in substance, edit it, recheck
every source, set `sources_checked`, and run:

```bash
python3 scripts/articles.py update <slug> --date YYYY-MM-DD
```

Fixing a typo does not need a new date.

---

## 4. Working with an AI assistant

An AI assistant can do steps 2 to 4 and prepare step 6. It must not do step 5.

- Give it this file, `AGENTS.md` and `PRODUCT.md`.
- Ask for the source list first, with a quotation from each source, before any
  drafting. Reject sources it did not open.
- Ask it to list every claim it could not support. Remove those claims or find
  a source.
- It may run `new`, `sync` and the tests. It may run `publish` only when the
  owner has given the date in writing.
- Unattended publication is not allowed. There is no scheduled job, and none
  should be added.

---

## 5. Backlog

Ideas only. None of these is promised or displayed on the site.

- What a Google Business Profile does, and what it cannot do, for a service
  business
- Structured data for a small business: what is worth marking up
- How to read Search Console before paying anyone for SEO
- What happens to a domain when it expires
- How to brief a website project so the quote means something
- Checking how AI assistants describe your business: a repeatable method
