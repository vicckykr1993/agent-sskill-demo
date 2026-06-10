"""
pr_description.py — Reference script for PR Description Generator skill
Fetches PR details from GitHub API and generates a full structured PR description.
Optionally posts the description back to the PR.
"""

import argparse
import json
import re
import urllib.request
import urllib.error
from datetime import datetime


# ─── GitHub API Helpers ───────────────────────────────────────────────────────

def github_get(endpoint: str, token: str = None) -> dict:
    """Make a GET request to the GitHub API."""
    url = f"https://api.github.com{endpoint}"
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github.v3+json")
    if token:
        req.add_header("Authorization", f"token {token}")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"GitHub API error {e.code}: {e.reason} — {endpoint}")


def github_patch(endpoint: str, data: dict, token: str) -> dict:
    """Make a PATCH request to the GitHub API."""
    url = f"https://api.github.com{endpoint}"
    payload = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="PATCH")
    req.add_header("Accept", "application/vnd.github.v3+json")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"token {token}")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"GitHub API error {e.code}: {e.reason}")


# ─── PR Details Fetcher ───────────────────────────────────────────────────────

def fetch_pr_details(repo: str, pr_number: int, token: str = None) -> dict:
    """
    Fetch full PR details from GitHub API.
    Returns a structured dict with all info needed for description generation.

    Args:
        repo: "owner/repo" format
        pr_number: PR number (integer)
        token: optional GitHub PAT for private repos

    Returns: {
        title, number, author, created_at,
        head_branch, base_branch, body,
        labels, commits, files, repo
    }
    """
    # Core PR info
    pr = github_get(f"/repos/{repo}/pulls/{pr_number}", token)

    # Commits
    commits_raw = github_get(f"/repos/{repo}/pulls/{pr_number}/commits", token)
    commits = [
        {
            "sha": c["sha"][:7],
            "message": c["commit"]["message"].split("\n")[0],  # first line only
            "author": c["commit"]["author"]["name"],
        }
        for c in commits_raw
    ]

    # Changed files
    files_raw = github_get(f"/repos/{repo}/pulls/{pr_number}/files", token)
    files = [
        {
            "filename": f["filename"],
            "status": f["status"],          # added, modified, removed, renamed
            "additions": f["additions"],
            "deletions": f["deletions"],
            "changes": f["changes"],
        }
        for f in files_raw
    ]

    return {
        "repo": repo,
        "number": pr_number,
        "title": pr["title"],
        "author": pr["user"]["login"],
        "created_at": pr["created_at"][:10],
        "head_branch": pr["head"]["ref"],
        "base_branch": pr["base"]["ref"],
        "body": pr.get("body") or "",
        "labels": [l["name"] for l in pr.get("labels", [])],
        "commits": commits,
        "files": files,
        "url": pr["html_url"],
        "state": pr["state"],
        "draft": pr.get("draft", False),
    }


# ─── PR Type Detector ─────────────────────────────────────────────────────────

PR_TYPE_RULES = [
    (["fix", "bug", "hotfix", "patch", "resolve"],           "🐛 Bug Fix",      "bug"),
    (["feat", "feature", "add", "new", "implement"],         "✨ New Feature",   "feature"),
    (["refactor", "cleanup", "restructure", "reorganize"],   "♻️ Refactor",     "refactor"),
    (["docs", "readme", "documentation", "comment"],         "📝 Documentation","docs"),
    (["test", "spec", "coverage", "unittest"],               "🧪 Tests",         "test"),
    (["chore", "ci", "cd", "deploy", "build", "pipeline"],  "🔧 Chore/CI",      "chore"),
    (["style", "lint", "format", "prettier"],                "💅 Style",         "style"),
]

def detect_pr_type(details: dict) -> tuple:
    """
    Auto-detect PR type based on title, branch name, and commit messages.
    Returns (label_emoji_str, raw_label)
    """
    # Combine all text sources for matching
    search_text = " ".join([
        details["title"].lower(),
        details["head_branch"].lower(),
        *[c["message"].lower() for c in details["commits"]],
    ])

    for keywords, label, raw in PR_TYPE_RULES:
        if any(kw in search_text for kw in keywords):
            return label, raw

    return "🔀 General", "general"


# ─── Checklist Builder ────────────────────────────────────────────────────────

def build_type_checklist(detected_label: str) -> str:
    """Build the type checklist with the detected type pre-checked."""
    types = [
        ("🐛 Bug Fix",      "bug"),
        ("✨ New Feature",  "feature"),
        ("♻️ Refactor",    "refactor"),
        ("📝 Documentation","docs"),
        ("🧪 Tests",        "test"),
        ("🔧 Chore/CI",     "chore"),
        ("💅 Style",        "style"),
    ]
    lines = []
    for label, raw in types:
        checked = "x" if raw == detected_label else " "
        lines.append(f"- [{checked}] {label}")
    return "\n".join(lines)


# ─── Test Command Suggester ───────────────────────────────────────────────────

