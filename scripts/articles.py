#!/usr/bin/env python3
"""Keep the Insights article library in sync.

Standard library only. This is a convenience, not a build step: every article is
a complete HTML page committed at insights/<slug>/index.html, and the site still
deploys with a plain git push. The script only keeps the repetitive parts
consistent so nobody has to recreate the layout by hand.

    python3 scripts/articles.py new <slug> "Article title"
    python3 scripts/articles.py sync            # re-render articles, the Insights index and the sitemap
    python3 scripts/articles.py sync --check    # exit 1 if anything is out of date (used by the tests)
    python3 scripts/articles.py publish <slug> --date YYYY-MM-DD
    python3 scripts/articles.py publish --all --date YYYY-MM-DD
    python3 scripts/articles.py publish --all --date YYYY-MM-DD --redate   # correct the date before launch
    python3 scripts/articles.py update <slug> --date YYYY-MM-DD
    python3 scripts/articles.py status

How an article page is organised
  1. Settings live in the page itself, in <script type="application/json" id="article-meta">.
  2. The article text lives between <!-- article:start --> and <!-- article:end -->.
     Write plain HTML there: <h2 id="...">, <p>, <ul>, <table>, <figure>.
  3. Everything else on the page (head tags, structured data, byline, contents
     list, sources, related links, header and footer) is rendered from those two
     things by `sync`, using scripts/templates/article.html. The header, footer
     and shared head tags are copied from insights/index.html, so articles can
     never drift from the rest of the site.

Rules this script enforces
  - A draft is never given a publication date. Drafts carry noindex, stay out of
    the sitemap, and show "Editorial draft" in the byline.
  - Publication dates are set only by `publish`, with a date the owner chooses.
  - Nothing is published automatically. `publish` edits files; a person still
    reviews, commits and pushes.

Full instructions: docs/INSIGHTS.md
"""
import datetime
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAIN = "https://luckydomains.io"
INDEX = "insights/index.html"
TEMPLATE = "scripts/templates/article.html"
SITEMAP = "sitemap.xml"
WORDS_PER_MINUTE = 230

# Pages an article can point readers to. Keys are used in the "services" setting.
SERVICES = {
    "websites": ("Website Design & Development", "/services/website-design/",
                 "Thoughtful design on strong technical and search foundations."),
    "seo": ("SEO & Search Visibility", "/services/seo/",
            "Technical health, useful content, and earned authority."),
    "ai": ("AI Visibility & Brand Authority", "/services/ai-visibility/",
           "Clear, consistent evidence for search engines and AI systems to draw on."),
    "entity": ("Entity SEO & Digital Identity", "/services/entity-seo/",
               "One verifiable identity across your site and your profiles."),
    "domains": ("Domain Acquisition & Brokerage", "/services/domain-acquisition/",
                "The right name, even when someone else owns it."),
    "buy": ("How we buy domains", "/how-we-buy-domains/",
            "The Lucky Domains acquisition process, step by step."),
    "check": ("Digital Presence Check", "/tools/digital-presence-check/",
              "Ten questions, about two minutes. Nothing is stored or sent."),
    "founder": ("About the founder", "/founder/ken-ashe/",
                "Ken Ashe, CPA, PMP, founder and operator."),
    "contact": ("Talk to Ken", "/contact/",
                "The first consultation is free, with no obligation."),
}
KINDS = {"websites": "Service", "seo": "Service", "ai": "Service", "entity": "Service",
         "domains": "Service", "buy": "Process", "check": "Free tool",
         "founder": "Founder", "contact": "Contact"}

META_RE = re.compile(r'<script type="application/json" id="article-meta">\s*(.*?)\s*</script>', re.S)
BODY_RE = re.compile(r"<!-- article:start -->\n?(.*?)\n?<!-- article:end -->", re.S)
H2_RE = re.compile(r'<h2 id="([^"]+)">(.*?)</h2>', re.S)
E = html.escape


def path(rel):
    return os.path.join(ROOT, rel)


def read(rel):
    with open(path(rel), encoding="utf-8") as fh:
        return fh.read()


def between(text, name, rel):
    m = re.search(r"<!-- %s:start -->\n?(.*?)\n?<!-- %s:end -->" % (name, name), text, re.S)
    if not m:
        sys.exit("%s has no <!-- %s:start --> ... <!-- %s:end --> block" % (rel, name, name))
    return m.group(1)


def replace_between(text, name, new, rel):
    pat = re.compile(r"(<!-- %s:start -->)\n.*?([ \t]*<!-- %s:end -->)" % (name, name), re.S)
    if not pat.search(text):
        sys.exit("%s has no <!-- %s:start --> ... <!-- %s:end --> block" % (rel, name, name))
    return pat.sub(lambda m: m.group(1) + "\n" + (new + "\n" if new else "") + m.group(2), text, count=1)


