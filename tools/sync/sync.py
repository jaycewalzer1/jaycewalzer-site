"""Weekly check: did the resume or any GitHub project change? If so, hand the changes to a
headless Claude Code run that updates the site, its write-ups and its videos.

    python3 tools/sync/sync.py              # detect; run the agent if something changed
    python3 tools/sync/sync.py --dry-run    # detect and print, change nothing
    python3 tools/sync/sync.py --baseline   # record what is on GitHub now as already synced
    python3 tools/sync/sync.py --selftest   # check gh, Overleaf, claude and file access

Detection is plain API calls and costs nothing. The agent only runs when one of these is true:
a new or removed repo; a repo's README, description, homepage or visibility changed; a repo
has new commits and was last reviewed REVIEW_DAYS or more days ago; the resume on Overleaf
changed; an earlier run left something owed.

Everything this script remembers is in tools/sync/local/ (not in git): state.json, owed.json,
holds.md, the Overleaf clone and the reports. The log is ~/Library/Logs/jaycewalzer-site-sync.log. The agent's instructions are PROMPT.md.
"""
import argparse
import datetime
import fcntl
import glob
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
LOCAL = HERE / "local"
STATE = LOCAL / "state.json"
OWED = LOCAL / "owed.json"
RESUME_DIR = LOCAL / "resume"

OVERLEAF_GIT = "https://git.overleaf.com/64ecc81c0101605112ebff00"
SKIP_REPOS = {"jaycewalzer-site"}  # the site itself: its commits are this job's own output
REVIEW_DAYS = 6  # commits that don't touch the README are looked at this often (under a week, so every weekly run)
AGENT_TIMEOUT_S = 4 * 3600
MAX_FAILURES = 3  # after this many failed agent runs in a row, stop retrying and just notify
AGENT_TOOLS = ["Bash", "Read", "Edit", "Write", "Glob", "Grep", "Agent"]

REPOS_QUERY = """
query($cursor: String) {
  viewer {
    repositories(first: 100, after: $cursor, ownerAffiliations: OWNER) {
      pageInfo { hasNextPage endCursor }
      nodes {
        name url visibility description homepageUrl isFork isArchived pushedAt
        defaultBranchRef { name target { oid } }
        readme: object(expression: "HEAD:README.md") { ... on Blob { oid } }
      }
    }
  }
}
"""

os.environ["PATH"] = os.pathsep.join(
    [str(Path.home() / ".local/bin"), "/opt/homebrew/bin", "/usr/local/bin", os.environ.get("PATH", "/usr/bin:/bin")]
)
TODAY = datetime.date.today()
STAMP = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")


def log(msg):
    print(f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] {msg}", flush=True)


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def notify(text):
    script = f"display notification {json.dumps(text)} with title \"jaycewalzer.com sync\""
    run(["osascript", "-e", script])


def load(path, default):
    return json.loads(path.read_text()) if path.exists() else default


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n")
    tmp.replace(path)


# ---------- GitHub ----------

def github_repos():
    repos, cursor = {}, None
    while True:
        cmd = ["gh", "api", "graphql", "-f", f"query={REPOS_QUERY}"]
        if cursor:
            cmd += ["-f", f"cursor={cursor}"]
        r = run(cmd)
        if r.returncode != 0:
            raise RuntimeError(f"gh api failed: {r.stderr.strip()}")
        page = json.loads(r.stdout)["data"]["viewer"]["repositories"]
        for n in page["nodes"]:
            if n["name"] in SKIP_REPOS:
                continue
            branch = n["defaultBranchRef"] or {}
            repos[n["name"]] = {
                "url": n["url"],
                "visibility": n["visibility"].lower(),
                "description": n["description"] or "",
                "homepage": n["homepageUrl"] or "",
                "fork": n["isFork"],
                "archived": n["isArchived"],
                "branch": branch.get("name", ""),
                "sha": (branch.get("target") or {}).get("oid", ""),
                "readme": (n["readme"] or {}).get("oid", ""),
            }
        if not page["pageInfo"]["hasNextPage"]:
            return repos
        cursor = page["pageInfo"]["endCursor"]


