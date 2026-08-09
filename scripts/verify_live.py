#!/usr/bin/env python3
"""Verify the LIVE luckydomains.io deployment.

Run after every deployment, and any time something looks wrong.

    python3 scripts/verify_live.py

Checks, in order:
  1. Every page returns 200 over HTTPS and serves real content
  2. www returns a 301 to the apex
  3. Apex DNS resolves to exactly the four GitHub Pages IPs
  4. www resolves to kenashe.github.io
  5. Google Workspace MX records are still present   <- protects the owner's email
  6. Each page's rel=canonical matches its sitemap entry

Exit code 0 if everything passes, 1 otherwise, so it is safe to use in CI or a
pre flight check.

Standard library only. DNS is queried over DNS-over-HTTPS so no resolver library
is needed. Note this hits the public internet; it verifies production, not a
local working copy. For local checks use tests/test_site.py.
"""
import json
import re
import ssl
import sys
import urllib.error
import urllib.request

SITE = "https://luckydomains.io"
APEX = "luckydomains.io"
PAGES = ["/", "/services.html", "/about.html", "/contact.html",
         "/news/website-relaunch.html", "/404.html"]
GITHUB_IPS = {"185.199.108.153", "185.199.109.153",
              "185.199.110.153", "185.199.111.153"}
PAGES_HOST = "kenashe.github.io"
CONTENT_MARKERS = {
    "/": "Secure the perfect domain",
    "/services.html": "Own the name your brand deserves",
    "/about.html": "Ken Ashe",
    "/contact.html": "info@luckydomains.io",
    "/news/website-relaunch.html": "Lucky Domains",
}

CTX = ssl.create_default_context()
failures = []
warnings = []


def ok(msg):
    print("  PASS  %s" % msg)


def bad(msg):
    print("  FAIL  %s" % msg)
    failures.append(msg)


def warn(msg):
    print("  WARN  %s" % msg)
    warnings.append(msg)


def fetch(url, redirect=True):
    """Return (status, headers, body_text). status is None on transport error."""
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):
            return None

    opener = (urllib.request.build_opener()
              if redirect else urllib.request.build_opener(NoRedirect))
    r = urllib.request.Request(url, headers={"User-Agent": "luckydomains-verify"})
    try:
        with opener.open(r, timeout=30) as resp:
            return resp.status, dict(resp.headers), resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read().decode("utf-8", "replace")
    except Exception as e:
        print("        (transport error: %s)" % e)
        return None, {}, ""


def dns(name, rrtype):
    """Query DNS over HTTPS. Returns a list of record data strings."""
    url = "https://dns.google/resolve?name=%s&type=%s" % (name, rrtype)
    try:
        r = urllib.request.Request(url, headers={"User-Agent": "luckydomains-verify"})
        with urllib.request.urlopen(r, timeout=20) as resp:
            return [a.get("data", "") for a in json.load(resp).get("Answer", [])]
    except Exception as e:
        print("        (dns error: %s)" % e)
        return []


print("Verifying %s\n" % SITE)

# 1. Pages respond and carry real content
print("1. Page availability over HTTPS")
for path in PAGES:
    status, _h, body = fetch(SITE + path)
    if status == 200:
        marker = CONTENT_MARKERS.get(path)
        if marker and marker not in body:
            bad("%s returned 200 but is missing expected content %r" % (path, marker))
        else:
            ok("%s -> 200" % path)
    elif status is None:
        bad("%s unreachable" % path)
    else:
        bad("%s -> %s" % (path, status))

# 2. www redirects to apex
print("\n2. www redirect")
status, headers, _b = fetch("https://www." + APEX + "/", redirect=False)
location = headers.get("Location", headers.get("location", ""))
if status in (301, 308) and APEX in location and "www." not in location:
    ok("www -> %s (%s)" % (location, status))
elif status == 200:
    warn("www returned 200 rather than redirecting. GitHub normally 301s www to "
         "the apex; this can lag for a few minutes after a Pages change.")
else:
    warn("www returned %s, Location=%r. Can be transient right after a Pages "
         "re-enable while the certificate is reissued." % (status, location))

# 3 and 4. DNS
print("\n3. Apex DNS")
a_records = set(dns(APEX, "A"))
if a_records == GITHUB_IPS:
    ok("apex resolves to exactly the four GitHub Pages IPs")
else:
    extra = a_records - GITHUB_IPS
    missing = GITHUB_IPS - a_records
    if extra:
        bad("apex has unexpected A record(s): %s. A leftover record from a "
            "previous host will break the Pages domain check." % ", ".join(sorted(extra)))
    if missing:
        bad("apex is missing GitHub IP(s): %s" % ", ".join(sorted(missing)))

print("\n4. www DNS")
cname = dns("www." + APEX, "CNAME")
if any(PAGES_HOST in c for c in cname):
    ok("www CNAME -> %s" % cname[0])
else:
    bad("www CNAME is %r, expected %s" % (cname, PAGES_HOST))

# 5. Email must be untouched
print("\n5. Email DNS (must never be broken by a website change)")
mx = dns(APEX, "MX")
if any("google" in m.lower() for m in mx):
    ok("Google Workspace MX records present (%d records)" % len(mx))
else:
    bad("Google MX records are MISSING. The owner's email may be down. "
        "Restore from DATA_SOURCES.md section 3 immediately.")

txt = dns(APEX, "TXT")
if any("v=spf1" in t for t in txt):
    ok("SPF record present")
else:
    warn("No SPF record found")
if any("v=DMARC1" in t for t in dns("_dmarc." + APEX, "TXT")):
    ok("DMARC record present")
else:
    warn("No DMARC record. Known gap, see DATA_SOURCES.md section 4.")

# 6. Canonicals agree with the sitemap
print("\n6. Canonical and sitemap agreement")
status, _h, sitemap = fetch(SITE + "/sitemap.xml")
if status != 200:
    bad("sitemap.xml -> %s" % status)
else:
    locs = set(re.findall(r"<loc>([^<]+)</loc>", sitemap))
    ok("sitemap lists %d URLs" % len(locs))
    for path in [p for p in PAGES if p != "/404.html"]:
        status, _h, body = fetch(SITE + path)
        m = re.search(r'<link rel="canonical" href="([^"]+)"', body or "")
        if not m:
            bad("%s has no canonical tag" % path)
            continue
        canon = m.group(1)
        if canon not in locs:
            bad("%s canonical %s is not in the sitemap" % (path, canon))
        else:
            ok("%s canonical matches sitemap" % path)

# Summary
print("\n" + "=" * 62)
if failures:
    print("FAILED: %d problem(s)" % len(failures))
    for f in failures:
        print("  - %s" % f)
    if warnings:
        print("plus %d warning(s)" % len(warnings))
    sys.exit(1)
print("All checks passed." + (" %d warning(s)." % len(warnings) if warnings else ""))
for w in warnings:
    print("  - %s" % w)
sys.exit(0)
