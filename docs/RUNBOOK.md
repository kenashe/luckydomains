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
3. **Decide on analytics.** See `DECISIONS.md` D10.
4. **Delete the legacy `.html` stubs** once Search Console shows the `.html`
   URLs dropped (DECISIONS D11).

---

## 8. Staging review for a large change

Small edits go straight to `main`. A redesign, a new section, or a batch of
articles goes through a branch, a draft pull request and a staging copy, and
reaches `main` only when the owner says so.

1. Work on a named branch, for example `digital-presence-production-candidate`.
   Open a **draft** pull request against `main`. Do not merge it.
2. Export a staging copy from the branch into the separate review repository,
   `kenashe/luckydomains-design-concepts`:

   ```bash
   # in a checkout of kenashe/luckydomains-design-concepts
   python3 tools/dp_export.py /path/to/luckydomains-checkout
   ```

   The export refuses to run from `main` or with uncommitted changes, so the
   staging copy always matches a commit. It records that commit in
   `STAGING.json`.
3. The staging copy lives at
   `https://kenashe.github.io/luckydomains-design-concepts/digital-presence-production-candidate/`.
   The export makes only these changes, and checks each one before it finishes:
   a path prefix on root absolute links; `noindex,nofollow,noarchive` on every
   page; staging canonical and social URLs; a notice bar; and a disabled contact
   form (access key removed, endpoint replaced, submit blocked). It leaves out
   `CNAME`, `robots.txt`, `sitemap.xml`, documentation, tests and scripts.
4. Never edit the staging copy by hand, and never point a custom domain,
   analytics, or a live form at it.

The staging copy cannot prove three things, because they only exist on the real
domain: the contact form delivering mail, the legacy stubs and `www`
redirecting, and the `404.html` page being served for missing paths. Check
those after launch (section 9).

---

## 9. Launch checklist for the November 2026 redesign

Prepared, not executed. Every step that changes production needs the owner's
explicit approval. Work top to bottom and stop at the first failure.

**Before the merge**

1. The owner has reviewed the complete staging site.
2. The owner has approved the text of all five Insights articles.
3. The owner has approved the byline and given the publication date or dates.
4. Safari on a Mac and on an iPhone has been checked by a person. The automated
   checks ran in Chromium and Firefox only.
5. Bring the branch up to date with `main` and resolve anything that changed:

   ```bash
   git fetch origin && git checkout digital-presence-production-candidate
   git merge origin/main        # or rebase, then re-export staging if anything changed
   ```

   If `main` changed the shared Ken Ashe `Person` node, mirror the new node into
   the three pages that carry it (AGENTS.md section 7).
6. Set the publication dates the owner gave, then run the launch tests:

   ```bash
   python3 scripts/articles.py publish --all --date YYYY-MM-DD
   python3 tests/test_site.py --launch
   ```

   Commit and push the branch. CI must be green on the pull request.
7. Record the commit that is live now. This is the rollback point:

   ```bash
   git rev-parse origin/main
   ```

   When the candidate was prepared it was
   `efed1ded196d8ecc157f6d02f41f170b69033f45`.

**The merge**

8. The owner marks the pull request ready and merges it, or tells an agent in
   writing to merge it. Use a merge commit, not a squash, so the rollback in
   section 10 is a single revert. GitHub Pages redeploys within a few minutes.

**After the merge**

9. Run `python3 scripts/verify_live.py`. It checks every page, the `www`
   redirect, DNS and that the Google Workspace MX records are untouched.
10. In a browser, on the live domain:
    - navigation, the Services menu and the mobile menu
    - the presence map, its Pause control and the diagnostic
    - the Digital Presence Check
    - one article, including its contents list
    - `https://luckydomains.io/services.html` and the other legacy stubs
      redirect to the directory URLs
    - a missing path such as `/nope` shows the 404 page
11. Submit the contact form once from a browser, with a message that says it is
    a launch test, and confirm the email arrives at `info@luckydomains.io`.
    Do not test with curl; Web3Forms rejects it (section 4).
12. View source on the home page and one article. Confirm the canonical URL is
    on `luckydomains.io`, there is no `noindex` on indexable pages, and no
    staging URL appears. Paste the home page and one article into Google's Rich
    Results Test and the Schema Markup Validator.
13. Open `https://luckydomains.io/sitemap.xml` and confirm the five article
    URLs are listed. In Search Console, resubmit the sitemap and request
    indexing for the home page and `/insights/`.
14. Only now merge the KenAshe.ai pull request that updates its description of
    Lucky Domains and links to the new pages. Its links point at pages that
    must already be live.
15. Capture final screenshots of the live site for the record.

Any failure at steps 9 to 12 that a visitor would notice triggers section 10.

---

## 10. Rollback

GitHub Pages serves whatever `main` contains, so a rollback is a commit.

**Preferred: revert the merge.** This keeps history and needs no force push.

```bash
git fetch origin && git checkout main && git pull
git log --oneline -5                      # find the merge commit
git revert -m 1 <merge-commit-sha>        # creates a new commit that undoes it
python3 tests/test_site.py
git push origin main
python3 scripts/verify_live.py            # after Pages redeploys
```

**If the merge was a squash or a fast forward,** revert the range instead:

```bash
git revert --no-commit efed1ded196d8ecc157f6d02f41f170b69033f45..HEAD
git commit -m "Roll back the November 2026 redesign"
git push origin main
```

**Do not** force push `main`, delete the `CNAME` file, change Pages settings or
touch DNS as part of a rollback. None of them is needed, and each can take the
site or the email offline.

After a rollback the old pages are live again within a few minutes. The new
URLs (`/insights/`, the new service pages, `/tools/digital-presence-check/`)
return 404 again, which is why step 14 comes last: KenAshe.ai must not link to
them until the launch has held.

Tell the owner what failed, what was rolled back, and the commit now live.