def long_date(iso):
    d = datetime.date.fromisoformat(iso)
    return "%s %d, %d" % (d.strftime("%B"), d.day, d.year)


def slugs():
    base = path("insights")
    return sorted(d for d in os.listdir(base)
                  if os.path.isfile(os.path.join(base, d, "index.html")))


def load(slug):
    rel = "insights/%s/index.html" % slug
    text = read(rel)
    m, b = META_RE.search(text), BODY_RE.search(text)
    if not m or not b:
        sys.exit("%s is missing its article-meta block or its article:start/end markers" % rel)
    try:
        meta = json.loads(m.group(1))
    except ValueError as exc:
        sys.exit("%s: the article-meta block is not valid JSON (%s)" % (rel, exc))
    for key in ("title", "description", "summary", "category", "topic", "author", "status"):
        if not str(meta.get(key, "")).strip():
            sys.exit("%s: the article-meta block needs a value for %r" % (rel, key))
    if meta["status"] not in ("draft", "published"):
        sys.exit("%s: status must be draft or published" % rel)
    if meta["status"] == "published" and not meta.get("published"):
        sys.exit("%s: a published article needs a published date. Use `publish`." % rel)
    if meta["status"] == "draft" and meta.get("published"):
        sys.exit("%s: a draft must not carry a published date" % rel)
    meta["slug"] = slug
    return meta, b.group(1).strip("\n"), text


def minutes(body):
    words = len(re.sub(r"<[^>]+>", " ", body).split())
    return max(1, int(round(words / float(WORDS_PER_MINUTE))))


def sort_key(meta):
    if meta["status"] == "published":
        # newest first; articles published on the same day keep their "order" setting
        return (0, -datetime.date.fromisoformat(meta["published"]).toordinal(), meta.get("order", 99), meta["slug"])
    return (1, meta.get("order", 99), meta["slug"])


def status_text(meta):
    if meta["status"] == "published":
        out = "Published %s" % long_date(meta["published"])
        if meta.get("updated") and meta["updated"] != meta["published"]:
            out += ", updated %s" % long_date(meta["updated"])
        return out
    return "Editorial draft"


def date_line(meta):
    if meta["status"] == "published":
        out = 'Published <time datetime="%s">%s</time>' % (meta["published"], long_date(meta["published"]))
        if meta.get("updated") and meta["updated"] != meta["published"]:
            out += ', updated <time datetime="%s">%s</time>' % (meta["updated"], long_date(meta["updated"]))
        return out
    drafted = (", %s" % long_date(meta["drafted"])) if meta.get("drafted") else ""
    return '<span class="art-draft">Editorial draft%s. Not yet published.</span>' % drafted


def jsonld(meta, url):
    article = {
        "@type": "Article",
        "@id": url + "#article",
        "headline": meta["title"],
        "description": meta["description"],
        "url": url,
        "mainEntityOfPage": url,
        "inLanguage": "en-US",
        "articleSection": meta["topic"],
        "image": DOMAIN + "/assets/og-image.png",
        # The author is the shared Ken Ashe Person record. Keep these values the same as that record
        # (AGENTS.md section 7): one @id, one url. The visible byline links to the founder page.
        "author": {"@type": "Person", "@id": "https://kenashe.ai/#ken-ashe", "name": meta["author"],
                   "url": "https://kenashe.ai/"},
        "publisher": {"@type": "Organization", "@id": DOMAIN + "/#organization", "name": "Lucky Domains",
                      "url": DOMAIN + "/"},
        "isPartOf": {"@id": DOMAIN + "/#website"},
    }
    if meta["status"] == "published":
        article["datePublished"] = meta["published"]
        article["dateModified"] = meta.get("updated") or meta["published"]
    crumbs = {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN + "/"},
            {"@type": "ListItem", "position": 2, "name": "Insights", "item": DOMAIN + "/insights/"},
            {"@type": "ListItem", "position": 3, "name": meta["title"], "item": url},
        ],
    }
    return json.dumps({"@context": "https://schema.org", "@graph": [article, crumbs]},
                      indent=2, ensure_ascii=False)


def card(meta, level="h3"):
    return ('<article class="card ins-card reveal"><p class="art-kind">%s · %s</p>'
            '<%s><a href="/insights/%s/">%s</a></%s><p>%s</p>'
            '<p class="ins-meta">%s<span class="art-dot" aria-hidden="true"></span>%d min read</p></article>'
            % (E(meta["category"]), E(meta["topic"]), level, meta["slug"], E(meta["title"]), level,
               E(meta["summary"]), status_text(meta), meta["minutes"]))


