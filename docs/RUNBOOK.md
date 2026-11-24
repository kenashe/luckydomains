# RUNBOOK.md

Operational procedures for luckydomains.io: deploying, changing DNS, rotating
credentials, and recovering from the failure modes this site has actually hit.

Audience: whoever is maintaining the site, human or agent.

---

## 1. Deploy a change

### Normal path
```bash
git add -A
git commit -m "Describe the change"
git push origin main
```

GitHub Pages redeploys automatically, typically within a minute. There is no
build and no pipeline to trigger.

Then verify:
```bash
python3 scripts/verify_live.py
```

### Before you push
```bash
python3 tests/test_site.py
```
CI runs the same suite, but catching it locally is faster.

### Alternative path, for agents without git credentials
```bash
export GITHUB_PAT=github_pat_...      # see .env.example
export GITHUB_REPO=luckydomains

# ALWAYS pull first. The repo may contain work you do not have locally.
python3 scripts/deploy.py pull --dir ./site-checkout

# edit files in ./site-checkout, then:
python3 scripts/deploy.py deploy --dir ./site-checkout \
    --cname luckydomains.io --message "Describe the change"
```

`deploy` refuses to run if the repository contains files your local directory
does not, and prints exactly what would be deleted. That guard exists because
the deploy replaces the branch contents wholesale. Override with
`--allow-delete` only when removal is genuinely intended.

---

## 2. Rotate the GitHub deploy token

> **Current token issued 9 August 2026 with a 90 day expiry, so it lapses around
> 7 November 2026.** Put a reminder in the calendar a week before. The symptom of
> a lapsed token is `401 Bad credentials` from any script.

Symptom: any script prints `401 Bad credentials`. Fine grained tokens expire
after 30 days by default. This is routine, not a fault.

1. GitHub > Settings > Developer settings > Personal access tokens >
   Fine-grained tokens > **Generate new token**
2. Resource owner: your account. Repository access: **Only select
   repositories** > `luckydomains`
3. Repository permissions: **Contents: Read and write**, **Workflows: Read and
   write**, and optionally **Pages: Read and write**

   Workflows write is easy to miss and is **required**: GitHub rejects any API
   push that creates or edits a file under `.github/workflows/`, which this repo
   has. Without it the deploy fails partway with an unhelpful message.

   A pre-filled link that sets the name, expiry and all three permissions, so
   you only have to pick the repository:

   ```
   https://github.com/settings/personal-access-tokens/new?name=Lucky+Domains+deploy&target_name=kenashe&expires_in=90&contents=write&pages=write&workflows=write
   ```

   Repository selection cannot be pre-filled. On the form choose **Only select
   repositories** and pick `luckydomains`
4. Generate, copy the `github_pat_...` value, and store it wherever your tooling
   reads secrets from. Never commit it.
5. Confirm: `python3 scripts/deploy.py verify`

Consider a longer expiry, or no expiry, if the rotation cadence is annoying.
The token is scoped to one repository with two permissions, so the blast radius
is small.

---

## 3. Change DNS

DNS is at **GoDaddy**, under the `luckydomains.io` domain, Manage DNS.

**Before touching anything, note the rule:** website records are the A records
on `@` and the `www` CNAME. Everything else, in particular **MX and TXT**,
carries live Google Workspace email. Do not modify or delete those.

Current correct values are in `DATA_SOURCES.md` section 3.

### If records are greyed out and cannot be edited
That is a Domain Connect lock left behind by a third party integration, in this
project's history, Wix. Disconnecting on the third party side does not always
release it.

Contact GoDaddy support and ask, naming the records exactly:

> On luckydomains.io, please remove the orphaned Domain Connect managed DNS
> records that are locked from a disconnected third party integration. Please do
> not modify my MX or TXT records.

---

## 4. Failure playbook

### The site returns 404 on luckydomains.io
Most likely the repository was made private, which silently unpublishes Pages.

1. Check visibility: `python3 scripts/deploy.py verify` prints `Private: ...`,
   or look at the repo page.
