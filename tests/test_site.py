#!/usr/bin/env python3
"""Test suite for the Lucky Domains static site.

    python3 tests/test_site.py

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
 13. Production pages are indexable and carry no staging or design-review text
 14. Structured data parses, and the shared Person node is identical everywhere
 15. Fonts are self hosted and no third party script or stylesheet is loaded
 16. Portfolio records show a type and a status, and limits stay visible
 17. In-page anchors that other pages link to still exist

Run it before every commit. It takes well under a second.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAIN = "https://luckydomains.io"

# Page file -> canonical URL. The single source of truth for URL shape.
PAGES = {
    "index.html": DOMAIN + "/",
    "ventures/index.html": DOMAIN + "/ventures/",
    "ventures/zerohuman/index.html": DOMAIN + "/ventures/zerohuman/",
    "ventures/ai-agent-economy/index.html": DOMAIN + "/ventures/ai-agent-economy/",
    "ventures/autonomous-seo-agent/index.html": DOMAIN + "/ventures/autonomous-seo-agent/",
    "services/index.html": DOMAIN + "/services/",
    "services/entity-seo/index.html": DOMAIN + "/services/entity-seo/",
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
# In the sitemap and crawlable, but intentionally noindex and not canonical checked.
UNLISTED = ["404.html"]

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
    'href="/ventures"', 'href="/ventures.html"', 'href="/ventures/index.html"',
    'href="/ventures/zerohuman"', 'href="/ventures/ai-agent-economy"',
    'href="/ventures/autonomous-seo-agent"', 'href="/updates/"', 'href="/founder/"',
]

# Text that belongs only to the design review or the staging copy. None of it
# may reach production (DECISIONS D13, docs/VENTURE_LAB_MIGRATION.md).
REVIEW_ONLY = [
    "Design concept only", "Not the live Lucky Domains website", "Venture Lab v2",
    "All concepts", "Selected direction refinement", "This concept proposes",
    "proposed positioning", "luckydomains-design-concepts", "production-candidate",
    "kenashe.github.io", "Facts as of", "Staging review", "Concept form",
]

# The one phrase used for what the company builds. Variants drift, so they fail.
PHRASE_VARIANTS = ["internet-native businesses", "internet-native products",
                   "internet-native companies"]

# Services the owner has not approved for sale. They must not be advertised.
UNAPPROVED_SERVICES = ["Naming across DNS and ENS", "AI consulting",
                       "AI transformation", "automation consulting",
                       "social media management services", "monthly retainer"]

# Anchors that inbound links depend on, including links from kenashe.ai.
REQUIRED_ANCHORS = {
    "services/index.html": ["domains", "selling", "websites", "seo", "identity"],
    "ventures/index.html": ["operating", "experiments", "internal", "services",
                            "zerohuman", "domain-brokerage"],
    "founder/ken-ashe/index.html": ["connect"],
    "news/index.html": ["media-resources"],
    "index.html": ["domain-desk", "featured"],
}

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
          "CNAME", ".nojekyll", "robots.txt", "sitemap.xml", "site.webmanifest",
          "README.md", "AGENTS.md", "ARCHITECTURE.md", "PRODUCT.md",
          "DECISIONS.md", "DATA_SOURCES.md", ".env.example", "docs/RUNBOOK.md",
          "docs/VENTURE_LAB_MIGRATION.md", "ventures/index.html",
          "ventures/zerohuman/index.html", "ventures/ai-agent-economy/index.html",
          "ventures/autonomous-seo-agent/index.html", "services/entity-seo/index.html",
          "news/index.html", "assets/logo-wordmark.png",
          "assets/logo-wordmark-reversed.png", "assets/fonts/inter.woff2",
          "assets/fonts/bricolage-grotesque.woff2", "assets/fonts/jetbrains-mono.woff2"]:
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
for loc in locs:
    check(loc in PAGES.values(), "sitemap lists an unexpected URL", loc)
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
for f in ALL_HTML + ["css/styles.css", "js/main.js", "robots.txt", "sitemap.xml"]:
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
check('data-access-key="78e7aac4-b264-47c3-b006-c42db75d9889"' in contact,
      "the Web3Forms access key changed, it must stay the existing key")
check("https://api.web3forms.com/submit" in read("js/main.js"),
      "main.js no longer posts to Web3Forms")
check(contact.count('type="radio" name="need"') == 4,
      "contact form should offer exactly four inquiry paths")
for path_label in ["Domain acquisition or brokerage", "Venture or product partnership",
                   "Media or speaking inquiry", "General inquiry"]:
    check(path_label in contact, "contact path missing", path_label)
check("<noscript>" in contact, "contact form lost its no JavaScript fallback")
check('role="status"' in contact, "contact form lost its status region")
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
print("13. Production pages are indexable and free of review text")
for page in PAGES:
    body = read(page)
    check('name="robots"' not in body, "production page carries a robots meta", page)
    check(body.count("<h1") == 1, "page should have exactly one h1", page)
    check('property="og:url" content="%s"' % PAGES[page] in body,
          "og:url does not match the canonical", page)
SOURCE_FILES = ALL_HTML + ["css/styles.css", "js/main.js", "sitemap.xml",
                           "robots.txt", "site.webmanifest"]
for f in SOURCE_FILES:
    body = read(f)
    for token in REVIEW_ONLY:
        check(token not in body, "review or staging text in %s" % f, token)
    for token in PHRASE_VARIANTS:
        check(token not in body, "use 'internet-native ventures' in %s" % f, token)
    for token in UNAPPROVED_SERVICES:
        check(token.lower() not in body.lower(), "unapproved service in %s" % f, token)

# ---------------------------------------------------------------------------
print("14. Structured data")
import json
ld_re = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)


def find_person(node):
    """Return the full Ken Ashe Person node (the one that carries sameAs)."""
    if isinstance(node, dict):
        if node.get("@id") == "https://kenashe.ai/#ken-ashe" and "sameAs" in node:
            return node
        for value in node.values():
            hit = find_person(value)
            if hit:
                return hit
    elif isinstance(node, list):
        for value in node:
            hit = find_person(value)
            if hit:
                return hit
    return None


persons = {}
for page in PAGES:
    for block in ld_re.findall(read(page)):
        try:
            data = json.loads(block)
        except ValueError as exc:
            check(False, "structured data does not parse in %s" % page, str(exc))
            continue
        person = find_person(data)
        if person:
            persons[page] = json.dumps(person, sort_keys=True)
for page in ["index.html", "founder/ken-ashe/index.html",
             "news/website-relaunch/index.html"]:
    check(page in persons, "shared Person node missing", page)
check(len(set(persons.values())) == 1,
      "the Ken Ashe Person node differs between pages (DECISIONS D9)",
      ", ".join(sorted(persons)))
home = read("index.html")
check('"@type": "Organization"' in home, "home page lost its Organization node")
check("Domain brokerage" in home, "Organization no longer mentions domain brokerage")
for page in ["ventures/index.html", "ventures/zerohuman/index.html", "services/index.html"]:
    check("BreadcrumbList" in read(page), "no breadcrumb markup", page)

# ---------------------------------------------------------------------------
print("15. No third party requests")
for page in ALL_HTML:
    body = read(page)
    for host in ["fonts.googleapis.com", "fonts.gstatic.com", "googletagmanager",
                 "google-analytics", "gtag(", "plausible", "hotjar", "facebook.net"]:
        check(host not in body, "third party resource in %s" % page, host)
    for src in re.findall(r'<script[^>]+src="([^"]+)"', body):
        check(src.startswith("/"), "external script in %s" % page, src)
css = read("css/styles.css")
check("@import" not in css and "http" not in css, "stylesheet loads something external")
check("prefers-reduced-motion" in css, "reduced motion block is missing from the stylesheet")
check(".skip" in css, "skip link style is missing")

# ---------------------------------------------------------------------------
print("16. Portfolio taxonomy and limits")
ventures = read("ventures/index.html")
for label in ["Autonomous service", "Experiment", "Internal operating system",
              "Commercial service", "Studio build"]:
    check('class="ty">%s<' % label in ventures, "portfolio type missing", label)
for label in ["LIVE", "SHIPPED", "ACTIVE"]:
    check("</i>%s</span>" % label in ventures, "portfolio status missing", label)
zh = read("ventures/zerohuman/index.html")
check("no outside agent has bought from it" in zh,
      "ZeroHuman page lost its outside-agent limitation")
check("no outside agent has bought from it" in home,
      "home page lost the ZeroHuman limitation")
check("A Lucky Domains venture" in zh, "ZeroHuman relationship label missing")
check("Built by" in home and "Operated by" in home,
      "home page lost the built by and operated by line")
check("The domain desk is still open." in home, "home page lost the domain desk")
check("Domains were the beginning." in home, "home page lost its headline")
for page in PAGES:
    check('href="/services/#domains"' in read(page),
          "domain acquisition is not linked from", page)
release = read("news/website-relaunch/index.html")
check("Lucky Domains Launches Redesigned Website for Premium Domain Acquisition and SEO"
      in release, "the June 2026 release headline changed")

# ---------------------------------------------------------------------------
print("17. Anchors that inbound links rely on")
for page, anchors in REQUIRED_ANCHORS.items():
    body = read(page)
    for anchor in anchors:
        check('id="%s"' % anchor in body, "anchor missing in %s" % page, "#" + anchor)
frag_re = re.compile(r'href="(/[^"#?]*)(?:\?[^"#]*)?#([^"]+)"')
for page in ALL_HTML:
    for path, frag in frag_re.findall(read(page)):
        target = "index.html" if path == "/" else path.lstrip("/") + "index.html"
        if exists(target):
            check('id="%s"' % frag in read(target),
                  "link to a missing anchor in %s" % page, "%s#%s" % (path, frag))

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