def repo_changes(now, synced):
    """Compare GitHub now with what the site was last synced against."""
    changes = []
    for name, cur in sorted(now.items()):
        old = synced.get(name)
        if old is None:
            changes.append({"repo": name, "kind": "new", "now": cur})
            continue
        why = [k for k in ("readme", "description", "homepage", "visibility") if cur[k] != old.get(k, "")]
        age = (TODAY - datetime.date.fromisoformat(old.get("reviewed", "2000-01-01"))).days
        if not why and cur["sha"] != old.get("sha") and age >= REVIEW_DAYS:
            why = ["commits"]
        if why:
            changes.append({"repo": name, "kind": "changed", "what": why, "since_sha": old.get("sha", ""),
                            "was": {k: old.get(k, "") for k in ("description", "homepage", "visibility")}, "now": cur})
    for name in sorted(set(synced) - set(now)):
        changes.append({"repo": name, "kind": "removed", "was": synced[name]})
    return changes


# ---------- Overleaf ----------

def overleaf_git(*args, cwd=None):
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    return run(["git", "-c", "credential.helper=osxkeychain", *args], cwd=cwd, env=env, timeout=120)


def resume_change(state):
    """None if unchanged, else what the agent needs. Never raises: no access is reported, not fatal."""
    r = overleaf_git("ls-remote", OVERLEAF_GIT, "HEAD")
    if r.returncode != 0 or not r.stdout.strip():
        return {"status": "unreachable", "error": (r.stderr.strip() or "no HEAD").splitlines()[-1]}
    head = r.stdout.split()[0]
    old = state.get("resume", {}).get("sha", "")
    if head == old:
        return None
    return {"status": "changed", "sha": head, "since_sha": old, "first_sync": not old}


def resume_fetch(head):
    if (RESUME_DIR / ".git").exists():
        r = overleaf_git("fetch", "origin", cwd=RESUME_DIR)
        if r.returncode == 0:
            r = run(["git", "checkout", "-q", "--detach", head], cwd=RESUME_DIR)
    else:
        LOCAL.mkdir(parents=True, exist_ok=True)
        r = overleaf_git("clone", "-q", OVERLEAF_GIT, str(RESUME_DIR))
    if r.returncode != 0:
        raise RuntimeError(f"Overleaf fetch failed: {r.stderr.strip()}")


# ---------- the agent ----------

def find_claude():
    found = shutil.which("claude")
    if found:
        return found
    hits = sorted(glob.glob(str(Path.home() / ".nvm/versions/node/*/bin/claude")), key=os.path.getmtime)
    if not hits:
        raise RuntimeError("claude CLI not found")
    os.environ["PATH"] = str(Path(hits[-1]).parent) + os.pathsep + os.environ["PATH"]  # it needs node beside it
    return hits[-1]


def claude(prompt, timeout, tools=()):
    cmd = [find_claude(), "-p", "--permission-mode", "acceptEdits"]
    if tools:
        cmd += ["--allowedTools", *tools]
    return subprocess.run(cmd, input=prompt, capture_output=True, text=True, cwd=ROOT, timeout=timeout)


def run_agent(pending):
    report = LOCAL / "reports" / f"{STAMP}.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    holds = LOCAL / "holds.md"
    prompt = "\n\n".join([
        (HERE / "PROMPT.md").read_text(),
        "## Standing holds (from tools/sync/local/holds.md)\n\n" + (holds.read_text() if holds.exists() else "none"),
        f"## This run\n\nToday is {TODAY}. Write your report to `{report}`.\n\n```json\n{json.dumps(pending, indent=2)}\n```",
    ])
    try:
        r = claude(prompt, AGENT_TIMEOUT_S, AGENT_TOOLS)
    except subprocess.TimeoutExpired:
        log(f"agent timed out after {AGENT_TIMEOUT_S} s")
        return False, report
    log(f"agent exit {r.returncode}\n{r.stdout.strip()}\n{r.stderr.strip()}")
    done = report.exists() and "STATUS: done" in report.read_text()
    return r.returncode == 0 and done, report


# ---------- commands ----------

def detect(state):
    now = github_repos()
    changes = repo_changes(now, state.get("repos", {}))
    resume = resume_change(state)
    owed = load(OWED, [])
    return now, changes, resume, owed