def suggest_test_command(details: dict) -> str:
    """Suggest a test command based on files changed."""
    filenames = [f["filename"] for f in details["files"]]
    exts = {f.split(".")[-1] for f in filenames if "." in f}

    if "py" in exts:
        return "pytest"
    elif "js" in exts or "ts" in exts or "jsx" in exts or "tsx" in exts:
        return "npm test"
    elif "java" in exts:
        return "mvn test"
    elif "go" in exts:
        return "go test ./..."
    elif "rb" in exts:
        return "bundle exec rspec"
    else:
        return "Run your project's test suite"


# ─── Files Summary Builder ────────────────────────────────────────────────────

def build_files_summary(files: list) -> str:
    """Format changed files into a readable list."""
    status_emoji = {
        "added": "➕",
        "modified": "✏️",
        "removed": "🗑️",
        "renamed": "🔄",
        "changed": "✏️",
    }
    lines = []
    for f in files[:20]:  # cap at 20 files
        emoji = status_emoji.get(f["status"], "📄")
        lines.append(
            f"- {emoji} `{f['filename']}` "
            f"(+{f['additions']} / -{f['deletions']})"
        )
    if len(files) > 20:
        lines.append(f"- ... and {len(files) - 20} more files")
    return "\n".join(lines)


# ─── Summary Generator ────────────────────────────────────────────────────────

def generate_summary(details: dict) -> str:
    """Auto-generate a summary from title and commit messages."""
    title = details["title"]
    commits = details["commits"]
    branch = details["head_branch"]

    if len(commits) == 1:
        return f"This PR {commits[0]['message'].lower()} (branch: `{branch}`)."
    else:
        bullet_commits = "\n".join(f"- {c['message']}" for c in commits[:5])
        suffix = f"\n- ... and {len(commits) - 5} more commits" if len(commits) > 5 else ""
        return f"This PR includes the following changes from branch `{branch}`:\n{bullet_commits}{suffix}"


# ─── Main Description Generator ───────────────────────────────────────────────

def generate_description(details: dict, pr_type_tuple: tuple) -> str:
    """
    Generate the full PR description markdown.
    Returns a formatted string ready to post to GitHub.
    """
    pr_type_label, pr_type_raw = pr_type_tuple
    summary = generate_summary(details)
    type_checklist = build_type_checklist(pr_type_raw)
    files_summary = build_files_summary(details["files"])
    test_cmd = suggest_test_command(details)

    # Auto notes from commits if > 3
    notes = ""
    if len(details["commits"]) > 3:
        notes = f"This PR contains {len(details['commits'])} commits. Consider squashing before merge."
    if details["draft"]:
        notes += "\n⚠️ This PR is currently a **Draft** — not ready for review yet."

    return f"""## 📋 Summary
{summary}

---

## 🏷️ Type of Change
{type_checklist}

> ✅ Auto-detected: **{pr_type_label}**

---

## 📂 Changes Made
{files_summary}

---

## 🧪 How to Test
1. Checkout branch: `git checkout {details['head_branch']}`
2. Run: `{test_cmd}`
3. Verify the changes work as described in the summary above.

---

## 📸 Screenshots
<!-- Add before/after screenshots if UI changes are involved -->
| Before | After |
|--------|-------|
| _N/A_  | _N/A_ |

---

## ✅ Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No breaking changes (or breaking changes documented)

---

## 📝 Additional Notes
{notes if notes else "_No additional notes._"}

---
*🤖 Auto-generated by PR Description Generator skill | PR #{details['number']} by @{details['author']} on {details['created_at']}*"""


# ─── Post Back to GitHub ──────────────────────────────────────────────────────

def post_description(repo: str, pr_number: int, description: str, token: str) -> bool:
    """
    Post the generated description back to the GitHub PR.
    Returns True if successful.
    """
    try:
        github_patch(
            f"/repos/{repo}/pulls/{pr_number}",
            {"body": description},
            token
        )
        return True
    except Exception as e:
        print(f"❌ Failed to post description: {e}")
        return False


# ─── CLI Entry Point ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PR Description Generator")
    parser.add_argument("--repo", required=True, help="GitHub repo in owner/repo format")
    parser.add_argument("--pr", required=True, type=int, help="PR number")
    parser.add_argument("--token", default=None, help="GitHub PAT (optional for public repos)")
    parser.add_argument("--post", action="store_true", help="Post description back to PR")
    args = parser.parse_args()

    print(f"\n🔍 Fetching PR #{args.pr} from {args.repo}...\n")
    try:
        details = fetch_pr_details(args.repo, args.pr, args.token)
        pr_type = detect_pr_type(details)
        description = generate_description(details, pr_type)

        print(f"✅ PR: {details['title']}")
        print(f"👤 Author: @{details['author']} | 📅 {details['created_at']}")
        print(f"🔀 {details['head_branch']} → {details['base_branch']}")
        print(f"🏷️  Type: {pr_type[0]}")
        print(f"📂 Files changed: {len(details['files'])}")
        print(f"💬 Commits: {len(details['commits'])}")
        print("\n" + "─" * 60)
        print(description)
        print("─" * 60)

        if args.post:
            if not args.token:
                print("\n⚠️  --token required to post description back to GitHub.")
            else:
                success = post_description(args.repo, args.pr, description, args.token)
                if success:
                    print(f"\n✅ Description posted to PR #{args.pr} successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")