2. If private: Settings > General > Danger Zone > **Change to public**.
3. **Re-enable Pages.** Settings > Pages > Source: Deploy from a branch >
   `main` > `/root` > Save. A visibility change turns Pages off and it does not
   return by itself.
4. Confirm the Custom domain box still reads `luckydomains.io`. The committed
   `CNAME` should repopulate it.
5. `python3 scripts/verify_live.py`

Other causes: the `CNAME` file was deleted from the repo, or the apex A records
were changed at GoDaddy.

### Pages says "DNS check in progress" or "unsuccessful"
Expected right after a DNS change or a Pages re-enable. GitHub is validating the
domain before issuing a certificate.

- Confirm the apex resolves to exactly the four GitHub IPs and nothing else. A
  leftover A record from a previous host is the usual culprit.
- Click **Check again** in Settings > Pages.
- Allow up to an hour. Once it goes green, tick **Enforce HTTPS**.
- If it stalls beyond an hour: clear the Custom domain field, Save, re-enter
  `luckydomains.io`, Save. That forces a fresh check.

### HTTPS certificate warnings
Certificates are issued by GitHub after the domain validates. Immediately after
a DNS change or a Pages re-enable there is a window where the certificate does
not yet cover the domain. It resolves itself, usually within the hour. If
**Enforce HTTPS** is greyed out, the certificate has not been issued yet.

### www works but the apex does not, or vice versa
- Apex broken: check the four A records at GoDaddy.
- `www` broken: check the `www` CNAME points to `kenashe.github.io`. The 301
  from `www` to the apex is issued by GitHub and needs no configuration.
- Right after a Pages re-enable, `www` can lag the apex by a few minutes while
  the certificate is reissued for both names.

### The contact form shows "Form not yet connected"
`js/main.js` is reporting that the Web3Forms access key is missing or still the
placeholder. Check the `data-access-key` attribute on the form in
`contact/index.html`. See `DATA_SOURCES.md` section 5.

### The contact form fails when tested with curl
Not a fault. The Web3Forms free plan only accepts submissions originating from a
browser and rejects server side requests. Test in a real browser.

### Email stops working
The website and email are independent, so a site change should never cause this.
Check the MX and TXT records against `DATA_SOURCES.md` section 3 and restore any
that are missing. If they are intact, the problem is in Google Workspace, not
in DNS or this repository.

---

## 5. Regenerate brand assets

Only needed if the logo changes. Derived assets are committed.

```bash
python3 -m pip install Pillow
python3 scripts/make_assets.py
python3 tests/test_site.py
```

Sources are in `assets/source/`. The script writes the favicons, the app icons,
the transparent logos and the 1200x630 Open Graph image into `assets/`.

---

## 6. Post deployment verification

```bash
python3 scripts/verify_live.py
```

Checks the HTTP status of every page, that the apex serves real content over
HTTPS, that `www` returns a 301 to the apex, that apex DNS resolves to exactly
the four GitHub IPs, that canonicals match the sitemap, and that the Google MX
records are still present.

Manual spot checks worth doing after a visible change:
- Load the site in a browser and confirm the padlock.
- Submit the contact form and confirm the email arrives.
- Check one page on a phone width viewport.

---

## 7. Outstanding operational tasks

Not blocking, but open. Fuller detail in `DATA_SOURCES.md` and `PRODUCT.md`.

1. **Publish DKIM and DMARC records.** SPF is correct; both others are missing.
   Values and steps in `DATA_SOURCES.md` section 4.
2. **Google Search Console.** Add a **Domain property** for `luckydomains.io`,
   which covers the apex, `www`, http and https in one, and verify it with the
   TXT record GSC supplies. Then submit `https://luckydomains.io/sitemap.xml`,
   and use URL Inspection on `https://luckydomains.io/` to request indexing.
   No manual removal of the `www` URLs is needed: the automatic 301 plus the
   canonical tags consolidate them.
3. **Testimonials.** The fabricated homepage quotes are gone. Add only real,
   owner-supplied material. See `PRODUCT.md` section 8.
