---
name: PR Description Generator
description: Use this skill when the user mentions a pull request or PR. Triggers on: user typing "generate PR description", "write PR description", "PR description for...", user pasting a GitHub PR link (github.com/.../pull/...), or user mentioning "PR", "pull request", "raised a PR", "opened a PR". Automatically fetch PR details and generate a full structured description.
---

# PR Description Generator Skill

## Triggers
Activate this skill when the user:
1. Types **"generate PR description"**, **"write PR description"**, **"create PR description"**
2. Pastes a **GitHub PR link** — e.g. `https://github.com/owner/repo/pull/123`
3. Mentions **"PR"**, **"pull request"**, **"raised a PR"**, **"opened a PR"**

---

## Step 1 — Extract PR Info

### If user pastes a PR link:
Parse the URL to extract:
- `owner` — GitHub username/org
- `repo` — repository name
- `pr_number` — pull request number

Then use `scripts/pr_description.py` to fetch PR details via GitHub API:
- PR title, branch name (head → base)
- Author, created date
- List of commits (messages)
- List of changed files (with additions/deletions)
- Existing labels

### If user mentions a PR without a link:
Ask:
> "Could you share the PR link or tell me the repo name and PR number? 🔗"

### If user types "generate PR description" without context:
Ask:
> "Sure! Please paste the PR link or describe what changes you made and I'll generate a description. 📝"

---

## Step 2 — Detect PR Type (Conditional Logic)

Based on the PR title, branch name, and commit messages, auto-detect the PR type:

| Keywords Found                          | PR Type         | Label     |
|-----------------------------------------|-----------------|-----------|
| `fix`, `bug`, `hotfix`, `patch`         | 🐛 Bug Fix       | `bug`     |
| `feat`, `feature`, `add`, `new`         | ✨ Feature        | `feature` |
| `refactor`, `cleanup`, `restructure`    | ♻️ Refactor      | `refactor`|
| `docs`, `readme`, `documentation`       | 📝 Documentation | `docs`    |
| `test`, `spec`, `coverage`              | 🧪 Tests         | `test`    |
| `chore`, `ci`, `cd`, `deploy`, `build`  | 🔧 Chore/CI      | `chore`   |
| `style`, `lint`, `format`               | 💅 Style         | `style`   |
| None of the above                       | 🔀 General       | `general` |

---

## Step 3 — Generate Full PR Description

Output the description in this exact markdown template:

```markdown
## 📋 Summary
<!-- A clear and concise description of what this PR does -->
{auto_generated_summary_from_commits_and_title}

---

## 🏷️ Type of Change
- [ ] 🐛 Bug Fix
- [ ] ✨ New Feature
- [ ] ♻️ Refactor
- [ ] 📝 Documentation
- [ ] 🧪 Tests
- [ ] 🔧 Chore / CI
- [ ] 💅 Style

> ✅ Auto-detected: **{detected_type}**

---

## 📂 Changes Made
{list_of_changed_files_with_brief_description}

---

## 🧪 How to Test
1. Checkout branch: `git checkout {branch_name}`
2. Run: `{suggested_test_command}`
3. Verify: {what_to_verify}

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
<!-- Any extra context, known issues, or follow-up tasks -->
{auto_notes_from_commits_or_blank}
```

---

## Step 4 — Post Description to GitHub (Optional)

After generating, ask:
> "Want me to post this description directly to the PR on GitHub? I'll need your GitHub token. 🔑"

If user confirms and provides token, use `scripts/pr_description.py` to PATCH the PR body via GitHub API.

---

## Reference Script

See `scripts/pr_description.py` for full implementation.

```bash
# Fetch PR info and generate description
python scripts/pr_description.py --repo "vicckykr1993/agent-sskill-demo" --pr 5

# Also post the description back to GitHub
python scripts/pr_description.py --repo "owner/repo" --pr 12 --token ghp_xxx --post
```

```python
from scripts.pr_description import fetch_pr_details, detect_pr_type, generate_description, post_description

details = fetch_pr_details("vicckykr1993/agent-sskill-demo", 5)
pr_type = detect_pr_type(details)
description = generate_description(details, pr_type)
print(description)

# Optionally post back
post_description("vickkykr1993/agent-sskill-demo", 5, description, token="ghp_xxx")
```

---

## Example Interaction

**User:** https://github.com/vicckykr1993/agent-sskill-demo/pull/3
**Claude:** Fetching PR details... ✅

> Generated full PR description with:
> - ✨ Type auto-detected as **Feature**
> - 📂 3 files changed listed
> - 🧪 Test steps based on branch
> - ✅ Checklist pre-filled

Want me to post this back to the PR? 🚀
