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
    "services.html": DOMAIN + "/services.html",
    "about.html": DOMAIN + "/about.html",
    "contact.html": DOMAIN + "/contact.html",
    "news/website-relaunch.html": DOMAIN + "/news/website-relaunch.html",
}
# In the sitemap and crawlable, but intentionally noindex and not canonical checked.
UNLISTED = ["404.html"]

# Internal link forms that must never appear. Each points at a duplicate URL.
FORBIDDEN_LINKS = [
    'href="index.html"', "href='index.html'",
    'href="/index.html"', "href='/index.html'",
    'href="./index.html"', 'href="../index.html"',
    'href="services.html"', 'href="about.html"', 'href="contact.html"',
    'href="/services"', 'href="/about"', 'href="/contact"',
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
for f in ["index.html", "services.html", "about.html", "contact.html", "404.html",
          "news/website-relaunch.html", "css/styles.css", "js/main.js",
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
for dup in ["Disallow: /index.html", "Disallow: /services.html",
            "Disallow: /about.html", "Disallow: /contact.html", "Disallow: /\n"]:
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
contact = read("contact.html")
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
