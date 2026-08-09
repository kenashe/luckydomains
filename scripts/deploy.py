#!/usr/bin/env python3
"""Publish the Lucky Domains site to GitHub Pages over the GitHub REST API.

WHEN YOU NEED THIS
------------------
You probably do not. The normal way to deploy is:

    git add -A && git commit -m "..." && git push origin main

GitHub Pages serves the `main` branch directly and redeploys within about a
minute. This script exists for one narrow case: an automated agent that holds a
GitHub API token but has no git credentials configured. It is a convenience,
not infrastructure.

USAGE
-----
    export GITHUB_PAT=github_pat_...     # see .env.example
    export GITHUB_REPO=luckydomains
    export GITHUB_OWNER=kenashe          # optional, this is the default

    python3 scripts/deploy.py verify
    python3 scripts/deploy.py pull   --dir ./site-checkout
    python3 scripts/deploy.py deploy --dir ./site-checkout \
            --cname luckydomains.io --message "Describe the change"

ALWAYS `pull` BEFORE YOU EDIT. The repository may contain work that your local
directory does not, and `deploy` replaces the branch contents wholesale. The
delete guard will stop you, but pulling first is the habit that avoids the
situation entirely.

Standard library only. No third party packages.
"""
import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request

API = "https://api.github.com"
PAT = os.environ.get("GITHUB_PAT", "")
OWNER = os.environ.get("GITHUB_OWNER", "kenashe")
REPO = os.environ.get("GITHUB_REPO", "")
BRANCH = "main"

HEADERS = {
    "Authorization": "Bearer " + PAT,
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "luckydomains-deploy",
}


def req(method, path, body=None):
    """Call the GitHub API. Returns (status, parsed_json). Never raises on HTTP error."""
    url = path if path.startswith("http") else API + path
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, method=method, headers=dict(HEADERS))
    if data is not None:
        r.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(r) as resp:
            raw = resp.read()
            return resp.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            payload = json.loads(raw)
        except Exception:
            payload = {"message": raw.decode("utf-8", "replace")}
        return e.code, payload


def die(msg, code=1):
    print("ERROR: " + msg)
    sys.exit(code)


def need_repo():
    if not PAT:
        die("GITHUB_PAT is not set. See .env.example.")
    if not REPO:
        die("GITHUB_REPO is not set, for example GITHUB_REPO=luckydomains.")


def repo_paths():
    """Every file path on the branch. Empty set if the repo has no commits."""
    st, tree = req("GET", "/repos/%s/%s/git/trees/%s?recursive=1" % (OWNER, REPO, BRANCH))
    if st != 200:
        return set()
    return set(b["path"] for b in tree.get("tree", []) if b.get("type") == "blob")


def file_bytes(path):
    """Fetch one file's bytes via the contents API. Works for private repos too."""
    st, out = req("GET", "/repos/%s/%s/contents/%s?ref=%s" % (OWNER, REPO, path, BRANCH))
    if st != 200 or "content" not in out:
        return None
    return base64.b64decode(out["content"])


def collect(directory):
    """Every file under directory, as (relative_path, absolute_path), sorted."""
    files = []
    for root, _dirs, names in os.walk(directory):
        if ".git" in root.split(os.sep):
            continue
        for n in names:
            full = os.path.join(root, n)
            rel = os.path.relpath(full, directory).replace(os.sep, "/")
            files.append((rel, full))
    files.sort()
    return files


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def verify():
    need_repo()
    st, repo = req("GET", "/repos/%s/%s" % (OWNER, REPO))
    if st == 401:
        die("401 Bad credentials. The token has expired or been revoked. "
            "Fine grained tokens default to 30 day expiry. See docs/RUNBOOK.md.")
    if st == 404:
        die("Repo %s/%s not found, or the token is not scoped to it." % (OWNER, REPO))
    if st != 200:
        die("GET repo failed (%s): %s" % (st, repo.get("message")))

    perms = repo.get("permissions", {})
    private = repo.get("private")
    print("Repo:        %s" % repo.get("full_name"))
    print("Private:     %s" % private)
    print("Default ref: %s" % (repo.get("default_branch") or "(empty repo)"))
    print("Permissions: pull=%s push=%s admin=%s"
          % (perms.get("pull"), perms.get("push"), perms.get("admin")))
    print("Files on %s: %d" % (BRANCH, len(repo_paths())))
    if private:
        print("")
        print("WARNING: this repository is PRIVATE. GitHub Pages on the free plan")
        print("will not serve it, so luckydomains.io will return 404. Set it public")
        print("and re-enable Pages. See docs/RUNBOOK.md section 4.")
    if not perms.get("push"):
        die("Token cannot push. It needs Contents: Read and write.")
    print("OK: token can push to %s/%s." % (OWNER, REPO))


def pull(directory):
    need_repo()
    paths = repo_paths()
    if not paths:
        die("No files on %s. Empty repo, or the token cannot read it." % BRANCH)
    os.makedirs(directory, exist_ok=True)
    print("Pulling %d files from %s/%s@%s into %s"
          % (len(paths), OWNER, REPO, BRANCH, directory))
    got = 0
    for p in sorted(paths):
        blob = file_bytes(p)
        if blob is None:
            print("  !! could not fetch %s" % p)
            continue
        dest = os.path.join(directory, p)
        os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
        with open(dest, "wb") as fh:
            fh.write(blob)
        got += 1
    print("Pulled %d/%d files." % (got, len(paths)))


