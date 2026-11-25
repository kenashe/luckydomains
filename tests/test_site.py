#!/usr/bin/env python3
"""Test suite for the Lucky Domains static site.

    python3 tests/test_site.py            # every commit, and CI
    python3 tests/test_site.py --launch   # before a production launch: also fails on draft articles

Standard library only. No packages to install, no test runner, no config.
Exit code 0 if everything passes, 1 otherwise. CI runs exactly this command.

These tests assert the things that have ACTUALLY broken on this project rather
than generic best practice:

  1. Internal links never point at a duplicate URL form (this shipped broken)
  2. Internal links resolve to files that exist
  3. Every page has a self referencing canonical matching its sitemap entry
  4. The sitemap lists every real page and nothing that does not exist
  5. Required meta, Open Graph and structured data are present
  6. No leftover placeholder tokens, for example an unconfigured form key
  7. No em dashes, a house style rule from the owner
  8. Deployment critical files are correct: CNAME, .nojekyll, robots.txt
  9. Images carry width and height, and below the fold images lazy load
 10. The contact form keeps its mailto fallback and honeypot
 11. Legacy .html stubs still redirect to the directory URL
 12. The header and footer are identical on every page
 13. Titles and descriptions are unique, and structured data is valid JSON
 14. Insights articles are in sync with scripts/articles.py, and a draft never
     carries a publication date or reaches the sitemap
 15. The Digital Presence Check stays a browser-only self-check
 16. Owner decisions hold: no portfolio, no monthly SEO package, no review banners

Run it before every commit. It takes about a second.
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAIN = "https://luckydomains.io"

# Page file -> canonical URL. The single source of truth for URL shape.
PAGES = {
    "index.html": DOMAIN + "/",
    "services/index.html": DOMAIN + "/services/",
    "services/website-design/index.html": DOMAIN + "/services/website-design/",
    "services/seo/index.html": DOMAIN + "/services/seo/",
    "services/ai-visibility/index.html": DOMAIN + "/services/ai-visibility/",
    "services/entity-seo/index.html": DOMAIN + "/services/entity-seo/",
    "services/domain-acquisition/index.html": DOMAIN + "/services/domain-acquisition/",
    "tools/digital-presence-check/index.html": DOMAIN + "/tools/digital-presence-check/",
    "insights/index.html": DOMAIN + "/insights/",
    "about/index.html": DOMAIN + "/about/",
    "contact/index.html": DOMAIN + "/contact/",
    "how-we-buy-domains/index.html": DOMAIN + "/how-we-buy-domains/",
    "news/index.html": DOMAIN + "/news/",
    "news/website-relaunch/index.html": DOMAIN + "/news/website-relaunch/",
    "founder/ken-ashe/index.html": DOMAIN + "/founder/ken-ashe/",
}
# Legacy .html URLs kept as noindex stubs that point at the directory canonical (DECISIONS D11).
STUBS = {
    "services.html": "/services/",
    "about.html": "/about/",
    "contact.html": "/contact/",
    "how-we-buy-domains.html": "/how-we-buy-domains/",
    "news/website-relaunch.html": "/news/website-relaunch/",
}
# Crawlable, but intentionally noindex and not canonical checked.
UNLISTED = ["404.html"]

# Insights articles are discovered from disk. Each one is insights/<slug>/index.html.
ARTICLE_DIR = os.path.join(ROOT, "insights")
ARTICLES = sorted(d for d in os.listdir(ARTICLE_DIR)
                  if os.path.isfile(os.path.join(ARTICLE_DIR, d, "index.html"))) if os.path.isdir(ARTICLE_DIR) else []
LAUNCH = "--launch" in sys.argv

# Internal link forms that must never appear. Each points at a duplicate URL.
FORBIDDEN_LINKS = [
    'href="index.html"', "href='index.html'",
    'href="/index.html"', "href='/index.html'",
    'href="./index.html"', 'href="../index.html"',
    # Legacy .html forms and slash-less extensionless forms. Canonical is the
    # trailing-slash directory URL, for example /services/ (DECISIONS D11).
    'href="services.html"', 'href="about.html"', 'href="contact.html"',
    'href="/services.html"', 'href="/about.html"', 'href="/contact.html"',
    'href="/how-we-buy-domains.html"', 'href="/news/website-relaunch.html"',
    'href="/services"', 'href="/about"', 'href="/contact"',
    'href="/how-we-buy-domains"', 'href="/news/website-relaunch"', 'href="/news"',
    'href="/services/entity-seo"', 'href="/services/entity-seo.html"',
    'href="/founder/ken-ashe"', 'href="/founder/ken-ashe.html"',
    'href="/founder/ken-ashe/index.html"', 'href="/services/index.html"',
    'href="/about/index.html"', 'href="/contact/index.html"',
    # Pages added with the November 2026 redesign (DECISIONS D12).
    'href="/insights"', 'href="/insights.html"', 'href="/insights/index.html"',
    'href="/services/website-design"', 'href="/services/seo"', 'href="/services/ai-visibility"',
    'href="/services/domain-acquisition"', 'href="/tools/digital-presence-check"',
    'href="/tools/"', 'href="/tools"', 'href="/founder/"', 'href="/founder"',
]

PLACEHOLDERS = [
    "YOUR_WEB3FORMS_ACCESS_KEY", "YOUR_ACCESS_KEY", "TODO", "FIXME",
    "lorem ipsum", "Lorem ipsum", "XXXX", "Your Name Here",
]

results = {"pass": 0, "fail": 0}
failures = []


def check(condition, label, detail=""):
    if condition:
        results["pass"] += 1
    else:
        results["fail"] += 1
        failures.append(label + ((": " + detail) if detail else ""))
        print("  FAIL  %s%s" % (label, (" | " + detail) if detail else ""))


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


def exists(rel):
    return os.path.isfile(os.path.join(ROOT, rel))


def html_files():
    out = []
    for dirpath, dirnames, names in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames
                       if d not in (".git", ".github", "scripts", "tests", "docs")]
        for n in names:
            if n.endswith(".html"):
                out.append(os.path.relpath(os.path.join(dirpath, n), ROOT)
                           .replace(os.sep, "/"))
    return sorted(out)


print("Testing Lucky Domains site at %s\n" % ROOT)
ALL_HTML = html_files()

# ---------------------------------------------------------------------------
print("1. Required files exist")
for f in ["index.html", "services/index.html", "about/index.html", "contact/index.html",
          "404.html", "how-we-buy-domains/index.html", "founder/ken-ashe/index.html",
          "news/website-relaunch/index.html", "css/styles.css", "js/main.js",
          "services/website-design/index.html", "services/seo/index.html",
          "services/ai-visibility/index.html", "services/entity-seo/index.html",
          "services/domain-acquisition/index.html", "insights/index.html",
          "tools/digital-presence-check/index.html", "scripts/articles.py",
          "scripts/templates/article.html", "docs/INSIGHTS.md",
          "assets/fonts/jakarta-normal-400-800.woff2", "assets/fonts/inter-normal-400-600.woff2",
          "assets/logo-icon-128.png",
          "CNAME", ".nojekyll", "robots.txt", "sitemap.xml", "site.webmanifest",
          "README.md", "AGENTS.md", "ARCHITECTURE.md", "PRODUCT.md",
          "DECISIONS.md", "DATA_SOURCES.md", ".env.example", "docs/RUNBOOK.md"]:
    check(exists(f), "missing file", f)

# ---------------------------------------------------------------------------
print("2. No internal links to duplicate URL forms")
for page in ALL_HTML:
    body = read(page)
    for bad_link in FORBIDDEN_LINKS:
        check(bad_link not in body, "duplicate URL link in %s" % page, bad_link)

# ---------------------------------------------------------------------------
print("3. Internal links resolve to real files")
href_re = re.compile(r'href="([^"]+)"')
src_re = re.compile(r'src="([^"]+)"')
for page in ALL_HTML:
    body = read(page)
    for attr_re in (href_re, src_re):
        for target in attr_re.findall(body):
            if target.startswith(("http://", "https://", "mailto:", "tel:", "#",
                                  "data:")) or not target:
                continue
            path = target.split("#")[0].split("?")[0]
            if not path:
                continue
            if path == "/":
                check(exists("index.html"), "root link target missing", page)
                continue
            rel = path.lstrip("/") if path.startswith("/") else \
                os.path.normpath(os.path.join(os.path.dirname(page), path)).replace(os.sep, "/")
            # A trailing slash is a directory index, for example /founder/ken-ashe/
            if rel.endswith("/"):
                rel = rel + "index.html"
            check(exists(rel), "broken link in %s" % page, "%s -> %s" % (target, rel))

# ---------------------------------------------------------------------------
print("4. Canonical tags are correct and self referencing")
for page, canonical in PAGES.items():
    body = read(page)
    m = re.search(r'<link rel="canonical" href="([^"]+)"', body)
    check(m is not None, "no canonical tag", page)
    if m:
        check(m.group(1) == canonical, "wrong canonical in %s" % page,
              "found %s, expected %s" % (m.group(1), canonical))

# ---------------------------------------------------------------------------
print("5. Sitemap matches the real pages")
sitemap = read("sitemap.xml")
locs = set(re.findall(r"<loc>([^<]+)</loc>", sitemap))
for page, canonical in PAGES.items():
    check(canonical in locs, "page missing from sitemap", canonical)
article_urls = set(DOMAIN + "/insights/%s/" % a for a in ARTICLES)
for loc in locs:
    check(loc in PAGES.values() or loc in article_urls, "sitemap lists an unexpected URL", loc)
check(all(loc.startswith(DOMAIN) for loc in locs),
      "sitemap contains a non apex URL",
      ", ".join(l for l in locs if not l.startswith(DOMAIN)))
check(not any("www." in loc for loc in locs),
      "sitemap references the www host",
      ", ".join(l for l in locs if "www." in l))

# ---------------------------------------------------------------------------
print("6. Required metadata is present")
for page in list(PAGES) + UNLISTED:
    body = read(page)
    check("<title>" in body, "no title tag", page)
    check('<html lang="en">' in body, "missing lang attribute", page)
    check('name="viewport"' in body, "no viewport meta", page)
    check("<h1" in body, "no h1", page)
    if page in PAGES:
        check('name="description"' in body, "no meta description", page)
        check('property="og:title"' in body, "no og:title", page)
        check('property="og:image"' in body, "no og:image", page)
        check('application/ld+json' in body, "no structured data", page)
check('name="robots" content="noindex"' in read("404.html"),
      "404 page is not noindex")

# ---------------------------------------------------------------------------
print("7. No leftover placeholders")
for page in ALL_HTML:
    body = read(page)
    for token in PLACEHOLDERS:
        check(token not in body, "placeholder left in %s" % page, token)

# ---------------------------------------------------------------------------
print("8. House style: no em dashes")
for f in ALL_HTML + ["css/styles.css", "js/main.js", "robots.txt", "sitemap.xml",
                     "scripts/articles.py", "scripts/templates/article.html", "docs/INSIGHTS.md"]:
    body = read(f)
    check("—" not in body, "em dash found in %s" % f)
    check("–" not in body, "en dash found in %s" % f)

# ---------------------------------------------------------------------------
print("9. Deployment critical files")
check(read("CNAME").strip() == "luckydomains.io", "CNAME is wrong",
      read("CNAME").strip())
robots = read("robots.txt")
check("Sitemap:" in robots, "robots.txt does not declare the sitemap")
check(DOMAIN + "/sitemap.xml" in robots, "robots.txt sitemap URL is wrong")
for dup in ["Disallow: /index.html", "Disallow: /services", "Disallow: /about",
            "Disallow: /contact", "Disallow: /news", "Disallow: /\n"]:
    check(dup not in robots, "robots.txt blocks a real page", dup.strip())

# ---------------------------------------------------------------------------
print("10. Images and performance hygiene")
img_re = re.compile(r"<img[^>]*>")
for page in ALL_HTML:
    for tag in img_re.findall(read(page)):
        check("width=" in tag and "height=" in tag,
              "image without explicit dimensions in %s" % page, tag[:70])
        check("alt=" in tag, "image without alt attribute in %s" % page, tag[:70])
lazy_count = sum(len(re.findall(r'loading="lazy"', read(p))) for p in ALL_HTML)
check(lazy_count > 0, "no images use lazy loading")

# ---------------------------------------------------------------------------
print("11. Contact form integrity")
contact = read("contact/index.html")
check('id="contact-form"' in contact, "contact form is missing")
check("data-access-key=" in contact, "form has no Web3Forms access key")
check('name="botcheck"' in contact, "form is missing its honeypot field")
check("mailto:info@luckydomains.io" in contact,
      "contact page lost its mailto fallback")
for page in list(PAGES):
    check("mailto:info@luckydomains.io" in read(page),
          "page lost the footer email link", page)
check("tel:" not in contact, "a phone number was added, owner asked for none")

# ---------------------------------------------------------------------------
print("12. Legacy .html stubs redirect to the directory canonical")
for stub, target in STUBS.items():
    check(exists(stub), "legacy stub missing", stub)
    if not exists(stub):
        continue
    body = read(stub)
    check('name="robots" content="noindex' in body, "stub is not noindex", stub)
    check('<link rel="canonical" href="%s%s">' % (DOMAIN, target) in body,
          "stub canonical does not point at the new URL", stub)
    check('http-equiv="refresh" content="0; url=%s"' % target in body,
          "stub has no instant meta refresh", stub)
    check(len(body) < 1500, "stub carries real content, it should only redirect", stub)

# ---------------------------------------------------------------------------
print("13. The header and footer are identical on every page")


def block(body, name):
    m = re.search(r"<!-- %s:start -->(.*?)<!-- %s:end -->" % (name, name), body, re.S)
    return re.sub(r' aria-current="page"', "", m.group(1)) if m else None


reference = read("index.html")
for name in ("header", "footer", "head-common"):
    ref = block(reference, name)
    check(ref is not None, "home page has no %s block" % name)
    for page in list(PAGES) + UNLISTED + ["insights/%s/index.html" % a for a in ARTICLES]:
        got = block(read(page), name)
        check(got is not None, "page has no %s block" % name, page)
        if got is not None and ref is not None:
            check(got == ref, "%s differs from the home page" % name, page)

# ---------------------------------------------------------------------------
print("14. Titles, descriptions and structured data")
titles, descs = {}, {}
for page in list(PAGES) + ["insights/%s/index.html" % a for a in ARTICLES]:
    body = read(page)
    t = re.search(r"<title>(.*?)</title>", body, re.S)
    d = re.search(r'<meta name="description" content="([^"]*)"', body)
    if t:
        check(t.group(1) not in titles, "duplicate title", "%s and %s" % (page, titles.get(t.group(1))))
        titles[t.group(1)] = page
    if d:
        check(d.group(1) not in descs, "duplicate meta description", "%s and %s" % (page, descs.get(d.group(1))))
        descs[d.group(1)] = page
        check(50 <= len(d.group(1)) <= 200, "meta description length is unusual in %s" % page, str(len(d.group(1))))
    for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', body, re.S):
        try:
            json.loads(raw)
        except ValueError as exc:
            check(False, "structured data is not valid JSON in %s" % page, str(exc))
        else:
            check(True, "structured data parses")
    check("kenashe.github.io" not in body, "a staging URL leaked into %s" % page)
    check("fonts.googleapis.com" not in body, "page loads fonts from a third party: %s" % page)
    for src in re.findall(r'<script[^>]*\ssrc="([^"]+)"', body):
        check(src == "/js/main.js", "unexpected script in %s" % page, src)
person = re.search(r'\{\s*"@type": "Person",\s*"@id": "https://kenashe\.ai/#ken-ashe",\s*"name": "Ken Ashe",\s*"alternateName".*?"knowsAbout": \[.*?\]',
                   read("index.html"), re.S)
check(person is not None, "home page lost the shared Ken Ashe Person node")
if person:
    for page in ("founder/ken-ashe/index.html", "news/website-relaunch/index.html"):
        check(person.group(0) in read(page), "the shared Person node differs in %s (DECISIONS D9)" % page)

# One Organization, described the same way on every page that describes it.
ORG_ID = DOMAIN + "/#organization"
ORG_DESCRIPTION = ("Lucky Domains is a digital presence studio for the AI era, offering website design and "
                   "development, SEO, AI visibility, digital identity, and domain acquisition and brokerage.")


def nodes(obj):
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            for n in nodes(value):
                yield n
    elif isinstance(obj, list):
        for value in obj:
            for n in nodes(value):
                yield n


org_topics, org_addresses, people = set(), set(), set()
for page in list(PAGES) + ["insights/%s/index.html" % a for a in ARTICLES]:
    for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', read(page), re.S):
        try:
            data = json.loads(raw)
        except ValueError:
            continue
        for n in nodes(data):
            if n.get("@id") == ORG_ID:
                check(n.get("name", "Lucky Domains") == "Lucky Domains", "the Organization is renamed in %s" % page)
                if "description" in n:
                    check(n["description"] == ORG_DESCRIPTION, "the Organization description differs in %s" % page,
                          n["description"][:80])
                if "knowsAbout" in n:
                    org_topics.add(json.dumps(n["knowsAbout"]))
                if "address" in n:
                    org_addresses.add(json.dumps(n["address"], sort_keys=True))
            if n.get("@id") == "https://kenashe.ai/#ken-ashe" and "url" in n:
                people.add(n["url"])
            if n.get("@type") == "Organization" and n.get("name") == "Lucky Domains":
                check(n.get("@id") == ORG_ID, "a second Lucky Domains Organization identity in %s" % page, str(n.get("@id")))
            if n.get("@type") == "ProfilePage" and "description" in n:
                check("digital presence studio" in n["description"] and "SEO practice" not in n["description"],
                      "the ProfilePage description is out of date in %s" % page, n["description"][:80])
            if n.get("@type") == "Article":
                author, publisher = n.get("author", {}), n.get("publisher", {})
                check(author.get("@id") == "https://kenashe.ai/#ken-ashe", "article author is not the shared Person record", page)
                check(publisher.get("@id") == ORG_ID, "article publisher is not the shared Organization record", page)
check(len(org_topics) == 1, "the Organization knowsAbout list differs between pages", str(len(org_topics)))
check(len(org_addresses) == 1, "the Organization address differs between pages", str(len(org_addresses)))
check(people == set(["https://kenashe.ai/"]), "the shared Person record is given more than one url", str(sorted(people)))

# ---------------------------------------------------------------------------
print("15. Insights articles")
check(len(ARTICLES) > 0, "no Insights articles found")
sync = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "articles.py"), "sync", "--check"],
                      stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
check(sync.returncode == 0, "articles are out of sync, run: python3 scripts/articles.py sync", sync.stdout.strip()[:300])
insights_index = read("insights/index.html")
drafts = []
for a in ARTICLES:
    page = "insights/%s/index.html" % a
    body = read(page)
    url = DOMAIN + "/insights/%s/" % a
    check('<link rel="canonical" href="%s">' % url in body, "wrong canonical in %s" % page)
    check('href="/insights/%s/"' % a in insights_index, "article is not listed on /insights/", a)
    check('"@type": "Article"' in body and '"@type": "BreadcrumbList"' in body, "article lacks Article or BreadcrumbList data", page)
    check(body.count("<h1") == 1, "article needs exactly one h1", page)
    check('id="sources"' in body, "article has no sources section", page)
    meta = re.search(r'<script type="application/json" id="article-meta">(.*?)</script>', body, re.S)
    check(meta is not None, "article has no article-meta block", page)
    status = json.loads(meta.group(1)).get("status") if meta else None
    if status == "draft":
        drafts.append(a)
        check('"datePublished"' not in body, "a draft carries a publication date", page)
        check('<meta name="robots" content="noindex">' in body, "a draft is indexable", page)
        check("Editorial draft" in body, "a draft is not labelled as a draft", page)
        check(url not in locs, "a draft is in the sitemap", url)
    else:
        check('"datePublished"' in body, "a published article has no datePublished", page)
        check('name="robots"' not in body, "a published article carries a robots meta tag", page)
        check("Editorial draft" not in body, "a published article is still labelled a draft", page)
        check(url in locs, "a published article is missing from the sitemap", url)
if drafts:
    print("  NOTE  %d draft article(s), not indexable and not in the sitemap: %s" % (len(drafts), ", ".join(drafts)))
    if LAUNCH:
        check(False, "launch check: draft articles remain. Publish them with an owner-approved date or remove them",
              ", ".join(drafts))

# ---------------------------------------------------------------------------
print("16. Digital Presence Check stays a browser-only self-check")
dpc = read("tools/digital-presence-check/index.html")
check("This is a preliminary self-check, not a technical audit." in dpc, "the self-check statement is missing")
check("<form" not in dpc, "the check must not contain a form element")
check(len(re.findall(r'<fieldset class="dq"', dpc)) == 10, "the check should have ten questions")
check(all(re.fullmatch(r"dpc-\d+", n) for n in re.findall(r'<input[^>]*\sname="([^"]+)"', dpc)),
      "the check collects a named field other than its own radio groups")
check('type="email"' not in dpc and 'type="text"' not in dpc, "the check asks for typed input")
script = read("js/main.js")
for token in ("localStorage", "sessionStorage", "document.cookie", "sendBeacon", "XMLHttpRequest"):
    check(token not in script, "js/main.js uses %s, the site stores and sends nothing but the contact form" % token)
check(script.count("fetch(") == 1, "js/main.js should make exactly one network request, the contact form",
      str(script.count("fetch(")))

# ---------------------------------------------------------------------------
print("17. Owner decisions")
release = "news/website-relaunch/index.html"       # history, left exactly as published
for page in ALL_HTML:
    if page == release or page in STUBS:
        continue
    body = read(page)
    visible = re.sub(r'href="[^"]*"', "", body)
    check(not re.search(r'href="/work/|href="/portfolio/|href="/case-stud', body), "portfolio link in %s" % page)
    check(not re.search(r"case stud|testimonial|our portfolio|selected work", visible, re.I),
          "portfolio or testimonial wording in %s" % page)
    check("Growth SEO" not in body, "the retired Growth SEO package is named in %s" % page)
    check("SEO Audit or Project" not in body, "the earlier engagement name is used in %s" % page)
    check(not re.search(r"domain acquisition, brokerage,? and SEO|SEO practice run with", body, re.I),
          "the earlier company description is used in %s" % page)
    check(not re.search(r"Design concept only|Staging review|noindex,nofollow,noarchive", body),
          "a review or staging banner leaked into %s" % page)
    check(not re.search(r"guaranteed? (rankings|ranking|citations|placement)", re.sub(r"(no|not|never|cannot|without|do not)[^.]{0,80}guarantee", "", body, flags=re.I), re.I),
          "a guarantee claim in %s" % page)
for page in PAGES:
    if page == release:
        continue
    check('name="robots"' not in read(page), "an indexable page carries a robots meta tag", page)
check("<h3>SEO Audits &amp; Optimization</h3>" in read("services/index.html"), "the SEO engagement is not named SEO Audits & Optimization")

# ---------------------------------------------------------------------------
print("\n" + "=" * 62)
total = results["pass"] + results["fail"]
if results["fail"]:
    print("FAILED  %d/%d checks failed" % (results["fail"], total))
    print("\nFailures:")
    for f in sorted(set(failures)):
        print("  - %s" % f)
    sys.exit(1)
print("PASSED  all %d checks" % total)
sys.exit(0)