def render(meta, body, chrome, library):
    url = "%s/insights/%s/" % (DOMAIN, meta["slug"])
    stored = dict((k, v) for k, v in meta.items() if k not in ("slug", "minutes"))
    toc = ['        <li><a href="#%s">%s</a></li>' % (i, re.sub(r"<[^>]+>", "", t).strip())
           for i, t in H2_RE.findall(body)]
    sources = ""
    if meta.get("sources"):
        toc.append('        <li><a href="#sources">Sources</a></li>')
        items = "".join('<li><a href="%s" rel="noopener">%s</a>%s</li>'
                        % (E(s["url"]), E(s["title"]), (", " + E(s["publisher"])) if s.get("publisher") else "")
                        for s in meta["sources"])
        checked = ('<p class="art-checked">Links checked %s.</p>' % long_date(meta["sources_checked"])
                   if meta.get("sources_checked") else "")
        sources = '<section class="art-sources" id="sources"><h2>Sources</h2><ol>%s</ol>%s</section>' % (items, checked)
    services = ""
    if meta.get("services"):
        cards = ""
        for key in meta["services"]:
            if key not in SERVICES:
                sys.exit("insights/%s: unknown service key %r. Known keys: %s"
                         % (meta["slug"], key, ", ".join(sorted(SERVICES))))
            name, href, line = SERVICES[key]
            cards += ('<a class="card art-svc reveal" href="%s"><span class="tag">%s</span><strong>%s</strong><span>%s</span></a>'
                      % (href, KINDS[key], E(name), E(line)))
        services = ('<section class="section section-soft art-next" aria-labelledby="art-next-h"><div class="container">'
                    '<h2 id="art-next-h">Where Lucky Domains can help</h2><div class="art-svcs">%s</div></div></section>' % cards)
    related = ""
    rel_cards = "".join(card(library[s]) for s in meta.get("related", []) if s in library)
    for s in meta.get("related", []):
        if s not in library:
            sys.exit("insights/%s: related article %r does not exist" % (meta["slug"], s))
    if rel_cards:
        related = ('<section class="section art-related" aria-labelledby="art-rel-h"><div class="container">'
                   '<h2 id="art-rel-h">Keep reading</h2><div class="grid grid-2">%s</div>'
                   '<p class="center v3-more"><a class="link-arrow" href="/insights/">All insights</a></p></div></section>' % rel_cards)
    og_dates = ""
    if meta["status"] == "published":
        og_dates = '<meta property="article:published_time" content="%s">\n' % meta["published"]
        og_dates += '<meta property="article:modified_time" content="%s">\n' % (meta.get("updated") or meta["published"])
    values = {
        "seo_title": E(meta.get("seo_title") or (meta["title"] + " | Lucky Domains")),
        "title": E(meta["title"]),
        "description": E(meta["description"]),
        "summary": E(meta["summary"]),
        "category": E(meta["category"]),
        "topic": E(meta["topic"]),
        "author": E(meta["author"]),
        "url": url,
        "robots": '<meta name="robots" content="noindex">\n' if meta["status"] == "draft" else "",
        "og_dates": og_dates,
        "head_common": "<!-- head-common:start -->\n%s\n<!-- head-common:end -->" % chrome["head-common"],
        "header": "<!-- header:start -->\n%s\n<!-- header:end -->" % chrome["header"],
        "footer": "<!-- footer:start -->\n%s\n<!-- footer:end -->" % chrome["footer"],
        "jsonld": jsonld(meta, url),
        "meta_json": json.dumps(stored, indent=2, ensure_ascii=False).replace("</", "<\\/"),
        "date_line": date_line(meta),
        "minutes": str(meta["minutes"]),
        "toc": "\n".join(toc),
        "body": body,
        "sources": sources,
        "services": services,
        "related": related,
    }
    out = read(TEMPLATE)
    for key, value in values.items():
        out = out.replace("{{%s}}" % key, value)
    left = re.findall(r"\{\{[a-z_]+\}\}", out.replace(body, ""))
    if left:
        sys.exit("template placeholders were not filled: %s" % ", ".join(sorted(set(left))))
    return out