def ensure_initialized():
    """The Git Data API cannot write blobs to a repo with zero commits.

    It returns 409 "Git Repository is empty". Create one bootstrap commit
    through the Contents API first, which does work on an empty repo.
    """
    st, _ = req("GET", "/repos/%s/%s/git/ref/heads/%s" % (OWNER, REPO, BRANCH))
    if st == 200:
        return
    st, out = req("PUT", "/repos/%s/%s/contents/.init" % (OWNER, REPO),
                  {"message": "Initialize repository",
                   "content": base64.b64encode(b"init\n").decode("ascii"),
                   "branch": BRANCH})
    if st not in (200, 201):
        die("Could not initialize empty repo (%s): %s" % (st, out.get("message")))
    print("Initialized empty repository on %s." % BRANCH)


def deploy(directory, cname, allow_delete, message):
    need_repo()
    if not os.path.isdir(directory):
        die("Directory not found: " + directory)
    files = collect(directory)
    if not files:
        die("No files in " + directory)

    # Guard: this deploy replaces the branch wholesale, so anything present in
    # the repo but missing locally would be silently deleted. Refuse instead.
    local = set(rel for rel, _ in files)
    remote = repo_paths()
    would_delete = sorted(p for p in remote - local if p != ".init")
    if would_delete and not allow_delete:
        print("REFUSING TO DEPLOY.")
        print("%d file(s) exist in the repo but not in %s, so deploying would "
              "DELETE them:" % (len(would_delete), directory))
        for p in would_delete:
            print("   - %s" % p)
        print("")
        print("Run:  python3 scripts/deploy.py pull --dir %s" % directory)
        print("or pass --allow-delete if the removal is intended.")
        sys.exit(2)
    if would_delete:
        print("NOTE: --allow-delete given, removing %d file(s)." % len(would_delete))

    ensure_initialized()
    print("Uploading %d files to %s/%s" % (len(files), OWNER, REPO))

    tree = []
    for rel, full in files:
        with open(full, "rb") as fh:
            content_b64 = base64.b64encode(fh.read()).decode("ascii")
        st, blob = req("POST", "/repos/%s/%s/git/blobs" % (OWNER, REPO),
                       {"content": content_b64, "encoding": "base64"})
        if st not in (200, 201):
            die("Blob failed for %s (%s): %s" % (rel, st, blob.get("message")))
        tree.append({"path": rel, "mode": "100644", "type": "blob", "sha": blob["sha"]})
    print("  uploaded %d blobs" % len(tree))

    st, tree_obj = req("POST", "/repos/%s/%s/git/trees" % (OWNER, REPO), {"tree": tree})
    if st not in (200, 201):
        die("Tree failed (%s): %s" % (st, tree_obj.get("message")))

    parents = []
    st, ref = req("GET", "/repos/%s/%s/git/ref/heads/%s" % (OWNER, REPO, BRANCH))
    if st == 200:
        parents = [ref["object"]["sha"]]

    st, commit = req("POST", "/repos/%s/%s/git/commits" % (OWNER, REPO),
                     {"message": message, "tree": tree_obj["sha"], "parents": parents})
    if st not in (200, 201):
        die("Commit failed (%s): %s" % (st, commit.get("message")))
    sha = commit["sha"]

    if parents:
        st, out = req("PATCH", "/repos/%s/%s/git/refs/heads/%s" % (OWNER, REPO, BRANCH),
                      {"sha": sha, "force": True})
    else:
        st, out = req("POST", "/repos/%s/%s/git/refs" % (OWNER, REPO),
                      {"ref": "refs/heads/%s" % BRANCH, "sha": sha})
    if st not in (200, 201):
        die("Ref update failed (%s): %s" % (st, out.get("message")))
    print("Committed %s to %s." % (sha[:7], BRANCH))

    configure_pages(cname)


def configure_pages(cname):
    """Best effort. Pages is usually already enabled; a 403 here is harmless."""
    st, out = req("POST", "/repos/%s/%s/pages" % (OWNER, REPO),
                  {"source": {"branch": BRANCH, "path": "/"}})
    if st in (200, 201):
        print("GitHub Pages enabled (source: %s /root)." % BRANCH)
    elif st == 409:
        print("GitHub Pages already enabled.")
    elif st == 403:
        print("NOTE: token lacks Pages: write, so Pages was not touched. "
              "Harmless if Pages is already on.")
    else:
        print("NOTE: could not enable Pages (%s): %s" % (st, out.get("message")))

    if cname:
        st, out = req("PUT", "/repos/%s/%s/pages" % (OWNER, REPO),
                      {"cname": cname, "https_enforced": True})
        if st in (200, 204):
            print("Custom domain set to %s, HTTPS enforced." % cname)
        elif st == 403:
            print("NOTE: token lacks Pages: write, custom domain unchanged. "
                  "The committed CNAME file still applies it.")
        else:
            print("NOTE: custom domain not set (%s): %s" % (st, out.get("message")))

    st, pages = req("GET", "/repos/%s/%s/pages" % (OWNER, REPO))
    if st == 200:
        print("Pages status: %s" % pages.get("status"))
        print("Pages URL:    %s" % pages.get("html_url"))


def main():
    ap = argparse.ArgumentParser(description="Deploy luckydomains.io via the GitHub API.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("verify", help="check token, permissions and repo visibility")
    p = sub.add_parser("pull", help="download the current branch into a directory")
    p.add_argument("--dir", required=True)
    d = sub.add_parser("deploy", help="commit a directory to the branch")
    d.add_argument("--dir", required=True)
    d.add_argument("--cname", default="")
    d.add_argument("--allow-delete", action="store_true",
                   help="permit deleting repo files absent from --dir")
    d.add_argument("--message", default="Update Lucky Domains site")
    args = ap.parse_args()

    if args.cmd == "verify":
        verify()
    elif args.cmd == "pull":
        pull(args.dir)
    elif args.cmd == "deploy":
        deploy(args.dir, args.cname, args.allow_delete, args.message)


if __name__ == "__main__":
    main()