def describe(changes, resume, owed):
    lines = []
    for c in changes:
        lines.append(f"  {c['repo']}: {c['kind']}" + (f" ({', '.join(c['what'])})" if "what" in c else ""))
    if resume:
        lines.append(f"  resume: {resume['status']}" + (f" ({resume['error']})" if "error" in resume else ""))
    for o in owed:
        lines.append(f"  owed: {o.get('what', o)}")
    return "\n".join(lines) or "  nothing"


def mark_synced(state, now, names):
    repos = state.setdefault("repos", {})
    for name in names:
        if name in now:
            repos[name] = dict(now[name], reviewed=str(TODAY))
        else:
            repos.pop(name, None)


def cmd_baseline(state):
    now = github_repos()
    mark_synced(state, now, set(now) | set(state.get("repos", {})))
    save(STATE, state)
    log(f"baseline recorded for {len(now)} repos (resume baseline is set by its first sync)")


def cmd_selftest():
    ok = True
    def check(name, good, detail=""):
        nonlocal ok
        ok = ok and good
        log(f"{'ok  ' if good else 'FAIL'} {name} {detail}")
    try:
        check("github", True, f"{len(github_repos())} repos visible")
    except Exception as e:
        check("github", False, str(e))
    r = resume_change({})
    check("overleaf", r["status"] == "changed", r.get("error", r.get("sha", ""))[:60])
    check("site files", (ROOT / "site.json").exists() and os.access(ROOT, os.W_OK))
    try:
        out = claude("Reply with the single word: ready", 180)
        check("claude", out.returncode == 0 and "ready" in out.stdout.lower(), (out.stdout.strip() or out.stderr.strip())[:80])
    except Exception as e:
        check("claude", False, str(e))
    return 0 if ok else 1


def cmd_sync(state, dry_run):
    now, changes, resume, owed = detect(state)
    unreachable = bool(resume) and resume["status"] == "unreachable"
    work = bool(changes or owed or (resume and not unreachable))
    log("found:\n" + describe(changes, resume, owed))
    if dry_run:
        return 0
    if unreachable and state.get("resume_ok", True):
        notify("Can't read the resume on Overleaf, so resume changes are not being checked. See tools/sync/README.md.")
    state["resume_ok"] = not unreachable
    if not work:
        save(STATE, state)
        return 0
    if state.get("failures", 0) >= MAX_FAILURES:
        save(STATE, state)
        notify(f"Stuck: the last {MAX_FAILURES} update runs failed, so nothing is being updated. Log: ~/Library/Logs/jaycewalzer-site-sync.log")
        log("not running the agent: too many failures in a row (set \"failures\": 0 in state.json to retry)")
        return 1
    if resume and not unreachable:
        resume_fetch(resume["sha"])
        resume["path"] = str(RESUME_DIR)
    pending = {"repos": changes, "resume": None if unreachable else resume, "owed": owed}
    save(LOCAL / "pending.json", pending)
    ok, report = run_agent(pending)
    if ok:
        mark_synced(state, now, [c["repo"] for c in changes])
        if pending["resume"]:
            state["resume"] = {"sha": resume["sha"], "synced": str(TODAY)}
        state["failures"] = 0
        notify(f"Site updated from {len(changes)} repo change(s)" + (" and the resume" if pending["resume"] else "")
               + f". Report: {report.name}")
    else:
        state["failures"] = state.get("failures", 0) + 1
        notify(f"Update run failed ({state['failures']} in a row); it will retry next week. Log: ~/Library/Logs/jaycewalzer-site-sync.log")
    save(STATE, state)
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--baseline", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    LOCAL.mkdir(parents=True, exist_ok=True)
    if args.selftest:
        return cmd_selftest()
    lock = open(LOCAL / "lock", "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        log("another sync is still running; skipping")
        return 0
    state = load(STATE, {})
    if args.baseline:
        return cmd_baseline(state)
    return cmd_sync(state, args.dry_run)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        log(f"sync failed: {e}")
        notify(f"Sync check failed: {e}"[:200])
        sys.exit(1)