def sync(check=False):
    index = read(INDEX)
    chrome = dict((name, between(index, name, INDEX)) for name in ("head-common", "header", "footer"))
    library = {}
    for slug in slugs():
        meta, body, _ = load(slug)
        meta["minutes"] = minutes(body)
        library[slug] = (meta, body)
    metas = dict((s, m) for s, (m, _) in library.items())
    ordered = sorted(metas.values(), key=sort_key)
    outputs = {}
    for slug, (meta, body) in library.items():
        outputs["insights/%s/index.html" % slug] = render(meta, body, chrome, metas)
    cards = "\n".join("      " + card(m, "h2") for m in ordered)
    outputs[INDEX] = replace_between(index, "articles", cards, INDEX)
    lines = []
    for m in ordered:
        if m["status"] != "published":
            continue
        lines.append("  <url><loc>%s/insights/%s/</loc><lastmod>%s</lastmod><changefreq>yearly</changefreq>"
                     "<priority>0.6</priority></url>" % (DOMAIN, m["slug"], m.get("updated") or m["published"]))
    outputs[SITEMAP] = replace_between(read(SITEMAP), "insights", "\n".join(lines), SITEMAP)
    changed = []
    for rel, text in sorted(outputs.items()):
        if read(rel) != text:
            changed.append(rel)
            if not check:
                with open(path(rel), "w", encoding="utf-8") as fh:
                    fh.write(text)
    drafts = [m["slug"] for m in ordered if m["status"] == "draft"]
    if check:
        if changed:
            print("Out of date. Run: python3 scripts/articles.py sync")
            for rel in changed:
                print("  " + rel)
            return 1
        print("In sync: %d articles (%d draft)." % (len(ordered), len(drafts)))
        return 0
    print("Synced %d articles (%d draft). Files rewritten: %d." % (len(ordered), len(drafts), len(changed)))
    for rel in changed:
        print("  " + rel)
    return 0


def set_meta(slug, changes):
    meta, _, text = load(slug)
    stored = dict((k, v) for k, v in meta.items() if k != "slug")
    stored.update(changes)
    block = ('<script type="application/json" id="article-meta">\n%s\n</script>'
             % json.dumps(stored, indent=2, ensure_ascii=False).replace("</", "<\\/"))
    with open(path("insights/%s/index.html" % slug), "w", encoding="utf-8") as fh:
        fh.write(META_RE.sub(lambda m: block, text, count=1))


def need_date(args):
    if "--date" not in args:
        sys.exit("Give the date the owner approved: --date YYYY-MM-DD")
    value = args[args.index("--date") + 1]
    try:
        datetime.date.fromisoformat(value)
    except ValueError:
        sys.exit("--date must look like 2026-12-01")
    return value


def main(argv):
    if not argv:
        print(__doc__)
        return 0
    cmd, args = argv[0], argv[1:]
    if cmd == "sync":
        return sync(check="--check" in args)
    if cmd == "status":
        for slug in slugs():
            meta, body, _ = load(slug)
            print("%-10s %-46s %s" % (meta["status"], slug, meta.get("published") or "no publication date"))
        return 0
    if cmd == "publish":
        date = need_date(args)
        targets = slugs() if "--all" in args else [a for a in args if not a.startswith("--") and a != date]
        if not targets:
            sys.exit("Name an article slug, or use --all")
        for slug in targets:
            meta, _, _ = load(slug)
            if meta["status"] == "published" and "--redate" not in args:
                print("already published, left alone: %s (add --redate to correct its date before it goes live)" % slug)
                continue
            set_meta(slug, {"status": "published", "published": date, "updated": date})
            print("published %s on %s" % (slug, date))
        return sync()
    if cmd == "update":
        date = need_date(args)
        targets = [a for a in args if not a.startswith("--") and a != date]
        for slug in targets:
            meta, _, _ = load(slug)
            if meta["status"] != "published":
                sys.exit("%s is a draft. Publish it first." % slug)
            set_meta(slug, {"updated": date})
        return sync()
    if cmd == "new":
        if len(args) < 2:
            sys.exit('Usage: python3 scripts/articles.py new <slug> "Article title"')
        slug, title = args[0], args[1]
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug):
            sys.exit("Use a lowercase slug with hyphens, for example how-domain-escrow-works")
        rel = "insights/%s/index.html" % slug
        if os.path.exists(path(rel)):
            sys.exit("%s already exists" % rel)
        meta = {"title": title, "description": "One or two sentences for search results, under 160 characters.",
                "summary": "The short introduction shown under the title.", "category": "Guide", "topic": "Websites",
                "author": "Ken Ashe", "status": "draft", "drafted": datetime.date.today().isoformat(),
                "published": "", "updated": "", "order": 50, "services": ["check", "contact"], "related": [],
                "sources": [], "sources_checked": ""}
        body = ('<h2 id="first-section">First section heading</h2>\n'
                "<p>Write the article here. Give every h2 an id so it appears in the contents list.</p>")
        os.makedirs(os.path.dirname(path(rel)))
        with open(path(rel), "w", encoding="utf-8") as fh:
            fh.write('<script type="application/json" id="article-meta">\n%s\n</script>\n'
                     "<!-- article:start -->\n%s\n<!-- article:end -->\n" % (json.dumps(meta, indent=2), body))
        print("created %s as a draft" % rel)
        return sync()
    sys.exit("Unknown command %r. Run with no arguments for help." % cmd)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
