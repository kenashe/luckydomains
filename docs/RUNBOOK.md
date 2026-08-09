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

Symptom: any script prints `401 Bad credentials`. Fine grained tokens expire
after 30 days by default. This is routine, not a fault.

1. GitHub > Settings > Developer settings > Personal access tokens >
   Fine-grained tokens > **Generate new token**
2. Resource owner: your account. Repository access: **Only select
   repositories** > `luckydomains`
3. Repository permissions: **Contents: Read and write**, and optionally
   **Pages: Read and write**
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
`contact.html`. See `DATA_SOURCES.md` section 5.

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
3. **Replace or remove the fabricated homepage testimonials.** See `PRODUCT.md`
   section 8.
4. **Decide on analytics.** See `DECISIONS.md` D10.