4. **Decide on analytics.** See `DECISIONS.md` D10.

---

## 8. Browser checks for a visible change

The test suite is static. A change to layout, motion, or the form also needs a
browser pass. Any tool works. The checks that matter:

- **Widths:** 320, 375, 390, 768, 1024 and 1440 pixels. No horizontal scroll.
- **Engines:** Chromium and Firefox at minimum. Check Safari on a Mac and on an
  iPhone before a launch. Do not report Safari as tested unless Safari or WebKit
  actually ran.
- **Accessibility:** axe-core, WCAG 2 A and AA, on every page.
- **Keyboard:** skip link, visible focus on every control, menu opens and closes
  with Escape, Pause works on the operating-status panel, FAQ and raw-evidence
  disclosures open with Enter.
- **Reduced motion:** nothing animates, nothing is hidden, and the hero buttons
  stay in the first screen.
- **No JavaScript:** navigation, every status row, every FAQ answer and all
  content are visible. The contact page shows its email fallback.
- **Console:** no errors on any page.

## 9. Test the contact form

Use a real browser. Never curl: Web3Forms sits behind Cloudflare and rejects
non-browser requests, which looks like a failure and is not one.

1. Open `/contact/`. Confirm the four paths show and that choosing a non-domain
   path hides the domain fields.
2. Submit with empty fields. The first empty required field takes focus and the
   status line asks for the highlighted fields.
3. Fill the form with a subject line that says it is a test, and submit once.
4. Expect "Thanks. Your message is on its way." and an email at
   `info@luckydomains.io` with the subject `luckydomains.io: <need> / <domain>`.
5. Do not change `data-access-key`. The tests fail if it changes.

## 10. Staging review

Staging lives outside this repository, at
`kenashe/luckydomains-design-concepts`, under `production-candidate/`. It is a
generated copy of a branch of this repository with five differences: a path
prefix, noindex, a review notice, a disabled form, and no `CNAME`. To refresh it,
run `tools/export_staging.py` in that repository against a checkout of the
branch. Never edit the staging copy by hand, and never copy a staging file back
here.

## 11. Production cutover checklist

Do these in order. Stop and roll back (section 12) on any critical failure.

1. The owner reviews staging.
2. The owner approves both draft pull requests (this repository and kenashe.ai).
3. Rebase the branch on the current `main`. Keep the shared Person schema node
   from `main` if it changed.
4. Run `python3 tests/test_site.py` and the browser checks in section 8.
5. Record the current `main` commit hash for rollback.
6. Merge the pull request to `main`.
7. Watch the Pages deployment finish (repository > Actions > pages build).
8. Run `python3 scripts/verify_live.py`.
9. Test the live contact form in a browser (section 9).
10. Verify canonicals, robots.txt, sitemap.xml, Open Graph tags, structured data
    and the legacy `.html` stubs on the live site.
11. Verify `https://www.luckydomains.io/` still 301s to the apex.
12. Verify the MX and TXT records are unchanged (`verify_live.py` checks MX).
13. Review in Safari on a Mac and on an iPhone.
14. In Search Console, resubmit `https://luckydomains.io/sitemap.xml` and inspect
    `/ventures/` and `/ventures/zerohuman/`.
15. Only now merge the kenashe.ai cross-link pull request, so its links point at
    pages that exist.
16. Capture final screenshots.

## 12. Roll back

The site is whatever `main` contains, so rolling back is a revert.

```bash
git checkout main && git pull
git revert -m 1 <merge commit>     # for a merge commit
# or, for a squash merge:  git revert <squash commit>
python3 tests/test_site.py
git push origin main
```

Pages redeploys within about a minute. Then run `python3 scripts/verify_live.py`
(its content markers on that commit match the older pages). Do not force push
`main`, do not delete the branch, and do not touch DNS: a content rollback never
needs a DNS change. If kenashe.ai cross-links were already merged, revert that
pull request too, because its links would point at pages that no longer exist.

